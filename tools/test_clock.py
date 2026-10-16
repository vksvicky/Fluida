"""Clock fill matches the locked hour and minute model."""

import unittest

from clock import display_hour, hour_fill, minute_fill


class ClockTests(unittest.TestCase):
    def test_midnight_and_noon_are_twelve(self):
        self.assertEqual(display_hour(0), 12)
        self.assertEqual(display_hour(12), 12)
        self.assertEqual(display_hour(13), 1)
        self.assertEqual(display_hour(23), 11)

    def test_hour_column_is_empty_at_one_and_full_at_twelve(self):
        self.assertEqual(hour_fill(1), 0)
        self.assertEqual(hour_fill(13), 0)
        self.assertAlmostEqual(hour_fill(10), 9 / 11)
        self.assertEqual(hour_fill(0), 1)
        self.assertEqual(hour_fill(12), 1)

    def test_minute_column_includes_seconds_and_stays_below_one(self):
        self.assertEqual(minute_fill(0, 0), 0)
        self.assertAlmostEqual(minute_fill(30, 0), 0.5)
        self.assertLess(minute_fill(59, 59), 1)
        self.assertGreater(minute_fill(59, 59), minute_fill(59, 0))
