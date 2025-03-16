'''Extracting the duration of solar activity

- Above X %tile
- Merging two duration closer then Y days

'''


from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.stats import *

# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

OUTPUT_DIR = "artifacts/OUTPUT/Starlink/timespans/percentile"


# Solar activity window above the 80, 95, and 99 %tile
DST_TIMESPAN_PTILE_99 = f"{OUTPUT_DIR}/above_ptile_99.csv"
DST_TIMESPAN_PTILE_95 = f"{OUTPUT_DIR}/above_ptile_95.csv"
DST_TIMESPAN_PTILE_80 = f"{OUTPUT_DIR}/above_ptile_80.csv"

# Merging the solar activity window closer than 10 days
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
    print(f'''percentile: {ptile}, {percentile(df_dst["nT"], ptile)}''')
    df = extract_timespan_above_nT_intensity(
        df_dst, percentile(df_dst["nT"], ptile)
    )
    df = add_window_duration(df)
    export_as_csv(df, filename)

# Merge windows closer than 10 days
for unmerged_fname, merged_fname in [
    (DST_TIMESPAN_PTILE_80, MERGED_DST_TIMESPAN_PTILE_80),
    (DST_TIMESPAN_PTILE_95, MERGED_DST_TIMESPAN_PTILE_95),
    (DST_TIMESPAN_PTILE_99, MERGED_DST_TIMESPAN_PTILE_99)
]:
    df = read_timespan_CSV(unmerged_fname)
    df = merge_window(df, 10)
    export_as_csv(df, merged_fname)