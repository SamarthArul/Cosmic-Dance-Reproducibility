

import pandas as pd

from cosmic_dance.io import fetch_from_url


class DST:
    '''Data attributes for Dst index'''
    TIMESTAMP = "TIMESTAMP"
    NANOTESLA = "nT"


def parse_dst_index(urls: list[str]) -> pd.DataFrame:
    '''Request content from the given URLs in given order and generates a Dataframe with timestamp and intensity (nT)

    Params
    -------
    urls: list[str]
        List of URLs, in order (month wise)

    Returns
    -------
    pd.DataFrame: Dataframe of Dst index
    '''

    dst_index_records = []

    for id, url in enumerate(urls):
        print(f"|- ({id+1}/{len(urls)}): {url}")

        # Fetch and parse the content
        content = fetch_from_url(url)
        content = content.split('\n')[:-3]

        for line in content:

            # Extract Year, Month, Date
            yy = line[3:5]
            mm = line[5:7]
            dd = line[8:10]

            # Extract hourly value with timestamp
            h = 0
            for index in range(20, 116, 4):
                date = pd.to_datetime(
                    f"20{yy}-{mm}-{dd} {str(h).rjust(2, '0')}:00:00"
                )
                nT = int(line[index:index+4].strip())

                h += 1

                # Store the records
                dst_index_records.append({
                    DST.TIMESTAMP: date,
                    DST.NANOTESLA: nT
                })

    # create Dataframe
    return pd.DataFrame.from_dict(dst_index_records)
