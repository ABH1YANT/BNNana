import torch
import torch.nn as nn

import pandas as pd
import numpy as np
import json

from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==============================================================
# 1. MODEL ARCHITECTURE
# ==============================================================

class ResidualBlock(nn.Module):

    def __init__(self, size):

        super().__init__()

        self.norm = nn.LayerNorm(size)

        self.net = nn.Sequential(
            nn.Linear(size, size * 2),
            nn.GELU(),
            nn.Linear(size * 2, size)
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


# ==============================================================
# 2. PATHS
# ==============================================================

ROOT = Path(
    r"C:\Users\DELL\Desktop\BNNana"
)

DATA_DIR = (
    ROOT
    / "datasets"
    / "processed"
)

# Raw master dataset
MASTER_DATASET = (
    DATA_DIR
    / "master_dataset.csv"
)

# IMPORTANT:
# Your screenshot shows the LUTs here.
LUT_DIR = ROOT / "artifacts" / "feature_luts"

LUT_METADATA = ROOT / "artifacts" / "lut_metadata.json"

MODEL_PATH = (
    ROOT
    / "artifacts"
    / "teacher_model.pth"
)

# Raw source datasets
CSV_SOURCES = {

    "BENIGN":
        DATA_DIR / "BENIGN.csv",

    "DNS":
        DATA_DIR / "DNS.csv",

    "SYN":
        DATA_DIR / "SYN.csv",

    "UDP":
        DATA_DIR / "UDP.csv"
}


# Number of unseen samples collected from each source
SAMPLES_PER_CLASS = 25000

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ==============================================================
# 3. EXACT 16 FEATURES
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
# 4. LOAD LUT METADATA
# ==============================================================

def load_lut_metadata():

    print("\nLoading LUT metadata...")

    if not LUT_METADATA.exists():

        raise FileNotFoundError(
            f"\nLUT metadata not found:\n"
            f"{LUT_METADATA}"
        )

    with open(
        LUT_METADATA,
        "r",
        encoding="utf-8"
    ) as f:

        metadata = json.load(f)

    return metadata


# ==============================================================
# 5. LOAD LUTS
# ==============================================================

def load_luts():

    print("\nLoading feature LUTs...")

    luts = {}

    for feature in FEATURES:

        safe_name = (
            feature
            .replace("/", "_")
            .replace("\\", "_")
            .replace(" ", "_")
        )

        lut_path = (
            LUT_DIR
            / f"{safe_name}_lut.csv"
        )

        if not lut_path.exists():

            raise FileNotFoundError(
                f"\nLUT not found for:\n"
                f"{feature}\n"
                f"Expected:\n"
                f"{lut_path}"
            )

        lut_df = pd.read_csv(
            lut_path
        )

        luts[feature] = (
            lut_df[
                "normalized_value"
            ]
            .values
            .astype(np.float32)
        )

        print(
            f"  {feature:35s} "
            f"{len(luts[feature]):,} entries"
        )

    return luts


# ==============================================================
# 6. RAW VALUES -> SAME LUT VALUES USED FOR TRAINING
# ==============================================================

def apply_luts(
    df,
    metadata,
    luts
):

    output = np.zeros(
        (len(df), len(FEATURES)),
        dtype=np.float32
    )

    for feature_index, feature in enumerate(FEATURES):

        # ------------------------------------------------------
        # Read raw feature
        # ------------------------------------------------------

        values = pd.to_numeric(
            df[feature],
            errors="coerce"
        ).fillna(0).values

        # Negative values are clamped to zero
        values = np.maximum(
            values,
            0
        )

        values = values.astype(
            np.uint64
        )

        # ------------------------------------------------------
        # Get LUT configuration
        # ------------------------------------------------------

        feature_meta = metadata[
            feature
        ]

        original_bits = int(
            feature_meta[
                "original_bits"
            ]
        )

        lut_bits = int(
            feature_meta[
                "lut_bits"
            ]
        )

        # ------------------------------------------------------
        # Generate LUT address
        # ------------------------------------------------------

        if original_bits <= 16:

            # Exact value is the address
            addresses = values.astype(
                np.int64
            )

        else:

            # Keep upper 16 bits
            shift = (
                original_bits - 16
            )

            addresses = (
                values >> shift
            ).astype(
                np.int64
            )

        # ------------------------------------------------------
        # Clamp to LUT range
        # ------------------------------------------------------

        max_address = (
            (1 << lut_bits) - 1
        )

        addresses = np.clip(
            addresses,
            0,
            max_address
        )

        # ------------------------------------------------------
        # LUT lookup
        #
        # This already contains:
        #
        # representative
        #       ↓
        # log1p
        #       ↓
        # MinMax
        # ------------------------------------------------------

        output[:, feature_index] = (
            luts[feature][addresses]
        )

    return output


# ==============================================================
# 7. MAIN
# ==============================================================

def main():

    print("=" * 70)
    print("BNNana TEACHER — UNSEEN DATA STRESS TEST")
    print("=" * 70)


    # ==========================================================
    # STEP 1 — LOAD LUTS
    # ==========================================================

    metadata = load_lut_metadata()

    luts = load_luts()


    # ==========================================================
    # STEP 2 — LOAD MASTER DATASET
    #
    # Used ONLY to identify samples that were already seen.
    # ==========================================================

    print(
        "\nLoading master dataset "
        "to identify seen samples..."
    )

    master_df = pd.read_csv(
        MASTER_DATASET,
        usecols=FEATURES
    )

    seen_samples = set(
        tuple(x)
        for x in master_df.values
    )

    del master_df

    print(
        f"Seen samples identified: "
        f"{len(seen_samples):,}"
    )


    # ==========================================================
    # STEP 3 — COLLECT UNSEEN RAW SAMPLES
    # ==========================================================

    all_data = []

    for category, path in CSV_SOURCES.items():

        print(
            f"\nExtracting unseen samples "
            f"from {category}..."
        )

        if not path.exists():

            print(
                f"WARNING: File not found:\n"
                f"{path}"
            )

            continue

        chunks = pd.read_csv(
            path,
            low_memory=False,
            chunksize=100000
        )

        category_samples = []

        for chunk in chunks:

            # --------------------------------------------------
            # Clean column names
            # --------------------------------------------------

            chunk.columns = [
                str(c).strip()
                for c in chunk.columns
            ]

            chunk = chunk.loc[
                :,
                ~chunk.columns.duplicated()
            ].copy()

            # --------------------------------------------------
            # Find Label column
            # --------------------------------------------------

            label_cols = [
                c
                for c in chunk.columns
                if c.lower() == "label"
            ]

            if not label_cols:

                continue

            raw_labels = chunk[
                label_cols[0]
            ]

            # --------------------------------------------------
            # Binary label
            #
            # BENIGN = 0
            # Everything else = 1
            # --------------------------------------------------

            is_attack = (
                raw_labels
                .astype(str)
                .str.strip()
                .str.upper()
                != "BENIGN"
            )

            chunk[
                "BinaryLabel"
            ] = is_attack.astype(int)

            # --------------------------------------------------
            # Remove duplicates inside raw source
            # --------------------------------------------------

            chunk = chunk.drop_duplicates(
                subset=FEATURES
            )

            # --------------------------------------------------
            # Remove samples already present in master
            # --------------------------------------------------

            chunk_values = (
                chunk[FEATURES].values
            )

            unseen_mask = [

                tuple(x)
                not in seen_samples

                for x in chunk_values
            ]

            chunk = chunk[
                unseen_mask
            ]

            # --------------------------------------------------
            # Keep unseen samples
            # --------------------------------------------------

            if not chunk.empty:

                category_samples.append(
                    chunk[
                        FEATURES
                        + ["BinaryLabel"]
                    ]
                )

            current_total = sum(
                len(c)
                for c in category_samples
            )

            if (
                current_total
                >= SAMPLES_PER_CLASS
            ):

                break

        # ------------------------------------------------------
        # Add category
        # ------------------------------------------------------

        if category_samples:

            cat_df = pd.concat(
                category_samples,
                ignore_index=True
            )

            cat_df = cat_df.head(
                SAMPLES_PER_CLASS
            )

            cat_df["Source"] = category

            all_data.append(
                cat_df
            )

            print(
                f"Collected "
                f"{len(cat_df):,} "
                f"UNSEEN samples."
            )

        else:

            print(
                f"WARNING: No unseen "
                f"samples found for {category}"
            )


    # ==========================================================
    # STEP 4 — COMBINE
    # ==========================================================

    if not all_data:

        print(
            "\nERROR: No unseen data collected."
        )

        return

    test_df = pd.concat(
        all_data,
        ignore_index=True
    )

    print(
        f"\nTotal unseen samples: "
        f"{len(test_df):,}"
    )


    # ==========================================================
    # STEP 5 — APPLY SAME LUT PREPROCESSING
    # ==========================================================

    print(
        "\nApplying SAME LUT preprocessing "
        "used during teacher training..."
    )

    X_processed = apply_luts(
        test_df,
        metadata,
        luts
    )

    y_true = (
        test_df[
            "BinaryLabel"
        ]
        .values
        .astype(int)
    )


    # ==========================================================
    # STEP 6 — CHECK PROCESSED VALUES
    # ==========================================================

    print(
        "\nProcessed feature ranges:"
    )

    for i, feature in enumerate(FEATURES):

        print(
            f"{feature:35s} "
            f"min={X_processed[:, i].min():.6f} "
            f"max={X_processed[:, i].max():.6f}"
        )


    # ==========================================================
    # STEP 7 — LOAD TEACHER
    # ==========================================================

    print(
        f"\nLoading teacher model "
        f"on {DEVICE}..."
    )

    model = FPSuperTeacher(
        len(FEATURES)
    ).to(DEVICE)

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=DEVICE
        )
    )

    model.eval()


    # ==========================================================
    # STEP 8 — INFERENCE
    # ==========================================================

    print(
        "\nRunning inference..."
    )

    X_tensor = torch.tensor(
        X_processed,
        dtype=torch.float32
    ).to(DEVICE)

    y_pred_list = []

    batch_size = 5000

    with torch.no_grad():

        for i in range(
            0,
            len(X_tensor),
            batch_size
        ):

            batch_x = X_tensor[
                i:i + batch_size
            ]

            logits = model(
                batch_x
            )

            preds = (
                torch.sigmoid(logits)
                > 0.5
            ).cpu().numpy()

            y_pred_list.extend(
                preds
            )

    y_pred = (
        np.array(y_pred_list)
        .astype(int)
    )

    test_df[
        "Prediction"
    ] = y_pred


    # ==========================================================
    # STEP 9 — OVERALL RESULTS
    # ==========================================================

    print("\n")
    print("=" * 70)
    print("TEACHER MODEL — UNSEEN DATA RESULTS")
    print("=" * 70)

    print(
        f"\nTotal samples: "
        f"{len(test_df):,}"
    )

    print("-" * 50)

    print(
        f"Accuracy  : "
        f"{accuracy_score(y_true, y_pred):.6%}"
    )

    print(
        f"F1-Score  : "
        f"{f1_score(y_true, y_pred):.6%}"
    )

    print(
        f"Precision : "
        f"{precision_score(y_true, y_pred):.6%}"
    )

    print(
        f"Recall    : "
        f"{recall_score(y_true, y_pred):.6%}"
    )

    print(
        "\nOverall Confusion Matrix:"
    )

    print(
        confusion_matrix(
            y_true,
            y_pred,
            labels=[0, 1]
        )
    )


    # ==========================================================
    # STEP 10 — PER SOURCE RESULTS
    # ==========================================================

    print("\n")
    print("=" * 70)
    print("PER-SOURCE RESULTS")
    print("=" * 70)

    for source in CSV_SOURCES.keys():

        subset = test_df[
            test_df["Source"]
            == source
        ]

        if subset.empty:

            continue

        s_true = (
            subset[
                "BinaryLabel"
            ]
            .values
        )

        s_pred = (
            subset[
                "Prediction"
            ]
            .values
        )

        print(
            f"\nCATEGORY: {source}"
        )

        print("-" * 50)

        print(
            f"Samples   : "
            f"{len(subset):,}"
        )

        print(
            f"Accuracy  : "
            f"{accuracy_score(s_true, s_pred):.6%}"
        )

        print(
            f"F1-Score  : "
            f"{f1_score(s_true, s_pred):.6%}"
        )

        print(
            f"Precision : "
            f"{precision_score(s_true, s_pred):.6%}"
        )

        print(
            f"Recall    : "
            f"{recall_score(s_true, s_pred):.6%}"
        )

        print(
            "Confusion Matrix:"
        )

        print(
            confusion_matrix(
                s_true,
                s_pred,
                labels=[0, 1]
            )
        )


    # ==========================================================
    # STEP 11 — SAVE RESULTS
    # ==========================================================

    output_path = (
        DATA_DIR
        / "teacher_unseen_stress_test.csv"
    )

    test_df.to_csv(
        output_path,
        index=False
    )

    print("\n")
    print("=" * 70)

    print(
        "Stress test complete."
    )

    print(
        f"\nDetailed results saved to:"
    )

    print(
        output_path
    )

    print("=" * 70)


# ==============================================================
# RUN
# ==============================================================

if __name__ == "__main__":
    main()