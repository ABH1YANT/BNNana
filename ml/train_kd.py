import copy
import json
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import numpy as np
from pathlib import Path
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from .config import cfg
from .model import BNNClassifier 
from .layers import BinaryLinear # Explicitly import for type checking

# ==============================================================
# 1. KNOWLEDGE DISTILLATION CONFIGURATION
# ==============================================================

DATA_PATH = cfg.DATA_DIR / "scaled_dataset.csv"
TEACHER_PATH = cfg.ARTIFACT_DIR / "teacher_for_distillation.pt"
FEAT_FILE = cfg.ARTIFACT_DIR / "selected_features.json"

# Distillation Hyperparameters (Adjusted for BNN constraints)
TEMPERATURE = 2.0
ALPHA = 0.2  # 30% Teacher guidance, 70% Ground Truth

DEVICE = cfg.DEVICE

# ==============================================================
# 2. DYNAMIC FEATURE LOADING
# ==============================================================

if not FEAT_FILE.exists():
    raise FileNotFoundError(f"Feature definition missing: {FEAT_FILE}")

with open(FEAT_FILE, "r") as f:
    FEATURES = json.load(f)

# ==============================================================
# 3. TEACHER ARCHITECTURE
# ==============================================================

class ResidualBlock(nn.Module):
    def __init__(self, size):
        super().__init__()
        self.norm = nn.LayerNorm(size)
        self.net = nn.Sequential(
            nn.Linear(size, size * 2),
            nn.GELU(),
            nn.Linear(size * 2, size)
        )
    def forward(self, x):
        return x + self.net(self.norm(x))

class FPSuperTeacher(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.stem = nn.Sequential(nn.Linear(input_size, 512), nn.GELU())
        self.stack = nn.Sequential(
            ResidualBlock(512),
            nn.Linear(512, 256),
            nn.GELU(),
            ResidualBlock(256),
            nn.Linear(256, 128),
            nn.GELU(),
            ResidualBlock(128)
        )
        self.head = nn.Linear(128, 1)

    def forward(self, x):
        x = self.stem(x)
        x = self.stack(x)
        return self.head(x).squeeze(-1)

# ==============================================================
# 4. DATA LOADING
# ==============================================================

def load_data():
    print(f"\n[{time.strftime('%H:%M:%S')}] Loading LUT-processed dataset...")
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURES].values.astype(np.float32)
    y = df["Label"].values.astype(np.float32)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )

    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train)),
        batch_size=cfg.BATCH_SIZE, shuffle=True
    )
    val_loader = DataLoader(
        TensorDataset(torch.from_numpy(X_val), torch.from_numpy(y_val)),
        batch_size=cfg.BATCH_SIZE, shuffle=False
    )
    test_loader = DataLoader(
        TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test)),
        batch_size=cfg.BATCH_SIZE, shuffle=False
    )

    return train_loader, val_loader, test_loader

# ==============================================================
# 5. DISTILLATION LOSS (Numerically Stable)
# ==============================================================

class DistillationLoss(nn.Module):
    def __init__(self, temperature, alpha):
        super().__init__()
        self.T = temperature
        self.alpha = alpha
        self.hard_loss = nn.BCEWithLogitsLoss()

    def forward(self, student_logits, teacher_logits, labels):
        # 1. Ground-truth loss (Hard Labels)
        hard_loss = self.hard_loss(student_logits, labels)

        # 2. Teacher soft targets
        teacher_probs = torch.sigmoid(teacher_logits / self.T)

        # 3. Distillation loss (Soft Labels)
        # Using binary_cross_entropy_with_logits for numerical stability
        soft_loss = F.binary_cross_entropy_with_logits(
            student_logits / self.T,
            teacher_probs
        )

        # Standard T^2 scaling to keep gradient magnitudes consistent
        soft_loss = soft_loss * (self.T ** 2)

        return (self.alpha * soft_loss) + ((1.0 - self.alpha) * hard_loss)

# ==============================================================
# 6. EVALUATION
# ==============================================================

