"""
trainer.py
The training engine with Early Stopping, ReduceLROnPlateau support, 
weight clipping, and F1-based checkpointing.
"""

import torch
import json
import numpy as np
from sklearn.metrics import f1_score, accuracy_score
from .config import cfg
from .layers import BinaryLinear

class Trainer:
    def __init__(self, model, criterion, optimizer, device, patience=10, scheduler=None):
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.patience = patience
        self.scheduler = scheduler
        
        # Checkpointing based on F1-Score (higher is better)
        self.best_f1 = 0.0
        self.counter = 0
        self.history = {
            "train_loss": [], 
            "val_loss": [], 
            "val_f1": [], 
            "val_acc": []
        }

    def clip_weights(self):
        """
        BNN Essential: Clamps latent weights to [-1, 1] after each update.
        This prevents latent weights from drifting too far from the 
        zero-threshold, keeping the model responsive to gradients.
        """
        for module in self.model.modules():
            if isinstance(module, BinaryLinear):
                module.weight.data.clamp_(-1.0, 1.0)

    def train_epoch(self, train_loader):
        self.model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(self.device), labels.to(self.device).float()
            
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            
            # Ensure shapes match: [batch_size]
            loss = self.criterion(outputs, labels.view_as(outputs))
            
            loss.backward()
            self.optimizer.step()
            
            # --- BNN SPECIFIC STEP ---
            self.clip_weights()
            
            running_loss += loss.item()
            
        return running_loss / len(train_loader)

    def validate(self, val_loader):
        self.model.eval()
        running_loss = 0.0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device).float()
                outputs = self.model(inputs)
                
                loss = self.criterion(outputs, labels.view_as(outputs))
                running_loss += loss.item()
                
                # Convert logits to binary predictions
                preds = (torch.sigmoid(outputs) > 0.5).float().cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().numpy())
        
        avg_loss = running_loss / len(val_loader)
        avg_f1 = f1_score(all_labels, all_preds, zero_division=0)
        avg_acc = accuracy_score(all_labels, all_preds)
        
        return avg_loss, avg_f1, avg_acc

    def fit(self, train_loader, val_loader, epochs):
        print(f"Starting BNN training on {self.device}...")
        print(f"{'Epoch':<8} | {'Loss':<8} | {'Val F1':<8} | {'Val Acc':<8} | {'LR':<8}")
        print("-" * 55)

        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss, val_f1, val_acc = self.validate(val_loader)
            
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            self.history["val_f1"].append(val_f1)
            self.history["val_acc"].append(val_acc)
            
            current_lr = self.optimizer.param_groups[0]['lr']
            print(f"{epoch+1:<8} | {train_loss:<8.4f} | {val_f1:<8.4f} | {val_acc:<8.4f} | {current_lr:<8.6f}")
            
            # Scheduler step (ReduceLROnPlateau monitors F1 or Loss)
            if self.scheduler is not None:
                # If scheduler is configured for 'max', give it F1. If 'min', give it Loss.
                if self.scheduler.mode == 'max':
                    self.scheduler.step(val_f1)
                else:
                    self.scheduler.step(val_loss)
            
            # Checkpointing based on F1-Score
            if val_f1 > self.best_f1:
                self.best_f1 = val_f1
                self.counter = 0
                torch.save(self.model.state_dict(), cfg.MODEL_SAVE_PATH)
                # print(f"  [Save] Best F1 updated: {val_f1:.4f}")
            else:
                self.counter += 1
                if self.counter >= self.patience:
                    print(f"\n[Early Stopping] Triggered at epoch {epoch+1}. Best F1: {self.best_f1:.4f}")
                    break

        # Load best weights before finishing
        if cfg.MODEL_SAVE_PATH.exists():
            self.model.load_state_dict(torch.load(cfg.MODEL_SAVE_PATH))
            
        with open(cfg.METRICS_PATH, "w") as f:
            json.dump(self.history, f, indent=4)
            
        return self.history