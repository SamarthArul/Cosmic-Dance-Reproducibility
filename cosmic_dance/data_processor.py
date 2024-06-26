import os
from datetime import timedelta

import numpy as np
import pandas as pd


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


def read_TLEs_in_CSV(file_path: str, epoch_date_type: bool = True, ldate_type: bool = True) -> pd.DataFrame:
    df = read_CSV(file_path)
    if ldate_type:
        df["LAUNCH_DATE"] = pd.to_datetime(df["LAUNCH_DATE"])
    if epoch_date_type:
        df["EPOCH"] = pd.to_datetime(df["EPOCH"])
    return df


def get_merged_TLEs_from_CSVs(file_path: str, epoch_date_type: bool = True, ldate_type: bool = True) -> pd.DataFrame:
    list_of_df = list()
    for file in get_file_names(file_path):
        _file_path = f"{file_path}/{file}"
        list_of_df.append(read_TLEs_in_CSV(
            _file_path, epoch_date_type, ldate_type)
        )

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
