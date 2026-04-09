import os
import logging
from sqlalchemy import create_engine, text
from sqlmodel import SQLModel
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert as mysql_insert

from app.load import SolarFlare

logger = logging.getLogger(__name__)


def _upsert_flares(session: Session, records: list[dict]) -> int:
    """Bulk upsert using ON DUPLICATE KEY UPDATE."""
    if not records:
        logger.info('No records to upsert.')
        return 0

    solar_flare_upsert_stmt = mysql_insert(SolarFlare).values(records)

    update_dict = {
        c.name: solar_flare_upsert_stmt.inserted[c.name]
        for c in SolarFlare.__table__.columns
        if c.name not in ('id', 'inserted_at')
    }

    solar_flare_upsert_stmt = solar_flare_upsert_stmt.on_duplicate_key_update(**update_dict)

    result = session.execute(solar_flare_upsert_stmt)
    session.commit()

    affected = result.rowcount or 0
    logger.info('Bulk upsert complete — affected rows: %d', affected)
    return affected


def build_engine(url: str | None = None):
    """
    Construct and validate a SQLAlchemy engine.

    Connection URL resolution priority:
      1. Explicit ``url`` argument
      2. ``DB_URL`` environment variable
      3. Individual environment variables:
         DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

    Args:
        url (str | None): Full database URL.

    Returns:
        Engine: A validated SQLAlchemy engine instance.

    Raises:
        Exception: Connection failure during validation.
    """

    db_url = url or os.getenv('DB_URL')
    if not db_url:
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        dbname = os.getenv('DB_NAME')
        db_url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}'

    engine = create_engine(db_url, echo=False, pool_pre_ping=True)

    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
    except Exception as e:
        logger.error('Database connection failed: %s', e)
        raise

    logger.info('DB: %s', engine.url.render_as_string(hide_password=True))
    return engine


def init_db(engine) -> None:
    """
    Initialize database schema. Creates all tables if they do not already exist.

    Args:
        engine (Engine): SQLAlchemy engine bound to the target database.
    """
    SQLModel.metadata.create_all(engine)
    logger.info('DB tables initialized.')


def load_to_db(records: list[dict], engine=None) -> int:
    """
    Persist transformed FLR records to MariaDB.

    Args:
        records (list[dict]): Output of ``transform_flr_records()``.
        engine (Engine | None): SQLAlchemy engine; built from env vars when omitted.

    Returns:
        int: Number of affected rows.
    """
    if engine is None:
        engine = build_engine()

    with Session(engine) as session:
        return _upsert_flares(session, records)
