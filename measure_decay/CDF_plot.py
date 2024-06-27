import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

from cosmic_dance.data_processor import *

plt.rcParams.update({'font.size': 20})

CSV_FILE_PATH = "/home/suvam/Projects/CosmicDance/altitude_decay_after_1_5_10.csv"
TITLE = 'All Starlink Sat absolute diff'
FILE_NAME = 'CDF_of_altitude_drop_99.png'

df = pd.read_csv(CSV_FILE_PATH)
df = df.drop_duplicates()

fig, ax = plt.subplots(figsize=(20, 10))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))


# df = df[df["KM_after_DAY_1"] < 199]
x, y = get_CDF(df["KM_after_DAY_1"])
_df = pd.DataFrame({"X": x, "Y": y})
_df = _df[_df["Y"] > 0.98]
ax.scatter(
    _df["X"], _df["Y"],
    color='g', s=5, marker="o",
    label='After 1 days'
)

# df = df[df["KM_after_DAY_5"] < 199]
x, y = get_CDF(df["KM_after_DAY_5"])
_df = pd.DataFrame({"X": x, "Y": y})
_df = _df[_df["Y"] > 0.98]
ax.scatter(
    _df["X"], _df["Y"],
    color='b', s=5, marker="^",
    label='After 5 days'
)


# df = df[df["KM_after_DAY_10"] < 199]
x, y = get_CDF(df["KM_after_DAY_10"])
_df = pd.DataFrame({"X": x, "Y": y})
_df = _df[_df["Y"] > 0.98]
ax.scatter(
    _df["X"], _df["Y"],
    color='r', s=5, marker="D",
    label='After 10 days'
)

# plt.xlabel('Absolute altitude difference (km)')
plt.xlabel('Altitude drop (km)')
plt.ylabel('CDF')

# plt.xlim(0, 180)
plt.grid()
plt.legend()
plt.tight_layout()

# plt.show()
plt.savefig(FILE_NAME, dpi=300)
plt.close()
