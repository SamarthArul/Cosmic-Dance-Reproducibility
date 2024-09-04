'''Fetch all recent TLEs from celestrak and update the list of NORAD Catalog Number with new launched satellites'''

from cosmic_dance.io import *
from cosmic_dance.TLEs import *

OUTPUT_DIR = f"{OUTPUT_DIR}/Starlink"

# INPUT FILE(s)
OLD_CAT_IDS = "artifacts/NORAD_CAT_NUM/StarlinkCatIDs.txt"
URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"


# OUTPUT FILE(s)
TLE_FILE = f"{OUTPUT_DIR}/Starlink.tle"
NEW_CAT_IDS = f"{OUTPUT_DIR}/NewStarlinkCatIDs.txt"

# Confim before write
input(f" OUTPUT file: ({TLE_FILE})")
input(f" OUTPUT file: ({NEW_CAT_IDS})")

# Create OUTPUT directory
create_directories(OUTPUT_DIR)

# Fetch recent TLEs from celestrak and write into a file
write_to_file(
    fetch_from_url(URL),
    TLE_FILE
)

# Find new NORAD Catalog Numbers and update the old list of NORAD Catalog Numbers with new one
find_new_catalog_numbers(TLE_FILE, OLD_CAT_IDS, NEW_CAT_IDS)
