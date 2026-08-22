import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# ------------------------------------------------------------------
# 1. Configuration & Paths
# ------------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATA_PATH = ROOT / "datasets" / "processed" / "master_dataset.csv"
FEAT_PATH = ROOT / "artifacts" / "selected_features.json"
SCALER_PATH = ROOT / "artifacts" / "scaler_teacher.pkl"
MODEL_PATH = ROOT / "artifacts" / "teacher_model.pth"

# Hyperparameters
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 64
LEARNING_RATE = 0.0005
MAX_EPOCHS = 100
EARLY_STOPPING_PATIENCE = 10
SCHEDULER_PATIENCE = 4
SCHEDULER_FACTOR = 0.5

# ------------------------------------------------------------------
# 2. Teacher Model Architecture (32-16-8)
# ------------------------------------------------------------------
class FPTeacherClassifier(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        # Layer 1: 64 Neurons
        self.layer1 = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.BatchNorm1d(64),
            nn.ReLU()
        )
        # Layer 2: 32 Neurons
        self.layer2 = nn.Sequential(
            nn.Linear(64, 64),
            nn.BatchNorm1d(64),
            nn.ReLU()
        )
        # Layer 3: 16 Neurons
        self.layer3 = nn.Sequential(
            nn.Linear(64, 64),
            nn.BatchNorm1d(64),
            nn.ReLU()
        )
        # Output Layer (Logits)
        self.output = nn.Linear(64, 1)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        return self.output(x).squeeze(-1)

# ------------------------------------------------------------------
# 3. Dataset Helper
# ------------------------------------------------------------------
class NIDSDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
    def __len__(self): return len(self.y)
    def __getitem__(self, idx): return self.X[idx], self.y[idx]

# ------------------------------------------------------------------
# 4. Main Execution
# ------------------------------------------------------------------
def main():
    # --- Data Preparation ---
    print("Loading data and preparing features...")
    df = pd.read_csv(DATA_PATH)
    with open(FEAT_PATH, "r") as f:
        features = json.load(f)
    
    X = df[features].values
    y = df["Label"].values

    # Stratified Split (70/15/15)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

    # Scaling
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)
    joblib.dump(scaler, SCALER_PATH)

    train_loader = DataLoader(NIDSDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(NIDSDataset(X_val, y_val), batch_size=BATCH_SIZE)
    test_loader = DataLoader(NIDSDataset(X_test, y_test), batch_size=BATCH_SIZE)

    # --- Initialize Model, Optimizer, and Scheduler ---
    model = FPTeacherClassifier(len(features)).to(DEVICE)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # LR Scheduler: Reduces LR when validation loss stops improving
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=SCHEDULER_FACTOR, patience=SCHEDULER_PATIENCE)
    
    # --- Training Loop ---
    print(f"Training Teacher Model on {DEVICE}...")
    best_val_loss = float('inf')
    epochs_no_improve = 0

    for epoch in range(MAX_EPOCHS):
        model.train()
        train_loss = 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                val_loss += criterion(model(inputs), labels).item()
        
        avg_train = train_loss/len(train_loader)
        avg_val = val_loss/len(val_loader)
        current_lr = optimizer.param_groups[0]['lr']
        
        print(f"Epoch {epoch+1:02d} | Train Loss: {avg_train:.4f} | Val Loss: {avg_val:.4f} | LR: {current_lr:.6f}")

        # Step Scheduler
        scheduler.step(avg_val)

        # Early Stopping & Best Model Checkpointing
        if avg_val < best_val_loss:
            best_val_loss = avg_val
            epochs_no_improve = 0
            torch.save(model.state_dict(), MODEL_PATH)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= EARLY_STOPPING_PATIENCE:
                print(f"\n[Early Stopping] Triggered after {EARLY_STOPPING_PATIENCE} epochs of no improvement.")
                break

    # --- Evaluation ---
    print("\nEvaluating Best Teacher Model on Test Set...")
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()
    
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(DEVICE)
            logits = model(inputs)
            preds = (torch.sigmoid(logits) > 0.5).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)
    cm = confusion_matrix(all_labels, all_preds)

    print("-" * 30)
    print(f"Accuracy  : {acc:.4%}")
    print(f"F1-Score  : {f1:.4%}")
    print("-" * 30)
    print("Confusion Matrix:")
    print(cm)
    
    # --- Save Final Distillation Checkpoint ---
    distill_checkpoint = {
        'state_dict': model.state_dict(),
        'input_size': len(features),
        'hidden_dims': [32, 16, 8],
        'scaler_path': str(SCALER_PATH),
        'f1_score': f1
    }
    torch.save(distill_checkpoint, ROOT / "artifacts" / "teacher_for_distillation.pt")
    print(f"\n[SUCCESS] Teacher model and metadata saved for distillation.")

if __name__ == "__main__":
    main()