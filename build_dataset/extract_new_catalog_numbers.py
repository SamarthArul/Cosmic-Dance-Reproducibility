'''
Fetch all recent TLEs from celestrak and update the list of NORAD Catalog Number with new launched satellites
'''

from cosmic_dance.io import *
from cosmic_dance.TLEs import *


URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"

# Files
TLE_FILE = "/mnt/Storage/OUTPUTs/Starlink/Starlink.tle"

OLD_CAT_IDS = "artifacts/NORAD_CAT_NUM/StarlinkCatIDs.txt"
NEW_CAT_IDS = "NewStarlinkCatIDs.txt"


# Fetch recent TLEs from celestrak and write into a file
write_to_file(
    fetch_from_url(URL),
    TLE_FILE
)

# Find new NORAD Catalog Numbers and update the old list of NORAD Catalog Numbers with new one
find_new_catalog_numbers(TLE_FILE, OLD_CAT_IDS, NEW_CAT_IDS)
