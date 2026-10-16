import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 1024
CX, CY = SIZE // 2, SIZE // 2
DIAL_R = 480

# -------------------------------------------------------------
# 1. Base Dial Plate: Luxury Matte Slate / Titanium
# -------------------------------------------------------------
dial = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(dial)

# Draw circular dark slate dial backplate
# Subtle radial gradient from center (slightly lighter slate) to edge (darker obsidian)
for r in range(DIAL_R, 0, -1):
    ratio = r / float(DIAL_R)
    # Ambient light slightly above center
    val = int(58 - 22 * ratio)
    draw.ellipse((CX - r, CY - r, CX + r, CY + r), fill=(val, val + 2, val + 4, 255))

# Add authentic brushed titanium / slate micro-texture
random.seed(1337)
for y in range(CY - DIAL_R, CY + DIAL_R):
    for x in range(CX - DIAL_R, CX + DIAL_R):
        if (x - CX)**2 + (y - CY)**2 <= DIAL_R**2:
            p = dial.getpixel((x, y))
            n = random.randint(-2, 2)
            dial.putpixel((x, y), (max(0, min(255, p[0] + n)),
                                   max(0, min(255, p[1] + n)),
                                   max(0, min(255, p[2] + n)), 255))

# -------------------------------------------------------------
# 2. Outer Chapter Ring & Precision Railtrack
# -------------------------------------------------------------
# Outer titanium chamfer ring
draw.ellipse((CX - DIAL_R, CY - DIAL_R, CX + DIAL_R, CY + DIAL_R), outline=(130, 138, 150, 240), width=4)
draw.ellipse((CX - DIAL_R + 4, CY - DIAL_R + 4, CX + DIAL_R - 4, CY + DIAL_R - 4), outline=(35, 38, 45, 200), width=3)

# Chapter ring track at r = 445 to 470
track_r = 458
draw.ellipse((CX - track_r, CY - track_r, CX + track_r, CY + track_r), outline=(75, 82, 94, 180), width=1)
draw.ellipse((CX - track_r + 16, CY - track_r + 16, CX + track_r - 16, CY + track_r - 16), outline=(50, 55, 65, 140), width=1)

# Fonts
arial_bold = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
arial_reg = '/System/Library/Fonts/Supplemental/Arial.ttf'

font_rim = ImageFont.truetype(arial_reg, 12)
font_brand = ImageFont.truetype(arial_reg, 21)
font_sec_num = ImageFont.truetype(arial_bold, 28)
font_date_mon = ImageFont.truetype(arial_reg, 15)
font_date_num = ImageFont.truetype(arial_bold, 36)
font_scale = ImageFont.truetype(arial_bold, 18)
font_metric_val = ImageFont.truetype(arial_bold, 18)
font_step_val = ImageFont.truetype(arial_bold, 20)

# 60-second rim ticks
for s in range(60):
    rad = math.radians(s * 6.0 - 90.0)
    if s % 5 == 0:
        r1, r2 = track_r - 14, track_r + 2
        col = (230, 238, 248, 220)
        w = 2
        # Numerals 05, 10, ... 60
        num_str = f"{60 if s == 0 else s:02d}"
        nr = track_r - 28
        nx = CX + nr * math.cos(rad)
        ny = CY + nr * math.sin(rad)
        draw.text((nx, ny), num_str, fill=(170, 180, 195, 200), font=font_rim, anchor="mm")
    else:
        r1, r2 = track_r - 8, track_r
        col = (100, 110, 125, 140)
        w = 1
    p1 = (CX + r1 * math.cos(rad), CY + r1 * math.sin(rad))
    p2 = (CX + r2 * math.cos(rad), CY + r2 * math.sin(rad))
    draw.line([p1, p2], fill=col, width=w)

# -------------------------------------------------------------
# 3. Dual Vertical Capillary Fluid Tubes
# -------------------------------------------------------------
# Symmetrical geometry
TUBE_W = 64
TUBE_H = 460
TUBE_Y1 = 270
TUBE_Y2 = TUBE_Y1 + TUBE_H  # 730

