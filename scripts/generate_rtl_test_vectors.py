from pathlib import Path
import json
import pandas as pd

ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")

MASTER_DATASET = ROOT / "datasets" / "processed" / "master_dataset.csv"
OUT_DIR = ROOT / "fpga" / "artifactes"

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================
# CONFIGURATION
# ==============================================================

START_ROW = 0
END_ROW = 100

NUM_SAMPLES = END_ROW - START_ROW + 1


# ==============================================================
# FEATURES
# ==============================================================

FEATURES = [
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

WIDTHS = [
    14, 11, 25, 25, 16, 11, 1, 17,
    15, 17, 21, 15, 21, 21, 27, 21
]


# ==============================================================
# CREATE ONE 45-BYTE PACKET
# ==============================================================

def make_packet(row):

    packet = [0xAA]

    for feature, width in zip(FEATURES, WIDTHS):

        value = int(row[feature])

        if value < 0 or value >= (1 << width):
            raise ValueError(
                f"{feature}={value} does not fit in {width} bits"
            )

        # Little-endian byte order
        for i in range((width + 7) // 8):

            packet.append(
                (value >> (8 * i)) & 0xFF
            )

    packet.append(0x55)

    if len(packet) != 45:
        raise AssertionError(
            f"Packet length {len(packet)}, expected 45"
        )

    return packet


# ==============================================================
# MAIN
# ==============================================================

def main():

    # ----------------------------------------------------------
    # Load dataset
    # ----------------------------------------------------------

    df = pd.read_csv(MASTER_DATASET)


    # ----------------------------------------------------------
    # Validate row count
    # ----------------------------------------------------------

    if len(df) <= END_ROW:

        raise ValueError(
            f"Dataset has {len(df)} rows, "
            f"but row {END_ROW} was requested."
        )


    # ----------------------------------------------------------
    # Validate features
    # ----------------------------------------------------------

    missing = [
        f for f in FEATURES
        if f not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing features: {missing}"
        )


    # ----------------------------------------------------------
    # Select rows 0..100
    # ----------------------------------------------------------

    df_samples = df.iloc[
        START_ROW:END_ROW + 1
    ].copy()


    # ----------------------------------------------------------
    # Generate packets
    # ----------------------------------------------------------

    all_bytes = []
    metadata = []

    for local_index, (_, row) in enumerate(
        df_samples.iterrows()
    ):

        dataset_row = START_ROW + local_index

        packet = make_packet(row)

        all_bytes.extend(packet)


        metadata.append({

            "sample": local_index,

            "dataset_row": dataset_row,

            "label": (
                int(row["Label"])
                if "Label" in df.columns
                else None
            ),

            "features": {
                f: int(row[f])
                for f in FEATURES
            },

            "packet_hex": [
                f"{b:02X}"
                for b in packet
            ],

        })


    # ==========================================================
    # WRITE PACKET MEMORY
    # ==========================================================

    packet_file = (
        OUT_DIR /
        f"debug_{NUM_SAMPLES}_packets.mem"
    )

    packet_file.write_text(
        "".join(
            f"{b:02X}\n"
            for b in all_bytes
        ),
        encoding="utf-8"
    )


    # ==========================================================
    # WRITE LABEL MEMORY
    # ==========================================================

    if "Label" in df.columns:

        label_file = (
            OUT_DIR /
            f"debug_{NUM_SAMPLES}_labels.mem"
        )

        label_file.write_text(

            "".join(
                f"{int(x):02X}\n"
                for x in df_samples["Label"]
            ),

            encoding="utf-8"
        )

    else:

        label_file = None


    # ==========================================================
    # WRITE METADATA
    # ==========================================================

    metadata_file = (
        OUT_DIR /
        f"debug_{NUM_SAMPLES}_packet_metadata.json"
    )

    metadata_file.write_text(

        json.dumps(
            metadata,
            indent=2
        ),

        encoding="utf-8"
    )


    # ==========================================================
    # SUMMARY
    # ==========================================================

    print("=" * 70)
    print("RAW PACKETS GENERATED")
    print("=" * 70)

    print(f"Dataset rows : {START_ROW}..{END_ROW}")
    print(f"Samples      : {NUM_SAMPLES}")
    print(f"Packets      : {NUM_SAMPLES}")
    print(f"Bytes        : {NUM_SAMPLES * 45}")

    print("")
    print(f"Packets : {packet_file}")

    if label_file is not None:
        print(f"Labels  : {label_file}")

    print(f"Metadata: {metadata_file}")

    print("")
    print("Packet format:")
    print("  0xAA + 43 payload bytes + 0x55")
    print("=" * 70)


# ==============================================================
# ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    main()