'''Measuring how many satellite tracked and how many TLEs per satellite per days'''

import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def generate_tracking_insight(df: pd.DataFrame, query_date: pd.Timestamp, sat_tracked_csv: str, tle_per_sat_csv: str):
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
                "TOTAL_TLE": len(df[df["NORAD_CAT_ID"] == cat_id])
            },
            tle_per_sat_csv
        )


if __name__ == "__main__":

    PARALLEL_MODE = True

    # OUTPUT CSV file name
    SAT_TRACKED_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/tracking_anomaly/sat_tracked.csv"
    TLE_PER_SAT_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/tracking_anomaly/tle_per_sat.csv"

    # Event start date and next observation days
    START_DATE = pd.to_datetime("2024-05-01 00:00:00")
    UPTO_NEXT_DAYS = 30

    TLE_DIR_CSV = "/mnt/Storage/OUTPUTs/Starlink/TLEs"

    # Validate the output file
    input(f"{SAT_TRACKED_CSV} is empty ? ")
    input(f"{TLE_PER_SAT_CSV} is empty ? ")

    df_tles = get_merged_TLEs_from_all_CSVs(TLE_DIR_CSV)

    if PARALLEL_MODE:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            for i in range(UPTO_NEXT_DAYS+1):
                query_date = START_DATE+pd.Timedelta(days=i)

                executor.submit(
                    generate_tracking_insight,
                    get_records_by_date(df_tles, TLE.EPOCH, query_date),
                    query_date,
                    SAT_TRACKED_CSV,
                    TLE_PER_SAT_CSV
                )

            executor.shutdown()

    # Serial mode
    else:
        for i in range(UPTO_NEXT_DAYS+1):
            query_date = START_DATE+pd.Timedelta(days=i)

            generate_tracking_insight(
                get_records_by_date(df_tles, TLE.EPOCH, query_date),
                query_date,
                SAT_TRACKED_CSV,
                TLE_PER_SAT_CSV
            )

    print('|\n|- Complete.')
