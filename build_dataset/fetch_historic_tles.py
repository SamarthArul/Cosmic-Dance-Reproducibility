'''
Auto fetch all TLEs (from START_DATE to END_DATA) from https://www.space-track.org API by a satellite NORAD Catalog Number
- Request for each NORAD Catalog Number
- Save JSON file into give directory

'''

import json
import os
import time


def fetch_from_space_track_API(ID: str, PWD: str, NORAD_catalog_number: str, dir: str) -> bool:
    '''Fetch TLEs in JSON format using curl command

    Params
    ------
    ID: str
        space-track username(email)
    PWD: str
        space-track password
    NORAD_catalog_number: str
        NORAD Catalog Number of a satellite
    dir: str
        Output directory

    Returns
    -------
    bool:
        Status
    '''

    try:
        STATUS = os.system(
            f"""curl https://www.space-track.org/ajaxauth/login -d 'identity={ID}&password={PWD}&query=https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{NORAD_catalog_number}/orderby/TLE_LINE1%20ASC/EPOCH/{START_DATE}--{END_DATA}/format/json' > {dir}/{NORAD_catalog_number}.json"""
        )

    except Exception as e:
        print(f"|- Exception: {str(e)}")

    finally:
        # Check file size
        if 0 == os.path.getsize(f'{dir}/{NORAD_catalog_number}.json'):
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


def fetch_catelog_numbers() -> list[str]:
    '''Read all the NORAD Catalog Number from text file

    Returns
    -------
    list[str]: List of NORAD Catalog Numbers
    '''

    with open(CATELOG_NUMBER_FILE_PATH) as text_file:
        return text_file.read().strip().split('\n')


def read_credential() -> list[dict[str, str]]:
    '''Read the user credentials from JSON files

    Returns
    -------
    list[dict[str, str]]: list of dict with username and passwords
    '''

    credentials: list[dict[str, str]] = list()

    for credential in CREDENTIALS:
        with open(credential) as json_file:
            content = json.load(json_file)
            credentials.append(content)

    return credentials


if __name__ == '__main__':

    # TLE query start and end dates
    START_DATE = '2020-01-01'
    END_DATA = '2024-08-01'

    # Files
    # CATELOG_NUMBER_FILE_PATH = "artifacts/NORAD_CAT_NUM/StarlinkCatIDs.txt"
    CATELOG_NUMBER_FILE_PATH = "NewStarlinkCatIDs.txt"
    OUTPUT_DIR = "/mnt/Storage/OUTPUTs/Starlink/_TLEs"
    CREDENTIALS = [
        "credentials/credentials_1.json",
        "credentials/credentials_2.json",
        "credentials/credentials_3.json"
    ]

    # Read credentials and catelog numbers
    credentials = read_credential()
    catelog_numbers = fetch_catelog_numbers()

    # Fetch TLEs using credentials
    for id, catelog_number in enumerate(catelog_numbers):
        ID = credentials[id % len(credentials)].get('ID')
        PWD = credentials[id % len(credentials)].get('PWD')

        # Retry if failed
        while fetch_from_space_track_API(ID, PWD, catelog_number, OUTPUT_DIR) is False:
            print(f"|- Error: {catelog_number}, waiting...")
            time.sleep(30)

        print(
            f"|- Completed: {catelog_number}, Progress ({id+1}/{len(catelog_numbers)})"
        )

        # Wating to stay under the request limit
        if 0 == id % len(credentials):
            time.sleep(30)
