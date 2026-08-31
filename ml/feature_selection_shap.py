import pandas as pd
import numpy as np
import shap
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# ------------------------------------------------------------
# Configuration & Tier-1 Whitelist
# ------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATASET_PATH = ROOT / "datasets" / "processed" / "master_dataset.csv"
REPORT_DIR = ROOT / "reports"
ARTIFACT_DIR = ROOT / "artifacts"
RANDOM_SEED = 42

TIER_1 = [
    "Destination Port", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Total Length of Fwd Packets", "Total Length of Bwd Packets", "Subflow Fwd Bytes",
    "Subflow Bwd Bytes", "Subflow Fwd Packets", "Subflow Bwd Packets", "Max Packet Length",
    "Min Packet Length", "Fwd Packet Length Max", "Bwd Packet Length Max", "ACK Flag Count",
    "SYN Flag Count", "RST Flag Count", "FIN Flag Count", "PSH Flag Count", "URG Flag Count",
    "Bwd Header Length", "Fwd Header Length", "min_seg_size_forward", "act_data_pkt_fwd"
]

SUBSET_SIZES = [17, 15, 12, 10, 8]

def run_shap_selection():
    REPORT_DIR.mkdir(exist_ok=True)
    ARTIFACT_DIR.mkdir(exist_ok=True)

    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH, low_memory=False)
    
    available_features = [f for f in TIER_1 if f in df.columns]
    X = df[available_features]
    y = df["Label"]

    # 1. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_SEED
    )

    # 2. Train Selector Model
    print(f"Training RF Selector on {len(X_train):,} samples...")
    rf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED, n_jobs=-1)
    rf.fit(X_train, y_train)

    # 3. SHAP Analysis
    print("Calculating SHAP values...")
    explainer = shap.TreeExplainer(rf)
    
    # Sample 1000 rows and keep track of their true labels
    shap_sample = X_train.sample(min(1000, len(X_train)), random_state=RANDOM_SEED)
    y_sample = y_train.loc[shap_sample.index].values 
    
    raw_shap_values = explainer.shap_values(shap_sample)

    # --- Corrected SHAP Interpretation ---
    # For binary classification, we focus on the SHAP values for the 'Attack' class (index 1)
    # If RF returns a list [benign_shap, attack_shap], we take index 1.
    if isinstance(raw_shap_values, list):
        shap_values = raw_shap_values[1]
    elif len(raw_shap_values.shape) == 3:
        shap_values = raw_shap_values[:, :, 1]
    else:
        shap_values = raw_shap_values

    # Group SHAP values by the GROUND TRUTH labels of the samples
    benign_mask = (y_sample == 0)
    attack_mask = (y_sample == 1)

    # Calculate Mean Absolute SHAP for each ground truth group
    # This shows which features the model relies on when seeing Benign vs Attack traffic
    benign_impact = np.abs(shap_values[benign_mask]).mean(axis=0)
    attack_impact = np.abs(shap_values[attack_mask]).mean(axis=0)
    global_impact = np.abs(shap_values).mean(axis=0)

    # 4. Generate Importance Report
    results = pd.DataFrame({
        "Feature": available_features,
        "Global_Mean_Abs_SHAP": global_impact,
        "Impact_on_Benign_Samples": benign_impact,
        "Impact_on_Attack_Samples": attack_impact
    })

    results["Normalized_Importance"] = results["Global_Mean_Abs_SHAP"] / results["Global_Mean_Abs_SHAP"].sum()
    results = results.sort_values("Global_Mean_Abs_SHAP", ascending=False).reset_index(drop=True)
    results["Rank"] = results.index + 1

    # 5. Create Candidate Subsets
    subsets = {}
    for size in SUBSET_SIZES:
        subsets[f"top_{size}"] = results.head(size)["Feature"].tolist()

    # 6. Proxy Validation
    print("\nValidating Top 17 subset with Proxy RF...")
    top_features = subsets["top_17"]
    val_rf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED, n_jobs=-1)
    val_rf.fit(X_train[top_features], y_train)
    y_pred = val_rf.predict(X_test[top_features])
    
    print(f"Proxy RF Accuracy (Top 17): {accuracy_score(y_test, y_pred):.4%}")
    print(f"Proxy RF F1-Score (Top 17): {f1_score(y_test, y_pred):.4%}")

    # 7. Save Artifacts
    results.to_csv(REPORT_DIR / "shap_feature_importance.csv", index=False)
    with open(ARTIFACT_DIR / "shap_subsets.json", "w") as f:
        json.dump(subsets, f, indent=4)
    with open(ARTIFACT_DIR / "selected_features.json", "w") as f:
        json.dump(subsets["top_17"], f, indent=4)

    print(f"\nSHAP Analysis Complete. Results saved to {ARTIFACT_DIR}")

if __name__ == "__main__":
    run_shap_selection()