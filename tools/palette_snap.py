"""Snap watch bitmaps to a fixed palette, the same way Lunara keeps the moons smooth.

A photographic PNG has thousands of nearby colors. Connect IQ then
Floyd-Steinberg dithers them onto the MIP screen, which is the grain.
Nearest-color snapping plus an explicit resource palette leaves solid areas solid.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SIZES = (240, 260, 280, 360, 390, 416, 454)
COLOR_BUDGET = {
    "fluid_hour": 16,
    "fluid_minute": 16,
    "fluid_sight_hour": 12,
    "fluid_sight_minute": 12,
    "icon_heart": 8,
    "icon_battery": 8,
    "icon_flame": 8,
    "icon_temp": 8,
    "icon_steps": 8,
}


def quantize_dial(image: Image.Image, count: int = 128) -> tuple[Image.Image, list[tuple[int, int, int]]]:
    """Nearest-color reduction that keeps the picture's own blues and cyans.

    Thirty-two colors mixed the two fluids into green. A 128-color median cut
    does not, and the watch then has no leftover shades to dither into speckle.
    """
    rgba = image.convert("RGBA")
    flat = Image.new("RGB", rgba.size, (0, 0, 0))
    flat.paste(rgba, mask=rgba.getchannel("A"))
    reduced = flat.quantize(colors=count, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    raw = reduced.getpalette() or []
    palette: list[tuple[int, int, int]] = []
    for _uses, index in reduced.getcolors() or []:
        color = (raw[index * 3], raw[index * 3 + 1], raw[index * 3 + 2])
        if color not in palette:
            palette.append(color)
    if (0, 0, 0) not in palette:
        palette.insert(0, (0, 0, 0))
    snapped = snap_image(reduced.convert("RGBA"), palette)
    source = rgba.load()
    pixels = snapped.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if source[x, y][3] < 16:
                pixels[x, y] = (0, 0, 0, 0)
    return snapped, palette


def build_palette(image: Image.Image, count: int) -> list[tuple[int, int, int]]:
    """Colors actually used after a nearest-color reduction. No error diffusion."""
    opaque = image.convert("RGBA")
    rgb = Image.new("RGB", opaque.size, (0, 0, 0))
    rgb.paste(opaque, mask=opaque.getchannel("A"))
    reduced = rgb.quantize(colors=count, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    raw = reduced.getpalette() or []
    found: list[tuple[int, int, int]] = []
    for _uses, index in reduced.getcolors() or []:
        color = (raw[index * 3], raw[index * 3 + 1], raw[index * 3 + 2])
        if color not in found:
            found.append(color)
    return found


def snap_image(image: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    """Map every opaque pixel to the nearest palette color. Clear pixels stay clear."""
    source = image.convert("RGBA")
    out = source.copy()
    pixels = out.load()
    width, height = out.size
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 16:
                pixels[x, y] = (0, 0, 0, 0)
                continue
            best = palette[0]
            best_distance = 1_000_000
            for color in palette:
                distance = (red - color[0]) ** 2 + (green - color[1]) ** 2 + (blue - color[2]) ** 2
                if distance < best_distance:
                    best = color
                    best_distance = distance
                    if distance == 0:
                        break
            pixels[x, y] = (best[0], best[1], best[2], 255)
    return out


def palette_block(bitmap_id: str, filename: str, palette: list[tuple[int, int, int]]) -> str:
    colors = "\n".join(f"            <color>{red:02X}{green:02X}{blue:02X}</color>" for red, green, blue in palette)
    return (
        f'    <bitmap id="{bitmap_id}" filename="{filename}" dithering="none">\n'
        f"        <palette>\n{colors}\n        </palette>\n"
        f"    </bitmap>"
    )


def lock_dial(folder: Path) -> None:
    """Replace only the dial bitmap. The other icons stay as drawn."""
    path = folder / "dial_bg.png"
    xml_path = folder / "drawables.xml"
    if not path.exists() or not xml_path.exists():
        return
    image, palette = quantize_dial(Image.open(path))
    image.save(path)
    block = palette_block("dial_bg", "dial_bg.png", palette)
    text = xml_path.read_text()
    import re
    updated, replacements = re.subn(
        r'    <bitmap id="dial_bg".*?</bitmap>|    <bitmap id="dial_bg"[^>]*/>',
        block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if replacements != 1:
        raise RuntimeError(f"dial_bg entry missing in {xml_path}")
    xml_path.write_text(updated)


def snap_folder(folder: Path) -> None:
    blocks = ["<drawables>"]
    for name, count in COLOR_BUDGET.items():
        path = folder / f"{name}.png"
        if not path.exists():
            continue
        image = Image.open(path)
        palette = build_palette(image, count)
        snap_image(image, palette).save(path)
        blocks.append(palette_block(name, path.name, palette))
    blocks.append("</drawables>\n")
    (folder / "drawables.xml").write_text("\n".join(blocks))


def main() -> None:
    for size in SIZES:
        folder = ROOT / f"resources-round-{size}x{size}" / "drawables"
        if folder.is_dir():
            lock_dial(folder)
            print(f"dial {size}")


if __name__ == "__main__":
    main()
