"""
export_model.py

Final BNN -> FPGA Exporter

Single source of truth for features:
    artifacts/selected_features.json

Current model:
    INPUT_SIZE -> 64 -> 64 -> 32 -> 1

Dense connections:
    Layer 0: 16  -> 64
    Layer 1: 64  -> 64
    Layer 2: 128 -> 32
    Output : 160 -> 1

Hardware representation:

Layer 0:
    8-bit input
        |
        v
    signed add/subtract
        |
        v
    threshold
        |
        v
    binary output

Layer 1+:
    binary input
        |
        v
    XNOR with binary weights
        |
        v
    popcount
        |
        v
    threshold
        |
        v
    binary output

Output:
    binary input
        |
        v
    XNOR + popcount
        |
        v
    threshold = 81
        |
        v
    classification
"""

import torch
import torch.nn as nn

import json
import math
import numpy as np

from pathlib import Path
from datetime import datetime

import sys


# ============================================================
# 1. PROJECT PATH
# ============================================================

ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")

sys.path.insert(0, str(ROOT))

from ml.config import cfg
from ml.model import BNNClassifier
from ml.layers import BinaryLinear


# ============================================================
# 2. FPGA OUTPUT DIRECTORY
# ============================================================

FPGA_DIR = cfg.ARTIFACT_DIR / "fpga"

FPGA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. BASIC HELPERS
# ============================================================

def get_binary_weights(linear):
    """
    Convert BinaryLinear latent weights into the exact binary
    representation used by the model.

    PyTorch:
        weight >= 0 -> +1
        weight <  0 -> -1

    FPGA:
        +1 -> 1
        -1 -> 0
    """

    if not isinstance(linear, BinaryLinear):
        raise TypeError(
            f"Expected BinaryLinear, got {type(linear)}"
        )

    latent = (
        linear.weight
        .detach()
        .cpu()
        .numpy()
    )

    pm1 = np.where(
        latent >= 0,
        1,
        -1
    ).astype(np.int8)

    bits = np.where(
        pm1 > 0,
        1,
        0
    ).astype(np.uint8)

    return pm1, bits


def pack_weight_rows_to_hex(weight_bits):
    """
    Convert each neuron's binary weight vector into one hex word.

    Example:

        101100

    becomes:

        2c

    One line = one neuron.
    """

    weight_bits = np.asarray(weight_bits)

    if weight_bits.ndim != 2:
        raise ValueError(
            "Weight matrix must be 2-dimensional."
        )

    input_count = weight_bits.shape[1]

    hex_width = math.ceil(
        input_count / 4
    )

    result = []

    for row in weight_bits:

        bit_string = "".join(
            "1" if int(bit) else "0"
            for bit in row
        )

        value = int(
            bit_string,
            2
        )

        result.append(
            format(
                value,
                f"0{hex_width}x"
            )
        )

    return result


def write_weight_mem(path, weight_bits):
    """
    Write one packed hexadecimal weight word per neuron.
    """

    rows = pack_weight_rows_to_hex(
        weight_bits
    )

    with open(path, "w") as f:

        for row in rows:
            f.write(row + "\n")


def signed16_hex(value):
    """
    Convert signed integer to 16-bit two's complement hex.
    """

    value = int(value)

    if value < -32768 or value > 32767:
        raise ValueError(
            f"Value {value} does not fit in signed 16-bit."
        )

    if value < 0:
        value += 65536

    return f"{value:04x}"


def write_threshold_mem(path, thresholds):
    """
    Write signed 16-bit thresholds as hexadecimal.
    """

    with open(path, "w") as f:

        for threshold in thresholds:

            f.write(
                signed16_hex(threshold)
                + "\n"
            )


# ============================================================
# 4. BATCHNORM -> HARDWARE THRESHOLD
# ============================================================

