# ============================================================
# BNNana
# Distribution-Based LUT Generation
#
# Each selected feature gets its own LUT.
#
# FEATURE SELECTION:
#     Read directly from:
#         artifacts/selected_features.json
#
# LUT BIT WIDTH:
#     Default:
#         <= 16 bits -> keep original width
#         > 16 bits  -> compress to 16 bits
#
#     Additional intentional compression:
#         Min Packet Length          -> 10 bits
#         min_seg_size_forward       -> 10 bits
#
#         Bwd Packet Length Max      -> 12 bits
#         Destination Port           -> 12 bits
#         Fwd Packet Length Max      -> 12 bits
#         Max Packet Length          -> 12 bits
#         Total Backward Packets     -> 12 bits
#         Subflow Bwd Packets        -> 12 bits
#
# ADDRESSING:
#     The UPPER target_bits are kept.
#     Lower bits are discarded.
#
# Representative:
#     chosen from the DISTRIBUTION inside each bucket
#     (not simply median for every feature)
#
# After representative selection:
#     log1p()
#     MinMax -> [0,1]
#
# Existing:
#     scaled_dataset.csv
#     LUT CSV files
#     lut_metadata.json
#
# are regenerated/overwritten.
#
# Other artifacts are NOT modified.
# ============================================================

import json
import numpy as np
import pandas as pd

from pathlib import Path
from scipy.stats import skew


# ============================================================
# PATHS
# ============================================================

ROOT = Path(
    r"C:\Users\DELL\Desktop\BNNana"
)

INPUT_FILE = (
    ROOT
    / "datasets"
    / "processed"
    / "master_dataset.csv"
)

# ------------------------------------------------------------
# SELECTED FEATURES JSON
# ------------------------------------------------------------

SELECTED_FEATURES_FILE = (
    ROOT
    / "artifacts"
    / "selected_features.json"
)

# ------------------------------------------------------------
# LUT OUTPUT DIRECTORY
# ------------------------------------------------------------

OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "feature_luts"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ------------------------------------------------------------
# SCALED DATASET
# ------------------------------------------------------------

OUTPUT_DATASET = (
    ROOT
    / "datasets"
    / "processed"
    / "scaled_dataset.csv"
)

# ------------------------------------------------------------
# LUT METADATA
# ------------------------------------------------------------

OUTPUT_METADATA = (
    ROOT
    / "artifacts"
    / "lut_metadata.json"
)


# ============================================================
# INTENTIONAL FEATURE COMPRESSION
# ============================================================
#
# These features are deliberately reduced even though some
# of them are already <= 16 bits.
#
# If a selected feature is NOT listed here:
#
#     <=16 original bits -> keep original width
#     >16 original bits  -> use 16 bits
#
# ============================================================

TARGET_LUT_BITS = {

    # 11 -> 10
    "Min Packet Length": 10,
    "min_seg_size_forward": 10,

    # Compress to 12 bits
    "Bwd Packet Length Max": 12,
    "Destination Port": 12,
    "Fwd Packet Length Max": 12,
    "Max Packet Length": 12,
    "Total Backward Packets": 12,
    "Subflow Bwd Packets": 12,
}


# ============================================================
# LOAD SELECTED FEATURES
# ============================================================

def load_selected_features(json_file):

    print("\nLoading selected features:")
    print(json_file)

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    # --------------------------------------------------------
    # Format 1:
    #
    # [
    #     "Feature A",
    #     "Feature B"
    # ]
    # --------------------------------------------------------

    if isinstance(data, list):

        features = data

    # --------------------------------------------------------
    # Format 2:
    #
    # {
    #     "selected_features": [
    #         "Feature A",
    #         "Feature B"
    #     ]
    # }
    # --------------------------------------------------------

    elif isinstance(data, dict):

        if (
            "selected_features" in data
            and isinstance(
                data["selected_features"],
                list
            )
        ):

            features = data["selected_features"]

        # ----------------------------------------------------
        # Format 3:
        #
        # {
        #     "Feature A": {...},
        #     "Feature B": {...}
        # }
        #
        # Feature names are the dictionary keys.
        # ----------------------------------------------------

        elif all(
            isinstance(k, str)
            for k in data.keys()
        ):

            features = list(
                data.keys()
            )

        else:

            raise ValueError(
                "Unsupported selected_features.json format."
            )

    else:

        raise ValueError(
            "Unsupported selected_features.json format."
        )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    features = [
        str(feature)
        for feature in features
    ]

    if len(features) == 0:

        raise ValueError(
            "selected_features.json contains no features."
        )

    # Remove duplicates while preserving order

    features = list(
        dict.fromkeys(features)
    )

    print(
        f"\nSelected features: {len(features)}"
    )

    for i, feature in enumerate(
        features,
        start=1
    ):

        print(
            f"  {i:2d}. {feature}"
        )

    return features


# ============================================================
# BIT WIDTH
# ============================================================

