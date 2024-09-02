import sys
import math

import ephem

from cosmic_dance.io import *

G: float = 6.67408 * 10**(-11)
M: float = 5.9722*(10**24)
EARTH_RADIUS_M: float = 6378135.0


class TLE:
    '''Data attributes for TLEs'''

    OBJECT_NAME = "OBJECT_NAME"
    NORAD_CAT_ID = "NORAD_CAT_ID"
    CREATION_DATE = "CREATION_DATE"
    LAUNCH_DATE = "LAUNCH_DATE"

    EPOCH = "EPOCH"
    INCLINATION = "INCLINATION"
    RAAN = "RAAN"
    ARGP = "ARGP"
    ECCENTRICITY = "ECCENTRICITY"
    ALTITUDE_KM = "ALTITUDE_KM"
    MEAN_MOTION = "MEAN_MOTION"
    MEAN_ANOMALY = "MEAN_ANOMALY"
    BSTAR = "BSTAR"
    DRAG = "DRAG"

    LAT = "LAT"
    LONG = "LONG"

    RA_OF_ASC_NODE = "RA_OF_ASC_NODE"
    ARG_OF_PERICENTER = "ARG_OF_PERICENTER"

    LINE0 = "TLE_LINE0"
    LINE1 = "TLE_LINE1"
    LINE2 = "TLE_LINE2"


def get_merged_TLEs_from_all_CSVs(directory_name: str, epoch_date_type: bool = True, ldate_type: bool = True) -> pd.DataFrame:
    '''Read TLEs from all CSV files in directory

    Params
    ------
    directory_name: str
        directory of CSV files (NORAD_CAT_ID.csv)
    epoch_date_type: bool, optional
        EPOCH date type (Default pd.Timestamp)
    ldate_type: bool, optional
        Launch date type (Default pd.Timestamp)

    Returns
    -------
    DataFrame of all TLEs
    '''

    list_of_df = list()
    file_names = get_file_names(directory_name)

    for id, file in enumerate(file_names):
        sys.stdout.write(f"\r Reading {round(id/len(file_names)*100,1 )}%  ")

        _filename = f"{directory_name}/{file}"
        list_of_df.append(
            read_TLEs_in_CSV(
                _filename, epoch_date_type, ldate_type
            )
        )

    print()
    return pd.concat(list_of_df)


def read_orbit_raise_CSV(filename: str) -> pd.DataFrame:
    '''Read orbit raise CSV file

    Params
    ------
    filename: str
        CSV file (NORAD_CAT_ID.csv)

    Returns
    -------
    DataFrame of orbit raise complete records
    '''

    df = read_CSV(filename)

    df[TLE.LAUNCH_DATE] = pd.to_datetime(df[TLE.LAUNCH_DATE])
    df["ORBIT_RAISE_COMEPLETE"] = pd.to_datetime(df["ORBIT_RAISE_COMEPLETE"])

    return df


def read_TLEs_in_CSV(filename: str, epoch_date_type: bool = True, ldate_type: bool = True) -> pd.DataFrame:
    '''Read TLEs from CSV file

    Params
    ------
    filename: str
        CSV file (NORAD_CAT_ID.csv)
    epoch_date_type: bool, optional
        EPOCH date type (Default pd.Timestamp)
    ldate_type: bool, optional
        Launch date type (Default pd.Timestamp)

    Returns
    -------
    DataFrame of TLEs
    '''

    df = read_CSV(filename)

    if ldate_type:
        df[TLE.LAUNCH_DATE] = pd.to_datetime(df[TLE.LAUNCH_DATE])

    if epoch_date_type:
        df[TLE.EPOCH] = pd.to_datetime(df[TLE.EPOCH])

    return df


def satellite_age_in_days(df: pd.DataFrame) -> float:
    '''Counts how many days passed after the launch

    Params
    ------
    df: pd.DataFrame
        DataFrame of TLE CSV

    Returns
    ------
    float: Days
    '''

    _df = pd.to_datetime(df[TLE.EPOCH])
    return (_df.iloc[-1] - _df.iloc[0])/pd.Timedelta(days=1)


def convert_to_km(mean_motion: float) -> float:
    '''Calculate altitude in km from mean motion of satellites

    Params
    ------
    mean_motion: float
        Mean motion from TLE

    Returns
    -------
    float: Altitude in km
    '''

    return (math.pow(((G * M * ((24*60*60)/mean_motion) ** 2) /
                      (4 * math.pi ** 2)), (1/3)) - EARTH_RADIUS_M)/1000


def find_new_catalog_numbers(
        current_TLE_file: str,
        old_catalog_number_list_file: str,
        new_catalog_number_list_file: str
):
    '''Find new NORAD Catalog Numbers maybe new launched

    Params
    ------
    current_TLE_file: str
        TLE file
    old_catalog_number_list_file: str
        Old file with list of NORAD catalog numbers
    new_catalog_number_list_file: str
        New file with list of NORAD catalog numbers
    '''

    current_catalog_number_set: set[int] = set()
    old_catalog_number_set: set[int] = set()
    new_catalog_number_set: set[int] = set()

    # Get Catalog Numbers
    current_catalog_number_set = extract_catalog_numbers(current_TLE_file)
    old_catalog_number_set = read_catalog_number_list(
        old_catalog_number_list_file
    )

    # Find new Catalog Numbers
    print(f"|- New IDs")
    for cid in current_catalog_number_set:
        if cid not in old_catalog_number_set:
            print(f"|-- {cid}")

            new_catalog_number_set.add(cid)
            # Also update the old with new ones
            old_catalog_number_set.add(cid)

    # Write the new and updated old Catalog Numbers
    write_catalog_number_list(
        new_catalog_number_set,
        new_catalog_number_list_file
    )
    print(f"|- Written new list: {new_catalog_number_list_file}")
    write_catalog_number_list(
        old_catalog_number_set,
        old_catalog_number_list_file
    )
    print(f"|- Updated old list: {old_catalog_number_list_file}")


def extract_catalog_numbers(filename: str) -> set[int]:
    '''Extract NORAD Catalog Number for the TLEs file

    Params
    ---------
    filename: str
        TLE file path

    Returns
    -------
    set[int]: Set of NORAD Catalog Numbers
    '''

    catalog_number_set: set[int] = set()

    with open(filename, 'r') as f:

        for tles_line_1 in f:
            tles_line_2 = f.readline()
            tles_line_3 = f.readline()

            tle = ephem.readtle(tles_line_1, tles_line_2, tles_line_3)
            catalog_number_set.add(tle.catalog_number)

    return catalog_number_set
