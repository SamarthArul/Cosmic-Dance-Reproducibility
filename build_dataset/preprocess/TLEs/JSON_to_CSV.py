'''
Convert TLEs from JSON to CSV format
while removing some attributes if not required for the analysis
'''


import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def filter_and_convert_from_JSON(filename: str, output_dir: str):
    '''Filter the required attributes and write into a CSV file (NORAD_CAT_ID.csv)

    Params
    ------
    filename: str
        JSON file path
    output_dir: str
        Output CSV file directory
    '''

    # Reading the JSON file of TLEs
    tles = read_JSON_file(filename)

    # For each TLEs in the JSON file
    for tle in tles:
        # _tle = ephem.readtle(
        #     tle[TLE.LINE0],
        #     tle[TLE.LINE1],
        #     tle[TLE.LINE2]
        # )

        # Building a data data dictionary for each TLEs
        data_dict = {

            # TLE.OBJECT_NAME: tle[TLE.OBJECT_NAME],
            TLE.NORAD_CAT_ID: int(tle[TLE.NORAD_CAT_ID]),
            # TLE.CREATION_DATE: tle[TLE.CREATION_DATE],
            TLE.LAUNCH_DATE: tle[TLE.LAUNCH_DATE],

            TLE.EPOCH: tle[TLE.EPOCH],
            TLE.INCLINATION: float(tle[TLE.INCLINATION]),
            # TLE.RAAN: float(tle[TLE.RA_OF_ASC_NODE]),
            # TLE.ARGP: float(tle[TLE.ARG_OF_PERICENTER]),
            # TLE.ECCENTRICITY: float(tle[TLE.ECCENTRICITY]),
            TLE.ALTITUDE_KM: convert_to_km(float(tle[TLE.MEAN_MOTION])),
            # TLE.MEAN_MOTION: float(tle[TLE.MEAN_MOTION]),
            # TLE.MEAN_ANOMALY: float(tle[TLE.MEAN_ANOMALY]),

            TLE.DRAG: float(tle[TLE.BSTAR]),
            # TLE.DRAG: float(_tle.drag),
            # TLE.LAT: float(math.degrees(_tle.sublat)),
            # TLE.LONG: float(math.degrees(_tle.sublong))

        }

        CSV_logger(data_dict, output_dir)

        # Log probably tracking errors
        # if data[TLE.ALTITUDE_KM] > 650:
        #     print("_____________TLE ERROR____________")
        #     print(
        #         f"""NORAD_CAT_ID: {tle[TLE.NORAD_CAT_ID]}, EPOCH: {tle[TLE.EPOCH]}, ALTITUDE KM: {data[TLE.ALTITUDE_KM]}"""
        #     )
        #     print("_____________________________")
        #     print(tle[TLE.LINE0])
        #     print(tle[TLE.LINE1])
        #     print(tle[TLE.LINE2])
        #     print("_____________________________\n\n")


if __name__ == "__main__":

    PARALLEL_MODE = True

    # INPUT - JSON file Directory
    IN_DIR = "/mnt/Storage/OUTPUTs/Starlink/RAW_TLEs"
    # OUTPUT - CSV file Directory
    OUT_DIR = "/mnt/Storage/OUTPUTs/Starlink/TLEs"

    input(f"Make sure {OUT_DIR} is empty?")

    _count = 0
    if PARALLEL_MODE:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            # for each JSON file in input dir
            for file in get_file_names(IN_DIR):
                input_file_path = f"{IN_DIR}/{file}"
                output_file_path = f"{OUT_DIR}/{file.split('.')[0]}.csv"
                _count += 1
                print(f"|- Processing {file}")

                executor.submit(
                    filter_and_convert_from_JSON, input_file_path, output_file_path
                )

            executor.shutdown()

    # Serial mode
    else:

        # for each JSON file in input dir
        for file in get_file_names(IN_DIR):
            input_file_path = f"{IN_DIR}/{file}"
            output_file_path = f"{OUT_DIR}/{file.split('.')[0]}.csv"
            _count += 1
            print(f"|- Processing {file}")

            filter_and_convert_from_JSON(input_file_path, output_file_path)

    print(f"|\n|- Complete processing {_count} JSON file(s).")
