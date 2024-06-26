import ephem


catalog_number_list = list()
catalog_number_set = set()


def read_tles(filename_tles):
    with open(filename_tles, 'r') as f:
        for tles_line_1 in f:
            tles_line_2 = f.readline()
            tles_line_3 = f.readline()
            tle = ephem.readtle(tles_line_1, tles_line_2, tles_line_3)
            print(tle.catalog_number)
            catalog_number_list.append(tle.catalog_number)
            catalog_number_set.add(tle.catalog_number)


if __name__ == '__main__':

    # https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle
    TLE_FILE = "/mnt/Storage/OUTPUTs/starlink.tle"

    # https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=tle
    # TLE_FILE = "/mnt/Storage/LEO-NET/ResultsSolarSuperstorm/2024_OneWebTLEs/OneWeb.tle"

    read_tles(TLE_FILE)

    # print('List: ', len(catalog_number_list))
    # print('Set: ', len(catalog_number_set))
