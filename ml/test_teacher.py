import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# ------------------------------------------------------------------
# 1. Re-define Architecture
# ------------------------------------------------------------------
class ResidualBlock(nn.Module):
    def __init__(self, size):
        super().__init__()
        self.norm = nn.LayerNorm(size)
        self.net = nn.Sequential(
            nn.Linear(size, size * 2),
            nn.GELU(),
            nn.Linear(size * 2, size),
        )
    def forward(self, x):
        return x + self.net(self.norm(x))

class FPSuperTeacher(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.stem = nn.Sequential(nn.Linear(input_size, 512), nn.GELU())
        self.stack = nn.Sequential(
            ResidualBlock(512), nn.Linear(512, 256), nn.GELU(),
            ResidualBlock(256), nn.Linear(256, 128), nn.GELU(),
            ResidualBlock(128)
        )
        self.head = nn.Linear(128, 1)
    def forward(self, x):
        x = self.stem(x)
        x = self.stack(x)
        return self.head(x).squeeze(-1)

# ------------------------------------------------------------------
# 2. Configuration & Paths
# ------------------------------------------------------------------
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
DATA_DIR = ROOT / "datasets" / "processed"
MASTER_DATASET = DATA_DIR / "master_dataset.csv"
FEAT_PATH = ROOT / "artifacts" / "selected_features.json"
SCALER_PATH = ROOT / "artifacts" / "scaler_teacher.pkl"
MODEL_PATH = ROOT / "artifacts" / "teacher_model.pth"

CSV_SOURCES = {
    "BENIGN": DATA_DIR / "BENIGN.csv",
    "DNS": DATA_DIR / "DNS.csv",
    "SYN": DATA_DIR / "SYN.csv",
    "UDP": DATA_DIR / "UDP.csv"
}

SAMPLES_PER_CLASS = 25000
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():
    # 1. Load Metadata
    with open(FEAT_PATH, "r") as f:
        features = json.load(f)
    scaler = joblib.load(SCALER_PATH)
    
    # 2. Load "Seen" Data
    print("Loading Master Dataset to identify 'seen' samples...")
    master_df = pd.read_csv(MASTER_DATASET, usecols=features)
    seen_samples = set(tuple(x) for x in master_df.values)
    del master_df
    print(f"Identified {len(seen_samples):,} samples to exclude.")

    # 3. Collect Fresh Samples
    all_data = []
    
    for category, path in CSV_SOURCES.items():
        print(f"Extracting fresh samples from {category}...")
        chunks = pd.read_csv(path, low_memory=False, chunksize=100000)
        category_samples = []
        
        for chunk in chunks:
            # Clean column names
            chunk.columns = [str(c).strip() for c in chunk.columns]
            chunk = chunk.loc[:, ~chunk.columns.duplicated()].copy()
            
            # Find Label column
            label_cols = [c for c in chunk.columns if c.lower() == 'label']
            if not label_cols: continue
            
            # Extract labels safely
            raw_labels = chunk[label_cols[0]]
            if isinstance(raw_labels, pd.DataFrame):
                raw_labels = raw_labels.iloc[:, 0]

            # FIX: Corrected string accessor logic
            # We create a boolean mask: True if NOT benign, then convert to int (1 for attack, 0 for benign)
            is_attack = raw_labels.astype(str).str.strip().str.upper() != "BENIGN"
            chunk['BinaryLabel'] = is_attack.astype(int)
            
            # Filter to unique rows within chunk
            chunk = chunk.drop_duplicates(subset=features)
            
            # Filter out samples already in master_dataset
            chunk_vals = chunk[features].values
            chunk = chunk[[tuple(x) not in seen_samples for x in chunk_vals]]
            
            if not chunk.empty:
                category_samples.append(chunk[features + ['BinaryLabel']])
            
            current_total = sum(len(c) for c in category_samples)
            if current_total >= SAMPLES_PER_CLASS:
                break
        
        if category_samples:
            cat_df = pd.concat(category_samples).head(SAMPLES_PER_CLASS)
            cat_df['Source'] = category
            all_data.append(cat_df)
            print(f"   Collected {len(cat_df):,} unique, unseen samples.")
        else:
            print(f"   Warning: No samples found for {category}")

    if not all_data:
        print("Error: No data collected at all. Check file paths.")
        return

    test_df = pd.concat(all_data).reset_index(drop=True)

    # 4. Preprocessing
    X_raw = test_df[features].values
    y_true = test_df['BinaryLabel'].values
    
    print("\nApplying Log-Transform and Scaling...")
    X_log = np.log1p(np.abs(X_raw))
    X_scaled = scaler.transform(X_log)

    # 5. Model Inference
    print(f"Loading Teacher Model on {DEVICE}...")
    model = FPSuperTeacher(len(features)).to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()

    X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(DEVICE)
    
    with torch.no_grad():
        batch_size = 5000
        y_pred_list = []
        for i in range(0, len(X_tensor), batch_size):
            batch_x = X_tensor[i:i+batch_size]
            logits = model(batch_x)
            preds = (torch.sigmoid(logits) > 0.5).cpu().numpy()
            y_pred_list.extend(preds)
        
    y_pred = np.array(y_pred_list).astype(int)
    test_df['Prediction'] = y_pred

    # 6. Analysis and Reporting
    print("\n" + "="*50)
    print("         TEACHER MODEL STRESS TEST REPORT")
    print("="*50)

    print(f"\nOVERALL PERFORMANCE (N={len(test_df):,})")
    print("-" * 30)
    print(f"Accuracy  : {accuracy_score(y_true, y_pred):.6%}")
    print(f"F1-Score  : {f1_score(y_true, y_pred):.6%}")
    print(f"Precision : {precision_score(y_true, y_pred):.6%}")
    print(f"Recall    : {recall_score(y_true, y_pred):.6%}")
    print("\nOverall Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))

    for source in CSV_SOURCES.keys():
        subset = test_df[test_df['Source'] == source]
        if subset.empty: continue
        s_true = subset['BinaryLabel'].values
        s_pred = subset['Prediction'].values
        print(f"\nCATEGORY: {source}")
        print("-" * 30)
        print(f"Accuracy : {accuracy_score(s_true, s_pred):.6%}")
        print("Confusion Matrix:")
        print(confusion_matrix(s_true, s_pred, labels=[0, 1]))

    print("\n" + "="*50)
    print("Analysis Complete.")

if __name__ == "__main__":
    main()