import math
import sys
import time
import json
import requests
import ephem
import pandas as pd
from cosmic_dance.io import *

G: float = 6.67408 * 10**(-11)
M: float = 5.9722 * (10**24)
EARTH_RADIUS_M: float = 6378135.0
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"

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

def convert_from_JSON_to_CSV(filename: str, output_dir: str):
    '''Filter the required attributes and write into a CSV file (NORAD_CAT_ID.csv)'''
    tles = read_JSON_file(filename)
    for tle in tles:
        data_dict = {
            TLE.NORAD_CAT_ID: int(tle[TLE.NORAD_CAT_ID]),
            TLE.LAUNCH_DATE: tle[TLE.LAUNCH_DATE],
            TLE.EPOCH: tle[TLE.EPOCH],
            TLE.INCLINATION: float(tle[TLE.INCLINATION]),
            TLE.RAAN: float(tle[TLE.RA_OF_ASC_NODE]),
            TLE.ARGP: float(tle[TLE.ARG_OF_PERICENTER]),
            TLE.ECCENTRICITY: float(tle[TLE.ECCENTRICITY]),
            TLE.ALTITUDE_KM: convert_to_km(float(tle[TLE.MEAN_MOTION])),
            TLE.MEAN_MOTION: float(tle[TLE.MEAN_MOTION]),
            TLE.MEAN_ANOMALY: float(tle[TLE.MEAN_ANOMALY]),
            TLE.DRAG: float(tle[TLE.BSTAR]),
        }
        CSV_logger(data_dict, output_dir)

def download_satellite(catalog_number: int, credential: dict, start_date: str, end_date: str, output_dir: str) -> bool:
    """Download TLEs for a single satellite with retry logic"""
    cred_id = credential.get('identity', 'unknown')
    session = None
    
    try:
        session = create_session(credential)
        if not session:
            print(f"|- Failed to create session for satellite {catalog_number} with {cred_id}")
            return False
            
        attempt = 0
        max_attempts = 5
        
        while attempt < max_attempts:
            print(f"|- Starting attempt {attempt + 1} for {catalog_number} with {cred_id}")
            try:
                success = fetch_from_space_track_API(
                    session,
                    catalog_number,
                    start_date,
                    end_date,
                    output_dir
                )
                
                if success and check_response_content(output_dir, catalog_number):
                    print(f"|- Completed: {catalog_number} with {cred_id}")
                    return True
                    
                print(f"|- Failed attempt {attempt + 1} for {catalog_number} with {cred_id}: Invalid data or no success")
                time.sleep(3 + attempt)  # Progressive backoff
                attempt += 1
                print(f"|- Retrying after sleep for {catalog_number}, next attempt: {attempt + 1}")
                
            except requests.exceptions.RequestException as e:
                print(f"|- Network error for {catalog_number} with {cred_id}: {str(e)}, attempt {attempt + 1}")
                time.sleep(3 + attempt)
                attempt += 1
                print(f"|- Retrying after network error for {catalog_number}, next attempt: {attempt + 1}")
                
        print(f"|- Gave up on {catalog_number} after {max_attempts} attempts with {cred_id}")
        return False
        
    except Exception as e:
        print(f"|- Unexpected error for {catalog_number} with {cred_id}: {str(e)}")
        return False
    finally:
        if session:
            try:
                session.close()
            except:
                pass
    return False

def check_response_content(output_dir: str, catalog_number: int) -> bool:
    """Check if the JSON file contains valid data and not rate limit errors"""
    try:
        json_file = f"{output_dir}/{catalog_number}.json"
        with open(json_file, 'r') as f:
            content = f.read()
            if any(error_text in content for error_text in [
                '"error":', 
                'rate limit',
                'You\'ve violated'
            ]):
                return False
            data = json.loads(content)
            return bool(data and not (isinstance(data, list) and len(data) == 0))
    except:
        return False

