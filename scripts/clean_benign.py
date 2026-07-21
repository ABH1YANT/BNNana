"""
clean_benign.py

Cleans the Monday benign dataset from CIC-IDS2017.
"""

from pathlib import Path
import pandas as pd

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

ROOT = Path(r"C:\Users\a\Desktop\BNNana")

INPUT_FILE = ROOT / "datasets" / "raw" / "Monday-WorkingHours.pcap_ISCX.csv"
OUTPUT_FILE = ROOT / "datasets" / "processed" / "BENIGN.csv"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Columns to remove
# ------------------------------------------------------------------

COLUMNS_TO_DROP = [
    "Fwd PSH Flags",
    " Bwd PSH Flags",
    " Fwd URG Flags",
    " Bwd URG Flags",
    " Fwd Header Length.1",
    "Fwd Avg Bytes/Bulk",
    " Fwd Avg Packets/Bulk",
    " Fwd Avg Bulk Rate",
    " Bwd Avg Bytes/Bulk",
    " Bwd Avg Packets/Bulk",
    "Bwd Avg Bulk Rate",
]

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Original shape : {df.shape}")

existing = [c for c in COLUMNS_TO_DROP if c in df.columns]

df.drop(columns=existing, inplace=True)

print(f"Removed columns: {len(existing)}")
print(f"New shape      : {df.shape}")

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Ensure label is consistent
df["Label"] = "BENIGN"

df.to_csv(OUTPUT_FILE, index=False)

print(f"\nSaved to:\n{OUTPUT_FILE}")