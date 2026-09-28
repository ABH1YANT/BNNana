import torch
import json
from pathlib import Path

class Config:
    # --- Paths ---
    ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    # Ensure directories exist for artifacts and logs
    ARTIFACT_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    
    # --- Architecture ---
    # Dynamically load input size from the 16 selected features
    _feat_file = ARTIFACT_DIR / "selected_features.json"
    if _feat_file.exists():
        with open(_feat_file, "r") as f:
            INPUT_SIZE = len(json.load(f))
    else:
        INPUT_SIZE = 16 

    # Architecture: 16 -> 32 -> 16 -> (32+16) -> 8 -> (32+16+8) -> 1
    HIDDEN_LAYERS = [64,64,32] 
    
    # In model.py, this now triggers Dense Concatenation after Layer 2
    USE_RESIDUALS = True
    
    # --- Activation ---
    # BinarySign = Sign(x) -> {-1, +1}
    ACTIVATION_TYPE = "BinarySign" 
    ACTIVATION_PARAMS = {} 
    
    # --- Hardware Simulation (Q1.8) ---
    SIMULATE_FIXED_POINT = True
    # FRACTIONAL_BITS = 8 defines the ".8" in Q1.8
    # The model.py Quantizer will clamp to [-1.0, 1.0)
    FRACTIONAL_BITS = 8 

    # --- Training Hyperparameters ---
    OUTPUT_SIZE = 1
    BATCH_SIZE = 128        # Increased for gradient stability in Dense BNNs
    NUM_EPOCHS = 100        
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # --- Optimizer & Scheduler ---
    OPTIMIZER_TYPE = "AdamW"
    LEARNING_RATE = 0.0008  # Slightly lower for deep binarized stacks
    WEIGHT_DECAY = 0.02     # L2 regularization for latent weights
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 5
    
    # --- Early Stopping & Loss ---
    EARLY_STOPPING_PATIENCE = 15
    LOSS_TYPE = "BCEWithLogits"

    # --- Output Artifacts ---
    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bnn_v7_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler_bnn.pkl"
    METRICS_PATH = REPORT_DIR / "metrics_v7.json"
    REPORT_PATH = REPORT_DIR / "bnn_v7_training_report_dense.md"

cfg = Config()