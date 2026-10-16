"""Static Fluida plate: glass, caps, scales, brand, and the seconds ring.

Live fluid, seconds, date, and metrics are drawn on top of this plate.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from layout import (
    BASIS,
    BRAND_Y,
    DATE_DAY_Y,
    DATE_MONTH_Y,
    FLANK_LEFT,
    FLANK_RIGHT,
    HOUR_CX,
    METRIC_ROW,
    MINUTE_CX,
    SECONDS_R,
    SECONDS_Y,
    STEPS_Y,
    TUBE_BOTTOM,
    TUBE_TOP,
    TUBE_W,
    at,
)

ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = ARIAL_BOLD if bold else ARIAL
    return ImageFont.truetype(path, max(6, size))


def render_plate(size: int) -> Image.Image:
    """Chrome only. The tube bores stay dark so the device can fill them."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    cx = at(size, BASIS // 2)
    radius = at(size, 118)
    # One neutral fill. A shaded stack of circles becomes colored rings on an 8-bit MIP palette.
    draw.ellipse(
        (cx - radius, cx - radius, cx + radius, cx + radius),
        fill=(40, 40, 40, 255),
        outline=(96, 100, 106, 255),
        width=max(1, at(size, 1)),
    )

    _tube_chrome(draw, size, HOUR_CX)
    _tube_chrome(draw, size, MINUTE_CX)
    _scales(draw, size)
    _brand(draw, size)
    _seconds_ring(draw, size)
    return image


