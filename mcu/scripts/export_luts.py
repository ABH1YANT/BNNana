
from pathlib import Path
import csv
import json

# ============================================================
# PATHS
# ============================================================

# Folder containing the 16 extracted feature LUT CSV files.
LUT_DIR = Path(
    r"C:\Users\DELL\Desktop\BNNana\artifacts\feature_luts"
)

# LUT metadata JSON file.
METADATA = Path(
    r"C:\Users\DELL\Desktop\BNNana\artifacts\lut_metadata.json"
)

# Generated C++ header for the ESP32 firmware.
OUTPUT_HEADER = Path(
    r"C:\Users\DELL\Desktop\BNNana\mcu\Core\Inc\bnn_luts.h"
)


# ============================================================
# FEATURE ORDER
# Must match selected_features.json and the BNN input order.
# ============================================================

FEATURES = [
    ("Bwd Packet Length Max", "Bwd_Packet_Length_Max_lut.csv"),
    ("Min Packet Length", "Min_Packet_Length_lut.csv"),
    ("Subflow Bwd Bytes", "Subflow_Bwd_Bytes_lut.csv"),
    (
        "Total Length of Bwd Packets",
        "Total_Length_of_Bwd_Packets_lut.csv",
    ),
    ("Destination Port", "Destination_Port_lut.csv"),
    ("min_seg_size_forward", "min_seg_size_forward_lut.csv"),
    ("ACK Flag Count", "ACK_Flag_Count_lut.csv"),
    ("Subflow Bwd Packets", "Subflow_Bwd_Packets_lut.csv"),
    ("Fwd Packet Length Max", "Fwd_Packet_Length_Max_lut.csv"),
    ("Total Backward Packets", "Total_Backward_Packets_lut.csv"),
    ("Subflow Fwd Bytes", "Subflow_Fwd_Bytes_lut.csv"),
    ("Max Packet Length", "Max_Packet_Length_lut.csv"),
    (
        "Total Length of Fwd Packets",
        "Total_Length_of_Fwd_Packets_lut.csv",
    ),
    ("Bwd Header Length", "Bwd_Header_Length_lut.csv"),
    ("Flow Duration", "Flow_Duration_lut.csv"),
    ("Fwd Header Length", "Fwd_Header_Length_lut.csv"),
]


# ============================================================
# HELPERS
# ============================================================

def read_metadata():
    """Load and validate LUT metadata."""

    if not METADATA.is_file():
        raise FileNotFoundError(
            f"Metadata file not found:\n{METADATA}"
        )

    with METADATA.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    return metadata


