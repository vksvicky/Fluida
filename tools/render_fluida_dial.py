"""Procedural, mathematically defined renderer for FLUIDA Watch Face.
- Completely independent Hour and Minute tubes (NO top connecting arc, NO bottom cross-pipe)
- Distinct fluid circuits: Cobalt Blue for Hours (1-12), Cyan/Aquamarine for Minutes (00-60)
- Authentic Swiss typography (Avenir) with proper calibrations:
    Left: 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
    Right: 60, 50, 40, 30, 20, 10, 00 with 5-min subticks
- Independent top titanium caps and bottom reservoir manifolds
- Buttery-smooth animation showing minutes advancing from 00 to 60, then being sucked down/draining back into the bottom reservoir, while the hour steps smoothly from 10 to 11.
"""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MOCKUPS = Path("/Users/vivek/Development/Fluida/mockups")
MOCKUPS.mkdir(parents=True, exist_ok=True)

SIZE = 800
CX, CY = SIZE // 2, SIZE // 2
RADIUS = 350

# Fonts
FONT_PATH = "/System/Library/Fonts/Avenir.ttc"


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    index = 8 if bold else 0  # 8 is Avenir Heavy/Medium in TTC
    try:
        return ImageFont.truetype(FONT_PATH, size, index=index)
    except Exception:
        return ImageFont.truetype(FONT_PATH, size)


# Tube positions (Completely separate!)
TUBE_W = 68
TUBE_H = 340
TUBE_Y1 = CY - 170
TUBE_Y2 = TUBE_Y1 + TUBE_H

H_X1 = CX - 134
H_X2 = H_X1 + TUBE_W
H_CX = (H_X1 + H_X2) // 2

M_X1 = CX + 66
M_X2 = M_X1 + TUBE_W
M_CX = (M_X1 + M_X2) // 2


