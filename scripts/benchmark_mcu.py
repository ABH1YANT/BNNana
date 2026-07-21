import pandas as pd
import numpy as np
import joblib
import json
import time
from pathlib import Path
from tqdm import tqdm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from uart_bridge import UARTBridge

# --- Configuration ---
ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
DATASETS_DIR = ROOT / "datasets" / "processed"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

PORT = "COM4"
FEATURES_PATH = ARTIFACTS_DIR / "selected_features.json"

CSV_FILES = [
    DATASETS_DIR / "BENIGN.csv",
    DATASETS_DIR / "DNS.csv",
    DATASETS_DIR / "SYN.csv",
    DATASETS_DIR / "UDP.csv"
]

SAMPLES_PER_FILE = 2500 
WARMUP_SAMPLES = 10 

def load_and_clean_data(features):
    all_chunks = []
    for file_path in CSV_FILES:
        if not file_path.exists():
            print(f"Warning: {file_path} not found. Skipping.")
            continue
            
        print(f"Reading {file_path.name}...")
        # Read slightly more to account for dropped NaNs
        df = pd.read_csv(file_path, low_memory=False, nrows=SAMPLES_PER_FILE * 2)
        df.columns = df.columns.str.strip()
        
        if 'Label' not in df.columns:
            print(f"Warning: 'Label' column missing in {file_path.name}")
            continue
        
        # Vectorized Label Cleaning
        labels = df['Label'].astype(str).str.strip().str.upper()
        df['BinaryLabel'] = (labels != "BENIGN").astype(np.uint8)
        
        # 1. Filter columns and 2. FORCE ORDER to match selected_features.json
        # This is critical because the MCU expects a specific struct layout
        df = df[features + ['BinaryLabel']]
        
        # Handle non-finite values
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Sample the requested amount
        if len(df) > SAMPLES_PER_FILE:
            df = df.sample(n=SAMPLES_PER_FILE, random_state=42)
        
        all_chunks.append(df)
    
    if not all_chunks:
        raise FileNotFoundError("No valid datasets found to load.")

    combined = pd.concat(all_chunks, ignore_index=True)
    return combined[features], combined['BinaryLabel']

def main():
    # 1. Load Feature Definitions
    print(f"Loading feature definitions from {FEATURES_PATH}...")
    try:
        with open(FEATURES_PATH, "r") as f:
            selected_features = json.load(f)
        print(f"Model expects {len(selected_features)} features.")
    except Exception as e:
        print(f"Error loading features: {e}")
        return

    # 2. Load Raw Data
    # We send RAW data because the MCU now handles scaling internally
    X_raw, y_true = load_and_clean_data(selected_features)
    
    # Ensure data is float32 (4 bytes) for the MCU
    X_raw = X_raw.astype(np.float32)

    # 3. Connect to MCU
    try:
        bridge = UARTBridge(PORT)
        print(f"Connected to STM32 on {PORT}")
    except Exception as e:
        print(f"UART Connection Error: {e}")
        return

    results = []
    true_labels = []
    latencies = []
    cycles = []
    
    total_attempts = len(X_raw)
    print(f"Starting Benchmark ({total_attempts} samples + {WARMUP_SAMPLES} warmup)...")
    
    host_start_time = time.perf_counter()

    # 4. Benchmark Loop
    try:
        for i in tqdm(range(total_attempts)):
            # iloc[i] preserves the column order from selected_features
            sample = X_raw.iloc[i].tolist()
            
            # Safety check: Ensure packet size matches Protocol expectation (17 floats)
            if len(sample) != 17:
                print(f"Error: Sample {i} has {len(sample)} features, but Protocol expects 17.")
                break

            # Send to MCU
            response = bridge.exchange(sample)
            
            if response is not None:
                # Discard warmup samples from metrics
                if i >= WARMUP_SAMPLES:
                    results.append(response['prediction'])
                    true_labels.append(y_true.iloc[i])
                    latencies.append(response['latency_us'])
                    cycles.append(response['cycles'])
            else:
                # If UART fails, we don't append to true_labels, keeping them aligned
                pass

    finally:
        bridge.close()
        host_end_time = time.perf_counter()

    # 5. Compute Metrics
    if not results:
        print("Error: No data collected from MCU. Check UART wiring and Baud Rate.")
        return

    acc = accuracy_score(true_labels, results)
    prec = precision_score(true_labels, results, zero_division=0)
    rec = recall_score(true_labels, results, zero_division=0)
    f1 = f1_score(true_labels, results, zero_division=0)
    cm = confusion_matrix(true_labels, results)

    avg_lat = np.mean(latencies)
    avg_cyc = np.mean(cycles)
    throughput = 1_000_000 / avg_lat if avg_lat > 0 else 0
    
    expected_count = total_attempts - WARMUP_SAMPLES
    success_rate = len(results) / expected_count

    # 6. Final Report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "samples_attempted": expected_count,
        "samples_successful": len(results),
        "success_rate": success_rate,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "avg_latency_us": avg_lat,
        "avg_cycles": int(avg_cyc),
        "throughput_fps": throughput,
        "host_total_time_s": host_end_time - host_start_time
    }

    print("\n" + "="*40)
    print("      STM32 BNN BENCHMARK REPORT")
    print("="*40)
    print(f"UART Success    : {success_rate:.2%} ({len(results)}/{expected_count})")
    print(f"Accuracy        : {acc:.2%}")
    print(f"Precision       : {prec:.2%}")
    print(f"Recall          : {rec:.2%}")
    print(f"F1-Score        : {f1:.2%}")
    print("-" * 40)
    print(f"Avg Latency     : {avg_lat/1000:.3f} ms")
    print(f"Avg Cycles      : {int(avg_cyc):,}")
    print(f"Throughput      : {int(throughput)} samples/s")
    print(f"Host Total Time : {report['host_total_time_s']:.2f} s")
    print("-" * 40)
    print("Confusion Matrix:")
    print(cm)
    print("="*40)

    # Save to JSON
    report_file = REPORTS_DIR / "mcu_benchmark_results.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to {report_file}")

if __name__ == "__main__":
    main()