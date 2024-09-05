'''Extracting the duration of low solar activity

- Below X %tile
- Merging two duration closer then Y days

'''


from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.stats import *

# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

OUTPUT_DIR = "artifacts/OUTPUT/Starlink/timespans/quiet_day"

# Intensity below 80 %tile for atleast 13 days
DST_TIMESPAN_PTILE_80 = f"{OUTPUT_DIR}/below_ptile_80.csv"
# Merging the solar activity window closer than 10 days
MERGED_DST_TIMESPAN_PTILE_80 = f"{OUTPUT_DIR}/merged_below_ptile_80.csv"


# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

DST_CSV = "artifacts/DST/Dst_index.csv"


# ------------------------------------------------------------------

create_directories(OUTPUT_DIR)


df_dst = read_dst_index_CSV(DST_CSV)

# Below 80 %tile
df = extract_timespan_below_nT_intensity(
    df_dst,
    percentile(df_dst[DST.NANOTESLA], 80)
)

# Filter duration above 13 days
df = add_window_duration(df)
df = df[df[DST.DURATION_HOURS] > 13*24]
export_as_csv(df, DST_TIMESPAN_PTILE_80)

# Merge windows closer than 10 days
df = read_timespan_CSV(DST_TIMESPAN_PTILE_80)
df = merge_window(df, 10)
export_as_csv(df, MERGED_DST_TIMESPAN_PTILE_80)
