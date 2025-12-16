from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Generator, Iterable, Optional

from django.conf import settings as django_settings
from django.utils import timezone
from django.utils.module_loading import import_string


def get_setting(name: str, default):
    """Fetch a setting with a fallback."""
    return getattr(django_settings, name, default)


def load_callable(path: Optional[str], setting_name: str):
    """Import a callable from a dotted path with a clear error if it fails."""
    if path is None:
        return None
    try:
        return import_string(path)
    except Exception as exc:  # pragma: no cover - protective wrapper
        raise ImportError(f"Could not import {setting_name} callable '{path}': {exc}") from exc


def daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
    """Yield each date in the inclusive range."""
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def ceil_to_interval(dt: datetime, minutes: int) -> datetime:
    """Round up to the next interval boundary, preserving timezone awareness."""
    if minutes <= 0:
        raise ValueError("minutes must be positive")
    if timezone.is_naive(dt):
        raise ValueError("ceil_to_interval expects an aware datetime")

    base = dt.replace(second=0, microsecond=0)
    if dt.second or dt.microsecond:
        base += timedelta(minutes=1)
    remainder = (base.hour * 60 + base.minute) % minutes
    if remainder:
        base += timedelta(minutes=minutes - remainder)
    return base


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """Check whether two half-open intervals overlap."""
    return a_start < b_end and b_start < a_end


def ensure_aware(dt: datetime, tz=None, *, name: str = "datetime") -> datetime:
    """Ensure a datetime is timezone-aware, coercing with tz when possible."""
    if timezone.is_naive(dt):
        if tz is None:
            raise ValueError(f"{name} must be timezone-aware or tz must be provided")
        return timezone.make_aware(dt, tz)
    if tz:
        return dt.astimezone(tz)
    return dt


def get_identifier(obj, fallback=None):
    """Pick a reasonable identifier for a Django model-like object."""
    for attr in ("pk", "id"):
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return fallback
