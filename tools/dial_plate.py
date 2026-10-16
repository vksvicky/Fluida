"""Photorealistic 3D Fluida dial plate composited from the studio master art:
brushed Grade-5 titanium bezel and caps, 3D smoky borosilicate glass cylinders,
smooth matte slate dial face, calibrated regulator scales, brand header, and
the 4x supersampled bullseye spirit-level water chamber.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from layout import (
    BASIS,
    BRAND_Y,
    DATE_DAY_Y,
    DATE_MONTH_Y,
    FLANK_LEFT,
    FLANK_RIGHT,
    METRIC_ROW,
    ROW1_Y,
    SECONDS_CX,
    SECONDS_Y,
    STEPS_Y,
    at,
)

ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MASTER_DIR = Path(__file__).resolve().parent / "master_art"

# Master 1024x1024 studio coordinates
_CX, _CY, _R = 501, 505, 270
_ATRIUM_CX = 512
_SEC_CX, _SEC_CY = 512, 397
_H_X1, _H_X2 = 375, 435
_M_X1, _M_X2 = 588, 648
_TUBE_Y_TOP, _TUBE_Y_BOT = 330, 608
_SPAN_Y1, _SPAN_Y2 = 356, 582
_SPAN_H = _SPAN_Y2 - _SPAN_Y1

_MASTER_PLATE: Image.Image | None = None


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = ARIAL_BOLD if bold else ARIAL
    return ImageFont.truetype(path, max(6, size))


def _build_spirit_chamber() -> Image.Image:
    """4x supersampled bullseye horological spirit-level subdial."""
    scale = 4
    cw = 140 * scale
    ch = 140 * scale
    ccx = cw // 2
    ccy = ch // 2

    chamber_hi = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    scd = ImageDraw.Draw(chamber_hi)

    # Translucent sapphire-slate fluid floor over the water caustics
    for r in range(int(53 * scale), 0, -2):
        frac = r / (53.0 * scale)
        alpha = int(220 - frac * 50)
        scd.ellipse((ccx - r, ccy - r, ccx + r, ccy + r), fill=(14, 20, 28, alpha))

    r_mid = int(36 * scale)
    r_inner = int(22 * scale)
    r_outer = int(48 * scale)

    scd.ellipse((ccx - r_outer, ccy - r_outer, ccx + r_outer, ccy + r_outer), outline=(0, 200, 240, 130), width=scale)
    scd.ellipse((ccx - r_mid, ccy - r_mid, ccx + r_mid, ccy + r_mid), outline=(0, 220, 255, 160), width=scale)
    scd.ellipse((ccx - r_inner, ccy - r_inner, ccx + r_inner, ccy + r_inner), outline=(0, 240, 255, 200), width=int(1.5 * scale))

    ch_len = 8 * scale
    gap_out = 4 * scale
    scd.line([(ccx - r_outer - gap_out, ccy), (ccx - r_mid + ch_len, ccy)], fill=(0, 230, 255, 170), width=scale)
    scd.line([(ccx + r_mid - ch_len, ccy), (ccx + r_outer + gap_out, ccy)], fill=(0, 230, 255, 170), width=scale)
    scd.line([(ccx, ccy - r_outer - gap_out), (ccx, ccy - r_mid + ch_len)], fill=(0, 230, 255, 170), width=scale)
    scd.line([(ccx, ccy + r_mid - ch_len), (ccx, ccy + r_outer + gap_out)], fill=(0, 230, 255, 170), width=scale)

    for s in range(60):
        ang = math.radians(s * 6.0 - 90.0)
        tr = 51.5 * scale
        px = ccx + tr * math.cos(ang)
        py = ccy + tr * math.sin(ang)
        if s % 5 == 0:
            r_dot = int(2.6 * scale)
            scd.ellipse((px - r_dot, py - r_dot, px + r_dot, py + r_dot), fill=(0, 240, 255, 240))
        else:
            r_dot = int(1.3 * scale)
            scd.ellipse((px - r_dot, py - r_dot, px + r_dot, py + r_dot), fill=(0, 185, 225, 115))

    return chamber_hi.resize((140, 140), Image.Resampling.LANCZOS)


def _smooth_slate_plate(base: Image.Image) -> Image.Image:
    """Smooth sandblast micro-noise on the dark slate face while keeping 100% of the 3D titanium hardware."""
    rgb = base.convert("RGB")
    blur_med = rgb.filter(ImageFilter.GaussianBlur(radius=6.0))
    blur_wide = rgb.filter(ImageFilter.GaussianBlur(radius=14.0))

    out = base.copy()
    for y in range(_CY - _R, _CY + _R):
        for x in range(_CX - _R, _CX + _R):
            if math.hypot(x - _CX, y - _CY) > 236:
                continue
            if (373 <= x <= 437 and 280 <= y <= 730) or (586 <= x <= 650 and 280 <= y <= 730):
                continue
            if math.hypot(x - _SEC_CX, y - _SEC_CY) <= 64:
                continue
            r, g, b = rgb.getpixel((x, y))
            rm, gm, bm = blur_med.getpixel((x, y))
            rw, gw, bw = blur_wide.getpixel((x, y))
            lum_m = (rm + gm + bm) / 3.0
            sat_m = max(rm, gm, bm) - min(rm, gm, bm)
            edge_diff = max(abs(rm - rw), abs(gm - gw), abs(bm - bw))
            if sat_m < 18 and 30 <= lum_m <= 76 and edge_diff <= 12:
                alpha = max(0.0, min(1.0, (12.0 - edge_diff) / 8.0))
                nr = int(round(r * (1.0 - alpha) + rm * alpha))
                ng = int(round(g * (1.0 - alpha) + gm * alpha))
                nb = int(round(b * (1.0 - alpha) + bm * alpha))
                out.putpixel((x, y), (nr, ng, nb, 255))
    return out


def _get_master_plate() -> Image.Image:
    """Build and cache the 540x540 photorealistic master dial plate."""
    global _MASTER_PLATE
    if _MASTER_PLATE is not None:
        return _MASTER_PLATE

    base = _smooth_slate_plate(Image.open(MASTER_DIR / "topdown_fluida_photorealistic_base.jpg").convert("RGBA"))
    empty_col = Image.open(MASTER_DIR / "tube_empty_col.png").convert("RGBA")

    # 1. Paste 3D translucent smoky borosilicate empty glass cylinders into both bores
    base.paste(empty_col, (_H_X1, _TUBE_Y_TOP), empty_col)
    base.paste(empty_col, (_M_X1, _TUBE_Y_TOP), empty_col)

    # 2. Composite 4x supersampled bullseye spirit-level subdial
    spirit_1x = _build_spirit_chamber()
    base.alpha_composite(spirit_1x, (_SEC_CX - 70, _SEC_CY - 70))

    # 3. Composite brand header and calibrated regulator scales
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(overlay)
    font_brand = _font(17, bold=False)
    font_scale = _font(16, bold=True)

    sdraw.text((_ATRIUM_CX, 296), "F   L   U   I   D   A", fill=(235, 240, 248, 235), font=font_brand, anchor="mm")

    for h in range(1, 13):
        frac = (h - 1) / 11.0
        y = _SPAN_Y2 - int(round(frac * _SPAN_H))
        sdraw.line([(_H_X1 - 8, y), (_H_X1 - 2, y)], fill=(245, 248, 252, 240), width=2)
        sdraw.text((_H_X1 - 11, y), str(h), fill=(245, 248, 252, 255), font=font_scale, anchor="rm")
        if h < 12:
            y_mid = y - int(round(0.5 / 11.0 * _SPAN_H))
            sdraw.line([(_H_X1 - 5, y_mid), (_H_X1 - 2, y_mid)], fill=(140, 155, 175, 165), width=1)

    for m in (0, 10, 20, 30, 40, 50, 60):
        frac = m / 60.0
        y = _SPAN_Y2 - int(round(frac * _SPAN_H))
        sdraw.line([(_M_X2 + 2, y), (_M_X2 + 8, y)], fill=(245, 248, 252, 240), width=2)
        sdraw.text((_M_X2 + 11, y), f"{m:02d}", fill=(245, 248, 252, 255), font=font_scale, anchor="lm")
        if m < 60:
            y_mid = y - int(round(5.0 / 60.0 * _SPAN_H))
            sdraw.line([(_M_X2 + 2, y_mid), (_M_X2 + 6, y_mid)], fill=(0, 235, 255, 210), width=2)

    base.alpha_composite(overlay)

    # 4. Crop to the 540x540 dial circle with pure black outside the round perimeter
    dial_box = (_CX - _R, _CY - _R, _CX + _R, _CY + _R)
    dial_cropped = base.crop(dial_box)
    mask = Image.new("L", (2 * _R, 2 * _R), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 2 * _R - 1, 2 * _R - 1), fill=255)

    master_circle = Image.new("RGBA", (2 * _R, 2 * _R), (0, 0, 0, 255))
    master_circle.paste(dial_cropped, (0, 0), mask)
    _MASTER_PLATE = master_circle
    return _MASTER_PLATE


def render_plate(size: int) -> Image.Image:
    """Render the photorealistic 3D horological dial plate at target screen size."""
    master = _get_master_plate()
    scaled = master.resize((size, size), Image.Resampling.LANCZOS)

    # Ensure outer corner pixels outside the circle stay strictly (0, 0, 0, 255)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    out.paste(scaled, (0, 0), mask)
    return out


def face_anchors(size: int) -> dict[str, tuple[int, int]]:
    """Centers the live text uses, in screen pixels."""
    return {
        "seconds": (at(size, SECONDS_CX), at(size, SECONDS_Y)),
        "month": (at(size, SECONDS_CX), at(size, DATE_MONTH_Y)),
        "day": (at(size, SECONDS_CX), at(size, DATE_DAY_Y)),
        "heart": (at(size, FLANK_LEFT), at(size, ROW1_Y)),
        "battery": (at(size, FLANK_RIGHT), at(size, ROW1_Y)),
        "calories": (at(size, FLANK_LEFT), at(size, METRIC_ROW)),
        "temperature": (at(size, FLANK_RIGHT), at(size, METRIC_ROW)),
        "steps": (at(size, SECONDS_CX), at(size, STEPS_Y)),
    }


def write_plate(size: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    render_plate(size).save(path)
