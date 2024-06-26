import csv
import json
import math
import os

import ephem

IN_DIR = '/mnt/Storage/OUTPUTs/RAW_TLEs'
OUT_DIR = '/mnt/Storage/OUTPUTs/TLEs'

G: float = 6.67408 * 10**(-11)
M: float = 5.9722*(10**24)
EARTH_RADIUS_M: float = 6378135.0


def convert_to_km(mean_motion: float) -> float:
    return (math.pow(((G * M * ((24*60*60)/mean_motion) ** 2) /
                      (4 * math.pi ** 2)), (1/3)) - EARTH_RADIUS_M)/1000


def CSV_logger(data: dict[str, float | int], csv_file_path: str = "log.csv") -> None:
    '''Write CSV file from dict dataset

    Parameters
    ---------
    data: dict[str, float | int]
        Dataset in dict format (Key, value pair only)

    csv_file_path: str, optional
        CSV file name, default value is `log.csv`
    '''

    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            writer.writeheader()

    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        writer.writerow(data)


for file in sorted(os.listdir(IN_DIR)):
    input_file_path = f'{IN_DIR}/{file}'
    output_file_path = f"{OUT_DIR}/{file.split('.')[0]}.csv"
    # print(input_file_path)
    print(f" > Creating: {output_file_path}")

    with open(input_file_path) as json_file:
        all_tles = json.loads(json_file.read())
        for tle in all_tles:
            _tle = ephem.readtle(
                tle["TLE_LINE0"],
                tle["TLE_LINE1"],
                tle["TLE_LINE2"]
            )

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
