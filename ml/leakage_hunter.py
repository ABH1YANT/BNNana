import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# --- Paths ---
ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")
DATA_PATH = ROOT / "datasets" / "processed" / "master_dataset.csv"

def hunt_the_leak():
    # The FULL 16 features including Destination Port
    features = [
        "Min Packet Length",
        "Subflow Bwd Packets",
        "Destination Port", # Added back
        "Bwd Header Length",
        "Total Backward Packets",
        "min_seg_size_forward",
        "Fwd Packet Length Max",
        "Max Packet Length",
        "ACK Flag Count",
        "Bwd Packet Length Max",
        "Total Length of Bwd Packets",
        "Subflow Bwd Bytes",
        "Total Length of Fwd Packets",
        "Subflow Fwd Bytes",
        "Flow Duration",
        "Fwd Header Length"
    ]
    
    print(f"Loading data for Leakage Hunting... (Total Features: {len(features)})")
    df = pd.read_csv(DATA_PATH)
    
    # Ensure all features exist in the dataframe
    existing_features = [f for f in features if f in df.columns]
    X = df[existing_features]
    y = df["Label"]

    print("Training Random Forest to check feature importance...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X, y)
    
    importances = pd.DataFrame({
        'feature': existing_features,
        'importance': rf.feature_importances_
    }).sort_values(by='importance', ascending=False)

    print("\n--- Feature Importance (The Full List) ---")
    print(importances)
    
    # Check for duplicates across these 16 features
    duplicates = df.duplicated(subset=existing_features + ["Label"]).sum()
    print(f"\n--- Duplicate Check ---")
    print(f"Total Rows: {len(df)}")
    print(f"Duplicate Rows: {duplicates} ({duplicates/len(df):.2%})")
    print(f"Unique Rows: {len(df) - duplicates}")

if __name__ == "__main__":
    hunt_the_leak()