"""Photorealistic 3D liquid columns and concave meniscus cups built directly
from the studio master tube assets (`tube_blue_col.png`, `tube_blue_men.png`,
`tube_cyan_col.png`, `tube_cyan_men.png`).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from layout import MENISCUS, at, bore_box

MASTER_DIR = Path(__file__).resolve().parent / "master_art"

HOUR = "hour"
MINUTE = "minute"


def _build_master_sprite(kind: str) -> Image.Image:
    """Compose the 60x290 master 3D fluid column + 3D concave meniscus cup."""
    empty_col = Image.open(MASTER_DIR / "tube_empty_col.png").convert("RGBA")
    if kind == HOUR or (isinstance(kind, tuple) and kind[0][2] > kind[0][1]):
        col = Image.open(MASTER_DIR / "tube_blue_col.png").convert("RGBA")
        men = Image.open(MASTER_DIR / "tube_blue_men.png").convert("RGBA")
        men_y = 0
    else:
        col = Image.open(MASTER_DIR / "tube_cyan_col.png").convert("RGBA")
        men = Image.open(MASTER_DIR / "tube_cyan_men.png").convert("RGBA")
        men_y = 6

    w, body_h = col.size
    men_offset = 12
    master = Image.new("RGBA", (w, body_h + men_offset), (14, 18, 24, 255))
    # Fill top meniscus background with the 3D smoky borosilicate glass wall
    master.paste(empty_col.crop((0, 0, w, men_offset + 24)), (0, 0))
    # Paste the 3D volumetric liquid column starting at y = men_offset (reading line)
    master.paste(col, (0, men_offset), col)
    # Alpha-composite the 3D concave meniscus cup
    master.alpha_composite(men, (0, men_y))
    return master


def render_sprite(size: int, palette) -> Image.Image:
    """Scale the photorealistic 3D fluid column + meniscus to the target bore size."""
    left, top, right, bottom = bore_box(size, "hour")
    width = max(1, right - left)
    body = max(1, bottom - top)
    meniscus = max(3, at(size, MENISCUS))
    master = _build_master_sprite(palette)
    return master.resize((width, body + meniscus), Image.Resampling.LANCZOS)


def write_sprites(size: int, folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    render_sprite(size, HOUR).save(folder / "fluid_hour.png")
    render_sprite(size, MINUTE).save(folder / "fluid_minute.png")
