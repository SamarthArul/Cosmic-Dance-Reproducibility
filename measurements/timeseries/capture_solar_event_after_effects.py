'''Measuring the satellite altitude change over next few days after a solar event'''

import concurrent.futures

from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def absolute_altitude_change(tle_csv_filename: str, event_date: pd.Timestamp, next_observation_days: int):
    '''Capture abrupt altitude change in next few dys immediately after a event date

    Params
    ------
    tle_csv_filename: str
        Filename of TLE file (NORAD_CAT_ID.csv)
    event_date: pd.Timestamp
        Solar event Timestamp
    next_observation_days: int
        Obervation window from solar event date
    '''

    # Output CSV filename
    OUTPUT_CSV = f"{OUTPUT_DIR}/{event_date.date()}.csv"

    # Timestamps of each date for next obervation window
    after_effect_dates = [
        event_date+pd.Timedelta(days=day)
        for day in range(1, next_observation_days)
    ]

    # Extract the NORAD_CAT_ID from filename and read all TLEs
    cat_id = int(tle_csv_filename.split(".")[0])
    df_tles = read_TLEs_in_CSV(f"{TLE_CSV_DIR}/{tle_csv_filename}")

    # Skip the satellite if already started decay (no TLE found before the date)
    last_tle = get_last_TLE_before_the_date(df_tles, event_date)
    if last_tle is None:
        return

    median_altitude_before_event = get_median_altitude(df_tles, event_date)
    altitude_change = abs(
        median_altitude_before_event-last_tle.get(TLE.ALTITUDE_KM)
    )

    # Skip if already started decay
    if altitude_change >= ALTITUDE_THERSHOLD:
        print(f"|-- [{event_date.date()}] {cat_id} Natural decay.")
        return

    # When the satellite are not started decay
    print(f"|-- [{event_date.date()}] {cat_id} Testing after effects...")

    # Record of the EVENT DATE
    CSV_logger(
        {
            "CAT_ID": cat_id,
            "DAYS": 0,
            "EPOCH": last_tle.get(TLE.EPOCH),
            "MEDIAN_BEFORE": median_altitude_before_event,
            "ALTITUDE_CHANGE_KM": altitude_change,
            "nT": get_records_by_date(
                DF_NT, DST.TIMESTAMP, event_date
            )[DST.NANOTESLA].max(),
        },
        OUTPUT_CSV
    )

    # Record of after effects in next few days from the EVENT DATE
    for day_id, after_effect_date in enumerate(after_effect_dates):
        # print(day_id+1, after_effect_date)

        # Get the first TLEs of the satellite after each next days
        # And measure the altitude changes from the EVENT DATE
        tle_after = get_first_TLE_after_the_date(df_tles, after_effect_date)
        if tle_after is not None:
            CSV_logger(
                {
                    "CAT_ID": cat_id,
                    "DAYS": day_id+1,
                    "EPOCH": tle_after.get(TLE.EPOCH),
                    "MEDIAN_BEFORE": median_altitude_before_event,
                    "ALTITUDE_CHANGE_KM": abs(
                        median_altitude_before_event -
                        tle_after.get(TLE.ALTITUDE_KM)
                    ),
                    "nT": get_records_by_date(
                        DF_NT, DST.TIMESTAMP, after_effect_date
                    )[DST.NANOTESLA].max(),
                },
                OUTPUT_CSV
            )


if __name__ == '__main__':
    PARALLEL_MODE = True

    ALTITUDE_THERSHOLD = 5
    # DAYS = 15
    DAYS = 30

    # OUTPUT directory
    # OUTPUT_DIR = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/solar_events/absolute_altitude_change/quiet_day"
    OUTPUT_DIR = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/solar_events/absolute_altitude_change/merged_above_ptile_99/RAW"

    # Event dates for Quiet day(s) or Solar event day(s)
    # EVENT_DATES = [pd.to_datetime("2021-06-16"),]
    # EVENT_DATE = [pd.to_datetime("2024-03-03"),]
    # EVENT_DATES_CSV = "artifacts/DST/timespans/quiet_day/below_ptile_80.csv"
    EVENT_DATES_CSV = "artifacts/DST/timespans/percentile/merged_above_ptile_99.csv"

    # TLEs and DST files
    TLE_CSV_DIR = "/mnt/Storage/OUTPUTs/Starlink/TLEs"
    DST_CSV = "artifacts/DST/Dst_index.csv"

    # Confirm inputs
    input(f"{OUTPUT_DIR} is empty? ")
    input(f"EVENT_DATES_CSV: {EVENT_DATES_CSV}?")

    # Read DST index and Get TLEs CSV file of each satellites and event dates
    DF_NT = read_dst_index_CSV(DST_CSV)
    CAT_ID_CSVS = get_file_names(TLE_CSV_DIR)
    EVENT_DATES = read_timespan_CSV(EVENT_DATES_CSV)[DST.STARTTIME]

    # Test after effect on each satellites

    if PARALLEL_MODE:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            for event_date in EVENT_DATES:
                print(f"|- Starting: {event_date.date()}")

                for cat_id_csv in CAT_ID_CSVS:
                    executor.submit(
                        absolute_altitude_change, cat_id_csv, event_date, DAYS
                    )

            executor.shutdown()

    # Serial mode
    else:
        for event_date in EVENT_DATES:
            for cat_id_csv in CAT_ID_CSVS:
                absolute_altitude_change(
                    cat_id_csv, event_date, DAYS
                )

    print('|\n|- Complete.')