def _tube_chrome(draw: ImageDraw.ImageDraw, size: int, center_basis: int) -> None:
    left, top, right, bottom = _tube(size, center_basis)
    width = right - left
    mid = (left + right) // 2
    cap_h = at(size, 14)
    cap_w = width + at(size, 6)
    cap_y1 = top - cap_h + at(size, 2)
    draw.rounded_rectangle(
        (mid - cap_w // 2, cap_y1, mid + cap_w // 2, top + at(size, 2)),
        radius=at(size, 4),
        fill=(52, 58, 68, 255),
        outline=(115, 126, 142, 255),
        width=max(1, at(size, 1)),
    )
    bolt = max(2, at(size, 3))
    draw.ellipse(
        (mid - bolt, cap_y1 + at(size, 3), mid + bolt, cap_y1 + at(size, 3) + bolt * 2),
        fill=(160, 170, 185, 255),
        outline=(40, 45, 55, 255),
    )
    res_w = width + at(size, 8)
    res_h = at(size, 25)
    res_top = bottom - at(size, 2)
    draw.rounded_rectangle(
        (mid - res_w // 2, res_top, mid + res_w // 2, res_top + res_h),
        radius=at(size, 4),
        fill=(46, 52, 62, 255),
        outline=(115, 126, 142, 255),
        width=max(1, at(size, 1)),
    )
    draw.line(
        (mid - res_w // 2 + at(size, 2), res_top + at(size, 3), mid + res_w // 2 - at(size, 2), res_top + at(size, 3)),
        fill=(160, 172, 190, 255),
    )
    sight_x = at(size, 4)
    sight_y = at(size, 5)
    draw.rounded_rectangle(
        (mid - res_w // 2 + sight_x, res_top + sight_y, mid + res_w // 2 - sight_x, res_top + res_h - sight_y),
        radius=at(size, 2),
        fill=(10, 12, 16, 255),
        outline=(70, 78, 90, 255),
    )
    nut = at(size, 5)
    draw.rounded_rectangle(
        (left - at(size, 2), bottom - nut, right + at(size, 2), bottom),
        radius=at(size, 2),
        fill=(65, 72, 85, 255),
        outline=(140, 152, 170, 255),
    )
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=at(size, 3),
        fill=(12, 16, 22, 255),
        outline=(70, 80, 96, 255),
        width=max(1, at(size, 1)),
    )
    inset = max(1, at(size, 2))
    draw.line((left + inset, top + inset, left + inset, bottom - inset), fill=(230, 242, 255, 255), width=max(1, at(size, 1)))
    draw.line((right - inset, top + inset, right - inset, bottom - inset), fill=(120, 145, 170, 255))


def _tube(size: int, center_basis: int) -> tuple[int, int, int, int]:
    left = at(size, center_basis) - at(size, TUBE_W) // 2
    return left, at(size, TUBE_TOP), left + at(size, TUBE_W), at(size, TUBE_BOTTOM)


def _scales(draw: ImageDraw.ImageDraw, size: int) -> None:
    font = _font(max(6, int(round(8.5 * size / BASIS))), bold=True)
    hour_left, top, _, bottom = _tube(size, HOUR_CX)
    _, _, minute_right, _ = _tube(size, MINUTE_CX)
    span = (bottom - at(size, 6)) - (top + at(size, 6))
    y0 = bottom - at(size, 6)
    ink = (236, 242, 248, 255)
    for hour in range(1, 13):
        y = y0 - int(round((hour - 1) / 11 * span))
        draw.line((hour_left - at(size, 8), y, hour_left - at(size, 2), y), fill=ink)
        draw.text((hour_left - at(size, 10), y), str(hour), fill=ink, font=font, anchor="rm")
        if hour < 12:
            mid_y = y - int(round(0.5 / 11 * span))
            draw.line((hour_left - at(size, 5), mid_y, hour_left - at(size, 2), mid_y), fill=(140, 155, 175, 255))
    for minute in (0, 10, 20, 30, 40, 50, 60):
        y = y0 - int(round(minute / 60 * span))
        label = f"{minute:02d}"
        draw.line((minute_right + at(size, 2), y, minute_right + at(size, 8), y), fill=ink)
        draw.text((minute_right + at(size, 10), y), label, fill=ink, font=font, anchor="lm")
        if minute < 60:
            mid_y = y - int(round(5 / 60 * span))
            draw.line((minute_right + at(size, 2), mid_y, minute_right + at(size, 5), mid_y), fill=(150, 210, 205, 255))


def _brand(draw: ImageDraw.ImageDraw, size: int) -> None:
    font = _font(max(8, int(round(9.5 * size / BASIS))))
    draw.text(
        (at(size, BASIS // 2), at(size, BRAND_Y)),
        "F   L   U   I   D   A",
        fill=(232, 238, 246, 255),
        font=font,
        anchor="mm",
    )


def _seconds_ring(draw: ImageDraw.ImageDraw, size: int) -> None:
    cx = at(size, BASIS // 2)
    cy = at(size, SECONDS_Y)
    radius = at(size, SECONDS_R)
    draw.ellipse((cx - radius - at(size, 2), cy - radius - at(size, 2), cx + radius + at(size, 2), cy + radius + at(size, 2)), outline=(28, 32, 40, 255))
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(75, 85, 100, 255), width=max(1, at(size, 2)))
    inner = max(1, at(size, 2))
    draw.ellipse((cx - radius + inner, cy - radius + inner, cx + radius - inner, cy + radius - inner), outline=(28, 32, 40, 255))
    for second in range(60):
        angle = math.radians(second * 6 - 90)
        inner = radius - (at(size, 3) if second % 5 == 0 else at(size, 1))
        outer = radius + at(size, 2)
        color = (230, 236, 244, 255) if second % 5 == 0 else (120, 130, 145, 255)
        draw.line(
            (
                cx + inner * math.cos(angle),
                cy + inner * math.sin(angle),
                cx + outer * math.cos(angle),
                cy + outer * math.sin(angle),
            ),
            fill=color,
            width=1,
        )


def face_anchors(size: int) -> dict[str, tuple[int, int]]:
    """Centers the live text uses, in screen pixels."""
    return {
        "seconds": (at(size, BASIS // 2), at(size, SECONDS_Y)),
        "month": (at(size, BASIS // 2), at(size, DATE_MONTH_Y)),
        "day": (at(size, BASIS // 2), at(size, DATE_DAY_Y)),
        "heart": (at(size, FLANK_LEFT), at(size, DATE_DAY_Y)),
        "battery": (at(size, FLANK_RIGHT), at(size, DATE_DAY_Y)),
        "calories": (at(size, FLANK_LEFT), at(size, METRIC_ROW)),
        "temperature": (at(size, FLANK_RIGHT), at(size, METRIC_ROW)),
        "steps": (at(size, BASIS // 2), at(size, STEPS_Y)),
    }


def write_plate(size: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    render_plate(size).save(path)
