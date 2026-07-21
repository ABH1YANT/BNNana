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
    """Converts float to Q8.8 fixed-point with saturation."""
    ival = int(round(value * (1 << fraction_bits)))
    return max(-32768, min(32767, ival))

def to_fixed_point_hex(value, fraction_bits=8):
    """Converts float to 16-bit Q8.8 hex string (two's complement)."""
    ival = to_fixed_point(value, fraction_bits)
    if ival < 0:
        ival = (1 << 16) + ival
    return f"{ival & 0xFFFF:04x}"

def clean_feature_name(name):
    """Cleans feature names for C Enum compatibility."""
    return (name.upper().replace(" ", "_").replace("-", "_")
            .replace("/", "_").replace(".", "_").replace("(", "")
            .replace(")", "").strip("_"))

def pack_weights_to_hex(tensor):
    """Packs binary weights into hex strings for FPGA."""
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
    """Dynamically extracts weights and fused BN params from the modular model."""
    layers_data = []
    
    # 1. Extract from hidden_stack
    current_linear = None
    for module in model.hidden_stack:
        if isinstance(module, BinaryLinear):
            current_linear = module
        elif isinstance(module, nn.BatchNorm1d):
            # Fuse BatchNorm: y = Ax + B
            mu = module.running_mean.detach().numpy()
            var = module.running_var.detach().numpy()
            gamma = module.weight.detach().numpy()
            beta = module.bias.detach().numpy()
            eps = module.eps
            
            A = gamma / np.sqrt(var + eps)
            B = beta - (mu * A)
            
            layers_data.append({
                "type": "hidden",
                "weights": current_linear.weight.detach(),
                "A": A,
                "B": B
            })
            current_linear = None

    # 2. Extract from output_layer
    o_w = model.output_layer.weight.detach()
    o_b = model.output_layer.bias.detach().numpy()[0] if model.output_layer.bias is not None else 0.0
    
    layers_data.append({
        "type": "output",
        "weights": o_w,
        "bias": o_b
    })
    
    return layers_data

# ------------------------------------------------------------
# 3. Main Export Logic
# ------------------------------------------------------------

