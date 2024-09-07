import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def clean_up(filename: str) -> None:
    '''Remove nan values and format the date and time

    Params
    ------
    filename: str
        Path to the CSV file
    '''

    # By default removes nan values
    df = read_CSV(filename)

    # For consistent date and time formating
    df[TLE.EPOCH] = pd.to_datetime(df[TLE.EPOCH])

    export_as_csv(df, filename)


if __name__ == "__main__":

    PARALLEL_MODE = True

    # ------------------------------------------------------------------
    # OUTPUT FILE(s)
    # ------------------------------------------------------------------

    TLE_CSV_DIR = "artifacts/OUTPUT/HawkEye_360/TLEs"

    # ------------------------------------------------------------------
    # INPUT FILE(s)
    # ------------------------------------------------------------------

    TLE_CSV_DIR = "artifacts/OUTPUT/HawkEye_360/TLEs"

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
