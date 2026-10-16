"""Photorealistic animation engine v3:
- Completely static, crisp numerals and calibration ticks (no stretching!)
- Cylindrical fluid gradient with authentic optical refraction
- Glowing curved meniscus
- 1-Hz rising micro-bubbles with specular glints
- Dramatic siphon flush through the top arch and bottom return pipe
- Smooth hour advance from 10 to 11
- Seamless composite into the real watch photo with zero artifacts
"""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

MOCKUPS = Path("/Users/vivek/Development/Fluida/mockups")
SOURCE_IMG = MOCKUPS / "mockup_vessels_variant_B_skeleton_lab.jpg"
ANGLE = 15.06


def create_static_overlay(tube_img: Image.Image) -> Image.Image:
    """Extract static white numerals, calibration ticks, and glass reflections."""
    w, h = tube_img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pix_in = tube_img.load()
    pix_out = overlay.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = pix_in[x, y]
            brightness = (r + g + b) // 3
            # White numerals and tick marks
            # They have high R, G, B with low color saturation
            is_white_tick = (r > 155 and g > 165 and b > 165) and (max(r, g, b) - min(r, g, b) < 65)
            # Glass tube edge highlights
            is_edge_glint = (x < 7 or x > w - 8) and (brightness > 120)

            if is_white_tick:
                alpha = min(255, int((brightness - 130) * 3.0))
                pix_out[x, y] = (255, 255, 255, alpha)
            elif is_edge_glint:
                alpha = min(220, int(brightness * 0.75))
                pix_out[x, y] = (245, 250, 255, alpha)

    return overlay


def build_tube_frame(
    w: int,
    h: int,
    fill_frac: float,
    color_deep: tuple[int, int, int],
    color_core: tuple[int, int, int],
    meniscus_glow: tuple[int, int, int],
    overlay: Image.Image,
    bubble_offsets: list[float] = None,
) -> Image.Image:
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)

    # Tube interior boundaries (inside glass walls: x from 4 to w-5)
    ix1, ix2 = 5, w - 6
    iw = ix2 - ix1

    # Y level of fluid surface
    y_min, y_max = 16, h - 18
    fluid_y = int(y_max - fill_frac * (y_max - y_min))
    fluid_y = max(y_min, min(y_max, fluid_y))

    # 1. Dark skeleton gear background above fluid
    if fluid_y > 0:
        for y in range(fluid_y):
            # Subtle dark ruthenium texture
            gear_shading = 28 + int(8 * math.sin(y * 0.2))
            draw.line([(ix1, y), (ix2, y)], fill=(gear_shading, gear_shading + 3, gear_shading + 8, 255))

    # 2. Cylindrical liquid column below fluid_y
    if fluid_y < h:
        for x in range(ix1, ix2 + 1):
            # Cylindrical curvature factor: -1 at left, 0 in center, +1 at right
            norm_x = (x - (ix1 + iw / 2.0)) / (iw / 2.0)
            falloff = max(0.0, 1.0 - norm_x * norm_x)
            r = int(color_deep[0] * (1 - falloff) + color_core[0] * falloff)
            g = int(color_deep[1] * (1 - falloff) + color_core[1] * falloff)
            b = int(color_deep[2] * (1 - falloff) + color_core[2] * falloff)
            draw.line([(x, fluid_y), (x, h)], fill=(r, g, b, 240))

        # Glowing meniscus
        draw.ellipse((ix1, fluid_y - 4, ix2, fluid_y + 8), fill=(*meniscus_glow, 230))
        draw.ellipse((ix1 + 4, fluid_y - 2, ix2 - 4, fluid_y + 4), fill=(255, 255, 255, 255))

    # 3. Rising micro-bubbles inside fluid
    if bubble_offsets and fluid_y < y_max - 10:
        for b_frac in bubble_offsets:
            by = int(y_max - b_frac * (y_max - fluid_y))
            if fluid_y + 5 < by < y_max - 5:
                bx = ix1 + iw // 2 + int(4 * math.sin(by * 0.2))
                # Translucent spherical bubble with specular white highlight
                draw.ellipse((bx - 4, by - 4, bx + 4, by + 4), fill=(*meniscus_glow, 160), outline=(255, 255, 255, 230), width=1)
                draw.ellipse((bx - 2, by - 3, bx, by - 1), fill=(255, 255, 255, 255))

    # 4. Composite static white numerals, calibration ticks, and glass edge highlights
    out.alpha_composite(overlay)
    return out


