from dotenv import load_dotenv
import os
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import pandas as pd

DATASET_DIR = Path("datasets/asteroids_neows")
DATASET_DIR.mkdir(exist_ok=True)

_timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
RAW_FILE = DATASET_DIR / f"neows_raw_{_timestamp}.json"
CSV_FILE = DATASET_DIR / f"neows_{_timestamp}.csv"

API_URL = 'https://api.nasa.gov/neo/rest/v1/feed'

load_dotenv()
API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')


def save_raw_data(raw_json: dict) -> None:
    """
    Save raw JSON response from the API to a file.

    Parameters
    ----------
    raw_json : dict
        Raw JSON response from the NeoWs API.
    """
    with open(RAW_FILE, 'w') as f:
        json.dump(raw_json, f, indent=2)


def save_neows_to_csv(raw_data: dict) -> None:
    """
    Extract relevant fields from raw JSON and save them to a CSV file.

    Parameters
    ----------
    raw_data : dict
        Raw JSON response from the NASA NeoWs API containing near_earth_objects.
    """
    rows = []
    for date, asteroids in raw_data['near_earth_objects'].items():
        for ast in asteroids:
            approach = ast['close_approach_data'][0]
            rows.append({
                'date':                     date,
                'id':                       ast['id'],
                'name':                     ast['name'],
                'absolute_magnitude_h':     ast['absolute_magnitude_h'],
                'is_potentially_hazardous': ast['is_potentially_hazardous_asteroid'],
                'diameter_min_m':           ast['estimated_diameter']['meters']['estimated_diameter_min'],
                'diameter_max_m':           ast['estimated_diameter']['meters']['estimated_diameter_max'],
                'velocity_km_s':            float(approach['relative_velocity']['kilometers_per_second']),
                'miss_distance_km':         float(approach['miss_distance']['kilometers']),
            })

    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['date'])
    df.to_csv(CSV_FILE, index=False)


def get_data_neows(start_date: str | None = None, end_date: str | None = None) -> dict | None:
    """
    Fetch asteroid close approach data from the NASA NeoWs API.

    Parameters
    ----------
    start_date : str, optional
        Start date in YYYY-MM-DD format. Defaults to 7 days before today.
    end_date : str, optional
        End date in YYYY-MM-DD format. Defaults to today.

    Returns
    -------
    dict or None
        Raw JSON response as a dict, or None if the request failed.
    """
    today = datetime.now(timezone.utc)

    if end_date is None:
        end_date = today.strftime('%Y-%m-%d')
    if start_date is None:
        start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')

    query_parameters = {
        'start_date': start_date,
        'end_date':   end_date,
        'api_key':    API_KEY,
    }

    try:
        res = requests.get(API_URL, params=query_parameters, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return None


def main() -> None:
    raw_neows_json = get_data_neows()

    if raw_neows_json is None:
        print("No data retrieved, exiting.")
        return

    save_raw_data(raw_neows_json)
    save_neows_to_csv(raw_neows_json)


if __name__ == "__main__":
    main()