from pathlib import Path
import pandas as pd
import numpy as np
import json
import sys

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATASET_DIR = ROOT / "datasets" / "processed"
OUTPUT_FILE = DATASET_DIR / "master_dataset.csv"
SELECTED_FEATS_PATH = ROOT / "artifacts" / "selected_features.json"

# Sampling Targets
TARGET_BENIGN = 200_000
TARGET_ATTACK_PER_TYPE = 66_667 # Total ~200,001

ATTACK_FILES = ["SYN.csv", "UDP.csv", "DNS.csv"]
BENIGN_FILE = "BENIGN.csv"

LABEL_MAP = {
    "BENIGN": "BENIGN",
    "Syn": "SYN", "SYN": "SYN", "DrDoS_SYN": "SYN",
    "UDP": "UDP", "DrDoS_UDP": "UDP",
    "DNS": "DNS", "DrDoS_DNS": "DNS",
}

BINARY_ENCODING = {"BENIGN": 0, "SYN": 1, "UDP": 1, "DNS": 1}

# ------------------------------------------------------------------
# 1. Load Selected Features
# ------------------------------------------------------------------
if not SELECTED_FEATS_PATH.exists():
    print(f"ERROR: {SELECTED_FEATS_PATH} not found.")
    sys.exit(1)

with open(SELECTED_FEATS_PATH, "r") as f:
    SELECTED_FEATURES = json.load(f)

print(f"Targeting {len(SELECTED_FEATURES)} features defined in artifacts.")

# ------------------------------------------------------------------
# 2. Extraction Function
# ------------------------------------------------------------------
def extract_unique_candidates(filename, target_label, exclude_benign=False):
    path = DATASET_DIR / filename
    if not path.exists():
        print(f"Warning: {filename} not found.")
        return pd.DataFrame()

    print(f"Reading {filename}...")
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()
    
    # Normalize Labels
    df["Label"] = df["Label"].str.strip().replace(LABEL_MAP)
    
    # Filter
    if exclude_benign:
        df = df[df["Label"] == target_label]
    else:
        df = df[df["Label"] == "BENIGN"]

    # Keep only selected features + Label
    df = df[SELECTED_FEATURES + ["Label"]]

    # Clean
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    
    # Local deduplication to save memory
    df = df.drop_duplicates(subset=SELECTED_FEATURES)
    
    return df

# ------------------------------------------------------------------
# 3. Build Global Pool
# ------------------------------------------------------------------
all_candidates = []

# Get Benign
all_candidates.append(extract_unique_candidates(BENIGN_FILE, "BENIGN"))

# Get Attacks
for f in ATTACK_FILES:
    label = f.replace(".csv", "")
    all_candidates.append(extract_unique_candidates(f, label, exclude_benign=True))

print("\nMerging all files for global deduplication...")
master_pool = pd.concat(all_candidates, ignore_index=True)

# GLOBAL DEDUPLICATION
# This removes duplicates across different files.
# If the same feature pattern exists in BENIGN.csv and SYN.csv, 
# we drop the duplicates to ensure the model doesn't see the same data twice.
initial_count = len(master_pool)
master_pool = master_pool.drop_duplicates(subset=SELECTED_FEATURES)
final_count = len(master_pool)

print(f"Global deduplication complete.")
print(f"Removed {initial_count - final_count:,} cross-file duplicates.")

# ------------------------------------------------------------------
# 4. Final Sampling and Validation
# ------------------------------------------------------------------
final_subsets = []

print("\nFinal Class Balancing:")

# Process Benign
benign_pool = master_pool[master_pool["Label"] == "BENIGN"]
print(f"BENIGN : Available unique rows: {len(benign_pool):,}")
if len(benign_pool) < TARGET_BENIGN:
    print(f"!!! WARNING: Shortfall of {TARGET_BENIGN - len(benign_pool):,} rows for BENIGN")
final_subsets.append(benign_pool.sample(n=min(len(benign_pool), TARGET_BENIGN), random_state=42))

# Process each Attack type
for attack_label in ["SYN", "UDP", "DNS"]:
    attack_pool = master_pool[master_pool["Label"] == attack_label]
    print(f"{attack_label:6s} : Available unique rows: {len(attack_pool):,}")
    
    if len(attack_pool) < TARGET_ATTACK_PER_TYPE:
        print(f"!!! WARNING: Shortfall of {TARGET_ATTACK_PER_TYPE - len(attack_pool):,} rows for {attack_label}")
    
    final_subsets.append(attack_pool.sample(n=min(len(attack_pool), TARGET_ATTACK_PER_TYPE), random_state=42))

# Combine balanced data
master = pd.concat(final_subsets, ignore_index=True)

# Encoding
master["Label"] = master["Label"].map(BINARY_ENCODING)

# Shuffle
master = master.sample(frac=1, random_state=42).reset_index(drop=True)

# Save
master.to_csv(OUTPUT_FILE, index=False)

# ------------------------------------------------------------------
# 5. Summary
# ------------------------------------------------------------------
print("\n" + "="*40)
print("FINAL MASTER DATASET SUMMARY")
print("="*40)
print(master["Label"].value_counts().rename({0: "0 (Benign)", 1: "1 (Attack)"}))
print(f"Total Rows: {len(master):,}")
print(f"Total Features: {len(SELECTED_FEATURES)}")
print(f"Saved to: {OUTPUT_FILE}")

if len(master) < (TARGET_BENIGN + (TARGET_ATTACK_PER_TYPE * 3)):
    print("\nSTATUS: Dataset created but sampling targets were NOT met due to uniqueness constraints.")
else:
    print("\nSTATUS: Success! All sampling targets met with 100% unique rows.")