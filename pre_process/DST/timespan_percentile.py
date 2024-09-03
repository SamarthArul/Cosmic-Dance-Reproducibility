'''Extracting the duration of solar activity

- Above X %tile
- Merging two duration closer then Y days

'''


from cosmic_dance.dst_index import *
from cosmic_dance.io import *


DST_CSV = "artifacts/DST/Dst_index.csv"

# Solar activity window above the 80, 95, and 99 %tile
DST_TIMESPAN_PTILE_99 = "artifacts/DST/timespans/percentile/above_ptile_99.csv"
DST_TIMESPAN_PTILE_95 = "artifacts/DST/timespans/percentile/above_ptile_95.csv"
DST_TIMESPAN_PTILE_80 = "artifacts/DST/timespans/percentile/above_ptile_80.csv"

df_dst = read_dst_index_CSV(DST_CSV)
for ptile, filename in [
    (99, DST_TIMESPAN_PTILE_99),
    (95, DST_TIMESPAN_PTILE_95),
    (80, DST_TIMESPAN_PTILE_80)
]:
    df = extract_timespan_above_nT_intensity(
        df_dst, percentile(df_dst["nT"], ptile)
    )
    df = add_window_duration(df)
    export_as_csv(df, filename)


# Merging the solar activity window closer than 10 days
MERGED_DST_TIMESPAN_PTILE_80 = "artifacts/DST/timespans/percentile/merged_above_ptile_80.csv"
MERGED_DST_TIMESPAN_PTILE_95 = "artifacts/DST/timespans/percentile/merged_above_ptile_95.csv"
MERGED_DST_TIMESPAN_PTILE_99 = "artifacts/DST/timespans/percentile/merged_above_ptile_99.csv"

for unmerged_fname, merged_fname in [
    (DST_TIMESPAN_PTILE_80, MERGED_DST_TIMESPAN_PTILE_80),
    (DST_TIMESPAN_PTILE_95, MERGED_DST_TIMESPAN_PTILE_95),
    (DST_TIMESPAN_PTILE_99, MERGED_DST_TIMESPAN_PTILE_99)
]:
    df = read_timespan_CSV(unmerged_fname)
    df = merge_window(df, 10)
    export_as_csv(df, merged_fname)
