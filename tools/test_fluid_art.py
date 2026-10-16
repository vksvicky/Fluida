"""The fluid sprite is a cylinder, not a flat rectangle."""

import unittest

from fluid_art import HOUR, render_sprite


class FluidArtTests(unittest.TestCase):
    def test_core_is_brighter_than_the_glass_edge(self):
        image = render_sprite(240, HOUR)
        body = image.height - 4
        edge = image.getpixel((0, body))
        core = image.getpixel((image.width // 2, body))
        self.assertGreater(core[2], edge[2] + 40)
        self.assertGreater(core[0], edge[0])

    def test_meniscus_caps_the_column(self):
        image = render_sprite(240, HOUR)
        cap = image.getpixel((image.width // 2, 0))
        self.assertEqual(cap[3], 255)
        self.assertGreater(cap[0], 200)
