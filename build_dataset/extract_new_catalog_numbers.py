'''
Fetch all recent TLEs from celestrak and update the list of NORAD Catalog Number with new launched satellites
'''

import ephem
import requests

current_catalog_number_set: set[str] = set()

old_catalog_number_set: set[str] = set()
new_catalog_number_set: set[str] = set()


def extract_catalog_numbers(filename_tles: str):
    '''Extracts NORAD Catalog Number for the TLEs

    Params
    ---------
    filename_tles: string
        TLE file path
    '''

    with open(filename_tles, 'r') as f:
        for tles_line_1 in f:
            tles_line_2 = f.readline()
            tles_line_3 = f.readline()
            tle = ephem.readtle(tles_line_1, tles_line_2, tles_line_3)
            current_catalog_number_set.add(tle.catalog_number)


def write_tles(filename_tles: str, content: str):
    '''Write into a file

    Params
    ------
    filename_tles: string
        File path
    content: string
        File content
    '''

    with open(filename_tles, 'w') as f:
        f.write(content)


def read_old_cat_ids(filename: str):
    '''Read file with a list of NORAD Catalog Number

    Params
    ------
    filename: string
        File path
    '''

    with open(filename) as f:
        for id in f.read().strip().split('\n'):
            old_catalog_number_set.add(int(id))


def find_new_ids():
    'Find new NORAD Catalog Numbers maybe new launched'

    print(f"|- New IDs")
    for cid in current_catalog_number_set:
        if cid not in old_catalog_number_set:
            print(f"|-- {cid}")
            new_catalog_number_set.add(cid)
            old_catalog_number_set.add(cid)


def write_cat_ids(filename_tles: str, catalog_number_set: set[int]):
    '''Write file with a list of NORAD Catalog Number line by line

    Params
    ------
    filename_tles: string
        File path
    catalog_number_set: set[int]
        Set of NORAD Catalog Numbers
    '''

    with open(filename_tles, 'w') as f:
        for cat_id in catalog_number_set:
            f.write(f"{cat_id}\n")


if __name__ == '__main__':

    URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"

    # Files
    TLE_FILE = "/mnt/Storage/OUTPUTs/Starlink/Starlink.tle"

    OLD_CAT_IDS = "artifacts/NORAD_CAT_NUM/StarlinkCatIDs.txt"
    NEW_CAT_IDS = "NewStarlinkCatIDs.txt"

    # Fetch recent TLEs from celestrak
    response = requests.get(URL)
    assert response.ok

    # Write recent TLEs
    write_tles(TLE_FILE, response.text)
    print(f"|- Written: {TLE_FILE}")

    # Get the NORAD Catalog Numbers from recent TLEs
    extract_catalog_numbers(TLE_FILE)
    print(f"|- Extracted all CAT IDs")

    # OLD NORAD Catalog Number
    read_old_cat_ids(OLD_CAT_IDS)
    print(f"|- Read old CAT IDs")

    # Extract new NORAD Catalog Number
    find_new_ids()

    # Write new NORAD Catalog Numbers
    write_cat_ids(NEW_CAT_IDS, new_catalog_number_set)
    print(f"|- Written new IDs: {NEW_CAT_IDS}")

    # Update the old file with new NORAD Catalog Number
    write_cat_ids(OLD_CAT_IDS, old_catalog_number_set)
    print(f"|- Updated old CAT IDs: {OLD_CAT_IDS}")
