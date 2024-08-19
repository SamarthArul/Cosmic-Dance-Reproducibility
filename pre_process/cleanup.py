'''Remove satellite records based on criteria'''


from cosmic_dance.data_processor import *
import concurrent.futures


def clean_up(file_path: str) -> None:
    '''Remove the file if not match criteria

    Params
    ------
    file_path: str
        Path to the CSV file
    '''

    df = read_CSV(file_path)

    # Removing file with less than 10 TLEs
    if len(df) < 10:
        print(f"|- Remove: {file_path} < 10 TLEs")
        remove_file(file_path)

    # Removing file with satellite age below 30 days
    elif satellite_age_in_days(df) < 30:
        print(f"|- Remove: {file_path} < 30 days")
        remove_file(file_path)


if __name__ == '__main__':
    TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/Starlink/TLEs'

    with concurrent.futures.ProcessPoolExecutor() as executor:

        # For each file in that dir
        for file in get_file_names(TLE_DIR_CSV):
            file_path = f"{TLE_DIR_CSV}/{file}"

            executor.submit(
                clean_up, file_path
            )

        executor.shutdown()
        print(f'|\n|- Complete.')
