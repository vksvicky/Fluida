"""The baked photorealistic plate keeps the 3D tube bores ready for live fluid."""

import unittest

from dial_plate import render_plate
from layout import HOUR_CX, well_center


class DialPlateTests(unittest.TestCase):
    def test_hour_bore_stays_dark(self):
        image = render_plate(240).convert("RGB")
        bore = image.getpixel((HOUR_CX + 6, 100))
        cap = image.getpixel((HOUR_CX - 2, 30))
        self.assertLess(bore[0], 65)
        self.assertGreater(sum(cap), sum(bore) + 80)

    def test_dial_is_one_neutral_color(self):
        image = render_plate(240).convert("RGB")
        center = image.getpixel((122, 130))
        beside = image.getpixel((122, 115))
        self.assertLess(abs(center[0] - beside[0]), 15)
        self.assertLess(abs(center[0] - center[1]), 12)
        self.assertGreater(center[0], 20)
        self.assertLess(center[0], 75)

    def test_seconds_ring_is_lighter_than_its_center(self):
        image = render_plate(240).convert("RGB")
        wx, wy = well_center(240)
        center = max(image.getpixel((wx, wy)))
        rim = max(image.getpixel((wx, wy - 20)))
        self.assertLess(center, 90)
        self.assertGreater(rim, center)
