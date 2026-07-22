import torch
import json
from pathlib import Path

class Config:
    # --- Dynamic Path Resolution ---
    # Path(__file__) is .../BNNana/ml/config.py
    # .parent is .../BNNana/ml
    # .parent.parent is .../BNNana (The Project Root)
    ROOT = Path(__file__).resolve().parent.parent
    
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    # Ensure directories exist (Colab/Linux friendly)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Feature Handling ---
    _feat_file = ARTIFACT_DIR / "selected_features.json"
    if _feat_file.exists():
        with open(_feat_file, "r") as f:
            INPUT_SIZE = len(json.load(f))
    else:
        INPUT_SIZE = 17
        # We don't print here to avoid spamming during sweeps
    
    # --- BNN Architecture ---
    HIDDEN_LAYERS = [16, 16, 16]
    OUTPUT_SIZE = 1
    
    # BNN Specific: BinarySign uses the Sign function with STE
    ACTIVATION_TYPE = "BinarySign" 
    ACTIVATION_PARAMS = {} 

    # --- Hardware-Aware Training (FPGA Simulation) ---
    SIMULATE_FIXED_POINT = True
    FRACTIONAL_BITS = 8  
    
    # --- Training Hyperparameters ---
    OPTIMIZER_TYPE = "Adam"
    LEARNING_RATE = 0.001
    BATCH_SIZE = 64
    NUM_EPOCHS = 60        
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Regularization & Scheduling
    WEIGHT_DECAY = 1e-5
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 4
    EARLY_STOPPING_PATIENCE = 12
    
    # Loss Function
    LOSS_TYPE = "BCEWithLogits"
    POS_WEIGHT = 1.2

    # --- Output Paths (Derived from ROOT) ---
    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bwn_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler.pkl"
    METRICS_PATH = REPORT_DIR / "metrics.json"
    REPORT_PATH = REPORT_DIR / "training_report.md"

cfg = Config()