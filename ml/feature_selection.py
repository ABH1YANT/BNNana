from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.feature_selection import mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

# ------------------------------------------------------------
# Hardware-Friendly Whitelist (Tiers 1 & 2)
# ------------------------------------------------------------
TIER_1 = [
    "Destination Port", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Total Length of Fwd Packets", "Total Length of Bwd Packets", "Subflow Fwd Bytes",
    "Subflow Bwd Bytes", "Subflow Fwd Packets", "Subflow Bwd Packets", "Max Packet Length",
    "Min Packet Length", "Fwd Packet Length Max", "Bwd Packet Length Max", "ACK Flag Count",
    "SYN Flag Count", "RST Flag Count", "FIN Flag Count", "PSH Flag Count", "URG Flag Count",
    "Bwd Header Length", "Fwd Header Length", "min_seg_size_forward", "act_data_pkt_fwd"
]

TIER_2 = [
    "Average Packet Size", "Avg Fwd Segment Size", "Avg Bwd Segment Size"
]

WHITELIST = TIER_1

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATASET = ROOT / "datasets" / "processed" / "master_dataset.csv"
REPORT_DIR = ROOT / "reports"
ARTIFACT_DIR = ROOT / "artifacts"

REPORT_DIR.mkdir(exist_ok=True)
ARTIFACT_DIR.mkdir(exist_ok=True)

TOP_N = 24
CORR_THRESHOLD = 0.95 

def normalize_series(s):
    """Standard Min-Max normalization with division-by-zero protection."""
    rng = s.max() - s.min()
    if rng == 0:
        return np.zeros(len(s))
    return (s - s.min()) / rng

def main():
    print("Loading dataset...")
    df = pd.read_csv(DATASET, low_memory=False)

    # 1. Filter by Whitelist (Hardware-Aware)
    available_features = [f for f in WHITELIST if f in df.columns]
    X = df[available_features]
    y = df["Label"]

    # 2. Train/Test Split (Prevent Data Leakage)
    # Feature selection math will only see X_train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"Data split: {len(X_train):,} train samples, {len(X_test):,} test samples.")

    # ------------------------------------------------------------
    # 3. Calculate Importance Metrics (On Train Set Only)
    # ------------------------------------------------------------
    print("Calculating Mutual Information...")
    mi_scores = mutual_info_classif(X_train, y_train, random_state=42)

    print("Training Random Forest (300 estimators) for stable importance...")
    rf_selector = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    rf_selector.fit(X_train, y_train)
    rf_scores = rf_selector.feature_importances_

    results = pd.DataFrame({
        "Feature": X_train.columns,
        "MI_Raw": mi_scores,
        "RF_Raw": rf_scores
    })

    results["MI_Norm"] = normalize_series(results["MI_Raw"])
    results["RF_Norm"] = normalize_series(results["RF_Raw"])
    results["Combined_Score"] = results["MI_Norm"] + results["RF_Norm"]
    results = results.sort_values("Combined_Score", ascending=False)

    # ------------------------------------------------------------
    # 4. Correlation Filtering (On Train Set Only)
    # ------------------------------------------------------------
    print(f"Applying redundancy filter (Threshold: {CORR_THRESHOLD})...")
    corr_matrix = X_train.corr().abs()
    selected_features = []
    
    for feature in results["Feature"]:
        is_redundant = False
        for selected in selected_features:
            if corr_matrix.loc[feature, selected] > CORR_THRESHOLD:
                is_redundant = True
                break
        if not is_redundant:
            selected_features.append(feature)
        if len(selected_features) == TOP_N:
            break

    # ------------------------------------------------------------
    # 5. Proxy RF Accuracy (Sanity Check)
    # ------------------------------------------------------------
    print(f"\nEvaluating selection with Proxy RF using {TOP_N} features...")
    
    # Train on selected features only
    val_clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    val_clf.fit(X_train[selected_features], y_train)
    
    # Test on untouched test set
    y_pred = val_clf.predict(X_test[selected_features])

    proxy_acc = accuracy_score(y_test, y_pred)
    proxy_f1 = f1_score(y_test, y_pred)

    # ------------------------------------------------------------
    # 6. Save Artifacts and Metadata
    # ------------------------------------------------------------
    print("\n" + "="*40)
    print("FEATURE SELECTION RESULTS")
    print("="*40)
    print(f"Proxy RF Accuracy: {proxy_acc:.4%}")
    print(f"Proxy RF F1-Score: {proxy_f1:.4%}")
    
    # Save descriptive JSON
    metadata = {
        "selected_features": selected_features,
        "proxy_rf_metrics": {
            "accuracy": proxy_acc,
            "f1_score": proxy_f1
        },
        "parameters": {
            "top_n": TOP_N,
            "correlation_threshold": CORR_THRESHOLD,
            "hardware_aware_filter": True,
            "leakage_protection": True
        }
    }

    with open(ARTIFACT_DIR / "selected_features.json", "w") as f:
        json.dump(selected_features, f, indent=4) # Keep simple list for model.py

    with open(ARTIFACT_DIR / "feature_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    # Save Detailed CSV Report
    results["Is_Selected"] = results["Feature"].isin(selected_features)
    results.to_csv(REPORT_DIR / "feature_importance.csv", index=False)

    print(f"\nSelected features saved to {ARTIFACT_DIR / 'selected_features.json'}")
    print(f"Detailed metadata saved to {ARTIFACT_DIR / 'feature_metadata.json'}")

if __name__ == "__main__":
    main()