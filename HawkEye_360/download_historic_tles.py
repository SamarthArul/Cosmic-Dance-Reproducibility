from cosmic_dance.io import *
from cosmic_dance.TLEs import *


# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

TLE_DOWNLOAD_DIR = "artifacts/OUTPUT/HawkEye_360/RAW_TLEs"

# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

CATELOG_NUMBER_FILE = "artifacts/NORAD_CAT_NUM/HawkEye_360.txt"

# TLE EPOCH start and end date
START_DATE = '2020-01-01'
END_DATA = '2024-06-01'


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
