# Solar Flare ETL Pipeline
## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Running the Project](#running-the-project)
- [How It Works](#how-it-works)
- [Data Model](#data-model)
- [Development Process](#development-process)
- [Notes](#notes)
- [Possible Improvements](#possible-improvements)

## Overview

This project implements an **ETL (Extract–Transform–Load) pipeline** that collects solar flare data from NASA’s DONKI API, processes it, and stores it in a MariaDB database.

The pipeline runs continuously and periodically updates the dataset with new records.

### Solar Flare Guide
Flares happen when the powerful magnetic fields in and around the sun reconnect. They're usually associated with active regions, often seen as sun spots, where the magnetic fields are strongest. Flares are classified according to their strength. The smallest ones are B-class, followed by C, M and X, the largest. Similar to the Richter scale for earthquakes, each letter represents a ten-fold increase in energy output. So an X is 10 times an M and 100 times a C. Within each letter class, there is a finer scale from 1 to 9. C-class flares are too weak to noticeably affect Earth. M-class flares can cause brief radio blackouts at the poles and minor radiation storms that might endanger astronauts. Although X is the last letter, there are flares more than 10 times the power of an X1, so X-class flares can go higher than 9. The most powerful flare on record was in 2003, during the last solar maximum. It was so powerful that it overloaded the sensors measuring it. They cut-out at X17, and the flare was later estimated to be about X45. A powerful X-class flare like that can create long lasting radiation storms, which can harm satellites and even give airline passengers, flying near the poles, small radiation doses. X flares also have the potential to create global transmission problems and world-wide blackouts.

**Credits:** _NASA/Goddard Space Flight Center_

---

## Architecture
The project follows a ETL design:

```
app/
 ├── extract/     # Data acquisition from NASA API
 ├── transform/   # Data cleaning and transformation
 ├── load/        # Database loading (MariaDB)
```

### Workflow

1. **Extract**
   - Fetch solar flare (FLR) data from NASA DONKI API
   - Supports configurable date ranges or automatic lookback

2. **Transform**
   - Cleans and normalizes raw JSON data
   - Extracts structured fields (e.g., class type, duration, timestamps)
   - Converts data into a flat schema suitable for storage

3. **Load**
   - Stores data into MariaDB using SQLModel/SQLAlchemy
   - Uses **bulk upsert (ON DUPLICATE KEY UPDATE)** to avoid duplicates

---

## Features

- Continuous ETL execution with configurable refresh interval
- Incremental data updates
- Docker support for easy deployment
- CSV export capability (optional utility functions)

---

## Running the Project

```bash
docker-compose up --build
```

This will:

- Start MariaDB
- Build and run the ETL service
- Automatically initialize the database

---

## How It Works

- The pipeline runs in an **infinite loop**
- After each run:
  - It updates the time window
  - Sleeps for the configured interval

- Default behavior:
  - Fetch data from the last `LOOKBACK_DAYS`
  - Then switch to incremental updates

---

## Data Model

Each solar flare record includes:

- Flare ID and catalog
- Instrument
- Start, peak, and end times
- Duration
- Flare class
- Source location and active region
- Linked CME events
- Notification flag
- Metadata

---

## Development Process

The project was developed incrementally, starting from data extraction and progressing toward a fully functional ETL pipeline.

### 1. API Client

The implementation began with `api_client.py`, which is responsible for retrieving data from the NASA DONKI API.
This module builds upon scripts from previous lab exercises, (`iss_telemetry_logger.py` and `neows_logger.py`).

---

### 2. Data Transformation

Next, the transformation layer (`processor.py`) was developed.

- The incoming JSON data was cleaned and reshaped into a format suitable for database storage.
- The **flare class** was split into:
  - class letter (e.g., X, M, C)
  - numeric intensity value
- A new field **duration (in minutes)** was computed from timestamps.
- The logic was later refactored into multiple smaller functions to improve readability and maintainability.

CSV export functionality was added at a later stage as an auxiliary feature for validation and debugging.

---

### 3. Database Layer

After transformation, the database layer was developed:

#### `models.py`

- The `SolarFlare` class was defined based on the transformed data structure.
- A special column `inserted_at` was added, which automatically stores the timestamp when a record is created.

#### `mariadb_loader.py`

- Initially programmed as a single block of logic, this module was later refactored into multiple functions for better clarity.
- Additional flexibility was added:
  - Handling missing or optional data fields
  - Configurable database connection (e.g., dynamic `db_url` in engine creation)

---

### 4. Main Application

The `main.py` script was developed in stages:

1. **Initial validation phase**
   - Generated and inspected CSV output to verify correctness of the transformation layer

2. **Database integration**
   - Added functionality to connect to MariaDB
   - Loaded transformed data into the database
   - Verified successful insertion with a single run

3. **Refactoring phase**
   - Cleaned up code structure
   - Added comments for clarity
   - Removed  `main()` functions from modules
   - Added `__init__.py` files to expose a module API

---

### 5. Finalization

Once all components were working correctly:

- The `main.py` script was extended to run **periodically**
- The pipeline was converted into a continuous ETL process that:
  - fetches new data
  - processes it
  - stores it in the database at regular intervals

---

## Notes

- Default NASA API key (`DEMO_KEY`) has rate limits — use your own key for production.
- Time values are handled as timezone-aware UTC timestamps.

---

## Possible Improvements

- Add web application (GUI) to browse data from MariaDB
- Add option for user to download CSV (function to export CSV already done in export stage)
- Save last update timestamp to MariaDB instead of RAM
- Link Linked CME events for easier query (maybe separate table)
