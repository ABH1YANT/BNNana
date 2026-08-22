import torch
import json
from pathlib import Path

class Config:
    # --- Paths ---
    ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    # Ensure directories exist
    ARTIFACT_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    
    # --- Architecture ---
    _feat_file = ARTIFACT_DIR / "selected_features.json"
    INPUT_SIZE = len(json.load(open(_feat_file))) if _feat_file.exists() else 17
    
    # Updated to 4 layers of 16 neurons each
    HIDDEN_LAYERS = [8, 16, 32]
    
    # Toggle for Residual/Skip Connections
    USE_RESIDUALS = True 
    
    # --- Activation ---
    # Options: "BinarySign", "ReLU", "Hardtanh"
    ACTIVATION_TYPE = "BinarySign" 
    ACTIVATION_PARAMS = {} 
    
    # --- Hardware Simulation (FPGA Mirroring) ---
    SIMULATE_FIXED_POINT = True
    FRACTIONAL_BITS = 8  # Q8.8 format

    # --- Training Hyperparameters ---
    OUTPUT_SIZE = 1
    BATCH_SIZE = 64
    NUM_EPOCHS = 50        
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # --- Optimizer & Scheduler ---
    OPTIMIZER_TYPE = "Adam"
    LEARNING_RATE = 0.0005
    WEIGHT_DECAY = 1e-5
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 3
    
    # --- Early Stopping & Loss ---
    EARLY_STOPPING_PATIENCE = 10
    LOSS_TYPE = "BCEWithLogits"
    POS_WEIGHT = 1.2 # Handle slight class imbalance

    # --- Output Artifacts ---
    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bnn_v2_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler.pkl"
    METRICS_PATH = REPORT_DIR / "metrics.json"
    REPORT_PATH = REPORT_DIR / "bnn_v2_training_report.md"

cfg = Config()