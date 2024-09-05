from cosmic_dance.dst_index import *
from cosmic_dance.stack_plots import *
from cosmic_dance.TLEs import *


def plot_by_cat_id(df_nt: pd.DataFrame, df_tles: pd.DataFrame, cat_id: int):
    '''Helper method for calling plot_in_stack_with_nt()

    Plot time series with each satellite

    Params
    -------
    df_nt: pd.DataFrame
        Dst index data frame
    df_tles: pd.DataFrame
        TLEs data frame
    cat_id: int
        NORAD Catalog Number
    '''

    ldate = str(df_tles.iloc[-1]["LAUNCH_DATE"]).split(' ')[0]
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

    # ------------------------------------------------------------------
    # OUTPUT FILE(s)
    # ------------------------------------------------------------------

    PLOT_OUTPUT_DIR = "artifacts/OUTPUT/HawkEye_360/VIEW/RAW_CAT_ID"

    # ------------------------------------------------------------------
    # INPUT FILE(s)
    # ------------------------------------------------------------------

    # TLEs and DST files
    TLE_CSV_DIR = "artifacts/OUTPUT/HawkEye_360/TLEs"
    DST_CSV = "artifacts/DST/Dst_index.csv"

    START_DATE = pd.to_datetime("2024-04-01 00:00:00")
    END_DATE = pd.to_datetime("2024-06-01 00:00:00")
    TIME_DELTA = pd.Timedelta(days=2)

    # ------------------------------------------------------------------

    # Confirm
    input(f" File(s) in {PLOT_OUTPUT_DIR} might get altered? ")
    create_directories(PLOT_OUTPUT_DIR)

    # Reading CSVs
    df_nt = read_dst_index_CSV(DST_CSV)
    df_tles = get_merged_TLEs_from_all_CSVs(TLE_CSV_DIR)

    # Filtering
    if START_DATE is not None or END_DATE is not None:
        df_tles = get_all_TLE_between_two_date(df_tles, START_DATE, END_DATE)
        df_nt = df_nt[df_nt[DST.TIMESTAMP].between(START_DATE, END_DATE)]

    for cat_id in get_unique_cat_ids(df_tles):
        # Query TLEs by NORAD_CAT_ID
        df = get_TLEs_by_cat_id(df_tles, cat_id)
        plot_by_cat_id(df_nt, df, cat_id)
