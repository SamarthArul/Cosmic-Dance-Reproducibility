import concurrent.futures

from cosmic_dance.data_processor import *
from cosmic_dance.stack_plots import *


def plot(df_nt: pd.DataFrame, df_tles: pd.DataFrame, ldate: pd.Timestamp) -> str:

    ldate = str(ldate).split('T')[0]

    resp = plot_in_stack_ldate_with_nt(
        ldate,
        df_tles, df_nt,
        output_dir=PLOT_OUTPUT_DIR
    )

    return resp


if __name__ == '__main__':
    # PLOT_OUTPUT_DIR = '/mnt/Storage/OUTPUTs/VIEW/RAW_LDATE'
    PLOT_OUTPUT_DIR = '/mnt/Storage/OUTPUTs/VIEW/VALIDATE'

    DST_CSV = '/home/suvam/Projects/CosmicDance/CSVs/Dst_index.csv'
    TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/TLEs'

    df_nt = read_dst_index_CSV(DST_CSV)
    df_tles = get_merged_TLEs_from_CSVs(TLE_DIR_CSV)

    # for ldate in get_unique_launch_dates(df_tles):
    #     df = df_tles[df_tles["LAUNCH_DATE"] == ldate]
    #     plot(df_nt, df, ldate)

    tasks = set()
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for ldate in get_unique_launch_dates(df_tles):
            df = df_tles[df_tles["LAUNCH_DATE"] == ldate]

            tasks.add(executor.submit(plot, df_nt, df, ldate))

        for compute in concurrent.futures.as_completed(tasks):
            res = compute.result()
            print(res)
