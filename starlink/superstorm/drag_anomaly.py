'''Measuring satellite drag anomalies and statistics over few days'''

import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *
from cosmic_dance.measurement import generate_drag_insight


PARALLEL_MODE = True

# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/drag_anomaly"

# OUTPUT CSV file name
DRAG_OBSERVED_CSV = f"{OUTPUT_DIR}/drag_observed.csv"
POSITIVE_DRAG_OBSERVED_CSV = f"{OUTPUT_DIR}/positive_drag_observed.csv"

# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

TLE_DIR_CSV = "artifacts/OUTPUT/Starlink/TLEs"

# Event start date and next observation days
START_DATE = pd.to_datetime("2024-05-01 00:00:00")
UPTO_NEXT_DAYS = 30

# ------------------------------------------------------------------

recreate_directories(OUTPUT_DIR)

df_tles = get_merged_TLEs_from_all_CSVs(TLE_DIR_CSV)

if PARALLEL_MODE:
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for i in range(UPTO_NEXT_DAYS+1):
            query_date = START_DATE+pd.Timedelta(days=i)

            executor.submit(
                generate_drag_insight,
                get_records_by_date(df_tles, TLE.EPOCH, query_date),
                query_date,
                DRAG_OBSERVED_CSV,
                POSITIVE_DRAG_OBSERVED_CSV
            )

        executor.shutdown()

# Serial mode
else:
    for i in range(UPTO_NEXT_DAYS+1):
        query_date = START_DATE+pd.Timedelta(days=i)

        generate_drag_insight(
            get_records_by_date(df_tles, TLE.EPOCH, query_date),
            query_date,
            DRAG_OBSERVED_CSV,
            POSITIVE_DRAG_OBSERVED_CSV
        )

print('|\n|- Complete.')
