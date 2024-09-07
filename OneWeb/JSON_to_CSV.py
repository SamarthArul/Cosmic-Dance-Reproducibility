import concurrent.futures

from cosmic_dance.io import *
from cosmic_dance.TLEs import *

PARALLEL_MODE = True


# ------------------------------------------------------------------
# OUTPUT FILE(s)
# ------------------------------------------------------------------

# CSV file Directory
CSV_DIR = "artifacts/OUTPUT/OneWeb/TLEs"


# ------------------------------------------------------------------
# INPUT FILE(s)
# ------------------------------------------------------------------

# JSON file Directory
JSON_DIR = "artifacts/OUTPUT/OneWeb/RAW_TLEs"


# ------------------------------------------------------------------


recreate_directories(CSV_DIR)

_count = 0
if PARALLEL_MODE:
    with concurrent.futures.ProcessPoolExecutor() as executor:

        # for each JSON file in input dir
        for file in get_file_names(JSON_DIR):
            input_file_path = f"{JSON_DIR}/{file}"
            output_file_path = f"{CSV_DIR}/{file.split('.')[0]}.csv"
            _count += 1
            print(f"|- Processing {file}")

            executor.submit(
                convert_from_JSON_to_CSV, input_file_path, output_file_path
            )

        executor.shutdown()

# Serial mode
else:

    # for each JSON file in input dir
    for file in get_file_names(JSON_DIR):
        input_file_path = f"{JSON_DIR}/{file}"
        output_file_path = f"{CSV_DIR}/{file.split('.')[0]}.csv"
        _count += 1
        print(f"|- Processing {file}")

        convert_from_JSON_to_CSV(input_file_path, output_file_path)

print(f"|\n|- Complete processing {_count} JSON file(s).")
