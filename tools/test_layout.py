"""The device layout uses the 240px master mockup anchors."""

import unittest

from layout import (
    DATE_DAY_Y,
    DATE_MONTH_Y,
    HOUR_CX,
    METRIC_ROW,
    MINUTE_CX,
    ROW1_Y,
    STEPS_Y,
    TUBE_W,
    at,
    tube_box,
    well_center,
    well_radius,
)


class LayoutTests(unittest.TestCase):
    def test_240_anchors_match_the_mockup_pixels(self):
        self.assertEqual(tube_box(240, "hour")[0], HOUR_CX - TUBE_W // 2)
        self.assertEqual(tube_box(240, "minute")[0], MINUTE_CX - TUBE_W // 2)
        self.assertEqual(tube_box(240, "hour")[1], 42)
        self.assertEqual(tube_box(240, "hour")[3], 166)
        self.assertEqual(well_center(240), (125, 72))
        self.assertEqual(well_radius(240), 25)

    def test_enduro_scales_the_same_anchors(self):
        self.assertEqual(at(280, HOUR_CX), round(HOUR_CX * 280 / 240))
        hour = tube_box(280, "hour")
        minute = tube_box(280, "minute")
        well_x, well_y = well_center(280)
        self.assertLess(hour[2], well_x - well_radius(280))
        self.assertGreater(minute[0], well_x + well_radius(280))
        self.assertLess(well_y, 140)

    def test_date_sits_below_the_seconds_ring(self):
        ring_bottom = at(240, 72) + at(240, 25)
        self.assertGreater(at(240, DATE_MONTH_Y), ring_bottom)
        self.assertGreater(at(240, DATE_DAY_Y), at(240, DATE_MONTH_Y))
        self.assertGreater(at(240, ROW1_Y), at(240, DATE_DAY_Y))
        self.assertGreater(at(240, METRIC_ROW), at(240, ROW1_Y))
        self.assertGreater(at(240, STEPS_Y), at(240, METRIC_ROW))
