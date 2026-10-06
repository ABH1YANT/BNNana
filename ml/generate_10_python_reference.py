"""
generate_10_python_reference.py

Generate exact Python BNN reference checkpoints for the FIRST 10
rows of scaled_dataset.csv.

IMPORTANT:
- Uses the EXACT BNNClassifier from the training code.
- Uses the trained checkpoint; NO retraining.
- Uses scaled_dataset.csv exactly as trainer.py does.
- Does NOT manually recreate the BNN.
- Captures internal model checkpoints for RTL comparison.

Outputs:
    artifacts/debug_10_python_reference.json
    artifacts/debug_10_python_predictions.mem
    artifacts/debug_10_labels.mem
"""

import sys
import json
from pathlib import Path

import torch
import pandas as pd
import numpy as np


# ==============================================================
# 1. PROJECT PATH
# ==============================================================

# This script is expected to be in:
# C:\Users\DELL\Desktop\BNNana\scripts\

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent

# Allow Python to find the "bnn" package.
sys.path.insert(0, str(ROOT))


# ==============================================================
# 2. IMPORT THE EXACT TRAINING MODEL
# ==============================================================

# trainer.py uses:
#     from .config import cfg
#     from .model import BNNClassifier
#
# Therefore model.py must be imported as part of the bnn package.

from ml.model import BNNClassifier
from ml.config import cfg


# ==============================================================
# 3. PATHS
# ==============================================================

DATA_PATH = cfg.DATA_DIR / "scaled_dataset.csv"
FEATURE_PATH = cfg.ARTIFACT_DIR / "selected_features.json"
MODEL_PATH = cfg.MODEL_SAVE_PATH

OUTPUT_JSON = cfg.ARTIFACT_DIR / "debug_10_python_reference.json"
OUTPUT_PRED = cfg.ARTIFACT_DIR / "debug_10_python_predictions.mem"
OUTPUT_LABELS = cfg.ARTIFACT_DIR / "debug_10_labels.mem"


# ==============================================================
# 4. EXACT NUMBER OF DEBUG SAMPLES
# ==============================================================

NUM_SAMPLES = 10


# ==============================================================
# 5. HELPER
# ==============================================================

def tensor_to_list(x):
    """
    Convert a PyTorch tensor to a normal Python list.

    Keeps floating-point values as Python floats and integer
    tensors as Python integers.
    """
    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy().tolist()

    return x


# ==============================================================
# 6. LOAD FEATURE ORDER
# ==============================================================

print("=" * 70)
print("PYTHON BNN REFERENCE GENERATOR")
print("=" * 70)

print(f"Project root : {ROOT}")
print(f"Dataset      : {DATA_PATH}")
print(f"Checkpoint   : {MODEL_PATH}")
print(f"Features     : {FEATURE_PATH}")
print()


if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"scaled_dataset.csv not found:\n{DATA_PATH}"
    )

if not FEATURE_PATH.exists():
    raise FileNotFoundError(
        f"selected_features.json not found:\n{FEATURE_PATH}"
    )

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"BNN checkpoint not found:\n{MODEL_PATH}"
    )


with open(FEATURE_PATH, "r") as f:
    features = json.load(f)


print("Selected feature order:")
for i, feature in enumerate(features):
    print(f"  {i:2d}: {feature}")

print()


# ==============================================================
# 7. LOAD FIRST 10 ROWS
# ==============================================================

df = pd.read_csv(DATA_PATH)

missing_features = [
    feature for feature in features
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        "The following selected features are missing from "
        "scaled_dataset.csv:\n"
        + "\n".join(missing_features)
    )

if "Label" not in df.columns:
    raise ValueError("Label column not found in scaled_dataset.csv")


debug_df = df.iloc[:NUM_SAMPLES].copy()

X = debug_df[features].values.astype(np.float32)
y = debug_df["Label"].values.astype(np.float32)

print(f"Loaded {len(debug_df)} samples.")
print(f"Input shape: {X.shape}")
print()


