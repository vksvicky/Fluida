"""Generate visual mockups for Variant A (Curved Arcs) and Variant D (Dual U-Tube with Closed Circuit Flow)."""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path("/Users/vivek/Development/Fluida")
MOCKUPS = ROOT / "mockups"
MOCKUPS.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1000, 1000
CX, CY = WIDTH // 2, HEIGHT // 2
RADIUS = 420

# Colors
BEZEL_DARK = (32, 34, 38, 255)
BEZEL_TITANIUM = (70, 74, 80, 255)
BEZEL_LIGHT = (110, 115, 125, 255)
DIAL_BG = (18, 20, 24, 255)
DIAL_SUBTLE = (28, 32, 38, 255)
TEXT_WHITE = (240, 242, 245, 255)
TEXT_MUTED = (120, 130, 142, 255)
GLASS_HIGHLIGHT = (255, 255, 255, 45)
GLASS_SHADOW = (10, 12, 16, 180)

# Fluid colors
BLUE_DEEP = (0, 75, 175, 255)
BLUE_GLOW = (20, 130, 255, 255)
BLUE_LIGHT = (80, 180, 255, 255)

CYAN_DEEP = (0, 150, 175, 255)
CYAN_GLOW = (0, 235, 220, 255)
CYAN_LIGHT = (140, 255, 245, 255)


def draw_watch_case(draw: ImageDraw.ImageDraw, img: Image.Image) -> None:
    # Outer strap shadow & base
    draw.ellipse((CX - RADIUS - 30, CY - RADIUS - 30, CX + RADIUS + 30, CY + RADIUS + 30), fill=(10, 11, 13, 255))
    # Titanium Bezel
    for r in range(RADIUS + 25, RADIUS, -1):
        ratio = (r - RADIUS) / 25.0
        val = int(45 + 50 * ratio)
        draw.ellipse((CX - r, CY - r, CX + r, CY + r), outline=(val, val + 4, val + 8, 255), width=2)
    # Bezel tick ring
    draw.ellipse((CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS), fill=DIAL_BG, outline=BEZEL_LIGHT, width=3)
    # Dial inner chamfer
    draw.ellipse((CX - RADIUS + 8, CY - RADIUS + 8, CX + RADIUS - 8, CY + RADIUS - 8), outline=(26, 28, 34, 255), width=4)


