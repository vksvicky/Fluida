"""The photorealistic fluid sprite has a 3D cylindrical core and meniscus highlight."""

import unittest

from fluid_art import HOUR, render_sprite


class FluidArtTests(unittest.TestCase):
    def test_core_is_brighter_than_the_glass_edge(self):
        image = render_sprite(240, HOUR)
        body = image.height // 2
        edge = image.getpixel((0, body))
        core = image.getpixel((image.width // 2, body))
        self.assertGreater(core[2], edge[2] + 40)

    def test_meniscus_caps_the_column(self):
        image = render_sprite(240, HOUR)
        cx = image.width // 2
        peak_blue = max(image.getpixel((cx, y))[2] for y in range(12))
        self.assertEqual(image.getpixel((cx, 4))[3], 255)
        self.assertGreater(peak_blue, 200)