def main():
    # --- TARGET MODEL PATH ---
    TARGET_MODEL_PATH = ROOT / "models" / "all_runs" / "run_33_L3_Arch16-16-16_Adam_LR0.001.pth"
    
    if not TARGET_MODEL_PATH.exists():
        print(f"Error: Could not find model at {TARGET_MODEL_PATH}")
        return

    print(f"Exporting Specific Model: {TARGET_MODEL_PATH.name}")
    print(f"Architecture defined in config: {cfg.HIDDEN_LAYERS}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load Model
    model = BWNClassifier()
    try:
        model.load_state_dict(torch.load(TARGET_MODEL_PATH, map_location='cpu'))
    except Exception as e:
        print(f"Architecture Mismatch Error: {e}")
        print("Ensure cfg.HIDDEN_LAYERS in ml/config.py matches the model weights.")
        return
        
    model.eval()

    # Load Scaler
    scaler = joblib.load(cfg.SCALER_PATH)
    params = extract_parameters(model)

    # --- MCU EXPORT (weights.h / weights.c) ---
    print("Generating MCU Weight Files...")
    
    with open(cfg.ARTIFACT_DIR / "weights.h", "w") as f:
        f.write(f"// Generated from: {TARGET_MODEL_PATH.name}\n")
        f.write(f"// Export Date: {timestamp}\n#ifndef BNN_WEIGHTS_H\n#define BNN_WEIGHTS_H\n\n#include <stdint.h>\n\n")
        f.write(f"#define NUM_HIDDEN_LAYERS {len(cfg.HIDDEN_LAYERS)}\n")
        f.write(f"#define INPUT_SIZE {cfg.INPUT_SIZE}\n\n")
        
        for i, h_size in enumerate(cfg.HIDDEN_LAYERS):
            in_s = cfg.INPUT_SIZE if i == 0 else cfg.HIDDEN_LAYERS[i-1]
            f.write(f"// Layer {i} constants\n")
            f.write(f"extern const int8_t L{i}_WEIGHTS[{h_size}][{in_s}];\n")
            f.write(f"extern const int16_t L{i}_A[{h_size}];\n")
            f.write(f"extern const int16_t L{i}_B[{h_size}];\n\n")
            
        f.write(f"// Output Layer\nextern const int8_t OUT_WEIGHTS[{cfg.OUTPUT_SIZE}][{cfg.HIDDEN_LAYERS[-1]}];\n")
        f.write(f"extern const int16_t OUT_BIAS;\n\n#endif")

    with open(cfg.ARTIFACT_DIR / "weights.c", "w") as f:
        f.write('#include "weights.h"\n\n')
        
        for i, layer in enumerate(params[:-1]): # All hidden layers
            w_bin = torch.sign(layer['weights']).numpy().astype(int)
            rows = [ "{" + ", ".join(map(str, row)) + "}" for row in w_bin ]
            f.write(f"const int8_t L{i}_WEIGHTS[{w_bin.shape[0]}][{w_bin.shape[1]}] = {{\n    " + ",\n    ".join(rows) + "\n};\n")
            
            a_fix = [str(to_fixed_point(x)) for x in layer['A']]
            b_fix = [str(to_fixed_point(x)) for x in layer['B']]
            f.write(f"const int16_t L{i}_A[{len(a_fix)}] = {{ {', '.join(a_fix)} }};\n")
            f.write(f"const int16_t L{i}_B[{len(b_fix)}] = {{ {', '.join(b_fix)} }};\n\n")
            
        # Output Layer
        out_layer = params[-1]
        o_w_bin = torch.sign(out_layer['weights']).numpy().astype(int)
        o_rows = [ "{" + ", ".join(map(str, row)) + "}" for row in o_w_bin ]
        f.write(f"const int8_t OUT_WEIGHTS[1][{o_w_bin.shape[1]}] = {{ {', '.join(o_rows)} }};\n")
        f.write(f"const int16_t OUT_BIAS = {to_fixed_point(out_layer['bias'])};\n")

    # --- SCALER EXPORT (scaler.h / scaler.c) ---
    print("Generating MCU Scaler Files...")
    
    with open(cfg.ARTIFACT_DIR / "scaler.h", "w") as f:
        f.write(f"// Generated from: {TARGET_MODEL_PATH.name}\n")
        f.write(f"#ifndef SCALER_H\n#define SCALER_H\n\n")
        f.write(f"#define BNN_INPUTS {cfg.INPUT_SIZE}\n\n")
        f.write("extern const float SCALER_MIN[BNN_INPUTS];\n")
        f.write("extern const float SCALER_SCALE[BNN_INPUTS];\n\n")
        f.write("#endif")

    with open(cfg.ARTIFACT_DIR / "scaler.c", "w") as f:
        f.write('#include "scaler.h"\n\n')
        f.write(f"const float SCALER_MIN[BNN_INPUTS] = {{ {', '.join(map(str, scaler.min_))} }};\n\n")
        f.write(f"const float SCALER_SCALE[BNN_INPUTS] = {{ {', '.join(map(str, scaler.scale_))} }};\n")

    # --- FEATURE ORDER EXPORT ---
    with open(cfg.ARTIFACT_DIR / "selected_features.json", "r") as fj:
        features = json.load(fj)
    with open(cfg.ARTIFACT_DIR / "feature_order.h", "w") as f:
        f.write("#ifndef FEATURE_ORDER_H\n#define FEATURE_ORDER_H\n\ntypedef enum {\n")
        for feat in features:
            f.write(f"    FEAT_{clean_feature_name(feat)},\n")
        f.write(f"    NUM_FEATURES = {len(features)}\n}} FeatureIndex;\n\n#endif")

    # --- FPGA EXPORT (.mem) ---
    print("Generating FPGA .mem Files...")
    for i, layer in enumerate(params):
        prefix = f"layer{i}" if layer['type'] == "hidden" else "output"
        
        # Weights
        with open(cfg.ARTIFACT_DIR / f"{prefix}_weights.mem", "w") as f:
            f.write("\n".join(pack_weights_to_hex(layer['weights'])))
        
        # Affine (A and B packed into one 32-bit line for FPGA DSPs)
        if layer['type'] == "hidden":
            with open(cfg.ARTIFACT_DIR / f"{prefix}_affine.mem", "w") as f:
                for a, b in zip(layer['A'], layer['B']):
                    f.write(f"{to_fixed_point_hex(a)}{to_fixed_point_hex(b)}\n")
        else:
            with open(cfg.ARTIFACT_DIR / "output_bias.mem", "w") as f:
                f.write(to_fixed_point_hex(layer['bias']) + "\n")

    print(f"\nSuccess! Artifacts for {TARGET_MODEL_PATH.name} exported to {cfg.ARTIFACT_DIR}")

if __name__ == "__main__":
    main()