
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = Path(
    r"C:\Users\DELL\Desktop\BNNana\datasets\processed\master_dataset.csv"
)

NUM_TEST_ROWS = 100

FEATURES = [
    "Bwd Packet Length Max",
    "Min Packet Length",
    "Subflow Bwd Bytes",
    "Total Length of Bwd Packets",
    "Destination Port",
    "min_seg_size_forward",
    "ACK Flag Count",
    "Subflow Bwd Packets",
    "Fwd Packet Length Max",
    "Total Backward Packets",
    "Subflow Fwd Bytes",
    "Max Packet Length",
    "Total Length of Fwd Packets",
    "Bwd Header Length",
    "Flow Duration",
    "Fwd Header Length",
]

LABEL_COLUMN = "Label"


def main():
    # --------------------------------------------------------
    # 1. Check that the dataset exists.
    # --------------------------------------------------------
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    print("Loading BNNana master dataset...")
    print(DATASET_PATH)

    # --------------------------------------------------------
    # 2. Load only the first 100 data rows.
    # --------------------------------------------------------
    df = pd.read_csv(
        DATASET_PATH,
        nrows=NUM_TEST_ROWS,
    )

    # --------------------------------------------------------
    # 3. Validate required columns.
    # --------------------------------------------------------
    required_columns = FEATURES + [LABEL_COLUMN]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(missing)
        )

    # --------------------------------------------------------
    # 4. Select features and labels.
    # --------------------------------------------------------
    selected = df[required_columns].copy()

    # Convert selected columns to numeric values.
    for col in required_columns:
        selected[col] = pd.to_numeric(
            selected[col],
            errors="coerce",
        )

    if selected.isnull().any().any():
        bad_columns = selected.columns[
            selected.isnull().any()
        ].tolist()

        raise ValueError(
            f"Missing or invalid values in: {bad_columns}"
        )

    # --------------------------------------------------------
    # 5. Validate labels.
    # --------------------------------------------------------
    labels = selected[LABEL_COLUMN]

    if not labels.isin([0, 1]).all():
        raise ValueError(
            "Label column must contain only 0 or 1."
        )

    # --------------------------------------------------------
    # 6. Validate raw feature values.
    # --------------------------------------------------------
    feature_data = selected[FEATURES]

    if (feature_data < 0).any().any():
        raise ValueError(
            "This raw-feature test expects non-negative values."
        )

    if not (feature_data % 1 == 0).all().all():
        raise ValueError(
            "A selected feature contains non-integer values."
        )

    # --------------------------------------------------------
    # 7. Display the dataset summary.
    # --------------------------------------------------------
    print()
    print("Dataset validation successful.")
    print(f"Rows loaded: {len(selected)}")
    print(f"Feature count: {len(FEATURES)}")
    print(f"Class 0 samples: {(labels == 0).sum()}")
    print(f"Class 1 samples: {(labels == 1).sum()}")

    print()
    print("Feature order:")
    for index, name in enumerate(FEATURES):
        print(f"{index:2d}: {name}")

    print()
    print("First 5 selected samples:")
    print(selected.head().to_string(index=False))

    # --------------------------------------------------------
    # 8. Save a small, reproducible test file.
    # --------------------------------------------------------
    output_path = DATASET_PATH.parent / "esp32_test_100.csv"

    selected.to_csv(output_path, index=False)

    print()
    print(f"Test subset saved to:\n{output_path}")
    print()
    print(
        "This script validates and prepares the dataset. "
        "It does not send samples to the ESP32 yet."
    )


if __name__ == "__main__":
    main()
