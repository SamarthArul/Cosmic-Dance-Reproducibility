# Cosmic Dance - Measuring Orbital Shifts

A tool designed to analyze the impact of solar radiation on spaceborne infrastructure, particularly in Low Earth Orbit (LEO). By leveraging data from large-scale deployments like SpaceX’s Starlink, `CosmicDance` provides insights into satellite orbital shifts and identifies risks such as premature orbital decay. 



<p align="center">
<img src="docs/img/overview_45210_45534.png">
</p>


## Table of Contents
- [Setting up](#setting-up)
- [Measure orbital shifts](#measure-orbital-shifts)
    - [Acquire dataset](#acquire-dataset) 
    - [Pre-procee the dataset](#pre-procee-the-dataset)
    - [Timeseries](#timeseries)
    - [Type of orbital shifts](#type-of-orbital-shifts)
    - [Maximum altitude change](#maximum-altitude-change)
    - [Measuring Solar Superstorm of May 2024](#measuring-solar-superstorm-of-may-2024)
    - [Analysis of a few other satellites](#analysis-of-a-few-other-satellites)
- [Citation](#citation)

<!-- - [Orchestration](#orchestration)
- [Orchestration Behind NAT](#orchestration-behind-nat)
- [Service Templates](#service-templates)
- [Node Types](#node-types)
- [Relationship Types](#relationship-types)
- [Supporting Repositories](#supporting-repositories)
- [License](#license)
 -->




## Setting up

- Install dependencies

```bash
sudo apt install curl
```

- Create conda environment

```bash
conda env create -f dependencies/environment.yml
```

- Set `CosmicDance` path

```bash
export PYTHONPATH=`COSMIC_DANCE_PATH`
```

## Measure orbital shifts

### Acquire dataset
- Get Dst index
```bash
python starlink/build_dataset/acquire/Dst_index.py
```
- Get satellite NORAD Catalog Number
```bash
python starlink/build_dataset/acquire/new_catalog_numbers.py
```
- Download TLEs 
```bash
python starlink/build_dataset/acquire/download_historic_tles.py
```

### Pre-procee the dataset
#### Dst Index
- Solar storm times according to NOAA Space Weather Scales
```bash
python starlink/build_dataset/preprocess/DST/timespan_NOAA.py
```
- Solar activities above some percentile
```bash
python starlink/build_dataset/preprocess/DST/timespan_percentile.py
```
- Quiet time below some percentile
```bash
python starlink/build_dataset/preprocess/DST/timespan_quiet_day.py
```
#### TLEs
- Convert TLEs from JSON to CSV
```bash
python starlink/build_dataset/preprocess/TLEs/JSON_to_CSV.py
```
- Cleanup the TLEs
```bash
python starlink/build_dataset/preprocess/TLEs/cleanup.py
```
- Remove TLEs before orbit raise (Starlink)
```bash
python starlink/build_dataset/preprocess/TLEs/remove_orbit_raise_maneuver.py
```

### Timeseries
- Generate launch date (or satellite) wise time series plot of orbital parameters with intensity of solar activities
```bash
python starlink/timeseries/view_timeseries_with_dst.py
```
- Other time series plots in [notebook](/starlink/timeseries/timeseries_view.ipynb)


### Type of orbital shifts
- Orbital shifts after quiet day

Set `OUTPUT_DIR` and `EVENT_DATES_CSV`
```python
OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/track_altitude_change/quiet_day"
EVENT_DATES_CSV = "artifacts/OUTPUT/Starlink/timespans/quiet_day/below_ptile_80.csv"
```
Execute the measurement script

```bash
python starlink/orbital_shifts/trace_altitude.py
```

- Orbital shifts after high solar activity day

Set `OUTPUT_DIR` and `EVENT_DATES_CSV`

```python
OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/track_altitude_change/merged_above_ptile_99/RAW"
EVENT_DATES_CSV = "artifacts/OUTPUT/Starlink/timespans/percentile/merged_above_ptile_99.csv"
```
Execute the measurement script


```bash
python starlink/orbital_shifts/trace_altitude.py
```

- Segregate the type of shifts

```bash
python starlink/orbital_shifts/detect_altitude_shifts.py
```

- View the type of shifts in [notebook](/starlink/orbital_shifts/view_altitude_shift.ipynb)

### Maximum altitude change

#### For intensity

- After low intensity solar activity days

Set `OUTPUT_DIR`, `OUTPUT_CSV`, and `DST_TIMESPAN`

```python
OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/maximum_altitude_change"
OUTPUT_CSV = f"{OUTPUT_DIR}/quiet_day_after_1_5_10.csv"
DST_TIMESPAN = "artifacts/OUTPUT/Starlink/timespans/quiet_day/merged_below_ptile_80.csv"
```

Execute the measurement script

```bash
python starlink/altitude_change/for_intensity.py
```

- After high intensity solar activity days

Set `OUTPUT_DIR`, `OUTPUT_CSV`, and `DST_TIMESPAN`

```python
OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/maximum_altitude_change"
OUTPUT_CSV = f"{OUTPUT_DIR}/event_day_after_1_5_10.csv"
DST_TIMESPAN = "artifacts/OUTPUT/Starlink/timespans/percentile/merged_above_ptile_95.csv"
```

Execute the measurement script

```bash
python starlink/altitude_change/for_intensity.py
```


#### For duration

- Short duration events

Set `OUTPUT_DIR`, `OUTPUT_CSV`, and `df_timespan`

```python
OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/maximum_altitude_change"
OUTPUT_CSV = f"{OUTPUT_DIR}/below_H9.csv"
df_timespan = df_timespan[df_timespan[DST.DURATION_HOURS] < 9]
```

Execute the measurement script

```bash
python starlink/altitude_change/for_duration.py
```


- Long duration events

Set `OUTPUT_DIR`, `OUTPUT_CSV`, and `df_timespan`

```python
OUTPUT_DIR = "artifacts/OUTPUT/Starlink/measurement/maximum_altitude_change"
OUTPUT_CSV = f"{OUTPUT_DIR}/above_H9.csv"
df_timespan = df_timespan[df_timespan[DST.DURATION_HOURS] > 9]
```

Execute the measurement script

```bash
python starlink/altitude_change/for_duration.py
```

- View maximum altitude change/drag distribution in [notebook](/starlink/altitude_change/view_change_distribution.ipynb)

### Measuring Solar Superstorm of May 2024

- Check for tracking anomaly

```bash
python starlink/superstorm/tracking_anomaly.py
```

- Check for drag anomaly

```bash
python starlink/superstorm/drag_anomaly.py
```

- Look for anomalies in [notebook](/starlink/timeseries/timeseries_view.ipynb)

### Analysis of a few other satellites

- [HawkEye_360](/HawkEye_360/)
- [ISRO](/ISRO/)


## Citation

```
Basak, Suvam, et al. "CosmicDance: Measuring Low Earth Orbital Shifts Due to Solar Radiations" Proceedings of the ACM Internet Measurement conference. 2024.
```

```bibtex
@inproceedings {CosmicDance,
    author = {Basak, Suvam and Pal, Amitangshu and Bhattacherjee, Debopam},
    title = {CosmicDance: Measuring Low Earth Orbital Shifts Due to Solar Radiations},
    booktitle = {{ACM IMC}},
    year = {2024},
    doi = {10.1145/3646547.3689024}
}
```