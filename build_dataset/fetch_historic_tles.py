'''
Fetch all TLEs (from START_DATE to END_DATA) from https://www.space-track.org API by a satellite NORAD Catalog Number
- Request for each NORAD Catalog Number
- Save JSON file into given directory
'''


import time

from cosmic_dance.io import *

# TLE query start and end dates
START_DATE = '2020-01-01'
END_DATA = '2024-08-01'

# Input and output files
# CATELOG_NUMBER_FILE_PATH = "artifacts/NORAD_CAT_NUM/StarlinkCatIDs.txt"
CATELOG_NUMBER_FILE_PATH = "NewStarlinkCatIDs.txt"
OUTPUT_DIR = "/mnt/Storage/OUTPUTs/Starlink/_TLEs"
CREDENTIALS = [
    "credentials/credentials_1.json",
    "credentials/credentials_2.json",
    "credentials/credentials_3.json"
]

# Confirm
input(f"Confirm output file ({OUTPUT_DIR})? ")

# Read credentials and catelog numbers
credentials = read_credentials(CREDENTIALS)
catelog_numbers = read_catalog_number_list(
    CATELOG_NUMBER_FILE_PATH,
    in_order=True
)

# Fetch TLEs using credentials
for id, catelog_number in enumerate(catelog_numbers):
    username = credentials[id % len(credentials)].get('ID')
    password = credentials[id % len(credentials)].get('PWD')

    # Retry if failed
    while fetch_from_space_track_API(username, password, catelog_number, START_DATE, END_DATA, OUTPUT_DIR) is False:
        print(f"|- Error: {catelog_number}, waiting...")
        time.sleep(30)

    print(
        f"|- Completed: {catelog_number}, Progress ({id+1}/{len(catelog_numbers)})"
    )

    # Wating to stay under the request limit
    if 0 == id % len(credentials):
        time.sleep(30)
