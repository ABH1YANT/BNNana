import pandas as pd

file_path = "datasets\\raw\\Monday-WorkingHours.pcap_ISCX.csv"  # Swap with whatever file you're testing

# nrows=3 tells Pandas to only load the first 3 lines of actual data.
# It automatically reads the very first line as the column titles.
df_peek = pd.read_csv(file_path, nrows=3)

# 1. Print the clean grid (Titles + 3 Rows)
print("--- THE DATA ---")
print(df_peek)

print("\n--- JUST THE TITLES (For easy copy-pasting) ---")
# 2. Dump just the titles into a clean list
columns_list = df_peek.columns.tolist()
for i, col in enumerate(columns_list):
    print(f"{i}: {col}")