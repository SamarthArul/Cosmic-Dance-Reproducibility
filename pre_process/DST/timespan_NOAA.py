'''Extracting the duration of solar activity using the NOAA scales explanation:

NOAA categorizes geomagnetic storms into five classes:

G1 (Minor)
G2 (Moderate)
G3 (Strong)
G4 (Severe)
G5 (Extreme)

Source: https://www.swpc.noaa.gov/noaa-scales-explanation
'''


from cosmic_dance.dst_index import *
from cosmic_dance.io import *

DST_CSV = "artifacts/DST/Dst_index.csv"

# MILD
OUTPUT_MILD_FILE = "artifacts/DST/timespans/NOAA/MILD.csv"
MILD_LB = 50
MILD_UB = 100

# MODERERATE
OUTPUT_MODERERATE_FILE = "artifacts/DST/timespans/NOAA/MODERERATE.csv"
MODERERATE_LB = 101
MODERERATE_UB = 200

# SEVERE
OUTPUT_INTENSE_FILE = "artifacts/DST/timespans/NOAA/SEVERE.csv"
SEVERE_LB = 201
SEVERE_UB = 250

# EXTREME
OUTPUT_SUPER_FILE = "artifacts/DST/timespans/NOAA/EXTREME.csv"
EXTREME_LB = 251
EXTREME_UB = 1800


# Create the time windows of different scale
df_dst = read_dst_index_CSV(DST_CSV)
for lb, ub, filename in [
    (MILD_LB, MILD_UB, OUTPUT_MILD_FILE),
    (MODERERATE_LB, MODERERATE_UB, OUTPUT_MODERERATE_FILE),
    (SEVERE_LB, SEVERE_UB, OUTPUT_INTENSE_FILE),
    (EXTREME_LB, EXTREME_UB, OUTPUT_SUPER_FILE),
]:
    df = extract_timespan_between_nT_intensity(df_dst, lb, ub)
    export_as_csv(df, filename)
