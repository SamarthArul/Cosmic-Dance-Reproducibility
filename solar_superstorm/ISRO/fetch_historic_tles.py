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


if __name__ == '__main__':

    START_DATE = '2020-01-01'
    END_DATA = '2024-06-01'

    # 1
    OUTPUT_DIR = '/mnt/Storage/OUTPUTs/ISRO/RAW_TLEs'
    CREDENTIALS = 'credentials/credentials_1.json'

    with open(CREDENTIALS) as json_file:
        credentials = json.load(json_file)
        ID = credentials.get('ID')
        PWD = credentials.get('PWD')

    catelog_numbers = [
        44804,  # CARTOSAT-3
        44857,  # RISAT-2BR1
        46905,  # RISAT-2BR2
        44233,  # RISAT-2B
        51656,  # EOS-4
        36795,  # CARTOSAT-2B
        54361,  # EOS-6
        58694,  # XPOSAT
        41877,  # RESOURCESAT-2A
        55562,  # EOS-7
    ]

    for id, catelog_number in enumerate(catelog_numbers):
        while fetch_from_space_track_API(ID, PWD, catelog_number, OUTPUT_DIR) is False:
            pass
        print(f'Completed ({id+1}/{len(catelog_numbers)})')
        time.sleep(30)
