import requests
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

API_URL = 'https://api.nasa.gov/DONKI/FLR'


def _validate_date(date_str: str) -> str:
    """Validate date string format (YYYY-MM-DD)."""
    datetime.strptime(date_str, '%Y-%m-%d')
    return date_str


def get_flr_data(api_key: str, start_date: str | None = None, end_date: str | None = None, timeout: int = 10, lookback_days: int = 30) -> list:
    """
    Fetch solar flare (FLR) data from NASA DONKI API.

    If dates are not provided:
        - end_date defaults to today (UTC)
        - start_date defaults to today minus lookback_days

    Args:
        api_key (str): NASA API key.
        start_date (str | None): Start date in YYYY-MM-DD format.
        end_date (str | None): End date in YYYY-MM-DD format.
        timeout (int): HTTP request timeout in seconds.
        lookback_days (int): Number of days to look back if start_date is not provided.

    Returns:
        list: List of solar flare records (raw JSON objects).

    Raises:
        ValueError: If start_date or end_date has invalid format.
        requests.exceptions.RequestException: If the HTTP request fails.
    """
    today = datetime.now(timezone.utc)

    if end_date is None:
        end_date = today.strftime('%Y-%m-%d')
    else:
        end_date = _validate_date(end_date)

    if start_date is None:
        start_date = (today - timedelta(days=lookback_days)
                      ).strftime('%Y-%m-%d')
    else:
        start_date = _validate_date(start_date)

    query_parameters = {
        'startDate': start_date,
        'endDate':   end_date,
        'api_key':    api_key,
    }

    logger.info("Fetching FLR data from %s to %s", start_date, end_date)

    try:
        res = requests.get(API_URL, params=query_parameters, timeout=timeout)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        logger.exception('Failed to fetch FLR data')
        raise
