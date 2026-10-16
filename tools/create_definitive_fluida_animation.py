"""Generate clean static watch and smooth animation with:
1. NO top connecting arch! (The central skeleton wheel and ruby jewel are fully open and visible)
2. NO bottom connecting pipe! (Each tube has its own independent closed base reservoir)
3. Left tube: Hours 1-12 with proper Swiss typography
4. Right tube: Minutes 00-60 with proper Swiss typography
5. Buttery smooth animation: Minute fills 00 -> 60, then is sucked down backward into its own reservoir, Hour steps 10 -> 11!
"""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MOCKUPS = Path("/Users/vivek/Development/Fluida/mockups")
SOURCE_IMG = MOCKUPS / "mockup_vessels_variant_B_skeleton_lab.jpg"
ANGLE = 15.06


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir.ttc", size, index=8 if bold else 0)
    except Exception:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)


def create_clean_independent_fluida() -> None:
    # 1. Load source image and rotate so tubes are vertical
    base_full = Image.open(SOURCE_IMG).convert("RGBA")
    rot_full = base_full.rotate(ANGLE, resample=Image.Resampling.BICUBIC)
    w, h = rot_full.size

    # Exact tube dimensions in rotated 1024x1024 frame:
    # Left Tube (Hour): X: 386 to 458 (w=72). Y: 388 to 642 (h=254)
    # Right Tube (Minute): X: 548 to 618 (w=70). Y: 388 to 642 (h=254)
    hx1, hx2 = 386, 458
    mx1, mx2 = 548, 618
    y1, y2 = 388, 642
    hcx = (hx1 + hx2) // 2
    mcx = (mx1 + mx2) // 2
    tw_h = hx2 - hx1
    tw_m = mx2 - mx1
    th = y2 - y1

    # 2. Reconstruct the clean dial backdrop:
    # Sample real dark ruthenium skeleton gear texture from central area
    clean_dial = rot_full.copy()
    c_draw = ImageDraw.Draw(clean_dial)

    # A. PAINT OUT THE TOP CONNECTING ARCH:
    # The arch is between X: 440 and 565, Y: 280 to 390
    # Behind the arch is the central skeleton wheel with spokes and ruby jewel at (502, 345)
    # Let's recreate the clean circular skeleton balance wheel and ruby jewel!
    wheel_cx, wheel_cy = 502, 340
    # Dark movement cavity behind wheel
    c_draw.ellipse((wheel_cx - 65, wheel_cy - 65, wheel_cx + 65, wheel_cy + 65), fill=(22, 25, 32))
    # Titanium wheel rim
    c_draw.ellipse((wheel_cx - 60, wheel_cy - 60, wheel_cx + 60, wheel_cy + 60), outline=(68, 76, 90), width=4)
    # 3 Spokes
    for sp_deg in (90, 210, 330):
        s_rad = math.radians(sp_deg)
        sx = wheel_cx + 56 * math.cos(s_rad)
        sy = wheel_cy + 56 * math.sin(s_rad)
        c_draw.line([(wheel_cx, wheel_cy), (sx, sy)], fill=(55, 62, 74), width=6)
        c_draw.line([(wheel_cx, wheel_cy), (sx, sy)], fill=(80, 90, 106), width=2)
    # Ruby pivot jewel in center
    c_draw.ellipse((wheel_cx - 14, wheel_cy - 14, wheel_cx + 14, wheel_cy + 14), fill=(60, 68, 80), outline=(100, 112, 130), width=2)
    c_draw.ellipse((wheel_cx - 9, wheel_cy - 9, wheel_cx + 9, wheel_cy + 9), fill=(195, 25, 75), outline=(245, 80, 130), width=1)
    c_draw.ellipse((wheel_cx - 4, wheel_cy - 4, wheel_cx + 4, wheel_cy + 4), fill=(255, 120, 160))

    # B. PAINT OUT THE BOTTOM CONNECTING PIPE:
    # The bottom pipe runs between X: 435 and 570, Y: 635 to 705
    # Behind it is the dark circular movement bridge
    bridge_box = (360, 630, 645, 715)
    c_draw.rectangle(bridge_box, fill=(24, 27, 34))
    # Beveled titanium edge of the lower movement bridge
    c_draw.arc((320, 520, 685, 710), start=35, end=145, fill=(50, 56, 68), width=5)
    c_draw.arc((320, 520, 685, 710), start=35, end=145, fill=(78, 88, 104), width=2)

    # 3. BUILD INDEPENDENT CLOSED CAPS AND BASES FOR EACH TUBE:
    # Left Tube (Hour):
    # Top Cap: clean rounded titanium cap closing the tube at the top
    c_draw.rounded_rectangle((hx1 - 2, y1 - 12, hx2 + 2, y1 + 6), radius=5, fill=(65, 72, 85), outline=(130, 142, 160), width=2)
    c_draw.ellipse((hcx - 5, y1 - 8, hcx + 5, y1 - 2), fill=(170, 180, 195))
    # Independent Bottom Reservoir Base: closed glass bubble/metal cup
    c_draw.rounded_rectangle((hx1 - 2, y2 - 6, hx2 + 2, y2 + 26), radius=7, fill=(52, 58, 70), outline=(115, 126, 142), width=2)
    # Blue reservoir glass bulb
    c_draw.ellipse((hcx - 18, y2 + 2, hcx + 18, y2 + 22), fill=(15, 55, 160), outline=(60, 120, 230), width=2)

    # Right Tube (Minute):
    # Top Cap: clean rounded titanium cap closing the tube at the top
    c_draw.rounded_rectangle((mx1 - 2, y1 - 12, mx2 + 2, y1 + 6), radius=5, fill=(65, 72, 85), outline=(130, 142, 160), width=2)
    c_draw.ellipse((mcx - 5, y1 - 8, mcx + 5, y1 - 2), fill=(170, 180, 195))
    # Independent Bottom Reservoir Base: closed glass bubble/metal cup
    c_draw.rounded_rectangle((mx1 - 2, y2 - 6, mx2 + 2, y2 + 26), radius=7, fill=(52, 58, 70), outline=(115, 126, 142), width=2)
    # Cyan reservoir glass bulb
    c_draw.ellipse((mcx - 18, y2 + 2, mcx + 18, y2 + 22), fill=(0, 130, 125), outline=(0, 215, 205), width=2)

    # Titanium Clamping Brackets (holding each tube securely)
    for y_br in (y1 + 42, y2 - 42):
        c_draw.rounded_rectangle((hx1 - 8, y_br - 6, hx2 + 8, y_br + 6), radius=3, fill=(68, 76, 90), outline=(135, 148, 168), width=1)
        c_draw.ellipse((hx1 - 5, y_br - 2, hx1 - 1, y_br + 2), fill=(185, 195, 210))
        c_draw.ellipse((hx2 + 1, y_br - 2, hx2 + 5, y_br + 2), fill=(185, 195, 210))

        c_draw.rounded_rectangle((mx1 - 8, y_br - 6, mx2 + 8, y_br + 6), radius=3, fill=(68, 76, 90), outline=(135, 148, 168), width=1)
        c_draw.ellipse((mx1 - 5, y_br - 2, mx1 - 1, y_br + 2), fill=(185, 195, 210))
        c_draw.ellipse((mx2 + 1, y_br - 2, mx2 + 5, y_br + 2), fill=(185, 195, 210))

    # 4. SWISS TYPOGRAPHY & CALIBRATION OVERLAY (Avenir font)
    scale_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(scale_overlay)
    font_scale = get_font(13, bold=True)
    font_sub = get_font(10, bold=False)

    usable_y1 = y1 + 14
    usable_y2 = y2 - 14
    span = usable_y2 - usable_y1

    # LEFT TUBE: Hours 1 to 12
    for h_num in range(1, 13):
        frac = (h_num - 1) / 11.0
        ty = usable_y2 - int(frac * span)
        # Major tick
        s_draw.line([(hx1 + 5, ty), (hx1 + 18, ty)], fill=(255, 255, 255, 255), width=2)
        # Numeral
        s_draw.text((hx1 + 24, ty), str(h_num), fill=(255, 255, 255, 255), font=font_scale, anchor="lm")
        # Sub-tick (half hour)
        if h_num < 12:
            ty_sub = ty - int(0.5 / 11.0 * span)
            s_draw.line([(hx1 + 5, ty_sub), (hx1 + 12, ty_sub)], fill=(200, 220, 245, 180), width=1)

    # RIGHT TUBE: Minutes 00 to 60
    for m_num in (0, 10, 20, 30, 40, 50, 60):
        frac = m_num / 60.0
        ty = usable_y2 - int(frac * span)
        # Major tick
        s_draw.line([(mx2 - 18, ty), (mx2 - 5, ty)], fill=(255, 255, 255, 255), width=2)
        # Numeral
        s_draw.text((mx2 - 24, ty), f"{m_num:02d}", fill=(255, 255, 255, 255), font=font_scale, anchor="rm")
        # 5-minute sub-tick
        if m_num < 60:
            ty_5 = ty - int(5.0 / 60.0 * span)
            s_draw.line([(mx2 - 13, ty_5), (mx2 - 5, ty_5)], fill=(185, 250, 245, 190), width=1)
            for sub_m in (1, 2, 3, 4, 6, 7, 8, 9):
                ty_1 = ty - int(sub_m / 60.0 * span)
                s_draw.line([(mx2 - 9, ty_1), (mx2 - 5, ty_1)], fill=(155, 230, 225, 130), width=1)

    # 5. 3D BOROSILICATE GLASS CYLINDER SPECULAR HIGHLIGHTS
    glass_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glass_layer := glass_overlay)
    for bx1, bx2 in [(hx1, hx2), (mx1, mx2)]:
        # Left wall glint
        g_draw.line([(bx1 + 2, y1), (bx1 + 2, y2)], fill=(255, 255, 255, 200), width=2)
        g_draw.line([(bx1 + 5, y1), (bx1 + 5, y2)], fill=(210, 230, 255, 75), width=2)
        # Right wall glint
        g_draw.line([(bx2 - 2, y1), (bx2 - 2, y2)], fill=(255, 255, 255, 190), width=2)
        g_draw.line([(bx2 - 5, y1), (bx2 - 5, y2)], fill=(210, 230, 255, 65), width=2)

    # Colors
    BLUE_DEEP = (10, 60, 215)
    BLUE_CORE = (30, 145, 255)
    BLUE_MENISCUS = (180, 230, 255)

    CYAN_DEEP = (0, 160, 185)
    CYAN_CORE = (15, 235, 220)
    CYAN_MENISCUS = (185, 255, 245)

    def draw_fluid_body(
        bx1: int,
        bx2: int,
        fill_frac: float,
        deep_col: tuple[int, int, int],
        core_col: tuple[int, int, int],
        meniscus_col: tuple[int, int, int],
        bubbles: list[float] = None,
    ) -> Image.Image:
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        ix1, ix2 = bx1 + 4, bx2 - 4
        iw = ix2 - ix1

        fluid_y = usable_y2 - int(fill_frac * span)
        fluid_y = max(usable_y1, min(usable_y2, fluid_y))

        # Cylindrical liquid column
        for x in range(ix1, ix2 + 1):
            norm_x = (x - (ix1 + iw / 2.0)) / (iw / 2.0)
            falloff = max(0.0, 1.0 - norm_x * norm_x)
            r = int(deep_col[0] * (1 - falloff) + core_col[0] * falloff)
            g = int(deep_col[1] * (1 - falloff) + core_col[1] * falloff)
            b = int(deep_col[2] * (1 - falloff) + core_col[2] * falloff)
            d.line([(x, fluid_y), (x, y2)], fill=(r, g, b, 245))

        # Glowing Meniscus
        d.ellipse((ix1, fluid_y - 3, ix2, fluid_y + 6), fill=(*meniscus_col, 240))
        d.ellipse((ix1 + 5, fluid_y - 1, ix2 - 5, fluid_y + 3), fill=(255, 255, 255, 255))

        # Rising micro-bubbles
        if bubbles and fluid_y < usable_y2 - 8:
            for b_frac in bubbles:
                by = usable_y2 - int(b_frac * (usable_y2 - fluid_y))
                if fluid_y + 5 < by < usable_y2 - 5:
                    bx = ix1 + iw // 2 + int(4 * math.sin(by * 0.2))
                    d.ellipse((bx - 4, by - 4, bx + 4, by + 4), fill=(*meniscus_col, 150), outline=(255, 255, 255, 230), width=1)
                    d.ellipse((bx - 2, by - 3, bx, by - 1), fill=(255, 255, 255, 255))

        return layer

    # 36-frame smooth animation timeline
    timeline = []

    # Phase 1: Rising from 0 to 60 (16 smooth frames)
    rise_m = [0.0, 4.0, 8.0, 14.0, 20.0, 26.0, 32.0, 38.0, 44.0, 50.0, 54.0, 57.0, 58.5, 59.2, 59.8, 60.0]
    for i, m in enumerate(rise_m):
        m_frac = m / 60.0
        h_frac = (10.0 + (m / 60.0) * 0.05) / 12.0
        b1 = (i * 0.18) % 1.0
        b2 = ((i + 5) * 0.18) % 1.0
        timeline.append((m_frac, h_frac, [b1, b2]))

    # Phase 2: Vacuum Siphon Drain! Smooth non-linear backward drain 60 -> 0 (12 frames)
    # Hour column steps smoothly from 10.05 to 11.00
    drain_m = [54.0, 45.0, 34.0, 24.0, 15.0, 8.0, 4.0, 1.5, 0.5, 0.0, 0.0, 0.0]
    drain_h = [10.08, 10.18, 10.35, 10.55, 10.75, 10.90, 10.97, 11.00, 11.00, 11.00, 11.00, 11.00]
    for d_m, d_h in zip(drain_m, drain_h):
        timeline.append((d_m / 60.0, d_h / 12.0, []))

    # Phase 3: Settle at 11:00 (8 frames)
    for i in range(8):
        m = i * 0.3
        b1 = (i * 0.22) % 1.0
        timeline.append((m / 60.0, 11.0 / 12.0, [b1]))

    frames = []
    print(f"Generating {len(timeline)} frames for clean independent watch...")

    for m_frac, h_frac, bubbles in timeline:
        frame_rot = clean_dial.copy()

        # Hour fluid
        h_fluid = draw_fluid_body(
            bx1=hx1,
            bx2=hx2,
            fill_frac=h_frac,
            deep_col=BLUE_DEEP,
            core_col=BLUE_CORE,
            meniscus_col=BLUE_MENISCUS,
            bubbles=None,
        )
        frame_rot.alpha_composite(h_fluid)

        # Minute fluid
        m_fluid = draw_fluid_body(
            bx1=mx1,
            bx2=mx2,
            fill_frac=m_frac,
            deep_col=CYAN_DEEP,
            core_col=CYAN_CORE,
            meniscus_col=CYAN_MENISCUS,
            bubbles=bubbles,
        )
        frame_rot.alpha_composite(m_fluid)

        # Scale markings
        frame_rot.alpha_composite(scale_overlay)

        # Glass highlights
        frame_rot.alpha_composite(glass_overlay)

        # Rotate back by -ANGLE
        final_rot = frame_rot.rotate(-ANGLE, resample=Image.Resampling.BICUBIC)

        # Blend onto untouched base_full
        mask = Image.new("L", (1024, 1024), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse((512 - 325, 512 - 325, 512 + 325, 512 + 325), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(2))

        composed = base_full.copy()
        composed.paste(final_rot, (0, 0), mask)

        # Save single high-res static frame for mockup_vessels_variant_B_clean.jpg
        if len(frames) == 0:
            composed.convert("RGB").save(MOCKUPS / "mockup_vessels_variant_B_clean.jpg", quality=95)

        # Crop to watch display (800x800 -> 600x600)
        crop_final = composed.crop((112, 112, 912, 912)).resize((600, 600), Image.Resampling.LANCZOS)
        frames.append(crop_final.convert("RGB"))

    out_gif = MOCKUPS / "animated_fluida_definitive.gif"
    frames[0].save(
        out_gif,
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
    )
    print(f"Clean independent animation saved: {out_gif}")


if __name__ == "__main__":
    create_clean_independent_fluida()
