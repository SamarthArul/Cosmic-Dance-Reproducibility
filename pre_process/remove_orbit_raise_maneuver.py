from cosmic_dance.data_processor import *


TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/TLEs'
ORBIT_RAISE_CSV = '/home/suvam/Projects/CosmicDance/CSVs/starlink_orbit_raise.csv'

orbit_raise_df = read_orbit_raise_CSV(ORBIT_RAISE_CSV)


list_of_sat_TLEs_in_CSV = [
    f'{TLE_DIR_CSV}/{csv_filename}' for csv_filename in get_file_names(TLE_DIR_CSV)
]


for csv_file in list_of_sat_TLEs_in_CSV:
    print(f' > {csv_file}')
    TLE_df = read_TLEs_in_CSV(csv_file)

    launch_date = TLE_df.iloc[-1]["LAUNCH_DATE"]
    row = orbit_raise_df[orbit_raise_df["LAUNCH_DATE"] == launch_date]

    if len(row) == 1:
        maneuver_complete_date = row.iloc[-1]["ORBIT_RAISE_COMEPLETE"]
        TLE_df = TLE_df[TLE_df["EPOCH"] > maneuver_complete_date]
        write_CSV(TLE_df, csv_file)
    else:
        print(f' > REMOVED:{launch_date} - {csv_file}')
        remove_file(csv_file)
