"""
evaluate.py
Loads a trained BNN model and generates a versioned Markdown report and JSON metrics.
Includes Log-Mix preprocessing and hardware-aware inference simulation.
"""

import torch
import json
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime
from pathlib import Path
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Relative imports
from .config import cfg
from .model import BWNClassifier
from .evaluator import Evaluator

class NIDSDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
    def __len__(self): return len(self.y)
    def __getitem__(self, idx): return self.X[idx], self.y[idx]

def append_markdown_report(metrics, path, model_name):
    """
    Generates a professional Markdown report entry for the BNN evaluation.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cm = metrics['confusion_matrix']
    path = Path(path)
    file_exists = path.exists()
    
    layers_str = " -> ".join(map(str, cfg.HIDDEN_LAYERS))
    hw_sim = f"Enabled (Q8.{cfg.FRACTIONAL_BITS} Fixed-Point)" if cfg.SIMULATE_FIXED_POINT else "Disabled"
    
    report_entry = f"""
## Evaluation Run: {timestamp}
**Model File:** `{model_name}`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | {layers_str} |
| **Activation** | {cfg.ACTIVATION_TYPE} |
| **Hardware Simulation** | {hw_sim} |
| **Preprocessing** | Log(1+x) + MinMaxScaler |
| **Features Used** | 16 Behavioral Features |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | {metrics['accuracy']:.6f} |
| **Precision** | {metrics['precision']:.6f} |
| **Recall** | {metrics['recall']:.6f} |
| **F1-Score** | {metrics['f1_score']:.6f} |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | {cm[0][0]} | {cm[0][1]} |
| **Actual Attack** | {cm[1][0]} | {cm[1][1]} |

---
"""
    with open(path, "a") as f:
        if not file_exists:
            f.write("# BNN v2 Training & Evaluation History\n")
            f.write("This report tracks the performance of Binarized Neural Networks using Log-Mix scaling.\n")
        f.write(report_entry)

def main(model_path=None):
    print("\n" + "="*50)
    print("BNN HARDWARE-AWARE EVALUATION START")
    print("="*50)

    # --- 1. Setup Paths ---
    NEW_REPORT_PATH = cfg.REPORT_DIR / "bnn_v2_training_report.md"
    target_path = Path(model_path) if model_path else cfg.MODEL_SAVE_PATH

    if not target_path.exists():
        print(f"[ERROR] Model not found at {target_path}")
        return

    # --- 2. Prepare Data (Must match train.py exactly) ---
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading and Preprocessing Test Data...")
    df = pd.read_csv(cfg.DATA_DIR / "master_dataset.csv")
    
    features = [
        "Min Packet Length", "Bwd Packet Length Max", "Total Length of Bwd Packets",
        "Subflow Bwd Bytes", "min_seg_size_forward", "Bwd Header Length",
        "Destination Port", "Total Length of Fwd Packets", "Fwd Packet Length Max",
        "ACK Flag Count", "Subflow Fwd Bytes", "Total Backward Packets",
        "Subflow Bwd Packets", "Max Packet Length", "Flow Duration", "Fwd Header Length"
    ]

    # Log Transformation
    X = df[features].values
    X = np.log1p(np.abs(X)) 
    y = df["Label"].values

    # Stratified Split (Using same seed as training)
    _, X_temp, _, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=cfg.RANDOM_SEED
    )
    _, X_test, _, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=cfg.RANDOM_SEED
    )

    # Load Scaler
    if not cfg.SCALER_PATH.exists():
        print(f"[ERROR] Scaler not found at {cfg.SCALER_PATH}. Run train.py first.")
        return
    scaler = joblib.load(cfg.SCALER_PATH)
    X_test_scaled = scaler.transform(X_test)
    
    test_loader = DataLoader(NIDSDataset(X_test_scaled, y_test), batch_size=cfg.BATCH_SIZE)

    # --- 3. Load Model ---
    model = BWNClassifier()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading weights from: {target_path.name}")
    model.load_state_dict(torch.load(target_path, map_location=cfg.DEVICE))
    model.to(cfg.DEVICE)
    model.eval()

    # --- 4. Run Inference ---
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running Inference on {len(X_test)} samples...")
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(cfg.DEVICE)
            outputs = model(inputs)
            preds = (torch.sigmoid(outputs) > 0.5).float().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    # --- 5. Calculate Metrics ---
    metrics = {
        'accuracy': accuracy_score(all_labels, all_preds),
        'precision': precision_score(all_labels, all_preds),
        'recall': recall_score(all_labels, all_preds),
        'f1_score': f1_score(all_labels, all_preds),
        'confusion_matrix': confusion_matrix(all_labels, all_preds).tolist()
    }

    # Save JSON metrics
    with open(cfg.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)

    # Append to Markdown Report
    append_markdown_report(metrics, NEW_REPORT_PATH, target_path.name)
    
    print("\n" + "-"*30)
    print(f"Accuracy  : {metrics['accuracy']:.6%}")
    print(f"F1-Score  : {metrics['f1_score']:.6%}")
    print(f"Precision : {metrics['precision']:.6%}")
    print(f"Recall    : {metrics['recall']:.6%}")
    print("-" * 30)
    print("Confusion Matrix:")
    print(np.array(metrics['confusion_matrix']))
    print("-" * 30)
    print(f"Evaluation Complete. Results saved to {NEW_REPORT_PATH}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()