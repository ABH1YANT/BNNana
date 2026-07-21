"""
train.py
Entry point for training and hyperparameter tuning.
"""

import torch
import joblib
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
    def __len__(self): return len(self.y)
    def __getitem__(self, idx): return self.X[idx], self.y[idx]

def prepare_data():
    df = pd.read_csv(cfg.DATA_DIR / "master_dataset.csv")
    # Load features used during feature selection
    import json
    with open(cfg.ARTIFACT_DIR / "selected_features.json", "r") as f:
        features = json.load(f)

    X = df[features].values
    y = df["Label"].values

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=cfg.RANDOM_SEED
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=cfg.RANDOM_SEED
    )

    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    
    joblib.dump(scaler, cfg.SCALER_PATH)
    
    return (
        DataLoader(NIDSDataset(X_train, y_train), batch_size=cfg.BATCH_SIZE, shuffle=True),
        DataLoader(NIDSDataset(X_val, y_val), batch_size=cfg.BATCH_SIZE),
    )

def train_model():
    print(f"Configuring Model: {len(cfg.HIDDEN_LAYERS)} Hidden Layers | Device: {cfg.DEVICE}")
    
    train_loader, val_loader = prepare_data()
    
    # 1. Instantiate Model
    model = BWNClassifier().to(cfg.DEVICE)
    
    # 2. Optimizer Factory
    opt_class = getattr(torch.optim, cfg.OPTIMIZER_TYPE)
    optimizer = opt_class(
        model.parameters(), 
        lr=cfg.LEARNING_RATE, 
        weight_decay=cfg.WEIGHT_DECAY
    )
    
    # 3. Scheduler Factory
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='min', 
        factor=cfg.SCHEDULER_FACTOR, 
        patience=cfg.SCHEDULER_PATIENCE
    )
    
    criterion = get_criterion()
    
    # 4. Trainer
    trainer = Trainer(
        model=model, 
        criterion=criterion, 
        optimizer=optimizer, 
        device=cfg.DEVICE, 
        patience=cfg.EARLY_STOPPING_PATIENCE,
        scheduler=scheduler
    )
    
    trainer.fit(train_loader, val_loader, cfg.NUM_EPOCHS)
    
    # Save Final Artifact
    torch.save(model.state_dict(), cfg.MODEL_SAVE_PATH)
    print(f"Training Complete. Model saved to {cfg.MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_model()