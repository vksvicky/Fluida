"""Generate 3 animated GIFs demonstrating the core water mechanics of FLUIDA:
1. gif_1_siphon_flush_reset.gif: Minute 59 -> 60 -> Siphon Flush -> 00 + Hour step 10 -> 11
2. gif_2_active_seconds_bubbles.gif: Rising micro-bubble aerator ticking each second
3. gif_3_am_pm_color_shift.gif: Day (Azure/Sun) to Night (Bioluminescent Violet/Moon) shift
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/vivek/Development/Fluida")
MOCKUPS = ROOT / "mockups"
MOCKUPS.mkdir(parents=True, exist_ok=True)

SIZE = 500
CX, CY = SIZE // 2, SIZE // 2
RADIUS = 210

# Color palettes
DARK_BG = (16, 18, 22)
TITANIUM_BEZEL = (65, 70, 78)
BEZEL_EDGE = (95, 102, 112)
SKELETON_PLATE = (28, 32, 40)
BRACKET_COLOR = (120, 128, 140)

# Tubes geometry
TUBE_W = 34
TUBE_H = 190
TUBE_R = 14
H_X = CX - 58
M_X = CX + 58
TUBE_TOP = CY - 75
TUBE_BOT = TUBE_TOP + TUBE_H


def draw_base_watch(draw: ImageDraw.ImageDraw, am_pm: str = "AM", sun_moon_angle: float = 0.0) -> None:
    # Outer bezel & case
    draw.ellipse((CX - RADIUS - 16, CY - RADIUS - 16, CX + RADIUS + 16, CY + RADIUS + 16), fill=(10, 11, 13))
    draw.ellipse((CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS), fill=DARK_BG, outline=TITANIUM_BEZEL, width=6)
    draw.ellipse((CX - RADIUS + 8, CY - RADIUS + 8, CX + RADIUS - 8, CY + RADIUS - 8), outline=(35, 38, 46), width=2)

    # Skeletonized backplate accents (gears & bridges)
    draw.ellipse((CX - 90, CY - 40, CX - 10, CY + 40), outline=(38, 44, 54), width=3)
    draw.ellipse((CX + 10, CY - 40, CX + 90, CY + 40), outline=(38, 44, 54), width=3)
    draw.ellipse((CX - 35, CY + 50, CX + 35, CY + 120), outline=(42, 48, 60), width=2)

    # Sun / Moon aperture at top center (under FLUIDA plaque)
    disc_cx, disc_cy = CX, TUBE_TOP - 42
    draw.ellipse((disc_cx - 24, disc_cy - 24, disc_cx + 24, disc_cy + 24), fill=(22, 26, 34), outline=(55, 62, 75), width=2)
    # Sun / Moon rotating disc
    sx = disc_cx + 12 * math.cos(math.radians(sun_moon_angle))
    sy = disc_cy + 12 * math.sin(math.radians(sun_moon_angle))
    if am_pm == "AM":
        # Golden Sun
        draw.ellipse((sx - 7, sy - 7, sx + 7, sy + 7), fill=(255, 205, 70), outline=(255, 235, 140), width=1)
    else:
        # Silver Moon
        draw.ellipse((sx - 7, sy - 7, sx + 7, sy + 7), fill=(210, 225, 245), outline=(255, 255, 255), width=1)
        draw.ellipse((sx - 4, sy - 7, sx + 7, sy + 7), fill=(22, 26, 34))

    # Top Brand Plaque
    draw.rectangle((CX - 48, TUBE_TOP - 66, CX + 48, TUBE_TOP - 50), fill=(45, 50, 60), outline=(75, 85, 100), width=1)
    draw.text((CX, TUBE_TOP - 59), "FLUIDA", fill=(240, 245, 250), anchor="mm")

    # Bottom siphon return pipe connecting both tubes
    draw.arc((CX - 58, TUBE_BOT - 10, CX + 58, TUBE_BOT + 45), start=0, end=180, fill=(65, 75, 92), width=6)
    draw.arc((CX - 58, TUBE_BOT - 10, CX + 58, TUBE_BOT + 45), start=0, end=180, fill=(90, 110, 135), width=2)


def draw_tubes(
    draw: ImageDraw.ImageDraw,
    hour_val: float,
    minute_val: float,
    blue_color: tuple[int, int, int],
    cyan_color: tuple[int, int, int],
    flush_siphon_active: bool = False,
    bubbles: list[tuple[float, float]] = None,
) -> None:
    # 1. Top Arch Glass Siphon
    arch_color = (65, 75, 92)
    arch_glow = (90, 115, 145)
    if flush_siphon_active:
        arch_glow = cyan_color
    draw.arc((H_X, TUBE_TOP - 46, M_X, TUBE_TOP + 10), start=180, end=360, fill=arch_color, width=8)
    draw.arc((H_X, TUBE_TOP - 46, M_X, TUBE_TOP + 10), start=180, end=360, fill=arch_glow, width=4)

    # 2. Left Tube: Hour
    # Outer borosilicate tube
    draw.rounded_rectangle((H_X - TUBE_W // 2, TUBE_TOP, H_X + TUBE_W // 2, TUBE_BOT), radius=TUBE_R, fill=(18, 22, 30), outline=(70, 80, 98), width=2)
    # Fluid
    h_fill_frac = max(0.05, min(1.0, hour_val / 12.0))
    h_level = TUBE_BOT - int((TUBE_H - 16) * h_fill_frac)
    draw.rounded_rectangle((H_X - TUBE_W // 2 + 3, h_level, H_X + TUBE_W // 2 - 3, TUBE_BOT - 3), radius=TUBE_R - 2, fill=blue_color)
    # Meniscus
    draw.ellipse((H_X - TUBE_W // 2 + 3, h_level - 4, H_X + TUBE_W // 2 - 3, h_level + 6), fill=(210, 235, 255))

    # 3. Right Tube: Minute
    draw.rounded_rectangle((M_X - TUBE_W // 2, TUBE_TOP, M_X + TUBE_W // 2, TUBE_BOT), radius=TUBE_R, fill=(18, 22, 30), outline=(70, 80, 98), width=2)
    m_fill_frac = max(0.05, min(1.0, minute_val / 60.0))
    m_level = TUBE_BOT - int((TUBE_H - 16) * m_fill_frac)
    draw.rounded_rectangle((M_X - TUBE_W // 2 + 3, m_level, M_X + TUBE_W // 2 - 3, TUBE_BOT - 3), radius=TUBE_R - 2, fill=cyan_color)
    # Meniscus
    draw.ellipse((M_X - TUBE_W // 2 + 3, m_level - 4, M_X + TUBE_W // 2 - 3, m_level + 6), fill=(220, 255, 250))

    # Bubbles inside minute tube (if provided)
    if bubbles:
        for bx, by in bubbles:
            # Clamp inside the fluid column
            if m_level < by < TUBE_BOT - 6:
                draw.ellipse((bx - 2, by - 2, bx + 2, by + 2), fill=(255, 255, 255), outline=(180, 255, 245))

    # Titanium Mounting Brackets
    for y_b in (TUBE_TOP + 28, TUBE_BOT - 28):
        draw.rounded_rectangle((H_X - TUBE_W // 2 - 6, y_b - 5, M_X + TUBE_W // 2 + 6, y_b + 5), radius=4, fill=(50, 56, 68), outline=(85, 95, 110), width=1)
        # Screws
        draw.ellipse((H_X - TUBE_W // 2 - 4, y_b - 2, H_X - TUBE_W // 2, y_b + 2), fill=(140, 150, 165))
        draw.ellipse((M_X + TUBE_W // 2, y_b - 2, M_X + TUBE_W // 2 + 4, y_b + 2), fill=(140, 150, 165))

    # Calibration scale ticks
    # Hours 1..12
    for h in range(1, 13):
        frac = (h - 1) / 11.0
        ty = TUBE_BOT - 12 - int(frac * (TUBE_H - 32))
        draw.line((H_X - TUBE_W // 2 - 8, ty, H_X - TUBE_W // 2 - 2, ty), fill=(120, 130, 145), width=1)
        if h in (1, 3, 6, 9, 10, 12):
            draw.text((H_X - TUBE_W // 2 - 12, ty), str(h), fill=(190, 205, 225) if h <= hour_val else (80, 90, 105), anchor="rm")

    # Minutes 00..60
    for m in (0, 10, 20, 30, 40, 50, 60):
        frac = m / 60.0
        ty = TUBE_BOT - 12 - int(frac * (TUBE_H - 32))
        draw.line((M_X + TUBE_W // 2 + 2, ty, M_X + TUBE_W // 2 + 8, ty), fill=(120, 130, 145), width=1)
        draw.text((M_X + TUBE_W // 2 + 12, ty), f"{m:02d}", fill=(180, 245, 235) if m <= minute_val else (80, 90, 105), anchor="lm")


# ==========================================
# 1. GIF 1: Siphon Flush & Hour Step
# ==========================================
def create_gif_1_siphon_flush() -> None:
    frames = []
    blue = (0, 115, 230)
    cyan = (0, 225, 210)

    # Phase A: Minute 58 -> 59 -> 60 (Rises slowly)
    for m in [58.0, 58.5, 59.0, 59.5, 60.0]:
        img = Image.new("RGB", (SIZE, SIZE), DARK_BG)
        draw = ImageDraw.Draw(img)
        draw_base_watch(draw, am_pm="AM", sun_moon_angle=0)
        draw_tubes(draw, hour_val=10.0, minute_val=m, blue_color=blue, cyan_color=cyan, flush_siphon_active=False)

        # Status annotation
        draw.rounded_rectangle((CX - 110, CY + 140, CX + 110, CY + 175), radius=6, fill=(24, 28, 36), outline=(50, 60, 75))
        draw.text((CX, CY + 152), f"TIME: 10:{int(m):02d}", fill=(240, 245, 250), anchor="mm")
        draw.text((CX, CY + 165), "Water reaches apex of siphon loop", fill=(140, 180, 220), anchor="mm")
        frames.append(img)

    # Phase B: Siphon Flush! Liquid rushes through top arch into bottom pipe, emptying to 00, Hour steps to 11
    flush_steps = [
        (58.0, 10.1, True, "Siphon Vacuum Triggers!"),
        (45.0, 10.3, True, "Cascade through top arch & return pipe"),
        (25.0, 10.6, True, "Suction pulls fluid downward rapidly"),
        (10.0, 10.8, True, "Hydraulic pressure pushes Hour up"),
        (2.0, 11.0, False, "Hour clicks to 11:00"),
        (0.0, 11.0, False, "FLUSH COMPLETE: 11:00 Reset!"),
        (0.0, 11.0, False, "FLUSH COMPLETE: 11:00 Reset!"),
    ]

    for m_val, h_val, is_siphon, status_txt in flush_steps:
        img = Image.new("RGB", (SIZE, SIZE), DARK_BG)
        draw = ImageDraw.Draw(img)
        draw_base_watch(draw, am_pm="AM", sun_moon_angle=0)
        draw_tubes(draw, hour_val=h_val, minute_val=m_val, blue_color=blue, cyan_color=cyan, flush_siphon_active=is_siphon)

        draw.rounded_rectangle((CX - 120, CY + 140, CX + 120, CY + 175), radius=6, fill=(35, 24, 30) if is_siphon else (20, 35, 30), outline=(80, 50, 60) if is_siphon else (40, 80, 60))
        draw.text((CX, CY + 152), f"TIME: {int(h_val):02d}:{int(m_val):02d}", fill=(255, 230, 230) if is_siphon else (200, 255, 220), anchor="mm")
        draw.text((CX, CY + 165), status_txt, fill=(255, 180, 180) if is_siphon else (160, 240, 190), anchor="mm")
        frames.append(img)

    frames[0].save(
        MOCKUPS / "gif_1_siphon_flush_reset.gif",
        save_all=True,
        append_images=frames[1:],
        duration=400,
        loop=0,
    )
    print("Saved gif_1_siphon_flush_reset.gif")


# ==========================================
# 2. GIF 2: Active Seconds (Aeration Bubbles)
# ==========================================
def create_gif_2_active_seconds() -> None:
    frames = []
    blue = (0, 115, 230)
    cyan = (0, 225, 210)

    # 10 frames simulating 5 seconds of bubble generation and rise
    num_frames = 12
    for f in range(num_frames):
        img = Image.new("RGB", (SIZE, SIZE), DARK_BG)
        draw = ImageDraw.Draw(img)
        draw_base_watch(draw, am_pm="AM", sun_moon_angle=0)

        # Bubble coordinates: rising up the Minute tube
        # Bubble 1
        b1_y = TUBE_BOT - 15 - ((f * 18) % (TUBE_H - 45))
        b1_x = M_X + int(4 * math.sin(f * 0.8))
        # Bubble 2 (offset)
        b2_y = TUBE_BOT - 15 - (((f + 6) * 18) % (TUBE_H - 45))
        b2_x = M_X - int(3 * math.cos(f * 0.8))

        bubbles = [(b1_x, b1_y), (b2_x, b2_y)]

        sec_count = (f % 5) + 1
        draw_tubes(draw, hour_val=10.0, minute_val=10.0, blue_color=blue, cyan_color=cyan, bubbles=bubbles)

        # Annotation
        draw.rounded_rectangle((CX - 120, CY + 140, CX + 120, CY + 175), radius=6, fill=(20, 28, 38), outline=(50, 75, 105))
        draw.text((CX, CY + 152), f"TIME: 10:10 - SECOND {sec_count:02d}", fill=(240, 245, 250), anchor="mm")
        draw.text((CX, CY + 165), "1-Hz Aeration Micro-Bubble Ticks Seconds", fill=(0, 235, 220), anchor="mm")

        frames.append(img)

    frames[0].save(
        MOCKUPS / "gif_2_active_seconds_bubbles.gif",
        save_all=True,
        append_images=frames[1:],
        duration=250,
        loop=0,
    )
    print("Saved gif_2_active_seconds_bubbles.gif")


# ==========================================
# 3. GIF 3: Day to Night (AM/PM Shift)
# ==========================================
def create_gif_3_am_pm_shift() -> None:
    frames = []

    # Transition from Day (Azure/Teal) to Night (Cobalt/Violet)
    # Day Colors
    day_blue = (0, 115, 235)
    day_cyan = (0, 235, 215)
    # Night Colors
    night_blue = (60, 40, 180)
    night_cyan = (150, 60, 230)

    num_steps = 10
    # Day frames
    for i in range(4):
        img = Image.new("RGB", (SIZE, SIZE), DARK_BG)
        draw = ImageDraw.Draw(img)
        draw_base_watch(draw, am_pm="AM", sun_moon_angle=0)
        draw_tubes(draw, hour_val=10.0, minute_val=10.0, blue_color=day_blue, cyan_color=day_cyan)
        draw.rounded_rectangle((CX - 120, CY + 140, CX + 120, CY + 175), radius=6, fill=(24, 32, 42), outline=(70, 95, 130))
        draw.text((CX, CY + 152), "AM MODE (DAYLIT AZURE)", fill=(255, 230, 140), anchor="mm")
        draw.text((CX, CY + 165), "Sun Disc at Apex - High-Contrast Daytime", fill=(180, 220, 255), anchor="mm")
        frames.append(img)

    # Twilight transition frames
    for step in range(num_steps):
        t = step / float(num_steps - 1)
        r_b = int(day_blue[0] * (1 - t) + night_blue[0] * t)
        g_b = int(day_blue[1] * (1 - t) + night_blue[1] * t)
        b_b = int(day_blue[2] * (1 - t) + night_blue[2] * t)

        r_c = int(day_cyan[0] * (1 - t) + night_cyan[0] * t)
        g_c = int(day_cyan[1] * (1 - t) + night_cyan[1] * t)
        b_c = int(day_cyan[2] * (1 - t) + night_cyan[2] * t)

        angle = t * 180.0
        mode_str = "AM" if t < 0.5 else "PM"

        img = Image.new("RGB", (SIZE, SIZE), DARK_BG)
        draw = ImageDraw.Draw(img)
        draw_base_watch(draw, am_pm=mode_str, sun_moon_angle=angle)
        draw_tubes(draw, hour_val=10.0, minute_val=10.0, blue_color=(r_b, g_b, b_b), cyan_color=(r_c, g_c, b_c))

        draw.rounded_rectangle((CX - 120, CY + 140, CX + 120, CY + 175), radius=6, fill=(30, 24, 38), outline=(80, 60, 100))
        draw.text((CX, CY + 152), f"TWILIGHT TRANSITION ({int(t*100)}%)", fill=(230, 200, 255), anchor="mm")
        draw.text((CX, CY + 165), "Disc rotates Sun -> Moon - Luminescence shifts", fill=(190, 160, 230), anchor="mm")
        frames.append(img)

    # Night frames
    for i in range(4):
        img = Image.new("RGB", (SIZE, SIZE), DARK_BG)
        draw = ImageDraw.Draw(img)
        draw_base_watch(draw, am_pm="PM", sun_moon_angle=180)
        draw_tubes(draw, hour_val=10.0, minute_val=10.0, blue_color=night_blue, cyan_color=night_cyan)
        draw.rounded_rectangle((CX - 120, CY + 140, CX + 120, CY + 175), radius=6, fill=(22, 18, 36), outline=(90, 65, 140))
        draw.text((CX, CY + 152), "PM MODE (BIOLUMINESCENT VIOLET)", fill=(200, 180, 255), anchor="mm")
        draw.text((CX, CY + 165), "Moon Disc - OLED Glow for Night Readability", fill=(220, 210, 255), anchor="mm")
        frames.append(img)

    frames[0].save(
        MOCKUPS / "gif_3_am_pm_color_shift.gif",
        save_all=True,
        append_images=frames[1:],
        duration=300,
        loop=0,
    )
    print("Saved gif_3_am_pm_color_shift.gif")


if __name__ == "__main__":
    create_gif_1_siphon_flush()
    create_gif_2_active_seconds()
    create_gif_3_am_pm_shift()
