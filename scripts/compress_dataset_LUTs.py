# ============================================================
# BNNana
# Distribution-Based LUT Generation
#
# Each feature gets its own LUT.
#
# <= 16 bits:
#     exact natural address range
#
# > 16 bits:
#     keep upper 16 bits as LUT address
#
# Representative:
#     chosen from the DISTRIBUTION inside each bucket
#     (not simply median for every feature)
#
# After representative selection:
#     log1p()
#     MinMax -> [0,1]
# ============================================================

import json
import numpy as np
import pandas as pd

from pathlib import Path
from scipy.stats import skew


# ============================================================
# PATHS
# ============================================================

ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")

INPUT_FILE = (
    ROOT
    / "datasets"
    / "processed"
    / "master_dataset.csv"
)

OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "feature_luts"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DATASET = (
    ROOT
    / "datasets"
    / "processed"
    / "scaled_dataset.csv"
)

OUTPUT_METADATA = (
    ROOT
    / "artifacts"
    / "lut_metadata.json"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "Min Packet Length",
    "Bwd Packet Length Max",
    "Total Length of Bwd Packets",
    "Subflow Bwd Bytes",
    "min_seg_size_forward",
    "Bwd Header Length",
    "Destination Port",
    "Total Length of Fwd Packets",
    "Fwd Packet Length Max",
    "ACK Flag Count",
    "Subflow Fwd Bytes",
    "Total Backward Packets",
    "Subflow Bwd Packets",
    "Max Packet Length",
    "Flow Duration",
    "Fwd Header Length",
]


# ============================================================
# BIT WIDTH
# ============================================================

def get_bit_width(max_value):

    max_value = int(max_value)

    if max_value <= 0:
        return 1

    return int(
        np.ceil(
            np.log2(max_value + 1)
        )
    )


# ============================================================
# CREATE LUT ADDRESS
# ============================================================

def make_addresses(values, original_bits):

    values = np.asarray(
        values,
        dtype=np.int64
    )

    lut_bits = min(
        original_bits,
        16
    )

    if original_bits <= 16:

        # Exact address
        addresses = values

    else:

        # Keep upper 16 bits
        shift = original_bits - 16

        addresses = (
            values.astype(np.uint64)
            >> shift
        )

    max_address = (
        (1 << lut_bits) - 1
    )

    addresses = np.clip(
        addresses,
        0,
        max_address
    )

    return addresses.astype(np.int64)


# ============================================================
# DISTRIBUTION-BASED REPRESENTATIVE
# ============================================================

def choose_representative(
    bucket_values,
    feature_skew
):
    """
    Choose one representative value from the
    distribution inside a bucket.

    The important point is:

        NOT simply median everywhere.

    For strongly right-skewed distributions:
        work in log space.

    For approximately symmetric distributions:
        work in raw space.

    The representative is the distribution's
    central location in the appropriate space.
    """

    values = np.asarray(
        bucket_values,
        dtype=np.float64
    )

    if len(values) == 0:
        return np.nan

    # --------------------------------------------------------
    # Remove invalid values
    # --------------------------------------------------------

    values = values[
        np.isfinite(values)
    ]

    if len(values) == 0:
        return np.nan

    values = np.maximum(
        values,
        0
    )

    # --------------------------------------------------------
    # Strong right skew
    # --------------------------------------------------------

    if feature_skew >= 2.0:

        # Transform the distribution first.
        #
        # This prevents a few extremely large values
        # from dominating the representative.

        log_values = np.log1p(values)

        representative_log = np.mean(
            log_values
        )

        representative = np.expm1(
            representative_log
        )

    # --------------------------------------------------------
    # Moderate skew
    # --------------------------------------------------------

    elif feature_skew >= 1.0:

        # Blend the raw and log-domain distribution
        # so the representative follows the actual
        # bucket distribution without being dominated
        # by the long tail.

        raw_center = np.mean(
            values
        )

        log_center = np.expm1(
            np.mean(
                np.log1p(values)
            )
        )

        representative = (
            0.25 * raw_center
            +
            0.75 * log_center
        )

    # --------------------------------------------------------
    # Low skew / approximately symmetric
    # --------------------------------------------------------

    else:

        representative = np.mean(
            values
        )

    return float(
        representative
    )


