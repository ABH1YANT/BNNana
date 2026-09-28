import json
import random
from pathlib import Path

import pandas as pd
import numpy as np


# ==============================================================
# PATHS
# ==============================================================

ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")

META_FILE = ROOT / "artifacts" / "lut_metadata.json"

OUT_DIR = ROOT / "fpga_new" / "tb_vectors"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = OUT_DIR / "preprocess_inputs.mem"
EXPECTED_FILE = OUT_DIR / "preprocess_expected.mem"


# ==============================================================
# CONFIGURATION
# ==============================================================

NUM_SAMPLES = 1000
RANDOM_SEED = 12345

random.seed(RANDOM_SEED)


# ==============================================================
# LOAD METADATA
# ==============================================================

with open(META_FILE, "r") as f:
    metadata = json.load(f)


# ==============================================================
# FEATURE ORDER
# ==============================================================
#
# This MUST match selected_features.json / preprocessing.v
#
# ==============================================================

feature_order = [
    "Bwd Packet Length Max",
    "Min Packet Length",
    "Subflow Bwd Bytes",
    "Total Length of Bwd Packets",
    "Destination Port",
    "min_seg_size_forward",
    "ACK Flag Count",
    "Subflow Bwd Packets",
    "Fwd Packet Length Max",
    "Total Backward Packets",
    "Subflow Fwd Bytes",
    "Max Packet Length",
    "Total Length of Fwd Packets",
    "Bwd Header Length",
    "Flow Duration",
    "Fwd Header Length",
]


# ==============================================================
# RAW FEATURE WIDTHS
# ==============================================================

raw_widths = [
    14,  # F0
    11,  # F1
    25,  # F2
    25,  # F3
    16,  # F4
    11,  # F5
    1,   # F6
    17,  # F7
    15,  # F8
    17,  # F9
    21,  # F10
    15,  # F11
    21,  # F12
    21,  # F13
    27,  # F14
    21,  # F15
]


# ==============================================================
# LOAD LUTs
# ==============================================================

luts = []

print()
print("Loading LUTs...")
print("----------------------------------------------")

for i, feature_name in enumerate(feature_order):

    if feature_name not in metadata:
        raise KeyError(
            f"Feature '{feature_name}' not found in lut_metadata.json"
        )

    info = metadata[feature_name]

    lut_file = Path(info["lut_file"])

    if not lut_file.exists():
        raise FileNotFoundError(
            f"LUT file not found:\n{lut_file}"
        )

    df = pd.read_csv(lut_file)

    if "normalized_value" not in df.columns:
        raise KeyError(
            f"'normalized_value' not found in {lut_file}"
        )

    normalized = df["normalized_value"].to_numpy(
        dtype=np.float64
    )

    # ----------------------------------------------------------
    # EXACT Q1.8 conversion used for FPGA .mem files
    # ----------------------------------------------------------

    q = np.clip(
        normalized,
        0.0,
        1.0 - 1.0 / 256.0
    )

    q = np.round(q * 256.0)

    q = np.clip(q, 0, 255).astype(np.uint8)

    luts.append({
        "name": feature_name,
        "max_value": int(info["max_value"]),
        "discarded_bits": int(
            info["discarded_lower_bits"]
        ),
        "lut_bits": int(info["lut_bits"]),
        "values": q,
    })

    print(
        f"F{i:2d}: {feature_name:<32} "
        f"LUT={len(q):5d} "
        f"discard={info['discarded_lower_bits']}"
    )


# ==============================================================
# PYTHON VERSION OF VERILOG LUT ADDRESSING
# ==============================================================

def get_lut_address(raw_value, discarded_bits, lut_size):

    # Verilog:
    #
    # addr = raw >> discarded_bits
    #

    address = raw_value >> discarded_bits

    if address >= lut_size:
        address = lut_size - 1

    return address


# ==============================================================
# PYTHON PREPROCESSING
# ==============================================================

def preprocess(raw_values):

    q_values = []

    for i, raw_value in enumerate(raw_values):

        lut = luts[i]

        address = get_lut_address(
            raw_value,
            lut["discarded_bits"],
            len(lut["values"])
        )

        q_value = int(
            lut["values"][address]
        )

        q_values.append(q_value)

    return q_values


