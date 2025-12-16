import datetime

from django.test import SimpleTestCase

from slots.utils import ceil_to_interval


class UtilsTests(SimpleTestCase):
    def test_ceil_to_interval_rounds_up(self):
        dt = datetime.datetime(2024, 1, 1, 10, 7, 10, tzinfo=datetime.timezone.utc)
        rounded = ceil_to_interval(dt, 15)
        self.assertEqual(rounded, datetime.datetime(2024, 1, 1, 10, 15, tzinfo=datetime.timezone.utc))

    def test_ceil_to_interval_keeps_aligned_value(self):
        dt = datetime.datetime(2024, 1, 1, 10, 30, tzinfo=datetime.timezone.utc)
        self.assertEqual(ceil_to_interval(dt, 15), dt)
