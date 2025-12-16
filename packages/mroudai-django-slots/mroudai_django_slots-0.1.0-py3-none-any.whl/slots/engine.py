from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from django.utils import timezone

from .utils import (
    ceil_to_interval,
    daterange,
    ensure_aware,
    get_identifier,
    get_setting,
    load_callable,
    overlaps,
)


DEFAULT_WORKING_WINDOWS_PATH = "availability.logic.get_working_windows"


@dataclass
class Slot:
    start: datetime
    end: datetime
    provider_id: Any
    service_id: Any
    capacity_total: int
    capacity_remaining: int
    meta: Dict[str, Any] = field(default_factory=dict)


def _resolve_tenant(service, provider, tenant):
    """Enforce tenant consistency if a tenant model is configured."""
    tenant_model_path = get_setting("SLOTS_TENANT_MODEL", None)
    if not tenant_model_path:
        return None

    service_tenant = getattr(service, "tenant", None)
    provider_tenant = getattr(provider, "tenant", None)

    if tenant is None:
        tenant = service_tenant or provider_tenant
    if tenant is not None:
        if service_tenant is not None and tenant != service_tenant:
            raise ValueError("Tenant mismatch between provided tenant and service. ")
        if provider_tenant is not None and tenant != provider_tenant:
            raise ValueError("Tenant mismatch between provided tenant and provider.")
    return tenant


def _call_variants(func, variants: Sequence[Dict[str, Any]], context: str):
    """Attempt several kwarg variants for a callable."""
    last_error = None
    for variant in variants:
        clean_kwargs = {k: v for k, v in variant.items() if v is not None}
        try:
            return func(**clean_kwargs)
        except TypeError as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    raise TypeError(f"{context} callable did not accept provided arguments")


def _get_capacity(service) -> int:
    for attr in ("capacity_total", "capacity", "capacity_per_slot"):
        if hasattr(service, attr):
            value = getattr(service, attr)
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    return 1


def _get_interval_minutes(service) -> int:
    default_interval = get_setting("SLOTS_DEFAULT_INTERVAL_MINUTES", 15)
    if getattr(service, "fixed_start_times_only", False):
        interval = getattr(service, "start_time_interval_minutes", None)
        if not interval:
            raise ValueError("Service requires fixed start times but no start_time_interval_minutes set.")
        return int(interval)
    return int(default_interval)


def _get_duration_minutes(service, addons: Optional[Iterable[Any]]) -> int:
    if not hasattr(service, "duration_minutes"):
        raise ValueError("Service must expose duration_minutes.")
    duration = getattr(service, "duration_minutes") or 0
    extra = 0
    for addon in addons or []:
        extra += getattr(addon, "extra_duration_minutes", 0) or 0
    return int(duration + extra)


def _validate_intervals_are_aware(intervals: Iterable[Tuple[datetime, datetime]], tz):
    validated = []
    for start, end in intervals:
        start_aw = ensure_aware(start, tz, name="busy interval start")
        end_aw = ensure_aware(end, tz, name="busy interval end")
        if end_aw <= start_aw:
            continue
        validated.append((start_aw, end_aw))
    return validated


def _fetch_busy_intervals(
    func,
    *,
    provider,
    service,
    start_date: date,
    end_date: date,
    tz,
    tenant,
):
    variants = [
        {
            "provider": provider,
            "service": service,
            "start_date": start_date,
            "end_date": end_date,
            "tenant": tenant,
            "tz": tz,
        },
        {"provider": provider, "start_date": start_date, "end_date": end_date},
        {"provider": provider, "service": service, "start_date": start_date, "end_date": end_date},
    ]
    intervals = _call_variants(func, variants, "busy intervals")
    return intervals or []


def _fetch_working_windows(func, *, provider, day: date, tz, tenant):
    variants = [
        {"provider": provider, "date": day, "tz": tz, "tenant": tenant},
        {"provider": provider, "start_date": day, "end_date": day, "tz": tz, "tenant": tenant},
        {"provider": provider, "date": day},
        {"provider": provider, "start_date": day, "end_date": day},
    ]
    windows = _call_variants(func, variants, "working windows")
    return windows or []


