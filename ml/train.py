"""
trainer.py

Entry point for training the Binarized Neural Network (BNN).

Preprocessing:
    The dataset is ALREADY processed by the LUT pipeline:
        Raw feature
            ↓
        LUT bucket
            ↓
        Representative value
            ↓
        log1p
            ↓
        MinMax [0,1]

Therefore this trainer performs NO additional preprocessing.

The BNN receives the exact same 16 processed features
used by the teacher model.
"""

import torch
import pandas as pd
import numpy as np
import os

from datetime import datetime

from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score,
    accuracy_score,
    precision_score,
    recall_score
)

# Relative imports from project
from .config import cfg
from .model import BWNClassifier
from .loss import get_criterion


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
# 2. PREPARE DATA
# ==============================================================

def prepare_data():

    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] "
        f"Loading LUT-processed dataset..."
    )

    # ----------------------------------------------------------
    # IMPORTANT:
    # scaled_dataset.csv already contains:
    #
    # LUT representative
    #       ↓
    # log1p
    #       ↓
    # MinMax
    #
    # DO NOT apply Log or MinMax again.
    # ----------------------------------------------------------

    data_path = (
        cfg.DATA_DIR
        / "scaled_dataset.csv"
    )

    if not data_path.exists():

        raise FileNotFoundError(
            f"\nProcessed dataset not found:\n"
            f"{data_path}"
        )

    df = pd.read_csv(
        data_path
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    # ==========================================================
    # EXACT 16 FEATURES
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

    # ----------------------------------------------------------
    # Verify all features exist
    # ----------------------------------------------------------

    missing_features = [
        feature
        for feature in features
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing features from scaled_dataset.csv:\n"
            + "\n".join(missing_features)
        )

    # ----------------------------------------------------------
    # Verify input size
    # ----------------------------------------------------------

    if len(features) != cfg.INPUT_SIZE:

        raise ValueError(
            f"Feature count ({len(features)}) "
            f"does not match cfg.INPUT_SIZE "
            f"({cfg.INPUT_SIZE})"
        )

    # ==========================================================
    # LOAD ALREADY-SCALED FEATURES
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

    # ==========================================================
    # FEATURE RANGE CHECK
    # ==========================================================

    print("\nProcessed feature range check:")

    for i, feature in enumerate(features):

        print(
            f"{feature:35s} "
            f"min={X[:, i].min():.6f} "
            f"max={X[:, i].max():.6f}"
        )

    # ==========================================================
    # STRATIFIED SPLIT
    #
    # Same 70 / 15 / 15 split as teacher
    # ==========================================================

    print(
        f"\n[{datetime.now().strftime('%H:%M:%S')}] "
        f"Performing Stratified Split (70/15/15)..."
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

    print("\nDataset split:")

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
    # WINDOWS SAFETY
    # ==========================================================

    num_cpus = (
        0
        if os.name == "nt"
        else 4
    )

    # ==========================================================
    # DATA LOADERS
    # ==========================================================

    train_loader = DataLoader(

        NIDSDataset(
            X_train,
            y_train
        ),

        batch_size=cfg.BATCH_SIZE,

        shuffle=True,

        num_workers=num_cpus,

        pin_memory=(
            True
            if torch.cuda.is_available()
            else False
        )
    )

    val_loader = DataLoader(

        NIDSDataset(
            X_val,
            y_val
        ),

        batch_size=cfg.BATCH_SIZE,

        shuffle=False,

        num_workers=num_cpus,

        pin_memory=(
            True
            if torch.cuda.is_available()
            else False
        )
    )

    test_loader = DataLoader(

        NIDSDataset(
            X_test,
            y_test
        ),

        batch_size=cfg.BATCH_SIZE,

        shuffle=False,

        num_workers=num_cpus,

        pin_memory=(
            True
            if torch.cuda.is_available()
            else False
        )
    )

    return (
        train_loader,
        val_loader,
        test_loader,
        features
    )


# ==============================================================
# 3. TRAINING
# ==============================================================

def train_model():

    print("\n" + "=" * 60)
    print(
        "BNN HARDWARE-AWARE TRAINING SESSION"
    )
    print("=" * 60)

    print(
        f"Input Features    : {cfg.INPUT_SIZE}"
    )

    print(
        f"Hidden Layers     : {cfg.HIDDEN_LAYERS}"
    )

    res_status = (
        "Enabled (Dense-Residual)"
        if cfg.USE_RESIDUALS
        else "Disabled"
    )

    print(
        f"Residuals         : {res_status}"
    )

    print(
        f"Activation        : {cfg.ACTIVATION_TYPE}"
    )

    print(
        "Preprocessing     : "
        "Preprocessed LUT + log1p + MinMax"
    )

    print(
        f"Optimizer         : "
        f"{cfg.OPTIMIZER_TYPE} "
        f"(LR: {cfg.LEARNING_RATE})"
    )

    hw_status = (

        f"Enabled (Q8.{cfg.FRACTIONAL_BITS} "
        f"Fixed-Point)"

        if cfg.SIMULATE_FIXED_POINT

        else "Disabled"
    )

    print(
        f"Hardware Sim      : {hw_status}"
    )

    print(
        f"Device            : {cfg.DEVICE}"
    )

    print("-" * 60)

    # ==========================================================
    # PREPARE DATA
    # ==========================================================

    (
        train_loader,
        val_loader,
        test_loader,
        features
    ) = prepare_data()

    # ==========================================================
    # MODEL
    # ==========================================================

    model = BWNClassifier().to(
        cfg.DEVICE
    )

    print(
        "\nBNN model created."
    )

    # ==========================================================
    # OPTIMIZER
    # ==========================================================

    optimizer = torch.optim.AdamW(

        model.parameters(),

        lr=cfg.LEARNING_RATE,

        weight_decay=cfg.WEIGHT_DECAY
    )

    # ==========================================================
    # SCHEDULER
    # ==========================================================

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(

        optimizer,

        mode="max",

        factor=cfg.SCHEDULER_FACTOR,

        patience=cfg.SCHEDULER_PATIENCE
    )

    # ==========================================================
    # LOSS
    # ==========================================================

    criterion = get_criterion()

    # ==========================================================
    # TRAINING VARIABLES
    # ==========================================================

    best_f1 = 0.0

    epochs_no_improve = 0

    best_epoch = 0

    # ==========================================================
    # TRAINING LOOP
    # ==========================================================

    print(
        f"\nStarting training for "
        f"{cfg.NUM_EPOCHS} epochs..."
    )

    print(
        f"{'Epoch':<8} | "
        f"{'Loss':<9} | "
        f"{'Val Acc':<10} | "
        f"{'Val F1':<10} | "
        f"{'Precision':<10} | "
        f"{'Recall':<10} | "
        f"{'LR':<10}"
    )

    print("-" * 90)

    try:

        for epoch in range(
            cfg.NUM_EPOCHS
        ):

            # ==================================================
            # TRAINING PHASE
            # ==================================================

            model.train()

            running_loss = 0.0

            for inputs, labels in train_loader:

                inputs = inputs.to(
                    cfg.DEVICE
                )

                labels = labels.to(
                    cfg.DEVICE
                )

                optimizer.zero_grad()

                outputs = model(
                    inputs
                )

                loss = criterion(
                    outputs,
                    labels
                )

                loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    max_norm=1.0
                )

                optimizer.step()

                running_loss += loss.item()

            # ==================================================
            # VALIDATION
            # ==================================================

            model.eval()

            val_preds = []
            val_labels = []

            with torch.no_grad():

                for inputs, labels in val_loader:

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

                    val_preds.extend(
                        preds
                    )

                    val_labels.extend(
                        labels.numpy()
                    )

            # ==================================================
            # METRICS
            # ==================================================

            epoch_loss = (
                running_loss
                / len(train_loader)
            )

            epoch_acc = accuracy_score(
                val_labels,
                val_preds
            )

            epoch_f1 = f1_score(
                val_labels,
                val_preds,
                zero_division=0
            )

            epoch_precision = precision_score(
                val_labels,
                val_preds,
                zero_division=0
            )

            epoch_recall = recall_score(
                val_labels,
                val_preds,
                zero_division=0
            )

            current_lr = (
                optimizer
                .param_groups[0]["lr"]
            )

            # ==================================================
            # SCHEDULER
            # ==================================================

            scheduler.step(
                epoch_f1
            )

            # ==================================================
            # PRINT
            # ==================================================

            print(
                f"{epoch + 1:<8} | "
                f"{epoch_loss:<9.4f} | "
                f"{epoch_acc:<10.4%} | "
                f"{epoch_f1:<10.4%} | "
                f"{epoch_precision:<10.4%} | "
                f"{epoch_recall:<10.4%} | "
                f"{current_lr:<10.6f}"
            )

            # ==================================================
            # SAVE BEST MODEL
            # ==================================================

            if epoch_f1 > best_f1:

                best_f1 = epoch_f1

                best_epoch = (
                    epoch + 1
                )

                epochs_no_improve = 0

                torch.save(
                    model.state_dict(),
                    cfg.MODEL_SAVE_PATH
                )

                print(
                    f"  [SAVE] New best F1: "
                    f"{best_f1:.6%}"
                )

            else:

                epochs_no_improve += 1

                if (
                    epochs_no_improve
                    >= cfg.EARLY_STOPPING_PATIENCE
                ):

                    print(
                        "\n[STOP] Early stopping "
                        "triggered after "
                        f"{cfg.EARLY_STOPPING_PATIENCE} "
                        "epochs without F1 improvement."
                    )

                    break

    except KeyboardInterrupt:

        print(
            "\n[WARN] Training interrupted "
            "by user."
        )

    # ==============================================================
    # FINAL TEST EVALUATION
    # ==============================================================

    print("\n" + "=" * 60)
    print(
        "FINAL BNN TEST SET EVALUATION"
    )
    print("=" * 60)

    if not cfg.MODEL_SAVE_PATH.exists():

        print(
            "No trained model was saved."
        )

        return

    # ----------------------------------------------------------
    # Load best model
    # ----------------------------------------------------------

    model.load_state_dict(
        torch.load(
            cfg.MODEL_SAVE_PATH,
            map_location=cfg.DEVICE
        )
    )

    model.eval()

    test_preds = []
    test_labels = []

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
            ).cpu().numpy()

            test_preds.extend(
                preds
            )

            test_labels.extend(
                labels.numpy()
            )

    # ==========================================================
    # FINAL METRICS
    # ==========================================================

    final_acc = accuracy_score(
        test_labels,
        test_preds
    )

    final_f1 = f1_score(
        test_labels,
        test_preds,
        zero_division=0
    )

    final_precision = precision_score(
        test_labels,
        test_preds,
        zero_division=0
    )

    final_recall = recall_score(
        test_labels,
        test_preds,
        zero_division=0
    )

    print(
        f"Best Validation F1 : "
        f"{best_f1:.6%}"
    )

    print(
        f"Best Epoch         : "
        f"{best_epoch}"
    )

    print(
        f"Test Accuracy      : "
        f"{final_acc:.6%}"
    )

    print(
        f"Test F1            : "
        f"{final_f1:.6%}"
    )

    print(
        f"Test Precision     : "
        f"{final_precision:.6%}"
    )

    print(
        f"Test Recall        : "
        f"{final_recall:.6%}"
    )

    print("=" * 60)

    print(
        "\nBNN TRAINING SESSION COMPLETE"
    )

    print(
        f"Best Model Saved to: "
        f"{cfg.MODEL_SAVE_PATH}"
    )

    print("=" * 60)


# ==============================================================
# RUN
# ==============================================================

if __name__ == "__main__":

    train_model()