# ============================================================
# BUILD LUT FOR ONE FEATURE
# ============================================================

def build_feature_lut(
    values,
    feature_name
):

    values = np.asarray(
        values,
        dtype=np.float64
    )

    values = np.nan_to_num(
        values,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )

    values = np.maximum(
        values,
        0
    )

    # --------------------------------------------------------
    # Feature statistics
    # --------------------------------------------------------

    max_value = int(
        np.max(values)
    )

    min_value = int(
        np.min(values)
    )

    original_bits = get_bit_width(
        max_value
    )

    lut_bits = min(
        original_bits,
        16
    )

    bucket_count = (
        1 << lut_bits
    )

    feature_skew = float(
        skew(values)
    )

    if not np.isfinite(feature_skew):
        feature_skew = 0.0

    # --------------------------------------------------------
    # Addresses
    # --------------------------------------------------------

    addresses = make_addresses(
        values,
        original_bits
    )

    # --------------------------------------------------------
    # LUT arrays
    # --------------------------------------------------------

    representatives = np.zeros(
        bucket_count,
        dtype=np.float64
    )

    sample_counts = np.zeros(
        bucket_count,
        dtype=np.int64
    )

    # --------------------------------------------------------
    # Fill every bucket
    # --------------------------------------------------------

    for bucket in range(
        bucket_count
    ):

        bucket_values = values[
            addresses == bucket
        ]

        sample_counts[bucket] = (
            len(bucket_values)
        )

        # ----------------------------------------------------
        # Non-empty bucket
        # ----------------------------------------------------

        if len(bucket_values) > 0:

            representatives[bucket] = (
                choose_representative(
                    bucket_values,
                    feature_skew
                )
            )

        # ----------------------------------------------------
        # Empty bucket
        # ----------------------------------------------------

        else:

            if original_bits <= 16:

                # Exact integer address
                representatives[bucket] = (
                    bucket
                )

            else:

                # Raw range represented by this
                # upper-16-bit bucket.

                shift = (
                    original_bits - 16
                )

                low = (
                    bucket << shift
                )

                high = (
                    ((bucket + 1) << shift)
                    - 1
                )

                representatives[bucket] = (
                    low + high
                ) / 2.0

    # ========================================================
    # Handle any remaining invalid LUT values
    # ========================================================

    representatives = np.nan_to_num(
        representatives,
        nan=0.0,
        posinf=float(max_value),
        neginf=0.0
    )

    representatives = np.maximum(
        representatives,
        0
    )

    # ========================================================
    # Apply LOG1P to REPRESENTATIVE
    # ========================================================

    log_values = np.log1p(
        representatives
    )

    # ========================================================
    # MinMax normalization
    # ========================================================

    log_min = np.min(
        log_values
    )

    log_max = np.max(
        log_values
    )

    if log_max > log_min:

        normalized_values = (
            log_values - log_min
        ) / (
            log_max - log_min
        )

    else:

        normalized_values = np.zeros(
            bucket_count,
            dtype=np.float64
        )

    # ========================================================
    # Dataset values
    # ========================================================

    transformed_values = (
        normalized_values[
            addresses
        ]
    )

    return {
        "addresses": addresses,
        "representatives": representatives,
        "log_values": log_values,
        "normalized_values": normalized_values,
        "sample_counts": sample_counts,
        "min_value": min_value,
        "max_value": max_value,
        "original_bits": original_bits,
        "lut_bits": lut_bits,
        "bucket_count": bucket_count,
        "feature_skew": feature_skew,
        "transformed_values": transformed_values,
    }


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 80)
print("BNNana DISTRIBUTION-BASED LUT GENERATION")
print("=" * 80)

