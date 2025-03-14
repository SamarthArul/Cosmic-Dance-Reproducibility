'''Removing the TLEs before satellites deployed into designated operational altitude'''


import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *


def strip_orbit_raise_maneuver(filename: str, orbit_raise_df: pd.DataFrame):
    '''Remove all the TLEs before ORBIT_RAISE_COMEPLETE

    Params
    ------
    filename: str
        CSV file (NORAD_CAT_ID.csv)
    orbit_raise_df: pd.DataFrame
        DataFrame of orbit raise
    '''

    df_TLE = read_TLEs_in_CSV(filename)

    # Get the launch date
    launch_date = df_TLE.iloc[-1][TLE.LAUNCH_DATE]

    # Query the row
    row = orbit_raise_df[orbit_raise_df[TLE.LAUNCH_DATE] == launch_date]

    # Found a record, remove TLEs upto orbit raise complete
    if len(row) == 1:

        maneuver_complete_date = row.iloc[-1]["ORBIT_RAISE_COMEPLETE"]

        df_TLE = df_TLE[df_TLE[TLE.EPOCH] > maneuver_complete_date]
        export_as_csv(df_TLE, filename)

        print(f'|- UPDATED:{launch_date} > {filename}')

    # Record not found, new launch remove the file
    else:

        remove_file(filename)
        print(f'|- REMOVED:{launch_date} > {filename}')


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
    ORBIT_RAISE_CSV = "artifacts/starlink_orbit_raise.csv"

    # ------------------------------------------------------------------

    # Confirm
    input(f" File(s) in ({TLE_CSV_DIR}) might get altered? ")

    orbit_raise_df = read_orbit_raise_CSV(ORBIT_RAISE_CSV)

    # Complete path to all CSV files
    list_of_sat_TLEs_in_CSV = [
        f'{TLE_CSV_DIR}/{csv_filename}' for csv_filename in get_file_names(TLE_CSV_DIR)
    ]

    if PARALLEL_MODE:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            # For all satellites
            for sat_TLEs_in_CSV in list_of_sat_TLEs_in_CSV:

                executor.submit(
                    strip_orbit_raise_maneuver,
                    sat_TLEs_in_CSV, orbit_raise_df
                )

            executor.shutdown()

    # Serial mode
    else:

        # For all satellites
        for sat_TLEs_in_CSV in list_of_sat_TLEs_in_CSV:
            strip_orbit_raise_maneuver(sat_TLEs_in_CSV, orbit_raise_df)

    print('|\n|- Comeplete.')
