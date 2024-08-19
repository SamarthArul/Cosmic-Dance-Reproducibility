'''Convert TLEs from JSON to CSV format while removing some attributes'''


import concurrent.futures
import json
import math
import os

import ephem

from cosmic_dance.data_processor import CSV_logger

G: float = 6.67408 * 10**(-11)
M: float = 5.9722*(10**24)
EARTH_RADIUS_M: float = 6378135.0


def convert_to_km(mean_motion: float) -> float:
    '''Calculate altitude in km from mean motion of satellites

    Params
    ------
    mean_motion: float
        Mean motion from TLE

    Returns
    -------
        Altitude in km (float)
    '''
    return (math.pow(((G * M * ((24*60*60)/mean_motion) ** 2) /
                      (4 * math.pi ** 2)), (1/3)) - EARTH_RADIUS_M)/1000


def filter_and_convert_to_JSON(input_file_path: str, output_file_path: str) -> None:
    '''Filter the the required attributes and write into a CSV files

    Params
    ------
    input_file_path: str
        Input JSON file path
    output_file_path: str
        Output CSV file path
    '''

    # Reading the JSON file of TLEs
    with open(input_file_path) as json_file:
        all_tles = json.loads(json_file.read())

        if len(all_tles):
            print(f"|- Creating file: {output_file_path}")
        else:
            print(f"|- Empty file: {input_file_path}")

        # For each TLEs in the JSON file
        for tle in all_tles:
            _tle = ephem.readtle(
                tle["TLE_LINE0"],
                tle["TLE_LINE1"],
                tle["TLE_LINE2"]
            )

            # Building a data data dictionary for each TLEs
            data = {
                # "OBJECT_NAME": tle["OBJECT_NAME"],
                "NORAD_CAT_ID": int(tle["NORAD_CAT_ID"]),
                # "CREATION_DATE": tle["CREATION_DATE"],
                "LAUNCH_DATE": tle["LAUNCH_DATE"],

                "EPOCH": tle["EPOCH"],
                # "INCLINATION": float(tle["INCLINATION"]),
                # "RAAN": float(tle["RA_OF_ASC_NODE"]),
                # "ARGP": float(tle["ARG_OF_PERICENTER"]),
                # "ECCENTRICITY": float(tle["ECCENTRICITY"]),
                "KM": convert_to_km(float(tle["MEAN_MOTION"])),
                # "MEAN_ANOMALY": float(tle["MEAN_ANOMALY"]),

                "DRAG": float(_tle.drag),
                # "LAT": float(math.degrees(_tle.sublat)),
                # "LONG": float(math.degrees(_tle.sublong))
            }

            CSV_logger(data, output_file_path)


if __name__ == '__main__':
    # Input and output directories
    IN_DIR = '/mnt/Storage/OUTPUTs/Starlink/RAW_TLEs'
    OUT_DIR = '/mnt/Storage/OUTPUTs/Starlink/TLEs'

    input(f'Make sure {OUT_DIR} is empty?')

    with concurrent.futures.ProcessPoolExecutor() as executor:

        # for each JSON file in input dir
        _count = 0
        for file in sorted(os.listdir(IN_DIR)):
            input_file_path = f'{IN_DIR}/{file}'
            output_file_path = f"{OUT_DIR}/{file.split('.')[0]}.csv"
            _count += 1

            executor.submit(
                filter_and_convert_to_JSON, input_file_path, output_file_path
            )

        executor.shutdown()
        print(f'|\n|- Complete processing {_count} JSON file(s).')
