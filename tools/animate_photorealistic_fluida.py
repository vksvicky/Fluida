"""Photorealistic animation engine for FLUIDA Watch Face.
Animates the actual photographic mockup (mockup_vessels_variant_B_skeleton_lab.jpg):
- Real titanium watch case, knurled bezel, and skeleton movement plates
- Minute liquid column rising, reaching 60, overflowing into the top glass arch
- Siphon cascade rapidly flushing the minute tube back to 00
- Hydraulic step advancing the blue Hour tube from 10 to 11
- Rising effervescent micro-bubbles tracking active seconds
"""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

MOCKUPS = Path("/Users/vivek/Development/Fluida/mockups")
SOURCE_IMG = MOCKUPS / "mockup_vessels_variant_B_skeleton_lab.jpg"

ANGLE = 15.06  # Exact tilt of the watch tubes in the photograph


def generate_photorealistic_animation() -> None:
    base_full = Image.open(SOURCE_IMG).convert("RGBA")

    # Rotate full image so tubes are perfectly vertical
    # Expand=True so we preserve full frame, center remains aligned
    rot_full = base_full.rotate(ANGLE, resample=Image.Resampling.BICUBIC)
    w, h = rot_full.size
    cx, cy = w // 2, h // 2

    # In rot_full coordinates (offset relative to crop_dial_test):
    # crop was at (200, 200) in 1024x1024
    # In test_rot (which was 624x624, centered at 312, 312):
    # Left tube box was: (186, 188, 258, 442) -> relative to (312, 312): (-126, -124, -54, 130)
    # Right tube box was: (346, 188, 418, 442) -> relative to (312, 312): (34, -124, 106, 130)

    # Let's verify absolute coordinates in rot_full (centered at cx, cy):
    # Left tube: X from cx - 126 to cx - 54, Y from cy - 124 to cy + 130
    # Right tube: X from cx + 34 to cx + 106, Y from cy - 124 to cy + 130

    # Let's crop a patch of the empty glass & skeleton gear background to use when tube is empty:
    # Notice in the minute tube, the region from Y: cy - 124 to cy - 40 is empty glass with gears!
    empty_glass_patch = rot_full.crop((cx + 34, cy - 124, cx + 106, cy - 40))

    # Real colors sampled directly from the photograph
    BLUE_DEEP = (10, 85, 230, 235)
    BLUE_CORE = (25, 140, 255, 255)
    BLUE_HIGHLIGHT = (180, 225, 255, 255)

    CYAN_DEEP = (0, 180, 190, 235)
    CYAN_CORE = (20, 235, 220, 255)
    CYAN_HIGHLIGHT = (210, 255, 250, 255)

    frames = []

    # Sequence of (minute_val, hour_val, is_siphon_cascade, bubble_y_offsets)
    # 1. Seconds ticking at 10:58 (Minute 58, 3 frames with rising bubble)
    # 2. Minute 59 (rising bubble reaches top)
    # 3. Minute 60 (fluid reaches arch)
    # 4. Siphon flush: fluid flows through top arch and bottom loop, minute drains, hour steps to 11
    # 5. Reset at 11:00 with fresh bubble

    steps = [
        # Normal running at 10:58 with 1-Hz rising bubbles
        (58.0, 10.0, False, [0.8, 0.4]),
        (58.3, 10.0, False, [0.6, 0.2]),
        (58.7, 10.0, False, [0.4, 0.95]),
        # Minute 59
        (59.0, 10.0, False, [0.2, 0.75]),
        (59.4, 10.0, False, [0.95, 0.55]),
        (59.8, 10.0, False, [0.75, 0.35]),
        # Minute 60 - Reaching apex of top arch
        (60.0, 10.0, True, [0.55, 0.15]),
        # Siphon cascade! Fluid pours through top arch, drains down, hour advances
        (48.0, 10.3, True, []),
        (32.0, 10.6, True, []),
        (16.0, 10.9, True, []),
        (4.0, 11.0, True, []),
        # Clean 11:00 reset
        (0.5, 11.0, False, [0.95]),
        (1.0, 11.0, False, [0.80]),
        (1.0, 11.0, False, [0.65]),
    ]

    for m_val, h_val, is_siphon, bubble_list in steps:
        frame_canvas = rot_full.copy()
        draw = ImageDraw.Draw(frame_canvas, "RGBA")

        # ----------------------------------------------------
        # 1. RENDER MINUTE TUBE FLUID (Right tube: X: cx+36 to cx+104, Y: cy-124 to cy+130)
        # ----------------------------------------------------
        x1_m, x2_m = cx + 36, cx + 104
        y_top, y_bot = cy - 124, cy + 130
        h_total = y_bot - y_top

        # Fluid fill level
        fill_ratio = max(0.02, min(1.0, m_val / 60.0))
        fluid_y = y_bot - int(h_total * fill_ratio)

        # Draw empty glass / skeleton background above fluid_y
        if fluid_y > y_top:
            empty_h = fluid_y - y_top
            # Tile / stretch empty glass patch
            empty_slice = empty_glass_patch.resize((x2_m - x1_m, empty_h), Image.Resampling.LANCZOS)
            frame_canvas.paste(empty_slice, (x1_m, y_top))

        # Fluid Column Overlay (smooth translucent gradient with glow)
        fluid_layer = Image.new("RGBA", (x2_m - x1_m, y_bot - fluid_y), (0, 0, 0, 0))
        f_draw = ImageDraw.Draw(fluid_layer)
        col_w = x2_m - x1_m

        for ix in range(col_w):
            # Cylindrical light refraction across tube diameter
            norm_x = (ix - col_w / 2.0) / (col_w / 2.0)
            falloff = max(0.0, 1.0 - norm_x * norm_x)
            r = int(CYAN_DEEP[0] * (1 - falloff) + CYAN_CORE[0] * falloff)
            g = int(CYAN_DEEP[1] * (1 - falloff) + CYAN_CORE[1] * falloff)
            b = int(CYAN_DEEP[2] * (1 - falloff) + CYAN_CORE[2] * falloff)
            f_draw.line([(ix, 0), (ix, y_bot - fluid_y)], fill=(r, g, b, 230))

        # Meniscus curved line
        f_draw.ellipse((2, -4, col_w - 2, 8), fill=CYAN_HIGHLIGHT)
        frame_canvas.alpha_composite(fluid_layer, (x1_m, fluid_y))

        # ----------------------------------------------------
        # 2. RENDER ACTIVE SECONDS MICRO-BUBBLES
        # ----------------------------------------------------
        for b_frac in bubble_list:
            by = y_bot - int((y_bot - fluid_y) * b_frac)
            if fluid_y + 6 < by < y_bot - 6:
                bx = x1_m + col_w // 2 + int(6 * math.sin(by * 0.1))
                # Translucent bubble with specular white highlight
                draw.ellipse((bx - 4, by - 4, bx + 4, by + 4), fill=(180, 255, 250, 120), outline=(230, 255, 255, 240), width=1)
                draw.ellipse((bx - 2, by - 3, bx, by - 1), fill=(255, 255, 255, 255))

        # ----------------------------------------------------
        # 3. RENDER HOUR TUBE FLUID (Left tube: X: cx-124 to cx-56, Y: cy-124 to cy+130)
        # ----------------------------------------------------
        x1_h, x2_h = cx - 124, cx - 56
        col_w_h = x2_h - x1_h
        h_ratio = max(0.05, min(1.0, h_val / 12.0))
        fluid_y_h = y_bot - int(h_total * h_ratio)

        # Fluid column
        h_layer = Image.new("RGBA", (col_w_h, y_bot - fluid_y_h), (0, 0, 0, 0))
        h_draw = ImageDraw.Draw(h_layer)
        for ix in range(col_w_h):
            norm_x = (ix - col_w_h / 2.0) / (col_w_h / 2.0)
            falloff = max(0.0, 1.0 - norm_x * norm_x)
            r = int(BLUE_DEEP[0] * (1 - falloff) + BLUE_CORE[0] * falloff)
            g = int(BLUE_DEEP[1] * (1 - falloff) + BLUE_CORE[1] * falloff)
            b = int(BLUE_DEEP[2] * (1 - falloff) + BLUE_CORE[2] * falloff)
            h_draw.line([(ix, 0), (ix, y_bot - fluid_y_h)], fill=(r, g, b, 235))

        # Hour Meniscus
        h_draw.ellipse((2, -4, col_w_h - 2, 8), fill=BLUE_HIGHLIGHT)
        frame_canvas.alpha_composite(h_layer, (x1_h, fluid_y_h))

        # ----------------------------------------------------
        # 4. RENDER TOP ARCH & BOTTOM SIPHON LOOPS (When active)
        # ----------------------------------------------------
        if is_siphon:
            # Top Arch glowing fluid stream
            arch_box = (cx - 100, cy - 220, cx + 80, cy - 60)
            draw.arc(arch_box, start=180, end=360, fill=(0, 235, 220, 210), width=10)
            draw.arc(arch_box, start=180, end=360, fill=(200, 255, 250, 255), width=4)

            # Bottom Return Pipe glowing fluid stream
            loop_box = (cx - 105, cy + 90, cx + 75, cy + 225)
            draw.arc(loop_box, start=0, end=180, fill=(0, 220, 240, 200), width=8)
            draw.arc(loop_box, start=0, end=180, fill=(220, 255, 255, 255), width=3)

        # ----------------------------------------------------
        # 5. RE-APPLY TITANIUM BRACKETS OVERLAY (So brackets stay cleanly in foreground)
        # ----------------------------------------------------
        # Bracket Y positions: cy - 138 to cy - 110 (top) and cy + 116 to cy + 144 (bottom)
        top_bracket = rot_full.crop((cx - 145, cy - 145, cx + 125, cy - 110))
        bot_bracket = rot_full.crop((cx - 145, cy + 115, cx + 125, cy + 150))
        frame_canvas.paste(top_bracket, (cx - 145, cy - 145), top_bracket)
        frame_canvas.paste(bot_bracket, (cx - 145, cy + 115), bot_bracket)

        # ----------------------------------------------------
        # 6. ROTATE BACK TO NATURAL WATCH ORIENTATION (-ANGLE)
        # ----------------------------------------------------
        final_frame = frame_canvas.rotate(-ANGLE, resample=Image.Resampling.BICUBIC)

        # Crop to the watch display region (750x750 centered)
        display_crop = final_frame.crop((cx - 375, cy - 375, cx + 375, cy + 375)).resize((500, 500), Image.Resampling.LANCZOS)
        frames.append(display_crop.convert("RGB"))

    # Save as high-quality animated GIF
    out_path = MOCKUPS / "animated_fluida_actual_watch.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=320,
        loop=0,
    )
    print(f"Saved: {out_path} ({len(frames)} frames)")


if __name__ == "__main__":
    generate_photorealistic_animation()
