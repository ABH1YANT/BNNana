"""
config.py
Contains all hyperparameters and architectural constants for the 
Binary Weight Neural Network (BWN).
"""

import torch

class Config:
    # --- Network Architecture ---
    INPUT_SIZE = 17        # Number of selected features from CICDDoS2019
    HIDDEN_SIZE = 16       # Initial implementation: 16 neurons
    OUTPUT_SIZE = 1        # Binary classification (0: Benign, 1: DDoS)
    
    # --- Training Hyperparameters ---
    BATCH_SIZE = 64
    LEARNING_RATE = 0.001
    NUM_EPOCHS = 50
    RANDOM_SEED = 42
    
    # --- Hardware Constraints ---
    # Weights will be binarized to +1 or -1.
    # Inputs are expected to be 8-bit unsigned integers (0-255).
    
    # --- Device Configuration ---
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # --- Paths ---
    MODEL_SAVE_PATH = "models/bwn_model.pt"
    METRICS_PATH = "reports/metrics.json"
    REPORT_PATH = "reports/training_report.md"

# Instantiate for use in other modules
cfg = Config()