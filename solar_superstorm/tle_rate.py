import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from cosmic_dance.data_processor import *

# TLE_DIR_CSV = '/mnt/Storage/OUTPUTs/TLEs'


# df_tles = get_merged_TLEs_from_CSVs(TLE_DIR_CSV)


# df_tles[df_tles["EPOCH"] > pd.to_datetime("2024-04-13")]
# print(df_tles)

# START_DATE = pd.to_datetime("2024-05-01 00:00:00")


# tle_update = []
# for d in range(32):
#     qdate = START_DATE+timedelta(days=d)

#     df = df_tles[df_tles['EPOCH'].dt.strftime(
#         '%Y-%m-%d') == qdate.strftime('%Y-%m-%d')]

#     print(qdate, len(df), len(df["NORAD_CAT_ID"].unique()))
#     tle_update.append({
#         "DAY": qdate,
#         "UPDATE": len(df),
#         "UNIQUE_SAT": len(df["NORAD_CAT_ID"].unique())
#     })

# pd.DataFrame.from_dict(tle_update).to_csv(
#     'tle_update_rate_final.csv', index=False)

# -----------
# Plotting
# -----------

df = pd.read_csv('tle_update_rate_final.csv')
# df = pd.read_csv('tle_update_rate.csv')
df["DAY"] = pd.to_datetime(df["DAY"])

df_dst = read_dst_index_CSV(
    '/home/suvam/Projects/CosmicDance/CSVs/Dst_index.csv', abs_value=False)
df_dst = df_dst[df_dst["TIMESTAMP"].between(
    df.iloc[0]["DAY"],
    df.iloc[-1]["DAY"]
)]


plt.rcParams["figure.figsize"] = (13, 7)
plt.rcParams.update({'font.size': 23})

fig, axs = plt.subplots(2, 1, sharex=True)
axs[-1].set_xticks([date for id, date in enumerate(df["DAY"])
                   if id % 2 == 0], minor=False)
axs[-1].set_xticklabels(axs[-1].get_xticks(), rotation=30)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))


for nt, t in zip(df_dst["nT"], df_dst["TIMESTAMP"]):
    if -300.0 >= nt:
        # print(nt)
        axs[0].axvline(x=t, color='r', linestyle='-', alpha=0.2)
        axs[1].axvline(x=t, color='r', linestyle='-', alpha=0.2)

axs[0].plot(df_dst["TIMESTAMP"], df_dst["nT"])
axs[0].axhline(y=-350.0, color='r', linestyle='--', label='G5 (Extreme)')

axs[1].scatter(df["DAY"], df["UNIQUE_SAT"], s=15, c='b')
axs[1].plot(df["DAY"], df["UNIQUE_SAT"],  linestyle='dotted', c='black')


axs[0].set_ylabel('Intensity (nT)')
axs[1].set_ylabel('# Sat tracked')
# axs[3].set_ylabel('Inclination')

axs[-1].set_xlabel('Date')

for i in range(2):
    axs[i].grid('x')
axs[0].legend()
plt.tight_layout()

plt.show()
