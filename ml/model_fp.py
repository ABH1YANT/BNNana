import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts

import pandas as pd
import numpy as np
import json
from pathlib import Path

from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix


# ------------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------------

ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")

DATA_PATH = (
    ROOT
    / "datasets"
    / "processed"
    / "scaled_dataset.csv"
)

MODEL_PATH = (
    ROOT
    / "artifacts"
    / "teacher_model.pth"
)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

BATCH_SIZE = 512
LEARNING_RATE = 0.001
MAX_EPOCHS = 150
EARLY_STOPPING_PATIENCE = 15


# ------------------------------------------------------------------
# 2. Residual Architecture
# ------------------------------------------------------------------

class ResidualBlock(nn.Module):

    def __init__(self, size):

        super().__init__()

        self.norm = nn.LayerNorm(size)

        self.net = nn.Sequential(
            nn.Linear(size, size * 2),
            nn.GELU(),
            nn.Linear(size * 2, size),
        )

    def forward(self, x):

        return x + self.net(
            self.norm(x)
        )


class FPSuperTeacher(nn.Module):

    def __init__(self, input_size):

        super().__init__()

        self.stem = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.GELU()
        )

        self.stack = nn.Sequential(

            ResidualBlock(512),

            nn.Linear(512, 256),
            nn.GELU(),

            ResidualBlock(256),

            nn.Linear(256, 128),
            nn.GELU(),

            ResidualBlock(128)
        )

        self.head = nn.Linear(128, 1)

    def forward(self, x):

        x = self.stem(x)
        x = self.stack(x)

        return self.head(x).squeeze(-1)


# ------------------------------------------------------------------
# 3. Main Execution
# ------------------------------------------------------------------

