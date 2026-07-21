import subprocess
import itertools
import json
import shutil
import pandas as pd
import sys
import time
from pathlib import Path

# --- 1. Search Space (13 Archs * 2 Opts * 2 LRs = 52 Runs) ---
ARCHITECTURES = [
    [16], [32],                          # 1 Layer
    [16, 16], [32, 32], [32, 16],        # 2 Layers (Symmetric + Bottleneck)
    [16, 32], [24, 24], [24, 12],        # 2 Layers (Expansion + Funnel)
    [16, 16, 16], [32, 32, 32],          # 3 Layers (Symmetric)
    [32, 16, 8], [8, 16, 32],            # 3 Layers (Funnel + Expansion)
    [32, 24, 16]                         # 3 Layers (Gradual Funnel)
]
OPTIMIZERS = ["Adam", "SGD"]
LEARNING_RATES = [0.001, 0.0005]

# --- 2. Absolute Path Configuration ---
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
CONFIG_PATH = ROOT / "ml" / "config.py"
MODELS_ROOT = ROOT / "models"
ALL_RUNS_DIR = MODELS_ROOT / "all_runs"
CHAMPIONS_DIR = MODELS_ROOT / "champions"
REPORTS_DIR = ROOT / "reports"
STATE_FILE = REPORTS_DIR / "sweeps" / "sweep_state.json"
SUMMARY_CSV = REPORTS_DIR / "sweeps" / "mega_sweep_summary.csv"

# Ensure directories exist
for d in [ALL_RUNS_DIR, CHAMPIONS_DIR, REPORTS_DIR / "sweeps"]:
    d.mkdir(parents=True, exist_ok=True)

# The template that will be written to ml/config.py for every run
CONFIG_TEMPLATE = """
import torch
import json
from pathlib import Path

class Config:
    ROOT = Path(r"C:\\Users\\a\\Desktop\\BNNana")
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    _feat_file = ARTIFACT_DIR / "selected_features.json"
    INPUT_SIZE = len(json.load(open(_feat_file))) if _feat_file.exists() else 17
    
    # --- SWEEP PARAMETERS ---
    HIDDEN_LAYERS = {hidden_layers}
    OPTIMIZER_TYPE = "{optimizer}"
    LEARNING_RATE = {lr}
    # ------------------------

    OUTPUT_SIZE = 1
    ACTIVATION_TYPE = "Hardtanh"  # Standard for BNN/BWN
    ACTIVATION_PARAMS = {{"min_val": 0.0, "max_val": 1.0}}
    
    BATCH_SIZE = 64
    NUM_EPOCHS = 40 
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    WEIGHT_DECAY = 1e-5
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 3
    EARLY_STOPPING_PATIENCE = 8
    LOSS_TYPE = "BCEWithLogits"
    POS_WEIGHT = 1.2  # Slight boost for DDoS class

    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bwn_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler.pkl"
    METRICS_PATH = REPORT_DIR / "metrics.json"
    REPORT_PATH = REPORT_DIR / "training_report.md"

cfg = Config()
"""

def run_cmd(cmd):
    # check=True will stop the sweep if a training run crashes
    subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    # Use SINGLE braces here because this is actual Python code
    return {
        "last_index": -1,
        "champions": {
            "accuracy": {"score": 0, "id": ""},
            "precision": {"score": 0, "id": ""},
            "recall": {"score": 0, "id": ""},
            "f1_score": {"score": 0, "id": ""},
            "overall": {"score": 0, "id": ""}
        },
        "results": []
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def main():
    grid = list(itertools.product(ARCHITECTURES, OPTIMIZERS, LEARNING_RATES))
    state = load_state()
    start_idx = state["last_index"] + 1

    if start_idx >= len(grid):
        print("✅ Sweep already complete. Delete sweep_state.json to restart.")
        return

    print(f"🚀 Starting Mega-Sweep: {len(grid)} experiments total.")
    print(f"📂 Reports: {REPORTS_DIR}")
    print(f"📂 Models: {MODELS_ROOT}")

    try:
        for i in range(start_idx, len(grid)):
            layers, opt, lr = grid[i]
            run_id = f"run_{i+1}_L{len(layers)}_Arch{'-'.join(map(str, layers))}_{opt}_LR{lr}"
            
            print(f"\n>>> [{i+1}/{len(grid)}] RUNNING: {run_id}")

            # 1. Update config.py
            with open(CONFIG_PATH, "w") as f:
                f.write(CONFIG_TEMPLATE.format(hidden_layers=layers, optimizer=opt, lr=lr))

            # 2. Run Train & Evaluate
            start_time = time.time()
            run_cmd("python -m ml.train")
            run_cmd("python -m ml.evaluate")
            duration = time.time() - start_time

            # 3. Collect Metrics
            try:
                with open(REPORTS_DIR / "metrics.json", "r") as f:
                    m = json.load(f)
                
                m['overall'] = (m['accuracy'] + m['f1_score']) / 2
                m['run_id'] = run_id
                m['duration_s'] = duration
                state["results"].append(m)

                # 4. Archive Model
                shutil.copy(ROOT / "artifacts" / "best_bwn_model.pth", ALL_RUNS_DIR / f"{run_id}.pth")

                # 5. Update Champions
                for metric in state["champions"].keys():
                    if m[metric] > state["champions"][metric]["score"]:
                        state["champions"][metric]["score"] = m[metric]
                        state["champions"][metric]["id"] = run_id
                        
                        # Save Champion
                        shutil.copy(ROOT / "artifacts" / "best_bwn_model.pth", CHAMPIONS_DIR / f"top_{metric}.pth")
                        with open(CHAMPIONS_DIR / f"top_{metric}_info.json", "w") as f:
                            json.dump(m, f, indent=4)

            except Exception as e:
                print(f"   ⚠️ Error processing metrics for {run_id}: {e}")

            # 6. Save State & CSV
            state["last_index"] = i
            save_state(state)
            pd.DataFrame(state["results"]).to_csv(SUMMARY_CSV, index=False)

    except KeyboardInterrupt:
        print("\n🛑 Sweep paused by user. Run again to resume from this point.")
        sys.exit(0)

    print("\n" + "="*60)
    print("🏆 MEGA-SWEEP COMPLETE 🏆")
    print("="*60)
    for metric, data in state["champions"].items():
        print(f"Best {metric.upper():<10}: {data['score']:.4f} ({data['id']})")
    print("="*60)

if __name__ == "__main__":
    main()