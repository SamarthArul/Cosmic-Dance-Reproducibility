'''Measuring satellite drag anomalies and statistics over few days'''

import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *
from cosmic_dance.dst_index import percentile


def generate_drag_insight(df: pd.DataFrame, query_date: pd.Timestamp, drag_observation_csv: str, positive_drag_stats_csv: str):
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


if __name__ == "__main__":

    PARALLEL_MODE = True

    # OUTPUT CSV file name
    DRAG_OBSERVED_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/drag_anomaly/drag_observed.csv"
    POSITIVE_DRAG_OBSERVED_CSV = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/drag_anomaly/positive_drag_observed.csv"

    # Event start date and next observation days
    START_DATE = pd.to_datetime("2024-05-01 00:00:00")
    UPTO_NEXT_DAYS = 30

    TLE_DIR_CSV = "/mnt/Storage/OUTPUTs/Starlink/TLEs"

    # Validate the output file
    input(f"{DRAG_OBSERVED_CSV} is empty ? ")
    input(f"{POSITIVE_DRAG_OBSERVED_CSV} is empty ? ")

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
