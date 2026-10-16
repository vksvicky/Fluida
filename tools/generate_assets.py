"""Build the photorealistic 3D plate, fluid sprites, icons, and fonts for every round size."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from bitmap_font import write_font
from dial_plate import write_plate
from fluid_art import write_sprites

ICONS = ("icon_heart", "icon_battery", "icon_flame", "icon_temp", "icon_steps")

ROOT = Path(__file__).resolve().parents[1]
SIZES = (240, 260, 280, 360, 390, 416, 454)

LIVE_FONTS = """<fonts>
    <font id="FaceMetric" filename="face_metric.fnt" antialias="false" />
    <font id="FaceSteps" filename="face_steps.fnt" antialias="false" />
    <font id="FaceSeconds" filename="face_seconds.fnt" antialias="false" />
    <font id="FaceDate" filename="face_date.fnt" antialias="false" />
    <font id="FaceMonth" filename="face_month.fnt" antialias="false" />
</fonts>
"""


def _drawables_xml() -> str:
    lines = [
        "<drawables>",
        '    <bitmap id="dial_bg" filename="dial_bg.png" />',
        '    <bitmap id="fluid_hour" filename="fluid_hour.png" />',
        '    <bitmap id="fluid_minute" filename="fluid_minute.png" />',
    ]
    for icon_id in ICONS:
        lines.append(f'    <bitmap id="{icon_id}" filename="{icon_id}.png" dithering="none" />')
    lines.append("</drawables>\n")
    return "\n".join(lines)


DIGITS = "0123456789"
METRIC = "0123456789,%°-"
MONTH = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def main() -> None:
    for size in SIZES:
        folder = ROOT / f"resources-round-{size}x{size}"
        fonts = folder / "fonts"
        _live_fonts(fonts, size)
        _icons(folder / "drawables", size)
        write_sprites(size, folder / "drawables")
        write_plate(size, folder / "drawables" / "dial_bg.png")
        (folder / "drawables" / "drawables.xml").write_text(_drawables_xml())
        (fonts / "fonts.xml").write_text(LIVE_FONTS)
        print(f"assets {size}")


def _live_fonts(folder: Path, size: int) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    write_font(_px(size, 9.0), folder / "face_metric.fnt", folder / "face_metric_0.png", charset=METRIC, bold=True)
    write_font(_px(size, 10.5), folder / "face_steps.fnt", folder / "face_steps_0.png", charset=METRIC, bold=True)
    write_font(_px(size, 14.5), folder / "face_seconds.fnt", folder / "face_seconds_0.png", charset=DIGITS, bold=True)
    write_font(_px(size, 13.5), folder / "face_date.fnt", folder / "face_date_0.png", charset=DIGITS, bold=True)
    write_font(_px(size, 7.0), folder / "face_month.fnt", folder / "face_month_0.png", charset=MONTH, bold=False)


def _icons(folder: Path, size: int) -> None:
    """Crisp horological icons matching the master luxury mockup."""
    folder.mkdir(parents=True, exist_ok=True)
    h_std = max(9, _px(size, 9.5))
    h_steps = max(11, _px(size, 11.5))
    _stamp(folder / "icon_heart.png", h_std, h_std, _heart, (255, 45, 75), (255, 45, 75))
    _stamp(folder / "icon_battery.png", max(12, _px(size, 12.0)), max(7, _px(size, 6.8)), _battery, (220, 230, 240), (0, 240, 125))
    _stamp(folder / "icon_flame.png", h_std, h_std, _flame, (255, 145, 40), (255, 220, 60))
    _stamp(folder / "icon_temp.png", h_std, h_std, _temp, (255, 215, 65), (255, 215, 65))
    _stamp(folder / "icon_steps.png", h_steps, h_steps, _steps, (0, 235, 255), (0, 235, 255))


def _stamp(
    path: Path,
    w: int,
    h: int,
    painter,
    color: tuple[int, int, int],
    core: tuple[int, int, int],
) -> None:
    scale = 8
    mask = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    painter(ImageDraw.Draw(mask), w * scale, h * scale, color, core)
    small = mask.resize((w, h), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            red, green, blue, alpha = small.getpixel((x, y))
            if alpha >= 90 and max(red, green, blue) >= 24:
                out.putpixel((x, y), (red, green, blue, 255))
    out.save(path)


def _heart(draw: ImageDraw.ImageDraw, w: int, h: int, color: tuple[int, int, int], _core: tuple[int, int, int]) -> None:
    r = w // 4
    draw.ellipse((0, int(h * 0.06), 2 * r, int(h * 0.06) + 2 * r), fill=color)
    draw.ellipse((w - 2 * r, int(h * 0.06), w, int(h * 0.06) + 2 * r), fill=color)
    draw.polygon([(0, int(h * 0.06) + r + 2), (w, int(h * 0.06) + r + 2), (w // 2, h - 2)], fill=color)


def _battery(draw: ImageDraw.ImageDraw, w: int, h: int, color: tuple[int, int, int], core: tuple[int, int, int]) -> None:
    bw = int(w * 0.86)
    stroke = max(2, int(round(h * 0.12)))
    draw.rounded_rectangle((0, 0, bw, h - 1), radius=max(2, h // 5), outline=color, width=stroke)
    draw.rounded_rectangle((bw, h // 4, w - 1, (3 * h) // 4), radius=max(1, h // 8), fill=color)
    pad = max(2, int(round(h * 0.20)))
    inner_w = int((bw - 2 * pad) * 0.78)
    draw.rounded_rectangle((pad, pad, pad + inner_w, h - 1 - pad), radius=max(1, h // 8), fill=core)


def _flame(draw: ImageDraw.ImageDraw, w: int, h: int, color: tuple[int, int, int], core: tuple[int, int, int]) -> None:
    pts = [
        (w // 2, 0),
        (int(w * 0.75), int(h * 0.35)),
        (w - 1, int(h * 0.65)),
        (int(w * 0.65), h - 1),
        (int(w * 0.35), h - 1),
        (0, int(h * 0.65)),
        (int(w * 0.25), int(h * 0.50)),
    ]
    draw.polygon(pts, fill=color)
    in_pts = [
        (w // 2, int(h * 0.35)),
        (int(w * 0.60), int(h * 0.60)),
        (w // 2, int(h * 0.88)),
        (int(w * 0.40), int(h * 0.60)),
    ]
    draw.polygon(in_pts, fill=core)


def _temp(draw: ImageDraw.ImageDraw, w: int, h: int, color: tuple[int, int, int], _core: tuple[int, int, int]) -> None:
    c = w // 2
    r = w // 4
    draw.ellipse((c - r, c - r, c + r, c + r), fill=color)
    for i in range(8):
        ang = i * math.pi / 4.0
        x1 = c + int((r + 2) * math.cos(ang))
        y1 = c + int((r + 2) * math.sin(ang))
        x2 = c + int((r + 5) * math.cos(ang))
        y2 = c + int((r + 5) * math.sin(ang))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)


def _steps(draw: ImageDraw.ImageDraw, w: int, h: int, color: tuple[int, int, int], _core: tuple[int, int, int]) -> None:
    draw.ellipse((int(w * 0.15), int(h * 0.45), int(w * 0.40), int(h * 0.90)), fill=color)
    draw.ellipse((int(w * 0.18), int(h * 0.20), int(w * 0.38), int(h * 0.42)), fill=color)
    draw.ellipse((int(w * 0.60), int(h * 0.15), int(w * 0.85), int(h * 0.60)), fill=color)
    draw.ellipse((int(w * 0.62), int(h * 0.62), int(w * 0.82), int(h * 0.85)), fill=color)


def _px(size: int, basis: float) -> int:
    return max(6, int(round(basis * size / 240.0)))


if __name__ == "__main__":
    main()
