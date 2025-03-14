'''Remove satellite records based on `clean_up` criteria'''


import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def clean_up(filename: str) -> None:
    '''Remove the file if not match criteria

    Params
    ------
    filename: str
        Path to the CSV file
    '''

    df = read_CSV(filename)

    # Removing file with less than 10 TLEs
    if len(df) < 10:
        print(f"|- Remove: {filename} < 10 TLEs")
        remove_file(filename)
        return

    # For consistent date and time formating
    df[TLE.EPOCH] = pd.to_datetime(df[TLE.EPOCH])

    # Removing file with satellite age below 30 days
    if satellite_age_in_days(df) < 30:
        print(f"|- Remove: {filename} < 30 days")
        remove_file(filename)
        return

    # Removing TLEs outside operation altitude
    _df = df[df[TLE.ALTITUDE_KM] < 650]
    if len(_df) < len(df):
        print(f"|- Invalid TLEs: {filename}: {len(df)-len(_df)}")

    export_as_csv(_df, filename)


if __name__ == "__main__":

    PARALLEL_MODE = False

    # ------------------------------------------------------------------
    # OUTPUT FILE(s)
    # ------------------------------------------------------------------

    TLE_CSV_DIR = "artifacts/OUTPUT/Starlink/TLEs"

    # ------------------------------------------------------------------
    # INPUT FILE(s)
    # ------------------------------------------------------------------

    TLE_CSV_DIR = "artifacts/OUTPUT/Starlink/TLEs"

    # ------------------------------------------------------------------

    # Confirm
    input(f" File(s) in ({TLE_CSV_DIR}) might get altered ? ")

    if PARALLEL_MODE:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            # For each file in that dir
            for file in get_file_names(TLE_CSV_DIR):
                file_path = f"{TLE_CSV_DIR}/{file}"

                executor.submit(clean_up, file_path)

            executor.shutdown()

    # Serial mode
    else:

        # For each file in that dir
        for file in get_file_names(TLE_CSV_DIR):
            file_path = f"{TLE_CSV_DIR}/{file}"

            clean_up(file_path)

    print(f'|\n|- Complete.')
