import copy
import json
import time

import torch
import torch.nn as nn
import pandas as pd
import numpy as np

from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from .config import cfg
from .model import BWNClassifier


# ==============================================================
# 1. KNOWLEDGE DISTILLATION CONFIGURATION
# ==============================================================

# --------------------------------------------------------------
# Dataset
# --------------------------------------------------------------

DATA_PATH = (
    cfg.DATA_DIR
    / "scaled_dataset.csv"
)

# --------------------------------------------------------------
# Teacher
# --------------------------------------------------------------

TEACHER_PATH = (
    cfg.ARTIFACT_DIR
    / "teacher_for_distillation.pt"
)

# --------------------------------------------------------------
# Student
#
# IMPORTANT:
# Student architecture comes directly from config.py
#
# Example:
#
# HIDDEN_LAYERS = [32, 16, 8]
#
# Change ONLY config.py to test another architecture.
# --------------------------------------------------------------

STUDENT_HIDDEN_LAYERS = cfg.HIDDEN_LAYERS

# --------------------------------------------------------------
# Distillation parameters
# --------------------------------------------------------------

TEMPERATURE = 4.0

# 0.7 = 70% teacher knowledge
# 0.3 = 30% true labels
ALPHA = 0.7

# --------------------------------------------------------------
# Training
# --------------------------------------------------------------

BATCH_SIZE = cfg.BATCH_SIZE
NUM_EPOCHS = cfg.NUM_EPOCHS

LEARNING_RATE = cfg.LEARNING_RATE
WEIGHT_DECAY = cfg.WEIGHT_DECAY

EARLY_STOPPING_PATIENCE = (
    cfg.EARLY_STOPPING_PATIENCE
)

DEVICE = cfg.DEVICE


# ==============================================================
# 2. FEATURES
# ==============================================================

