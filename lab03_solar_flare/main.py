import os
import time
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from app.extract import get_flr_data
from app.transform import transform_flr_records
from app.load.mariadb_loader import build_engine, init_db, load_to_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

today = datetime.now(timezone.utc)
default_start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
default_end = today.strftime('%Y-%m-%d')


def run_etl(api_key: str, start_date: str | None, end_date: str | None, lookback_days: int, engine) -> None:
    """Fetch, transform and load solar flare data."""
    logger.info('Fetching solar flare data from NASA DONKI API...')
    raw_records = get_flr_data(
        api_key=api_key, start_date=start_date, end_date=end_date, lookback_days=lookback_days)
    logger.info('Fetched %d raw records.', len(raw_records))

    logger.info('Transforming records...')
    transformed = transform_flr_records(raw_records)

    logger.info('Loading %d records into the database...', len(transformed))
    affected = load_to_db(transformed, engine=engine)
    logger.info('Done. Affected rows: %d', affected)


def main():
    load_dotenv()

    api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
    lookback_days = int(os.getenv('LOOKBACK_DAYS', '30'))
    refresh_hours = float(os.getenv('REFRESH_HOURS', '1'))
    refresh_interval = refresh_hours * 3600
    today = datetime.now(timezone.utc)
    start_date = os.getenv(
        'START_DATE', (today - timedelta(days=lookback_days)).strftime('%Y-%m-%d'))
    end_date = os.getenv('END_DATE', today.strftime('%Y-%m-%d'))

    logger.info('Connecting to database and initialising schema...')
    engine = build_engine()
    init_db(engine)

    run_count = 0
    while True:
        run_count += 1
        logger.info('=== ETL run #%d ===', run_count)
        logger.info('Date range: %s → %s', start_date, end_date)

        run_start_time = datetime.now(timezone.utc)

        try:
            run_etl(api_key=api_key, start_date=start_date,
                    end_date=end_date, lookback_days=lookback_days, engine=engine)
        except Exception:
            logger.exception(
                'ETL run #%d failed — will retry after %.1f h.', run_count, refresh_hours)

        start_date = run_start_time.strftime('%Y-%m-%d')
        end_date = (run_start_time + timedelta(hours=refresh_hours)
                    ).strftime('%Y-%m-%d')

        logger.info('Next run in %.1f hour(s). Sleeping...', refresh_hours)
        time.sleep(refresh_interval)


if __name__ == '__main__':
    main()
