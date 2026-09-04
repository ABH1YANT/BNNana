"""
evaluate.py

Loads a trained BNN model and evaluates it on the held-out test set.

IMPORTANT:
The test dataset is already preprocessed using:

    Raw feature
        ↓
    LUT bucket
        ↓
    Representative value
        ↓
    log1p
        ↓
    MinMax [0,1]
        ↓
    scaled_dataset.csv

Therefore NO additional Log transformation or MinMax scaling
is performed here.
"""

import torch
import json
import pandas as pd
import numpy as np

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
from .model import BWNClassifier


# ==============================================================
# 1. DATASET
# ==============================================================

class NIDSDataset(Dataset):

    def __init__(self, X, y):

        self.X = torch.tensor(
            X,
            dtype=torch.float32
        )

        self.y = torch.tensor(
            y,
            dtype=torch.float32
        )

    def __len__(self):

        return len(self.y)

    def __getitem__(self, idx):

        return (
            self.X[idx],
            self.y[idx]
        )


# ==============================================================
# 2. MARKDOWN REPORT
# ==============================================================

def append_markdown_report(
    metrics,
    path,
    model_name
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cm = metrics["confusion_matrix"]

    path = Path(path)

    file_exists = path.exists()

    layers_str = " -> ".join(
        map(str, cfg.HIDDEN_LAYERS)
    )

    hw_sim = (
        f"Enabled (Q8.{cfg.FRACTIONAL_BITS} Fixed-Point)"
        if cfg.SIMULATE_FIXED_POINT
        else "Disabled"
    )

    report_entry = f"""
## Evaluation Run: {timestamp}

**Model File:** `{model_name}`

### 1. System Configuration

| Parameter | Value |
| :--- | :--- |
| **Architecture** | {layers_str} |
| **Activation** | {cfg.ACTIVATION_TYPE} |
| **Hardware Simulation** | {hw_sim} |
| **Preprocessing** | LUT + Representative + log1p + MinMax |
| **Dataset** | scaled_dataset.csv |
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

    with open(
        path,
        "a",
        encoding="utf-8"
    ) as f:

        if not file_exists:

            f.write(
                "# BNN v2 Training & Evaluation History\n"
            )

            f.write(
                "This report tracks Binarized Neural Network "
                "performance using LUT-based preprocessing.\n"
            )

        f.write(
            report_entry
        )


# ==============================================================
# 3. MAIN
# ==============================================================

def main(model_path=None):

    print("\n" + "=" * 60)

    print(
        "BNN HARDWARE-AWARE EVALUATION"
    )

    print("=" * 60)

    # ==========================================================
    # STEP 1 — MODEL PATH
    # ==========================================================

    target_path = (
        Path(model_path)
        if model_path
        else cfg.MODEL_SAVE_PATH
    )

    if not target_path.exists():

        print(
            f"[ERROR] Model not found:\n"
            f"{target_path}"
        )

        return

    print(
        f"\nModel: {target_path.name}"
    )

    # ==========================================================
    # STEP 2 — LOAD SCALED DATASET
    # ==========================================================

    print(
        f"\n[{datetime.now().strftime('%H:%M:%S')}] "
        f"Loading LUT-processed dataset..."
    )

    data_path = (
        cfg.DATA_DIR
        / "scaled_dataset.csv"
    )

    if not data_path.exists():

        print(
            f"[ERROR] Processed dataset not found:\n"
            f"{data_path}"
        )

        return

    df = pd.read_csv(
        data_path
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    # ==========================================================
    # STEP 3 — EXACT 16 FEATURES
    # ==========================================================

    features = [

        "Min Packet Length",
        "Bwd Packet Length Max",
        "Total Length of Bwd Packets",
        "Subflow Bwd Bytes",
        "min_seg_size_forward",
        "Bwd Header Length",
        "Destination Port",
        "Total Length of Fwd Packets",
        "Fwd Packet Length Max",
        "ACK Flag Count",
        "Subflow Fwd Bytes",
        "Total Backward Packets",
        "Subflow Bwd Packets",
        "Max Packet Length",
        "Flow Duration",
        "Fwd Header Length"

    ]

    # ==========================================================
    # STEP 4 — LOAD ALREADY PROCESSED FEATURES
    # ==========================================================

    X = df[
        features
    ].values.astype(
        np.float32
    )

    y = df[
        "Label"
    ].values.astype(
        np.float32
    )

    print(
        "\nPreprocessing:"
    )

    print(
        "  LUT preprocessing : ALREADY DONE"
    )

    print(
        "  Log1p             : ALREADY DONE"
    )

    print(
        "  MinMax            : ALREADY DONE"
    )

    print(
        "  Additional scaling: NONE"
    )

    # ==========================================================
    # STEP 5 — FEATURE RANGE CHECK
    # ==========================================================

    print(
        "\nProcessed feature ranges:"
    )

    for i, feature in enumerate(features):

        print(
            f"{feature:35s} "
            f"min={X[:, i].min():.6f} "
            f"max={X[:, i].max():.6f}"
        )

    # ==========================================================
    # STEP 6 — SAME 70/15/15 SPLIT AS TRAINING
    # ==========================================================

    print(
        f"\n[{datetime.now().strftime('%H:%M:%S')}] "
        f"Creating identical 70/15/15 split..."
    )

    X_train, X_temp, y_train, y_temp = train_test_split(

        X,
        y,

        test_size=0.30,

        stratify=y,

        random_state=cfg.RANDOM_SEED
    )

    X_val, X_test, y_val, y_test = train_test_split(

        X_temp,
        y_temp,

        test_size=0.50,

        stratify=y_temp,

        random_state=cfg.RANDOM_SEED
    )

    print(
        f"Train      : {len(X_train):,}"
    )

    print(
        f"Validation : {len(X_val):,}"
    )

    print(
        f"Test       : {len(X_test):,}"
    )

    # ==========================================================
    # STEP 7 — TEST LOADER
    # ==========================================================

    test_loader = DataLoader(

        NIDSDataset(
            X_test,
            y_test
        ),

        batch_size=cfg.BATCH_SIZE,

        shuffle=False
    )

    # ==========================================================
    # STEP 8 — LOAD BNN
    # ==========================================================

    print(
        f"\n[{datetime.now().strftime('%H:%M:%S')}] "
        f"Loading BNN model..."
    )

    model = BWNClassifier()

    model.load_state_dict(
        torch.load(
            target_path,
            map_location=cfg.DEVICE
        )
    )

    model.to(
        cfg.DEVICE
    )

    model.eval()

    print(
        f"Model loaded: {target_path.name}"
    )

    # ==========================================================
    # STEP 9 — INFERENCE
    # ==========================================================

    print(
        f"\n[{datetime.now().strftime('%H:%M:%S')}] "
        f"Running inference on "
        f"{len(X_test):,} test samples..."
    )

    all_preds = []
    all_labels = []

    with torch.no_grad():

        for inputs, labels in test_loader:

            inputs = inputs.to(
                cfg.DEVICE
            )

            outputs = model(
                inputs
            )

            preds = (
                torch.sigmoid(outputs)
                > 0.5
            ).float().cpu().numpy()

            all_preds.extend(
                preds
            )

            all_labels.extend(
                labels.numpy()
            )

    # ==========================================================
    # STEP 10 — METRICS
    # ==========================================================

    metrics = {

        "accuracy":
            accuracy_score(
                all_labels,
                all_preds
            ),

        "precision":
            precision_score(
                all_labels,
                all_preds,
                zero_division=0
            ),

        "recall":
            recall_score(
                all_labels,
                all_preds,
                zero_division=0
            ),

        "f1_score":
            f1_score(
                all_labels,
                all_preds,
                zero_division=0
            ),

        "confusion_matrix":
            confusion_matrix(
                all_labels,
                all_preds,
                labels=[0, 1]
            ).tolist()
    }

    # ==========================================================
    # STEP 11 — SAVE JSON
    # ==========================================================

    with open(
        cfg.METRICS_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4
        )

    # ==========================================================
    # STEP 12 — MARKDOWN REPORT
    # ==========================================================

    report_path = (
        cfg.REPORT_DIR
        / "bnn_v5_training_report.md"
    )

    append_markdown_report(
        metrics,
        report_path,
        target_path.name
    )

    # ==========================================================
    # STEP 13 — PRINT RESULTS
    # ==========================================================

    print("\n" + "=" * 60)

    print(
        "FINAL BNN TEST RESULTS"
    )

    print("=" * 60)

    print(
        f"\nAccuracy  : "
        f"{metrics['accuracy']:.6%}"
    )

    print(
        f"F1-Score  : "
        f"{metrics['f1_score']:.6%}"
    )

    print(
        f"Precision : "
        f"{metrics['precision']:.6%}"
    )

    print(
        f"Recall    : "
        f"{metrics['recall']:.6%}"
    )

    print(
        "\nConfusion Matrix:"
    )

    print(
        np.array(
            metrics["confusion_matrix"]
        )
    )

    print(
        f"\nMetrics saved to:"
    )

    print(
        cfg.METRICS_PATH
    )

    print(
        f"\nReport saved to:"
    )

    print(
        report_path
    )

    print("\n" + "=" * 60)

    print(
        "Evaluation Complete."
    )

    print("=" * 60)


# ==============================================================
# RUN
# ==============================================================

if __name__ == "__main__":

    main()