def evaluate(model, loader):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for inputs, targets in loader:
            inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)
            logits = model(inputs)
            preds = (torch.sigmoid(logits) >= 0.5).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(targets.cpu().numpy())
    
    return {
        "accuracy": accuracy_score(all_labels, all_preds),
        "f1": f1_score(all_labels, all_preds, zero_division=0),
        "precision": precision_score(all_labels, all_preds, zero_division=0),
        "recall": recall_score(all_labels, all_preds, zero_division=0),
        "confusion_matrix": confusion_matrix(all_labels, all_preds).tolist()
    }

# ==============================================================
# 7. MAIN DISTILLATION LOOP
# ==============================================================

def main():
    start_time = time.time()
    print("\n" + "="*70 + "\nBNN KNOWLEDGE DISTILLATION (v6 Dense)\n" + "="*70)

    train_loader, val_loader, test_loader = load_data()

    # Load Teacher
    teacher = FPSuperTeacher(input_size=len(FEATURES))
    checkpoint = torch.load(TEACHER_PATH, map_location=DEVICE)
    teacher.load_state_dict(checkpoint["state_dict"])
    teacher.to(DEVICE).eval()
    for param in teacher.parameters(): param.requires_grad = False
    print(f"[OK] Teacher Loaded (F1: {checkpoint.get('f1_score', 0):.4%})")

    # Create Student
    student = BNNClassifier().to(DEVICE)
    print(f"[OK] Student Created: {cfg.HIDDEN_LAYERS} (Residuals: {cfg.USE_RESIDUALS})")

    criterion = DistillationLoss(TEMPERATURE, ALPHA)
    optimizer = torch.optim.AdamW(student.parameters(), lr=cfg.LEARNING_RATE, weight_decay=cfg.WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=5)

    best_f1 = 0.0
    epochs_no_improve = 0
    
    print(f"\nStarting Distillation (T={TEMPERATURE}, Alpha={ALPHA})...")
    print(f"{'Epoch':<6} | {'Val Acc':<10} | {'Val F1':<10} | {'LR':<10}")
    print("-" * 50)

    for epoch in range(1, cfg.NUM_EPOCHS + 1):
        student.train()
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            
            with torch.no_grad():
                teacher_logits = teacher(inputs)
            
            student_logits = student(inputs)
            loss = criterion(student_logits, teacher_logits, labels)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(student.parameters(), max_norm=1.0)
            optimizer.step()

            # --- CORRECTED BNN WEIGHT CLIPPING ---
            # We only clip the latent weights of BinaryLinear layers.
            # We MUST NOT clip BatchNorm weights (gamma/beta).
            for module in student.modules():
                if isinstance(module, BinaryLinear):
                    module.weight.data.clamp_(-1, 1)

        metrics = evaluate(student, val_loader)
        val_f1 = metrics["f1"]
        scheduler.step(val_f1)
        
        print(f"{epoch:<6} | {metrics['accuracy']:<10.4%} | {val_f1:<10.4%} | {optimizer.param_groups[0]['lr']:.6f}")

        if val_f1 > best_f1:
            best_f1 = val_f1
            epochs_no_improve = 0
            torch.save(student.state_dict(), cfg.MODEL_SAVE_PATH)
            print(f"  [SAVE] New Best F1: {best_f1:.6%}")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= cfg.EARLY_STOPPING_PATIENCE:
                print(f"\n[STOP] Early stopping at epoch {epoch}")
                break

    # Final Evaluation
    print("\n" + "="*70 + "\nFINAL TEST EVALUATION\n" + "="*70)
    student.load_state_dict(torch.load(cfg.MODEL_SAVE_PATH))
    test_metrics = evaluate(student, test_loader)
    
    for k, v in test_metrics.items():
        if k != "confusion_matrix": print(f"{k.capitalize():<10}: {v:.6%}")

    print(f"\nTotal Time: {(time.time() - start_time)/60:.2f} minutes")
    print(f"Model Saved: {cfg.MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()