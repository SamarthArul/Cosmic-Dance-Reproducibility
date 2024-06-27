import concurrent.futures

from cosmic_dance.data_processor import *
from cosmic_dance.stack_plots import *


def plot(df_nt: pd.DataFrame, file_path: str) -> str:
    df_tles = read_TLEs_in_CSV(file_path, ldate_type=False)

    cat_id = df_tles.iloc[-1]["NORAD_CAT_ID"]
    ldate = df_tles.iloc[-1]["LAUNCH_DATE"]

    resp = plot_in_stack_cat_id_with_nt(
        cat_id, ldate,
        df_tles, df_nt,
        output_dir=PLOT_OUTPUT_DIR
    )

    return resp


if __name__ == '__main__':
    PLOT_OUTPUT_DIR = '/mnt/Storage/OUTPUTs/HawkEye_360/VIEW'

    DST_CSV = '/home/suvam/Projects/CosmicDance/CSVs/Dst_index.csv'
    TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/HawkEye_360/TLEs'

    # df_nt = read_dst_index_CSV(DST_CSV)
    # for file in get_file_names(TLE_DIR_CSV):
    #     file_path = f"{TLE_DIR_CSV}/{file}"
    #     plot(df_nt, file_path)

    df_nt = read_dst_index_CSV(DST_CSV)
    tasks = set()
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for file in get_file_names(TLE_DIR_CSV):
            file_path = f"{TLE_DIR_CSV}/{file}"

            tasks.add(executor.submit(plot, df_nt, file_path))

        for compute in concurrent.futures.as_completed(tasks):
            res = compute.result()
            print(res)