FEATURES = [

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
# 3. EXACT TEACHER ARCHITECTURE
# ==============================================================

class ResidualBlock(nn.Module):

    def __init__(self, size):

        super().__init__()

        self.norm = nn.LayerNorm(size)

        self.net = nn.Sequential(

            nn.Linear(
                size,
                size * 2
            ),

            nn.GELU(),

            nn.Linear(
                size * 2,
                size
            )

        )

    def forward(self, x):

        return x + self.net(
            self.norm(x)
        )


class FPSuperTeacher(nn.Module):

    def __init__(self, input_size):

        super().__init__()

        # ------------------------------------------------------
        # Exact architecture from your teacher training script
        # ------------------------------------------------------

        self.stem = nn.Sequential(

            nn.Linear(
                input_size,
                512
            ),

            nn.GELU()

        )

        self.stack = nn.Sequential(

            ResidualBlock(512),

            nn.Linear(
                512,
                256
            ),

            nn.GELU(),

            ResidualBlock(256),

            nn.Linear(
                256,
                128
            ),

            nn.GELU(),

            ResidualBlock(128)

        )

        self.head = nn.Linear(
            128,
            1
        )

    def forward(self, x):

        x = self.stem(x)

        x = self.stack(x)

        return self.head(x).squeeze(-1)


# ==============================================================
# 4. LOAD DATASET
# ==============================================================

def load_data():

    print("\n")
    print("=" * 70)
    print("LOADING LUT-PROCESSED DATASET")
    print("=" * 70)

    print(
        f"Dataset: {DATA_PATH}"
    )

    df = pd.read_csv(
        DATA_PATH
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    # ----------------------------------------------------------
    # Features
    #
    # NO LOG TRANSFORMATION HERE
    # NO MINMAX SCALING HERE
    #
    # LUT processing has already done this.
    # ----------------------------------------------------------

    X = df[
        FEATURES
    ].values.astype(
        np.float32
    )

    y = df[
        "Label"
    ].values.astype(
        np.float32
    )

    print("\nFeature range check:")

    for i, feature in enumerate(FEATURES):

        print(
            f"{feature:35s} "
            f"min={X[:, i].min():.6f} "
            f"max={X[:, i].max():.6f}"
        )

    # ----------------------------------------------------------
    # Same split as teacher / BNN
    # ----------------------------------------------------------

    X_train, X_temp, y_train, y_temp = train_test_split(

        X,
        y,

        test_size=0.30,

        stratify=y,

        random_state=42

    )

    X_val, X_test, y_val, y_test = train_test_split(

        X_temp,
        y_temp,

        test_size=0.50,

        stratify=y_temp,

        random_state=42

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

    # ----------------------------------------------------------
    # Tensor datasets
    # ----------------------------------------------------------

    train_dataset = TensorDataset(

        torch.tensor(
            X_train,
            dtype=torch.float32
        ),

        torch.tensor(
            y_train,
            dtype=torch.float32
        )

    )

    val_dataset = TensorDataset(

        torch.tensor(
            X_val,
            dtype=torch.float32
        ),

        torch.tensor(
            y_val,
            dtype=torch.float32
        )

    )

    test_dataset = TensorDataset(

        torch.tensor(
            X_test,
            dtype=torch.float32
        ),

        torch.tensor(
            y_test,
            dtype=torch.float32
        )

    )

    # ----------------------------------------------------------
    # DataLoaders
    # ----------------------------------------------------------

    train_loader = DataLoader(

        train_dataset,

        batch_size=BATCH_SIZE,

        shuffle=True

    )

    val_loader = DataLoader(

        val_dataset,

        batch_size=BATCH_SIZE,

        shuffle=False

    )

    test_loader = DataLoader(

        test_dataset,

        batch_size=BATCH_SIZE,

        shuffle=False

    )

    return (
        train_loader,
        val_loader,
        test_loader
    )


# ==============================================================
# 5. LOAD FROZEN TEACHER
# ==============================================================

def load_teacher():

    print("\n")
    print("=" * 70)
    print("LOADING TEACHER")
    print("=" * 70)

    print(
        f"Teacher checkpoint: {TEACHER_PATH}"
    )

    # ----------------------------------------------------------
    # Create exact teacher architecture
    # ----------------------------------------------------------

    teacher = FPSuperTeacher(
        input_size=len(FEATURES)
    )

    # ----------------------------------------------------------
    # Load teacher_for_distillation.pt
    #
    # Your teacher script saved:
    #
    # {
    #     "state_dict": ...,
    #     "input_size": ...,
    #     "f1_score": ...,
    #     ...
    # }
    # ----------------------------------------------------------

    checkpoint = torch.load(

        TEACHER_PATH,

        map_location=DEVICE

    )

    if "state_dict" not in checkpoint:

        raise RuntimeError(
            "teacher_for_distillation.pt "
            "does not contain 'state_dict'."
        )

    teacher.load_state_dict(
        checkpoint["state_dict"]
    )

    teacher.to(DEVICE)

    teacher.eval()

    # ----------------------------------------------------------
    # Freeze teacher
    # ----------------------------------------------------------

    for parameter in teacher.parameters():

        parameter.requires_grad = False

    print(
        "[OK] Teacher loaded successfully."
    )

    if "f1_score" in checkpoint:

        print(
            f"Teacher saved Val F1: "
            f"{checkpoint['f1_score']:.6%}"
        )

    print(
        "[OK] Teacher is FROZEN."
    )

    return teacher


# ==============================================================
# 6. KNOWLEDGE DISTILLATION LOSS
# ==============================================================

class DistillationLoss(nn.Module):

    def __init__(
        self,
        temperature,
        alpha
    ):

        super().__init__()

        self.temperature = temperature

        self.alpha = alpha

        self.hard_loss = nn.BCEWithLogitsLoss()

    def forward(
        self,
        student_logits,
        teacher_logits,
        labels
    ):

        T = self.temperature

        # ------------------------------------------------------
        # HARD LABEL LOSS
        #
        # Student vs actual 0/1 label
        # ------------------------------------------------------

        hard_loss = self.hard_loss(

            student_logits,

            labels

        )

        # ------------------------------------------------------
        # SOFT TEACHER TARGET
        #
        # Teacher logit -> softened probability
        # ------------------------------------------------------

        teacher_soft = torch.sigmoid(

            teacher_logits / T

        )

        # ------------------------------------------------------
        # STUDENT SOFT OUTPUT
        # ------------------------------------------------------

        student_soft = torch.sigmoid(

            student_logits / T

        )

        # ------------------------------------------------------
        # Binary cross entropy between teacher and student
        # ------------------------------------------------------

        soft_loss = -(

            teacher_soft
            * torch.log(
                student_soft + 1e-8
            )

            +

            (1.0 - teacher_soft)
            * torch.log(
                1.0 - student_soft + 1e-8
            )

        ).mean()

        # Standard temperature scaling
        soft_loss = soft_loss * (
            T * T
        )

        # ------------------------------------------------------
        # Combined loss
        # ------------------------------------------------------

        total_loss = (

            self.alpha * soft_loss

            +

            (1.0 - self.alpha)
            * hard_loss

        )

        return (
            total_loss,
            soft_loss,
            hard_loss
        )


# ==============================================================
# 7. EVALUATION
# ==============================================================

def evaluate(
    model,
    loader
):

    model.eval()

    predictions = []
    labels = []

    total_loss = 0.0
    total_samples = 0

    criterion = nn.BCEWithLogitsLoss()

    with torch.no_grad():

        for inputs, targets in loader:

            inputs = inputs.to(
                DEVICE
            )

            targets = targets.to(
                DEVICE
            )

            logits = model(
                inputs
            )

            loss = criterion(
                logits,
                targets
            )

            total_loss += (
                loss.item()
                * len(targets)
            )

            total_samples += len(
                targets
            )

            probs = torch.sigmoid(
                logits
            )

            preds = (
                probs >= 0.5
            ).long()

            predictions.extend(
                preds.cpu().numpy()
            )

            labels.extend(
                targets.cpu().numpy()
            )

    accuracy = accuracy_score(
        labels,
        predictions
    )

    precision = precision_score(
        labels,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        labels,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        labels,
        predictions,
        zero_division=0
    )

    cm = confusion_matrix(
        labels,
        predictions
    )

    return {

        "loss":
            total_loss / total_samples,

        "accuracy":
            accuracy,

        "precision":
            precision,

        "recall":
            recall,

        "f1":
            f1,

        "confusion_matrix":
            cm.tolist()

    }


# ==============================================================
# 8. DISTILLATION TRAINING
# ==============================================================

def train_student(
    teacher,
    student,
    train_loader,
    val_loader
):

    criterion = DistillationLoss(

        temperature=TEMPERATURE,

        alpha=ALPHA

    )

    # ----------------------------------------------------------
    # ONLY student parameters are optimized
    # ----------------------------------------------------------

    optimizer = torch.optim.AdamW(

        student.parameters(),

        lr=LEARNING_RATE,

        weight_decay=WEIGHT_DECAY

    )

    scheduler = (
        torch.optim.lr_scheduler.ReduceLROnPlateau(

            optimizer,

            mode="max",

            factor=0.5,

            patience=5

        )
    )

    best_f1 = -1.0

    best_epoch = 0

    best_state = None

    epochs_without_improvement = 0

    print("\n")
    print("=" * 70)
    print("KNOWLEDGE DISTILLATION TRAINING")
    print("=" * 70)

    print(
        f"Temperature       : {TEMPERATURE}"
    )

    print(
        f"Teacher weight    : {ALPHA}"
    )

    print(
        f"Hard-label weight : {1.0 - ALPHA}"
    )

    print(
        f"Student           : "
        f"{STUDENT_HIDDEN_LAYERS}"
    )

    print(
        f"Learning rate     : "
        f"{LEARNING_RATE}"
    )

    print("\n")

    print(
        "Epoch | Loss    | Val Acc  | Val F1   | "
        "Precision | Recall   | LR"
    )

    print("-" * 85)

    for epoch in range(
        1,
        NUM_EPOCHS + 1
    ):

        # ======================================================
        # TRAIN STUDENT
        # ======================================================

        student.train()

        running_loss = 0.0

        running_soft_loss = 0.0

        running_hard_loss = 0.0

        sample_count = 0

        for inputs, labels in train_loader:

            inputs = inputs.to(
                DEVICE
            )

            labels = labels.to(
                DEVICE
            )

            optimizer.zero_grad()

            # --------------------------------------------------
            # Teacher inference
            #
            # Teacher is frozen.
            # --------------------------------------------------

            with torch.no_grad():

                teacher_logits = teacher(
                    inputs
                )

            # --------------------------------------------------
            # Student inference
            # --------------------------------------------------

            student_logits = student(
                inputs
            )

            # --------------------------------------------------
            # KD loss
            # --------------------------------------------------

            (
                loss,
                soft_loss,
                hard_loss
            ) = criterion(

                student_logits,

                teacher_logits,

                labels

            )

            loss.backward()

            # --------------------------------------------------
            # Gradient clipping
            # --------------------------------------------------

            torch.nn.utils.clip_grad_norm_(

                student.parameters(),

                max_norm=1.0

            )

            optimizer.step()

            batch_size = len(
                labels
            )

            running_loss += (
                loss.item()
                * batch_size
            )

            running_soft_loss += (
                soft_loss.item()
                * batch_size
            )

            running_hard_loss += (
                hard_loss.item()
                * batch_size
            )

            sample_count += batch_size

        train_loss = (
            running_loss
            / sample_count
        )

        avg_soft_loss = (
            running_soft_loss
            / sample_count
        )

        avg_hard_loss = (
            running_hard_loss
            / sample_count
        )

        # ======================================================
        # VALIDATION
        # ======================================================

        val_metrics = evaluate(

            student,

            val_loader

        )

        val_f1 = val_metrics[
            "f1"
        ]

        scheduler.step(
            val_f1
        )

        current_lr = (
            optimizer.param_groups[0]["lr"]
        )

        print(

            f"{epoch:5d} | "
            f"{train_loss:.4f}  | "
            f"{val_metrics['accuracy'] * 100:8.4f}% | "
            f"{val_metrics['f1'] * 100:8.4f}% | "
            f"{val_metrics['precision'] * 100:8.4f}% | "
            f"{val_metrics['recall'] * 100:8.4f}% | "
            f"{current_lr:.6f}"

        )

        # ======================================================
        # BEST MODEL
        # ======================================================

        if val_f1 > best_f1:

            best_f1 = val_f1

            best_epoch = epoch

            best_state = copy.deepcopy(
                student.state_dict()
            )

            epochs_without_improvement = 0

            print(
                f"  [SAVE] New best F1: "
                f"{best_f1:.6%}"
            )

        else:

            epochs_without_improvement += 1

        # ======================================================
        # EARLY STOPPING
        # ======================================================

        if (
            epochs_without_improvement
            >= EARLY_STOPPING_PATIENCE
        ):

            print(
                f"\n[STOP] Early stopping triggered "
                f"after {EARLY_STOPPING_PATIENCE} "
                f"epochs without F1 improvement."
            )

            break

    # ----------------------------------------------------------
    # Restore best student
    # ----------------------------------------------------------

    if best_state is None:

        raise RuntimeError(
            "No valid student checkpoint was created."
        )

    student.load_state_dict(
        best_state
    )

    return (
        student,
        best_f1,
        best_epoch
    )


# ==============================================================
# 9. SAVE DISTILLED MODEL
# ==============================================================

def save_model(
    student,
    best_epoch,
    best_val_f1,
    test_metrics
):

    architecture_name = "_".join(
        str(x)
        for x in STUDENT_HIDDEN_LAYERS
    )

    model_path = (

        cfg.ARTIFACT_DIR
        / f"best_bnn_kd_{architecture_name}_model.pth"

    )

    metrics_path = (

        cfg.REPORT_DIR
        / f"kd_{architecture_name}_metrics.json"

    )

    # ----------------------------------------------------------
    # Model checkpoint
    # ----------------------------------------------------------

    torch.save(

        {

            "model_state_dict":
                student.state_dict(),

            "architecture":
                STUDENT_HIDDEN_LAYERS,

            "input_size":
                len(FEATURES),

            "teacher_checkpoint":
                str(TEACHER_PATH),

            "temperature":
                TEMPERATURE,

            "alpha":
                ALPHA,

            "best_epoch":
                best_epoch,

            "best_validation_f1":
                best_val_f1,

            "test_metrics":
                test_metrics,

            "features":
                FEATURES,

            "dataset":
                "scaled_dataset.csv",

            "preprocessing":
                "LUT representative + log1p + MinMax"

        },

        model_path

    )

    # ----------------------------------------------------------
    # Metrics JSON
    # ----------------------------------------------------------

    report = {

        "architecture":
            STUDENT_HIDDEN_LAYERS,

        "input_size":
            len(FEATURES),

        "teacher":
            "teacher_for_distillation.pt",

        "temperature":
            TEMPERATURE,

        "alpha":
            ALPHA,

        "best_epoch":
            best_epoch,

        "best_validation_f1":
            best_val_f1,

        "test_accuracy":
            test_metrics["accuracy"],

        "test_precision":
            test_metrics["precision"],

        "test_recall":
            test_metrics["recall"],

        "test_f1":
            test_metrics["f1"],

        "confusion_matrix":
            test_metrics["confusion_matrix"],

        "preprocessing":
            "LUT representative + log1p + MinMax",

        "dataset":
            "scaled_dataset.csv"

    }

    with open(
        metrics_path,
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )

    return (
        model_path,
        metrics_path
    )


# ==============================================================
# 10. MAIN
# ==============================================================

def main():

    start_time = time.time()

    print("\n")
    print("=" * 70)
    print("BNN KNOWLEDGE DISTILLATION")
    print("=" * 70)

    print(
        f"Input Features       : {len(FEATURES)}"
    )

    print(
        f"Student Architecture : "
        f"{STUDENT_HIDDEN_LAYERS}"
    )

    print(
        f"Teacher Architecture : "
        f"16 -> 512 -> 256 -> 128 -> 1"
    )

    print(
        f"Activation           : "
        f"{cfg.ACTIVATION_TYPE}"
    )

    print(
        f"Residuals            : "
        f"{cfg.USE_RESIDUALS}"
    )

    print(
        f"Hardware Simulation  : "
        f"{cfg.SIMULATE_FIXED_POINT}"
    )

    print(
        f"Fixed Point          : "
        f"Q{cfg.FRACTIONAL_BITS}"
    )

    print(
        f"Temperature          : "
        f"{TEMPERATURE}"
    )

    print(
        f"Alpha                : "
        f"{ALPHA}"
    )

    print(
        f"Device               : "
        f"{DEVICE}"
    )

    # ==========================================================
    # Load data
    # ==========================================================

    (
        train_loader,
        val_loader,
        test_loader
    ) = load_data()

    # ==========================================================
    # Load frozen teacher
    # ==========================================================

    teacher = load_teacher()

    # ==========================================================
    # Create student
    #
    # BWNClassifier automatically uses cfg.HIDDEN_LAYERS
    # ==========================================================

    print("\n")
    print("=" * 70)
    print("CREATING BNN STUDENT")
    print("=" * 70)

    student = BWNClassifier()

    student.to(
        DEVICE
    )

    print(
        f"Student architecture: "
        f"{STUDENT_HIDDEN_LAYERS}"
    )

    # ==========================================================
    # Train with knowledge distillation
    # ==========================================================

    (
        student,
        best_val_f1,
        best_epoch
    ) = train_student(

        teacher,
        student,

        train_loader,
        val_loader

    )

    # ==========================================================
    # FINAL TEST
    # ==========================================================

    print("\n")
    print("=" * 70)
    print("FINAL DISTILLED BNN TEST SET EVALUATION")
    print("=" * 70)

    test_metrics = evaluate(

        student,

        test_loader

    )

    print(
        f"Best Validation F1 : "
        f"{best_val_f1:.6%}"
    )

    print(
        f"Best Epoch          : "
        f"{best_epoch}"
    )

    print(
        f"Test Accuracy       : "
        f"{test_metrics['accuracy']:.6%}"
    )

    print(
        f"Test Precision      : "
        f"{test_metrics['precision']:.6%}"
    )

    print(
        f"Test Recall         : "
        f"{test_metrics['recall']:.6%}"
    )

    print(
        f"Test F1             : "
        f"{test_metrics['f1']:.6%}"
    )

    print("\nConfusion Matrix:")

    print(
        np.array(
            test_metrics[
                "confusion_matrix"
            ]
        )
    )

    # ==========================================================
    # SAVE
    # ==========================================================

    (
        model_path,
        metrics_path
    ) = save_model(

        student,

        best_epoch,

        best_val_f1,

        test_metrics

    )

    elapsed = (
        time.time()
        - start_time
    )

    print("\n")
    print("=" * 70)
    print("OUTPUT FILES")
    print("=" * 70)

    print(
        f"Model   : {model_path}"
    )

    print(
        f"Metrics : {metrics_path}"
    )

    print(
        f"Time    : {elapsed / 60:.2f} minutes"
    )

    print("=" * 70)
    print("KNOWLEDGE DISTILLATION COMPLETE")
    print("=" * 70)


# ==============================================================
# RUN
# ==============================================================

if __name__ == "__main__":

    main()