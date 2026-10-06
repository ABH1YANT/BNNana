from pathlib import Path
import pandas as pd
import numpy as np
import json

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")
DATASET_DIR = ROOT / "datasets" / "processed"
OUTPUT_FILE = DATASET_DIR / "master_dataset.csv"

# ------------------------------------------------------------------
# Hardware limits
#
# These MUST match the actual FPGA feature_register.v / packet_parser.v
# field widths.
#
# Maximum unsigned value for N bits = (2^N) - 1
# ------------------------------------------------------------------
HW_BITS = {
    "Max Packet Length": 14,
    "Min Packet Length": 11,
    "Fwd Packet Length Max": 25,
    "Bwd Packet Length Max": 25,
    "Total Length of Fwd Packets": 16,
    "Total Length of Bwd Packets": 11,
    "Subflow Fwd Bytes": 1,
    "Subflow Bwd Bytes": 17,
    "Fwd Header Length": 15,
    "Bwd Header Length": 17,
    "Destination Port": 21,
    "Total Fwd Packets": 15,
    "Total Backward Packets": 21,
    "Subflow Fwd Packets": 21,
    "Subflow Bwd Packets": 27,
    "act_data_pkt_fwd": 21,
}

HW_LIMITS = {
    column: (1 << bits) - 1
    for column, bits in HW_BITS.items()
}

# ------------------------------------------------------------------
# Dataset / FPGA feature order
# ------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "Max Packet Length",
    "Min Packet Length",
    "Fwd Packet Length Max",
    "Bwd Packet Length Max",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Subflow Fwd Bytes",
    "Subflow Bwd Bytes",
    "Fwd Header Length",
    "Bwd Header Length",
    "Destination Port",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Subflow Fwd Packets",
    "Subflow Bwd Packets",
    "act_data_pkt_fwd",
    "Flow Duration",
    "min_seg_size_forward",
    "ACK Flag Count",
    "SYN Flag Count",
    "RST Flag Count",
    "FIN Flag Count",
    "PSH Flag Count",
    "URG Flag Count",
]

# ------------------------------------------------------------------
# Sampling
# ------------------------------------------------------------------
BENIGN_FILE = "BENIGN.csv"
ATTACK_FILES = [
    "SYN.csv",
    "UDP.csv",
    "DNS.csv",
]

SAMPLES_BENIGN = 200_000
SAMPLES_PER_ATTACK = 66_667

# ------------------------------------------------------------------
# Label normalization
# ------------------------------------------------------------------
LABEL_MAP = {
    "BENIGN": "BENIGN",

    "Syn": "SYN",
    "SYN": "SYN",
    "DrDoS_SYN": "SYN",

    "UDP": "UDP",
    "DrDoS_UDP": "UDP",

    "DNS": "DNS",
    "DrDoS_DNS": "DNS",
}

BINARY_ENCODING = {
    "BENIGN": 0,
    "SYN": 1,
    "UDP": 1,
    "DNS": 1,
}


# ------------------------------------------------------------------
# Print hardware limits
# ------------------------------------------------------------------
def print_hardware_limits():
    print()
    print("=" * 78)
    print("FPGA HARDWARE LIMITS")
    print("=" * 78)

    for column in REQUIRED_COLUMNS[:16]:
        bits = HW_BITS[column]
        limit = HW_LIMITS[column]
        print(f"{column:30s} : {bits:2d} bits -> 0 .. {limit:,}")

    print("=" * 78)
    print()


# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------
def clean_and_sample(path, target_label, n_samples, exclude_benign=False):

    print(f"Processing {path.name}...")

    df = pd.read_csv(path, low_memory=False)

    # Normalize column names
    df.columns = df.columns.str.strip()

    # --------------------------------------------------------------
    # Verify required columns exist
    # --------------------------------------------------------------
    missing = [
        column
        for column in REQUIRED_COLUMNS + ["Label"]
        if column not in df.columns
    ]

    if missing:
        raise RuntimeError(
            f"{path.name} is missing required columns:\n{missing}"
        )

    # Keep only required columns
    df = df[REQUIRED_COLUMNS + ["Label"]].copy()

    # --------------------------------------------------------------
    # Normalize labels
    # --------------------------------------------------------------
    df["Label"] = (
        df["Label"]
        .astype(str)
        .str.strip()
        .replace(LABEL_MAP)
    )

    if exclude_benign:
        df = df[df["Label"] == target_label]
    else:
        df = df[df["Label"] == "BENIGN"]

    # --------------------------------------------------------------
    # Remove NaN / Inf
    # --------------------------------------------------------------
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    # --------------------------------------------------------------
    # Convert feature columns to numeric
    # --------------------------------------------------------------
    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(subset=REQUIRED_COLUMNS)

    # --------------------------------------------------------------
    # Remove negative values
    # --------------------------------------------------------------
    df = df[
        (df[REQUIRED_COLUMNS] >= 0).all(axis=1)
    ]

    # --------------------------------------------------------------
    # Hardware saturation
    #
    # IMPORTANT:
    # Clip ONLY the 16 FPGA packet fields.
    # The remaining 8 dataset features are retained as before.
    # --------------------------------------------------------------
    print("  Applying FPGA hardware saturation...")

    for column, limit in HW_LIMITS.items():

        before_max = df[column].max()

        df[column] = df[column].clip(
            lower=0,
            upper=limit
        )

        after_max = df[column].max()

        if before_max > limit:
            print(
                f"    {column}: "
                f"clipped max {before_max} -> {after_max}"
            )

    # --------------------------------------------------------------
    # Integer conversion
    #
    # FPGA packet fields are integer-valued.
    # --------------------------------------------------------------
    for column in REQUIRED_COLUMNS[:16]:
        df[column] = np.rint(df[column]).astype(np.int64)

    # Keep the remaining dataset features numeric.
    for column in REQUIRED_COLUMNS[16:]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(subset=REQUIRED_COLUMNS)

    # --------------------------------------------------------------
    # Final hardware validation
    # --------------------------------------------------------------
    for column, limit in HW_LIMITS.items():

        invalid = (
            (df[column] < 0) |
            (df[column] > limit)
        )

        if invalid.any():

            bad_rows = df.loc[
                invalid,
                [column]
            ].head(5)

            raise RuntimeError(
                f"Hardware-limit validation failed for "
                f"{column}.\n"
                f"Maximum allowed: {limit}\n"
                f"Examples:\n{bad_rows}"
            )

    # --------------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------------
    df = df.drop_duplicates(
        subset=REQUIRED_COLUMNS + ["Label"]
    )

    # --------------------------------------------------------------
    # Sampling
    # --------------------------------------------------------------
    if len(df) > n_samples:

        df = df.sample(
            n=n_samples,
            random_state=42
        )

    else:

        print(
            f"  WARNING: Only {len(df):,} "
            f"unique valid samples available "
            f"for {target_label}"
        )

    print(
        f"  Final {target_label}: "
        f"{len(df):,} rows"
    )

    return df


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():

    DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print_hardware_limits()

    processed_dfs = []

    # --------------------------------------------------------------
    # BENIGN
    # --------------------------------------------------------------
    path_benign = DATASET_DIR / BENIGN_FILE

    if not path_benign.exists():
        raise FileNotFoundError(
            f"BENIGN dataset not found:\n{path_benign}"
        )

    processed_dfs.append(
        clean_and_sample(
            path_benign,
            "BENIGN",
            SAMPLES_BENIGN,
            exclude_benign=False
        )
    )

    # --------------------------------------------------------------
    # ATTACKS
    # --------------------------------------------------------------
    for filename in ATTACK_FILES:

        path_attack = DATASET_DIR / filename

        if not path_attack.exists():
            raise FileNotFoundError(
                f"Attack dataset not found:\n{path_attack}"
            )

        target = path_attack.stem

        processed_dfs.append(
            clean_and_sample(
                path_attack,
                target,
                SAMPLES_PER_ATTACK,
                exclude_benign=True
            )
        )

    # --------------------------------------------------------------
    # Merge
    # --------------------------------------------------------------
    print()
    print("Merging datasets...")

    master = pd.concat(
        processed_dfs,
        ignore_index=True
    )

    # --------------------------------------------------------------
    # Global deduplication
    # --------------------------------------------------------------
    print("Performing final global deduplication...")

    master = master.drop_duplicates(
        subset=REQUIRED_COLUMNS + ["Label"]
    ).reset_index(drop=True)

    # --------------------------------------------------------------
    # Binary labels
    # --------------------------------------------------------------
    master["Label"] = master["Label"].map(
        BINARY_ENCODING
    )

    if master["Label"].isna().any():
        raise RuntimeError(
            "Some labels could not be converted to "
            "binary labels."
        )

    master["Label"] = master["Label"].astype(np.int8)

    # --------------------------------------------------------------
    # Final hardware validation
    # --------------------------------------------------------------
    print("Performing final FPGA hardware validation...")

    for column, limit in HW_LIMITS.items():

        maximum = master[column].max()
        minimum = master[column].min()

        if minimum < 0 or maximum > limit:

            raise RuntimeError(
                f"FINAL HARDWARE VALIDATION FAILED\n"
                f"Feature: {column}\n"
                f"Observed range: {minimum} .. {maximum}\n"
                f"Allowed range: 0 .. {limit}"
            )

    # --------------------------------------------------------------
    # Shuffle
    # --------------------------------------------------------------
    print("Shuffling dataset...")

    master = master.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    # --------------------------------------------------------------
    # Save master dataset
    # --------------------------------------------------------------
    print(f"Saving:\n{OUTPUT_FILE}")

    master.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------------
    # Save feature order
    # --------------------------------------------------------------
    feature_order_path = DATASET_DIR / "feature_order.json"

    with open(
        feature_order_path,
        "w"
    ) as f:

        json.dump(
            REQUIRED_COLUMNS,
            f,
            indent=4
        )

    # --------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------
    print()
    print("=" * 78)
    print("FINAL DATASET SUMMARY")
    print("=" * 78)

    print(
        master["Label"]
        .value_counts()
        .sort_index()
        .rename({
            0: "0 (Benign)",
            1: "1 (Attack)"
        })
    )

    print()
    print(f"Total shape       : {master.shape}")
    print(f"Dataset           : {OUTPUT_FILE}")
    print(f"Feature order     : {feature_order_path}")
    print("Hardware limits   : APPLIED")
    print("Hardware validate  : PASSED")
    print("=" * 78)
    print("DONE")
    print("=" * 78)


if __name__ == "__main__":
    main()