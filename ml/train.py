"""
trainer.py
Entry point for training the Binarized Neural Network (BNN).

Preprocessing:
    The dataset is ALREADY processed by the LUT pipeline:
        Raw feature -> LUT bucket -> Representative -> log1p -> MinMax [0,1]
"""

import torch
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score,
    accuracy_score,
    precision_score,
    recall_score
)

# Relative imports from project
from .config import cfg
from .model import BNNClassifier  # Updated from BWN to BNN
from .loss import get_criterion

# ==============================================================
# 1. DATASET
# ==============================================================

class NIDSDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ==============================================================
# 2. PREPARE DATA
# ==============================================================

def prepare_data():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading LUT-processed dataset...")

    data_path = cfg.DATA_DIR / "scaled_dataset.csv"
    feat_file = cfg.ARTIFACT_DIR / "selected_features.json"

    if not data_path.exists():
        raise FileNotFoundError(f"Processed dataset not found: {data_path}")
    
    if not feat_file.exists():
        raise FileNotFoundError(f"Feature definition not found: {feat_file}")

    # 1. Load the EXACT features used during selection/config
    with open(feat_file, "r") as f:
        features = json.load(f)

    df = pd.read_csv(data_path)
    
    # 2. Verify all features exist in the CSV
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing features from scaled_dataset.csv:\n" + "\n".join(missing_features))

    # 3. Verify consistency with config
    if len(features) != cfg.INPUT_SIZE:
        raise ValueError(
            f"Feature count ({len(features)}) does not match cfg.INPUT_SIZE ({cfg.INPUT_SIZE}). "
            "Try restarting the terminal to refresh config."
        )

    X = df[features].values.astype(np.float32)
    y = df["Label"].values.astype(np.float32)

    # Range Check for Q1.8 Compatibility
    print("\nProcessed feature range check (Target: [0, 1]):")
    for i, feature in enumerate(features):
        print(f"{feature:35s} min={X[:, i].min():.6f} max={X[:, i].max():.6f}")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Performing Stratified Split (70/15/15)...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=cfg.RANDOM_SEED
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=cfg.RANDOM_SEED
    )

    print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")

    num_cpus = 0 if os.name == "nt" else 4

    train_loader = DataLoader(NIDSDataset(X_train, y_train), batch_size=cfg.BATCH_SIZE, shuffle=True, num_workers=num_cpus, pin_memory=torch.cuda.is_available())
    val_loader = DataLoader(NIDSDataset(X_val, y_val), batch_size=cfg.BATCH_SIZE, shuffle=False, num_workers=num_cpus, pin_memory=torch.cuda.is_available())
    test_loader = DataLoader(NIDSDataset(X_test, y_test), batch_size=cfg.BATCH_SIZE, shuffle=False, num_workers=num_cpus, pin_memory=torch.cuda.is_available())

    return train_loader, val_loader, test_loader, features

# ==============================================================
# 3. TRAINING
# ==============================================================

def train_model():
    print("\n" + "=" * 60)
    print("BNN HARDWARE-AWARE TRAINING SESSION (v6 Dense)")
    print("=" * 60)
    print(f"Input Features    : {cfg.INPUT_SIZE}")
    print(f"Hidden Layers     : {cfg.HIDDEN_LAYERS}")
    print(f"Residuals         : {'Enabled (Dense-Binary)' if cfg.USE_RESIDUALS else 'Disabled'}")
    print(f"Activation        : {cfg.ACTIVATION_TYPE}")
    print(f"Hardware Sim      : {'Enabled (Q1.8 Fixed-Point)' if cfg.SIMULATE_FIXED_POINT else 'Disabled'}")
    print(f"Device            : {cfg.DEVICE}")
    print("-" * 60)

    train_loader, val_loader, test_loader, _ = prepare_data()

    # Instantiate BNN
    model = BNNClassifier().to(cfg.DEVICE)
    print("\nBNN model created.")

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.LEARNING_RATE, weight_decay=cfg.WEIGHT_DECAY)
    
    # Scheduler monitors F1-Score (Max)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=cfg.SCHEDULER_FACTOR, patience=cfg.SCHEDULER_PATIENCE
    )

    criterion = get_criterion()

    best_f1 = 0.0
    epochs_no_improve = 0
    best_epoch = 0

    print(f"\nStarting training for {cfg.NUM_EPOCHS} epochs...")
    print(f"{'Epoch':<8} | {'Loss':<9} | {'Val Acc':<10} | {'Val F1':<10} | {'LR':<10}")
    print("-" * 75)

    try:
        for epoch in range(cfg.NUM_EPOCHS):
            # --- Training ---
            model.train()
            running_loss = 0.0
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(cfg.DEVICE), labels.to(cfg.DEVICE)
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                running_loss += loss.item()

            # --- Validation ---
            model.eval()
            val_preds, val_labels = [], []
            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs = inputs.to(cfg.DEVICE)
                    outputs = model(inputs)
                    preds = (torch.sigmoid(outputs) > 0.5).float().cpu().numpy()
                    val_preds.extend(preds)
                    val_labels.extend(labels.numpy())

            # --- Metrics ---
            epoch_loss = running_loss / len(train_loader)
            epoch_acc = accuracy_score(val_labels, val_preds)
            epoch_f1 = f1_score(val_labels, val_preds, zero_division=0)
            current_lr = optimizer.param_groups[0]["lr"]

            scheduler.step(epoch_f1)

            print(f"{epoch + 1:<8} | {epoch_loss:<9.4f} | {epoch_acc:<10.4%} | {epoch_f1:<10.4%} | {current_lr:<10.6f}")

            # --- Save Best ---
            if epoch_f1 > best_f1:
                best_f1 = epoch_f1
                best_epoch = epoch + 1
                epochs_no_improve = 0
                torch.save(model.state_dict(), cfg.MODEL_SAVE_PATH)
                print(f"  [SAVE] New best F1: {best_f1:.6%}")
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= cfg.EARLY_STOPPING_PATIENCE:
                    print(f"\n[STOP] Early stopping at epoch {epoch+1}")
                    break

    except KeyboardInterrupt:
        print("\n[WARN] Training interrupted.")

    # ==============================================================
    # FINAL TEST EVALUATION
    # ==============================================================
    print("\n" + "=" * 60)
    print("FINAL BNN TEST SET EVALUATION")
    print("=" * 60)

    if cfg.MODEL_SAVE_PATH.exists():
        model.load_state_dict(torch.load(cfg.MODEL_SAVE_PATH, map_location=cfg.DEVICE))
        model.eval()
        test_preds, test_labels = [], []
        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs = inputs.to(cfg.DEVICE)
                outputs = model(inputs)
                preds = (torch.sigmoid(outputs) > 0.5).cpu().numpy()
                test_preds.extend(preds)
                test_labels.extend(labels.numpy())

        print(f"Best Epoch         : {best_epoch}")
        print(f"Test Accuracy      : {accuracy_score(test_labels, test_preds):.6%}")
        print(f"Test F1            : {f1_score(test_labels, test_preds):.6%}")
        print(f"Test Precision     : {precision_score(test_labels, test_preds):.6%}")
        print(f"Test Recall        : {recall_score(test_labels, test_preds):.6%}")
    
    print("=" * 60)

if __name__ == "__main__":
    train_model()