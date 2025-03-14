'''
Fetch all TLEs (from START_DATE to END_DATE) from https://www.space-track.org API by a satellite NORAD Catalog Number
- Requests are distributed across multiple credentials
- Each credential respects a 2-second delay between requests (max 30 requests/minute)
- Saves JSON files into the specified directory
'''

import os
import json
import time
from cosmic_dance.io import *
from cosmic_dance.TLEs import *

# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

TLE_DOWNLOAD_DIR = "artifacts/OUTPUT/Starlink/RAW_TLEs_2"

# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

CATELOG_NUMBER_FILE = "artifacts/NORAD_CAT_NUM/StarlinkCatIDs.txt"
# CATELOG_NUMBER_FILE = "artifacts/OUTPUT/Starlink/NewStarlinkCatIDs.txt"  # Only download new launched satellites

# TLE EPOCH start and end date
START_DATE = '2020-01-01'
END_DATE = '2025-03-01'

CREDENTIALS = [
    "credentials/credentials_1.json",
    "credentials/credentials_2.json",
    "credentials/credentials_3.json",
    "credentials/credentials_4.json"
]

# ------------------------------------------------------------------

def find_missing_satellites(catalog_numbers: list[int], output_dir: str) -> list[int]:
    """Find satellites that:
    1. Don't have JSON files
    2. Have empty JSON files
    3. Have JSON files containing error messages
    """
    missing = []
    for sat_num in catalog_numbers:
        json_file = f"{output_dir}/{sat_num}.json"
        
        # Check if file exists
        if not os.path.exists(json_file):
            print(f"File missing for satellite {sat_num}")
            missing.append(sat_num)
            continue
            
        # Check if file is empty
        if os.path.getsize(json_file) == 0:
            print(f"Empty file for satellite {sat_num}")
            missing.append(sat_num)
            continue
            
        # Check file contents for errors
        try:
            with open(json_file, 'r') as f:
                content = f.read()
                # Check for various error indicators
                if any(error_text in content for error_text in [
                    '"error":', 
                    'You\'ve exceeded', 
                    'rate limit'
                ]):
                    print(f"Error in file for satellite {sat_num}")
                    missing.append(sat_num)
                    continue
                
                # Also check if it's valid JSON and has actual data
                data = json.loads(content)
                if not data or (isinstance(data, list) and len(data) == 0):
                    print(f"Empty JSON data for satellite {sat_num}")
                    missing.append(sat_num)
                    continue
                    
        except json.JSONDecodeError:
            print(f"Invalid JSON for satellite {sat_num}")
            missing.append(sat_num)
        except Exception as e:
            print(f"Error checking satellite {sat_num}: {str(e)}")
            missing.append(sat_num)
            
    return missing

# Confirm directory and create if needed
input(f"Confirm download directory ({TLE_DOWNLOAD_DIR})? ")
create_directories(TLE_DOWNLOAD_DIR)

# Read credentials and catalog numbers
credentials = read_credentials(CREDENTIALS)
catalog_numbers = read_catalog_number_list(
    CATELOG_NUMBER_FILE,
    in_order=True
)

# Find missing satellites
missing_numbers = find_missing_satellites(catalog_numbers, TLE_DOWNLOAD_DIR)

if missing_numbers:
    print(f"\nFound {len(missing_numbers)} satellites needing download:")
    print(f"First few satellites to process:", missing_numbers[:5], "...")
    
    # Save list with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    missing_file = f"{TLE_DOWNLOAD_DIR}/missing_satellites_{timestamp}.txt"
    with open(missing_file, 'w') as f:
        for sat in missing_numbers:
            f.write(f"{sat}\n")
    print(f"Full list saved to: {missing_file}")
    
    input("Press Enter to start downloading missing satellites...")
    
    # Download using the improved multi-credential method
    download_TLEs(
        missing_numbers,
        credentials,
        START_DATE,
        END_DATE,
        TLE_DOWNLOAD_DIR
    )
else:
    print("No missing satellites found! All files exist.")