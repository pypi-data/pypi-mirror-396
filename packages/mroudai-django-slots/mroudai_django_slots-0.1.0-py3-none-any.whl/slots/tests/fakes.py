from __future__ import annotations

import datetime
from typing import Iterable, List

from django.utils import timezone


class AddonStub:
    def __init__(self, addon_id: int, extra_duration_minutes: int = 0):
        self.id = addon_id
        self.extra_duration_minutes = extra_duration_minutes


class AddonManagerStub:
    def __init__(self, addons: Iterable[AddonStub]):
        self._addons = list(addons)

    def filter(self, id__in: Iterable[int]) -> List[AddonStub]:
        return [addon for addon in self._addons if addon.id in id__in]


class ServiceStub:
    def __init__(
        self,
        *,
        service_id=1,
        duration_minutes=30,
        buffer_before_minutes=0,
        buffer_after_minutes=0,
        minimum_notice_minutes=0,
        maximum_advance_days=None,
        fixed_start_times_only=False,
        start_time_interval_minutes=15,
        allow_multiple_clients_per_slot=False,
        capacity_total=1,
        addons=None,
        tenant=None,
    ):
        self.id = service_id
        self.duration_minutes = duration_minutes
        self.buffer_before_minutes = buffer_before_minutes
        self.buffer_after_minutes = buffer_after_minutes
        self.minimum_notice_minutes = minimum_notice_minutes
        self.maximum_advance_days = maximum_advance_days
        self.fixed_start_times_only = fixed_start_times_only
        self.start_time_interval_minutes = start_time_interval_minutes
        self.allow_multiple_clients_per_slot = allow_multiple_clients_per_slot
        self.capacity_total = capacity_total
        self.tenant = tenant
        if addons is not None:
            self.addons = AddonManagerStub(addons)


class ProviderStub:
    def __init__(self, provider_id=1, tenant=None):
        self.id = provider_id
        self.tenant = tenant


def _make_window(date, start_hour, start_minute, end_hour, end_minute, tz):
    tz = tz or datetime.timezone.utc
    start = datetime.datetime.combine(date, datetime.time(start_hour, start_minute))
    end = datetime.datetime.combine(date, datetime.time(end_hour, end_minute))
    return timezone.make_aware(start, tz), timezone.make_aware(end, tz)


def simple_working_windows(provider, date, tz=None, **kwargs):
    return [_make_window(date, 9, 0, 10, 0, tz)]


def buffered_working_windows(provider, date, tz=None, **kwargs):
    return [_make_window(date, 9, 5, 10, 0, tz)]


def long_working_windows(provider, date, tz=None, **kwargs):
    return [_make_window(date, 8, 0, 12, 0, tz)]


def busy_intervals_sample(provider, start_date, end_date, tz=None, **kwargs):
    tz = tz or datetime.timezone.utc
    start = datetime.datetime.combine(start_date, datetime.time(9, 10))
    end = datetime.datetime.combine(start_date, datetime.time(9, 25))
    return [(timezone.make_aware(start, tz), timezone.make_aware(end, tz))]
