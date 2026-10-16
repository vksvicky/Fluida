"""Dial anchors taken from the 240px Fluida mockup, then scaled to the screen."""

from __future__ import annotations

# Positions are pixels on the 240px mockup in tools/generate_fluida_240_dial.py.
BASIS = 240
HOUR_CX = 55
MINUTE_CX = 185
TUBE_W = 21
TUBE_TOP = 52
TUBE_BOTTOM = 184
BRAND_Y = 28
SECONDS_Y = 66
SECONDS_R = 20
DATE_MONTH_Y = 105
DATE_DAY_Y = 120
FLANK_LEFT = 88
FLANK_RIGHT = 152
METRIC_ROW = 148
STEPS_Y = 178
MENISCUS = 6

FLOOR = (0x12, 0x18, 0x20)
# Brighter than the spec swatches so the columns match the mockup glass.
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
    """Inner glass the live fluid sprite is clipped to."""
    left, top, right, bottom = tube_box(size, side)
    inset = max(1, at(size, 2))
    return left + inset, top, right - inset, bottom


def sight_box(size: int, side: str) -> tuple[int, int, int, int]:
    """Reservoir window under a tube. Same integer math as the watch face."""
    left, _top, right, bottom = tube_box(size, side)
    width = right - left
    mid = left + width // 2
    res_w = width + at(size, 8)
    res_top = bottom - at(size, 2)
    sight_x = max(1, at(size, 4))
    sight_y = max(1, at(size, 5))
    return (
        mid - res_w // 2 + sight_x,
        res_top + sight_y,
        mid + res_w // 2 - sight_x,
        res_top + at(size, 25) - sight_y,
    )


def well_center(size: int) -> tuple[int, int]:
    return at(size, BASIS // 2), at(size, SECONDS_Y)


def well_radius(size: int) -> int:
    return at(size, SECONDS_R)