def main():

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

    # ==============================================================
    # Step 1: Load ALREADY PROCESSED dataset
    # ==============================================================

    print("Step 1: Loading LUT-processed dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset shape: {df.shape}")

    # ==============================================================
    # Step 2: Load features
    #
    # NO LOG TRANSFORMATION
    # NO MINMAX SCALING
    #
    # These were already done during LUT generation.
    # ==============================================================

    X = df[features].values.astype(np.float32)

    y = df["Label"].values.astype(np.float32)

    print("\nFeature range check:")

    for i, feature in enumerate(features):

        print(
            f"{feature:35s} "
            f"min={X[:, i].min():.6f} "
            f"max={X[:, i].max():.6f}"
        )

    # ==============================================================
    # Step 3: Split
    # ==============================================================

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.3,
        stratify=y,
        random_state=42
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.5,
        stratify=y_temp,
        random_state=42
    )

    print("\nDataset split:")

    print(
        f"Train: {len(X_train):,}"
    )

    print(
        f"Validation: {len(X_val):,}"
    )

    print(
        f"Test: {len(X_test):,}"
    )

    # ==============================================================
    # Step 4: Dataset
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
    # Step 5: DataLoaders
    # ==============================================================

    train_loader = DataLoader(
        NIDSDataset(X_train, y_train),
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    val_loader = DataLoader(
        NIDSDataset(X_val, y_val),
        batch_size=BATCH_SIZE
    )

    test_loader = DataLoader(
        NIDSDataset(X_test, y_test),
        batch_size=BATCH_SIZE
    )

    # ==============================================================
    # Step 6: Training Setup
    # ==============================================================

    model = FPSuperTeacher(
        len(features)
    ).to(DEVICE)

    criterion = nn.BCEWithLogitsLoss()

    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.02
    )

    scheduler = CosineAnnealingWarmRestarts(
        optimizer,
        T_0=10,
        T_mult=2
    )

    print(
        f"\nTraining Residual Teacher "
        f"on {DEVICE}..."
    )

    best_f1 = 0.0

    epochs_no_improve = 0

    # ==============================================================
    # Step 7: Training
    # ==============================================================

    for epoch in range(MAX_EPOCHS):

        # ----------------------------------------------------------
        # TRAINING
        # ----------------------------------------------------------

        model.train()

        for inputs, labels in train_loader:

            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()

            loss = criterion(
                model(inputs),
                labels
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0
            )

            optimizer.step()

        scheduler.step()

        # ----------------------------------------------------------
        # TRAINING METRICS
        #
        # We evaluate the trained model on the training set
        # so we can compare Train F1 vs Validation F1.
        # ----------------------------------------------------------

        model.eval()

        train_preds = []
        train_labels = []

        with torch.no_grad():

            for inputs, labels in train_loader:

                inputs = inputs.to(DEVICE)

                outputs = model(inputs)

                preds = (
                    torch.sigmoid(outputs) > 0.5
                ).float().cpu().numpy()

                train_preds.extend(preds)

                train_labels.extend(
                    labels.numpy()
                )

        train_f1 = f1_score(
            train_labels,
            train_preds
        )

        train_acc = accuracy_score(
            train_labels,
            train_preds
        )

        # ----------------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------------

        val_preds = []
        val_labels = []

        with torch.no_grad():

            for inputs, labels in val_loader:

                inputs = inputs.to(DEVICE)

                outputs = model(inputs)

                preds = (
                    torch.sigmoid(outputs) > 0.5
                ).float().cpu().numpy()

                val_preds.extend(preds)

                val_labels.extend(
                    labels.numpy()
                )

        current_f1 = f1_score(
            val_labels,
            val_preds
        )

        current_acc = accuracy_score(
            val_labels,
            val_preds
        )

        # ----------------------------------------------------------
        # PRINT TRAIN + VALIDATION METRICS
        # ----------------------------------------------------------

        print(
            f"Epoch {epoch + 1:02d} | "
            f"Train F1: {train_f1:.6%} | "
            f"Val F1: {current_f1:.6%} | "
            f"Train Acc: {train_acc:.6%} | "
            f"Val Acc: {current_acc:.6%}"
        )

        # ----------------------------------------------------------
        # Save best model
        # ----------------------------------------------------------

        if current_f1 > best_f1:

            best_f1 = current_f1

            epochs_no_improve = 0

            torch.save(
                model.state_dict(),
                MODEL_PATH
            )

            torch.save(
                {
                    "state_dict":
                        model.state_dict(),

                    "input_size":
                        len(features),

                    "f1_score":
                        current_f1,

                    "features":
                        features,

                    "dataset":
                        "scaled_dataset.csv",

                    "preprocessing":
                        "LUT representative + log1p + MinMax"

                },
                ROOT
                / "artifacts"
                / "teacher_for_distillation.pt"
            )

        else:

            epochs_no_improve += 1

            if (
                epochs_no_improve
                >= EARLY_STOPPING_PATIENCE
            ):

                print(
                    f"\nEarly Stopping triggered "
                    f"after {EARLY_STOPPING_PATIENCE} "
                    f"epochs without F1 improvement."
                )

                break

    # ==============================================================
    # Step 8: Final Test Evaluation
    # ==============================================================

    print("\n" + "=" * 50)

    print(
        "FINAL TEST SET EVALUATION "
        "(BEST F1 MODEL)"
    )

    print("=" * 50)

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=DEVICE
        )
    )

    model.eval()

    test_preds = []
    test_labels = []

    with torch.no_grad():

        for inputs, labels in test_loader:

            inputs = inputs.to(DEVICE)

            outputs = model(inputs)

            preds = (
                torch.sigmoid(outputs) > 0.5
            ).cpu().numpy()

            test_preds.extend(preds)

            test_labels.extend(
                labels.numpy()
            )

    final_f1 = f1_score(
        test_labels,
        test_preds
    )

    final_acc = accuracy_score(
        test_labels,
        test_preds
    )

    print(
        f"Final Test F1-Score : "
        f"{final_f1:.6%}"
    )

    print(
        f"Final Test Accuracy : "
        f"{final_acc:.6%}"
    )

    print("-" * 50)

    print("Confusion Matrix:")

    print(
        confusion_matrix(
            test_labels,
            test_preds
        )
    )

    print("=" * 50)


# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------

if __name__ == "__main__":
    main()