def get_bit_width(max_value):

    max_value = int(
        max_value
    )

    if max_value <= 0:

        return 1

    return int(
        np.ceil(
            np.log2(
                max_value + 1
            )
        )
    )


# ============================================================
# DETERMINE TARGET LUT WIDTH
# ============================================================

def get_target_lut_bits(
    feature_name,
    original_bits
):

    # --------------------------------------------------------
    # Explicit compression target
    # --------------------------------------------------------

    if feature_name in TARGET_LUT_BITS:

        requested_bits = int(
            TARGET_LUT_BITS[
                feature_name
            ]
        )

        # Never allow target width to be greater
        # than the original representation.

        return min(
            requested_bits,
            original_bits
        )

    # --------------------------------------------------------
    # Existing/default rule
    # --------------------------------------------------------

    return min(
        original_bits,
        16
    )


# ============================================================
# CREATE LUT ADDRESS
# ============================================================

def make_addresses(
    values,
    original_bits,
    lut_bits
):

    values = np.asarray(
        values,
        dtype=np.int64
    )

    # --------------------------------------------------------
    # Number of lower bits to discard
    # --------------------------------------------------------

    discarded_bits = max(
        original_bits - lut_bits,
        0
    )

    # --------------------------------------------------------
    # No compression
    # --------------------------------------------------------

    if discarded_bits == 0:

        addresses = values

    # --------------------------------------------------------
    # Compression
    #
    # Keep upper lut_bits.
    # --------------------------------------------------------

    else:

        addresses = (
            values.astype(np.uint64)
            >> discarded_bits
        )

    # --------------------------------------------------------
    # Valid address range
    # --------------------------------------------------------

    max_address = (
        (1 << lut_bits) - 1
    )

    addresses = np.clip(
        addresses,
        0,
        max_address
    )

    return addresses.astype(
        np.int64
    )


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

    Strong right skew:
        log-domain mean

    Moderate skew:
        25% raw mean
        75% log-domain mean

    Low skew:
        raw mean
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

        log_values = np.log1p(
            values
        )

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
    # Low skew
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

    # --------------------------------------------------------
    # NEW:
    # Determine target width
    # --------------------------------------------------------

    lut_bits = get_target_lut_bits(
        feature_name,
        original_bits
    )

    # --------------------------------------------------------
    # LUT bucket count
    # --------------------------------------------------------

    bucket_count = (
        1 << lut_bits
    )

    # --------------------------------------------------------
    # Bits discarded
    # --------------------------------------------------------

    discarded_bits = max(
        original_bits - lut_bits,
        0
    )

    compressed = (
        discarded_bits > 0
    )

    # --------------------------------------------------------
    # Feature skew
    # --------------------------------------------------------

    feature_skew = float(
        skew(values)
    )

    if not np.isfinite(
        feature_skew
    ):

        feature_skew = 0.0

    # --------------------------------------------------------
    # Addresses
    # --------------------------------------------------------

    addresses = make_addresses(
        values,
        original_bits,
        lut_bits
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

        sample_counts[
            bucket
        ] = len(
            bucket_values
        )

        # ----------------------------------------------------
        # Non-empty bucket
        # ----------------------------------------------------

        if len(
            bucket_values
        ) > 0:

            representatives[
                bucket
            ] = choose_representative(
                bucket_values,
                feature_skew
            )

        # ----------------------------------------------------
        # Empty bucket
        # ----------------------------------------------------

        else:

            # ------------------------------------------------
            # Determine the raw range represented by
            # this LUT address.
            # ------------------------------------------------

            if discarded_bits == 0:

                # Exact raw value

                representatives[
                    bucket
                ] = bucket

            else:

                # ------------------------------------------------
                # Example:
                #
                # 16 -> 12 bits
                #
                # bucket 100 means raw values:
                #
                # 100 << 4
                # through
                # ((101 << 4) - 1)
                #
                # ------------------------------------------------

                low = (
                    bucket
                    << discarded_bits
                )

                high = (
                    (
                        (bucket + 1)
                        << discarded_bits
                    )
                    - 1
                )

                representatives[
                    bucket
                ] = (
                    low + high
                ) / 2.0

    # ========================================================
    # Handle invalid LUT values
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
    # Apply LOG1P
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
            log_values
            - log_min
        ) / (
            log_max
            - log_min
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

        "addresses":
            addresses,

        "representatives":
            representatives,

        "log_values":
            log_values,

        "normalized_values":
            normalized_values,

        "sample_counts":
            sample_counts,

        "min_value":
            min_value,

        "max_value":
            max_value,

        "original_bits":
            original_bits,

        "lut_bits":
            lut_bits,

        "bucket_count":
            bucket_count,

        "feature_skew":
            feature_skew,

        "discarded_bits":
            discarded_bits,

        "compressed":
            compressed,

        "transformed_values":
            transformed_values,
    }


# ============================================================
# LOAD SELECTED FEATURES
# ============================================================

FEATURES = load_selected_features(
    SELECTED_FEATURES_FILE
)


# ============================================================
# LOAD DATASET
# ============================================================

