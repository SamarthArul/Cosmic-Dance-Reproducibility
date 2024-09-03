'''Measuring maximum altitude change over next few days after a solar event'''

import concurrent.futures
import math

from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def compute_absolute_change(
        event_date: pd.Timestamp,
        observation_days: list[int],

        tle_filename: str,
        out_filename: str,

        change_thershold: float = 5.0
):
    '''Measure absolute altitude change of a given satellite by next a few observation days

    Params
    ------
    event_date: pd.Timestamp
        Timestamp of start date
    observation_days: list[int]
        Observation window length in days from start date
    tle_filename: str
        TLE CSV file name
    out_filename: str
        Output CSV file name
    change_thershold: float, optional
        Altitude change thershold (Default 0.5 KM)

    '''

    df_tle = read_TLEs_in_CSV(tle_filename)
    tle_before_dict = get_last_TLE_before_the_date(df_tle, event_date)

    # If not last TLE not found skip this satellite
    # If already altitude changed (way below median) a lot then skip this satellite
    if tle_before_dict is None:
        return
    median_altitude_before_event = get_median_altitude(df_tle, event_date)
    if math.isnan(median_altitude_before_event):
        return
    if abs(median_altitude_before_event-tle_before_dict.get(TLE.ALTITUDE_KM)) >= change_thershold:
        return

    # Build a record
    record = {
        "EVENT_DATE": event_date,
        "NORAD_CAT_ID": tle_before_dict.get(TLE.NORAD_CAT_ID),
        "LAUNCH_DATE": tle_before_dict.get(TLE.LAUNCH_DATE),
    }

    # Measure the altitude change over next few days
    for day_count in observation_days:
        end_date = event_date+pd.Timedelta(days=day_count)

        # Get the first TLE after the edate
        tle_after_dict = get_first_TLE_after_the_date(df_tle, end_date)

        # The satellite disappeared i.e, no TLEs after end_date
        if tle_after_dict is None:
            record[f"KM_after_DAY_{day_count}"] = 0
            print(
                f"""|- {tle_before_dict.get(TLE.NORAD_CAT_ID)} Gone after {event_date}"""
            )
            continue

        # If not disappeared then get all the TLEs within that window (event_date to end_date)
        df_tle_after_effect = get_all_TLE_between_two_date(
            df_tle,
            tle_before_dict.get(TLE.EPOCH),
            tle_after_dict.get(TLE.EPOCH)
        )

        # Take the absolute drag and altitude difference
        absolute_drag = df_tle_after_effect[TLE.DRAG].abs()
        absolute_altitude_change = (
            median_altitude_before_event - df_tle_after_effect[TLE.ALTITUDE_KM]
        ).abs()

        # Add the measurement to the record
        record[f"KM_after_DAY_{day_count}"] = absolute_altitude_change.max()
        record[f"DRAG_after_DAY_{day_count}"] = absolute_drag.max()

    CSV_logger(record, out_filename)


if __name__ == '__main__':

    PARALLEL_MODE = True

    ONSERVATION_DAYS = [1, 5, 10]

    # Quiet days
    # OUTPUT_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/measure_decay/quiet_day_after_1_5_10.csv"
    # TLE_CSV_DIR = "/mnt/Storage/OUTPUTs/Starlink/TLEs"
    # DST_TIMESPAN = "artifacts/DST/timespans/quiet_day/merged_below_ptile_80.csv"

    # Solar event days
    OUTPUT_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/measure_decay/event_day_after_1_5_10.csv"
    TLE_CSV_DIR = "/mnt/Storage/OUTPUTs/Starlink/TLEs"
    DST_TIMESPAN = "artifacts/DST/timespans/percentile/merged_above_ptile_95.csv"

    # Confirm write directory
    input(f"{OUTPUT_CSV} is empty ?")

    df_timespan = read_timespan_CSV(DST_TIMESPAN)

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