H_CX = CX - 170  # 342
H_X1 = H_CX - TUBE_W // 2  # 310
H_X2 = H_X1 + TUBE_W       # 374

M_CX = CX + 170  # 682
M_X1 = M_CX - TUBE_W // 2  # 650
M_X2 = M_X1 + TUBE_W       # 714

# Helper function to render a realistic fluid vessel
def draw_fluid_vessel(canvas, x1, x2, y1, y2, fill_pct, deep_col, mid_col, core_col, glint_col, glow_rgba):
    cx = (x1 + x2) // 2
    w = x2 - x1
    h = y2 - y1
    d = ImageDraw.Draw(canvas)

    # 1. Recessed dark well behind the glass tube
    well_col = (20, 23, 28, 240)
    d.rounded_rectangle([x1 - 2, y1, x2 + 2, y2], radius=6, fill=well_col, outline=(30, 35, 42, 200), width=1)

    # 2. Fluid Column
    fluid_h = int(h * fill_pct)
    fluid_top = y2 - fluid_h

    # Liquid glow layer
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([x1 - 6, fluid_top - 6, x2 + 6, y2 + 6], radius=8, fill=glow_rgba)
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(glow)
    d = ImageDraw.Draw(canvas)

    # 3D cylindrical volumetric liquid gradient
    for y in range(fluid_top, y2):
        for x in range(x1 + 2, x2 - 2):
            t = (x - (x1 + 2)) / float(w - 4)
            # Cylindrical curvature
            curve = math.sin(t * math.pi)
            
            # Base color gradient
            r = int(deep_col[0] * (1 - curve) + core_col[0] * curve)
            g = int(deep_col[1] * (1 - curve) + core_col[1] * curve)
            b = int(deep_col[2] * (1 - curve) + core_col[2] * curve)

            # Specular liquid glint stripe around t = 0.28
            glint_dist = abs(t - 0.28)
            if glint_dist < 0.12:
                g_factor = (1.0 - glint_dist / 0.12) ** 2
                r = int(r * (1 - g_factor) + glint_col[0] * g_factor)
                g = int(g * (1 - g_factor) + glint_col[1] * g_factor)
                b = int(b * (1 - g_factor) + glint_col[2] * g_factor)

            canvas.putpixel((x, y), (r, g, b, 255))

    # Curved 3D Meniscus at top of fluid
    meniscus_h = 7
    # Dark shadow under meniscus
    d.ellipse([x1 + 2, fluid_top - 2, x2 - 2, fluid_top + meniscus_h], fill=core_col)
    d.ellipse([x1 + 2, fluid_top - 4, x2 - 2, fluid_top + meniscus_h - 2], fill=glint_col)
    d.ellipse([x1 + 3, fluid_top - 4, x2 - 3, fluid_top + meniscus_h - 4], fill=(255, 255, 255, 220))

    # 3. Borosilicate Glass Tube Walls & Highlights
    # Empty upper tube has subtle glass reflections
    for y in range(y1, fluid_top):
        for x in range(x1 + 2, x2 - 2):
            t = (x - (x1 + 2)) / float(w - 4)
            if abs(t - 0.28) < 0.08:
                # Soft glass reflection
                canvas.putpixel((x, y), (200, 220, 240, 45))

    # Glass outer tube borders and caustics
    d.line([(x1, y1), (x1, y2)], fill=(45, 52, 62, 220), width=2)
    d.line([(x2, y1), (x2, y2)], fill=(45, 52, 62, 220), width=2)

    # Specular white glass highlights
    d.line([(x1 + 3, y1 + 4), (x1 + 3, y2 - 4)], fill=(255, 255, 255, 200), width=2)
    d.line([(x1 + 6, y1 + 6), (x1 + 6, y2 - 6)], fill=(210, 230, 255, 75), width=2)
    d.line([(x2 - 3, y1 + 4), (x2 - 3, y2 - 4)], fill=(255, 255, 255, 170), width=2)
    d.line([(x2 - 6, y1 + 6), (x2 - 6, y2 - 6)], fill=(210, 230, 255, 65), width=2)

    # 4. Independent Brushed Titanium End-Caps
    # Top Cap
    d.rounded_rectangle([x1 - 6, y1 - 22, x2 + 6, y1 + 4], radius=6, fill=(58, 64, 75, 255), outline=(120, 130, 145, 255), width=2)
    # Hex bolt on top cap
    d.ellipse([cx - 5, y1 - 14, cx + 5, y1 - 4], fill=(160, 170, 185, 255), outline=(50, 55, 65, 255), width=1)
    d.line([(cx - 3, y1 - 9), (cx + 3, y1 - 9)], fill=(40, 45, 55, 255), width=1)

    # Bottom Reservoir Manifold
    d.rounded_rectangle([x1 - 8, y2 - 4, x2 + 8, y2 + 28], radius=7, fill=(50, 56, 68, 255), outline=(115, 125, 140, 255), width=2)
    # Hydraulic valve indicator
    d.ellipse([cx - 7, y2 + 7, cx + 7, y2 + 21], fill=deep_col, outline=core_col, width=2)
    d.ellipse([cx - 3, y2 + 11, cx + 3, y2 + 17], fill=(255, 255, 255, 220))