def render_variant_a_curved_arcs() -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (12, 14, 16, 255))
    draw = ImageDraw.Draw(img)
    draw_watch_case(draw, img)

    # Dial plate with concentric guilloche
    for r in range(30, 320, 12):
        draw.ellipse((CX - r, CY - r, CX + r, CY + r), outline=(24, 27, 33, 255), width=1)

    # 1. Closed-loop flow reservoirs at top and bottom
    # Bottom reservoir (manifold where fluid drains to / pumps from)
    draw.rounded_rectangle((CX - 120, CY + 250, CX + 120, CY + 330), radius=16, fill=(24, 28, 35, 255), outline=(50, 56, 68, 255), width=2)
    draw.text((CX, CY + 290), "FLUID PUMP / SIPHON RETURN", fill=TEXT_MUTED, anchor="mm", font=None)

    # Top feeder loop
    draw.arc((CX - 80, CY - 340, CX + 80, CY - 260), start=180, end=360, fill=(45, 52, 64, 255), width=8)

    # 2. Curved Arc Tubes
    # Left Arc (Hours 1 to 12): radius 260, from 140 deg to 220 deg (or bottom to top: 220 to 140)
    # Let's define arc: 110 deg (bottom) to 250 deg (top) on left
    tube_r = 290
    tube_w = 26

    # Draw glass channel tracks
    bbox = (CX - tube_r, CY - tube_r, CX + tube_r, CY + tube_r)
    draw.arc(bbox, start=115, end=245, fill=(35, 42, 52, 255), width=tube_w)
    draw.arc(bbox, start=295, end=425, fill=(35, 42, 52, 255), width=tube_w)

    # Glass tube outlines
    inner_r = tube_r - tube_w // 2
    outer_r = tube_r + tube_w // 2
    draw.arc((CX - inner_r, CY - inner_r, CX + inner_r, CY + inner_r), start=113, end=247, fill=(70, 80, 96, 255), width=2)
    draw.arc((CX - outer_r, CY - outer_r, CX + outer_r, CY + outer_r), start=113, end=247, fill=(70, 80, 96, 255), width=2)
    draw.arc((CX - inner_r, CY - inner_r, CX + inner_r, CY + inner_r), start=293, end=427, fill=(70, 80, 96, 255), width=2)
    draw.arc((CX - outer_r, CY - outer_r, CX + outer_r, CY + outer_r), start=293, end=427, fill=(70, 80, 96, 255), width=2)

    # Fill Left Arc with Blue Liquid: Hour 10 out of 12.
    # Arc runs from 115 deg (bottom=1) to 245 deg (top=12). Span = 130 deg.
    # Level 10/12 = 115 + (10/12)*130 = 115 + 108 = 223 deg.
    draw.arc(bbox, start=115, end=223, fill=BLUE_GLOW, width=tube_w - 4)
    # Bright core
    draw.arc(bbox, start=115, end=223, fill=BLUE_LIGHT, width=8)

    # Meniscus bead at Hour 10
    rad_end = math.radians(223)
    mx = CX + tube_r * math.cos(rad_end)
    my = CY + tube_r * math.sin(rad_end)
    draw.ellipse((mx - 14, my - 14, mx + 14, my + 14), fill=(180, 225, 255, 255), outline=(255, 255, 255, 255), width=2)

    # Fill Right Arc with Cyan Liquid: Minute 10 out of 60.
    # Arc runs from 65 deg (bottom=00) to -65 (i.e. 295 deg to 425 deg). Bottom is 425 deg (or 65 deg).
    # Filling upward: from 65 deg moving counter-clockwise or clockwise?
    # Let's say it fills bottom-up: from 65 deg up to -65 deg (spanning 130 deg).
    # Minute 10/60 = (10/60)*130 = 21.6 deg upward from 65 deg -> 65 - 22 = 43 deg (which is 403 deg to 425 deg).
    draw.arc(bbox, start=403, end=425, fill=CYAN_GLOW, width=tube_w - 4)
    draw.arc(bbox, start=403, end=425, fill=CYAN_LIGHT, width=8)

    rad_m_end = math.radians(403)
    mmx = CX + tube_r * math.cos(rad_m_end)
    mmy = CY + tube_r * math.sin(rad_m_end)
    draw.ellipse((mmx - 14, mmy - 14, mmx + 14, mmy + 14), fill=(200, 255, 250, 255), outline=(255, 255, 255, 255), width=2)

    # Calibration ticks & numbers
    for h in range(1, 13):
        frac = (h - 1) / 11.0
        ang = math.radians(115 + frac * 130)
        tx = CX + (tube_r - 34) * math.cos(ang)
        ty = CY + (tube_r - 34) * math.sin(ang)
        draw.text((tx, ty), str(h), fill=(210, 220, 235, 255) if h <= 10 else (90, 100, 115, 255), anchor="mm")

    for m in (0, 10, 20, 30, 40, 50, 60):
        frac = m / 60.0
        ang = math.radians(65 - frac * 130)
        tx = CX + (tube_r + 36) * math.cos(ang)
        ty = CY + (tube_r + 36) * math.sin(ang)
        draw.text((tx, ty), f"{m:02d}", fill=(180, 245, 240, 255) if m <= 10 else (90, 100, 115, 255), anchor="mm")

    # Connecting siphon return pipes
    # Bottom left pipe to reservoir
    draw.line((CX - 150, CY + 270, CX - 80, CY + 270), fill=(60, 75, 95, 255), width=6)
    draw.line((CX + 80, CY + 270, CX + 150, CY + 270), fill=(50, 85, 90, 255), width=6)

    # Center branding & complication
    draw.text((CX, CY - 140), "FLUIDA", fill=TEXT_WHITE, anchor="mm", font=None)
    draw.text((CX, CY - 110), "RETROGRADE CLEPSYDRA", fill=TEXT_MUTED, anchor="mm", font=None)

    # Central Water Ripple Complication
    draw.ellipse((CX - 60, CY - 30, CX + 60, CY + 90), outline=(40, 50, 65, 255), width=2)
    draw.ellipse((CX - 40, CY - 10, CX + 40, CY + 70), outline=(55, 75, 100, 255), width=1)
    draw.text((CX, CY + 20), "10 : 10", fill=(255, 255, 255, 220), anchor="mm")
    draw.text((CX, CY + 45), "WED 14 • 82%", fill=TEXT_MUTED, anchor="mm")

    return img