print("\nLoading dataset:")
print(INPUT_FILE)

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"\nRows: {len(df):,}"
)

# ============================================================
# PROCESS FEATURES
# ============================================================

scaled_df = df.copy()

metadata = {}

for feature in FEATURES:

    print("\n" + "-" * 80)
    print(feature)
    print("-" * 80)

    values = pd.to_numeric(
        df[feature],
        errors="coerce"
    ).fillna(0).values

    result = build_feature_lut(
        values,
        feature
    )

    # --------------------------------------------------------
    # Replace dataset feature
    # --------------------------------------------------------

    scaled_df[feature] = (
        result["transformed_values"]
        .astype(np.float32)
    )

    # --------------------------------------------------------
    # Save LUT
    # --------------------------------------------------------

    safe_name = (
        feature
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    lut_file = (
        OUTPUT_DIR
        / f"{safe_name}_lut.csv"
    )

    lut_df = pd.DataFrame({

        "bucket":
            np.arange(
                result["bucket_count"]
            ),

        "representative_raw":
            result["representatives"],

        "log_value":
            result["log_values"],

        "normalized_value":
            result["normalized_values"],

        "sample_count":
            result["sample_counts"],
    })

    lut_df.to_csv(
        lut_file,
        index=False
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    compressed = (
        result["original_bits"] > 16
    )

    discarded_bits = max(
        result["original_bits"] - 16,
        0
    )

    metadata[feature] = {

        "min_value":
            result["min_value"],

        "max_value":
            result["max_value"],

        "skewness":
            result["feature_skew"],

        "original_bits":
            result["original_bits"],

        "lut_bits":
            result["lut_bits"],

        "bucket_count":
            result["bucket_count"],

        "compressed":
            compressed,

        "discarded_lower_bits":
            discarded_bits,

        "address_method":
            (
                "exact_value"
                if not compressed
                else "upper_16_bits"
            ),

        "representative_method":
            (
                "log_distribution_mean"
                if result["feature_skew"] >= 2.0
                else
                "raw_log_distribution_blend"
                if result["feature_skew"] >= 1.0
                else
                "raw_distribution_mean"
            ),

        "post_transform":
            "log1p_then_minmax",

        "lut_file":
            str(lut_file),
    }

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    nonempty = np.count_nonzero(
        result["sample_counts"]
    )

    print(
        f"Min              : "
        f"{result['min_value']:,}"
    )

    print(
        f"Max              : "
        f"{result['max_value']:,}"
    )

    print(
        f"Skewness         : "
        f"{result['feature_skew']:.4f}"
    )

    print(
        f"Original bits    : "
        f"{result['original_bits']}"
    )

    print(
        f"LUT bits         : "
        f"{result['lut_bits']}"
    )

    print(
        f"Buckets          : "
        f"{result['bucket_count']:,}"
    )

    print(
        f"Non-empty        : "
        f"{nonempty:,}"
    )

    print(
        f"Representative   : "
        f"{metadata[feature]['representative_method']}"
    )

    print(
        f"Discarded bits   : "
        f"{discarded_bits}"
    )


# ============================================================
# SAVE SCALED DATASET
# ============================================================

scaled_df.to_csv(
    OUTPUT_DATASET,
    index=False
)


# ============================================================
# SAVE METADATA
# ============================================================

with open(
    OUTPUT_METADATA,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=4
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 80)
print("DONE")
print("=" * 80)

print(
    f"\nScaled dataset:"
)

print(
    OUTPUT_DATASET
)

print(
    f"\nMetadata:"
)

print(
    OUTPUT_METADATA
)

print(
    f"\nLUT directory:"
)

print(
    OUTPUT_DIR
)

print("\nEvery feature now has:")
print("  - its own LUT")
print("  - its own bucket/address space")
print("  - distribution-based bucket representatives")
print("  - log1p transformation")
print("  - MinMax normalization")

print("\nNo comparison between representative methods was performed.")