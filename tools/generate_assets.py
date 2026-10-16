"""Build the mockup plate and the face fonts for every round size."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from bitmap_font import write_font
from dial_plate import write_plate
from fluid_art import write_sprites

ICONS = ("icon_heart", "icon_battery", "icon_flame", "icon_temp", "icon_steps")

ROOT = Path(__file__).resolve().parents[1]
SIZES = (240, 260, 280, 360, 390, 416, 454)
MIP_SIZES = (240, 260, 280)

LIVE_FONTS = """<fonts>
    <font id="FaceMetric" filename="face_metric.fnt" antialias="false" />
    <font id="FaceSeconds" filename="face_seconds.fnt" antialias="false" />
    <font id="FaceDate" filename="face_date.fnt" antialias="false" />
    <font id="FaceMonth" filename="face_month.fnt" antialias="false" />
</fonts>
"""

AMOLED_FONTS = """<fonts>
    <font id="FaceMetric" filename="face_metric.fnt" antialias="false" />
    <font id="FaceSeconds" filename="face_seconds.fnt" antialias="false" />
    <font id="FaceDate" filename="face_date.fnt" antialias="false" />
    <font id="FaceMonth" filename="face_month.fnt" antialias="false" />
    <font id="FaceScale" filename="face_scale.fnt" antialias="false" />
</fonts>
"""

def _drawables_xml(include_plate: bool) -> str:
    lines = ["<drawables>"]
    if include_plate:
        lines.append('    <bitmap id="dial_bg" filename="dial_bg.png" dithering="none" />')
    lines.append('    <bitmap id="fluid_hour" filename="fluid_hour.png" dithering="none" />')
    lines.append('    <bitmap id="fluid_minute" filename="fluid_minute.png" dithering="none" />')
    lines.append('    <bitmap id="fluid_sight_hour" filename="fluid_sight_hour.png" dithering="none" />')
    lines.append('    <bitmap id="fluid_sight_minute" filename="fluid_sight_minute.png" dithering="none" />')
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
        if size in MIP_SIZES:
            write_plate(size, folder / "drawables" / "dial_bg.png")
            (folder / "drawables" / "drawables.xml").write_text(_drawables_xml(True))
            (fonts / "fonts.xml").write_text(LIVE_FONTS)
        else:
            write_font(_px(size, 8.5), fonts / "face_scale.fnt", fonts / "face_scale_0.png", charset=DIGITS)
            (fonts / "fonts.xml").write_text(AMOLED_FONTS)
            (folder / "drawables" / "drawables.xml").write_text(_drawables_xml(False))
        print(f"assets {size}")


def _live_fonts(folder: Path, size: int) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    write_font(_px(size, 9.5), folder / "face_metric.fnt", folder / "face_metric_0.png", charset=METRIC)
    write_font(_px(size, 13), folder / "face_seconds.fnt", folder / "face_seconds_0.png", charset=DIGITS)
    write_font(_px(size, 16), folder / "face_date.fnt", folder / "face_date_0.png", charset=DIGITS)
    write_font(_px(size, 7.5), folder / "face_month.fnt", folder / "face_month_0.png", charset=MONTH, bold=False)


def _icons(folder: Path, size: int) -> None:
    """Hard-edged icons. Soft resizes turn into blobs on an 8-bit MIP screen."""
    folder.mkdir(parents=True, exist_ok=True)
    height = max(11, _px(size, 12))
    _stamp(folder / "icon_heart.png", height, _heart, (226, 48, 68))
    _stamp(folder / "icon_battery.png", height, _battery, (0, 210, 110))
    _stamp(folder / "icon_flame.png", height, _flame, (255, 122, 28), (255, 214, 90))
    _stamp(folder / "icon_temp.png", height, _temp, (255, 196, 48))
    _stamp(folder / "icon_steps.png", height, _steps, (0, 214, 230))


def _stamp(path: Path, size: int, painter, color: tuple[int, int, int], core: tuple[int, int, int] | None = None) -> None:
    big = size * 8
    mask = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    painter(ImageDraw.Draw(mask), big, color, core or color)
    small = mask.resize((size, size), Image.Resampling.BOX)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        for x in range(size):
            red, green, blue, alpha = small.getpixel((x, y))
            if alpha >= 110 and max(red, green, blue) >= 24:
                out.putpixel((x, y), (red, green, blue, 255))
    out.save(path)


def _heart(draw: ImageDraw.ImageDraw, n: int, color: tuple[int, int, int], _core: tuple[int, int, int]) -> None:
    radius = int(n * 0.27)
    draw.ellipse((int(n * 0.08), int(n * 0.10), int(n * 0.08) + radius * 2, int(n * 0.10) + radius * 2), fill=color)
    draw.ellipse((int(n * 0.40), int(n * 0.10), int(n * 0.40) + radius * 2, int(n * 0.10) + radius * 2), fill=color)
    draw.polygon([(int(n * 0.06), int(n * 0.36)), (int(n * 0.94), int(n * 0.36)), (n // 2, int(n * 0.94))], fill=color)


def _battery(draw: ImageDraw.ImageDraw, n: int, color: tuple[int, int, int], _core: tuple[int, int, int]) -> None:
    draw.rounded_rectangle((int(n * 0.06), int(n * 0.22), int(n * 0.76), int(n * 0.78)), radius=max(2, n // 10), outline=color, width=max(2, n // 12))
    draw.rectangle((int(n * 0.76), int(n * 0.38), int(n * 0.90), int(n * 0.62)), fill=color)
    draw.rectangle((int(n * 0.16), int(n * 0.34), int(n * 0.58), int(n * 0.66)), fill=color)


def _flame(draw: ImageDraw.ImageDraw, n: int, color: tuple[int, int, int], core: tuple[int, int, int]) -> None:
    draw.polygon(
        [(n // 2, int(n * 0.04)), (int(n * 0.90), int(n * 0.62)), (n // 2, int(n * 0.96)), (int(n * 0.10), int(n * 0.62))],
        fill=color,
    )
    draw.polygon(
        [(n // 2, int(n * 0.42)), (int(n * 0.68), int(n * 0.70)), (n // 2, int(n * 0.92)), (int(n * 0.32), int(n * 0.70))],
        fill=core,
    )


def _temp(draw: ImageDraw.ImageDraw, n: int, color: tuple[int, int, int], _core: tuple[int, int, int]) -> None:
    stem = max(2, n // 6)
    draw.rectangle((n // 2 - stem // 2, int(n * 0.08), n // 2 + stem // 2, int(n * 0.62)), fill=color)
    draw.ellipse((int(n * 0.22), int(n * 0.48), int(n * 0.78), int(n * 0.96)), fill=color)


def _steps(draw: ImageDraw.ImageDraw, n: int, color: tuple[int, int, int], _core: tuple[int, int, int]) -> None:
    draw.ellipse((int(n * 0.08), int(n * 0.18), int(n * 0.48), int(n * 0.78)), fill=color)
    draw.ellipse((int(n * 0.42), int(n * 0.34), int(n * 0.90), int(n * 0.92)), fill=color)


def _px(size: int, basis: float) -> int:
    return max(6, int(round(basis * size / 240)))


if __name__ == "__main__":
    main()
