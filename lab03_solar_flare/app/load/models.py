from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class SolarFlare(SQLModel, table=True):
    __tablename__ = "solar_flares"

    id: int | None = Field(default=None, primary_key=True)
    flr_id: str = Field(index=True, max_length=64, unique=True)
    catalog: str | None = Field(max_length=32, default=None)
    instrument: str | None = Field(default=None, max_length=255)
    begin_time: datetime | None = None
    peak_time: datetime | None = None
    end_time: datetime | None = None
    duration_minutes: int | None = None
    class_type: str | None = Field(default=None, index=True, max_length=8)
    class_letter: str | None = Field(default=None, max_length=1)
    class_value: float | None = None
    source_location: str | None = Field(max_length=32, default=None)
    active_region_num: int | None = None
    note: str | None = None
    linked_cme_ids: str | None = None
    has_notification: bool | None = None
    version_id: int | None = None
    submission_time: datetime | None = None
    link: str | None = Field(default=None, max_length=512)
    inserted_at: datetime = Field(default_factory=datetime.now(timezone.utc))
