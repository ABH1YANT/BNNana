"""
train.py
Entry point for training the Binarized Neural Network (BNN).
Handles data scaling, stratified splitting, and hardware-aware training orchestration.
"""

import torch
import joblib
import json
import pandas as pd
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from .config import cfg
from .model import BWNClassifier
from .loss import get_criterion
from .trainer import Trainer

class NIDSDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
    def __len__(self): 
        return len(self.y)
    def __getitem__(self, idx): 
        return self.X[idx], self.y[idx]

def prepare_data():
    """
    Loads master dataset, applies feature selection, performs stratified 
    splitting, and fits the MinMaxScaler (Layer 0).
    """
    print(f"Loading dataset from: {cfg.DATA_DIR}")
    
    # Load the master processed CSV
    master_path = cfg.DATA_DIR / "master_dataset.csv"
    if not master_path.exists():
        raise FileNotFoundError(f"Master dataset not found at {master_path}")
        
    df = pd.read_csv(master_path)
    
    # Load the specific features selected for this project
    if not cfg.ARTIFACT_DIR.joinpath("selected_features.json").exists():
        raise FileNotFoundError("selected_features.json missing from artifacts folder.")
        
    with open(cfg.ARTIFACT_DIR / "selected_features.json", "r") as f:
        features = json.load(f)

    X = df[features].values
    y = df["Label"].values

    # 1. Stratified split: 70% Train, 30% Temp (Val/Test)
    # Stratification ensures DDoS/Benign ratio is preserved across sets
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=cfg.RANDOM_SEED
    )
    
    # 2. Split Temp into 50% Val, 50% Test (15% of total each)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=cfg.RANDOM_SEED
    )

    # 3. MinMaxScaler (The "Layer 0" of the hardware pipeline)
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    # Note: X_test is transformed in evaluate.py using the saved scaler
    
    # Save scaler for MCU/FPGA export and evaluation
    joblib.dump(scaler, cfg.SCALER_PATH)
    print(f"Scaler saved to {cfg.SCALER_PATH}")

    train_loader = DataLoader(NIDSDataset(X_train, y_train), batch_size=cfg.BATCH_SIZE, shuffle=True, num_workers=2, pin_memory=True, persistent_workers=True)
    val_loader = DataLoader(NIDSDataset(X_val, y_val), batch_size=cfg.BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True, persistent_workers=True,)
    
    return train_loader, val_loader

def train_model():
    """
    Orchestrates the BNN training session using parameters defined in config.py.
    """
    print("\n" + "="*40)
    print("BNN TRAINING SESSION START")
    print("="*40)
    print(f"Architecture    : {cfg.INPUT_SIZE} -> {cfg.HIDDEN_LAYERS} -> {cfg.OUTPUT_SIZE}")
    print(f"Activation      : {cfg.ACTIVATION_TYPE}")
    print(f"Optimizer       : {cfg.OPTIMIZER_TYPE} (LR: {cfg.LEARNING_RATE})")
    print(f"Loss Function   : {cfg.LOSS_TYPE}")
    
    hw_status = f"Enabled (Q8.{cfg.FRACTIONAL_BITS})" if cfg.SIMULATE_FIXED_POINT else "Disabled"
    print(f"Hardware Sim    : {hw_status}")
    print(f"Device          : {cfg.DEVICE}")
    print("-" * 40)
    
    # 1. Prepare Data
    train_loader, val_loader = prepare_data()
    
    # 2. Instantiate BNN Model
    model = BWNClassifier().to(cfg.DEVICE)
    
    # 3. Optimizer Factory
    opt_class = getattr(torch.optim, cfg.OPTIMIZER_TYPE)
    optimizer = opt_class(
        model.parameters(), 
        lr=cfg.LEARNING_RATE, 
        weight_decay=cfg.WEIGHT_DECAY
    )
    
    # 4. Scheduler Factory (ReduceLROnPlateau)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='min', 
        factor=cfg.SCHEDULER_FACTOR, 
        patience=cfg.SCHEDULER_PATIENCE
    )
    
    # 5. Loss Factory
    criterion = get_criterion()
    
    # 6. Training Engine (Handles weight clipping and STE)
    trainer = Trainer(
        model=model, 
        criterion=criterion, 
        optimizer=optimizer, 
        device=cfg.DEVICE, 
        patience=cfg.EARLY_STOPPING_PATIENCE,
        scheduler=scheduler
    )
    
    # 7. Run Fit
    trainer.fit(train_loader, val_loader, cfg.NUM_EPOCHS)
    
    print("\n[OK] Training Complete.")
    print(f"Best Model Saved to: {cfg.MODEL_SAVE_PATH}")
    print("="*40 + "\n")

if __name__ == "__main__":
    train_model()