# Render Left Vessel: Hours (10.58 / 12)
hour_val = 10.58
draw_fluid_vessel(dial, H_X1, H_X2, TUBE_Y1, TUBE_Y2,
                  fill_pct=hour_val / 12.0,
                  deep_col=(0, 28, 95),
                  mid_col=(10, 90, 230),
                  core_col=(40, 150, 255),
                  glint_col=(180, 225, 255),
                  glow_rgba=(0, 110, 255, 120))

# Render Right Vessel: Minutes (35 / 60)
min_val = 35.0
draw_fluid_vessel(dial, M_X1, M_X2, TUBE_Y1, TUBE_Y2,
                  fill_pct=min_val / 60.0,
                  deep_col=(0, 55, 65),
                  mid_col=(0, 180, 195),
                  core_col=(40, 245, 230),
                  glint_col=(200, 255, 250),
                  glow_rgba=(0, 225, 240, 130))

draw = ImageDraw.Draw(dial)

# -------------------------------------------------------------
# 4. Calibrated Scales
# -------------------------------------------------------------
usable_y1 = TUBE_Y1 + 14
usable_y2 = TUBE_Y2 - 14
span = usable_y2 - usable_y1

# Left Tube: Hours 1 to 12
for h in range(1, 13):
    frac = (h - 1) / 11.0
    y = usable_y2 - int(frac * span)
    # Major calibration tick mark
    draw.line([(H_X1 - 22, y), (H_X1 - 6, y)], fill=(245, 248, 252, 230), width=2)
    # Hour numeral (right-aligned to X = H_X1 - 28)
    h_str = str(h)
    draw.text((H_X1 - 28, y), h_str, fill=(245, 248, 252, 255), font=font_scale, anchor="rm")
    # Half-hour intermediate tick
    if h < 12:
        y_mid = y - int(0.5 / 11.0 * span)
        draw.line([(H_X1 - 14, y_mid), (H_X1 - 6, y_mid)], fill=(150, 165, 185, 160), width=1)

# Right Tube: Minutes 00 to 60
for m in (0, 10, 20, 30, 40, 50, 60):
    frac = m / 60.0
    y = usable_y2 - int(frac * span)
    # Major calibration tick mark
    draw.line([(M_X2 + 6, y), (M_X2 + 22, y)], fill=(245, 248, 252, 230), width=2)
    # Minute numeral (left-aligned to X = M_X2 + 28)
    m_str = f"{m:02d}"
    draw.text((M_X2 + 28, y), m_str, fill=(245, 248, 252, 255), font=font_scale, anchor="lm")
    # 5-minute intermediate tick
    if m < 60:
        y_mid = y - int(5.0 / 60.0 * span)
        draw.line([(M_X2 + 6, y_mid), (M_X2 + 16, y_mid)], fill=(160, 220, 215, 180), width=1)
        # 1-minute fine ticks
        for sub_m in (1, 2, 3, 4, 6, 7, 8, 9):
            y_sub = y - int(sub_m / 60.0 * span)
            draw.line([(M_X2 + 6, y_sub), (M_X2 + 11, y_sub)], fill=(120, 170, 175, 130), width=1)

