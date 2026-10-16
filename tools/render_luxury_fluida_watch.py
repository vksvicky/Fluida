"""Luxury Horology Generator for FLUIDA Watch Face:
- Completely independent Hour (1-12) and Minute (00-60) tubes
- NO top connecting arc! NO bottom cross pipe!
- Dark ruthenium skeletonized dial plate with beveled bridge plates, circular gear trains, ruby jewels, and blued screws
- Brushed titanium knurled bezel with chamfered indices
- Crisp Swiss Avenir typography with exact calibrated markings:
    Left: 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
    Right: 60, 50, 40, 30, 20, 10, 00 with 5-min subticks
- Volumetric borosilicate glass cylinders with 3D cylindrical lighting and specular glints
- Buttery-smooth 36-frame animation showing:
    1. Minutes rising smoothly from 00 to 60
    2. Sucked-down vacuum drain rapidly pulling the minute fluid back into its bottom reservoir
    3. Smooth hydraulic step advancing the blue Hour tube from 10 to 11
    4. Rising 1-Hz micro-bubbles inside the liquid
"""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MOCKUPS = Path("/Users/vivek/Development/Fluida/mockups")
MOCKUPS.mkdir(parents=True, exist_ok=True)

SIZE = 900
CX, CY = SIZE // 2, SIZE // 2
RADIUS = 400

FONT_PATH = "/System/Library/Fonts/Avenir.ttc"


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_PATH, size, index=8 if bold else 0)
    except Exception:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)


# Tube positions - Completely separate!
TUBE_W = 82
TUBE_H = 400
TUBE_Y1 = CY - 200
TUBE_Y2 = TUBE_Y1 + TUBE_H

H_X1 = CX - 165
H_X2 = H_X1 + TUBE_W
H_CX = (H_X1 + H_X2) // 2

M_X1 = CX + 83
M_X2 = M_X1 + TUBE_W
M_CX = (M_X1 + M_X2) // 2