def render_dial_base() -> Image.Image:
    """Render the master static watch face backdrop at 800x800."""
    img = Image.new("RGBA", (SIZE, SIZE), (10, 12, 14, 255))
    draw = ImageDraw.Draw(img)

    # 1. Outer Dark Slate / Slate Stone Background
    for y in range(SIZE):
        v = int(14 + 6 * math.sin(y * 0.04) + 4 * math.cos(y * 0.08))
        draw.line([(0, y), (SIZE, y)], fill=(v, v + 2, v + 4, 255))

    # 2. Titanium Case with Chamfer & Lugs
    # Lugs top and bottom
    lug_w = 80
    draw.polygon([(CX - 190, 40), (CX - 190 + lug_w, 40), (CX - 190 + lug_w + 30, 160), (CX - 190 - 20, 160)], fill=(48, 52, 60))
    draw.polygon([(CX + 190, 40), (CX + 190 - lug_w, 40), (CX + 190 - lug_w - 30, 160), (CX + 190 + 20, 160)], fill=(48, 52, 60))
    draw.polygon([(CX - 190, SIZE - 40), (CX - 190 + lug_w, SIZE - 40), (CX - 190 + lug_w + 30, SIZE - 160), (CX - 190 - 20, SIZE - 160)], fill=(48, 52, 60))
    draw.polygon([(CX + 190, SIZE - 40), (CX + 190 - lug_w, SIZE - 40), (CX + 190 - lug_w - 30, SIZE - 160), (CX + 190 + 20, SIZE - 160)], fill=(48, 52, 60))

    # Circular Case body
    for r in range(RADIUS + 40, RADIUS + 15, -1):
        ratio = (r - RADIUS - 15) / 25.0
        c = int(42 + 25 * ratio)
        draw.ellipse((CX - r, CY - r, CX + r, CY + r), outline=(c, c + 3, c + 7, 255), width=2)

    # Knurled Titanium Bezel Ring
    bezel_r = RADIUS + 15
    for a in range(0, 360, 3):
        rad = math.radians(a)
        kx = CX + bezel_r * math.cos(rad)
        ky = CY + bezel_r * math.sin(rad)
        col = (90, 96, 105) if (a // 3) % 2 == 0 else (45, 48, 54)
        draw.line([(CX + (bezel_r - 12) * math.cos(rad), CY + (bezel_r - 12) * math.sin(rad)), (kx, ky)], fill=col, width=2)

    # Inner Bezel Chamfer Ring
    draw.ellipse((CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS), fill=(20, 23, 28, 255), outline=(110, 118, 130), width=4)
    draw.ellipse((CX - RADIUS + 8, CY - RADIUS + 8, CX + RADIUS - 8, CY + RADIUS - 8), outline=(32, 36, 44), width=3)

    # 3. Skeleton Movement Backplate
    # Ruthenium plates with circular cutouts
    inner_r = RADIUS - 15
    draw.ellipse((CX - inner_r, CY - inner_r, CX + inner_r, CY + inner_r), fill=(24, 27, 34, 255))

    # Gears and skeleton bridge architecture
    gear_color = (48, 54, 66)
    gear_teeth = (65, 72, 85)
    # Left balance wheel assembly
    draw.ellipse((CX - 190, CY - 70, CX - 70, CY + 50), fill=(20, 22, 28), outline=gear_color, width=4)
    draw.ellipse((CX - 170, CY - 50, CX - 90, CY + 30), outline=gear_teeth, width=2)
    # Center gear train
    draw.ellipse((CX - 60, CY - 60, CX + 60, CY + 60), fill=(22, 25, 32), outline=gear_color, width=4)
    draw.ellipse((CX - 40, CY - 40, CX + 40, CY + 40), outline=gear_teeth, width=2)
    # Right gear cluster
    draw.ellipse((CX + 70, CY - 70, CX + 190, CY + 50), fill=(20, 22, 28), outline=gear_color, width=4)
    draw.ellipse((CX + 90, CY - 50, CX + 170, CY + 30), outline=gear_teeth, width=2)

    # Ruby pivot jewels
    for jx, jy in [(CX - 130, CY - 10), (CX, CY), (CX + 130, CY - 10), (CX, CY + 140)]:
        draw.ellipse((jx - 8, jy - 8, jx + 8, jy + 8), fill=(60, 65, 75), outline=(100, 110, 125), width=1)
        draw.ellipse((jx - 5, jy - 5, jx + 5, jy + 5), fill=(210, 30, 80), outline=(255, 90, 140), width=1)

    # Movement bridge screws (heat-blued steel screws)
    for sx, sy in [(CX - 170, CY - 120), (CX + 170, CY - 120), (CX - 170, CY + 130), (CX + 170, CY + 130), (CX, CY - 120)]:
        draw.ellipse((sx - 5, sy - 5, sx + 5, sy + 5), fill=(25, 80, 190), outline=(50, 130, 240), width=1)
        draw.line([(sx - 3, sy), (sx + 3, sy)], fill=(15, 35, 75), width=1)

    # 4. Brand Plaque: "FLUIDA" at 12 o'clock
    plaque_w, plaque_h = 170, 38
    py = CY - RADIUS + 45
    draw.rounded_rectangle((CX - plaque_w // 2, py, CX + plaque_w // 2, py + plaque_h), radius=8, fill=(45, 50, 60), outline=(95, 105, 120), width=2)
    # Screws on plaque
    for px_s in (CX - plaque_w // 2 + 12, CX + plaque_w // 2 - 12):
        draw.ellipse((px_s - 4, py + plaque_h // 2 - 4, px_s + 4, py + plaque_h // 2 + 4), fill=(140, 150, 165), outline=(60, 65, 75), width=1)
        draw.line([(px_s - 2, py + plaque_h // 2), (px_s + 2, py + plaque_h // 2)], fill=(30, 35, 45), width=1)
    font_brand = get_font(20, bold=True)
    draw.text((CX, py + plaque_h // 2), "F L U I D A", fill=(245, 248, 252), font=font_brand, anchor="mm")

    # 5. Complications at 3 and 4 o'clock
    font_comp = get_font(16, bold=True)
    # Date window at 3 o'clock
    dx, dy = CX + 195, CY - 40
    draw.rounded_rectangle((dx - 28, dy - 18, dx + 28, dy + 18), radius=5, fill=(16, 18, 22), outline=(70, 78, 92), width=2)
    draw.text((dx, dy), "14", fill=(245, 248, 252), font=font_comp, anchor="mm")

    # Battery indicator at 4 o'clock
    bx, by = CX + 195, CY + 40
    draw.rounded_rectangle((bx - 32, by - 18, bx + 32, by + 18), radius=5, fill=(16, 18, 22), outline=(70, 78, 92), width=2)
    draw.text((bx, by), "82%", fill=(180, 240, 200), font=font_comp, anchor="mm")

    # 6. Independent Titanium Caps and Reservoir Manifolds for the Two Tubes
    # Left Tube (Hours):
    # Top Cap (Closed, independent!)
    draw.rounded_rectangle((H_X1 - 8, TUBE_Y1 - 22, H_X2 + 8, TUBE_Y1 + 4), radius=6, fill=(55, 62, 74), outline=(110, 120, 138), width=2)
    # Hex bolt on top cap
    draw.ellipse((H_CX - 5, TUBE_Y1 - 14, H_CX + 5, TUBE_Y1 - 4), fill=(150, 160, 175), outline=(50, 55, 65), width=1)
    # Bottom Reservoir Manifold (Closed, independent!)
    draw.rounded_rectangle((H_X1 - 10, TUBE_Y2 - 4, H_X2 + 10, TUBE_Y2 + 28), radius=7, fill=(48, 54, 65), outline=(105, 115, 132), width=2)
    # Pressure valve indicator
    draw.ellipse((H_CX - 6, TUBE_Y2 + 7, H_CX + 6, TUBE_Y2 + 19), fill=(25, 75, 160), outline=(90, 140, 230), width=1)

    # Right Tube (Minutes):
    # Top Cap (Closed, independent!)
    draw.rounded_rectangle((M_X1 - 8, TUBE_Y1 - 22, M_X2 + 8, TUBE_Y1 + 4), radius=6, fill=(55, 62, 74), outline=(110, 120, 138), width=2)
    draw.ellipse((M_CX - 5, TUBE_Y1 - 14, M_CX + 5, TUBE_Y1 - 4), fill=(150, 160, 175), outline=(50, 55, 65), width=1)
    # Bottom Reservoir Manifold (Closed, independent!)
    draw.rounded_rectangle((M_X1 - 10, TUBE_Y2 - 4, M_X2 + 10, TUBE_Y2 + 28), radius=7, fill=(48, 54, 65), outline=(105, 115, 132), width=2)
    draw.ellipse((M_CX - 6, TUBE_Y2 + 7, M_CX + 6, TUBE_Y2 + 19), fill=(0, 140, 135), outline=(0, 220, 210), width=1)

    # Mid-cylinder titanium clamping brackets
    for y_br in (TUBE_Y1 + 55, TUBE_Y2 - 55):
        # Left bracket
        draw.rounded_rectangle((H_X1 - 12, y_br - 7, H_X2 + 12, y_br + 7), radius=4, fill=(58, 65, 78), outline=(115, 125, 142), width=2)
        draw.ellipse((H_X1 - 8, y_br - 3, H_X1 - 2, y_br + 3), fill=(160, 170, 185))
        draw.ellipse((H_X2 + 2, y_br - 3, H_X2 + 8, y_br + 3), fill=(160, 170, 185))
        # Right bracket
        draw.rounded_rectangle((M_X1 - 12, y_br - 7, M_X2 + 12, y_br + 7), radius=4, fill=(58, 65, 78), outline=(115, 125, 142), width=2)
        draw.ellipse((M_X1 - 8, y_br - 3, M_X1 - 2, y_br + 3), fill=(160, 170, 185))
        draw.ellipse((M_X2 + 2, y_br - 3, M_X2 + 8, y_br + 3), fill=(160, 170, 185))

    return img


def render_scales() -> Image.Image:
    """Render the razor-sharp Swiss calibration markings and numerals."""
    scale_img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scale_img)

    font_scale = get_font(15, bold=True)
    font_sub = get_font(12, bold=False)

    usable_y_top = TUBE_Y1 + 12
    usable_y_bot = TUBE_Y2 - 12
    span = usable_y_bot - usable_y_top

    # LEFT TUBE: Hours 1 to 12
    # 12 at the top, 1 at the bottom
    for h in range(1, 13):
        frac = (h - 1) / 11.0
        y = usable_y_bot - int(frac * span)
        # Major tick mark
        draw.line([(H_X1 + 6, y), (H_X1 + 22, y)], fill=(255, 255, 255, 240), width=2)
        # Numeral
        draw.text((H_X1 + 28, y), str(h), fill=(255, 255, 255, 255), font=font_scale, anchor="lm")
        # Half-hour intermediate tick
        if h < 12:
            y_mid = y - int(0.5 / 11.0 * span)
            draw.line([(H_X1 + 6, y_mid), (H_X1 + 15, y_mid)], fill=(200, 215, 235, 180), width=1)

    # RIGHT TUBE: Minutes 00 to 60
    # 60 at top, 00 at bottom
    for m in (0, 10, 20, 30, 40, 50, 60):
        frac = m / 60.0
        y = usable_y_bot - int(frac * span)
        # Major tick mark
        draw.line([(M_X2 - 22, y), (M_X2 - 6, y)], fill=(255, 255, 255, 240), width=2)
        # Numeral
        draw.text((M_X2 - 28, y), f"{m:02d}", fill=(255, 255, 255, 255), font=font_scale, anchor="rm")
        # 5-minute intermediate tick
        if m < 60:
            y_mid = y - int(5.0 / 60.0 * span)
            draw.line([(M_X2 - 16, y_mid), (M_X2 - 6, y_mid)], fill=(180, 245, 240, 190), width=1)
            # 1-minute fine tick marks
            for sub_m in (1, 2, 3, 4, 6, 7, 8, 9):
                y_sub = y - int(sub_m / 60.0 * span)
                draw.line([(M_X2 - 11, y_sub), (M_X2 - 6, y_sub)], fill=(150, 220, 215, 140), width=1)

    return scale_img


def render_glass_tubes() -> Image.Image:
    """Render the 3D borosilicate glass tube walls, bevels, and specular highlights."""
    glass = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glass)

    for x1, x2 in [(H_X1, H_X2), (M_X1, M_X2)]:
        # Glass tube outer bevels
        draw.line([(x1, TUBE_Y1), (x1, TUBE_Y2)], fill=(40, 45, 55, 200), width=3)
        draw.line([(x2, TUBE_Y1), (x2, TUBE_Y2)], fill=(40, 45, 55, 200), width=3)

        # Specular glint on left glass edge
        draw.line([(x1 + 3, TUBE_Y1), (x1 + 3, TUBE_Y2)], fill=(255, 255, 255, 190), width=2)
        # Softer internal reflection
        draw.line([(x1 + 6, TUBE_Y1), (x1 + 6, TUBE_Y2)], fill=(210, 230, 255, 80), width=2)

        # Specular glint on right glass edge
        draw.line([(x2 - 3, TUBE_Y1), (x2 - 3, TUBE_Y2)], fill=(255, 255, 255, 170), width=2)
        draw.line([(x2 - 6, TUBE_Y1), (x2 - 6, TUBE_Y2)], fill=(210, 230, 255, 70), width=2)

    return glass


def build_fluid_column(
    x1: int,
    x2: int,
    y_top: int,
    y_bot: int,
    fill_frac: float,
    deep_color: tuple[int, int, int],
    core_color: tuple[int, int, int],
    meniscus_color: tuple[int, int, int],
    bubble_offsets: list[float] = None,
) -> Image.Image:
    """Render a physically modeled cylindrical liquid column with volumetric glow & meniscus."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    usable_y_top = y_top + 12
    usable_y_bot = y_bot - 12
    span = usable_y_bot - usable_y_top

    fluid_y = usable_y_bot - int(fill_frac * span)
    fluid_y = max(usable_y_top, min(usable_y_bot, fluid_y))

    # Fluid column interior: X from x1 + 5 to x2 - 5
    ix1, ix2 = x1 + 5, x2 - 5
    iw = ix2 - ix1

    # Cylindrical fluid shading
    for x in range(ix1, ix2 + 1):
        norm_x = (x - (ix1 + iw / 2.0)) / (iw / 2.0)
        falloff = max(0.0, 1.0 - norm_x * norm_x)
        r = int(deep_color[0] * (1 - falloff) + core_color[0] * falloff)
        g = int(deep_color[1] * (1 - falloff) + core_color[1] * falloff)
        b = int(deep_color[2] * (1 - falloff) + core_color[2] * falloff)
        draw.line([(x, fluid_y), (x, y_bot)], fill=(r, g, b, 240))

    # Glowing curved liquid meniscus at fluid_y
    draw.ellipse((ix1, fluid_y - 4, ix2, fluid_y + 8), fill=(*meniscus_color, 240))
    draw.ellipse((ix1 + 6, fluid_y - 2, ix2 - 6, fluid_y + 4), fill=(255, 255, 255, 255))

    # Rising micro-bubbles (1-Hz seconds)
    if bubble_offsets and fluid_y < usable_y_bot - 10:
        for b_frac in bubble_offsets:
            by = usable_y_bot - int(b_frac * (usable_y_bot - fluid_y))
            if fluid_y + 6 < by < usable_y_bot - 6:
                bx = ix1 + iw // 2 + int(5 * math.sin(by * 0.15))
                # Translucent bubble with specular white highlight
                draw.ellipse((bx - 4, by - 4, bx + 4, by + 4), fill=(*meniscus_color, 140), outline=(255, 255, 255, 230), width=1)
                draw.ellipse((bx - 2, by - 3, bx, by - 1), fill=(255, 255, 255, 255))

    return layer


def generate_fluida_smooth_animation() -> None:
    print("Rendering base dial components...")
    dial_base = render_dial_base()
    scales_overlay = render_scales()
    glass_overlay = render_glass_tubes()

    BLUE_DEEP = (10, 60, 210)
    BLUE_CORE = (30, 145, 255)
    BLUE_MENISCUS = (180, 230, 255)

    CYAN_DEEP = (0, 160, 185)
    CYAN_CORE = (15, 235, 220)
    CYAN_MENISCUS = (185, 255, 245)

    # 40-frame smooth animation timeline
    # 1. Minutes rising smoothly: 00 -> 10 -> 25 -> 40 -> 50 -> 55 -> 58 -> 60
    # 2. Reaches 60: Sucked down / vacuum siphon drain back to 00 in a rapid cascade!
    # 3. Simultaneously: Hour steps smoothly from 10 to 11!
    timeline = []

    # Phase 1: Rising from 0 to 60 (16 smooth frames)
    # Minute values: 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 54, 57, 58.5, 59.5, 60.0
    rise_minutes = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 54.0, 57.0, 58.5, 59.5, 60.0]
    for i, m in enumerate(rise_minutes):
        m_frac = m / 60.0
        h_frac = (10.0 + (m / 60.0) * 0.05) / 12.0  # slight continuous hour advance
        b1 = (i * 0.18) % 1.0
        b2 = ((i + 5) * 0.18) % 1.0
        timeline.append((m_frac, h_frac, [b1, b2], f"10:{int(m):02d}"))

    # Phase 2: Sucked-Down / Vacuum Flush! (10 fast smooth frames)
    # Minute sucked down: 52, 42, 30, 20, 12, 6, 2, 0.5, 0.0, 0.0
    # Hour advancing from 10.05 to 11.0: 10.1, 10.25, 10.45, 10.65, 10.82, 10.94, 10.99, 11.0, 11.0, 11.0
    flush_minutes = [52.0, 42.0, 30.0, 20.0, 12.0, 6.0, 2.0, 0.5, 0.0, 0.0]
    hour_steps = [10.10, 10.25, 10.45, 10.65, 10.82, 10.94, 10.99, 11.00, 11.00, 11.00]
    for m, h in zip(flush_minutes, hour_steps):
        timeline.append((m / 60.0, h / 12.0, [], f"{int(h):02d}:{int(m):02d} [SUCKED DOWN DRAIN]"))

    # Phase 3: Settle at 11:00 and start next cycle (6 frames)
    for i in range(6):
        m = i * 0.5
        b1 = (i * 0.2) % 1.0
        timeline.append((m / 60.0, 11.0 / 12.0, [b1], f"11:{int(m):02d}"))

    frames = []
    print(f"Generating {len(timeline)} high-precision frames...")

    for m_frac, h_frac, bubbles, label in timeline:
        frame = dial_base.copy()

        # 1. Left Hour Fluid Column
        h_fluid = build_fluid_column(
            x1=H_X1,
            x2=H_X2,
            y_top=TUBE_Y1,
            y_bot=TUBE_Y2,
            fill_frac=h_frac,
            deep_color=BLUE_DEEP,
            core_color=BLUE_CORE,
            meniscus_color=BLUE_MENISCUS,
            bubble_offsets=None,
        )
        frame.alpha_composite(h_fluid)

        # 2. Right Minute Fluid Column
        m_fluid = build_fluid_column(
            x1=M_X1,
            x2=M_X2,
            y_top=TUBE_Y1,
            y_bot=TUBE_Y2,
            fill_frac=m_frac,
            deep_color=CYAN_DEEP,
            core_color=CYAN_CORE,
            meniscus_color=CYAN_MENISCUS,
            bubble_offsets=bubbles,
        )
        frame.alpha_composite(m_fluid)

        # 3. Static Calibration Markings and Numerals (Crisp Swiss typography!)
        frame.alpha_composite(scales_overlay)

        # 4. Glass tube walls and specular highlights
        frame.alpha_composite(glass_overlay)

        # Downsample cleanly to 600x600 for buttery-smooth playback
        resized = frame.resize((600, 600), Image.Resampling.LANCZOS)
        frames.append(resized.convert("RGB"))

    out_gif = MOCKUPS / "animated_fluida_smooth_vacuum_flush.gif"
    frames[0].save(
        out_gif,
        save_all=True,
        append_images=frames[1:],
        duration=120,  # 120ms per frame = super smooth 8.3 FPS animation!
        loop=0,
    )
    print(f"Animation successfully created: {out_gif}")


if __name__ == "__main__":
    generate_fluida_smooth_animation()
