"""Dial anchors taken directly from the 540px Fluida master mockup scaled to 240px."""

from __future__ import annotations

# Positions are pixels on the 240px canvas mapped from the 540px dial master.
BASIS = 240
HOUR_CX = 77
MINUTE_CX = 172
TUBE_W = 27
TUBE_TOP = 42
TUBE_BOTTOM = 166
SPAN_TOP = 54
SPAN_BOTTOM = 154
BRAND_Y = 27
SECONDS_CX = 125
SECONDS_Y = 72
SECONDS_R = 25
SECONDS_ORBIT_R = 16
DATE_MONTH_Y = 109
DATE_DAY_Y = 120
FLANK_LEFT = 107
FLANK_RIGHT = 143
ROW1_Y = 141
METRIC_ROW = 160
STEPS_Y = 201
MENISCUS = 5

FLOOR = (0x12, 0x18, 0x20)
PALETTES = {
    0: ((0x23, 0x91, 0xFF), (0x1E, 0xF0, 0xE1), (0x00, 0xEB, 0xFF)),
    1: ((0xE6, 0x19, 0x4B), (0xF5, 0xB0, 0x41), (0xF5, 0xB0, 0x41)),
    2: ((0x9B, 0x59, 0xB6), (0x00, 0xFF, 0x7F), (0x00, 0xFF, 0x7F)),
    3: ((0x1A, 0x52, 0x76), (0xE0, 0xF7, 0xFA), (0xE0, 0xF7, 0xFA)),
}


def at(size: int, basis_px: int) -> int:
    """Scale a 240px mockup coordinate onto this screen."""
    return int(round(basis_px * size / BASIS))


def pixel(size: int, unit: float) -> int:
    return int(round(unit * size))


def tube_box(size: int, side: str) -> tuple[int, int, int, int]:
    center = HOUR_CX if side == "hour" else MINUTE_CX
    left = at(size, center) - at(size, TUBE_W) // 2
    right = left + at(size, TUBE_W)
    return left, at(size, TUBE_TOP), right, at(size, TUBE_BOTTOM)


def bore_box(size: int, side: str) -> tuple[int, int, int, int]:
    """Full 3D glass column bounds for the photorealistic fluid sprite."""
    return tube_box(size, side)


def scale_span(size: int) -> tuple[int, int]:
    """Top (12h / 60m) and bottom (1h / 00m) calibrated scale Y coordinates."""
    return at(size, SPAN_TOP), at(size, SPAN_BOTTOM)


def sight_box(size: int, side: str) -> tuple[int, int, int, int]:
    """Reservoir bounds under a tube."""
    left, _top, right, bottom = tube_box(size, side)
    return left, bottom, right, bottom + at(size, 18)


def well_center(size: int) -> tuple[int, int]:
    return at(size, SECONDS_CX), at(size, SECONDS_Y)


def well_radius(size: int) -> int:
    return at(size, SECONDS_R)
