import requests
import csv
import schedule
import time
import pprint
import os
from pathlib import Path
from datetime import datetime, timezone

"""
ISS Telemetry Logger

This script periodically retrieves telemetry data of the International Space Station
from the public API (wheretheiss.at) and appends the data to a CSV file.

The script runs continuously and records the ISS position every 2 seconds.
"""

DATASET_DIR = Path("datasets/iss_telemetry")
DATASET_DIR.mkdir(exist_ok=True)
CSV_FILE = DATASET_DIR / f"iss_telemetry_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

file_exists = os.path.isfile(CSV_FILE)

def update_iss_data():
    """
    Fetch the latest ISS telemetry data from the API
    and store it in the CSV file.

    Raises
    ------
    HTTPError
        If one occurs from GET request.
    """
    
    try:
        res = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=10)

        res.raise_for_status()

        iss_data_raw = res.json()

        iss_data_raw["timestamp"] = datetime.fromtimestamp(iss_data_raw["timestamp"], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        write_to_csv(iss_data_raw)

    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        print("-----------------------------")

def write_to_csv(data):
    
    """
    Append ISS telemetry data as a new row in the CSV file.

    Parameters
    ----------
    data : dict
        Dictionary containing ISS telemetry data returned by the API.
    """

    global file_exists

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()
            file_exists = True

        writer.writerow(data)

        pprint.pprint(data)
        print("-----------------------------")

def main():

    schedule.every(2).seconds.do(update_iss_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()