def generate_slots(
    service,
    provider,
    start_date: date,
    end_date: date,
    *,
    tz=None,
    now_dt: Optional[datetime] = None,
    addons: Optional[Iterable[Any]] = None,
    tenant=None,
) -> Dict[date, List[Slot]]:
    """Generate bookable slot candidates for a provider within a date range."""
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")

    tz = tz or timezone.get_current_timezone()
    now_dt = ensure_aware(now_dt or timezone.now(), tz, name="now_dt")
    tenant = _resolve_tenant(service, provider, tenant)

    interval_minutes = _get_interval_minutes(service)
    if interval_minutes <= 0:
        raise ValueError("Interval minutes must be positive.")
    interval_td = timedelta(minutes=interval_minutes)

    duration_minutes = _get_duration_minutes(service, addons)
    buffer_before = getattr(service, "buffer_before_minutes", 0) or 0
    buffer_after = getattr(service, "buffer_after_minutes", 0) or 0
    buffer_before_td = timedelta(minutes=buffer_before)
    buffer_after_td = timedelta(minutes=buffer_after)
    duration_td = timedelta(minutes=duration_minutes)
    booking_window_td = buffer_before_td + duration_td + buffer_after_td

    min_notice_minutes = getattr(service, "minimum_notice_minutes", 0) or 0
    max_advance_days = getattr(service, "maximum_advance_days", None)
    earliest_start = now_dt + timedelta(minutes=min_notice_minutes)
    latest_start = None
    if max_advance_days is not None:
        latest_start = now_dt + timedelta(days=max_advance_days)
        if earliest_start > latest_start:
            return {}

    working_windows_path = get_setting(
        "SLOTS_GET_WORKING_WINDOWS_FUNC",
        DEFAULT_WORKING_WINDOWS_PATH,
    )
    working_windows_func = load_callable(working_windows_path, "SLOTS_GET_WORKING_WINDOWS_FUNC")
    if working_windows_func is None:
        raise ValueError("SLOTS_GET_WORKING_WINDOWS_FUNC must be configured.")

    busy_intervals_func = load_callable(get_setting("SLOTS_GET_BUSY_INTERVALS_FUNC", None), "SLOTS_GET_BUSY_INTERVALS_FUNC")

    max_slots_per_day = int(get_setting("SLOTS_MAX_SLOTS_PER_DAY", 500))
    results: Dict[date, List[Slot]] = {}

    busy_intervals: List[Tuple[datetime, datetime]] = []
    if busy_intervals_func:
        busy_intervals = _validate_intervals_are_aware(
            _fetch_busy_intervals(
                busy_intervals_func,
                provider=provider,
                service=service,
                start_date=start_date,
                end_date=end_date,
                tz=tz,
                tenant=tenant,
            ),
            tz,
        )

    capacity_total = _get_capacity(service)
    addon_ids = [getattr(addon, "id", None) for addon in addons or [] if getattr(addon, "id", None) is not None]
    meta_base = {
        "buffer_before_minutes": buffer_before,
        "buffer_after_minutes": buffer_after,
        "duration_minutes": duration_minutes,
    }
    if addon_ids:
        meta_base["addons_applied"] = addon_ids

    for day in daterange(start_date, end_date):
        day_slots: List[Slot] = []
        windows = _fetch_working_windows(
            working_windows_func,
            provider=provider,
            day=day,
            tz=tz,
            tenant=tenant,
        )
        for window_start, window_end in windows:
            window_start = ensure_aware(window_start, tz, name="working window start")
            window_end = ensure_aware(window_end, tz, name="working window end")
            if window_end <= window_start:
                continue

            start_cursor = ceil_to_interval(window_start, interval_minutes)
            while start_cursor + booking_window_td <= window_end:
                visible_end = start_cursor + duration_td
                buffered_start = start_cursor - buffer_before_td
                buffered_end = visible_end + buffer_after_td

                if buffered_start < window_start or buffered_end > window_end:
                    start_cursor += interval_td
                    continue
                if start_cursor < earliest_start:
                    start_cursor += interval_td
                    continue
                if latest_start and start_cursor > latest_start:
                    break

                slot = Slot(
                    start=start_cursor,
                    end=visible_end,
                    provider_id=get_identifier(provider, None),
                    service_id=get_identifier(service, None),
                    capacity_total=capacity_total,
                    capacity_remaining=capacity_total,
                    meta=dict(meta_base),
                )
                day_slots.append(slot)

                if len(day_slots) >= max_slots_per_day:
                    break
                start_cursor += interval_td

            if len(day_slots) >= max_slots_per_day:
                break

        if busy_intervals:
            filtered: List[Slot] = []
            for slot in day_slots:
                buffered_start = slot.start - buffer_before_td
                buffered_end = slot.end + buffer_after_td
                if any(overlaps(buffered_start, buffered_end, b_start, b_end) for b_start, b_end in busy_intervals):
                    continue
                filtered.append(slot)
            day_slots = filtered

        if day_slots:
            results[day] = day_slots

    return results
