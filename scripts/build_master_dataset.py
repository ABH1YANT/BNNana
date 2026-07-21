from pathlib import Path
import pandas as pd
import numpy as np
import json

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATASET_DIR = ROOT / "datasets" / "processed"
OUTPUT_FILE = DATASET_DIR / "master_dataset.csv"

# Sampling Requirements
BENIGN_FILE = "BENIGN.csv"
ATTACK_FILES = ["SYN.csv", "UDP.csv", "DNS.csv"]

SAMPLES_BENIGN = 200_000
SAMPLES_PER_ATTACK = 66_667  # 66,667 * 3 ≈ 200,000

LABEL_MAP = {
    "BENIGN": "BENIGN",
    "Syn": "SYN", "SYN": "SYN", "DrDoS_SYN": "SYN",
    "UDP": "UDP", "DrDoS_UDP": "UDP",
    "DNS": "DNS", "DrDoS_DNS": "DNS",
}

# 0 = Benign, 1 = Attack
BINARY_ENCODING = {
    "BENIGN": 0,
    "SYN": 1,
    "UDP": 1,
    "DNS": 1
}

# ------------------------------------------------------------------
# Helper: Clean and Filter
# ------------------------------------------------------------------
def clean_and_sample(path, target_label, n_samples, exclude_benign=False):
    print(f"Processing {path.name}...")
    df = pd.read_csv(path, low_memory=False)
    
    # 1. Strip whitespace from columns
    df.columns = df.columns.str.strip()
    
    # 2. Normalize Labels
    df["Label"] = df["Label"].str.strip().replace(LABEL_MAP)
    
    # 3. Filter logic
    if exclude_benign:
        # Keep only the specific attack label, ignore Benign rows in attack files
        df = df[df["Label"] == target_label]
    else:
        # For the Benign file, ensure we only take Benign rows
        df = df[df["Label"] == "BENIGN"]

    # 4. Data Cleaning (Remove Inf and NaN)
    # Replace inf with NaN, then drop any row containing a NaN
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    # 5. Sampling
    if len(df) > n_samples:
        df = df.sample(n=n_samples, random_state=42)
    else:
        print(f"   Warning: Only {len(df)} samples available for {target_label}")
        
    return df

# ------------------------------------------------------------------
# Main Pipeline
# ------------------------------------------------------------------

# 1. Determine Common Columns first (to avoid memory issues later)
print("Determining common features across all files...")
common_cols = None
all_files = [BENIGN_FILE] + ATTACK_FILES

for f in all_files:
    path = DATASET_DIR / f
    if path.exists():
        cols = set(pd.read_csv(path, nrows=0).columns.str.strip())
        if common_cols is None:
            common_cols = cols
        else:
            common_cols &= cols

common_cols = sorted(list(common_cols))
print(f"Found {len(common_cols)} common features.")

# 2. Process and Collect Dataframes
processed_dfs = []

# Process Benign
path_benign = DATASET_DIR / BENIGN_FILE
if path_benign.exists():
    df_b = clean_and_sample(path_benign, "BENIGN", SAMPLES_BENIGN, exclude_benign=False)
    processed_dfs.append(df_b[common_cols])

# Process Attacks
for f in ATTACK_FILES:
    path_attack = DATASET_DIR / f
    if path_attack.exists():
        # Extract target label from filename (e.g., "SYN" from "SYN.csv")
        target = f.replace(".csv", "")
        df_a = clean_and_sample(path_attack, target, SAMPLES_PER_ATTACK, exclude_benign=True)
        processed_dfs.append(df_a[common_cols])

# 3. Merge
print("\nMerging datasets...")
master = pd.concat(processed_dfs, ignore_index=True)

# 4. Binary Encoding
print("Encoding labels (Benign=0, Attack=1)...")
master["Label"] = master["Label"].map(BINARY_ENCODING)

# 5. Final Cleaning Check
# Ensure no NaNs were introduced during concat and that all data is finite
master = master.replace([np.inf, -np.inf], np.nan).dropna()

# 6. Shuffle
print("Shuffling dataset...")
master = master.sample(frac=1, random_state=42).reset_index(drop=True)

# 7. Save Results
print(f"Saving to {OUTPUT_FILE}...")
master.to_csv(OUTPUT_FILE, index=False)

# Save feature order (excluding Label)
feature_order = [c for c in master.columns if c != "Label"]
with open(DATASET_DIR / "feature_order.json", "w") as f:
    json.dump(feature_order, f, indent=4)

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
print("\n" + "="*30)
print("FINAL DATASET SUMMARY")
print("="*30)
print(master["Label"].value_counts().rename({0: "0 (Benign)", 1: "1 (Attack)"}))
print(f"Total Shape: {master.shape}")
print(f"NaN Count:   {master.isna().sum().sum()}")
print("Done.")