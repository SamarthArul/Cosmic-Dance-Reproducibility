'''Measuring maximum altitude change over next few days after a solar event'''

import concurrent.futures

from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.measurement import maximum_altitude_difference
from cosmic_dance.TLEs import *

PARALLEL_MODE = False

# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/maximum_altitude_change"

# Quiet days
# OUTPUT_CSV = f"{OUTPUT_DIR}/quiet_day_after_1_5_10.csv"

# Solar event days
OUTPUT_CSV = f"{OUTPUT_DIR}/event_day_after_1_5_10.csv"


# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

# TLEs
TLE_CSV_DIR = "artifacts/OUTPUT/Starlink/TLEs"

# Dst index
# DST_TIMESPAN = "artifacts/OUTPUT/Starlink/timespans/quiet_day/merged_below_ptile_80.csv"
DST_TIMESPAN = "artifacts/OUTPUT/Starlink/timespans/percentile/merged_above_ptile_95.csv"


ONSERVATION_DAYS = [1, 5, 10]

# ------------------------------------------------------------------

create_directories(OUTPUT_DIR)

# Confirm write directory
input(f" OUTPUT FILE: ({OUTPUT_CSV}) is empty ?")


df_timespan = read_timespan_CSV(DST_TIMESPAN)

if PARALLEL_MODE:
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for id, event_date in enumerate(df_timespan[DST.STARTTIME]):
            print(
                f"|- [{id+1}/{len(df_timespan)}]  Starting from {event_date}..."
            )

            for filename in get_file_names(TLE_CSV_DIR):

                executor.submit(
                    maximum_altitude_difference,
                    event_date,
                    ONSERVATION_DAYS,
                    f"{TLE_CSV_DIR}/{filename}",
                    OUTPUT_CSV
                )

        executor.shutdown()

# Serial mode
else:

    for id, event_date in enumerate(df_timespan[DST.STARTTIME]):
        print(
            f"| - [{id+1}/{len(df_timespan)}]  Starting from {event_date}...  "
        )

        for filename in get_file_names(TLE_CSV_DIR):
            maximum_altitude_difference(
                event_date,
                ONSERVATION_DAYS,
                f"{TLE_CSV_DIR}/{filename}",
                OUTPUT_CSV
            )

print('|\n|- Complete.')
