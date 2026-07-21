"""
evaluate.py
Loads a specific trained model and generates a detailed Markdown report and JSON metrics.
"""

import torch
import json
import joblib
import pandas as pd
from datetime import datetime
from pathlib import Path
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split

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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cm = metrics['confusion_matrix']
    file_exists = Path(path).exists()
    
    # Format hidden layers for the report
    layers_str = " -> ".join(map(str, cfg.HIDDEN_LAYERS))
    
    report_entry = f"""
## Run Date: {timestamp}
**Evaluated Model File:** `{model_name}`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Input Features** | {cfg.INPUT_SIZE} |
| **Architecture** | {layers_str} |
| **Activation** | {cfg.ACTIVATION_TYPE} |
| **Optimizer** | {cfg.OPTIMIZER_TYPE} |
| **Batch Size** | {cfg.BATCH_SIZE} |
| **Loss Function** | {cfg.LOSS_TYPE} |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | {metrics['accuracy']:.4f} |
| **Precision** | {metrics['precision']:.4f} |
| **Recall** | {metrics['recall']:.4f} |
| **F1-Score** | {metrics['f1_score']:.4f} |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | {cm[0][0]} | {cm[0][1]} |
| **Actual DDoS** | {cm[1][0]} | {cm[1][1]} |

---
"""
    with open(path, "a") as f:
        if not file_exists:
            f.write("# BWN Training & Evaluation History\n")
        f.write(report_entry)

def main():
    # --- TARGET MODEL PATH ---
    TARGET_MODEL_PATH = Path(r"C:\Users\a\Desktop\BNNana\models\all_runs\run_33_L3_Arch16-16-16_Adam_LR0.001.pth")
    
    print(f"Loading test data for evaluation (Seed: {cfg.RANDOM_SEED})...")
    df = pd.read_csv(cfg.DATA_DIR / "master_dataset.csv")
    
    with open(cfg.ARTIFACT_DIR / "selected_features.json", "r") as f:
        selected_features = json.load(f)

    X = df[selected_features].values
    y = df["Label"].values

    # Replicate the split used in training to isolate the test set
    _, X_temp, _, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=cfg.RANDOM_SEED
    )
    _, X_test, _, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=cfg.RANDOM_SEED
    )

    scaler = joblib.load(cfg.SCALER_PATH)
    X_test_scaled = scaler.transform(X_test)
    test_loader = DataLoader(NIDSDataset(X_test_scaled, y_test), batch_size=cfg.BATCH_SIZE)

    # Instantiate modular model
    model = BWNClassifier()
    
    print(f"Loading weights from: {TARGET_MODEL_PATH.name}")
    model.load_state_dict(torch.load(TARGET_MODEL_PATH, map_location=cfg.DEVICE))
    model.to(cfg.DEVICE)

    print("Running Inference...")
    evaluator = Evaluator(model, cfg.DEVICE)
    metrics = evaluator.get_metrics(test_loader)

    # Save JSON metrics
    with open(cfg.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)

    # Append to Markdown Report
    append_markdown_report(metrics, cfg.REPORT_PATH, TARGET_MODEL_PATH.name)
    print(f"Evaluation Complete. Results appended to {cfg.REPORT_PATH}")

if __name__ == "__main__":
    main()