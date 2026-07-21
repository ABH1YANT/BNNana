"""
export_model.py
Full Export Pipeline: PyTorch -> [Artifacts] & [STM32 Project Folders]
Targeting: run_33_L3_Arch16-16-16_Adam_LR0.001.pth
"""

import torch
import torch.nn as nn
import joblib
import json
import numpy as np
import math
import shutil
from pathlib import Path
from datetime import datetime
import sys

# --- Path Configuration ---
ROOT = Path(r"C:\Users\a\Desktop\BNNana")
sys.path.insert(0, str(ROOT))

# STM32 Project Paths
MCU_INC_DIR = ROOT / "mcu" / "BNNana_inference" / "Core" / "Inc"
MCU_SRC_DIR = ROOT / "mcu" / "BNNana_inference" / "Core" / "Src"

from ml.config import cfg
from ml.model import BWNClassifier
from ml.layers import BinaryLinear

# Ensure MCU directories exist
MCU_INC_DIR.mkdir(parents=True, exist_ok=True)
MCU_SRC_DIR.mkdir(parents=True, exist_ok=True)

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
# 2. Parameter Extraction (Bias Fusion)
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
            lin_bias = current_linear.bias.detach().numpy() if current_linear.bias is not None else 0
            
            A = gamma / np.sqrt(var + eps)
            B = A * (lin_bias - mu) + beta
            
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

    # --- 1. GENERATE bnn_types.h ---
    with open(cfg.ARTIFACT_DIR / "selected_features.json", "r") as fj:
        features = json.load(fj)
    
    content_types = f"// Generated: {timestamp}\n#ifndef BNN_TYPES_H\n#define BNN_TYPES_H\n\n#include <stdint.h>\n\ntypedef struct {{\n"
    for feat in features:
        clean_name = feat.lower().replace(" ", "_").replace("-", "_").replace("/", "_").replace(".", "_")
        content_types += f"    float {clean_name};\n"
    content_types += f"}} FlowFeatures;\n\ntypedef union {{\n    FlowFeatures named;\n    float array[{len(features)}];\n}} BNN_Input;\n\n#endif"
    
    with open(cfg.ARTIFACT_DIR / "bnn_types.h", "w") as f: f.write(content_types)
    with open(MCU_INC_DIR / "bnn_types.h", "w") as f: f.write(content_types)

    # --- 2. GENERATE weights.h / weights.c ---
    # Header
    content_wh = f"// Generated from: {TARGET_MODEL_PATH.name}\n#ifndef BNN_WEIGHTS_H\n#define BNN_WEIGHTS_H\n#include <stdint.h>\n\n"
    content_wh += f"#define NUM_HIDDEN_LAYERS {len(cfg.HIDDEN_LAYERS)}\n#define INPUT_SIZE {cfg.INPUT_SIZE}\n"
    for i, h_size in enumerate(cfg.HIDDEN_LAYERS):
        content_wh += f"#define L{i}_SIZE {h_size}\n"
    content_wh += "\n"
    for i, h_size in enumerate(cfg.HIDDEN_LAYERS):
        in_s = cfg.INPUT_SIZE if i == 0 else cfg.HIDDEN_LAYERS[i-1]
        content_wh += f"extern const int8_t L{i}_WEIGHTS[{h_size}][{in_s}];\nextern const int16_t L{i}_A[{h_size}];\nextern const int16_t L{i}_B[{h_size}];\n\n"
    content_wh += f"extern const int8_t OUT_WEIGHTS[1][{cfg.HIDDEN_LAYERS[-1]}];\nextern const int16_t OUT_BIAS;\n#endif"
    
    with open(cfg.ARTIFACT_DIR / "weights.h", "w") as f: f.write(content_wh)
    with open(MCU_INC_DIR / "weights.h", "w") as f: f.write(content_wh)

    # Source
    content_wc = f'#include "weights.h"\n\n'
    for i, layer in enumerate(params[:-1]):
        w_bin = torch.sign(layer['weights']).numpy().astype(int)
        h_size, in_s = w_bin.shape
        rows = [ "{" + ", ".join(map(str, row)) + "}" for row in w_bin ]
        content_wc += f"const int8_t L{i}_WEIGHTS[{h_size}][{in_s}] = {{\n    " + ",\n    ".join(rows) + "\n};\n"
        content_wc += f"const int16_t L{i}_A[{h_size}] = {{ {', '.join([str(to_fixed_point(x)) for x in layer['A']])} }};\n"
        content_wc += f"const int16_t L{i}_B[{h_size}] = {{ {', '.join([str(to_fixed_point(x)) for x in layer['B']])} }};\n\n"
    
    o_w_bin = torch.sign(params[-1]['weights']).numpy().astype(int)
    content_wc += f"const int8_t OUT_WEIGHTS[1][{o_w_bin.shape[1]}] = {{ {{ {', '.join(map(str, o_w_bin.flatten()))} }} }};\n"
    content_wc += f"const int16_t OUT_BIAS = {to_fixed_point(params[-1]['bias'])};\n"
    
    with open(cfg.ARTIFACT_DIR / "weights.c", "w") as f: f.write(content_wc)
    with open(MCU_SRC_DIR / "weights.c", "w") as f: f.write(content_wc)

    # --- 3. GENERATE scaler.h / scaler.c ---
    content_sh = f"#ifndef SCALER_H\n#define SCALER_H\n#define BNN_INPUTS {cfg.INPUT_SIZE}\nextern const float SCALER_OFFSET[BNN_INPUTS];\nextern const float SCALER_SCALE[BNN_INPUTS];\n#endif"
    with open(cfg.ARTIFACT_DIR / "scaler.h", "w") as f: f.write(content_sh)
    with open(MCU_INC_DIR / "scaler.h", "w") as f: f.write(content_sh)

    content_sc = f'#include "scaler.h"\nconst float SCALER_OFFSET[{cfg.INPUT_SIZE}] = {{ {", ".join(map(str, scaler.min_))} }};\n'
    content_sc += f'const float SCALER_SCALE[{cfg.INPUT_SIZE}] = {{ {", ".join(map(str, scaler.scale_))} }};\n'
    with open(cfg.ARTIFACT_DIR / "scaler.c", "w") as f: f.write(content_sc)
    with open(MCU_SRC_DIR / "scaler.c", "w") as f: f.write(content_sc)

    # --- 4. GENERATE feature_order.h ---
    content_fo = "#ifndef FEATURE_ORDER_H\n#define FEATURE_ORDER_H\ntypedef enum {\n"
    for feat in features: content_fo += f"    FEAT_{clean_feature_name(feat)},\n"
    content_fo += f"    NUM_FEATURES = {len(features)}\n}} FeatureIndex;\n#endif"
    with open(cfg.ARTIFACT_DIR / "feature_order.h", "w") as f: f.write(content_fo)
    with open(MCU_INC_DIR / "feature_order.h", "w") as f: f.write(content_fo)

    # --- 5. FPGA EXPORT (.mem) ---
    for i, layer in enumerate(params):
        prefix = f"layer{i}" if layer['type'] == "hidden" else "output"
        with open(cfg.ARTIFACT_DIR / f"{prefix}_weights.mem", "w") as f:
            f.write("\n".join(pack_weights_to_hex(layer['weights'])))
        if layer['type'] == "hidden":
            with open(cfg.ARTIFACT_DIR / f"{prefix}_affine.mem", "w") as f:
                for a, b in zip(layer['A'], layer['B']):
                    f.write(f"{to_fixed_point_hex(a)}{to_fixed_point_hex(b)}\n")
        else:
            with open(cfg.ARTIFACT_DIR / "output_bias.mem", "w") as f:
                f.write(to_fixed_point_hex(layer['bias']) + "\n")

    print(f"Success! Artifacts deployed to:\n - {cfg.ARTIFACT_DIR}\n - {MCU_INC_DIR}\n - {MCU_SRC_DIR}")

if __name__ == "__main__":
    main()