def read_lut_csv(csv_path, feature, bucket_count):
    """
    Read one feature LUT.

    Expected CSV columns:
        bucket
        normalized_value

    Returns normalized values indexed by bucket number.
    """

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"LUT CSV not found:\n{csv_path}"
        )

    values = [None] * bucket_count

    with csv_path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {"bucket", "normalized_value"}

        if not reader.fieldnames:
            raise ValueError(
                f"{csv_path.name} is empty or has no CSV header."
            )

        actual_columns = set(reader.fieldnames)
        missing_columns = required_columns - actual_columns

        if missing_columns:
            raise ValueError(
                f"{csv_path.name} is missing columns: "
                f"{sorted(missing_columns)}. "
                f"Found: {reader.fieldnames}"
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                bucket = int(row["bucket"])
                normalized = float(row["normalized_value"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid data in {csv_path.name}, "
                    f"row {row_number}: {row}"
                ) from error

            if not 0 <= bucket < bucket_count:
                raise ValueError(
                    f"{feature}: bucket {bucket} is outside "
                    f"the expected range 0..{bucket_count - 1}."
                )

            if values[bucket] is not None:
                raise ValueError(
                    f"{feature}: duplicate bucket {bucket}."
                )

            if not 0.0 <= normalized <= 1.0:
                raise ValueError(
                    f"{feature}: normalized value {normalized} "
                    f"is outside [0, 1] in row {row_number}."
                )

            values[bucket] = normalized

    missing_buckets = [
        index
        for index, value in enumerate(values)
        if value is None
    ]

    if missing_buckets:
        preview = missing_buckets[:10]
        raise ValueError(
            f"{feature}: missing {len(missing_buckets)} LUT "
            f"buckets. First missing buckets: {preview}"
        )

    return values


def quantize_q8(normalized):
    """
    Convert a normalized LUT value to an unsigned 8-bit value.

    This encodes values using a scale factor of 256.
    The exact compatibility with model.py must be validated.
    """

    # Clamp to the range used by the current exporter.
    normalized = max(0.0, min(normalized, 255.0 / 256.0))

    # Python round() uses ties-to-even rounding.
    quantized = round(normalized * 256.0)

    return max(0, min(255, int(quantized)))


def format_cpp_array(array_name, values, values_per_line=16):
    """Format values as a C++ constexpr uint8_t array."""

    lines = [
        f"static constexpr uint8_t {array_name}[{len(values)}] = {{"
    ]

    for start in range(0, len(values), values_per_line):
        chunk = values[start:start + values_per_line]

        lines.append(
            "    " + ", ".join(str(value) for value in chunk) + ","
        )

    lines.append("};")

    return "\n".join(lines)


# ============================================================
# MAIN EXPORT
# ============================================================

def main():
    print("BNNana LUT exporter")
    print("===================")

    if not LUT_DIR.is_dir():
        raise NotADirectoryError(
            f"LUT folder not found:\n{LUT_DIR}"
        )

    metadata = read_metadata()

    output = [
        "// Generated by scripts/export_luts.py",
        "// Do not edit this file manually.",
        "#pragma once",
        "",
        "#include <stdint.h>",
        "",
        "static constexpr int BNN_LUT_FEATURES = 16;",
        "",
    ]

    for index, (feature, filename) in enumerate(FEATURES):
        print(f"Processing {index + 1}/16: {feature}")

        if feature not in metadata:
            raise KeyError(
                f"Feature '{feature}' is missing from metadata."
            )

        info = metadata[feature]

        if "discarded_lower_bits" not in info:
            raise KeyError(
                f"{feature}: metadata is missing "
                "'discarded_lower_bits'."
            )

        if "bucket_count" not in info:
            raise KeyError(
                f"{feature}: metadata is missing 'bucket_count'."
            )

        shift = int(info["discarded_lower_bits"])
        bucket_count = int(info["bucket_count"])

        if shift < 0:
            raise ValueError(
                f"{feature}: discarded_lower_bits cannot be negative."
            )

        if bucket_count <= 0:
            raise ValueError(
                f"{feature}: bucket_count must be positive."
            )

        csv_path = LUT_DIR / filename

        normalized_values = read_lut_csv(
            csv_path,
            feature,
            bucket_count,
        )

        # Convert normalized values to compact unsigned integers.
        quantized_values = [
            quantize_q8(value)
            for value in normalized_values
        ]

        output.append(f"// Feature {index}: {feature}")
        output.append(
            f"// LUT address: raw_value >> {shift}"
        )

        output.append(
            format_cpp_array(
                f"BNN_LUT_{index}",
                quantized_values,
            )
        )

        output.append(
            f"static constexpr int BNN_LUT_{index}_SHIFT = {shift};"
        )

        output.append(
            f"static constexpr int BNN_LUT_{index}_SIZE = "
            f"{bucket_count};"
        )

        output.append("")

    # Create the destination folder if necessary.
    OUTPUT_HEADER.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Write the generated C++ header.
    OUTPUT_HEADER.write_text(
        "\n".join(output) + "\n",
        encoding="utf-8",
    )

    print()
    print("LUT export completed successfully.")
    print(f"Input folder: {LUT_DIR}")
    print(f"Metadata:     {METADATA}")
    print(f"Output file:  {OUTPUT_HEADER}")
    print()
    print("Generated 16 LUT arrays.")


if __name__ == "__main__":
    main()
