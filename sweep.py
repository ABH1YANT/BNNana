import subprocess
import itertools
import json
import shutil
import pandas as pd
import sys
import time
from pathlib import Path

ARCHITECTURES = [
    # 3 Layers
    [16, 16, 16], [32, 32, 32],          # Symmetric
    [32, 16, 8], [8, 16, 32],            # Funnel / Expansion
    [32, 24, 16],                        # Gradual Funnel
    
    # 4 Layers
    [16, 16, 16, 16], [32, 32, 32, 32],  # Symmetric
    [32, 24, 16, 8], [8, 16, 24, 32],    # Funnel / Expansion
    
    # 5 Layers
    [16, 16, 16, 16, 16],                # Symmetric Small
    [32, 32, 32, 32, 32],                # Symmetric Large
    [32, 24, 16, 8, 4],                  # Deep Funnel
    [32, 32, 16, 16, 8]                  # Step Funnel
]
OPTIMIZERS = ["Adam", "SGD"]
LEARNING_RATES = [0.001, 0.0005]

# --- 2. Generalized Path Configuration ---
ROOT = Path(__file__).resolve().parent
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

# Template with BNN / Hardware-Aware parameters
CONFIG_TEMPLATE = """
import torch
import json
from pathlib import Path

class Config:
    ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = ROOT / "datasets" / "processed"
    ARTIFACT_DIR = ROOT / "artifacts"
    REPORT_DIR = ROOT / "reports"
    
    _feat_file = ARTIFACT_DIR / "selected_features.json"
    INPUT_SIZE = len(json.load(open(_feat_file))) if _feat_file.exists() else 17
    
    # --- SWEEP PARAMETERS ---
    HIDDEN_LAYERS = {hidden_layers}
    OPTIMIZER_TYPE = "{optimizer}"
    LEARNING_RATE = {lr}
    
    ACTIVATION_TYPE = "BinarySign" 
    ACTIVATION_PARAMS = {{}} 
    
    SIMULATE_FIXED_POINT = True
    FRACTIONAL_BITS = 8  
    # ------------------------

    OUTPUT_SIZE = 1
    BATCH_SIZE = 64
    NUM_EPOCHS = 50        
    RANDOM_SEED = 42
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    WEIGHT_DECAY = 1e-5
    SCHEDULER_FACTOR = 0.5
    SCHEDULER_PATIENCE = 4
    EARLY_STOPPING_PATIENCE = 10
    LOSS_TYPE = "BCEWithLogits"
    POS_WEIGHT = 1.2

    MODEL_SAVE_PATH = ARTIFACT_DIR / "best_bwn_model.pth"
    SCALER_PATH = ARTIFACT_DIR / "scaler.pkl"
    METRICS_PATH = REPORT_DIR / "metrics.json"
    REPORT_PATH = REPORT_DIR / "training_report.md"

cfg = Config()
"""

def run_cmd(cmd):
    full_cmd = f"{sys.executable} -m {cmd}"
    subprocess.run(full_cmd, shell=True, check=True, capture_output=True, text=True)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
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
        print("✅ Sweep already complete.")
        return

    print(f"🚀 Starting Deep BNN Sweep: {len(grid)} experiments (3-5 Layers).")

    try:
        for i in range(start_idx, len(grid)):
            layers, opt, lr = grid[i]
            run_id = f"run_{i+1}_L{len(layers)}_Arch{'-'.join(map(str, layers))}_{opt}_LR{lr}"
            
            print(f"\n>>> [{i+1}/{len(grid)}] RUNNING: {run_id}")

            with open(CONFIG_PATH, "w") as f:
                f.write(CONFIG_TEMPLATE.format(hidden_layers=layers, optimizer=opt, lr=lr))

            start_time = time.time()
            try:
                run_cmd("ml.train")
                run_cmd("ml.evaluate")
            except Exception as e:
                print(f"   ❌ Run {run_id} failed. Moving to next.")
                continue
                
            duration = time.time() - start_time

            try:
                with open(REPORTS_DIR / "metrics.json", "r") as f:
                    m = json.load(f)
                
                m['overall'] = (m['accuracy'] + m['f1_score']) / 2
                m['run_id'] = run_id
                m['duration_s'] = duration
                state["results"].append(m)

                shutil.copy(ROOT / "artifacts" / "best_bwn_model.pth", ALL_RUNS_DIR / f"{run_id}.pth")

                for metric in state["champions"].keys():
                    if m[metric] > state["champions"][metric]["score"]:
                        state["champions"][metric]["score"] = m[metric]
                        state["champions"][metric]["id"] = run_id
                        shutil.copy(ROOT / "artifacts" / "best_bwn_model.pth", CHAMPIONS_DIR / f"top_{metric}.pth")
                        with open(CHAMPIONS_DIR / f"top_{metric}_info.json", "w") as f:
                            json.dump(m, f, indent=4)

            except Exception as e:
                print(f"   ⚠️ Metrics error: {e}")

            state["last_index"] = i
            save_state(state)
            pd.DataFrame(state["results"]).to_csv(SUMMARY_CSV, index=False)

    except KeyboardInterrupt:
        print("\n🛑 Sweep paused. Run again to resume.")
        sys.exit(0)

    print("\n" + "="*60)
    print("🏆 DEEP BNN SWEEP COMPLETE 🏆")
    print("="*60)
    for metric, data in state["champions"].items():
        print(f"Best {metric.upper():<10}: {data['score']:.4f} ({data['id']})")

if __name__ == "__main__":
    main()