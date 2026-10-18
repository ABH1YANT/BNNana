#!/usr/bin/env python3
"""
BNNana FPGA hardware test: send 101 dataset samples over UART and read
one 8-bit classification result per packet.

Packet format expected by the current FPGA RTL:
    0xAA + 43 payload bytes + 0x55
Payload fields are sent in the exact FPGA parser order, little-endian.
The FPGA is expected to return one byte: 0x00 or 0x01.

Install dependency:
    py -m pip install pyserial

Example:
    py test_fpga_101_samples.py --port COM11

This script uses the first 101 rows by default. It does not shuffle the
dataset. The CSV must contain a Label column and all features listed in
selected_features.json, including the 16 fields required by the current RTL.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
import serial


DEFAULT_DATASET = r"C:\Users\a\Desktop\BNNana\datasets\processed\master_dataset.csv"
DEFAULT_SELECTED_FEATURES = r"C:\Users\a\Desktop\BNNana\artifacts\selected_features.json"
DEFAULT_PORT = "COM11"
DEFAULT_BAUD = 115200
DEFAULT_SAMPLES = 101
DEFAULT_TIMEOUT = 2.0

# Exact order, widths, and byte lengths expected by the current packet_parser.v.
# Byte order is little-endian (least-significant byte first).
FPGA_FEATURES = [
    ("Bwd Packet Length Max", 14, 2),
    ("Min Packet Length", 11, 2),
    ("Subflow Bwd Bytes", 25, 4),
    ("Total Length of Bwd Packets", 25, 4),
    ("Destination Port", 16, 2),
    ("min_seg_size_forward", 11, 2),
    ("ACK Flag Count", 1, 1),
    ("Subflow Bwd Packets", 17, 3),
    ("Fwd Packet Length Max", 15, 2),
    ("Total Backward Packets", 17, 3),
    ("Subflow Fwd Bytes", 21, 3),
    ("Max Packet Length", 15, 2),
    ("Total Length of Fwd Packets", 21, 3),
    ("Bwd Header Length", 21, 3),
    ("Flow Duration", 27, 4),
    ("Fwd Header Length", 21, 3),
]
LABEL_COLUMN = "Label"
HEADER = 0xAA
FOOTER = 0x55


def load_selected_features(path: Path) -> set[str]:
    """Accept a JSON list, or common dict wrappers containing a feature list."""
    with path.open("r", encoding="utf-8-sig") as f:
        obj = json.load(f)

    if isinstance(obj, list):
        names = obj
    elif isinstance(obj, dict):
        names = None
        for key in ("selected_features", "features", "feature_names", "columns"):
            if isinstance(obj.get(key), list):
                names = obj[key]
                break
        if names is None:
            # Also accept a mapping where feature names are the keys.
            if all(isinstance(k, str) for k in obj.keys()):
                names = list(obj.keys())
            else:
                raise ValueError(
                    "Unrecognized selected_features.json format. Expected a list "
                    "or a dict containing selected_features/features/feature_names/columns."
                )
    else:
        raise ValueError("selected_features.json must contain a JSON list or object.")

    if not all(isinstance(x, str) for x in names):
        raise ValueError("The selected feature names must all be strings.")
    return set(names)


def parse_label(value) -> int:
    """Convert a dataset label to binary 0/1."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        text = str(value).strip().lower()
        mapping = {
            "benign": 0, "normal": 0, "0": 0,
            "attack": 1, "malicious": 1, "ddos": 1, "1": 1,
        }
        if text in mapping:
            return mapping[text]
        raise ValueError(f"Unsupported label value: {value!r}")

    if number not in (0.0, 1.0):
        raise ValueError(
            f"Expected binary Label values 0/1, got {value!r}. "
            "Map the dataset labels to the FPGA's 0/1 classes first."
        )
    return int(number)


def feature_to_int(value, name: str) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Feature {name!r} has non-numeric value {value!r}.")
    if not pd.notna(number):
        raise ValueError(f"Feature {name!r} contains a missing value.")
    rounded = round(number)
    if abs(number - rounded) > 1e-6:
        raise ValueError(
            f"Feature {name!r} has non-integer value {value!r}. "
            "The current FPGA packet protocol sends integer feature values."
        )
    if rounded < 0:
        raise ValueError(
            f"Feature {name!r} has negative value {rounded}; current packet fields "
            "are unsigned."
        )
    return int(rounded)


def encode_packet(row, columns) -> bytes:
    payload = bytearray()

    for name, width, byte_count in FPGA_FEATURES:
        value = feature_to_int(row[columns[name]], name)
        if value >= (1 << width):
            raise ValueError(
                f"{name}={value} exceeds the unsigned {width}-bit range "
                f"(maximum {(1 << width) - 1})."
            )
        payload.extend(value.to_bytes(byte_count, byteorder="little", signed=False))

    if len(payload) != 43:
        raise AssertionError(f"Internal packet error: expected 43 payload bytes, got {len(payload)}.")

    return bytes([HEADER]) + bytes(payload) + bytes([FOOTER])


def read_one_result(ser: serial.Serial, timeout: float):
    """Read exactly one classification byte, with a deadline."""
    deadline = time.monotonic() + timeout
    data = bytearray()
    while len(data) < 1 and time.monotonic() < deadline:
        chunk = ser.read(1)
        if chunk:
            data.extend(chunk)
    return data[0] if data else None


