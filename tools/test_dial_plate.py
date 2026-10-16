"""The baked plate keeps the tube bores empty so live fluid can be drawn on top."""

import unittest

from dial_plate import render_plate


class DialPlateTests(unittest.TestCase):
    def test_hour_bore_stays_dark(self):
        image = render_plate(240).convert("RGB")
        pixel = image.getpixel((55, 118))
        self.assertLess(max(pixel), 40)

    def test_dial_is_one_neutral_color(self):
        image = render_plate(240).convert("RGB")
        center = image.getpixel((120, 140))
        beside = image.getpixel((120, 100))
        self.assertEqual(center, beside)
        self.assertEqual(center[0], center[1])
        self.assertEqual(center[1], center[2])

    def test_seconds_ring_is_lighter_than_its_center(self):
        image = render_plate(240).convert("RGB")
        center = max(image.getpixel((120, 66)))
        rim = max(image.getpixel((120, 46)))
        self.assertLess(center, 80)
        self.assertGreater(rim, center)
