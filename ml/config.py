
import torch
import json
from pathlib import Path

class Config:
    ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    _feat_file = ARTIFACT_DIR / "selected_features.json"
    INPUT_SIZE = len(json.load(open(_feat_file))) if _feat_file.exists() else 17
    
    HIDDEN_LAYERS = [32, 32, 16, 16, 8]
    OPTIMIZER_TYPE = "SGD"
    LEARNING_RATE = 0.0005
    
    ACTIVATION_TYPE = "BinarySign" 
    ACTIVATION_PARAMS = {} 
    
    SIMULATE_FIXED_POINT = True
    FRACTIONAL_BITS = 8  

    OUTPUT_SIZE = 1
    BATCH_SIZE = 1024
    NUM_EPOCHS = 50        
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    WEIGHT_DECAY = 1e-5
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 4
    EARLY_STOPPING_PATIENCE = 10
    LOSS_TYPE = "BCEWithLogits"
    POS_WEIGHT = 1.2

    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bwn_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler.pkl"
    METRICS_PATH = REPORT_DIR / "metrics.json"
    REPORT_PATH = REPORT_DIR / "bnn_v1_training_report.md"

cfg = Config()
