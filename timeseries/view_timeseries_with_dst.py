import concurrent.futures

from cosmic_dance.data_processor import *
from cosmic_dance.stack_plots import *


def plot_group_by_launch_date(df_nt: pd.DataFrame, df_tles: pd.DataFrame, ldate: pd.Timestamp) -> None:
    '''Helper method for calling plot_in_stack_with_nt()

    Params
    -------
    df_nt: pd.DataFrame
        Dst index data frame
    df_tles: pd.DataFrame
        TLEs data frame
    ldate: pd.Timestamp
        Launch date
    '''

    ldate = str(ldate).split('T')[0]
    title = f'Launch date: {ldate}'
    filename = f'{PLOT_OUTPUT_DIR}/{ldate}.png'

    filename = plot_in_stack_with_nt(
        df_tles=df_tles,
        df_nt=df_nt,

        sdate=START_DATE,
        edate=END_DATE,

        time_delta=TIME_DELTA,
        title=title,
        filename=filename
    )

    print(f'|- {filename}')


def plot_by_cat_id(df_nt: pd.DataFrame, df_tles: pd.DataFrame, cat_id: int) -> None:
    '''Helper method for calling plot_in_stack_with_nt()

    Params
    -------
    df_nt: pd.DataFrame
        Dst index data frame
    df_tles: pd.DataFrame
        TLEs data frame
    cat_id: int
        NORAD Catalog Number
    '''

    ldate = str(df_tles.iloc[-1]["LAUNCH_DATE"]).split('T')[0]
    title = f'CAT ID: {cat_id} || Launch date: {ldate}'
    filename = f'{PLOT_OUTPUT_DIR}/{cat_id}.png'

    filename = plot_in_stack_with_nt(
        df_tles=df_tles,
        df_nt=df_nt,

        sdate=START_DATE,
        edate=END_DATE,

        time_delta=TIME_DELTA,
        title=title,
        filename=filename
    )

    print(f'|- {filename}')


if __name__ == '__main__':
    # Output dir
    # PLOT_OUTPUT_DIR = '/mnt/Storage/OUTPUTs/Starlink/VIEW/SUPERSTORM'
    # PLOT_OUTPUT_DIR = '/mnt/Storage/OUTPUTs/Starlink/VIEW/RAW_LDATE'
    PLOT_OUTPUT_DIR = '/mnt/Storage/OUTPUTs/Starlink/VIEW/RAW_CAT_ID'

    # TLEs and DST files
    TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/Starlink/TLEs'
    DST_CSV = 'artifacts/DST/Dst_index.csv'

    # Start & end timen marking interval
    START_DATE = None
    END_DATE = None
    # START_DATE = pd.to_datetime("2024-04-01")
    # END_DATE = pd.to_datetime("2024-05-30")
    TIME_DELTA = timedelta(weeks=4)

    # Reading CSVs
    df_nt = read_dst_index_CSV(DST_CSV)
    df_tles = get_merged_TLEs_from_CSVs(TLE_DIR_CSV)

    # Filtering
    if START_DATE is not None or END_DATE is not None:
        df_tles = get_all_TLE_between_two_date(df_tles, START_DATE, END_DATE)
        df_nt = df_nt[df_nt["TIMESTAMP"].between(START_DATE, END_DATE)]

    with concurrent.futures.ProcessPoolExecutor() as executor:

        # ----------------------Batch by LAUNCH_DATE---------------------------
        # for ldate in get_unique_launch_dates(df_tles):
        #     # Query TLEs by LAUNCH_DATE
        #     df = df_tles[df_tles["LAUNCH_DATE"] == ldate]
        #     executor.submit(plot_group_by_launch_date, df_nt, df, ldate)
        # ---------------------------------------------------------------------

        # ----------------------Plot by NORAD Catalog Number-------------------
        for cat_id in get_unique_cat_ids(df_tles):
            # Query TLEs by NORAD_CAT_ID
            df = df_tles[df_tles["NORAD_CAT_ID"] == cat_id]
            executor.submit(plot_by_cat_id, df_nt, df, cat_id)
        # ---------------------------------------------------------------------

        executor.shutdown()
        print('|\n|- Complete.')
