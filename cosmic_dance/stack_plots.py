
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["figure.figsize"] = (20, 10)
plt.rcParams.update({'font.size': 20})
SIZE = 5


def get_CDF(data: pd.Series) -> tuple[np.array, np.array]:
    '''Get X and Y axis values for Cumulative distribution function

    Params
    ------
    data: pd.Series
        List of data points

    Returns
    -------
    tuple[np.array, np.array] X and Y axis values
    '''

    x = np.sort(data)
    y = np.arange(len(data)) / float(len(data))
    return x, y


def get_date_marks(sdate: pd.Timestamp, edate: pd.Timestamp, time_delta: pd.Timedelta) -> list[pd.Timestamp]:
    '''Create list of time stamps

    Params
    ------
    sdate: pd.Timestamp
        Start timestamp
    edate: pd.Timestamp
        End timestamp
    time_delta: pd.Timedelta
        Time interval

    Returns
    --------
    list[pd.Timestamp]
        List of timestamp
    '''

    date_marks: list[pd.Timestamp] = []

    date_marks.append(sdate)
    while sdate <= edate:
        sdate += time_delta
        date_marks.append(sdate)

    return date_marks


def plot_in_stack_with_nt(
    df_tles: pd.DataFrame,
    df_nt: pd.DataFrame,

    time_delta: pd.Timedelta,


    sdate: pd.Timestamp = None,
    edate: pd.Timestamp = None,
    title: str = None,
    filename: str = None
) -> str | None:
    '''Plot time series grouped by satellite launch date NORAD_CAT_ID color coded

    Params
    ------
    df_tles: pd.DataFrame
        TLE DataFrame
    df_nt: pd.DataFrame
        Dst index DataFrame

    time_delta: pd.Timedelta
        X axis marking time interval

    sdate: pd.Timestamp = None
        Start timestamp, optional
    edate: pd.Timestamp = None
        End timestamp, optional
    title: str
        Figure title, optional
    filename: str, optional
        Outpur directory path, optional

    Returns
    --------
    str
        PNG file name
    '''

    # Dates
    if sdate is None:
        sdate = df_tles["EPOCH"].min()
    if edate is None:
        edate = df_tles["EPOCH"].max()

    # Plot
    fig, axs = plt.subplots(3, 1, sharex=True)

    # Dst Index
    axs[0].scatter(
        df_nt["TIMESTAMP"], df_nt["nT"],

        label='nT',
        s=SIZE,
        c='b'
    )
    axs[0].axhline(
        y=67,

        color='r',
        linestyle='--',
        label=f'{99}%tile'
    )

    # Altitude
    axs[1].scatter(
        df_tles["EPOCH"], df_tles["KM"],
        label='KM',
        s=SIZE,
        c=df_tles["NORAD_CAT_ID"]
    )
    axs[1].set_ylim(250, 650)

    # Drag
    axs[2].scatter(
        df_tles["EPOCH"], df_tles["DRAG"],

        label='DRAG',
        s=SIZE,
        c=df_tles["NORAD_CAT_ID"]
    )

    #  Timeseties (x axis marking)
    axs[-1].set_xticks(get_date_marks(sdate, edate, time_delta), minor=False)
    axs[-1].set_xticklabels(axs[-1].get_xticks(), rotation=40)
    axs[-1].set_xlabel('Epoch')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    if title:
        axs[0].set_title(title)

    # Y axis
    axs[0].set_ylabel('nT')
    axs[1].set_ylabel('KM')
    axs[2].set_ylabel('DRAG')

    for i in range(3):
        axs[i].grid('x')
    axs[0].legend()

    if len(filename):
        plt.tight_layout()
        # plt.savefig(plot_file_path, dpi=300)
        plt.savefig(filename)
        plt.close()
        return filename
    else:
        plt.show()
