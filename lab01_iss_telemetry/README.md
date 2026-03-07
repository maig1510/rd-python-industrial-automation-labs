# ISS Telemetry Tools

This project contains two Python scripts for collecting and visualizing telemetry data of the **International Space Station (ISS)**.

1. **iss_telemetry_logger.py** – collects ISS telemetry data from a public API and stores it in a CSV dataset.
2. **iss_telemetry_visualisation.py** – loads the collected dataset and generates visualizations using Python data-analysis libraries.

Together, these scripts allow you to **record real ISS telemetry data and analyze it visually.**

---

# Data Source

Telemetry data is retrieved from the public API:

https://api.wheretheiss.at/v1/satellites/25544

This API provides real-time information about the ISS, including:

* latitude
* longitude
* altitude
* velocity
* visibility
* footprint
* timestamp
* satellite name and ID

The logger periodically queries this API and stores the results in a structured CSV dataset.

---

# Project Structure

```
project/
│
├─ datasets/
│  └─ iss_telemetry/
│      └─ iss_telemetry_YYYYMMDD_HHMMSS.csv
│
├─ iss_telemetry_logger.py
├─ iss_telemetry_visualisation.py
└─ README.md
```

The dataset directory is automatically created when the logger runs.

---

# 1. ISS Telemetry Logger

## Description

`iss_telemetry_logger.py` continuously collects telemetry data from the ISS API and stores it in a CSV file.

Each run creates a **new dataset file** with a timestamp in its filename.

Example output file:

```
datasets/iss_telemetry/iss_telemetry_20260307_102300.csv
```

The script collects data **every 2 seconds**.

---

## Collected Fields

Dataset columns:

```
name
id
latitude
longitude
altitude
velocity
visibility
footprint
timestamp
```

Timestamp values are converted to **UTC datetime format**.

---

## How to Run

```bash
python iss_telemetry_logger.py
```

The script will:

1. Create the dataset directory (if it does not exist)
2. Start polling the API every 2 seconds
3. Append new telemetry records to the CSV file
4. Print each record to the console

Example console output:

```
{'name': 'iss',
 'id': 25544,
 'latitude': 47.123,
 'longitude': 12.456,
 'altitude': 423.8,
 'velocity': 27600,
 'visibility': 'daylight',
 'footprint': 4500,
 'timestamp': '2026-03-07 10:22:10'}
```

Stop the logger with:

```
CTRL + C
```

---

# 2. ISS Telemetry Visualisation

## Description

`iss_telemetry_visualisation.py` loads the collected telemetry dataset and generates graphs using **Seaborn** and **Matplotlib**.

The script is designed to visualize trends in the collected ISS telemetry data.

---

## How to Run

Example usage:

```bash
python iss_telemetry_visualisation.py datasets/iss_telemetry/iss_telemetry_20260307_102300.csv
```

Typical workflow:

1. Run the logger to collect data.
2. Stop the logger after some time.
3. Use the generated CSV dataset for visualization.

---

## Example Workflow

### Step 1 – Start telemetry collection

```bash
python iss_telemetry_logger.py
```

Wait several minutes to collect data.

---

### Step 2 – Stop the logger

Press:

```
CTRL + C
```

---

### Step 3 – Generate graphs

```bash
python iss_telemetry_visualisation.py datasets/iss_telemetry/iss_telemetry_20260307_102300.csv
```

The script will read the dataset and generate visualizations.

---

# Example Dataset

Example CSV structure:

```
name,id,latitude,longitude,altitude,velocity,visibility,footprint,timestamp
iss,25544,47.123,12.456,423.8,27600,daylight,4500,2026-03-07 10:22:10
iss,25544,47.145,12.502,423.7,27601,daylight,4500,2026-03-07 10:22:12
```

Each row represents a **single telemetry snapshot**.

---
