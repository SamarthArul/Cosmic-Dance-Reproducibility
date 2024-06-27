import concurrent.futures
import math
import sys

from cosmic_dance.data_processor import *


def compute_abs_decay(tle_CSV: str, sdate: pd.Timestamp, edates: list[pd.Timestamp]) -> bool:
    # print(tle_CSV, sdate, edates)

    tle_df = read_TLEs_in_CSV(tle_CSV)

    last_tle_dict = get_last_TLE_before_the_date(tle_df, sdate)
    if last_tle_dict is None:
        return False, tle_CSV.split('.')[0].split('/')[-1]

    # Validate Gen2 satellites
    if START_LAUNCH_DATE_GEN_2 > last_tle_dict.get("LAUNCH_DATE"):
        return False, last_tle_dict.get("NORAD_CAT_ID")

    median_altitude_before_event = get_median_altitude_by_cat_id(tle_df, sdate)
    if math.isnan(median_altitude_before_event):
        return False, last_tle_dict.get("NORAD_CAT_ID")

    _abs_diff = abs(median_altitude_before_event-last_tle_dict.get("KM"))
    if _abs_diff >= 5:
        # print(f""" {last_tle_dict.get("NORAD_CAT_ID")} =>  ABS DIFF: {round(_abs_diff)}km CURRENT: {last_tle_dict.get("KM")}km""")
        return False, last_tle_dict.get("NORAD_CAT_ID")

    _record = {
        "NORAD_CAT_ID": last_tle_dict.get("NORAD_CAT_ID"),
        "LAUNCH_DATE": last_tle_dict.get("LAUNCH_DATE"),
        "EVENT_DATE": sdate,
    }

    for edate in edates:
        tle_after_dict = get_first_TLE_after_the_date(tle_df, edate)

        if tle_after_dict is None:
            _record[f"KM_after_DAY_{(edate-sdate)/timedelta(days=1)}"] = 0
            continue

        tle_after_effect_df = get_all_TLE_between_two_date(
            tle_df, last_tle_dict.get("EPOCH"), tle_after_dict.get("EPOCH")
        )
        abs_diff = (
            median_altitude_before_event - tle_after_effect_df["KM"]
        ).abs()
        _record[f"KM_after_DAY_{int((edate-sdate)/timedelta(days=1))}"] = abs_diff.max()

    CSV_logger(_record, OUTPUT_CSV)
    return True, _record.get("NORAD_CAT_ID")


def compute_decay(tle_CSV: str, sdate: pd.Timestamp, edates: list[pd.Timestamp]) -> bool:
    # print(tle_CSV, sdate, edates)

    tle_df = read_TLEs_in_CSV(tle_CSV)

    last_tle_dict = get_last_TLE_before_the_date(tle_df, sdate)
    if last_tle_dict is None:
        return False, tle_CSV.split('.')[0].split('/')[-1]

    # # Validate Gen2 satellites
    # if START_LAUNCH_DATE_GEN_2 > last_tle_dict.get("LAUNCH_DATE"):
    #     return False, last_tle_dict.get("NORAD_CAT_ID")

    median_altitude_before_event = get_median_altitude_by_cat_id(tle_df, sdate)
    if math.isnan(median_altitude_before_event):
        return False, last_tle_dict.get("NORAD_CAT_ID")

    _abs_diff = abs(median_altitude_before_event-last_tle_dict.get("KM"))
    if _abs_diff >= 5:
        # print(f""" {last_tle_dict.get("NORAD_CAT_ID")} =>  ABS DIFF: {round(_abs_diff)}km CURRENT: {last_tle_dict.get("KM")}km""")
        return False, last_tle_dict.get("NORAD_CAT_ID")

    _record = {
        "NORAD_CAT_ID": last_tle_dict.get("NORAD_CAT_ID"),
        "LAUNCH_DATE": last_tle_dict.get("LAUNCH_DATE"),
        "EVENT_DATE": sdate,
    }

    for edate in edates:
        tle_after_dict = get_first_TLE_after_the_date(tle_df, edate)

        if tle_after_dict is None:
            _record[f"KM_after_DAY_{(edate-sdate)/timedelta(days=1)}"] = 0
            continue

        tle_after_effect_df = get_all_TLE_between_two_date(
            tle_df, last_tle_dict.get("EPOCH"), tle_after_dict.get("EPOCH")
        )
        _diff = (last_tle_dict.get("KM") - tle_after_effect_df["KM"]).min()
        if _diff < 0:
            _record[f"KM_after_DAY_{int((edate-sdate)/timedelta(days=1))}"] = abs(_diff)
        else:
            _record[f"KM_after_DAY_{int((edate-sdate)/timedelta(days=1))}"] = 0.0

    CSV_logger(_record, OUTPUT_CSV)
    return True, _record.get("NORAD_CAT_ID")


if __name__ == '__main__':
    OUTPUT_CSV = 'altitude_decay_after_1_5_10.csv'
    TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/TLEs'
    DST_TIMESPAN_PTILE_99 = '/home/suvam/Projects/CosmicDance/CSVs/PT_99.csv'

    # # Only with Gen2 sats
    # START_LAUNCH_DATE_GEN_2 = pd.to_datetime('2022-12-28T00:00:00.00')

    df_timespan = read_timespan_CSV(DST_TIMESPAN_PTILE_99)
    list_of_sat_TLEs_in_CSV = [
        f'{TLE_DIR_CSV}/{CSV_filename}' for CSV_filename in get_file_names(TLE_DIR_CSV)
    ]

    # # Test processing code
    # for id, sdate in enumerate(df_timespan["STARTTIME"]):
    #     print(f"[{id+1}/{len(df_timespan)}]\tStarting from {sdate}...")

    #     for TLEs_in_CSV in list_of_sat_TLEs_in_CSV:
    #         edates = [sdate+timedelta(days=days) for days in [1, 5, 10]]
    #         print(compute_decay(TLEs_in_CSV, sdate, edates))

    #         exit()

    # Execute in pool
    tasks = set()
    id = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for sdate in df_timespan["STARTTIME"]:
            for TLEs_in_CSV in list_of_sat_TLEs_in_CSV:

                id += 1
                sys.stdout.write(f"\r [{id}] Starting... ")

                edates = [sdate+timedelta(days=days) for days in [1, 5, 10]]
                tasks.add(executor.submit(
                    compute_decay,
                    TLEs_in_CSV, sdate, edates
                ))

        print()
        _complete_count = 0
        for compute in concurrent.futures.as_completed(tasks):
            _status, _cat_id = compute.result()
            _complete_count += 1
            sys.stdout.write(
                f"""\r [{_complete_count}/{id}] Complete {round(_complete_count/id*100,1)}%  """
            )
        print()
