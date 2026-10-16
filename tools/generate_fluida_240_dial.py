import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def render_fluida(scale=1.0):
    SIZE = int(240 * scale)
    CX = SIZE // 2
    CY = SIZE // 2
    R = int(118 * scale)

    # 1. Base Slate Dial Plate (Clean minimal circular watch face)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark matte titanium slate background with subtle radial vignette
    for r in range(R, 0, -1):
        ratio = r / float(R)
        v = int((40 - 16 * ratio) * 1.0)
        draw.ellipse([CX - r, CY - r, CX + r, CY + r], fill=(v, v + 2, v + 4, 255))

    # Fine slate metallic texture
    random.seed(42)
    for y in range(CY - R, CY + R):
        for x in range(CX - R, CX + R):
            if (x - CX)**2 + (y - CY)**2 <= R**2:
                p = img.getpixel((x, y))
                n = random.randint(-1, 1)
                img.putpixel((x, y), (max(0, min(255, p[0] + n)),
                                      max(0, min(255, p[1] + n)),
                                      max(0, min(255, p[2] + n)), 255))

    # Minimalist outer titanium bezel rim (NO numbers around the border!)
    draw.ellipse([CX - R, CY - R, CX + R, CY + R], outline=(80, 88, 100, 240), width=max(1, int(1.5 * scale)))
    draw.ellipse([CX - R + int(2 * scale), CY - R + int(2 * scale), CX + R - int(2 * scale), CY + R - int(2 * scale)], outline=(25, 28, 33, 200), width=max(1, int(1 * scale)))

    # Exact Garmin Arial fonts
    arial_bold = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
    arial_reg = '/System/Library/Fonts/Supplemental/Arial.ttf'

    font_brand = ImageFont.truetype(arial_reg, max(8, int(9.5 * scale)))
    font_sec_num = ImageFont.truetype(arial_bold, max(9, int(13 * scale)))
    font_date_mon = ImageFont.truetype(arial_reg, max(6, int(7.5 * scale)))
    font_date_num = ImageFont.truetype(arial_bold, max(11, int(16 * scale)))
    font_metric_val = ImageFont.truetype(arial_bold, max(7, int(9.5 * scale)))
    font_step_val = ImageFont.truetype(arial_bold, max(8, int(11 * scale)))
    font_scale_num = ImageFont.truetype(arial_bold, max(6, int(8.5 * scale)))
    font_sub_dist = ImageFont.truetype(arial_reg, max(6, int(7.5 * scale)))

    # WIDER 3D TUBES & REPOSITIONED TO CLEAR CIRCULAR BEZEL
    # Tube width = 21px, height = 132px (y = 52 to y = 184)
    TUBE_W = int(21 * scale)
    TUBE_Y1 = int(52 * scale)
    TUBE_Y2 = int(184 * scale)
    TUBE_H = TUBE_Y2 - TUBE_Y1

    # Inward by 10px so scale numerals (1-12 and 00-60) have safe margin from circular bezel
    H_CX = int(55 * scale)
    H_X1 = H_CX - TUBE_W // 2
    H_X2 = H_X1 + TUBE_W

    M_CX = int(185 * scale)
    M_X1 = M_CX - TUBE_W // 2
    M_X2 = M_X1 + TUBE_W

    # Render Liquid Housing Manifolds & 3D Volumetric Tubes
    def draw_3d_tube_system(canvas, x1, x2, y1, y2, fill_frac, deep_c, mid_c, core_c, glint_c, glow_rgba):
        cx = (x1 + x2) // 2
        w = x2 - x1
        h = y2 - y1
        d = ImageDraw.Draw(canvas)

        # -----------------------------------------------------------------
        # A. BOTTOM LIQUID HOUSING RESERVOIR (Physical chamber holding the liquid)
        # -----------------------------------------------------------------
        res_w = w + int(8 * scale)
        res_h = int(25 * scale)
        res_x1 = cx - res_w // 2
        res_x2 = res_x1 + res_w
        res_y1 = y2 - int(2 * scale)
        res_y2 = res_y1 + res_h

        # Machined titanium reservoir chamber block
        d.rounded_rectangle([res_x1, res_y1, res_x2, res_y2], radius=int(4 * scale), fill=(46, 52, 62, 255), outline=(115, 126, 142, 255), width=max(1, int(1.5 * scale)))
        
        # Horizontal milled grooves on chamber block
        d.line([(res_x1 + int(2*scale), res_y1 + int(3*scale)), (res_x2 - int(2*scale), res_y1 + int(3*scale))], fill=(160, 172, 190, 200), width=max(1, int(1*scale)))
        d.line([(res_x1 + int(3*scale), res_y2 - int(3*scale)), (res_x2 - int(3*scale), res_y2 - int(3*scale))], fill=(25, 28, 35, 180), width=max(1, int(1*scale)))

        # Liquid Reservoir Sight-Gauge Window showing fluid reservoir level
        sight_margin_x = int(3.5 * scale)
        sight_margin_y = int(5 * scale)
        sight_x1 = res_x1 + sight_margin_x
        sight_x2 = res_x2 - sight_margin_x
        sight_y1 = res_y1 + sight_margin_y
        sight_y2 = res_y2 - sight_margin_y

        d.rounded_rectangle([sight_x1, sight_y1, sight_x2, sight_y2], radius=int(3 * scale), fill=(10, 12, 16, 255), outline=(70, 78, 90, 220), width=max(1, int(1 * scale)))
        
        # Deep liquid pool glowing inside reservoir window
        d.rounded_rectangle([sight_x1 + 1, sight_y1 + 1, sight_x2 - 1, sight_y2 - 1], radius=int(2 * scale), fill=deep_c)
        # Meniscus level in reservoir window
        res_men_y = sight_y1 + int((sight_y2 - sight_y1) * 0.35)
        d.rounded_rectangle([sight_x1 + 1, res_men_y, sight_x2 - 1, sight_y2 - 1], radius=int(2 * scale), fill=core_c)
        d.line([(sight_x1 + int(2*scale), res_men_y), (sight_x2 - int(2*scale), res_men_y)], fill=glint_c, width=max(1, int(1*scale)))

        # Compression collar nut connecting tube into reservoir
        nut_h = int(5 * scale)
        d.rounded_rectangle([x1 - int(2*scale), y2 - nut_h, x2 + int(2*scale), y2], radius=int(2 * scale), fill=(65, 72, 85, 255), outline=(140, 152, 170, 255), width=max(1, int(1*scale)))

        # -----------------------------------------------------------------
        # B. TOP TITANIUM EXPANSION CAP
        # -----------------------------------------------------------------
        cap_h = int(14 * scale)
        cap_w = w + int(6 * scale)
        cap_x1 = cx - cap_w // 2
        cap_x2 = cap_x1 + cap_w
        cap_y1 = y1 - cap_h + int(2 * scale)
        cap_y2 = y1 + int(2 * scale)

        d.rounded_rectangle([cap_x1, cap_y1, cap_x2, cap_y2], radius=int(4 * scale), fill=(52, 58, 68, 255), outline=(115, 126, 142, 255), width=max(1, int(1.5 * scale)))
        # Micro hex bolt on top cap
        bolt_r = int(2.5 * scale)
        d.ellipse([cx - bolt_r, cap_y1 + int(3*scale), cx + bolt_r, cap_y1 + int(3*scale) + bolt_r * 2], fill=(160, 170, 185, 255), outline=(40, 45, 55, 255), width=1)

        # -----------------------------------------------------------------
        # C. 3D BOROSILICATE GLASS TUBE & VOLUMETRIC FLUID
        # -----------------------------------------------------------------
        # Recessed background channel behind glass
        d.rounded_rectangle([x1 - 1, y1, x2 + 1, y2], radius=int(3 * scale), fill=(16, 18, 22, 255), outline=(28, 32, 38, 200), width=1)

        # Fluid column height
        fluid_h = int(h * fill_frac)
        fluid_top = y2 - fluid_h

        # Ambient fluid glow
        glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.rounded_rectangle([x1 - int(3*scale), fluid_top - int(3*scale), x2 + int(3*scale), y2 + int(2*scale)], radius=int(5*scale), fill=glow_rgba)
        glow = glow.filter(ImageFilter.GaussianBlur(max(2, int(3 * scale))))
        canvas.alpha_composite(glow)
        d = ImageDraw.Draw(canvas)

        # Volumetric 3D cylindrical liquid fill
        for py in range(fluid_top, y2):
            for px in range(x1 + 1, x2 - 1):
                t = (px - (x1 + 1)) / float(w - 2)
                curve = math.sin(t * math.pi)
                
                cr = int(deep_c[0] * (1 - curve) + core_c[0] * curve)
                cg = int(deep_c[1] * (1 - curve) + core_c[1] * curve)
                cb = int(deep_c[2] * (1 - curve) + core_c[2] * curve)

                glint_d = abs(t - 0.26)
                if glint_d < 0.14:
                    gf = (1.0 - glint_d / 0.14) ** 2
                    cr = int(cr * (1 - gf) + glint_c[0] * gf)
                    cg = int(cg * (1 - gf) + glint_c[1] * gf)
                    cb = int(cb * (1 - gf) + glint_c[2] * gf)

                canvas.putpixel((px, py), (cr, cg, cb, 255))

        # 3D Liquid Meniscus (curved dome surface tension)
        men_h = max(3, int(4 * scale))
        d.ellipse([x1 + 1, fluid_top - int(2*scale), x2 - 1, fluid_top + men_h], fill=core_c)
        d.ellipse([x1 + 2, fluid_top - int(3*scale), x2 - 2, fluid_top + men_h - int(1*scale)], fill=glint_c)
        d.ellipse([x1 + int(3*scale), fluid_top - int(3*scale), x2 - int(3*scale), fluid_top + men_h - int(3*scale)], fill=(255, 255, 255, 230))

        # Borosilicate glass tube walls and specular reflections
        for py in range(y1, fluid_top):
            for px in range(x1 + 1, x2 - 1):
                t = (px - (x1 + 1)) / float(w - 2)
                if abs(t - 0.26) < 0.08:
                    canvas.putpixel((px, py), (210, 230, 255, int(40 * scale)))

        # Outer glass tube edges
        d.line([(x1, y1), (x1, y2)], fill=(45, 52, 62, 220), width=max(1, int(1.5 * scale)))
        d.line([(x2, y1), (x2, y2)], fill=(45, 52, 62, 220), width=max(1, int(1.5 * scale)))

        # Specular highlight along left glass flank
        d.line([(x1 + int(2*scale), y1 + int(2*scale)), (x1 + int(2*scale), y2 - int(2*scale))], fill=(255, 255, 255, 190), width=max(1, int(1.5 * scale)))
        d.line([(x2 - int(2*scale), y1 + int(2*scale)), (x2 - int(2*scale), y2 - int(2*scale))], fill=(210, 230, 255, 140), width=max(1, int(1*scale)))

    # Draw Left Tube: Hours (10.58 / 12)
    hour_fill = 10.58 / 12.0
    draw_3d_tube_system(img, H_X1, H_X2, TUBE_Y1, TUBE_Y2, hour_fill,
                        deep_c=(0, 25, 95), mid_c=(10, 85, 230), core_c=(35, 145, 255), glint_c=(170, 225, 255),
                        glow_rgba=(0, 110, 255, 130))

    # Draw Right Tube: Minutes (35 / 60)
    min_fill = 35.0 / 60.0
    draw_3d_tube_system(img, M_X1, M_X2, TUBE_Y1, TUBE_Y2, min_fill,
                        deep_c=(0, 50, 60), mid_c=(0, 180, 195), core_c=(30, 240, 225), glint_c=(190, 255, 250),
                        glow_rgba=(0, 225, 240, 140))

    draw = ImageDraw.Draw(img)

    # -----------------------------------------------------------------
    # 2. CALIBRATED FLANK MARKINGS (Comfortable margins from circle edge)
    # -----------------------------------------------------------------
    usable_y1 = TUBE_Y1 + int(6 * scale)
    usable_y2 = TUBE_Y2 - int(6 * scale)
    span = usable_y2 - usable_y1

    # Left Tube: Hours 1 to 12
    for h in range(1, 13):
        frac = (h - 1) / 11.0
        y = usable_y2 - int(frac * span)
        draw.line([(H_X1 - int(8 * scale), y), (H_X1 - int(2 * scale), y)], fill=(245, 248, 252, 220), width=max(1, int(1 * scale)))
        draw.text((H_X1 - int(10 * scale), y), str(h), fill=(245, 248, 252, 255), font=font_scale_num, anchor="rm")
        if h < 12:
            y_mid = y - int(0.5 / 11.0 * span)
            draw.line([(H_X1 - int(5 * scale), y_mid), (H_X1 - int(2 * scale), y_mid)], fill=(140, 155, 175, 150), width=1)

    # Right Tube: Minutes 00 to 60
    for m in (0, 10, 20, 30, 40, 50, 60):
        frac = m / 60.0
        y = usable_y2 - int(frac * span)
        draw.line([(M_X2 + int(2 * scale), y), (M_X2 + int(8 * scale), y)], fill=(245, 248, 252, 220), width=max(1, int(1 * scale)))
        draw.text((M_X2 + int(10 * scale), y), f"{m:02d}", fill=(245, 248, 252, 255), font=font_scale_num, anchor="lm")
        if m < 60:
            y_mid = y - int(5.0 / 60.0 * span)
            draw.line([(M_X2 + int(2 * scale), y_mid), (M_X2 + int(5 * scale), y_mid)], fill=(150, 210, 205, 170), width=1)

    # -----------------------------------------------------------------
    # 3. SPACIOUS CENTRAL ATRIUM & COMPLICATIONS
    # Width between tubes: M_X1 - H_X2 = 174 - 66 = 108px (Plenty of space!)
    # -----------------------------------------------------------------
    # Zone 1: BRAND "F L U I D A" (y = 28)
    draw.text((CX, int(28 * scale)), "F   L   U   I   D   A", fill=(235, 240, 248, 230), font=font_brand, anchor="mm")

    # Zone 2: CIRCULAR SECONDS SUB-DIAL (cx = 120, cy = 66, radius = 20)
    sec_cx, sec_cy = CX, int(66 * scale)
    sec_r = int(20 * scale)

    # Recessed circular capillary track
    draw.circle((sec_cx, sec_cy), sec_r + max(1, int(2*scale)), outline=(28, 32, 40, 200), width=1)
    draw.circle((sec_cx, sec_cy), sec_r, outline=(75, 85, 100, 220), width=max(1, int(1.5*scale)))
    draw.circle((sec_cx, sec_cy), sec_r - max(1, int(2*scale)), outline=(28, 32, 40, 200), width=1)

    # 60 micro-ticks
    for s in range(60):
        rad = math.radians(s * 6.0 - 90.0)
        if s % 5 == 0:
            r1, r2 = sec_r - int(3 * scale), sec_r + int(3 * scale)
            col = (235, 242, 252, 220)
            w = max(1, int(1.5 * scale))
        else:
            r1, r2 = sec_r - int(1.5 * scale), sec_r + int(1.5 * scale)
            col = (110, 122, 138, 120)
            w = 1
        p1 = (sec_cx + r1 * math.cos(rad), sec_cy + r1 * math.sin(rad))
        p2 = (sec_cx + r2 * math.cos(rad), sec_cy + r2 * math.sin(rad))
        draw.line([p1, p2], fill=col, width=w)

    # Traveling illuminated fluid bubble at second 35
    bubble_rad = math.radians(35 * 6.0 - 90.0)
    bx = sec_cx + sec_r * math.cos(bubble_rad)
    by = sec_cy + sec_r * math.sin(bubble_rad)

    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.circle((bx, by), int(7 * scale), fill=(0, 225, 255, 160))
    gd.circle((bx, by), int(3.5 * scale), fill=(255, 255, 255, 230))
    glow = glow.filter(ImageFilter.GaussianBlur(max(1, int(2 * scale))))
    img.alpha_composite(glow)
    draw = ImageDraw.Draw(img)

    draw.circle((bx, by), int(3.5 * scale), fill=(0, 235, 255, 250), outline=(255, 255, 255, 255), width=1)

    # Digital Seconds "35" inside subdial
    draw.text((sec_cx, sec_cy - int(1 * scale)), "35", fill=(0, 245, 255, 255), font=font_sec_num, anchor="mm")

    # Zone 3: DATE COMPLICATION (y = 104 / 118)
    draw.text((CX, int(105 * scale)), "O C T", fill=(160, 172, 185, 230), font=font_date_mon, anchor="mm")
    draw.text((CX, int(120 * scale)), "14", fill=(245, 248, 252, 255), font=font_date_num, anchor="mm")

    # Helper to load & tint authentic Garmin icons
    def load_garmin_icon(path, target_h, tint_color=None):
        im = Image.open(path).convert('RGB')
        out = Image.new('RGBA', im.size)
        for y in range(im.height):
            for x in range(im.width):
                r, g, b = im.getpixel((x, y))
                intensity = max(r, g, b)
                if intensity > 15:
                    scale_c = min(2.0, 255.0 / float(intensity)) if intensity < 160 else 1.0
                    alpha = min(255, int((intensity / 255.0)**0.45 * 255))
                    if tint_color is not None:
                        out.putpixel((x, y), (tint_color[0], tint_color[1], tint_color[2], alpha))
                    else:
                        out.putpixel((x, y), (min(255, int(r * scale_c)),
                                              min(255, int(g * scale_c)),
                                              min(255, int(b * scale_c)),
                                              alpha))
                else:
                    out.putpixel((x, y), (0, 0, 0, 0))
        ratio = target_h / float(im.height)
        new_size = (max(1, int(im.width * ratio)), target_h)
        return out.resize(new_size, Image.Resampling.LANCZOS)

    icon_h_val = max(8, int(9.5 * scale))
    icon_hr = load_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_heart_red.png', icon_h_val)
    icon_batt = load_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_battery_green.png', max(7, int(8.5 * scale)))
    icon_flame = load_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_flame_orange.png', icon_h_val)
    icon_temp = load_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_weather_temp_white.png', icon_h_val, tint_color=(255, 205, 60))
    icon_steps = load_garmin_icon('/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/scratch/icon_steps_teal.png', max(9, int(11 * scale)))

    # Centers for flanking metrics (Left center = 88, Right center = 152)
    flank_left_cx = int(88 * scale)
    flank_right_cx = int(152 * scale)

    # Zone 4: PRIMARY FLANKING ROW 1 (y = 120, next to Date):
    # Left: Heart Rate (♥ 72, NO "BPM"!)
    hr_val = "72"
    hr_bbox = draw.textbbox((0, 0), hr_val, font=font_metric_val)
    hr_tw = hr_bbox[2] - hr_bbox[0]
    hr_total_w = icon_hr.width + int(3 * scale) + hr_tw
    hr_start_x = flank_left_cx - hr_total_w // 2

    img.paste(icon_hr, (int(hr_start_x), int(120 * scale) - icon_hr.height // 2), icon_hr)
    draw.text((hr_start_x + icon_hr.width + int(3 * scale), int(120 * scale)), hr_val, fill=(245, 248, 252, 245), font=font_metric_val, anchor="lm")

    # Right: Battery (🔋 82%, SWAPPED with Steps!)
    batt_val = "82%"
    batt_bbox = draw.textbbox((0, 0), batt_val, font=font_metric_val)
    batt_tw = batt_bbox[2] - batt_bbox[0]
    batt_total_w = icon_batt.width + int(3 * scale) + batt_tw
    batt_start_x = flank_right_cx - batt_total_w // 2

    img.paste(icon_batt, (int(batt_start_x), int(120 * scale) - icon_batt.height // 2), icon_batt)
    draw.text((batt_start_x + icon_batt.width + int(3 * scale), int(120 * scale)), batt_val, fill=(0, 240, 125, 245), font=font_metric_val, anchor="lm")

    # Zone 5: SECONDARY FLANKING ROW 2 (Additional Garmin Metrics at y = 148):
    # Left: Calories (🔥 540)
    cal_val = "540"
    cal_bbox = draw.textbbox((0, 0), cal_val, font=font_metric_val)
    cal_tw = cal_bbox[2] - cal_bbox[0]
    cal_total_w = icon_flame.width + int(3 * scale) + cal_tw
    cal_start_x = flank_left_cx - cal_total_w // 2

    img.paste(icon_flame, (int(cal_start_x), int(148 * scale) - icon_flame.height // 2), icon_flame)
    draw.text((cal_start_x + icon_flame.width + int(3 * scale), int(148 * scale)), cal_val, fill=(255, 145, 40, 245), font=font_metric_val, anchor="lm")

    # Right: Weather Temp (🌤 21°)
    temp_val = "21°"
    temp_bbox = draw.textbbox((0, 0), temp_val, font=font_metric_val)
    temp_tw = temp_bbox[2] - temp_bbox[0]
    temp_total_w = icon_temp.width + int(3 * scale) + temp_tw
    temp_start_x = flank_right_cx - temp_total_w // 2

    img.paste(icon_temp, (int(temp_start_x), int(148 * scale) - icon_temp.height // 2), icon_temp)
    draw.text((temp_start_x + icon_temp.width + int(3 * scale), int(148 * scale)), temp_val, fill=(255, 215, 65, 245), font=font_metric_val, anchor="lm")

    # Zone 6: BOTTOM COMPLICATION: STEPS (y = 178, centered at X = 120)
    step_val = "8,450"
    st_bbox = draw.textbbox((0, 0), step_val, font=font_step_val)
    stw = st_bbox[2] - st_bbox[0]
    step_total_w = icon_steps.width + int(4 * scale) + stw
    step_start_x = CX - step_total_w // 2

    img.paste(icon_steps, (int(step_start_x), int(178 * scale) - icon_steps.height // 2), icon_steps)
    draw.text((step_start_x + icon_steps.width + int(4 * scale), int(178 * scale)), step_val, fill=(0, 235, 255, 245), font=font_step_val, anchor="lm")

    # Zone 7: BOTTOM RIM: DISTANCE (y = 202)
    draw.text((CX, int(202 * scale)), "5.2 KM", fill=(140, 150, 165, 200), font=font_sub_dist, anchor="mm")

    return img

# Render Native Smallest Resolution (240x240)
dial_240 = render_fluida(scale=1.0)
out_240 = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/mockup_fluida_dial_240.png"
dial_240.save(out_240)
print("Native 240x240 Dial saved to:", out_240)

# Render High-DPI Inspection Version (960x960, exactly 4x scale for crisp visual inspection)
dial_960 = render_fluida(scale=4.0)
out_960 = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/mockup_fluida_dial_240_inspected_4x.png"
dial_960.save(out_960)
print("Inspected 4x (960x960) Dial saved to:", out_960)

# Also composite onto the flat top-down luxury watch case at exact scale!
case_path = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/topdown_watch_case_base_1792042183938.jpg"
case_base = Image.open(case_path).convert("RGBA")
case_dial_size = 332
dial_for_case = dial_960.resize((case_dial_size, case_dial_size), Image.Resampling.LANCZOS)

mask = Image.new("L", (case_dial_size, case_dial_size), 0)
md = ImageDraw.Draw(mask)
md.ellipse((0, 0, case_dial_size, case_dial_size), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1))

paste_pos = (510 - case_dial_size // 2, 507 - case_dial_size // 2)
case_base.paste(dial_for_case, paste_pos, mask)

out_case = "/Users/vivek/.gemini/antigravity/brain/3cc45044-09c4-4018-adaa-b22bac9ef4bc/mockup_fluida_watch_240_scale.jpg"
case_base.convert("RGB").save(out_case, quality=98)
print("Watch Mockup with 240-scale Dial saved to:", out_case)

