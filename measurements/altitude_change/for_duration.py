'''Measuring maximum altitude change over next few days after a solar event of different duration'''

import concurrent.futures

from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.TLEs import *
from measurements.altitude_change.for_intensity import compute_absolute_change

if __name__ == '__main__':

    PARALLEL_MODE = True

    ONSERVATION_DAYS = [1, 5, 10]

    # Storm duration
    # OUTPUT_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/measure_decay/below_H9.csv"
    OUTPUT_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/measure_decay/above_H9.csv"
    TLE_CSV_DIR = "/mnt/Storage/OUTPUTs/Starlink/TLEs"
    DST_TIMESPAN = "artifacts/DST/timespans/percentile/merged_above_ptile_99.csv"

    # Confirm write directory
    input(f"{OUTPUT_CSV} is empty ?")

    df_timespan = read_timespan_CSV(DST_TIMESPAN)
    # df_timespan = df_timespan[df_timespan[DST.DURATION_HOURS] < 9]
    df_timespan = df_timespan[df_timespan[DST.DURATION_HOURS] > 9]

    if PARALLEL_MODE:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            for id, event_date in enumerate(df_timespan[DST.STARTTIME]):
                print(
                    f"|- [{id+1}/{len(df_timespan)}]  Starting from {event_date}..."
                )

                for filename in get_file_names(TLE_CSV_DIR):

                    executor.submit(
                        compute_absolute_change,
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
                compute_absolute_change(
                    event_date,
                    ONSERVATION_DAYS,
                    f"{TLE_CSV_DIR}/{filename}",
                    OUTPUT_CSV
                )

    print('|\n|- Complete.')
