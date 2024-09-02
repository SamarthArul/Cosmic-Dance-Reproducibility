import ephem

from cosmic_dance.io import *


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