print("\n")
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
# VALIDATE FEATURES
# ============================================================

missing_features = [
    feature
    for feature in FEATURES
    if feature not in df.columns
]

if missing_features:

    print("\nERROR: The following selected features")
    print("are missing from master_dataset.csv:\n")

    for feature in missing_features:

        print(
            f"  - {feature}"
        )

    raise ValueError(
        "Selected features do not match dataset columns."
    )


# ============================================================
# PROCESS FEATURES
# ============================================================

scaled_df = df.copy()

metadata = {}

# Summary table

summary_rows = []


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

    scaled_df[
        feature
    ] = (
        result[
            "transformed_values"
        ]
        .astype(np.float32)
    )

    # --------------------------------------------------------
    # Safe filename
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

    # --------------------------------------------------------
    # Save LUT
    # --------------------------------------------------------

    lut_df = pd.DataFrame({

        "bucket":
            np.arange(
                result[
                    "bucket_count"
                ]
            ),

        "representative_raw":
            result[
                "representatives"
            ],

        "log_value":
            result[
                "log_values"
            ],

        "normalized_value":
            result[
                "normalized_values"
            ],

        "sample_count":
            result[
                "sample_counts"
            ],
    })

    lut_df.to_csv(
        lut_file,
        index=False
    )

    # --------------------------------------------------------
    # Address method
    # --------------------------------------------------------

    if result["discarded_bits"] == 0:

        address_method = (
            "exact_value"
        )

    else:

        address_method = (
            "upper_bits"
        )

    # --------------------------------------------------------
    # Representative method
    # --------------------------------------------------------

    if result["feature_skew"] >= 2.0:

        representative_method = (
            "log_distribution_mean"
        )

    elif result["feature_skew"] >= 1.0:

        representative_method = (
            "raw_log_distribution_blend"
        )

    else:

        representative_method = (
            "raw_distribution_mean"
        )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

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
            result["compressed"],

        "discarded_lower_bits":
            result["discarded_bits"],

        "address_method":
            address_method,

        "representative_method":
            representative_method,

        "post_transform":
            "log1p_then_minmax",

        "lut_file":
            str(lut_file),
    }

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    nonempty = np.count_nonzero(
        result[
            "sample_counts"
        ]
    )

    summary_rows.append({

        "Feature":
            feature,

        "Max Value":
            result["max_value"],

        "Original Bits":
            result["original_bits"],

        "LUT Bits":
            result["lut_bits"],

        "Buckets":
            result["bucket_count"],

        "Discarded Bits":
            result["discarded_bits"],

        "Non-empty Buckets":
            nonempty,

        "Compressed":
            result["compressed"],
    })

    # --------------------------------------------------------
    # Print feature result
    # --------------------------------------------------------

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
        f"{representative_method}"
    )

    print(
        f"Discarded bits   : "
        f"{result['discarded_bits']}"
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
# FINAL COMPRESSION TABLE
# ============================================================

summary_df = pd.DataFrame(
    summary_rows
)

print("\n")
print("=" * 100)
print("FINAL FEATURE COMPRESSION TABLE")
print("=" * 100)

print(
    summary_df.to_string(
        index=False
    )
)


# ============================================================
# BIT SUMMARY
# ============================================================

total_original_bits = (
    summary_df[
        "Original Bits"
    ].sum()
)

total_lut_bits = (
    summary_df[
        "LUT Bits"
    ].sum()
)

total_discarded_bits = (
    summary_df[
        "Discarded Bits"
    ].sum()
)

if total_original_bits > 0:

    reduction_percent = (
        total_discarded_bits
        /
        total_original_bits
        *
        100
    )

else:

    reduction_percent = 0.0


print("\n")
print("=" * 80)
print("OVERALL BIT REDUCTION")
print("=" * 80)

print(
    f"Original total bits : "
    f"{total_original_bits}"
)

print(
    f"Final LUT bits      : "
    f"{total_lut_bits}"
)

print(
    f"Bits discarded      : "
    f"{total_discarded_bits}"
)

print(
    f"Reduction           : "
    f"{reduction_percent:.2f}%"
)


# ============================================================
# OUTPUT LOCATIONS
# ============================================================

print("\n")
print("=" * 80)
print("DONE")
print("=" * 80)

print(
    "\nScaled dataset:"
)

print(
    OUTPUT_DATASET
)

print(
    "\nMetadata:"
)

print(
    OUTPUT_METADATA
)

print(
    "\nLUT directory:"
)

print(
    OUTPUT_DIR
)

print("\nSelected features source:")
print(
    SELECTED_FEATURES_FILE
)

print("\nEvery selected feature now has:")
print("  - its own LUT")
print("  - its own address width")
print("  - distribution-based bucket representatives")
print("  - log1p transformation")
print("  - MinMax normalization")

print("\nExisting LUT files are overwritten.")
print("scaled_dataset.csv is overwritten.")
print("lut_metadata.json is overwritten.")
print("No other artifacts are modified.")