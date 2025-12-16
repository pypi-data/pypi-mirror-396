"""
UTC-naive datetime helpers for repositories.

The database columns are `TIMESTAMP WITHOUT TIME ZONE`, so we store and
filter using UTC-naive values to avoid aware/naive mixups across drivers.
"""

from datetime import datetime, timezone
from typing import Optional


def utc_now_naive() -> datetime:
    """Return current UTC time without tzinfo (matches naive DB columns)."""
    return datetime.utcnow()


def to_naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert aware datetime to naive UTC; pass through None/naive unchanged."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

