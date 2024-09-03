'''
Detects the type of orbital shift using record of orbital params over a few days 
and Segregate similar Segregate orbital shift into directories

Currently detects:
- Minor/Noimpact
- Station keeping
- Permanent decay
'''

import concurrent.futures

from cosmic_dance.dst_index import *
from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def minor_no_impact(df: pd.DataFrame) -> bool:
    '''
    Detects no orbital decay if
    - Difference of first day altitude change and median altitude change < 0.05 KM
    - Difference of last day altitude change and median altitude change < 0.05 KM
    - Difference of max altitude change and median altitude change < 1 KM


    Params:
    -------
    df: pd.DataFrame
        DataFrame of orbital params over a few days

    Returns
    -------
    bool: True if positive
    '''

    altitude_first = df.iloc[0]["ALTITUDE_CHANGE_KM"]
    altitude_last = df.iloc[-1]["ALTITUDE_CHANGE_KM"]
    altitude_median = df["ALTITUDE_CHANGE_KM"].median()

    median_start_end_diff = max(
        abs(altitude_first-altitude_median),
        abs(altitude_last-altitude_median)
    )
    median_max_diff = abs(
        altitude_median-df["ALTITUDE_CHANGE_KM"].max()
    )

    if median_start_end_diff < 0.05 and median_max_diff < 1:
        return True
    return False


def station_keeping(df: pd.DataFrame) -> bool:
    '''
    Detects station keeping if
    - First day altitude change is lower than median altitude change
    - Last day altitude change is lower than median altitude change


    Params:
    -------
    df: pd.DataFrame
        DataFrame of orbital params over a few days

    Returns
    -------
    bool: True if positive
    '''

    altitude_first = df.iloc[0]["ALTITUDE_CHANGE_KM"]
    altitude_last = df.iloc[-1]["ALTITUDE_CHANGE_KM"]
    altitude_median = df["ALTITUDE_CHANGE_KM"].median()

    if altitude_first < altitude_median and altitude_median > altitude_last:
        return True
    return False


def permanent_decay(df: pd.DataFrame) -> bool:
    '''
    Detects permanent decay if
    - Difference of first day altitude change and median altitude change > 0.05 KM
    - Difference of last day altitude change and median altitude change > 0.05 KM

    Params:
    -------
    df: pd.DataFrame
        DataFrame of orbital params over a few days

    Returns
    -------
    bool: True if positive
    '''

    altitude_first = df.iloc[0]["ALTITUDE_CHANGE_KM"]
    altitude_last = df.iloc[-1]["ALTITUDE_CHANGE_KM"]
    altitude_median = df["ALTITUDE_CHANGE_KM"].median()

    if altitude_median-altitude_first > 0.05 and altitude_last-altitude_median > 0.05:
        return True
    return False


def detect_shift_type(filename: str):
    '''Segregate orbital shift using record of orbital params over a few days

    Params
    ------
    filename: str
        CSV filename
    '''

    df = read_CSV(f"{INPUT_DIR}/{filename}")
    print(f"|- Processing: {filename}")

    # List of similar type of orbital shift
    station_keeping_dfs: list[pd.DataFrame] = list()
    minor_no_impact_dfs: list[pd.DataFrame] = list()
    permanent_decay_dfs: list[pd.DataFrame] = list()
    undecidable_dfs: list[pd.DataFrame] = list()

    # For each satellite (Query unique NORAD Catalog Numbers)
    for cat_id in df["CAT_ID"].unique():
        df_after_effects_cat_id = df[df["CAT_ID"] == cat_id]

        # Inspecting orbital params of each satellite
        if minor_no_impact(df_after_effects_cat_id):
            minor_no_impact_dfs.append(df_after_effects_cat_id)

        elif station_keeping(df_after_effects_cat_id):
            station_keeping_dfs.append(df_after_effects_cat_id)

        elif permanent_decay(df_after_effects_cat_id):
            permanent_decay_dfs.append(df_after_effects_cat_id)

        # If none of the existing pattern matched
        else:
            undecidable_dfs.append(df_after_effects_cat_id)
            print(f"|-- {cat_id} Undecidable")

    # Merge all similar shift and export into a CSV file (EVENT_DATE.csv)
    for dfs, dir in [
        (station_keeping_dfs, f"{OUTPUT_DIR}/{STATION_KEEPING}"),
        (minor_no_impact_dfs, f"{OUTPUT_DIR}/{MINOR_NO_IMPACT}"),
        (permanent_decay_dfs, f"{OUTPUT_DIR}/{PERMANENT_DECAY}"),
        (undecidable_dfs, f"{OUTPUT_DIR}/{UNDECIDABLE}"),
    ]:
        if len(dfs):
            pd.concat(dfs).to_csv(
                f"{dir}/{filename}",
                index=False
            )


if __name__ == '__main__':

    PARALLEL_MODE = True

    # `capture_solar_event_after_effects.py` output directory is the input
    INPUT_DIR = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/solar_events/absolute_altitude_change/merged_above_ptile_99/RAW"
    OUTPUT_DIR = "/mnt/Storage/OUTPUTs/Starlink/OUTPUTs/solar_events/absolute_altitude_change/merged_above_ptile_99"

    # Classes
    PERMANENT_DECAY = "permanent_decay"
    STATION_KEEPING = "station_keeping"
    MINOR_NO_IMPACT = "minor_no_impact"
    UNDECIDABLE = "undecidable"

    input(f"Directory {OUTPUT_DIR} will be altered ?")
    create_directories(
        f"{OUTPUT_DIR}/{STATION_KEEPING}",
        f"{OUTPUT_DIR}/{MINOR_NO_IMPACT}",
        f"{OUTPUT_DIR}/{PERMANENT_DECAY}",
        f"{OUTPUT_DIR}/{UNDECIDABLE}",
    )

    if PARALLEL_MODE:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            # For each CSv files (EVENT_DATE.csv)
            for filename in sorted(os.listdir(INPUT_DIR)):
                executor.submit(detect_shift_type, filename)

            executor.shutdown()

    # Serial mode
    else:
        for filename in get_file_names(INPUT_DIR):
            detect_shift_type(filename)
