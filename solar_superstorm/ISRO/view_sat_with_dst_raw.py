import concurrent.futures

from cosmic_dance.data_processor import *
from cosmic_dance.stack_plots import *


def plot(df_nt: pd.DataFrame, file: str) -> str:
    file_path = f"{TLE_DIR_CSV}/{file}"
    df_tles = read_TLEs_in_CSV(file_path, ldate_type=False)
    df_tles = get_all_TLE_between_two_date(df_tles, START_DATE, END_DATE)

    cat_id = df_tles.iloc[-1]["NORAD_CAT_ID"]
    ldate = df_tles.iloc[-1]["LAUNCH_DATE"]

    resp = plot_in_stack_cat_id_with_nt(
        f"{cat_id} || {file.split('.')[0]}",
        ldate,
        df_tles, df_nt,
        output_dir=PLOT_OUTPUT_DIR
    )

    return resp


if __name__ == '__main__':
    START_DATE = pd.to_datetime("2024-04-01 00:00:00")
    END_DATE = pd.to_datetime("2024-06-01 00:00:00")

    PLOT_OUTPUT_DIR = '/mnt/Storage/OUTPUTs/ISRO/VIEW'

    DST_CSV = '/home/suvam/Projects/CosmicDance/CSVs/Dst_index.csv'
    TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/ISRO/TLEs'

    df_nt = read_dst_index_CSV(DST_CSV)
    for file in get_file_names(TLE_DIR_CSV):
        plot(df_nt, file)