def render_luxury_dial_base() -> Image.Image:
    """Render a high-end luxury skeletonized titanium dial backdrop."""
    img = Image.new("RGBA", (SIZE, SIZE), (12, 14, 17, 255))
    draw = ImageDraw.Draw(img)

    # 1. Slate stone background texture with soft directional lighting
    for y in range(SIZE):
        noise = int(14 + 5 * math.sin(y * 0.05) + 3 * math.cos(y * 0.12))
        draw.line([(0, y), (SIZE, y)], fill=(noise, noise + 2, noise + 4, 255))

    # 2. Brushed Titanium Case & Lugs
    # Four rugged angled lugs
    lug_w = 95
    draw.polygon([(CX - 220, 40), (CX - 220 + lug_w, 40), (CX - 220 + lug_w + 35, 180), (CX - 220 - 25, 180)], fill=(45, 49, 57))
    draw.polygon([(CX + 220, 40), (CX + 220 - lug_w, 40), (CX + 220 - lug_w - 35, 180), (CX + 220 + 25, 180)], fill=(45, 49, 57))
    draw.polygon([(CX - 220, SIZE - 40), (CX - 220 + lug_w, SIZE - 40), (CX - 220 + lug_w + 35, SIZE - 180), (CX - 220 - 25, SIZE - 180)], fill=(45, 49, 57))
    draw.polygon([(CX + 220, SIZE - 40), (CX + 220 - lug_w, SIZE - 40), (CX + 220 - lug_w - 35, SIZE - 180), (CX + 220 + 25, SIZE - 180)], fill=(45, 49, 57))

    # Circular Titanium Case with metallic gradient
    for r in range(RADIUS + 45, RADIUS + 15, -1):
        ratio = (r - RADIUS - 15) / 30.0
        c = int(45 + 30 * ratio)
        draw.ellipse((CX - r, CY - r, CX + r, CY + r), outline=(c, c + 3, c + 8, 255), width=2)

    # Knurled Bezel Ring with authentic diamond knurling pattern
    bezel_r = RADIUS + 15
    for deg in range(0, 360, 2):
        rad = math.radians(deg)
        x_out = CX + bezel_r * math.cos(rad)
        y_out = CY + bezel_r * math.sin(rad)
        x_in = CX + (bezel_r - 14) * math.cos(rad)
        y_in = CY + (bezel_r - 14) * math.sin(rad)
        color = (100, 108, 120) if (deg // 2) % 2 == 0 else (42, 45, 52)
        draw.line([(x_in, y_in), (x_out, y_out)], fill=color, width=2)

    # Inner Bezel Chamfer & Minute Ring
    draw.ellipse((CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS), fill=(22, 25, 30, 255), outline=(125, 134, 148), width=4)
    draw.ellipse((CX - RADIUS + 10, CY - RADIUS + 10, CX + RADIUS - 10, CY + RADIUS - 10), outline=(35, 40, 48), width=3)

    # Outer 60-minute tick track around dial rim
    rim_r = RADIUS - 6
    for deg in range(0, 360, 6):
        rad = math.radians(deg)
        tick_len = 10 if deg % 30 == 0 else 5
        x1 = CX + (rim_r - tick_len) * math.cos(rad)
        y1 = CY + (rim_r - tick_len) * math.sin(rad)
        x2 = CX + rim_r * math.cos(rad)
        y2 = CY + rim_r * math.sin(rad)
        col = (230, 235, 245) if deg % 30 == 0 else (110, 120, 135)
        draw.line([(x1, y1), (x2, y2)], fill=col, width=2 if deg % 30 == 0 else 1)

    # 3. Skeleton Movement Ruthenium Plate & Circular Dial Mask
    inner_r = RADIUS - 18
    # Create a separate layer for the dial plate so stripes are clipped cleanly inside the circle
    dial_plate = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dp_draw = ImageDraw.Draw(dial_plate)
    dp_draw.ellipse((CX - inner_r, CY - inner_r, CX + inner_r, CY + inner_r), fill=(26, 30, 38, 255))

    # Côtes de Genève (Geneva Stripes) strictly inside the circular plate
    for stripe_y in range(CY - inner_r, CY + inner_r, 18):
        shade = int(32 + 5 * math.sin(stripe_y * 0.1))
        dp_draw.line([(CX - inner_r, stripe_y), (CX + inner_r, stripe_y)], fill=(shade, shade + 3, shade + 7, 120), width=9)

    # Circular mask to ensure zero bleed outside the bezel
    dial_mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(dial_mask).ellipse((CX - inner_r, CY - inner_r, CX + inner_r, CY + inner_r), fill=255)
    img.paste(dial_plate, (0, 0), dial_mask)

    # Circular skeleton balance wheel & gear cutout assemblies
    # A. Central skeleton balance wheel assembly (where top arch used to be!)
    wheel_cx, wheel_cy = CX, CY - 90
    draw.ellipse((wheel_cx - 75, wheel_cy - 75, wheel_cx + 75, wheel_cy + 75), fill=(18, 20, 26), outline=(52, 58, 70), width=4)
    draw.ellipse((wheel_cx - 65, wheel_cy - 65, wheel_cx + 65, wheel_cy + 65), outline=(78, 88, 104), width=3)
    # 4 Titanium wheel spokes
    for a in (0, 90, 180, 270):
        rad = math.radians(a + 45)
        sx = wheel_cx + 60 * math.cos(rad)
        sy = wheel_cy + 60 * math.sin(rad)
        draw.line([(wheel_cx, wheel_cy), (sx, sy)], fill=(60, 68, 80), width=6)
        draw.line([(wheel_cx, wheel_cy), (sx, sy)], fill=(95, 105, 122), width=2)
    # Ruby pivot bearing in center of wheel
    draw.ellipse((wheel_cx - 16, wheel_cy - 16, wheel_cx + 16, wheel_cy + 16), fill=(65, 72, 85), outline=(120, 130, 148), width=2)
    draw.ellipse((wheel_cx - 10, wheel_cy - 10, wheel_cx + 10, wheel_cy + 10), fill=(210, 25, 80), outline=(255, 80, 135), width=1)
    draw.ellipse((wheel_cx - 4, wheel_cy - 4, wheel_cx + 4, wheel_cy + 4), fill=(255, 140, 180))

    # B. Lower movement bridge assembly (where bottom pipe used to be!)
    bot_bridge_cy = CY + 175
    draw.ellipse((CX - 90, bot_bridge_cy - 50, CX + 90, bot_bridge_cy + 50), fill=(20, 23, 29), outline=(55, 62, 75), width=4)
    draw.ellipse((CX - 75, bot_bridge_cy - 35, CX + 75, bot_bridge_cy + 35), outline=(82, 92, 110), width=2)
    # Lower ruby jewel
    draw.ellipse((CX - 12, bot_bridge_cy - 12, CX + 12, bot_bridge_cy + 12), fill=(65, 72, 85), outline=(120, 130, 148), width=2)
    draw.ellipse((CX - 7, bot_bridge_cy - 7, CX + 7, bot_bridge_cy + 7), fill=(210, 25, 80), outline=(255, 80, 135), width=1)

    # C. Lateral balance wheel jewels & heat-blued steel screws
    for jx, jy in [(CX - 225, CY), (CX + 225, CY), (CX - 120, CY + 100), (CX + 120, CY + 100)]:
        draw.ellipse((jx - 10, jy - 10, jx + 10, jy + 10), fill=(55, 62, 74), outline=(110, 120, 135), width=1)
        draw.ellipse((jx - 6, jy - 6, jx + 6, jy + 6), fill=(210, 30, 85), outline=(255, 90, 145), width=1)
    # Blued steel screws
    for sx, sy in [(CX - 210, CY - 120), (CX + 210, CY - 120), (CX - 210, CY + 120), (CX + 210, CY + 120), (CX, CY - 195)]:
        draw.ellipse((sx - 6, sy - 6, sx + 6, sy + 6), fill=(22, 75, 185), outline=(60, 135, 245), width=2)
        draw.line([(sx - 4, sy), (sx + 4, sy)], fill=(12, 35, 85), width=2)

    # 4. Brand Plaque: "FLUIDA" at 12 o'clock
    plaque_w, plaque_h = 190, 44
    py = CY - RADIUS + 48
    draw.rounded_rectangle((CX - plaque_w // 2, py, CX + plaque_w // 2, py + plaque_h), radius=9, fill=(50, 56, 68), outline=(110, 120, 138), width=2)
    for px_s in (CX - plaque_w // 2 + 14, CX + plaque_w // 2 - 14):
        draw.ellipse((px_s - 5, py + plaque_h // 2 - 5, px_s + 5, py + plaque_h // 2 + 5), fill=(160, 170, 185), outline=(65, 72, 85), width=1)
        draw.line([(px_s - 3, py + plaque_h // 2), (px_s + 3, py + plaque_h // 2)], fill=(35, 40, 50), width=1)
    font_brand = get_font(22, bold=True)
    draw.text((CX, py + plaque_h // 2), "F L U I D A", fill=(245, 248, 252), font=font_brand, anchor="mm")

    # 5. Complications at 3 and 4 o'clock
    font_comp = get_font(18, bold=True)
    # Date window at 3 o'clock
    dx, dy = CX + 235, CY - 45
    draw.rounded_rectangle((dx - 32, dy - 20, dx + 32, dy + 20), radius=6, fill=(16, 18, 24), outline=(80, 90, 106), width=2)
    draw.text((dx, dy), "14", fill=(245, 248, 252), font=font_comp, anchor="mm")

    # Battery indicator at 4 o'clock
    bx, by = CX + 235, CY + 45
    draw.rounded_rectangle((bx - 36, by - 20, bx + 36, by + 20), radius=6, fill=(16, 18, 24), outline=(80, 90, 106), width=2)
    draw.text((bx, by), "82%", fill=(175, 245, 205), font=font_comp, anchor="mm")

    # 6. Independent Titanium Caps and Reservoir Manifolds for each Tube:
    # LEFT TUBE (Hours):
    # Top Cap (Closed, independent!)
    draw.rounded_rectangle((H_X1 - 4, TUBE_Y1 - 16, H_X2 + 4, TUBE_Y1 + 6), radius=6, fill=(62, 70, 84), outline=(135, 148, 168), width=2)
    draw.ellipse((H_CX - 6, TUBE_Y1 - 10, H_CX + 6, TUBE_Y1 + 2), fill=(175, 185, 200), outline=(60, 68, 80), width=1)
    # Bottom Manifold (Closed reservoir base!)
    draw.rounded_rectangle((H_X1 - 6, TUBE_Y2 - 4, H_X2 + 6, TUBE_Y2 + 28), radius=7, fill=(54, 62, 75), outline=(125, 136, 155), width=2)
    draw.ellipse((H_CX - 18, TUBE_Y2 + 4, H_CX + 18, TUBE_Y2 + 22), fill=(15, 60, 175), outline=(65, 130, 245), width=2)

    # RIGHT TUBE (Minutes):
    # Top Cap (Closed, independent!)
    draw.rounded_rectangle((M_X1 - 4, TUBE_Y1 - 16, M_X2 + 4, TUBE_Y1 + 6), radius=6, fill=(62, 70, 84), outline=(135, 148, 168), width=2)
    draw.ellipse((M_CX - 6, TUBE_Y1 - 10, M_CX + 6, TUBE_Y1 + 2), fill=(175, 185, 200), outline=(60, 68, 80), width=1)
    # Bottom Manifold (Closed reservoir base!)
    draw.rounded_rectangle((M_X1 - 6, TUBE_Y2 - 4, M_X2 + 6, TUBE_Y2 + 28), radius=7, fill=(54, 62, 75), outline=(125, 136, 155), width=2)
    draw.ellipse((M_CX - 18, TUBE_Y2 + 4, M_CX + 18, TUBE_Y2 + 22), fill=(0, 145, 140), outline=(0, 230, 220), width=2)

    # Heavy titanium clamping brackets
    for y_br in (TUBE_Y1 + 65, TUBE_Y2 - 65):
        # Left bracket
        draw.rounded_rectangle((H_X1 - 12, y_br - 8, H_X2 + 12, y_br + 8), radius=4, fill=(68, 76, 90), outline=(140, 152, 172), width=2)
        draw.ellipse((H_X1 - 8, y_br - 4, H_X1 - 2, y_br + 4), fill=(185, 195, 210))
        draw.ellipse((H_X2 + 2, y_br - 4, H_X2 + 8, y_br + 4), fill=(185, 195, 210))
        # Right bracket
        draw.rounded_rectangle((M_X1 - 12, y_br - 8, M_X2 + 12, y_br + 8), radius=4, fill=(68, 76, 90), outline=(140, 152, 172), width=2)
        draw.ellipse((M_X1 - 8, y_br - 4, M_X1 - 2, y_br + 4), fill=(185, 195, 210))
        draw.ellipse((M_X2 + 2, y_br - 4, M_X2 + 8, y_br + 4), fill=(185, 195, 210))

    return img


def render_swiss_scales() -> Image.Image:
    """Render razor-sharp Swiss typography calibration markings."""
    scales = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scales)

    font_major = get_font(16, bold=True)
    font_minor = get_font(13, bold=False)

    usable_y1 = TUBE_Y1 + 18
    usable_y2 = TUBE_Y2 - 18
    span = usable_y2 - usable_y1

    # LEFT TUBE: Hours 1 to 12
    for h in range(1, 13):
        frac = (h - 1) / 11.0
        y = usable_y2 - int(frac * span)
        # Major tick baton
        draw.line([(H_X1 + 7, y), (H_X1 + 24, y)], fill=(255, 255, 255, 255), width=2)
        # Hour Numeral
        draw.text((H_X1 + 30, y), str(h), fill=(255, 255, 255, 255), font=font_major, anchor="lm")
        # Half-hour tick
        if h < 12:
            y_sub = y - int(0.5 / 11.0 * span)
            draw.line([(H_X1 + 7, y_sub), (H_X1 + 16, y_sub)], fill=(210, 225, 245, 190), width=1)

    # RIGHT TUBE: Minutes 00 to 60
    for m in (0, 10, 20, 30, 40, 50, 60):
        frac = m / 60.0
        y = usable_y2 - int(frac * span)
        # Major tick baton
        draw.line([(M_X2 - 24, y), (M_X2 - 7, y)], fill=(255, 255, 255, 255), width=2)
        # Minute Numeral
        draw.text((M_X2 - 30, y), f"{m:02d}", fill=(255, 255, 255, 255), font=font_major, anchor="rm")
        # 5-minute subtick
        if m < 60:
            y_5 = y - int(5.0 / 60.0 * span)
            draw.line([(M_X2 - 18, y_5), (M_X2 - 7, y_5)], fill=(195, 255, 250, 190), width=1)
            # 1-minute fine subticks
            for sub_m in (1, 2, 3, 4, 6, 7, 8, 9):
                y_1 = y - int(sub_m / 60.0 * span)
                draw.line([(M_X2 - 12, y_1), (M_X2 - 7, y_1)], fill=(160, 235, 230, 130), width=1)

    return scales


def render_borosilicate_glass() -> Image.Image:
    """Render 3D cylindrical glass reflections and tube walls."""
    glass = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glass)

    for x1, x2 in [(H_X1, H_X2), (M_X1, M_X2)]:
        # Dark outer wall bevel
        draw.line([(x1, TUBE_Y1), (x1, TUBE_Y2)], fill=(40, 45, 55, 210), width=3)
        draw.line([(x2, TUBE_Y1), (x2, TUBE_Y2)], fill=(40, 45, 55, 210), width=3)

        # Specular glint on left glass wall
        draw.line([(x1 + 3, TUBE_Y1), (x1 + 3, TUBE_Y2)], fill=(255, 255, 255, 200), width=2)
        draw.line([(x1 + 6, TUBE_Y1), (x1 + 6, TUBE_Y2)], fill=(210, 235, 255, 80), width=2)

        # Specular glint on right glass wall
        draw.line([(x2 - 3, TUBE_Y1), (x2 - 3, TUBE_Y2)], fill=(255, 255, 255, 190), width=2)
        draw.line([(x2 - 6, TUBE_Y1), (x2 - 6, TUBE_Y2)], fill=(210, 235, 255, 70), width=2)

    return glass


def build_fluid_column(
    x1: int,
    x2: int,
    y_top: int,
    y_bot: int,
    fill_frac: float,
    deep_col: tuple[int, int, int],
    core_col: tuple[int, int, int],
    meniscus_col: tuple[int, int, int],
    bubbles: list[float] = None,
) -> Image.Image:
    """Render authentic cylindrical liquid column with volumetric glow & curved meniscus."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    usable_y1 = y_top + 18
    usable_y2 = y_bot - 18
    span = usable_y2 - usable_y1

    fluid_y = usable_y2 - int(fill_frac * span)
    fluid_y = max(usable_y1, min(usable_y2, fluid_y))

    ix1, ix2 = x1 + 5, x2 - 5
    iw = ix2 - ix1

    # Cylindrical fluid shading
    for x in range(ix1, ix2 + 1):
        norm_x = (x - (ix1 + iw / 2.0)) / (iw / 2.0)
        falloff = max(0.0, 1.0 - norm_x * norm_x)
        r = int(deep_col[0] * (1 - falloff) + core_col[0] * falloff)
        g = int(deep_col[1] * (1 - falloff) + core_col[1] * falloff)
        b = int(deep_col[2] * (1 - falloff) + core_col[2] * falloff)
        draw.line([(x, fluid_y), (x, y_bot)], fill=(r, g, b, 245))

    # Glowing Curved Liquid Meniscus
    draw.ellipse((ix1, fluid_y - 4, ix2, fluid_y + 8), fill=(*meniscus_col, 245))
    draw.ellipse((ix1 + 6, fluid_y - 2, ix2 - 6, fluid_y + 4), fill=(255, 255, 255, 255))

    # Rising micro-bubbles (1-Hz seconds)
    if bubbles and fluid_y < usable_y2 - 10:
        for b_frac in bubbles:
            by = usable_y2 - int(b_frac * (usable_y2 - fluid_y))
            if fluid_y + 6 < by < usable_y2 - 6:
                bx = ix1 + iw // 2 + int(5 * math.sin(by * 0.15))
                draw.ellipse((bx - 5, by - 5, bx + 5, by + 5), fill=(*meniscus_col, 160), outline=(255, 255, 255, 235), width=1)
                draw.ellipse((bx - 2, by - 3, bx, by - 1), fill=(255, 255, 255, 255))

    return layer


def generate_animation() -> None:
    print("Generating base luxury dial assets...")
    dial_base = render_luxury_dial_base()
    scales_overlay = render_swiss_scales()
    glass_overlay = render_borosilicate_glass()

    BLUE_DEEP = (12, 60, 215)
    BLUE_CORE = (32, 145, 255)
    BLUE_MENISCUS = (180, 230, 255)

    CYAN_DEEP = (0, 160, 185)
    CYAN_CORE = (15, 235, 220)
    CYAN_MENISCUS = (185, 255, 245)

    # 36-frame smooth timeline:
    # Phase 1: Minutes rising 00 -> 60 (16 smooth frames)
    # Phase 2: Sucked-Down / Vacuum Siphon Drain! Fluid is sucked backward into bottom reservoir (12 frames)
    #          Simultaneously: Hour steps smoothly from 10 to 11!
    # Phase 3: Settle at 11:00 (8 frames)
    timeline = []

    # Phase 1: Minutes rising smoothly from 0 to 60
    rise_m = [0.0, 4.0, 8.0, 14.0, 20.0, 26.0, 32.0, 38.0, 44.0, 50.0, 54.0, 57.0, 58.5, 59.2, 59.8, 60.0]
    for i, m in enumerate(rise_m):
        m_frac = m / 60.0
        h_frac = (10.0 + (m / 60.0) * 0.05) / 12.0
        b1 = (i * 0.18) % 1.0
        b2 = ((i + 5) * 0.18) % 1.0
        timeline.append((m_frac, h_frac, [b1, b2]))

    # Phase 2: Sucked-down drain! (Smooth non-linear backward vacuum drain)
    drain_m = [54.0, 45.0, 34.0, 24.0, 15.0, 8.0, 4.0, 1.5, 0.5, 0.0, 0.0, 0.0]
    drain_h = [10.08, 10.18, 10.35, 10.55, 10.75, 10.90, 10.97, 11.00, 11.00, 11.00, 11.00, 11.00]
    for d_m, d_h in zip(drain_m, drain_h):
        timeline.append((d_m / 60.0, d_h / 12.0, []))

    # Phase 3: Settle at 11:00
    for i in range(8):
        m = i * 0.3
        b1 = (i * 0.22) % 1.0
        timeline.append((m / 60.0, 11.0 / 12.0, [b1]))

    frames = []
    print(f"Compositing {len(timeline)} frames...")

    for m_frac, h_frac, bubbles in timeline:
        frame = dial_base.copy()

        # 1. Left Hour Fluid Column
        h_fluid = build_fluid_column(
            x1=H_X1,
            x2=H_X2,
            y_top=TUBE_Y1,
            y_bot=TUBE_Y2,
            fill_frac=h_frac,
            deep_col=BLUE_DEEP,
            core_col=BLUE_CORE,
            meniscus_col=BLUE_MENISCUS,
            bubbles=None,
        )
        frame.alpha_composite(h_fluid)

        # 2. Right Minute Fluid Column
        m_fluid = build_fluid_column(
            x1=M_X1,
            x2=M_X2,
            y_top=TUBE_Y1,
            y_bot=TUBE_Y2,
            fill_frac=m_frac,
            deep_col=CYAN_DEEP,
            core_col=CYAN_CORE,
            meniscus_col=CYAN_MENISCUS,
            bubbles=bubbles,
        )
        frame.alpha_composite(m_fluid)

        # 3. Static Swiss Scales Overlay (1..12 and 00..60)
        frame.alpha_composite(scales_overlay)

        # 4. Glass reflections and highlights
        frame.alpha_composite(glass_overlay)

        # Downsample cleanly to 650x650 for buttery-smooth playback
        resized = frame.resize((650, 650), Image.Resampling.LANCZOS)
        frames.append(resized.convert("RGB"))

        # Save the clean static watch image at 10:10
        if len(frames) == 3:  # at 10:10
            frame.convert("RGB").save(MOCKUPS / "fluida_watch_face_clean.jpg", quality=95)

    out_gif = MOCKUPS / "animated_fluida_smooth_vacuum_drain.gif"
    frames[0].save(
        out_gif,
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
    )
    print(f"Luxury animation completed: {out_gif}")


if __name__ == "__main__":
    generate_animation()
