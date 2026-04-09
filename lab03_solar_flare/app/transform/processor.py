import pandas as pd
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_DATETIME_FMT = '%Y-%m-%dT%H:%MZ'

_CSV_FIELDNAMES = [
    'flr_id', 'catalog', 'instrument',
    'begin_time', 'peak_time', 'end_time', 'duration_minutes',
    'class_type', 'class_letter', 'class_value',
    'source_location', 'active_region_num',
    'note', 'linked_cme_ids', 'has_notification',
    'version_id', 'submission_time', 'link',
]


def _parse_dt(value: str | None) -> datetime | None:
    """Parse UTC datetime string to a timezone-aware datetime."""
    if not value:
        return None
    try:
        dt = datetime.strptime(value, _DATETIME_FMT)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        logger.warning('Cannot parse datetime: %r', value)
        return None


def _flare_class_letter(class_type: str | None) -> str | None:
    """Return the letter part of a flare class (e.g. 'X' from 'X1.4')."""
    if class_type and class_type[0].upper() in ('A', 'B', 'C', 'M', 'X'):
        return class_type[0].upper()
    return None


def _flare_class_value(class_type: str | None) -> float | None:
    """Return the numeric part of a flare class (e.g. 1.4 from 'X1.4')."""
    if class_type and len(class_type) > 1:
        try:
            return float(class_type[1:])
        except ValueError:
            pass
    return None


def _duration_minutes(begin: datetime | None, end: datetime | None) -> int | None:
    """Return the duration of a flare in whole minutes."""
    if begin and end:
        delta = end - begin
        return int(delta.total_seconds() // 60)
    return None


def _linked_cme_ids(raw: dict) -> str | None:
    """Return a comma-separated string of linked CME activity IDs, or None."""
    events = raw.get('linkedEvents') or []
    cme_ids = [
        e['activityID']
        for e in events
        if isinstance(e, dict) and 'CME' in e.get('activityID', '')
    ]
    return ','.join(cme_ids) if cme_ids else None


def _has_notification(raw: dict) -> bool:
    """Return True if at least one alert notification was sent."""
    return bool(raw.get('sentNotifications'))


def _to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert transformed FLR records to a pandas DataFrame."""
    df = pd.DataFrame(records, columns=_CSV_FIELDNAMES)

    for col in ('begin_time', 'peak_time', 'end_time', 'submission_time'):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors='coerce')

    return df


def transform_flr_record(raw: dict) -> dict[str, Any]:
    """
    Transform a single raw FLR record into a flat, typed dictionary.

    Keys map 1-to-1 with the ``solar_flares`` database table columns and the
    CSV header row.

    Args:
        raw(dict): A single raw JSON object from ``get_flr_data()``.

    Returns:
        dict: A flat dictionary with typed / cleaned values.
    """
    begin = _parse_dt(raw.get('beginTime'))
    peak = _parse_dt(raw.get('peakTime'))
    end = _parse_dt(raw.get('endTime'))
    class_type = raw.get('classType') or None

    instruments: list[dict] = raw.get('instruments') or []
    instrument_names = ','.join(
        i.get('displayName', '') for i in instruments if isinstance(i, dict)
    )

    return {
        'flr_id':            raw.get('flrID'),
        'catalog':           raw.get('catalog'),
        'instrument':        instrument_names or None,
        'begin_time':        begin,
        'peak_time':         peak,
        'end_time':          end,
        'duration_minutes':  _duration_minutes(begin, end),
        'class_type':        class_type,
        'class_letter':      _flare_class_letter(class_type),
        'class_value':       _flare_class_value(class_type),
        'source_location':   raw.get('sourceLocation') or None,
        'active_region_num': raw.get('activeRegionNum'),
        'note':              raw.get('note') or None,
        'linked_cme_ids':    _linked_cme_ids(raw),
        'has_notification':  _has_notification(raw),
        'version_id':        raw.get('versionId'),
        'submission_time':   _parse_dt(raw.get('submissionTime')),
        'link':              raw.get('link') or None,
    }


def transform_flr_records(raw_list: list[dict]) -> list[dict[str, Any]]:
    """
    Transform a list of raw FLR records.

    Args:
        raw_list(list[dict]): Output of ``get_flr_data()``.

    Returns:
        list: List of flat, typed dictionaries ready for DB insertion or export.
    """
    transformed = []
    for raw in raw_list:
        try:
            transformed.append(transform_flr_record(raw))
        except Exception:
            logger.exception('Failed to transform record: %r',
                             raw.get('flrID'))
    logger.info('Transformed %d / %d records.',
                len(transformed), len(raw_list))
    return transformed


def to_csv_string(records: list[dict[str, Any]]) -> str:
    """
    Serialise transformed records to a CSV string.

    Args:
        records(list[dict[str, Any]]): Output of ``transform_flr_records()``.

    Returns:
        str: UTF-8 CSV text including a header row.
    """
    df = _to_dataframe(records)
    return df.to_csv(index=False, date_format='%Y-%m-%dT%H:%M:%SZ')


def to_csv_file(records: list[dict[str, Any]], path: str) -> None:
    """
    Write transformed records to a CSV file.

    Args:
        records(list[dict[str, Any]]): Output of ``transform_flr_records()``.
        path(str):    Destination file path (UTF-8, LF line endings).
    """
    df = _to_dataframe(records)
    df.to_csv(path, index=False,
              date_format='%Y-%m-%dT%H:%M:%SZ', encoding='utf-8')
    logger.info('Wrote %d records to %s', len(df), path)