# -------------------------------------------------------------
# 5. Geometrically Spaced Central Complications
# -------------------------------------------------------------
# 1. TOP: BRANDING "F L U I D A" (y = 195)
brand_str = "F   L   U   I   D   A"
draw.text((CX, 195), brand_str, fill=(235, 240, 248, 235), font=font_brand, anchor="mm")

# 2. UPPER-CENTER: CIRCULAR SECONDS SUB-DIAL (cx = 512, cy = 360, radius = 52)
sec_cx, sec_cy = CX, 360
sec_r = 52

# Sunk circular track with bevel and shadow
draw.circle((sec_cx, sec_cy), sec_r + 4, outline=(30, 34, 42, 200), width=1)
draw.circle((sec_cx, sec_cy), sec_r, outline=(85, 95, 110, 220), width=2)
draw.circle((sec_cx, sec_cy), sec_r - 4, outline=(30, 34, 42, 200), width=1)

# 60 micro-ticks
for s in range(60):
    rad = math.radians(s * 6.0 - 90.0)
    if s % 5 == 0:
        r1, r2 = sec_r - 6, sec_r + 6
        col = (235, 242, 252, 220)
        w = 2
    else:
        r1, r2 = sec_r - 3, sec_r + 3
        col = (115, 128, 142, 130)
        w = 1
    p1 = (sec_cx + r1 * math.cos(rad), sec_cy + r1 * math.sin(rad))
    p2 = (sec_cx + r2 * math.cos(rad), sec_cy + r2 * math.sin(rad))
    draw.line([p1, p2], fill=col, width=w)

# Traveling fluid bubble at 35 seconds
sec_val = 35
bubble_rad = math.radians(sec_val * 6.0 - 90.0)
bx = sec_cx + sec_r * math.cos(bubble_rad)
by = sec_cy + sec_r * math.sin(bubble_rad)

# Glowing fluid bead
glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.circle((bx, by), 15, fill=(0, 225, 255, 160))
gd.circle((bx, by), 7, fill=(255, 255, 255, 230))
glow = glow.filter(ImageFilter.GaussianBlur(4))
dial.alpha_composite(glow)
draw = ImageDraw.Draw(dial)

draw.circle((bx, by), 7, fill=(0, 235, 255, 245), outline=(255, 255, 255, 255), width=1)
draw.circle((bx - 2, by - 2), 2, fill=(255, 255, 255, 255))

# Digital Seconds "35" centered inside
draw.text((sec_cx, sec_cy - 2), "35", fill=(0, 245, 255, 255), font=font_sec_num, anchor="mm")

# 3. MID-DIAL: DATE COMPLICATION (y = 520 / 552)
draw.text((CX, 520), "O  C  T", fill=(160, 172, 185, 230), font=font_date_mon, anchor="mm")
draw.text((CX, 554), "14", fill=(245, 248, 252, 255), font=font_date_num, anchor="mm")

# 4. FLANKING METRICS (Balanced row at y = 554):
# Load authentic Garmin icons
def load_authentic_garmin_icon(path, target_h=18):
    im = Image.open(path).convert('RGB')
    out = Image.new('RGBA', im.size)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = im.getpixel((x, y))
            intensity = max(r, g, b)
            if intensity > 15:
                scale = min(2.0, 255.0 / float(intensity)) if intensity < 160 else 1.0
                alpha = min(255, int((intensity / 255.0)**0.4 * 255))
                out.putpixel((x, y), (min(255, int(r * scale)),
                                      min(255, int(g * scale)),
                                      min(255, int(b * scale)),
                                      alpha))
            else:
                out.putpixel((x, y), (0, 0, 0, 0))
    ratio = target_h / float(im.height)
    new_size = (int(im.width * ratio), target_h)
    return out.resize(new_size, Image.Resampling.LANCZOS)