def main():
    parser = argparse.ArgumentParser(
        description="Send dataset samples to the BNNana FPGA and receive classifications."
    )
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Path to master_dataset.csv")
    parser.add_argument("--features", default=DEFAULT_SELECTED_FEATURES,
                        help="Path to selected_features.json")
    parser.add_argument("--port", default=DEFAULT_PORT, help="Serial port, e.g. COM11")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD, help="UART baud rate")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES,
                        help="Number of sequential dataset rows to send (default: 101)")
    parser.add_argument("--start-row", type=int, default=0,
                        help="Zero-based row index to start from (default: 0)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help="Seconds to wait for each FPGA result")
    parser.add_argument("--output", default="fpga_101_sample_results.csv",
                        help="Output CSV for per-sample results")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    features_path = Path(args.features)

    if args.samples < 1 or args.start_row < 0:
        parser.error("--samples must be positive and --start-row must be zero or greater.")

    try:
        selected = load_selected_features(features_path)
        missing_from_selection = [name for name, _, _ in FPGA_FEATURES if name not in selected]
        if missing_from_selection:
            raise ValueError(
                "selected_features.json does not include all 16 features required by the "
                "current FPGA packet parser. Missing: " + ", ".join(missing_from_selection)
            )

        df = pd.read_csv(dataset_path)
        # Strip accidental whitespace in CSV column headings without changing feature names.
        df.columns = [str(c).strip() for c in df.columns]

        required_columns = [name for name, _, _ in FPGA_FEATURES] + [LABEL_COLUMN]
        missing = [name for name in required_columns if name not in df.columns]
        if missing:
            raise ValueError("Dataset is missing required columns: " + ", ".join(missing))

        end_row = args.start_row + args.samples
        if len(df) < end_row:
            raise ValueError(
                f"Requested rows {args.start_row}..{end_row - 1}, but dataset has only "
                f"{len(df)} rows."
            )

        test_df = df.iloc[args.start_row:end_row].copy()

        # Validate all samples before opening the port, avoiding a partial test due to bad data.
        expected_labels = []
        packets = []
        for offset, (_, row) in enumerate(test_df.iterrows()):
            sample_idx = args.start_row + offset
            expected_labels.append(parse_label(row[LABEL_COLUMN]))
            packets.append(encode_packet(row, {name: name for name, _, _ in FPGA_FEATURES}))

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print()
    print("=" * 72)
    print("BNNana FPGA DATASET INTEGRATION TEST")
    print("=" * 72)
    print(f"Dataset       : {dataset_path}")
    print(f"Selected feats: {features_path}")
    print(f"UART          : {args.port} @ {args.baud}, 8-N-1")
    print(f"Rows          : {args.start_row} through {args.start_row + args.samples - 1}")
    print(f"Samples       : {args.samples}")
    print(f"Packet        : 0xAA + 43 payload bytes + 0x55")
    print("Feature order : fixed to the current FPGA packet_parser.v")
    print("=" * 72)

    results = []
    try:
        with serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            write_timeout=args.timeout,
        ) as ser:
            # Allow USB-UART/board startup, but do not clear input after each packet:
            # that could discard a valid FPGA classification.
            time.sleep(0.2)
            ser.reset_input_buffer()

            for offset, packet in enumerate(packets):
                row_index = args.start_row + offset
                expected = expected_labels[offset]
                started = time.perf_counter()

                ser.write(packet)
                ser.flush()

                received = read_one_result(ser, args.timeout)
                elapsed_ms = (time.perf_counter() - started) * 1000.0

                if received is None:
                    status = "TIMEOUT"
                    predicted = None
                    print(
                        f"Row {row_index}: expected={expected} received=TIMEOUT "
                        f"after {elapsed_ms:.1f} ms"
                    )
                elif received not in (0x00, 0x01):
                    status = "INVALID_BYTE"
                    predicted = received
                    print(
                        f"Row {row_index}: expected={expected} received=0x{received:02X} "
                        f"INVALID ({elapsed_ms:.1f} ms)"
                    )
                else:
                    predicted = received
                    status = "PASS" if predicted == expected else "MISMATCH"
                    print(
                        f"Row {row_index}: expected={expected} predicted={predicted} "
                        f"{status} ({elapsed_ms:.1f} ms)"
                    )

                results.append({
                    "dataset_row": row_index,
                    "expected_label": expected,
                    "fpga_classification": predicted,
                    "status": status,
                    "elapsed_ms": round(elapsed_ms, 3),
                })

    except Exception as exc:
        print(f"\nUART ERROR: {exc}", file=sys.stderr)
        return 3

    result_df = pd.DataFrame(results)
    output_path = Path(args.output)
    result_df.to_csv(output_path, index=False)

    valid_results = result_df["fpga_classification"].isin([0, 1])
    compared = result_df[valid_results]
    correct = int((compared["fpga_classification"] == compared["expected_label"]).sum())
    mismatches = int((compared["fpga_classification"] != compared["expected_label"]).sum())
    timeouts = int((result_df["status"] == "TIMEOUT").sum())
    invalid = int((result_df["status"] == "INVALID_BYTE").sum())
    pass_rate = (correct / len(compared) * 100.0) if len(compared) else 0.0

    print()
    print("=" * 72)
    print("FINAL SUMMARY")
    print("=" * 72)
    print(f"Samples attempted      : {len(result_df)}")
    print(f"Valid FPGA results     : {len(compared)}")
    print(f"Matches with labels    : {correct}")
    print(f"Label mismatches       : {mismatches}")
    print(f"UART timeouts          : {timeouts}")
    print(f"Invalid result bytes   : {invalid}")
    print(f"Accuracy on valid replies: {pass_rate:.2f}%")
    print(f"Results saved to       : {output_path.resolve()}")
    print("=" * 72)

    if len(result_df) == args.samples and timeouts == 0 and invalid == 0:
        print("UART exchange completed for every requested sample.")
    else:
        print("TEST INCOMPLETE: investigate timeouts, framing, packet handling, or UART setup.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())