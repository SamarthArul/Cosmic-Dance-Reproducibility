from cosmic_dance.data_processor import *

DST_CSV = '/home/suvam/Projects/CosmicDance/CSVs/Dst_index.csv'
DST_TIMESPAN_PTILE_99 = '/home/suvam/Projects/CosmicDance/CSVs/PT_99.csv'


df_nt = read_dst_index_CSV(DST_CSV)

# Above 95%tile
ptile = percentile(df_nt["nT"], 99)
print(f'Ptile 99%: {ptile}')
df = extract_timespan_above_nT_intensity(df_nt, ptile)
write_CSV(df, DST_TIMESPAN_PTILE_99)