def download_TLEs(
    catalog_numbers: list[int],  # Changed from List[int] to list[int]
    credentials: list[dict[str, str]],  # Changed from List[Dict[str, str]] to list[dict[str, str]]
    start_date: str,
    end_date: str,
    output_dir: str
):
    '''Download all TLEs sequentially with a single credential, switching on repeated failures'''
    if not credentials:
        raise Exception("No credentials provided")
    
    current_cred_idx = 0
    current_credential = credentials[current_cred_idx]
    consecutive_failures = 0
    MIN_DELAY = 3  # Minimum delay between requests in seconds
    
    print(f"Starting downloads with credential: {current_credential.get('identity', 'cred_0')}")
    print(f"Processing {len(catalog_numbers)} satellites")
    
    failed = []
    completed = 0
    
    for cat_num in catalog_numbers:
        start_time = time.time()
        
        success = download_satellite(cat_num, current_credential, start_date, end_date, output_dir)
        completed += 1
        
        if success:
            consecutive_failures = 0
        else:
            failed.append(cat_num)
            consecutive_failures += 1
            print(f"|- Consecutive failures: {consecutive_failures}")
            
            if consecutive_failures >= 5 and current_cred_idx < len(credentials) - 1:
                current_cred_idx += 1
                current_credential = credentials[current_cred_idx]
                consecutive_failures = 0
                print(f"|- Switching to new credential: {current_credential.get('identity', f'cred_{current_cred_idx}')}")
        
        print(f"Progress: {completed}/{len(catalog_numbers)} ({round(100*completed/len(catalog_numbers),2)}%)")
        
        # Enforce 2.1-second delay between requests
        elapsed = time.time() - start_time
        if elapsed < MIN_DELAY:
            time.sleep(MIN_DELAY - elapsed)
    
    if failed:
        print(f"\nFailed to download {len(failed)} satellites: {failed[:5]}{'...' if len(failed) > 5 else ''}")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        failed_file = f"{output_dir}/failed_satellites_{timestamp}.txt"
        with open(failed_file, 'w') as f:
            for sat in failed:
                f.write(f"{sat}\n")
        print(f"Failed satellites saved to: {failed_file}")
    
    print(f"\nCompleted download process: {len(catalog_numbers) - len(failed)} successful, {len(failed)} failed")

def create_session(credential: dict) -> requests.Session | None:
    """Create a new session with the given credentials"""
    try:
        session = requests.Session()
        response = session.post(
            LOGIN_URL,
            data={
                "identity": credential.get('identity'),
                "password": credential.get('password')
            }
        )
        if response.ok:
            return session
        print(f"|- Session creation failed for {credential.get('identity', 'unknown')}")
        return None
    except Exception as e:
        print(f"Session creation error: {str(e)}")
        return None

def get_median_altitude(df: pd.DataFrame, end_date: pd.Timestamp = None) -> float:
    '''Calculate the median altitude from the TLEs up to given date'''
    if end_date is not None:
        df = df[df[TLE.EPOCH] < end_date]
    return df[TLE.ALTITUDE_KM].median()

def get_first_TLE_after_the_date(df: pd.DataFrame, date: pd.Timestamp) -> dict[str, float] | None:
    '''Query the immediate first TLE after the given date'''
    df = df[df[TLE.EPOCH] > date]
    if len(df):
        return df.iloc[0].to_dict()
    return None

def get_last_TLE_before_the_date(df: pd.DataFrame, date: pd.Timestamp) -> dict[str, float] | None:
    '''Query the immediate last TLE before the given date'''
    df = df[df[TLE.EPOCH] < date]
    if len(df):
        return df.iloc[-1].to_dict()
    return None

def get_TLEs_by_cat_id(df: pd.DataFrame, cat_id: int) -> pd.DataFrame:
    '''Query all the TLEs by NORAD Catalog Number'''
    return df[df[TLE.NORAD_CAT_ID] == cat_id]

def get_TLEs_by_launch_date(df: pd.DataFrame, ldate: pd.Timestamp) -> pd.DataFrame:
    '''Query all the TLEs by launch date'''
    return df[df[TLE.LAUNCH_DATE] == ldate]

def get_unique_launch_dates(df: pd.DataFrame) -> pd.Series:
    '''Unique launch dates in the given TLEs'''
    return df[TLE.LAUNCH_DATE].unique()

def get_unique_cat_ids(df: pd.DataFrame) -> pd.Series:
    '''Unique NORAD Catalog Number in the given TLEs'''
    return df[TLE.NORAD_CAT_ID].unique()

