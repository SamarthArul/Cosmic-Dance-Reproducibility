from cosmic_dance.data_processor import *

TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/TLEs'

for file in get_file_names(TLE_DIR_CSV):
    file_path = f"{TLE_DIR_CSV}/{file}"
    df = read_CSV(file_path)

    # Removing file with less than 10 TLEs
    if len(df) < 10:
        print(f" > Remove: {file_path} < 10 TLEs")
        remove_file(file_path)

    elif satellite_age_in_days(df) < 30:
        print(f" > Remove: {file_path} < 30 days")
        remove_file(file_path)
