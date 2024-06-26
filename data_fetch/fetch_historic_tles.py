import json
import os
import time

'''
Python script to fetch TLEs (from 2020-01-01 to 2024-04-30) from https://www.space-track.org by a satellite catelog number
Saves in JSON format
'''


def fetch_from_space_track_API(ID: str, PWD: str, NORAD_catalog_number: str, dir: str) -> bool:
    STATUS = os.system(
        f"""curl https://www.space-track.org/ajaxauth/login -d 'identity={ID}&password={PWD}&query=https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{NORAD_catalog_number}/orderby/TLE_LINE1%20ASC/EPOCH/{START_DATE}--{END_DATA}/format/json' > {dir}/{NORAD_catalog_number}.json"""
    )

    # Validate
    with open(f'{dir}/{NORAD_catalog_number}.json') as json_file:
        content = json.load(json_file)[-1]

        if 'error' in content:
            print(f'Failed: {NORAD_catalog_number}')
            print(f'ERROR: {content["error"]}')

            # Wait
            for t in range(200):
                time.sleep(1)
                print(t, end=', ')

            return False

    if 0 == STATUS:
        print(f'Success: {NORAD_catalog_number}')
        return True
    else:
        print(f'Failed: {NORAD_catalog_number}')
        return False


def fetch_catelog_numbers(file_path: str) -> list[str]:
    with open(file_path) as text_file:
        return text_file.read().strip().split('\n')


if __name__ == '__main__':

    START_DATE = '2020-01-01'
    END_DATA = '2024-06-01'

    # # 1
    # CATELOG_NUMBER_FILE_PATH = 'catelog_numbers_1.txt'
    # OUTPUT_DIR = '/mnt/Storage/OUTPUTs/TLE_1'
    # CREDENTIALS = 'credentials/credentials_1.json'

    # # 2
    # CATELOG_NUMBER_FILE_PATH = 'catelog_numbers_2.txt'
    # OUTPUT_DIR = '/mnt/Storage/OUTPUTs/TLE_2'
    # CREDENTIALS = 'credentials/credentials_2.json'

    # 3
    CATELOG_NUMBER_FILE_PATH = 'catelog_numbers_3.txt'
    OUTPUT_DIR = '/mnt/Storage/OUTPUTs/TLE_3'
    CREDENTIALS = 'credentials/credentials_3.json'

    with open(CREDENTIALS) as json_file:
        credentials = json.load(json_file)
        ID = credentials.get('ID')
        PWD = credentials.get('PWD')

    catelog_numbers = fetch_catelog_numbers(CATELOG_NUMBER_FILE_PATH)

    for id, catelog_number in enumerate(catelog_numbers):
        while fetch_from_space_track_API(ID, PWD, catelog_number, OUTPUT_DIR) is False:
            pass
        print(f'Completed ({id+1}/{len(catelog_numbers)})')
        time.sleep(30)
