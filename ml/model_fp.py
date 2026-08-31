import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

# ------------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATA_PATH = ROOT / "datasets" / "processed" / "master_dataset.csv"
SCALER_PATH = ROOT / "artifacts" / "scaler_teacher.pkl"
MODEL_PATH = ROOT / "artifacts" / "teacher_model.pth"
DISTILL_PATH = ROOT / "artifacts" / "teacher_for_distillation.pt"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 512 
LEARNING_RATE = 0.001
MAX_EPOCHS = 150
PATIENCE = 15  # Stop if F1 doesn't improve for 15 epochs

# ------------------------------------------------------------------
# 2. Residual Architecture
# ------------------------------------------------------------------
class ResidualBlock(nn.Module):
    def __init__(self, size):
        super().__init__()
        self.norm = nn.LayerNorm(size)
        self.net = nn.Sequential(
            nn.Linear(size, size * 2),
            nn.GELU(),
            nn.Linear(size * 2, size),
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

# ------------------------------------------------------------------
# 3. Main Execution
# ------------------------------------------------------------------
def main():
    features = [
        "Min Packet Length", "Bwd Packet Length Max", "Total Length of Bwd Packets",
        "Subflow Bwd Bytes", "min_seg_size_forward", "Bwd Header Length",
        "Destination Port", "Total Length of Fwd Packets", "Fwd Packet Length Max",
        "ACK Flag Count", "Subflow Fwd Bytes", "Total Backward Packets",
        "Subflow Bwd Packets", "Max Packet Length", "Flow Duration", "Fwd Header Length"
    ]
    
    print("Step 1: Loading Data...")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
        
    df = pd.read_csv(DATA_PATH)
    X = df[features].values
    y = df["Label"].values

    # Step 2: Split (70/15/15)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

    # Step 3: Scaling (MinMax Only)
    print("Step 2: Applying MinMaxScaler...")
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)
    joblib.dump(scaler, SCALER_PATH)

    class NIDSDataset(Dataset):
        def __init__(self, X, y):
            self.X = torch.tensor(X, dtype=torch.float32)
            self.y = torch.tensor(y, dtype=torch.float32)
        def __len__(self): return len(self.y)
        def __getitem__(self, idx): return self.X[idx], self.y[idx]

    train_loader = DataLoader(NIDSDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(NIDSDataset(X_val, y_val), batch_size=BATCH_SIZE)

    # Step 4: Training Setup
    model = FPSuperTeacher(len(features)).to(DEVICE)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.02)
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)
    
    print(f"Step 3: Training Super-Teacher on {DEVICE}...")
    best_f1 = 0
    epochs_without_improvement = 0

    for epoch in range(MAX_EPOCHS):
        model.train()
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            loss = criterion(model(inputs), labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
        
        scheduler.step()

        # Validation Loop
        model.eval()
        all_preds = []
        all_labels = []
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                logits = model(inputs)
                preds = (torch.sigmoid(logits) > 0.5).cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().numpy())
        
        val_acc = accuracy_score(all_labels, all_preds)
        val_f1 = f1_score(all_labels, all_preds)

        print(f"Epoch {epoch+1:03d} | Val Acc: {val_acc:.6%} | Val F1: {val_f1:.6%}")

        # Early Stopping & Model Selection
        if val_f1 > best_f1:
            best_f1 = val_f1
            epochs_without_improvement = 0
            torch.save(model.state_dict(), MODEL_PATH)
            
            # Save artifact for Distillation
            torch.save({
                'state_dict': model.state_dict(),
                'input_size': len(features),
                'f1_score': val_f1,
                'features': features,
                'transform': 'minmax_only'
            }, DISTILL_PATH)
        else:
            epochs_without_improvement += 1
        
        if epochs_without_improvement >= PATIENCE:
            print(f"\n[EARLY STOPPING] Triggered at epoch {epoch+1}. Best F1: {best_f1:.6%}")
            break

    print(f"\n[SUCCESS] Final Teacher F1-Score: {best_f1:.6%}")

if __name__ == "__main__":
    main()