# ==============================================================
# 8. CREATE EXACT TRAINING MODEL
# ==============================================================

print("Creating BNNClassifier...")

model = BNNClassifier().to(cfg.DEVICE)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=cfg.DEVICE
)

model.load_state_dict(checkpoint)

# VERY IMPORTANT:
# trainer.py uses model.eval() for validation/test.
#
# This makes BatchNorm use its trained running statistics,
# which is what we want for FPGA inference comparison.

model.eval()

print("Checkpoint loaded successfully.")
print(f"Device: {cfg.DEVICE}")
print()


# ==============================================================
# 9. CHECK MODEL STRUCTURE
# ==============================================================

print("Model:")
print(model)
print()


# ==============================================================
# 10. CHECKPOINT STORAGE
# ==============================================================

checkpoints = {}


def save_hook(name):
    """
    Create a forward hook that stores the module output.
    """

    def hook(module, inputs, output):
        checkpoints[name] = tensor_to_list(output)

    return hook


# ==============================================================
# 11. REGISTER HOOKS
# ==============================================================

# --------------------------------------------------------------
# Input quantizer
# --------------------------------------------------------------

model.input_quantizer.register_forward_hook(
    save_hook("input_quantizer")
)


# --------------------------------------------------------------
# Layer 0
# --------------------------------------------------------------

model.layers[0].linear.register_forward_hook(
    save_hook("layer0_linear")
)

model.layers[0].bn.register_forward_hook(
    save_hook("layer0_bn")
)

model.layers[0].activation.register_forward_hook(
    save_hook("layer0_binary")
)


# --------------------------------------------------------------
# Layer 1
# --------------------------------------------------------------

model.layers[1].linear.register_forward_hook(
    save_hook("layer1_linear")
)

model.layers[1].bn.register_forward_hook(
    save_hook("layer1_bn")
)

model.layers[1].activation.register_forward_hook(
    save_hook("layer1_binary")
)


# --------------------------------------------------------------
# Layer 2
# --------------------------------------------------------------

model.layers[2].linear.register_forward_hook(
    save_hook("layer2_linear")
)

model.layers[2].bn.register_forward_hook(
    save_hook("layer2_bn")
)

model.layers[2].activation.register_forward_hook(
    save_hook("layer2_binary")
)


# --------------------------------------------------------------
# Output layer
# --------------------------------------------------------------

model.output_layer.register_forward_hook(
    save_hook("output_linear")
)


# ==============================================================
# 12. RUN EXACT MODEL
# ==============================================================

print("Running exact BNN on first 10 samples...")
print()

input_tensor = torch.tensor(
    X,
    dtype=torch.float32,
    device=cfg.DEVICE
)

with torch.no_grad():
    logits = model(input_tensor)


logits_np = logits.detach().cpu().numpy()

# trainer.py uses:
#
#     torch.sigmoid(outputs) > 0.5
#
# This is mathematically equivalent to:
#
#     outputs > 0
#
predictions = (logits_np > 0).astype(np.int32)

labels = y.astype(np.int32)


# ==============================================================
# 13. PRINT RESULTS
# ==============================================================

print("=" * 70)
print("PYTHON RESULTS")
print("=" * 70)

correct = 0

for i in range(NUM_SAMPLES):

    is_correct = predictions[i] == labels[i]

    if is_correct:
        correct += 1

    print(
        f"Sample {i:2d} | "
        f"Logit = {logits_np[i]: .8f} | "
        f"Prediction = {predictions[i]} | "
        f"Label = {labels[i]} | "
        f"{'MATCH' if is_correct else 'MISMATCH'}"
    )

print()

print(
    f"Python accuracy on first {NUM_SAMPLES}: "
    f"{correct}/{NUM_SAMPLES} = "
    f"{100.0 * correct / NUM_SAMPLES:.2f}%"
)

print()


# ==============================================================
# 14. DISPLAY CHECKPOINT SHAPES
# ==============================================================

