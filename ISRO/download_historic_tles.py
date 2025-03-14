from cosmic_dance.io import *
from cosmic_dance.TLEs import *

# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

TLE_DOWNLOAD_DIR = "artifacts/OUTPUT/ISRO/RAW_TLEs"

# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------


# TLE EPOCH start and end date
START_DATE = '2020-01-01'
END_DATA = '2024-06-01'

CREDENTIALS = [
    "credentials/credentials_1.json",
    "credentials/credentials_2.json",
    "credentials/credentials_3.json",
    "credentials/credentials_4.json",
    "credentials/credentials_5.json",
    "credentials/credentials_6.json",
    "credentials/credentials_7.json",
    "credentials/credentials_8.json",
    "credentials/credentials_9.json",
    "credentials/credentials_10.json"
]

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

# ------------------------------------------------------------------


# Confirm
input(f"Confirm download directory ({TLE_DOWNLOAD_DIR})? ")

create_directories(TLE_DOWNLOAD_DIR)

# Read credentials and catelog numbers
credentials = read_credentials(CREDENTIALS)


download_TLEs(
    catelog_numbers,
    credentials,
    START_DATE,
    END_DATA,
    TLE_DOWNLOAD_DIR
)
