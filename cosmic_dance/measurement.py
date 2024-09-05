
from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.stats import percentile
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


def maximum_altitude_difference(
    event_date: pd.Timestamp,
    observation_days: list[int],

    tle_filename: str,
    out_filename: str,

    change_thershold: float = 5.0
):
    '''Measure maximum altitude difference observed of a given satellite by next a few observation days

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


def generate_tracking_insight(
    df: pd.DataFrame,
    query_date: pd.Timestamp,
    sat_tracked_csv: str,
    tle_per_sat_csv: str
):
    '''Extracts number of satellites tracked and number of TLEs per satellites

    Params
    ------
    df: pd.DataFrame
        DataFrame of TLEs
    query_date: pd.Timestamp
        Timestamp of a day
    sat_tracked_csv: str
        CSV filename for number of satellite tracked
    tle_per_sat_csv: str
        CSV filename for number of TLEs per satellite tracked
    '''

    unique_cat_ids = get_unique_cat_ids(df)

    print(
        f'''|- [{query_date}] #TLEs: {len(df)} #Sats: {len(unique_cat_ids)}'''
    )

    # Total number of satellite tracked on that day (query_date)
    CSV_logger(
        {
            "DAY": query_date,
            "TOTAL_TLE_UPDATE": len(df),
            "UNIQUE_SAT": len(unique_cat_ids)
        },
        sat_tracked_csv
    )

    # Total number of TLEs per satellite on that day (query_date)
    for cat_id in unique_cat_ids:
        CSV_logger(
            {
                "DAY": query_date,
                "NORAD_CAT_ID": cat_id,
                "TOTAL_TLE": len(df[df[TLE.NORAD_CAT_ID] == cat_id])
            },
            tle_per_sat_csv
        )


def generate_drag_insight(
    df: pd.DataFrame,
    query_date: pd.Timestamp,
    drag_observation_csv: str,
    positive_drag_stats_csv: str
):
    '''Extract drag experienced by satellites, 
    negative (count be station keeping) and positive drags are segregated 
    and statistics of positive drag generated

    Params
    ------
    df: pd.DataFrame
        DataFrame of TLEs
    query_date: pd.Timestamp
        Timestamp of a day
    drag_observation_csv: str
        CSV filename for +ve and -ve drag obervation
    positive_drag_stats_csv: str
        CSV filename for statistics of +ve obervation
    '''

    df_positive = df[df[TLE.DRAG] > 0]
    df_negative = df[df[TLE.DRAG] < 0]
    df_zero = df[df[TLE.DRAG] == 0]

    print(
        f'''|- [{query_date}] #+ve DRAG: {len(df_positive)}  #-ve DRAG: {len(df_negative)}'''
    )

    # Total positive and negative drag observations
    CSV_logger(
        {
            "DAY": query_date,
            "TOTAL_TLE": len(df),
            "POSITIVE_DRAG": len(df_positive),
            "NEGATIVE_DRAG": len(df_negative),
            "ZERO_DRAG": len(df_zero),
        },
        drag_observation_csv
    )

    # Statistics of positive drag observations
    CSV_logger(
        {
            "DAY": query_date,
            "MEDIAN": df_positive["DRAG"].median(),
            "MEAN": df_positive["DRAG"].mean(),
            "MAX": df_positive["DRAG"].max(),
            "MIN": df_positive["DRAG"].min(),
            "P95": percentile(df_positive[TLE.DRAG], 95),
        },
        positive_drag_stats_csv
    )