print("=" * 70)
print("CHECKPOINT SHAPES")
print("=" * 70)

for name, value in checkpoints.items():

    arr = np.asarray(value)

    print(
        f"{name:20s}: "
        f"shape={arr.shape}"
    )

print()


# ==============================================================
# 15. CONVERT CHECKPOINTS TO DEBUG-FRIENDLY FORMAT
# ==============================================================

reference = {
    "metadata": {
        "num_samples": NUM_SAMPLES,
        "dataset": str(DATA_PATH),
        "checkpoint": str(MODEL_PATH),
        "device": str(cfg.DEVICE),
        "input_features": features,
        "hidden_layers": cfg.HIDDEN_LAYERS,
        "use_residuals": cfg.USE_RESIDUALS,
        "activation": cfg.ACTIVATION_TYPE,
        "simulate_fixed_point": cfg.SIMULATE_FIXED_POINT,
        "fractional_bits": cfg.FRACTIONAL_BITS,
    },

    "inputs": X.tolist(),

    "labels": labels.tolist(),

    "predictions": predictions.tolist(),

    "logits": logits_np.tolist(),

    "checkpoints": checkpoints,
}


# ==============================================================
# 16. SAVE JSON
# ==============================================================

with open(OUTPUT_JSON, "w") as f:
    json.dump(
        reference,
        f,
        indent=2
    )

print(f"Saved Python reference:")
print(f"  {OUTPUT_JSON}")


# ==============================================================
# 17. SAVE PREDICTIONS FOR VERILOG
# ==============================================================

with open(OUTPUT_PRED, "w") as f:

    for prediction in predictions:
        f.write(f"{int(prediction)}\n")


print(f"Saved predictions:")
print(f"  {OUTPUT_PRED}")


# ==============================================================
# 18. SAVE LABELS FOR VERILOG
# ==============================================================

with open(OUTPUT_LABELS, "w") as f:

    for label in labels:
        f.write(f"{int(label)}\n")


print(f"Saved labels:")
print(f"  {OUTPUT_LABELS}")


# ==============================================================
# 19. PRINT IMPORTANT CHECKPOINTS
# ==============================================================

print()
print("=" * 70)
print("IMPORTANT CHECKPOINTS")
print("=" * 70)


# Input after Q1.8 quantization
if "input_quantizer" in checkpoints:

    q = np.asarray(checkpoints["input_quantizer"])

    print("\nINPUT QUANTIZER")
    for sample in range(NUM_SAMPLES):
        print(
            f"Sample {sample}: "
            + " ".join(
                f"{v:.6f}" for v in q[sample]
            )
        )


# Layer 0 binary output
if "layer0_binary" in checkpoints:

    b0 = np.asarray(checkpoints["layer0_binary"])

    print("\nLAYER 0 BINARY OUTPUT")
    for sample in range(NUM_SAMPLES):
        bits = "".join(
            "1" if v > 0 else "0"
            for v in b0[sample]
        )

        print(
            f"Sample {sample}: "
            f"{bits}"
        )


# Layer 1 binary output
if "layer1_binary" in checkpoints:

    b1 = np.asarray(checkpoints["layer1_binary"])

    print("\nLAYER 1 BINARY OUTPUT")
    for sample in range(NUM_SAMPLES):
        bits = "".join(
            "1" if v > 0 else "0"
            for v in b1[sample]
        )

        print(
            f"Sample {sample}: "
            f"{bits}"
        )


# Layer 2 binary output
if "layer2_binary" in checkpoints:

    b2 = np.asarray(checkpoints["layer2_binary"])

    print("\nLAYER 2 BINARY OUTPUT")
    for sample in range(NUM_SAMPLES):
        bits = "".join(
            "1" if v > 0 else "0"
            for v in b2[sample]
        )

        print(
            f"Sample {sample}: "
            f"{bits}"
        )


print()
print("=" * 70)
print("DONE")
print("=" * 70)