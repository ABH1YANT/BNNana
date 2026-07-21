"""
clean_datasets.py

Removes unnecessary columns from all raw datasets and writes the cleaned
versions to datasets/processed/.

Input:
    datasets/raw/
        ├── Syn.csv
        ├── DrDoS_UDP.csv
        └── DrDoS_DNS.csv

Output:
    datasets/processed/
        ├── Syn.csv
        ├── DrDoS_UDP.csv
        └── DrDoS_DNS.csv
"""

from pathlib import Path
import pandas as pd

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

ROOT = Path(r"C:\Users\a\Desktop\BNNana")

RAW_DIR = ROOT / "datasets" / "raw"
PROCESSED_DIR = ROOT / "datasets" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "Syn.csv",
    "DrDoS_UDP.csv",
    "DrDoS_DNS.csv",
]

# ------------------------------------------------------------------
# Columns to remove
# ------------------------------------------------------------------

COLUMNS_TO_DROP = [
    "Unnamed: 0",
    "Flow ID",
    " Source IP",
    " Destination IP",
    " Timestamp",
    " Fwd Header Length.1",
    "Fwd PSH Flags",
    " Bwd PSH Flags",
    " Fwd URG Flags",
    " Bwd URG Flags",
    "Fwd Avg Bytes/Bulk",
    " Fwd Avg Packets/Bulk",
    " Fwd Avg Bulk Rate",
    " Bwd Avg Bytes/Bulk",
    " Bwd Avg Packets/Bulk",
    "Bwd Avg Bulk Rate",
    "SimillarHTTP",
]

# ------------------------------------------------------------------
# Process each dataset
# ------------------------------------------------------------------

for filename in FILES:

    input_file = RAW_DIR / filename
    output_file = PROCESSED_DIR / filename

    print("=" * 60)
    print(f"Processing: {filename}")

    df = pd.read_csv(input_file)

    print(f"Original shape : {df.shape}")

    existing_columns = [c for c in COLUMNS_TO_DROP if c in df.columns]
    missing_columns = [c for c in COLUMNS_TO_DROP if c not in df.columns]

    df.drop(columns=existing_columns, inplace=True)

    print(f"Removed columns: {len(existing_columns)}")
    print(f"New shape      : {df.shape}")

    if missing_columns:
        print("\nColumns not found:")
        for col in missing_columns:
            print(f"  - {col}")

    df.to_csv(output_file, index=False)

    print(f"Saved to: {output_file}")

print("\nDone! All datasets have been cleaned.")