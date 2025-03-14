'''
Extracting the duration of solar activity

- Above X %tile
- Merging two durations closer than Y days
'''

from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.stats import *
import os
import pandas as pd

# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

OUTPUT_DIR = "artifacts/OUTPUT/Starlink/timespans/percentile"

# Solar activity windows above the 80, 95, and 99 %tile
DST_TIMESPAN_PTILE_99 = f"{OUTPUT_DIR}/above_ptile_99.csv"
DST_TIMESPAN_PTILE_95 = f"{OUTPUT_DIR}/above_ptile_95.csv"
DST_TIMESPAN_PTILE_80 = f"{OUTPUT_DIR}/above_ptile_80.csv"

# Merging the solar activity windows closer than 10 days
MERGED_DST_TIMESPAN_PTILE_80 = f"{OUTPUT_DIR}/merged_above_ptile_80.csv"
MERGED_DST_TIMESPAN_PTILE_95 = f"{OUTPUT_DIR}/merged_above_ptile_95.csv"
MERGED_DST_TIMESPAN_PTILE_99 = f"{OUTPUT_DIR}/merged_above_ptile_99.csv"

# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

DST_CSV = "artifacts/DST/Dst_index.csv"

# ------------------------------------------------------------------

create_directories(OUTPUT_DIR)

# Above 80, 95, 99 %tile
df_dst = read_dst_index_CSV(DST_CSV)

for ptile, filename in [
    (99, DST_TIMESPAN_PTILE_99),
    (95, DST_TIMESPAN_PTILE_95),
    (80, DST_TIMESPAN_PTILE_80)
]:
    threshold = percentile(df_dst["nT"], ptile)
    print(f"percentile: {ptile}, {threshold}")

    df = extract_timespan_above_nT_intensity(df_dst, threshold)
    print(df.head())  # Debugging

    if df.empty:
        print(f"Warning: No data found for {ptile} percentile")
        # **Fix: Ensure CSV file contains column headers**
        pd.DataFrame(columns=["STARTTIME", "ENDTIME"]).to_csv(filename, index=False)
        continue  # Skip further processing

    print("Not empty")
    export_as_csv(df, filename)
    df = add_window_duration(df)
    export_as_csv(df, filename)

# Merge windows closer than 10 days (ONLY if files are non-empty)
# Merge windows closer than 10 days (ONLY if files are non-empty and valid)
for unmerged_fname, merged_fname in [
    (DST_TIMESPAN_PTILE_80, MERGED_DST_TIMESPAN_PTILE_80),
    (DST_TIMESPAN_PTILE_95, MERGED_DST_TIMESPAN_PTILE_95),
    (DST_TIMESPAN_PTILE_99, MERGED_DST_TIMESPAN_PTILE_99)
]:
    if not os.path.exists(unmerged_fname) or os.stat(unmerged_fname).st_size == 0:
        print(f"Skipping merge: {unmerged_fname} does not exist or is empty.")
        continue

    df = read_timespan_CSV(unmerged_fname)

    # Debugging: Ensure required columns exist
    print(f"Processing {unmerged_fname} - Columns found: {df.columns}")

    if "ENDTIME" not in df.columns or "STARTTIME" not in df.columns:
        print(f"Skipping merge: {unmerged_fname} is missing required columns.")
        continue

    df = merge_window(df, 10)
    export_as_csv(df, merged_fname)

