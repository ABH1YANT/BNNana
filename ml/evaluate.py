"""
evaluate.py
Loads a trained BNN model and evaluates it on the held-out test set.
Aligned with BNN v6 (Dense Residuals starting after Layer 1) and Q1.8 simulation.
"""

import torch
import json
import pandas as pd
import numpy as np
import os
from datetime import datetime
from pathlib import Path
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# Relative imports
from .config import cfg
from .model import BNNClassifier

# ==============================================================
# 1. DATASET
# ==============================================================

class NIDSDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ==============================================================
# 2. MARKDOWN REPORT
# ==============================================================

def append_markdown_report(metrics, path, model_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cm = metrics["confusion_matrix"]
    path = Path(path)
    file_exists = path.exists()

    layers_str = " -> ".join(map(str, cfg.HIDDEN_LAYERS))
    hw_sim = f"Enabled (Q1.8 Fixed-Point)" if cfg.SIMULATE_FIXED_POINT else "Disabled"
    
    # Documentation of the specific v6 logic
    res_logic = "Dense Concatenation (Binary Only)" if cfg.USE_RESIDUALS else "Standard Sequential"
    input_logic = "Excluded from Residuals (Consumed by L1)" if cfg.USE_RESIDUALS else "N/A"

    report_entry = f"""
## Evaluation Run: {timestamp}
**Model File:** `{model_name}`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | {layers_str} |
| **Residual Logic** | {res_logic} |
| **Input Propagation** | {input_logic} |
| **Hardware Sim** | {hw_sim} |
| **Input Features** | {cfg.INPUT_SIZE} |
| **Activation** | {cfg.ACTIVATION_TYPE} |

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
    with open(path, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("# BNN v6 Evaluation History\n")
            f.write("Tracking performance of Dense-Residual BNNs with Q1.8 Input Quantization.\n")
        f.write(report_entry)

# ==============================================================
# 3. MAIN
# ==============================================================

def main(model_path=None):
    print("\n" + "=" * 60)
    print("BNN HARDWARE-AWARE EVALUATION (v6 Dense)")
    print("=" * 60)

    # 1. Determine Model Path
    target_path = Path(model_path) if model_path else cfg.MODEL_SAVE_PATH
    if not target_path.exists():
        print(f"[ERROR] Model not found: {target_path}")
        return

    # 2. Load Dynamic Features
    feat_file = cfg.ARTIFACT_DIR / "selected_features.json"
    if not feat_file.exists():
        raise FileNotFoundError(f"Feature definition missing: {feat_file}")
    
    with open(feat_file, "r") as f:
        features = json.load(f)

    # 3. Load Dataset
    data_path = cfg.DATA_DIR / "scaled_dataset.csv"
    if not data_path.exists():
        print(f"[ERROR] Processed dataset not found: {data_path}")
        return

    df = pd.read_csv(data_path)
    X = df[features].values.astype(np.float32)
    y = df["Label"].values.astype(np.float32)

    # 4. Replicate 70/15/15 Split (Must match train.py exactly)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=cfg.RANDOM_SEED
    )
    _, X_test, _, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=cfg.RANDOM_SEED
    )

    # Windows safety: num_workers=0 for evaluation
    test_loader = DataLoader(NIDSDataset(X_test, y_test), batch_size=cfg.BATCH_SIZE, shuffle=False, num_workers=0)

    # 5. Load BNN
    model = BNNClassifier()
    model.load_state_dict(torch.load(target_path, map_location=cfg.DEVICE))
    model.to(cfg.DEVICE).eval()
    print(f"Model loaded: {target_path.name}")

    # 6. Inference
    print(f"Running inference on {len(X_test):,} samples...")
    all_preds, all_labels = [], []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(cfg.DEVICE)
            logits = model(inputs)
            
            # Hardware-aligned decision: Logit > 0 is Attack (1)
            # This mirrors the FPGA sign-bit check
            preds = (logits > 0).int().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy().astype(int))

    # 7. Metrics
    metrics = {
        "accuracy": accuracy_score(all_labels, all_preds),
        "precision": precision_score(all_labels, all_preds, zero_division=0),
        "recall": recall_score(all_labels, all_preds, zero_division=0),
        "f1_score": f1_score(all_labels, all_preds, zero_division=0),
        "confusion_matrix": confusion_matrix(all_labels, all_preds, labels=[0, 1]).tolist()
    }

    # 8. Save and Report
    with open(cfg.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    append_markdown_report(metrics, cfg.REPORT_PATH, target_path.name)

    print("\n" + "=" * 60)
    print(f"Accuracy  : {metrics['accuracy']:.6%}")
    print(f"F1-Score  : {metrics['f1_score']:.6%}")
    print(f"Precision : {metrics['precision']:.6%}")
    print(f"Recall    : {metrics['recall']:.6%}")
    print("\nConfusion Matrix:")
    print(np.array(metrics["confusion_matrix"]))
    print(f"\nReport updated: {cfg.REPORT_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    # Allow passing a specific model path via command line
    cmd_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(cmd_path)