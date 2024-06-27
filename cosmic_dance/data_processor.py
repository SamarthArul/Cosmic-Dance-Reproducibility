import csv
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd


def CSV_logger(data: dict[str, float | int], csv_file_path: str = "log.csv") -> None:
    '''Write CSV file from dict dataset

    Parameters
    ---------
    data: dict[str, float | int]
        Dataset in dict format (Key, value pair only)

    csv_file_path: str, optional
        CSV file name, default value is `log.csv`
    '''

    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            writer.writeheader()

    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        writer.writerow(data)


def get_file_names(file_path: str) -> list[str]:
    return sorted(os.listdir(file_path))


def remove_file(file_path: str) -> None:
    os.remove(file_path)


def read_CSV(file_path: str, remove_nan: bool = True) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    if remove_nan:
        return df.dropna()
    else:
        return df


def read_orbit_raise_CSV(file_path: str) -> pd.DataFrame:
    df = read_CSV(file_path)
    df["LAUNCH_DATE"] = pd.to_datetime(df["LAUNCH_DATE"])
    df["ORBIT_RAISE_COMEPLETE"] = pd.to_datetime(df["ORBIT_RAISE_COMEPLETE"])
    return df


def read_TLEs_in_CSV(file_path: str, epoch_date_type: bool = True, ldate_type: bool = True) -> pd.DataFrame:
    df = read_CSV(file_path)
    if ldate_type:
        df["LAUNCH_DATE"] = pd.to_datetime(df["LAUNCH_DATE"])
    if epoch_date_type:
        df["EPOCH"] = pd.to_datetime(df["EPOCH"])
    return df


def get_merged_TLEs_from_CSVs(file_path: str, epoch_date_type: bool = True, ldate_type: bool = True) -> pd.DataFrame:
    list_of_df = list()
    file_names = get_file_names(file_path)

    for id, file in enumerate(file_names):
        sys.stdout.write(f'\r Reading {round(id/len(file_names)*100,1 )}%  ')

        _file_path = f"{file_path}/{file}"
        list_of_df.append(read_TLEs_in_CSV(
            _file_path, epoch_date_type, ldate_type)
        )

    print()
    return pd.concat(list_of_df)


def write_CSV(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path, index=False)


def satellite_age_in_days(df: pd.DataFrame) -> float:
    _df = pd.to_datetime(df["EPOCH"])
    return (_df.iloc[-1] - _df.iloc[0])/pd.Timedelta(days=1)


def read_dst_index_CSV(file_path: str, abs_value: bool = True) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
    if abs_value:
        df["nT"] = df["nT"].abs()
    return df


def percentile(df: pd.Series, percentiles: list[float]) -> list[float]:
    return np.percentile(df, percentiles)


def get_unique_cat_ids(df: pd.DataFrame) -> pd.Series:
    return df["NORAD_CAT_ID"].unique()


def get_unique_launch_dates(df: pd.DataFrame) -> pd.Series:
    return df["LAUNCH_DATE"].unique()


def get_all_TLE_between_two_date(df: pd.DataFrame, sdate: pd.Timestamp, edate: pd.Timestamp, cat_id: int | None = None) -> pd.DataFrame | None:
    if cat_id is not None:
        df = df[df["NORAD_CAT_ID"] == cat_id]
    df = df[df["EPOCH"].between(sdate, edate)]

    if len(df):
        return df
    return None


def extract_timespan_above_nT_intensity(df: pd.DataFrame, THRESHOLD: float) -> pd.DataFrame:
    active_time_records = []
    stime = None
    etime = None

    for timestamp, nT in zip(df["TIMESTAMP"], df["nT"]):

        if (nT > THRESHOLD) and (stime is None):
            stime = timestamp
            # print(timestamp, nT, '\t START')
        elif (nT < THRESHOLD) and (stime is not None) and (etime is None):
            etime = timestamp
            # print(timestamp, nT, '\t END')
        # else:
        #     print(timestamp, nT)

        if (stime is not None) and (etime is not None):
            active_time_records.append({
                "STARTTIME": stime,
                "ENDTIME": etime
            })
            # print('RECORDED')

            stime, etime = None, None

    df = pd.DataFrame.from_dict(active_time_records)
    return df


def read_timespan_CSV(file_path: str) -> pd.DataFrame:
    df = read_CSV(file_path)
    df["STARTTIME"] = pd.to_datetime(df["STARTTIME"])
    df["ENDTIME"] = pd.to_datetime(df["ENDTIME"])
    df["DURATION_HOURS"] = (
        df["ENDTIME"] - df["STARTTIME"]
    ) / pd.Timedelta(hours=1)
    return df


def get_last_TLE_before_the_date(df: pd.DataFrame, date: pd.Timestamp) -> dict[str, float]:
    df = df[df["EPOCH"] < date]
    if len(df):
        return df.iloc[-1].to_dict()
    return None


def get_median_altitude_by_cat_id(df: pd.DataFrame, end_date: pd.Timestamp = None) -> float:
    if end_date is not None:
        df = df[df["EPOCH"] < end_date]
    return df["KM"].median()


def get_first_TLE_after_the_date(df: pd.DataFrame, date: pd.Timestamp) -> dict[str, float]:
    df = df[df["EPOCH"] > date]
    if len(df):
        return df.iloc[0].to_dict()
    return None


def get_CDF(data: pd.Series) -> tuple[np.array, np.array]:
    x = np.sort(data)
    y = np.arange(len(data)) / float(len(data))
    return x, y