icon_hr = load_authentic_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_heart_red.png', target_h=18)
icon_batt = load_authentic_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_battery_green.png', target_h=16)
icon_steps = load_authentic_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_steps_teal.png', target_h=18)

# Left Flank: Heart Rate (centered around X = 422)
hr_val = "72"
hr_bbox = draw.textbbox((0, 0), hr_val, font=font_metric_val)
hr_tw = hr_bbox[2] - hr_bbox[0]
hr_total_w = icon_hr.width + 6 + hr_tw
hr_start_x = 422 - hr_total_w // 2

dial.paste(icon_hr, (int(hr_start_x), 554 - icon_hr.height // 2), icon_hr)
draw.text((hr_start_x + icon_hr.width + 6, 554), hr_val, fill=(245, 248, 252, 245), font=font_metric_val, anchor="lm")

# Right Flank: Battery (centered around X = 602, SWAPPED with Steps!)
batt_val = "82%"
batt_bbox = draw.textbbox((0, 0), batt_val, font=font_metric_val)
batt_tw = batt_bbox[2] - batt_bbox[0]
batt_total_w = icon_batt.width + 6 + batt_tw
batt_start_x = 602 - batt_total_w // 2

dial.paste(icon_batt, (int(batt_start_x), 554 - icon_batt.height // 2), icon_batt)
draw.text((batt_start_x + icon_batt.width + 6, 554), batt_val, fill=(0, 240, 125, 245), font=font_metric_val, anchor="lm")

# 5. BOTTOM COMPLICATION: STEPS (y = 720, centered at X = 512, SWAPPED with Battery!)
step_val = "8,450"
st_bbox = draw.textbbox((0, 0), step_val, font=font_step_val)
stw = st_bbox[2] - st_bbox[0]
step_total_w = icon_steps.width + 7 + stw
step_start_x = CX - step_total_w // 2

dial.paste(icon_steps, (int(step_start_x), 720 - icon_steps.height // 2), icon_steps)
draw.text((step_start_x + icon_steps.width + 7, 720), step_val, fill=(0, 235, 255, 245), font=font_step_val, anchor="lm")

# Save master 1024x1024 flat dial
dial_rgb = dial.convert("RGB")
out_dial_1024 = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/mockup_fluida_topdown_dial_1024.png"
dial_rgb.save(out_dial_1024, quality=98)
print("Master 1024x1024 Top-Down Dial written to:", out_dial_1024)

# Save 454x454 Connect IQ ready AMOLED dial
dial_454 = dial.resize((454, 454), Image.Resampling.LANCZOS)
out_dial_454 = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/mockup_fluida_topdown_dial_454.png"
dial_454.save(out_dial_454)
print("Connect IQ 454x454 Dial written to:", out_dial_454)

# -------------------------------------------------------------
# 6. Full Watch Studio Mockup (Flat Top-Down Case Composition)
# -------------------------------------------------------------
case_path = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/topdown_watch_case_base_1792042183938.jpg"
case_base = Image.open(case_path).convert("RGBA")

# Dial in the case is centered at (510, 507) with radius R = 166 (diameter = 332)
# Resize the 1024 dial into circular mask for the watch case
case_dial_size = 332
dial_for_case = dial.resize((case_dial_size, case_dial_size), Image.Resampling.LANCZOS)

# Create circular mask
mask = Image.new("L", (case_dial_size, case_dial_size), 0)
md = ImageDraw.Draw(mask)
md.ellipse((0, 0, case_dial_size, case_dial_size), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1))

# Composite into watch case at (510 - 166, 507 - 166) = (344, 341)
paste_pos = (510 - case_dial_size // 2, 507 - case_dial_size // 2)
case_base.paste(dial_for_case, paste_pos, mask)

out_case = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/mockup_fluida_luxury_topdown_watch.jpg"
case_base.convert("RGB").save(out_case, quality=98)
print("Master Full Luxury Top-Down Watch Mockup written to:", out_case)
