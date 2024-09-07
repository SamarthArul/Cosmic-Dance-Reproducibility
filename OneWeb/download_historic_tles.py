from cosmic_dance.io import *
from cosmic_dance.TLEs import *


# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

TLE_DOWNLOAD_DIR = "artifacts/OUTPUT/OneWeb/RAW_TLEs"

# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

CATELOG_NUMBER_FILE = "artifacts/NORAD_CAT_NUM/OneWebCatIDs.txt"
# CATELOG_NUMBER_FILE = "artifacts/OUTPUT/Starlink/NewOneWebCatIDs.txt"  # Only download new launched satellites

# TLE EPOCH start and end date
START_DATE = '2020-01-01'
END_DATA = '2024-08-01'


CREDENTIALS = [
    "credentials/credentials_1.json",
    "credentials/credentials_2.json",
    "credentials/credentials_3.json"
]

# ------------------------------------------------------------------


# Confirm
input(f"Confirm download directory ({TLE_DOWNLOAD_DIR})? ")

create_directories(TLE_DOWNLOAD_DIR)

# Read credentials and catelog numbers
credentials = read_credentials(CREDENTIALS)
catelog_numbers = read_catalog_number_list(
    CATELOG_NUMBER_FILE,
    in_order=True
)

download_TLEs(
    catelog_numbers,
    credentials,
    START_DATE,
    END_DATA,
    TLE_DOWNLOAD_DIR
)
