
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta

plt.rcParams["figure.figsize"] = (20, 10)
plt.rcParams.update({'font.size': 10})
SIZE = 5


def _get_date_marks(sdate: pd.Timestamp, edate: pd.Timestamp):
    date_marks = []
    date_marks.append(sdate)

    while sdate <= edate:
        sdate = sdate+timedelta(weeks=4)
        # sdate = sdate+timedelta(days=1)
        date_marks.append(sdate)

    return date_marks


def plot_in_stack_cat_id_with_nt(
        cat_id: int,
        ldate: pd.Timestamp,

        df_tles: pd.DataFrame,
        df_nt: pd.DataFrame,

        sdate: pd.Timestamp = None,
        edate: pd.Timestamp = None,
        output_dir: str = ''
) -> str:

    # Dates
    if sdate is None or edate is None:
        sdate, edate = df_tles["EPOCH"].min(), df_tles["EPOCH"].max()
    df_nt = df_nt[df_nt["TIMESTAMP"].between(sdate, edate)]

    # Plot
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[-1].set_xticks(_get_date_marks(sdate, edate), minor=False)
    axs[-1].set_xticklabels(axs[-1].get_xticks(), rotation=40)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    axs[0].scatter(df_nt["TIMESTAMP"], df_nt["nT"], label='nT', s=SIZE, c='b')
    axs[0].axhline(y=67, color='r', linestyle='--', label=f'{99}%tile')

    axs[1].scatter(df_tles["EPOCH"], df_tles["KM"], label='KM', s=SIZE, c='g')
    # axs[1].set_ylim(250, 650)
    axs[2].scatter(df_tles["EPOCH"], df_tles["DRAG"],
                   label='DRAG', s=SIZE, c='g')

    axs[0].set_title(f"""CAT_ID: {cat_id} || Ldate: {ldate}""")
    axs[-1].set_xlabel('Epoch')
    axs[0].set_ylabel('nT')
    axs[1].set_ylabel('KM')
    axs[2].set_ylabel('DRAG')

    # axs[0].legend()
    # axs[3].legend()
    # axs[6].legend()

    for i in range(3):
        axs[i].grid('x')
    axs[0].legend()
    plt.tight_layout()

    if len(output_dir):
        plot_file_path = f"{output_dir}/{cat_id}.png"
        plt.savefig(plot_file_path)
        plt.close()
        return plot_file_path
    else:
        plt.show()
        return ''


def plot_in_stack_ldate_with_nt(
    ldate: pd.Timestamp,

    df_tles: pd.DataFrame,
    df_nt: pd.DataFrame,

    sdate: pd.Timestamp = None,
    edate: pd.Timestamp = None,
    output_dir: str = ''
) -> str:

    # Dates
    if sdate is None or edate is None:
        sdate, edate = df_tles["EPOCH"].min(), df_tles["EPOCH"].max()
    df_nt = df_nt[df_nt["TIMESTAMP"].between(sdate, edate)]

    # Plot
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[-1].set_xticks(_get_date_marks(sdate, edate), minor=False)
    axs[-1].set_xticklabels(axs[-1].get_xticks(), rotation=40)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    axs[0].scatter(df_nt["TIMESTAMP"], df_nt["nT"], label='nT', s=SIZE, c='b')
    axs[0].axhline(y=67, color='r', linestyle='--', label=f'{99}%tile')

    axs[1].scatter(df_tles["EPOCH"], df_tles["KM"], label='KM',
                   s=SIZE, c=df_tles["NORAD_CAT_ID"])
    # axs[1].set_ylim(250, 650)
    axs[2].scatter(df_tles["EPOCH"], df_tles["DRAG"],
                   label='DRAG', s=SIZE, c=df_tles["NORAD_CAT_ID"])

    axs[0].set_title(f"""Ldate: {ldate}""")
    axs[-1].set_xlabel('Epoch')
    axs[0].set_ylabel('nT')
    axs[1].set_ylabel('KM')
    axs[2].set_ylabel('DRAG')

    # axs[0].legend()
    # axs[3].legend()
    # axs[6].legend()

    for i in range(3):
        axs[i].grid('x')
    axs[0].legend()
    plt.tight_layout()

    if len(output_dir):
        plot_file_path = f"{output_dir}/{ldate}.png"
        plt.savefig(plot_file_path)
        plt.close()
        return plot_file_path
    else:
        plt.show()
        return ''
