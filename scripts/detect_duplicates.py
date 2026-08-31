import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# --- Dynamic Pathing ---
# Finds the BNNana root folder automatically
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "datasets" / "processed" / "master_dataset.csv"
FEATURES_PATH = ROOT / "artifacts" / "selected_features.json"

def hunt_the_leak():
    # 1. Load the features from JSON
    if not FEATURES_PATH.exists():
        print(f"ERROR: {FEATURES_PATH} not found. Run feature selection first.")
        return
    
    with open(FEATURES_PATH, "r") as f:
        features = json.load(f)
    
    print(f"Loaded {len(features)} features from selected_features.json")

    # 2. Load the dataset
    if not DATA_PATH.exists():
        print(f"ERROR: Could not find dataset at {DATA_PATH}")
        return

    print(f"Loading dataset: {DATA_PATH.name}...")
    df = pd.read_csv(DATA_PATH)
    
    # 3. Verify features exist in the CSV
    available_features = [f for f in features if f in df.columns]
    if len(available_features) != len(features):
        missing = set(features) - set(available_features)
        print(f"WARNING: {len(missing)} features in JSON are missing from CSV: {missing}")

    X = df[available_features]
    y = df["Label"]

    # 4. Feature Importance (Leakage Check)
    print(f"Training Random Forest on {len(available_features)} features to find 'too-good' predictors...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X, y)
    
    importances = pd.DataFrame({
        'feature': available_features,
        'importance': rf.feature_importances_
    }).sort_values(by='importance', ascending=False)

    print("\n--- Feature Importance (Top Predictors) ---")
    print(importances.head(10))
    if importances['importance'].iloc[0] > 0.80:
        print(f"\n!!! ALERT: Feature '{importances['feature'].iloc[0]}' has extremely high importance.")
        print("This is a strong indicator of data leakage.")

    # 5. Duplicate Check
    # We check for duplicates ONLY on the features the model sees
    duplicates = df.duplicated(subset=available_features).sum()
    print(f"\n--- Duplicate Check (Based on Selected Features) ---")
    print(f"Total Rows: {len(df):,}")
    print(f"Duplicate Rows: {duplicates:,} ({duplicates/len(df):.2%})")
    
    if (duplicates/len(df)) > 0.10:
        print("\n!!! ALERT: High number of duplicates detected.")
        print("If your train/test split contains these duplicates, the model is 'cheating' by seeing the test data during training.")

if __name__ == "__main__":
    hunt_the_leak()