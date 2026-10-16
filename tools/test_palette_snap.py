"""Palette snapping removes dither speckle without inventing extra colors."""

import unittest

from PIL import Image

from palette_snap import build_palette, palette_block, quantize_dial, snap_image


class PaletteSnapTests(unittest.TestCase):
    def test_a_smooth_gradient_stays_in_bands_instead_of_speckle(self):
        image = Image.new("RGB", (80, 8))
        for x in range(80):
            shade = int(x * 255 / 79)
            for y in range(8):
                image.putpixel((x, y), (shade, shade, shade))
        snapped = snap_image(image, build_palette(image, 8))
        colors = set()
        for x in range(80):
            top = snapped.getpixel((x, 0))
            bottom = snapped.getpixel((x, 7))
            self.assertEqual(top, bottom)
            colors.add(top[:3])
        self.assertLessEqual(len(colors), 8)

    def test_clear_pixels_stay_clear(self):
        image = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        image.putpixel((1, 1), (20, 40, 200, 255))
        snapped = snap_image(image, [(0, 0, 255)])
        self.assertEqual(snapped.getpixel((0, 0))[3], 0)
        self.assertEqual(snapped.getpixel((1, 1))[:3], (0, 0, 255))

    def test_blue_glass_stays_blue(self):
        image = Image.new("RGB", (24, 24), (16, 70, 220))
        for x in range(12):
            image.putpixel((x, 0), (0, 0, 0))
            image.putpixel((x, 1), (16, 210, 205))
        snapped, _palette = quantize_dial(image, 128)
        red, green, blue = snapped.getpixel((20, 20))[:3]
        self.assertGreater(blue, green)
        self.assertGreater(blue, red)

    def test_resource_palette_disables_dithering(self):
        xml = palette_block("dial_bg", "dial_bg.png", [(0, 0, 0), (35, 145, 255)])
        self.assertIn('dithering="none"', xml)
        self.assertIn("<color>000000</color>", xml)
        self.assertIn("<color>2391FF</color>", xml)
