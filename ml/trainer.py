"""
trainer.py
The training engine with Early Stopping, ReduceLROnPlateau support, 
and model checkpointing.
"""

import torch
import json
from .config import cfg

class Trainer:
    def __init__(self, model, criterion, optimizer, device, patience=5, scheduler=None):
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.patience = patience
        self.scheduler = scheduler
        self.best_val_loss = float('inf')
        self.counter = 0
        self.history = {"train_loss": [], "val_loss": []}

    def train_epoch(self, train_loader):
        self.model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(self.device), labels.to(self.device).float()
            
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            
            # Ensure shapes match: [batch_size] vs [batch_size]
            loss = self.criterion(outputs, labels.view_as(outputs))
            
            loss.backward()
            self.optimizer.step()
            running_loss += loss.item()
            
        return running_loss / len(train_loader)

    def validate(self, val_loader):
        self.model.eval()
        running_loss = 0.0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device).float()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels.view_as(outputs))
                running_loss += loss.item()
        return running_loss / len(val_loader)

    def fit(self, train_loader, val_loader, epochs):
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)
            
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            
            current_lr = self.optimizer.param_groups[0]['lr']
            print(f"Epoch {epoch+1:02d}/{epochs} | Train: {train_loss:.4f} | Val: {val_loss:.4f} | LR: {current_lr:.6f}")
            
            if self.scheduler is not None:
                self.scheduler.step(val_loss)
            
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.counter = 0
                torch.save(self.model.state_dict(), cfg.MODEL_SAVE_PATH)
            else:
                self.counter += 1
                if self.counter >= self.patience:
                    print(f"\n[Early Stopping] Triggered at epoch {epoch+1}")
                    break

        if cfg.MODEL_SAVE_PATH.exists():
            self.model.load_state_dict(torch.load(cfg.MODEL_SAVE_PATH))
            
        # Save history to metrics.json
        with open(cfg.METRICS_PATH, "w") as f:
            json.dump(self.history, f, indent=4)
            
        return self.history