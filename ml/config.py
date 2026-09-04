import torch
import json
from pathlib import Path

class Config:
    # --- Paths ---
    ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    ARTIFACT_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    
    # --- Architecture ---
    INPUT_SIZE = 16 # Your 16 behavioral features
    HIDDEN_LAYERS = [32,16,8] # High capacity for 99.99%
    USE_RESIDUALS = True 
    
    # --- Activation ---
    ACTIVATION_TYPE = "BinarySign" 
    ACTIVATION_PARAMS = {} 
    
    # --- Hardware Simulation ---
    SIMULATE_FIXED_POINT = True
    FRACTIONAL_BITS = 8 

    # --- Training Hyperparameters ---
    OUTPUT_SIZE = 1
    BATCH_SIZE = 128        
    NUM_EPOCHS = 100        
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # --- Optimizer & Scheduler ---
    OPTIMIZER_TYPE = "AdamW"
    LEARNING_RATE = 0.0008
    WEIGHT_DECAY = 0.02
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 5
    
    # --- Early Stopping & Loss ---
    EARLY_STOPPING_PATIENCE = 15
    LOSS_TYPE = "BCEWithLogits"

    # --- Output Artifacts ---
    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bnn_v6_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler_bnn.pkl"
    METRICS_PATH = REPORT_DIR / "metrics.json"
    REPORT_PATH = REPORT_DIR / "bnn_v6_training_report_luts.md"

cfg = Config()