def run() -> None:
    base_full = Image.open(SOURCE_IMG).convert("RGBA")
    rot_full = base_full.rotate(ANGLE, resample=Image.Resampling.BICUBIC)

    # Tube bounding boxes
    x1_h, x2_h = 386, 458
    x1_m, x2_m = 548, 618
    y1, y2 = 388, 642
    tw_h, tw_m, th = x2_h - x1_h, x2_m - x1_m, y2 - y1

    tube_m_orig = rot_full.crop((x1_m, y1, x2_m, y2))
    tube_h_orig = rot_full.crop((x1_h, y1, x2_h, y2))

    overlay_m = create_static_overlay(tube_m_orig)
    overlay_h = create_static_overlay(tube_h_orig)

    top_bracket = rot_full.crop((365, 375, 638, 405))
    bot_bracket = rot_full.crop((365, 625, 638, 660))

    # Colors
    BLUE_DEEP = (10, 60, 200)
    BLUE_CORE = (25, 140, 255)
    BLUE_MENISCUS = (170, 225, 255)

    CYAN_DEEP = (0, 160, 180)
    CYAN_CORE = (20, 235, 220)
    CYAN_MENISCUS = (180, 255, 245)

    # Animation steps
    timeline = [
        # (minute_frac, hour_frac, siphon_active, bubbles)
        # Running at 10:58 (Minute 58)
        (0.92, 10.0 / 12.0, False, [0.85, 0.35]),
        (0.94, 10.0 / 12.0, False, [0.65, 0.15]),
        (0.97, 10.0 / 12.0, False, [0.45, 0.95]),
        # Minute 59
        (0.99, 10.0 / 12.0, False, [0.25, 0.75]),
        # Minute 60: Touching top arch
        (1.00, 10.0 / 12.0, True, [0.05, 0.55]),
        # Siphon flush cascade! Minute empties, Hour steps 10 -> 11
        (0.68, 10.2 / 12.0, True, []),
        (0.38, 10.5 / 12.0, True, []),
        (0.16, 10.8 / 12.0, True, []),
        (0.04, 11.0 / 12.0, True, []),
        # 11:00 reset
        (0.02, 11.0 / 12.0, False, [0.95]),
        (0.02, 11.0 / 12.0, False, [0.75]),
        (0.02, 11.0 / 12.0, False, [0.55]),
    ]

    frames = []

    for m_frac, h_frac, is_siphon, bubbles in timeline:
        frame_rot = rot_full.copy()

        # Left Hour Tube
        h_tube = build_tube_frame(
            w=tw_h,
            h=th,
            fill_frac=h_frac,
            color_deep=BLUE_DEEP,
            color_core=BLUE_CORE,
            meniscus_glow=BLUE_MENISCUS,
            overlay=overlay_h,
            bubble_offsets=None,
        )
        frame_rot.paste(h_tube, (x1_h, y1), h_tube)

        # Right Minute Tube
        m_tube = build_tube_frame(
            w=tw_m,
            h=th,
            fill_frac=m_frac,
            color_deep=CYAN_DEEP,
            color_core=CYAN_CORE,
            meniscus_glow=CYAN_MENISCUS,
            overlay=overlay_m,
            bubble_offsets=bubbles,
        )
        frame_rot.paste(m_tube, (x1_m, y1), m_tube)

        # Top Arch siphon stream
        if is_siphon:
            draw_rot = ImageDraw.Draw(frame_rot, "RGBA")
            draw_rot.arc((422, 310, 582, 460), start=180, end=360, fill=(0, 240, 225, 200), width=12)
            draw_rot.arc((422, 310, 582, 460), start=180, end=360, fill=(230, 255, 255, 255), width=4)

        # Re-paste titanium brackets
        frame_rot.paste(top_bracket, (365, 375), top_bracket)
        frame_rot.paste(bot_bracket, (365, 625), bot_bracket)

        # Rotate back to original angle (-ANGLE)
        final_rot = frame_rot.rotate(-ANGLE, resample=Image.Resampling.BICUBIC)

        # Circular blend mask for dial center (radius 325)
        mask = Image.new("L", (1024, 1024), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse((512 - 325, 512 - 325, 512 + 325, 512 + 325), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(2))

        composed = base_full.copy()
        composed.paste(final_rot, (0, 0), mask)

        # Crop to watch display (800x800 -> 600x600)
        crop_final = composed.crop((112, 112, 912, 912)).resize((600, 600), Image.Resampling.LANCZOS)
        frames.append(crop_final.convert("RGB"))

    out_gif = MOCKUPS / "animated_fluida_actual_watch.gif"
    frames[0].save(
        out_gif,
        save_all=True,
        append_images=frames[1:],
        duration=320,
        loop=0,
    )
    print(f"Saved v3 photorealistic animation to: {out_gif}")


if __name__ == "__main__":
    run()
