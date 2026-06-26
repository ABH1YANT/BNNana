"""
train.py
Entry point for training and hyperparameter tuning.
"""

import torch
from torch.utils.data import DataLoader
from config import cfg
from model import BWNClassifier
from loss import get_criterion
from trainer import Trainer

def run_experiment(hidden_size, lr, opt_type, batch_size):
    print(f"\n--- Starting Experiment: Hidden={hidden_size}, LR={lr}, Opt={opt_type} ---")
    
    # 1. Setup Model
    model = BWNClassifier(cfg.INPUT_SIZE, hidden_size, cfg.OUTPUT_SIZE)
    
    # 2. Setup Data (Placeholders - ML Engineer 2 provides these)
    # train_loader = ...
    # val_loader = ...
    
    # 3. Setup Optimizer
    if opt_type == "Adam":
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    else:
        optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
        
    # 4. Setup Loss (Add pos_weight if classes are imbalanced)
    criterion = get_criterion()
    
    # 5. Train
    trainer = Trainer(model, criterion, optimizer, cfg.DEVICE, patience=7)
    # trainer.fit(train_loader, val_loader, cfg.NUM_EPOCHS)

if __name__ == "__main__":
    # Example of a quick sweep you can run:
    for h_size in [16, 32, 64]:
        for learning_rate in [1e-2, 1e-3]:
            run_experiment(h_size, learning_rate, "Adam", 64)