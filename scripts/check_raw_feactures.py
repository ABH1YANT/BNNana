from pathlib import Path
import pandas as pd
import numpy as np

# ================================================================
# CONFIGURATION
# ================================================================

ROOT = Path(r"C:\Users\DELL\Desktop\BNNana")
DATA_PATH = ROOT / "datasets" / "processed" / "master_dataset.csv"

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
    "Fwd Header Length"
]

# Percentiles we want to inspect
PERCENTILES = [50, 90, 95, 99, 99.9, 99.99, 100]


# ================================================================
# BIT CALCULATION
# ================================================================

def bits_required(value):
    """
    Number of unsigned bits required to represent values
    from 0 up to 'value'.
    """
    value = int(np.ceil(value))

    if value <= 0:
        return 1

    return int(np.ceil(np.log2(value + 1)))


# ================================================================
# LOAD DATASET
# ================================================================

print("=" * 110)
print("LOADING MASTER DATASET")
print("=" * 110)

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

print(f"Dataset shape : {df.shape}")
print(f"Rows          : {len(df):,}")

# Make sure all features are numeric
for feature in FEATURES:
    df[feature] = pd.to_numeric(df[feature], errors="coerce")


# ================================================================
# BASIC STATISTICS + PERCENTILES + BIT WIDTH
# ================================================================

results = []

for feature in FEATURES:

    x = df[feature].dropna()

    skew = x.skew()

    row = {
        "Feature": feature,
        "Min": x.min(),
        "Max": x.max(),
        "Mean": x.mean(),
        "Median": x.median(),
        "Std": x.std(),
        "Skewness": skew,
        "Unique": x.nunique(),
        "Zeros": (x == 0).sum(),
        "Negative": (x < 0).sum(),
    }

    # Percentiles
    for p in PERCENTILES:
        value = np.percentile(x, p)

        if p == 100:
            name = "P100_Max"
        else:
            name = f"P{str(p).replace('.', '_')}"

        row[name] = value

        # Bits needed at this percentile
        row[f"{name}_Bits"] = bits_required(value)

    results.append(row)

stats = pd.DataFrame(results)


# ================================================================
# BASIC STATISTICS
# ================================================================

print("\n")
print("=" * 110)
print("BASIC STATISTICS")
print("=" * 110)

display_cols = [
    "Feature",
    "Min",
    "Max",
    "Mean",
    "Median",
    "Std",
    "Skewness",
    "Unique",
    "Zeros",
    "Negative"
]

print(stats[display_cols].to_string(index=False))


# ================================================================
# PERCENTILE TABLE
# ================================================================

print("\n")
print("=" * 110)
print("PERCENTILE DISTRIBUTION")
print("=" * 110)

for _, row in stats.iterrows():

    print("\n" + "-" * 100)
    print(row["Feature"])
    print("-" * 100)

    for p in PERCENTILES:

        if p == 100:
            name = "P100_Max"
            label = "MAX"
        else:
            name = f"P{str(p).replace('.', '_')}"
            label = f"P{p}%"

        value = row[name]
        bits = row[f"{name}_Bits"]

        print(
            f"{label:<8} : "
            f"{value:>18,.2f}    "
            f"Bits required: {bits:>2}"
        )


# ================================================================
# COMPACT BIT-WIDTH TABLE
# ================================================================

print("\n")
print("=" * 110)
print("EFFECTIVE BIT-WIDTH COMPARISON")
print("=" * 110)

bit_cols = ["Feature"]

for p in PERCENTILES:
    if p == 100:
        bit_cols.append("P100_Max_Bits")
    else:
        bit_cols.append(f"P{str(p).replace('.', '_')}_Bits")

print(
    stats[bit_cols].to_string(index=False)
)


# ================================================================
# SKEWNESS + P99.9 + MAX
# ================================================================

print("\n")
print("=" * 110)
print("SKEWNESS / EFFECTIVE RANGE SUMMARY")
print("=" * 110)

summary = stats[
    [
        "Feature",
        "Skewness",
        "P95",
        "P95_Bits",
        "P99",
        "P99_Bits",
        "P99_9",
        "P99_9_Bits",
        "P100_Max",
        "P100_Max_Bits"
    ]
].copy()

print(summary.to_string(index=False))


# ================================================================
# SAVE RESULTS
# ================================================================

OUTPUT_FILE = ROOT / "artifacts" / "master_feature_statistics.csv"

stats.to_csv(OUTPUT_FILE, index=False)

print("\n")
print("=" * 110)
print("DONE")
print("=" * 110)
print(f"Statistics saved to:")
print(OUTPUT_FILE)