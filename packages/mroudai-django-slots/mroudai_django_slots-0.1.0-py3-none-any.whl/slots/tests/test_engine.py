import datetime
from datetime import date

from django.test import TestCase, override_settings
from django.utils import timezone

from slots.engine import generate_slots
from slots.tests.fakes import (
    AddonStub,
    ProviderStub,
    ServiceStub,
    buffered_working_windows,
    busy_intervals_sample,
    long_working_windows,
    simple_working_windows,
)


@override_settings(SLOTS_GET_WORKING_WINDOWS_FUNC="slots.tests.fakes.simple_working_windows")
class EngineWorkingWindowTests(TestCase):
    def setUp(self):
        self.provider = ProviderStub()
        self.day = date(2024, 1, 1)

    def test_fixed_start_times_alignment(self):
        service = ServiceStub(duration_minutes=20, fixed_start_times_only=True, start_time_interval_minutes=20)
        slots = generate_slots(
            service=service,
            provider=self.provider,
            start_date=self.day,
            end_date=self.day,
            tz=datetime.timezone.utc,
            now_dt=timezone.make_aware(datetime.datetime(2023, 12, 31, 8, 0), datetime.timezone.utc),
        )
        self.assertIn(self.day, slots)
        self.assertEqual([slot.start.minute for slot in slots[self.day]], [0, 20, 40])

    @override_settings(SLOTS_GET_WORKING_WINDOWS_FUNC="slots.tests.fakes.buffered_working_windows")
    def test_buffer_respected_inside_window(self):
        service = ServiceStub(duration_minutes=20, buffer_before_minutes=5, buffer_after_minutes=5)
        slots = generate_slots(
            service=service,
            provider=self.provider,
            start_date=self.day,
            end_date=self.day,
            tz=datetime.timezone.utc,
            now_dt=timezone.make_aware(datetime.datetime(2023, 12, 31, 8, 0), datetime.timezone.utc),
        )
        starts = [slot.start.time() for slot in slots[self.day]]
        self.assertEqual(starts, [datetime.time(9, 15), datetime.time(9, 30)])

    def test_duration_with_addons_extends_end(self):
        addon = AddonStub(addon_id=1, extra_duration_minutes=15)
        service = ServiceStub(duration_minutes=30)
        slots = generate_slots(
            service=service,
            provider=self.provider,
            start_date=self.day,
            end_date=self.day,
            tz=datetime.timezone.utc,
            now_dt=timezone.make_aware(datetime.datetime(2023, 12, 31, 8, 0), datetime.timezone.utc),
            addons=[addon],
        )
        ends = [slot.end.time() for slot in slots[self.day]]
        self.assertEqual(ends[:2], [datetime.time(9, 45), datetime.time(10, 0)])

    @override_settings(SLOTS_GET_WORKING_WINDOWS_FUNC="slots.tests.fakes.long_working_windows")
    def test_minimum_notice_filters_early_slots(self):
        service = ServiceStub(duration_minutes=30, minimum_notice_minutes=120)
        now_dt = timezone.make_aware(datetime.datetime(2024, 1, 1, 8, 0), datetime.timezone.utc)
        slots = generate_slots(
            service=service,
            provider=self.provider,
            start_date=self.day,
            end_date=self.day,
            tz=datetime.timezone.utc,
            now_dt=now_dt,
        )
        starts = [slot.start for slot in slots[self.day]]
        self.assertTrue(all(start >= timezone.make_aware(datetime.datetime(2024, 1, 1, 10, 0), datetime.timezone.utc) for start in starts))

    def test_maximum_advance_blocks_far_future(self):
        service = ServiceStub(duration_minutes=30, maximum_advance_days=1)
        future_day = self.day + datetime.timedelta(days=2)
        now_dt = timezone.make_aware(datetime.datetime(2024, 1, 1, 8, 0), datetime.timezone.utc)
        slots = generate_slots(
            service=service,
            provider=self.provider,
            start_date=future_day,
            end_date=future_day,
            tz=datetime.timezone.utc,
            now_dt=now_dt,
        )
        self.assertEqual(slots, {})

    def test_working_window_slicing_count(self):
        service = ServiceStub(duration_minutes=30)
        slots = generate_slots(
            service=service,
            provider=self.provider,
            start_date=self.day,
            end_date=self.day,
            tz=datetime.timezone.utc,
            now_dt=timezone.make_aware(datetime.datetime(2023, 12, 31, 8, 0), datetime.timezone.utc),
        )
        self.assertEqual(len(slots[self.day]), 3)

    @override_settings(
        SLOTS_GET_WORKING_WINDOWS_FUNC="slots.tests.fakes.simple_working_windows",
        SLOTS_GET_BUSY_INTERVALS_FUNC="slots.tests.fakes.busy_intervals_sample",
    )
    def test_busy_intervals_remove_overlaps(self):
        service = ServiceStub(duration_minutes=30)
        slots = generate_slots(
            service=service,
            provider=self.provider,
            start_date=self.day,
            end_date=self.day,
            tz=datetime.timezone.utc,
            now_dt=timezone.make_aware(datetime.datetime(2023, 12, 31, 8, 0), datetime.timezone.utc),
        )
        # busy interval 09:10-09:25 removes first two slots, leaving only the final candidate
        self.assertEqual([slot.start.time() for slot in slots[self.day]], [datetime.time(9, 30)])
