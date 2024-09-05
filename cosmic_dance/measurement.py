
from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def track_satellite_altitude_change(
    out_filename: str,
    tle_csv_filename: str,

    df_dst: pd.DataFrame,
    event_date: pd.Timestamp,
    next_observation_days: int,

    change_thershold: float = 5.0
):
    '''Capture abrupt altitude change over next few days immediately after a event date

    Params
    ------
    out_filename: str
        Output CSV file name
    tle_csv_filename: str
        Filename of TLE file (NORAD_CAT_ID.csv)
    df_dst: pd.DataFrame
        DataFrame of Dst indices
    event_date: pd.Timestamp
        Solar event Timestamp
    next_observation_days: int
        Obervation window from solar event date
    change_thershold: float, optional
        Altitude change thershold (Default 0.5 KM)
    '''

    # Read all TLEs
    df_tles = read_TLEs_in_CSV(tle_csv_filename)

    # Skip the satellite if already started decay (no TLE found before the date)
    last_tle = get_last_TLE_before_the_date(df_tles, event_date)
    if last_tle is None:
        return

    median_altitude_before_event = get_median_altitude(df_tles, event_date)
    altitude_change = abs(
        median_altitude_before_event-last_tle.get(TLE.ALTITUDE_KM)
    )

    # Skip if already started decay
    if altitude_change >= change_thershold:
        print(
            f"|-- [{event_date.date()}] {last_tle.get(TLE.NORAD_CAT_ID)} Natural decay."
        )
        return

    # When the satellite are not started decay
    print(
        f"|-- [{event_date.date()}] {last_tle.get(TLE.NORAD_CAT_ID)} Testing after effects..."
    )

    # Record of the EVENT DATE
    CSV_logger(
        {
            "CAT_ID": last_tle.get(TLE.NORAD_CAT_ID),
            "DAYS": 0,
            "EPOCH": last_tle.get(TLE.EPOCH),
            "MEDIAN_BEFORE": median_altitude_before_event,
            "ALTITUDE_CHANGE_KM": altitude_change,
            "nT": get_records_by_date(
                df_dst, DST.TIMESTAMP, event_date
            )[DST.NANOTESLA].max(),
        },
        out_filename
    )

    # Record of after effects in next few days from the EVENT DATE
    # Timestamps of each date for next obervation window
    for day_id in range(1, next_observation_days+1):
        after_effect_date = event_date+pd.Timedelta(days=day_id)

        # Get the first TLEs of the satellite after each next days
        # And measure the altitude changes from the EVENT DATE
        tle_after = get_first_TLE_after_the_date(df_tles, after_effect_date)
        if tle_after is not None:
            CSV_logger(
                {
                    "CAT_ID": tle_after.get(TLE.NORAD_CAT_ID),
                    "DAYS": day_id,
                    "EPOCH": tle_after.get(TLE.EPOCH),
                    "MEDIAN_BEFORE": median_altitude_before_event,
                    "ALTITUDE_CHANGE_KM": abs(
                        median_altitude_before_event -
                        tle_after.get(TLE.ALTITUDE_KM)
                    ),
                    "nT": get_records_by_date(
                        df_dst, DST.TIMESTAMP, after_effect_date
                    )[DST.NANOTESLA].max(),
                },
                out_filename
            )
