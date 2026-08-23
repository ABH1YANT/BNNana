"""
train.py
Entry point for training the Binarized Neural Network (BNN).
Handles Log-Mix scaling, stratified splitting, and hardware-aware training orchestration.
Optimized to save the best model based on F1-Score with Early Stopping.
"""

import torch
import joblib
import json
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score

# Relative imports from your project module
from .config import cfg
from .model import BWNClassifier
from .loss import get_criterion

class NIDSDataset(Dataset):
    """
    Custom Dataset for Network Intrusion Detection Data.
    Converts numpy arrays to PyTorch tensors.
    """
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        
    def __len__(self): 
        return len(self.y)
        
    def __getitem__(self, idx): 
        return self.X[idx], self.y[idx]

def prepare_data():
    """
    Loads master dataset, applies 16-feature selection, performs Logarithmic 
    transformation, stratified splitting, and fits the MinMaxScaler.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading dataset from: {cfg.DATA_DIR}")
    
    master_path = cfg.DATA_DIR / "master_dataset.csv"
    if not master_path.exists():
        raise FileNotFoundError(f"Master dataset not found at {master_path}")
        
    df = pd.read_csv(master_path)
    
    # The 16 features verified for behavioral analysis
    features = [
        "Min Packet Length",
        "Bwd Packet Length Max",
        "Total Length of Bwd Packets",
        "Subflow Bwd Bytes",
        "min_seg_size_forward",
        "Bwd Header Length",
        "Destination Port",
        "Total Length of Fwd Packets",
        "Fwd Packet Length Max",
        "ACK Flag Count",
        "Subflow Fwd Bytes",
        "Total Backward Packets",
        "Subflow Bwd Packets",
        "Max Packet Length",
        "Flow Duration",
        "Fwd Header Length"
    ]

    # --- STEP 1: LOGARITHMIC TRANSFORMATION ---
    # We apply log(1+abs(x)) to handle skewed network distributions
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Applying Logarithmic Transformation...")
    X = df[features].values
    X = np.log1p(np.abs(X)) 
    y = df["Label"].values

    # --- STEP 2: STRATIFIED SPLIT ---
    # 70% Train, 15% Val, 15% Test
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Performing Stratified Split (70/15/15)...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=cfg.RANDOM_SEED
    )
    
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=cfg.RANDOM_SEED
    )

    # --- STEP 3: MINMAX SCALING (The 'Mix') ---
    # This is the "Layer 0" of the hardware pipeline
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fitting MinMaxScaler...")
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    
    # Save scaler for MCU/FPGA export and evaluation
    joblib.dump(scaler, cfg.SCALER_PATH)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scaler saved to {cfg.SCALER_PATH}")

    # Windows Safety: num_workers > 0 can cause issues in some environments
    num_cpus = 0 if os.name == 'nt' else 4 

    train_loader = DataLoader(
        NIDSDataset(X_train, y_train), 
        batch_size=cfg.BATCH_SIZE, 
        shuffle=True, 
        num_workers=num_cpus, 
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    val_loader = DataLoader(
        NIDSDataset(X_val, y_val), 
        batch_size=cfg.BATCH_SIZE, 
        shuffle=False, 
        num_workers=num_cpus, 
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    return train_loader, val_loader

def train_model():
    """
    Orchestrates the BNN training session using parameters defined in config.py.
    Implements a full training loop with F1-Score tracking and Early Stopping.
    """
    print("\n" + "="*50)
    print("BNN HARDWARE-AWARE TRAINING SESSION START")
    print("="*50)
    print(f"Input Features    : {cfg.INPUT_SIZE}")
    print(f"Hidden Layers     : {cfg.HIDDEN_LAYERS}")
    
    res_status = "Enabled (Dense-Residual)" if cfg.USE_RESIDUALS else "Disabled"
    print(f"Residuals         : {res_status}")
    
    print(f"Activation        : {cfg.ACTIVATION_TYPE}")
    print(f"Preprocessing     : Log(1+x) + MinMaxScaler")
    print(f"Optimizer         : {cfg.OPTIMIZER_TYPE} (LR: {cfg.LEARNING_RATE})")
    
    hw_status = f"Enabled (Q8.{cfg.FRACTIONAL_BITS} Fixed-Point)" if cfg.SIMULATE_FIXED_POINT else "Disabled"
    print(f"Hardware Sim      : {hw_status}")
    print(f"Device            : {cfg.DEVICE}")
    print("-" * 50)
    
    # 1. Prepare Data
    train_loader, val_loader = prepare_data()
    
    # 2. Instantiate BNN Model
    model = BWNClassifier().to(cfg.DEVICE)
    
    # 3. Optimizer Factory (Using AdamW for better weight decay in BNNs)
    optimizer = torch.optim.AdamW(
        model.parameters(), 
        lr=cfg.LEARNING_RATE, 
        weight_decay=cfg.WEIGHT_DECAY
    )
    
    # 4. Scheduler Factory (ReduceLROnPlateau based on F1-Score)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='max', 
        factor=cfg.SCHEDULER_FACTOR, 
        patience=cfg.SCHEDULER_PATIENCE
    )
    
    # 5. Loss Factory
    criterion = get_criterion()
    
    # 6. Training Loop Variables
    best_f1 = 0.0
    epochs_no_improve = 0
    
    print(f"\nStarting training for {cfg.NUM_EPOCHS} epochs...")
    print(f"{'Epoch':<8} | {'Loss':<8} | {'Val Acc':<10} | {'Val F1':<10} | {'LR':<10}")
    print("-" * 60)

    try:
        for epoch in range(cfg.NUM_EPOCHS):
            # --- Training Phase ---
            model.train()
            running_loss = 0.0
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(cfg.DEVICE), labels.to(cfg.DEVICE)
                
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                
                # Gradient Clipping to stabilize BNN weight flipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                optimizer.step()
                running_loss += loss.item()

            # --- Validation Phase ---
            model.eval()
            val_preds, val_labels = [], []
            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs = inputs.to(cfg.DEVICE)
                    outputs = model(inputs)
                    # Convert logits to binary predictions
                    preds = (torch.sigmoid(outputs) > 0.5).float().cpu().numpy()
                    val_preds.extend(preds)
                    val_labels.extend(labels.numpy())

            # Calculate Metrics
            epoch_loss = running_loss / len(train_loader)
            epoch_f1 = f1_score(val_labels, val_preds, zero_division=0)
            epoch_acc = accuracy_score(val_labels, val_preds)
            current_lr = optimizer.param_groups[0]['lr']

            # Step Scheduler
            scheduler.step(epoch_f1)

            print(f"{epoch+1:<8} | {epoch_loss:<8.4f} | {epoch_acc:<10.2%} | {epoch_f1:<10.2%} | {current_lr:<10.6f}")

            # --- Save Best Model based on F1-Score ---
            if epoch_f1 > best_f1:
                best_f1 = epoch_f1
                epochs_no_improve = 0
                torch.save(model.state_dict(), cfg.MODEL_SAVE_PATH)
                print(f"  [SAVE] New Best F1-Score detected. Model saved to {cfg.MODEL_SAVE_PATH.name}")
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= cfg.EARLY_STOPPING_PATIENCE:
                    print(f"\n[STOP] Early stopping triggered after {cfg.EARLY_STOPPING_PATIENCE} epochs without F1 improvement.")
                    break

    except KeyboardInterrupt:
        print("\n[WARN] Training interrupted by user.")

    print("\n" + "="*50)
    print("BNN TRAINING SESSION COMPLETE")
    print("="*50)
    print(f"Best Validation F1 : {best_f1:.4%}")
    print(f"Best Model Saved to: {cfg.MODEL_SAVE_PATH}")
    print("="*50 + "\n")

if __name__ == "__main__":
    train_model()