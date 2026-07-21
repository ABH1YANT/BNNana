"""
export_model.py
Full Export Pipeline: PyTorch -> [MCU (Fixed-Point C)] & [FPGA (Verilog .mem)]
Targeting: run_33_L3_Arch16-16-16_Adam_LR0.001.pth
"""

import torch
import torch.nn as nn
import joblib
import json
import numpy as np
import math
from pathlib import Path
from datetime import datetime
import sys

# Setup Pathing
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
sys.path.insert(0, str(ROOT))

from ml.config import cfg
from ml.model import BWNClassifier
from ml.layers import BinaryLinear

# ------------------------------------------------------------
# 1. Utility Functions
# ------------------------------------------------------------

def to_fixed_point(value, fraction_bits=8):
    ival = int(round(value * (1 << fraction_bits)))
    return max(-32768, min(32767, ival))

def to_fixed_point_hex(value, fraction_bits=8):
    ival = to_fixed_point(value, fraction_bits)
    if ival < 0:
        ival = (1 << 16) + ival
    return f"{ival & 0xFFFF:04x}"

def clean_feature_name(name):
    return (name.upper().replace(" ", "_").replace("-", "_")
            .replace("/", "_").replace(".", "_").replace("(", "")
            .replace(")", "").strip("_"))

def pack_weights_to_hex(tensor):
    weights = torch.sign(tensor).cpu().detach().numpy()
    hex_rows = []
    bit_width = weights.shape[1]
    hex_width = math.ceil(bit_width / 4)
    for row in weights:
        bits = "".join(['1' if x > 0 else '0' for x in row])
        hex_val = hex(int(bits, 2))[2:].zfill(hex_width)
        hex_rows.append(hex_val)
    return hex_rows

# ------------------------------------------------------------
# 2. Parameter Extraction Logic
# ------------------------------------------------------------

def extract_parameters(model):
    layers_data = []
    current_linear = None
    for module in model.hidden_stack:
        if isinstance(module, BinaryLinear):
            current_linear = module
        elif isinstance(module, nn.BatchNorm1d):
            mu = module.running_mean.detach().numpy()
            var = module.running_var.detach().numpy()
            gamma = module.weight.detach().numpy()
            beta = module.bias.detach().numpy()
            eps = module.eps
            A = gamma / np.sqrt(var + eps)
            B = beta - (mu * A)
            layers_data.append({"type": "hidden", "weights": current_linear.weight.detach(), "A": A, "B": B})
            current_linear = None

    o_w = model.output_layer.weight.detach()
    o_b = model.output_layer.bias.detach().numpy()[0] if model.output_layer.bias is not None else 0.0
    layers_data.append({"type": "output", "weights": o_w, "bias": o_b})
    return layers_data

# ------------------------------------------------------------
# 3. Main Export Logic
# ------------------------------------------------------------

def main():
    TARGET_MODEL_PATH = ROOT / "models" / "all_runs" / "run_33_L3_Arch16-16-16_Adam_LR0.001.pth"
    
    if not TARGET_MODEL_PATH.exists():
        print(f"Error: {TARGET_MODEL_PATH} not found.")
        return

    print(f"Exporting: {TARGET_MODEL_PATH.name}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    model = BWNClassifier()
    model.load_state_dict(torch.load(TARGET_MODEL_PATH, map_location='cpu'))
    model.eval()

    scaler = joblib.load(cfg.SCALER_PATH)
    params = extract_parameters(model)

    # --- GENERATE bnn_types.h (CRITICAL FOR STRUCT ORDER) ---
    with open(cfg.ARTIFACT_DIR / "selected_features.json", "r") as fj:
        features = json.load(fj)
    
    with open(cfg.ARTIFACT_DIR / "bnn_types.h", "w") as f:
        f.write(f"// Generated: {timestamp}\n#ifndef BNN_TYPES_H\n#define BNN_TYPES_H\n\n#include <stdint.h>\n\n")
        f.write("typedef struct {\n")
        for feat in features:
            clean_name = feat.lower().replace(" ", "_").replace("-", "_").replace("/", "_").replace(".", "_")
            f.write(f"    float {clean_name};\n")
        f.write("} FlowFeatures;\n\ntypedef union {\n    FlowFeatures named;\n")
        f.write(f"    float array[{len(features)}];\n}} BNN_Input;\n\n#endif")

    # --- MCU EXPORT (weights.h / weights.c) ---
    with open(cfg.ARTIFACT_DIR / "weights.h", "w") as f:
        f.write(f"#ifndef BNN_WEIGHTS_H\n#define BNN_WEIGHTS_H\n#include <stdint.h>\n")
        f.write(f"#define NUM_HIDDEN_LAYERS {len(cfg.HIDDEN_LAYERS)}\n#define INPUT_SIZE {cfg.INPUT_SIZE}\n")
        for i, h_size in enumerate(cfg.HIDDEN_LAYERS):
            in_s = cfg.INPUT_SIZE if i == 0 else cfg.HIDDEN_LAYERS[i-1]
            f.write(f"extern const int8_t L{i}_WEIGHTS[{h_size}][{in_s}];\nextern const int16_t L{i}_A[{h_size}];\nextern const int16_t L{i}_B[{h_size}];\n")
        f.write(f"extern const int8_t OUT_WEIGHTS[1][{cfg.HIDDEN_LAYERS[-1]}];\nextern const int16_t OUT_BIAS;\n#endif")

    with open(cfg.ARTIFACT_DIR / "weights.c", "w") as f:
        f.write('#include "weights.h"\n')
        for i, layer in enumerate(params[:-1]):
            w_bin = torch.sign(layer['weights']).numpy().astype(int)
            rows = [ "{" + ", ".join(map(str, row)) + "}" for row in w_bin ]
            f.write(f"const int8_t L{i}_WEIGHTS[{w_bin.shape[0]}][{w_bin.shape[1]}] = {{\n    " + ",\n    ".join(rows) + "\n};\n")
            f.write(f"const int16_t L{i}_A[] = {{ {', '.join([str(to_fixed_point(x)) for x in layer['A']])} }};\n")
            f.write(f"const int16_t L{i}_B[] = {{ {', '.join([str(to_fixed_point(x)) for x in layer['B']])} }};\n")
        out_layer = params[-1]
        o_w_bin = torch.sign(out_layer['weights']).numpy().astype(int)
        f.write(f"const int8_t OUT_WEIGHTS[1][{o_w_bin.shape[1]}] = {{ {{ {', '.join(map(str, o_w_bin.flatten()))} }} }};\n")
        f.write(f"const int16_t OUT_BIAS = {to_fixed_point(out_layer['bias'])};\n")

    # --- SCALER EXPORT ---
    with open(cfg.ARTIFACT_DIR / "scaler.h", "w") as f:
        f.write(f"#ifndef SCALER_H\n#define SCALER_H\n#define BNN_INPUTS {cfg.INPUT_SIZE}\n")
        f.write("extern const float SCALER_MIN[BNN_INPUTS];\nextern const float SCALER_SCALE[BNN_INPUTS];\n#endif")
    with open(cfg.ARTIFACT_DIR / "scaler.c", "w") as f:
        f.write('#include "scaler.h"\n')
        f.write(f"const float SCALER_MIN[] = {{ {', '.join(map(str, scaler.min_))} }};\n")
        f.write(f"const float SCALER_SCALE[] = {{ {', '.join(map(str, scaler.scale_))} }};\n")

    print(f"Success! Artifacts exported to {cfg.ARTIFACT_DIR}")

if __name__ == "__main__":
    main()