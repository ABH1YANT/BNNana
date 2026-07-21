import torch
import json
from pathlib import Path

class Config:
    ROOT = Path(r"C:\Users\a\Desktop\BNNana")
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    _feat_file = ARTIFACT_DIR / "selected_features.json"
    INPUT_SIZE = len(json.load(open(_feat_file))) if _feat_file.exists() else 17
    
    # --- UPDATED PARAMETERS ---
    HIDDEN_LAYERS = [16, 16, 16]
    OPTIMIZER_TYPE = "Adam"
    LEARNING_RATE = 0.001
    ACTIVATION_TYPE = "Hardtanh"
    ACTIVATION_PARAMS = {"min_val": 0.0, "max_val": 1.0}
    # --------------------------

    OUTPUT_SIZE = 1
    BATCH_SIZE = 64
    NUM_EPOCHS = 40 
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    WEIGHT_DECAY = 1e-5
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 3
    EARLY_STOPPING_PATIENCE = 8
    LOSS_TYPE = "BCEWithLogits"
    POS_WEIGHT = 1.0  # Slight boost for DDoS class

    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bwn_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler.pkl"
    METRICS_PATH = REPORT_DIR / "metrics.json"
    REPORT_PATH = REPORT_DIR / "training_report.md"

cfg = Config()