def fuse_batchnorm(linear, bn):
    """
    Convert:

        BinaryLinear -> BatchNorm -> BinarySign

    into:

        effective binary weights
        +
        integer threshold

    For:

        z = sum(w*x)

        BN(z) = gamma * (z-mu)/sqrt(var+eps) + beta

    Define:

        A = gamma/sqrt(var+eps)

        B = beta - A*mu

    We need:

        A*z + B >= 0

    If A > 0:

        z >= -B/A

    If A < 0:

        -z >= -B/|A|

    Therefore when A < 0, all weights are flipped.

    Returns effective weights and floating-point threshold
    in the SAME accumulator domain as z.
    """

    original_pm1, _ = get_binary_weights(
        linear
    )

    gamma = (
        bn.weight
        .detach()
        .cpu()
        .numpy()
    )

    beta = (
        bn.bias
        .detach()
        .cpu()
        .numpy()
    )

    mean = (
        bn.running_mean
        .detach()
        .cpu()
        .numpy()
    )

    var = (
        bn.running_var
        .detach()
        .cpu()
        .numpy()
    )

    eps = bn.eps

    effective_pm1 = original_pm1.copy()

    thresholds = []

    for neuron in range(
        linear.out_features
    ):

        A = (
            gamma[neuron]
            /
            np.sqrt(
                var[neuron] + eps
            )
        )

        B = (
            beta[neuron]
            -
            A * mean[neuron]
        )

        # Extremely unlikely for normal BatchNorm,
        # but handle safely.
        if abs(A) < 1e-12:

            if B >= 0:

                # Always +1.
                threshold = -1e9

            else:

                # Always -1.
                threshold = 1e9

        else:

            if A < 0:

                # Flip the entire weight vector.
                effective_pm1[
                    neuron, :
                ] *= -1

            threshold = (
                -B / abs(A)
            )

        thresholds.append(
            float(threshold)
        )

    effective_bits = np.where(
        effective_pm1 > 0,
        1,
        0
    ).astype(np.uint8)

    return (
        effective_pm1,
        effective_bits,
        np.array(
            thresholds,
            dtype=np.float64
        )
    )


# ============================================================
# 5. HIDDEN BINARY THRESHOLD
# ============================================================

def signed_threshold_to_popcount(
    signed_threshold,
    input_count
):
    """
    Binary XNOR/popcount relation:

        signed_sum = 2*popcount - N

    We need:

        signed_sum >= T

    therefore:

        popcount >= (T + N)/2

    Return the smallest integer popcount satisfying it.
    """

    threshold = math.ceil(
        (
            signed_threshold
            +
            input_count
        ) / 2
    )

    return max(
        0,
        min(
            input_count,
            threshold
        )
    )


# ============================================================
# 6. LOAD FEATURES
# ============================================================

def load_features():
    """
    selected_features.json is the SINGLE source of truth.

    Do not hardcode feature names anywhere in this exporter.
    """

    feature_file = (
        cfg.ARTIFACT_DIR
        /
        "selected_features.json"
    )

    if not feature_file.exists():

        raise FileNotFoundError(
            f"Feature file not found:\n"
            f"{feature_file}"
        )

    with open(
        feature_file,
        "r"
    ) as f:

        features = json.load(f)

    if not isinstance(features, list):

        raise ValueError(
            "selected_features.json must contain a JSON list."
        )

    if len(features) != cfg.INPUT_SIZE:

        raise ValueError(
            "Feature count mismatch.\n"
            f"selected_features.json: {len(features)}\n"
            f"cfg.INPUT_SIZE: {cfg.INPUT_SIZE}"
        )

    return features


# ============================================================
# 7. MAIN
# ============================================================

