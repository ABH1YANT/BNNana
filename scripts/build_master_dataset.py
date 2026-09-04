from pathlib import Path
import pandas as pd
import numpy as np
import json

# ------------------------------------------------------------------
# Configuration & Hardware Limits
# ------------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATASET_DIR = ROOT / "datasets" / "processed"
OUTPUT_FILE = DATASET_DIR / "master_dataset.csv"

# Hardware-defined limits based on bit-widths
HW_LIMITS = {
    # Packet Lengths (17 bits: 0 - 65,536)
    "Max Packet Length": 65536,
    "Min Packet Length": 65536,
    "Fwd Packet Length Max": 65536,
    "Bwd Packet Length Max": 65536,
    
    # Total/Subflow Bytes (24 bits: 0 - 16,777,216 [16MB])
    "Total Length of Fwd Packets": 16777216,
    "Total Length of Bwd Packets": 16777216,
    "Subflow Fwd Bytes": 16777216,
    "Subflow Bwd Bytes": 16777216,
    
    # Header Lengths (20 bits: 0 - 1,048,576 [1MB])
    "Fwd Header Length": 1048576,
    "Bwd Header Length": 1048576,
    
    # Port (16 bits: 0 - 65,535)
    "Destination Port": 65535,
    
    # Packet Counts (17 bits: 0 - 100,000)
    "Total Fwd Packets": 100000,
    "Total Backward Packets": 100000,
    "Subflow Fwd Packets": 100000,
    "Subflow Bwd Packets": 100000,
    "act_data_pkt_fwd": 100000,
    
    # Flow Duration (27 bits: 0 - 120,000,000 µs)
    "Flow Duration": 120000000,
    
    # Segment Size (11 bits: 0 - 1,500)
    "min_seg_size_forward": 1500,
    
    # Flag Counts (10 bits: 0 - 1,000)
    "ACK Flag Count": 1000,
    "SYN Flag Count": 1000,
    "RST Flag Count": 1000,
    "FIN Flag Count": 1000,
    "PSH Flag Count": 1000,
    "URG Flag Count": 1000
}

REQUIRED_COLUMNS = list(HW_LIMITS.keys())

# Sampling Requirements
BENIGN_FILE = "BENIGN.csv"
ATTACK_FILES = ["SYN.csv", "UDP.csv", "DNS.csv"]
SAMPLES_BENIGN = 200_000
SAMPLES_PER_ATTACK = 66_667 

LABEL_MAP = {
    "BENIGN": "BENIGN",
    "Syn": "SYN", "SYN": "SYN", "DrDoS_SYN": "SYN",
    "UDP": "UDP", "DrDoS_UDP": "UDP",
    "DNS": "DNS", "DrDoS_DNS": "DNS",
}

BINARY_ENCODING = {"BENIGN": 0, "SYN": 1, "UDP": 1, "DNS": 1}

# ------------------------------------------------------------------
# Helper: Clean, Filter, Saturate, and Deduplicate
# ------------------------------------------------------------------
def clean_and_sample(path, target_label, n_samples, exclude_benign=False):
    print(f"Processing {path.name}...")
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()
    
    # 1. Keep ONLY required columns + Label
    df = df[REQUIRED_COLUMNS + ["Label"]]
    
    # 2. Normalize Labels and Filter
    df["Label"] = df["Label"].str.strip().replace(LABEL_MAP)
    if exclude_benign:
        df = df[df["Label"] == target_label]
    else:
        df = df[df["Label"] == "BENIGN"]

    # 3. Data Cleaning (Remove Inf and NaN)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    # 4. Remove Negative Values
    df = df[(df[REQUIRED_COLUMNS] >= 0).all(axis=1)]

    # 5. HARDWARE SATURATION (Clipping)
    # This ensures values fit in the defined bit-widths
    for col, limit in HW_LIMITS.items():
        df[col] = df[col].clip(upper=limit)

    # 6. Feature-Specific Deduplication
    df = df.drop_duplicates(subset=REQUIRED_COLUMNS + ["Label"])
    
    # 7. Sampling
    if len(df) > n_samples:
        df = df.sample(n=n_samples, random_state=42)
    else:
        print(f"   Warning: Only {len(df):,} unique valid samples available for {target_label}")
        
    return df

# ------------------------------------------------------------------
# Main Pipeline
# ------------------------------------------------------------------
processed_dfs = []

# Process Benign
path_benign = DATASET_DIR / BENIGN_FILE
if path_benign.exists():
    processed_dfs.append(clean_and_sample(path_benign, "BENIGN", SAMPLES_BENIGN))

# Process Attacks
for f in ATTACK_FILES:
    path_attack = DATASET_DIR / f
    if path_attack.exists():
        target = f.replace(".csv", "")
        processed_dfs.append(clean_and_sample(path_attack, target, SAMPLES_PER_ATTACK, exclude_benign=True))

# Merge and Final Global Deduplication
print("\nMerging and performing final cross-file deduplication...")
master = pd.concat(processed_dfs, ignore_index=True)
master = master.drop_duplicates(subset=REQUIRED_COLUMNS + ["Label"]).reset_index(drop=True)

# Binary Encoding
master["Label"] = master["Label"].map(BINARY_ENCODING)

# Shuffle and Save
print("Shuffling and saving...")
master = master.sample(frac=1, random_state=42).reset_index(drop=True)
master.to_csv(OUTPUT_FILE, index=False)

# Save feature order
with open(DATASET_DIR / "feature_order.json", "w") as f:
    json.dump(REQUIRED_COLUMNS, f, indent=4)

print("\n" + "="*30)
print("FINAL DATASET SUMMARY")
print("="*30)
print(master["Label"].value_counts().rename({0: "0 (Benign)", 1: "1 (Attack)"}))
print(f"Total Shape: {master.shape}")
print("Hardware Saturation: Applied")
print("Done.")