# ==============================================================
# PACK RAW FEATURES
#
# Total width = 278 bits
#
# F0  = bits 13:0
# F1  = bits 24:14
# ...
# F15 = bits 277:257
# ==============================================================

def pack_raw_values(raw_values):

    packed = 0
    bit_position = 0

    for value, width in zip(
        raw_values,
        raw_widths
    ):

        value = int(value)

        if value < 0:
            raise ValueError(
                f"Negative value: {value}"
            )

        if value >= (1 << width):
            raise ValueError(
                f"Value {value} does not fit "
                f"in {width} bits"
            )

        packed |= value << bit_position

        bit_position += width

    return packed


# ==============================================================
# PACK EXPECTED Q VALUES
#
# F0  = bits 7:0
# F1  = bits 15:8
# ...
# F15 = bits 127:120
# ==============================================================

def pack_expected_values(q_values):

    packed = 0
    bit_position = 0

    for value in q_values:

        packed |= int(value) << bit_position

        bit_position += 8

    return packed


# ==============================================================
# GENERATE TEST SAMPLES
# ==============================================================

samples = []


# --------------------------------------------------------------
# TEST 0: all zeros
# --------------------------------------------------------------

samples.append([
    0
    for _ in range(16)
])


# --------------------------------------------------------------
# TEST 1: all maximum values
# --------------------------------------------------------------

samples.append([
    lut["max_value"]
    for lut in luts
])


# --------------------------------------------------------------
# TEST 2-17:
# each feature individually at maximum
# --------------------------------------------------------------

for feature_index in range(16):

    sample = [0] * 16

    sample[feature_index] = \
        luts[feature_index]["max_value"]

    samples.append(sample)


# --------------------------------------------------------------
# RANDOM TESTS
# --------------------------------------------------------------

while len(samples) < NUM_SAMPLES:

    sample = []

    for lut in luts:

        value = random.randint(
            0,
            lut["max_value"]
        )

        sample.append(value)

    samples.append(sample)


# ==============================================================
# WRITE FILES
# ==============================================================

print()
print("Generating test vectors...")
print("----------------------------------------------")


with open(INPUT_FILE, "w") as input_file, \
     open(EXPECTED_FILE, "w") as expected_file:

    for sample_number, raw_values in enumerate(samples):

        # ------------------------------------------------------
        # Python expected preprocessing
        # ------------------------------------------------------

        q_values = preprocess(raw_values)

        # ------------------------------------------------------
        # Pack raw inputs
        # ------------------------------------------------------

        packed_input = pack_raw_values(
            raw_values
        )

        # ------------------------------------------------------
        # Pack expected outputs
        # ------------------------------------------------------

        packed_expected = pack_expected_values(
            q_values
        )

        # ------------------------------------------------------
        # Write
        # ------------------------------------------------------

        input_file.write(
            f"{packed_input:070X}\n"
        )

        expected_file.write(
            f"{packed_expected:032X}\n"
        )


# ==============================================================
# PRINT VERIFICATION INFORMATION
# ==============================================================

print()
print("==============================================")
print("PREPROCESSING TEST VECTORS GENERATED")
print("==============================================")

print(f"Samples        : {len(samples)}")
print(f"Raw width      : 278 bits")
print(f"Expected width : 128 bits")

print()
print("Input file:")
print(INPUT_FILE)

print()
print("Expected file:")
print(EXPECTED_FILE)


# ==============================================================
# SHOW FIRST TWO TESTS
# ==============================================================

print()
print("----------------------------------------------")
print("TEST 0: ALL ZERO")
print("----------------------------------------------")

q0 = preprocess(samples[0])

print(
    "Expected Q1.8:",
    " ".join(f"{x:02X}" for x in q0)
)


print()
print("----------------------------------------------")
print("TEST 1: ALL MAXIMUM")
print("----------------------------------------------")

q1 = preprocess(samples[1])

print(
    "Expected Q1.8:",
    " ".join(f"{x:02X}" for x in q1)
)


print()
print("==============================================")
print("DONE")
print("==============================================")