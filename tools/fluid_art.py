"""Volumetric column used by the plate reservoirs and the live fluid sprites.

The shading is the mockup's cylinder: dark edges, a bright core, and a
specular streak. The sprite keeps the meniscus at the top so the watch can
slide it to the current fill.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image

from layout import MENISCUS, at, bore_box, sight_box

HOUR = ((0, 25, 95), (35, 145, 255), (190, 230, 255))
MINUTE = ((0, 55, 65), (30, 240, 225), (210, 255, 250))


def shade(x: int, width: int, deep: tuple[int, int, int], core: tuple[int, int, int], glint: tuple[int, int, int]) -> tuple[int, int, int]:
    span = max(1, width - 1)
    t = x / span
    curve = math.sin(t * math.pi)
    color = [int(deep[i] * (1 - curve) + core[i] * curve) for i in range(3)]
    distance = abs(t - 0.22)
    if distance < 0.10:
        mix = (1 - distance / 0.10) ** 2
        color = [int(color[i] * (1 - mix) + glint[i] * mix) for i in range(3)]
    return color[0], color[1], color[2]


def paint_volume(image: Image.Image, box: tuple[int, int, int, int], palette: tuple) -> None:
    left, top, right, bottom = box
    width = right - left
    if width < 2 or bottom <= top:
        return
    deep, core, glint = palette
    for x in range(width):
        color = shade(x, width, deep, core, glint) + (255,)
        for y in range(top, bottom):
            image.putpixel((left + x, y), color)
    meniscus = top + max(1, (bottom - top) // 5)
    for x in range(1, width - 1):
        image.putpixel((left + x, meniscus), glint + (255,))


def render_sprite(size: int, palette: tuple) -> Image.Image:
    _left, top, right, bottom = bore_box(size, "hour")
    width = right - _left
    body = bottom - top
    meniscus = max(3, at(size, MENISCUS))
    deep, core, glint = palette
    bore = (12, 16, 22, 255)
    image = Image.new("RGBA", (width, body + meniscus), bore)
    for x in range(width):
        color = shade(x, width, deep, core, glint) + (255,)
        for y in range(meniscus, meniscus + body):
            image.putpixel((x, y), color)
    radius_x = max(1, width / 2)
    center = (width - 1) / 2
    for y in range(meniscus):
        for x in range(width):
            nx = (x - center) / radius_x
            ny = (y - meniscus) / meniscus
            if nx * nx + ny * ny > 1:
                continue
            if y < meniscus * 0.35:
                image.putpixel((x, y), (255, 255, 255, 255))
            elif y < meniscus * 0.6:
                image.putpixel((x, y), glint + (255,))
            else:
                image.putpixel((x, y), core + (255,))
    return image


def render_sight(size: int, side: str, palette: tuple) -> Image.Image:
    left, top, right, bottom = sight_box(size, side)
    image = Image.new("RGBA", (max(1, right - left), max(1, bottom - top)), (12, 16, 22, 255))
    paint_volume(image, (0, 0, image.width, image.height), palette)
    return image


def write_sprites(size: int, folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    render_sprite(size, HOUR).save(folder / "fluid_hour.png")
    render_sprite(size, MINUTE).save(folder / "fluid_minute.png")
    render_sight(size, "hour", HOUR).save(folder / "fluid_sight_hour.png")
    render_sight(size, "minute", MINUTE).save(folder / "fluid_sight_minute.png")
