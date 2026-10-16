"""The device layout uses the 240px mockup anchors, not the overlapping box grid."""

import unittest

from layout import at, tube_box, well_center, well_radius


class LayoutTests(unittest.TestCase):
    def test_240_anchors_match_the_mockup_pixels(self):
        self.assertEqual(tube_box(240, "hour")[0], 55 - 10)
        self.assertEqual(tube_box(240, "minute")[0], 185 - 10)
        self.assertEqual(tube_box(240, "hour")[1], 52)
        self.assertEqual(tube_box(240, "hour")[3], 184)
        self.assertEqual(well_center(240), (120, 66))
        self.assertEqual(well_radius(240), 20)

    def test_enduro_scales_the_same_anchors(self):
        self.assertEqual(at(280, 55), round(55 * 280 / 240))
        hour = tube_box(280, "hour")
        minute = tube_box(280, "minute")
        well_x, well_y = well_center(280)
        self.assertLess(hour[2], well_x - well_radius(280))
        self.assertGreater(minute[0], well_x + well_radius(280))
        self.assertLess(well_y, 140)

    def test_date_sits_below_the_seconds_ring(self):
        ring_bottom = at(240, 66) + at(240, 20)
        self.assertGreater(at(240, 105), ring_bottom)
        self.assertGreater(at(240, 120), at(240, 105))
        self.assertGreater(at(240, 178), at(240, 148))
