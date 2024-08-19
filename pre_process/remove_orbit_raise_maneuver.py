'''Removing the TLEs before satellites deployed into designated operational altitude'''


import concurrent.futures

from cosmic_dance.data_processor import *


def strip_orbit_raise_maneuver(sat_TLEs_in_CSV: str, orbit_raise_df: pd.DataFrame):
    '''Remove all the TLEs before ORBIT_RAISE_COMEPLETE date

    Params
    ------
    sat_TLEs_in_CSV: str
        CSV file path
    orbit_raise_df: pd.DataFrame
        DataFrame of orbit raise date CSV file 
    '''
    TLE_df = read_TLEs_in_CSV(sat_TLEs_in_CSV)

    # Get the launch date
    launch_date = TLE_df.iloc[-1]["LAUNCH_DATE"]

    # Query the row
    row = orbit_raise_df[orbit_raise_df["LAUNCH_DATE"] == launch_date]

    if len(row) == 1:
        # Found a record, remove TLEs upto orbit raise complete
        maneuver_complete_date = row.iloc[-1]["ORBIT_RAISE_COMEPLETE"]
        TLE_df = TLE_df[TLE_df["EPOCH"] > maneuver_complete_date]
        write_CSV(TLE_df, sat_TLEs_in_CSV)
        print(f'|- UPDATED:{launch_date} > {sat_TLEs_in_CSV}')

    else:
        # Record not found, new launch remove the file
        remove_file(sat_TLEs_in_CSV)
        print(f'|- REMOVED:{launch_date} > {sat_TLEs_in_CSV}')


if __name__ == '__main__':
    TLE_CSV_DIR = "/mnt/Storage/OUTPUTs/Starlink/TLEs"
    ORBIT_RAISE_CSV = "artifacts/starlink_orbit_raise.csv"

    orbit_raise_df = read_orbit_raise_CSV(ORBIT_RAISE_CSV)

    # Path to all CSV files
    list_of_sat_TLEs_in_CSV = [
        f'{TLE_CSV_DIR}/{csv_filename}' for csv_filename in get_file_names(TLE_CSV_DIR)
    ]

    with concurrent.futures.ProcessPoolExecutor() as executor:

        # For all satellites
        for sat_TLEs_in_CSV in list_of_sat_TLEs_in_CSV:
            executor.submit(
                strip_orbit_raise_maneuver,
                sat_TLEs_in_CSV, orbit_raise_df
            )

        executor.shutdown()
        print('|\n|- Comeplete.')