def render_variant_d_dual_utube() -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (12, 14, 16, 255))
    draw = ImageDraw.Draw(img)
    draw_watch_case(draw, img)

    # Top feeder chamber (where fluid originates / circulates)
    draw.rounded_rectangle((CX - 160, CY - 310, CX + 160, CY - 240), radius=14, fill=(25, 30, 38, 255), outline=(55, 65, 80, 255), width=2)
    draw.text((CX, CY - 275), "TOP EXPANSION MANIFOLD", fill=TEXT_MUTED, anchor="mm")

    # Two Glass U-Tubes: Left for Hours, Right for Minutes
    # Each U-tube has an outer down-leg and inner up-leg with a bottom U-turn loop
    for x_mid, is_left in [(-110, True), (110, False)]:
        col_x = CX + x_mid
        y_top = CY - 210
        y_bot = CY + 190
        w = 34

        # U-tube glass background
        draw.rounded_rectangle((col_x - w, y_top, col_x + w, y_bot), radius=w, fill=(22, 26, 34, 255), outline=(60, 70, 85, 255), width=3)

        # Fluid column
        if is_left:
            # Hour 10 / 12 -> 83% fill
            fill_h = int((y_bot - y_top) * 0.83)
            fill_y = y_bot - fill_h
            draw.rounded_rectangle((col_x - w + 4, fill_y, col_x + w - 4, y_bot - 4), radius=w - 4, fill=BLUE_GLOW)
            draw.rounded_rectangle((col_x - w + 12, fill_y + 4, col_x + w - 12, y_bot - 8), radius=w - 12, fill=BLUE_LIGHT)
            # Meniscus curve
            draw.ellipse((col_x - w + 4, fill_y - 6, col_x + w - 4, fill_y + 10), fill=(200, 235, 255, 255))
            # Graduation ticks
            for h in range(1, 13):
                frac = (h - 1) / 11.0
                ty = y_bot - 20 - int(frac * (y_bot - y_top - 60))
                draw.line((col_x - w - 16, ty, col_x - w - 4, ty), fill=(180, 190, 210, 255), width=2)
                draw.text((col_x - w - 24, ty), str(h), fill=(220, 230, 245, 255) if h <= 10 else (80, 90, 105, 255), anchor="rm")
            draw.text((col_x, y_bot + 28), "HOURS", fill=(100, 160, 255, 255), anchor="mm")
        else:
            # Minute 10 / 60 -> 16.7% fill
            fill_h = int((y_bot - y_top) * 0.17)
            fill_y = y_bot - fill_h
            draw.rounded_rectangle((col_x - w + 4, fill_y, col_x + w - 4, y_bot - 4), radius=w - 4, fill=CYAN_GLOW)
            draw.rounded_rectangle((col_x - w + 12, fill_y + 4, col_x + w - 12, y_bot - 8), radius=w - 12, fill=CYAN_LIGHT)
            # Meniscus curve
            draw.ellipse((col_x - w + 4, fill_y - 6, col_x + w - 4, fill_y + 10), fill=(220, 255, 250, 255))
            # Graduation ticks
            for m in (0, 10, 20, 30, 40, 50, 60):
                frac = m / 60.0
                ty = y_bot - 20 - int(frac * (y_bot - y_top - 60))
                draw.line((col_x + w + 4, ty, col_x + w + 16, ty), fill=(160, 220, 215, 255), width=2)
                draw.text((col_x + w + 24, ty), f"{m:02d}", fill=(180, 245, 240, 255) if m <= 10 else (80, 90, 105, 255), anchor="lm")
            draw.text((col_x, y_bot + 28), "MINUTES", fill=(0, 235, 220, 255), anchor="mm")

    # Recirculation siphon loop at the bottom connecting both to a central purge valve
    draw.arc((CX - 60, CY + 180, CX + 60, CY + 260), start=0, end=180, fill=(70, 85, 105, 255), width=8)
    draw.ellipse((CX - 12, CY + 250, CX + 12, CY + 274), fill=(90, 105, 130, 255), outline=(140, 160, 190, 255), width=2)
    draw.text((CX, CY + 295), "AUTO-SIPHON FLUSH RESET", fill=TEXT_MUTED, anchor="mm")

    # Center branding & complications
    draw.text((CX, CY - 100), "FLUIDA", fill=TEXT_WHITE, anchor="mm")
    draw.text((CX, CY - 75), "TWIN MANOMETER", fill=TEXT_MUTED, anchor="mm")

    # Central status display
    draw.rounded_rectangle((CX - 50, CY - 20, CX + 50, CY + 40), radius=8, fill=(24, 28, 36, 255), outline=(45, 55, 70, 255), width=1)
    draw.text((CX, CY), "14 OCT", fill=TEXT_WHITE, anchor="mm")
    draw.text((CX, CY + 22), "82% BAT", fill=(100, 220, 140, 255), anchor="mm")

    return img


if __name__ == "__main__":
    img_a = render_variant_a_curved_arcs()
    img_a.save(MOCKUPS / "mockup_vessels_variant_A_curved_arcs.png")
    print(f"Saved: {MOCKUPS / 'mockup_vessels_variant_A_curved_arcs.png'}")

    img_d = render_variant_d_dual_utube()
    img_d.save(MOCKUPS / "mockup_vessels_variant_D_dual_utube.png")
    print(f"Saved: {MOCKUPS / 'mockup_vessels_variant_D_dual_utube.png'}")
