import datetime
from datetime import date

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.utils import timezone

from slots.selectors import list_available_slots, list_available_slots_for_service
from slots.tests.fakes import AddonStub, ProviderStub, ServiceStub


@override_settings(SLOTS_GET_WORKING_WINDOWS_FUNC="slots.tests.fakes.simple_working_windows")
class SelectorTests(TestCase):
    def test_addon_ids_are_resolved(self):
        addon = AddonStub(addon_id=1, extra_duration_minutes=15)
        service = ServiceStub(duration_minutes=30, addons=[addon])
        provider = ProviderStub()
        day = date(2024, 1, 1)

        result = list_available_slots(
            service=service,
            provider=provider,
            start_date=day,
            end_date=day,
            tz=datetime.timezone.utc,
            now_dt=timezone.make_aware(datetime.datetime(2023, 12, 31, 9, 0), datetime.timezone.utc),
            addon_ids=[1],
        )
        slot = result[day][0]
        self.assertEqual(slot.end, datetime.datetime(2024, 1, 1, 9, 45, tzinfo=datetime.timezone.utc))
        self.assertEqual(slot.meta.get("addons_applied"), [1])

    def test_missing_provider_model_raises(self):
        service = ServiceStub()
        with self.assertRaises(ImproperlyConfigured):
            list_available_slots_for_service(
                service=service,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 1),
                tz=datetime.timezone.utc,
                now_dt=timezone.make_aware(datetime.datetime(2023, 12, 31, 9, 0), datetime.timezone.utc),
            )
