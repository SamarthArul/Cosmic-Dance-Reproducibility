'''Trace the satellite altitude change over next few days after a solar event'''

import concurrent.futures

from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.measurement import track_satellite_altitude_change
from cosmic_dance.TLEs import *

PARALLEL_MODE = True


# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

# OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/track_altitude_change/quiet_day"
OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/track_altitude_change/merged_above_ptile_99/RAW"


# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------


# Event dates for Quiet day(s) or Solar event day(s)
# EVENT_DATES = [pd.to_datetime("2021-06-16"),]
# EVENT_DATES = [pd.to_datetime("2024-03-03"),]

# EVENT_DATES_CSV = "artifacts/OUTPUT/Starlink/timespans/quiet_day/below_ptile_80.csv"
EVENT_DATES_CSV = "artifacts/OUTPUT/Starlink/timespans/percentile/merged_above_ptile_99.csv"

# TLEs and DST files
TLE_CSV_DIR = "artifacts/OUTPUT/Starlink/TLEs"
DST_CSV = "artifacts/DST/Dst_index.csv"

# DAYS = 15
DAYS = 30

# ------------------------------------------------------------------


recreate_directories(OUTPUT_DIR)

# Read DST index and Get TLEs CSV file of each satellites and event dates
DF_DST = read_dst_index_CSV(DST_CSV)
CAT_ID_CSVS = get_file_names(TLE_CSV_DIR)
EVENT_DATES = read_timespan_CSV(EVENT_DATES_CSV)[DST.STARTTIME]


# Test after effect on each satellites

if PARALLEL_MODE:
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for event_date in EVENT_DATES:
            print(f"|- Starting: {event_date.date()}")
            for cat_id_csv in CAT_ID_CSVS:

                executor.submit(
                    track_satellite_altitude_change,

                    f"{OUTPUT_DIR}/{event_date.date()}.csv",
                    f"{TLE_CSV_DIR}/{cat_id_csv}",
                    DF_DST,
                    event_date,
                    DAYS
                )

        executor.shutdown()

# Serial mode
else:
    for event_date in EVENT_DATES:
        for cat_id_csv in CAT_ID_CSVS:

            track_satellite_altitude_change(
                f"{OUTPUT_DIR}/{event_date.date()}.csv",
                f"{TLE_CSV_DIR}/{cat_id_csv}",
                DF_DST,
                event_date,
                DAYS
            )

print('|\n|- Complete.')
