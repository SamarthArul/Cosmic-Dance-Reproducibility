
import csv
import json
import os

import pandas as pd
import requests


def remove_file(filename: str):
    '''Read CSV file as Dataframe

    Params
    ------
    filename: str
        Path to the file
    '''

    os.remove(filename)


def write_CSV(df: pd.DataFrame, filename: str):
    '''Write CSV file from Dataframe

    Params
    ------
    df: pd.DataFrame
        DataFrame to be written
    filename: str
        CSV filename
    '''

    df.to_csv(filename, index=False)


def read_CSV(filename: str, remove_nan: bool = True) -> pd.DataFrame:
    '''Read CSV file as Dataframe

    Params
    ------
    filename: str
        Path to CSV file
    remove_nan: bool, optional
        Remove nan values

    Returns
    -------
    pd.DataFrame
    '''

    df = pd.read_csv(filename)

    if remove_nan:
        return df.dropna()
    else:
        return df


def get_file_names(directory_name: str) -> list[str]:
    '''Get the sorted list of filenames inside given directory

    Params
    ------
    directory_name: str
        Directory (path)

    Returns
    -------
    list[str]: list of filenames

    '''

    return sorted(os.listdir(directory_name))


def read_JSON_file(filename: str) -> dict[str, int | float]:
    '''Read JSON file

    Params
    ------
    filename: str
        JSON file

    Returns
    -------
    dict[str, int | float]: dictionary
    '''

    with open(filename) as json_file:
        return json.loads(json_file.read())


def CSV_logger(data: dict[str, float | int], csv_file_path: str = "log.csv"):
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


def fetch_from_space_track_API(
    email: str,
    password: str,
    NORAD_catalog_number: str,
    start_date: str,
    end_date: str,
    output_dir: str
) -> bool:
    '''Fetch TLEs in JSON format using curl command from space-track API

    Params
    ------
    email: str
        space-track username(email)
    password: str,
        space-track password
    NORAD_catalog_number: str
        NORAD Catalog Number of a satellite
    start_date: str
        TLE epoch start date
    end_date: str
        TLE epoch end date
    output_dir: str
        Output directory

    Returns
    -------
    bool:
        Status
    '''

    try:
        STATUS = os.system(
            f"""curl https://www.space-track.org/ajaxauth/login -d 'identity={email}&password={password}&query=https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{NORAD_catalog_number}/orderby/TLE_LINE1%20ASC/EPOCH/{start_date}--{end_date}/format/json' > {output_dir}/{NORAD_catalog_number}.json"""
        )

    except Exception as e:
        print(f"|- Exception: {str(e)}")

    finally:
        # Check file size
        if 0 == os.path.getsize(f"{output_dir}/{NORAD_catalog_number}.json"):
            return False

        # # Validate content
        # with open(f'{dir}/{NORAD_catalog_number}.json') as json_file:

        #     content = json.load(json_file)
        #     if 0 == len(content):
        #         return False

        #     content = content[-1]

        #     if 'error' in content:
        #         print(f'Failed: {NORAD_catalog_number}')
        #         print(f'ERROR: {content["error"]}')

        #         # Wait
        #         for t in range(200):
        #             time.sleep(1)
        #             print(t, end=', ')

        #         return False

        # CURL execution status
        if 0 == STATUS:
            print(f'Success: {NORAD_catalog_number}')
            return True
        else:
            print(f'Failed: {NORAD_catalog_number}')
            return False


def read_credentials(filename_list: list[str]) -> list[dict[str, str]]:
    '''Read the user credentials from JSON files

    Returns
    -------
    list[dict[str, str]]: list of dict with username and passwords
    '''

    credentials: list[dict[str, str]] = list()

    for credential in filename_list:
        with open(credential) as json_file:
            content = json.load(json_file)
            credentials.append(content)

    return credentials


def read_catalog_number_list(filename: str, in_order: bool = False) -> set[int] | list[int]:
    '''Read file with a list of NORAD Catalog Number

    Params
    ------
    filename: str
        File path
    '''

    catalog_number_set: set[int] = set()

    with open(filename) as f:
        for id in f.read().strip().split('\n'):
            catalog_number_set.add(int(id))

    if in_order:
        return sorted(list(catalog_number_set))

    return catalog_number_set


def write_catalog_number_list(catalog_number_set: set[int], filename: str):
    '''Write file with a list of NORAD Catalog Number line by line

    Params
    ------
    catalog_number_set: set[int]
        Set of NORAD Catalog Numbers
    filename_tles: string
        File path
    '''

    with open(filename, 'w') as f:
        for cat_id in catalog_number_set:
            f.write(f"{cat_id}\n")


def write_to_file(content: str, filename: str):
    '''Write into a file

    Params
    ------
    content: str
        File content
    filename: str
        File path
    '''

    with open(filename, 'w') as f:
        f.write(content)
    print(f"|- Save file: {filename}")


def fetch_from_url(url: str) -> str:
    '''Read the content from the URL

    Params
    -------
    url: str
        Web URL

    Returns
    -------
    str: content as string
    '''

    response = requests.get(url)
    assert response.ok
    return response.text


def export_as_csv(df: pd.DataFrame, filename: str):
    '''Save DataFrame as CSV file

    Params
    ---------
    df: pd.DataFrame
        DataFrame
    filename: str
        Filename including path
    '''

    df.to_csv(filename, index=False)
    print(f"|- Save file: {filename}")