def get_all_TLE_between_two_date(
    df: pd.DataFrame,
    sdate: pd.Timestamp,
    edate: pd.Timestamp,
    cat_id: int | None = None
) -> pd.DataFrame | None:
    '''Query all the TLEs of given satellite(s) within the time window'''
    if cat_id is not None:
        df = df[df[TLE.NORAD_CAT_ID] == cat_id]
    df = df[df[TLE.EPOCH].between(sdate, edate)]
    if len(df):
        return df
    return None

def get_merged_TLEs_from_all_CSVs(directory_name: str, epoch_date_type: bool = True, ldate_type: bool = True, epoch_mixed_format: bool = True) -> pd.DataFrame:
    '''Read TLEs from all CSV files in directory'''
    list_of_df = []
    file_names = get_file_names(directory_name)
    for id, file in enumerate(file_names):
        sys.stdout.write(f"\r Reading {round(id/len(file_names)*100,1)}%  ")
        _filename = f"{directory_name}/{file}"
        list_of_df.append(
            read_TLEs_in_CSV(
                _filename, epoch_date_type, ldate_type, epoch_mixed_format
            )
        )
    print()
    return pd.concat(list_of_df)

def read_orbit_raise_CSV(filename: str) -> pd.DataFrame:
    '''Read orbit raise CSV file'''
    df = read_CSV(filename)
    df[TLE.LAUNCH_DATE] = pd.to_datetime(df[TLE.LAUNCH_DATE])
    df["ORBIT_RAISE_COMEPLETE"] = pd.to_datetime(df["ORBIT_RAISE_COMEPLETE"])
    return df

def read_TLEs_in_CSV(filename: str, epoch_date_type: bool = True, ldate_type: bool = True, epoch_mixed_format: bool = True) -> pd.DataFrame:
    '''Read TLEs from CSV file'''
    df = read_CSV(filename)
    if ldate_type:
        df[TLE.LAUNCH_DATE] = pd.to_datetime(df[TLE.LAUNCH_DATE])
    if epoch_date_type:
        if epoch_mixed_format:
            df[TLE.EPOCH] = pd.to_datetime(df[TLE.EPOCH], format='mixed')
        else:
            df[TLE.EPOCH] = pd.to_datetime(df[TLE.EPOCH])
    return df

def satellite_age_in_days(df: pd.DataFrame) -> float:
    '''Counts how many days passed after the launch'''
    return (df[TLE.EPOCH].iloc[-1] - df[TLE.EPOCH].iloc[0]) / pd.Timedelta(days=1)

def convert_to_km(mean_motion: float) -> float:
    '''Calculate altitude in km from mean motion of satellites'''
    return (math.pow(((G * M * ((24*60*60)/mean_motion) ** 2) /
                     (4 * math.pi ** 2)), (1/3)) - EARTH_RADIUS_M) / 1000

def find_new_catalog_numbers(
    current_TLE_file: str,
    old_catalog_number_list_file: str,
    new_catalog_number_list_file: str
):
    '''Find new NORAD Catalog Numbers maybe new launched'''
    current_catalog_number_set = extract_catalog_numbers(current_TLE_file)
    old_catalog_number_set = read_catalog_number_list(old_catalog_number_list_file)
    new_catalog_number_set = set()
    
    print(f"|- New IDs")
    for cid in current_catalog_number_set:
        if cid not in old_catalog_number_set:
            print(f"|-- {cid}")
            new_catalog_number_set.add(cid)
            old_catalog_number_set.add(cid)
    
    write_catalog_number_list(new_catalog_number_set, new_catalog_number_list_file)
    print(f"|- Written new list: {new_catalog_number_list_file}")
    write_catalog_number_list(old_catalog_number_set, old_catalog_number_list_file)
    print(f"|- Updated old list: {old_catalog_number_list_file}")

def extract_catalog_numbers(filename: str) -> set[int]:
    '''Extract NORAD Catalog Number for the TLEs file'''
    catalog_number_set = set()
    with open(filename, 'r') as f:
        for tles_line_1 in f:
            tles_line_2 = f.readline()
            tles_line_3 = f.readline()
            tle = ephem.readtle(tles_line_1, tles_line_2, tles_line_3)
            catalog_number_set.add(tle.catalog_number)
    return catalog_number_set