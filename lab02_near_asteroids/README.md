# NASA NeoWs Asteroid Data Tools

This project contains two Python scripts for collecting and visualizing data about **near-Earth asteroids** using the NASA NeoWs API.

1. **neows_logger.py** – fetches asteroid data from the API and stores it as JSON and CSV datasets
2. **neows_visualisation.py** – loads the dataset and visualizes asteroid behavior using Seaborn

Together, these scripts allow you to **collect real astronomical data and analyze asteroid characteristics visually.**

---

# Data Source

Asteroid data is retrieved from the public API provided by NASA:

https://api.nasa.gov/neo/rest/v1/feed

This API provides information about **near-Earth objects (NEOs)**, including:

* asteroid name and ID
* estimated diameter (min/max)
* absolute magnitude
* velocity relative to Earth
* miss distance (closest approach)
* hazard classification

The logger fetches data for a selected date range (default: last 7 days).

---

# 1. NeoWs Data Logger

## Description

`neows_logger.py` retrieves asteroid data from the NASA NeoWs API and stores it in both raw and processed formats.

Each run creates:

* a **raw JSON file** (full API response)
* a **CSV dataset** (cleaned, structured data)

Example output files:

```
datasets/asteroids_neows/neows_raw_20260323_120000.json
datasets/asteroids_neows/neows_20260323_120000.csv
```

---

## Collected Fields

Dataset columns:

```
date
id
name
absolute_magnitude_h
is_potentially_hazardous
diameter_min_m
diameter_max_m
velocity_km_s
miss_distance_km
```

Dates are converted to **datetime format** for time-based analysis.

---

## How to Run

```bash
python neows_logger.py
```

The script will:

1. Create the dataset directory (if needed)
2. Fetch asteroid data (default: last 7 days)
3. Save raw JSON data
4. Convert and store structured CSV dataset

If the request fails, the script exits safely.

---

# 2. Asteroid Data Visualization

## Description

`neows_visualisation.py` loads the most recent dataset and generates visualizations using **Seaborn** and **Matplotlib**.

The default visualization is a **scatter plot of asteroid miss distance over time**.

---

## How to Run

```bash
python neows_visualisation.py
```

The script will:

1. Locate the most recent dataset file
2. Load it into a pandas DataFrame
3. Generate a scatter plot

---

## Visualization Details

Default plot:

* **X-axis** → date of close approach
* **Y-axis** → miss distance (km)
* **Color (hue)** → hazardous vs non-hazardous

Color mapping:

* Red → potentially hazardous
* Blue → non-hazardous

---

## Example Workflow

### Step 1 – Fetch asteroid data

```bash
python neows_logger.py
```

---

### Step 2 – Generate visualization

```bash
python neows_visualisation.py
```

---

# Example Dataset

Example CSV structure:

```
date,id,name,absolute_magnitude_h,is_potentially_hazardous,diameter_min_m,diameter_max_m,velocity_km_s,miss_distance_km
2024-03-01,12345,(2024 AB),22.1,False,45.2,98.3,12.5,4500000
2024-03-01,67890,(2024 CD),19.3,True,120.5,300.1,18.2,750000
```

Each row represents a **single asteroid close approach event**.

---

# Notes

* The API allows a maximum of **7 days per request**
* `DEMO_KEY` is rate-limited; use a personal API key for larger usage
* Some asteroids may have incomplete or missing fields

---

# Possible Improvements

* Add CLI arguments for custom date ranges
* Support multiple visualization types (histogram, KDE, boxplot)
* Store data in a database instead of CSV
* Add statistical analysis (correlations, distributions)
* Build an interactive dashboard (Streamlit)

---

# Purpose

This project demonstrates a complete **data pipeline workflow**:

* API data collection
* data transformation
* dataset versi