def main():

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print("=" * 70)
    print("BNN FPGA EXPORT")
    print("=" * 70)

    # --------------------------------------------------------
    # Load feature definition
    # --------------------------------------------------------

    features = load_features()

    print()
    print("Features loaded from:")
    print(
        cfg.ARTIFACT_DIR
        /
        "selected_features.json"
    )

    print()
    print("Feature order:")

    for i, feature in enumerate(features):

        print(
            f"  [{i:02d}] {feature}"
        )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model_path = cfg.MODEL_SAVE_PATH

    print()
    print(
        f"Loading model:\n{model_path}"
    )

    if not model_path.exists():

        raise FileNotFoundError(
            f"Model not found:\n{model_path}\n\n"
            "Run train.py first."
        )

    model = BNNClassifier()

    state_dict = torch.load(
        model_path,
        map_location="cpu"
    )

    model.load_state_dict(
        state_dict
    )

    model.eval()

    # --------------------------------------------------------
    # Architecture verification
    # --------------------------------------------------------

    print()
    print("Architecture verification:")
    print(
        f"  Input: {cfg.INPUT_SIZE}"
    )
    print(
        f"  Hidden: {cfg.HIDDEN_LAYERS}"
    )
    print(
        f"  Dense: {cfg.USE_RESIDUALS}"
    )
    print(
        f"  Output: {cfg.OUTPUT_SIZE}"
    )

    expected_hidden = [64, 64, 32]

    if cfg.HIDDEN_LAYERS != expected_hidden:

        raise ValueError(
            "Expected HIDDEN_LAYERS = [64, 64, 32].\n"
            f"Found: {cfg.HIDDEN_LAYERS}"
        )

    if cfg.INPUT_SIZE != len(features):

        raise ValueError(
            "Input size and feature count disagree."
        )

    if not cfg.USE_RESIDUALS:

        raise ValueError(
            "This exporter expects dense concatenation "
            "(USE_RESIDUALS=True)."
        )

    # --------------------------------------------------------
    # Expected dimensions
    # --------------------------------------------------------

    expected_dims = [
        (16, 64),
        (64, 64),
        (128, 32),
        (160, 1)
    ]

    actual_dims = []

    for layer in model.layers:

        actual_dims.append(
            (
                layer.linear.in_features,
                layer.linear.out_features
            )
        )

    actual_dims.append(
        (
            model.output_layer.in_features,
            model.output_layer.out_features
        )
    )

    print()
    print("Layer dimensions:")

    for i, dims in enumerate(actual_dims):

        print(
            f"  Layer {i}: "
            f"{dims[0]} -> {dims[1]}"
        )

        if dims != expected_dims[i]:

            raise ValueError(
                f"Layer {i} dimension mismatch.\n"
                f"Expected: {expected_dims[i]}\n"
                f"Found:    {dims}"
            )

    # ========================================================
    # HIDDEN LAYERS
    # ========================================================

    total_weights = 0

    for layer_index, layer in enumerate(
        model.layers
    ):

        linear = layer.linear
        bn = layer.bn

        print()
        print(
            f"--- Hidden Layer {layer_index} ---"
        )

        print(
            f"Input : {linear.in_features}"
        )

        print(
            f"Output: {linear.out_features}"
        )

        # ----------------------------------------------------
        # Fuse BN
        # ----------------------------------------------------

        (
            effective_pm1,
            effective_bits,
            floating_thresholds
        ) = fuse_batchnorm(
            linear,
            bn
        )

        # ----------------------------------------------------
        # Weight file
        # ----------------------------------------------------

        weight_file = (
            FPGA_DIR
            /
            f"layer{layer_index}_weights.mem"
        )

        write_weight_mem(
            weight_file,
            effective_bits
        )

        # ----------------------------------------------------
        # Threshold
        # ----------------------------------------------------

        if layer_index == 0:

            # ------------------------------------------------
            # IMPORTANT:
            #
            # Layer 0 receives an 8-bit integer.
            #
            # PyTorch input:
            #
            #     x_q = integer / 256
            #
            # FPGA input:
            #
            #     integer
            #
            # Therefore multiply threshold by 256.
            # ------------------------------------------------

            raw_thresholds = []

            for t in floating_thresholds:

                if abs(t) > 1e8:

                    raw_thresholds.append(
                        int(
                            -32768
                            if t < 0
                            else 32767
                        )
                    )

                else:

                    raw_t = math.ceil(
                        t
                        *
                        (
                            2
                            **
                            cfg.FRACTIONAL_BITS
                        )
                    )

                    raw_thresholds.append(
                        raw_t
                    )

            threshold_file = (
                FPGA_DIR
                /
                "layer0_thresholds.mem"
            )

            write_threshold_mem(
                threshold_file,
                raw_thresholds
            )

            print(
                "Accumulator: 8-bit signed add/subtract"
            )

            print(
                "Threshold domain: raw Q1.8 integer"
            )

        else:

            # ------------------------------------------------
            # Layer 1+:
            #
            # Binary inputs
            # Binary weights
            #
            # signed_sum = 2*popcount - N
            # ------------------------------------------------

            popcount_thresholds = []

            for t in floating_thresholds:

                if abs(t) > 1e8:

                    if t < 0:

                        pc_threshold = 0

                    else:

                        pc_threshold = (
                            linear.in_features + 1
                        )

                else:

                    signed_t = math.ceil(t)

                    pc_threshold = (
                        signed_threshold_to_popcount(
                            signed_t,
                            linear.in_features
                        )
                    )

                popcount_thresholds.append(
                    pc_threshold
                )

            threshold_file = (
                FPGA_DIR
                /
                f"layer{layer_index}_thresholds.mem"
            )

            write_threshold_mem(
                threshold_file,
                popcount_thresholds
            )

            print(
                "Accumulator: XNOR + popcount"
            )

            print(
                "Threshold domain: popcount"
            )

        layer_weights = (
            linear.in_features
            *
            linear.out_features
        )

        total_weights += layer_weights

        print(
            f"Weights: {layer_weights}"
        )

        print(
            f"Generated: {weight_file.name}"
        )

        print(
            f"Generated: {threshold_file.name}"
        )

    # ========================================================
    # OUTPUT LAYER
    # ========================================================

    print()
    print("--- Output Layer ---")

    output_linear = model.output_layer

    (
        output_pm1,
        output_bits
    ) = get_binary_weights(
        output_linear
    )

    output_weight_file = (
        FPGA_DIR
        /
        "output_weights.mem"
    )

    write_weight_mem(
        output_weight_file,
        output_bits
    )

    output_inputs = (
        output_linear.in_features
    )

    # No BatchNorm.
    #
    # Training classification:
    #
    # sigmoid(logit) > 0.5
    #
    # equivalent to:
    #
    # logit > 0
    #
    # For binary dot product:
    #
    # logit = 2*popcount - N
    #
    # Need:
    #
    # 2*popcount - N > 0
    #
    # For N = 160:
    #
    # popcount > 80
    #
    # Therefore:
    #
    # popcount >= 81

    output_threshold = (
        output_inputs // 2
    ) + 1

    output_threshold_file = (
        FPGA_DIR
        /
        "output_threshold.mem"
    )

    write_threshold_mem(
        output_threshold_file,
        [output_threshold]
    )

    output_weight_count = (
        output_linear.in_features
        *
        output_linear.out_features
    )

    total_weights += output_weight_count

    print(
        f"Input: {output_inputs}"
    )

    print(
        f"Weights: {output_weight_count}"
    )

    print(
        f"Output threshold: {output_threshold}"
    )

    print(
        f"Generated: {output_weight_file.name}"
    )

    print(
        f"Generated: {output_threshold_file.name}"
    )

    # ========================================================
    # FEATURE ORDER
    # ========================================================

    feature_output = (
        FPGA_DIR
        /
        "feature_order.json"
    )

    with open(
        feature_output,
        "w"
    ) as f:

        json.dump(
            features,
            f,
            indent=2
        )

    # ========================================================
    # QUANTIZATION METADATA
    # ========================================================

    quantization = {

        "input_features": len(features),

        "training_input": "Q1.8",

        "fractional_bits":
            cfg.FRACTIONAL_BITS,

        "scale":
            2 ** cfg.FRACTIONAL_BITS,

        "fpga_input": "uint8",

        "fpga_range": [
            0,
            255
        ],

        "conversion":
            "q1_8_value = uint8_value / 256.0",

        "layer0_accumulator":
            "signed sum of ± uint8 values"
    }

    with open(
        FPGA_DIR
        /
        "quantization.json",
        "w"
    ) as f:

        json.dump(
            quantization,
            f,
            indent=2
        )

    # ========================================================
    # MODEL METADATA
    # ========================================================

    model_info = {

        "generated":
            timestamp,

        "model":
            model_path.name,

        "input_size":
            cfg.INPUT_SIZE,

        "features":
            features,

        "hidden_layers":
            cfg.HIDDEN_LAYERS,

        "dense_connections":
            bool(cfg.USE_RESIDUALS),

        "output_size":
            cfg.OUTPUT_SIZE,

        "dimensions": [

            {
                "layer": 0,
                "input": 16,
                "output": 64
            },

            {
                "layer": 1,
                "input": 64,
                "output": 64
            },

            {
                "layer": 2,
                "input": 128,
                "output": 32
            },

            {
                "layer": "output",
                "input": 160,
                "output": 1
            }
        ],

        "weight_encoding": {

            "0":
                "-1",

            "1":
                "+1"
        },

        "weight_count": {

            "layer0":
                16 * 64,

            "layer1":
                64 * 64,

            "layer2":
                128 * 32,

            "output":
                160,

            "total":
                total_weights
        },

        "total_binary_weights":
            total_weights,

        "activation":
            "BinarySign",

        "batchnorm":
            "fused into thresholds",

        "hardware": {

            "layer0":
                "signed add/subtract + comparator",

            "layer1":
                "XNOR + popcount + comparator",

            "layer2":
                "XNOR + popcount + comparator",

            "output":
                "XNOR + popcount + comparator"
        }
    }

    with open(
        FPGA_DIR
        /
        "model_info.json",
        "w"
    ) as f:

        json.dump(
            model_info,
            f,
            indent=2
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("EXPORT SUCCESSFUL")
    print("=" * 70)

    print(
        f"FPGA artifacts:\n{FPGA_DIR}"
    )

    print()
    print(
        "Architecture:"
    )

    print(
        "16 -> 64 -> 64 -> 32 -> 1"
    )

    print(
        "Dense concatenation: ON"
    )

    print()
    print(
        "Weights:"
    )

    print(
        "Layer 0 : 1,024"
    )

    print(
        "Layer 1 : 4,096"
    )

    print(
        "Layer 2 : 4,096"
    )

    print(
        "Output  :   160"
    )

    print(
        f"TOTAL   : {total_weights:,}"
    )

    print()
    print(
        "Generated files:"
    )

    for file in sorted(
        FPGA_DIR.iterdir()
    ):

        if file.is_file():

            print(
                f"  {file.name}"
            )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "These artifacts were generated from the "
        "current trained .pth."
    )

    print(
        "Do not manually edit the .mem files."
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()