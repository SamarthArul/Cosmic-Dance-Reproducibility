
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from cosmic_dance.dst_index import DST
from cosmic_dance.TLEs import TLE

plt.rcParams["figure.figsize"] = (20, 10)
plt.rcParams.update({'font.size': 20})

SIZE = 5
PTILE = 99


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


    sdate: pd.Timestamp | None = None,
    edate: pd.Timestamp | None = None,
    title: str | None = None,
    filename: str | None = None

) -> str | None:
    '''Plot time series grouped by satellite launch date NORAD_CAT_ID color coded

    Params
    ------
    df_tles: pd.DataFrame
        DataFrame of TLEs
    df_nt: pd.DataFrame
        DataFrame of Dst index

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

    # Take start and end date of TLEs if sdate and edate not given
    if sdate is None:
        sdate = df_tles[TLE.EPOCH].min()
    if edate is None:
        edate = df_tles[TLE.EPOCH].max()

    # Plot
    fig, axs = plt.subplots(3, 1, sharex=True)

    # Dst Index
    axs[0].scatter(
        df_nt[DST.TIMESTAMP], df_nt[DST.NANOTESLA],

        label='nT',
        s=SIZE,
        c='b'
    )
    axs[0].axhline(
        y=percentile(df_nt[DST.NANOTESLA], PTILE),

        color='r',
        linestyle='--',
        label=f'{PTILE}%tile'
    )

    # Altitude
    axs[1].scatter(
        df_tles[TLE.EPOCH], df_tles[TLE.ALTITUDE_KM],
        label='KM',
        s=SIZE,
        c=df_tles[TLE.NORAD_CAT_ID]
    )
    axs[1].set_ylim(250, 650)

    # Drag
    axs[2].scatter(
        df_tles[TLE.EPOCH], df_tles[TLE.DRAG],

        label='DRAG',
        s=SIZE,
        c=df_tles[TLE.NORAD_CAT_ID]
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

    # Save if filename is given
    if len(filename):
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        return filename

    else:
        plt.show()
