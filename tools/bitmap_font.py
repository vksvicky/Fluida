"""Write a Connect IQ bitmap font in the same text format Lunara uses."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
CHARSET = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ%°,:-"


def write_font(
    size: int,
    fnt_path: Path,
    png_path: Path,
    bold: bool = True,
    charset: str = CHARSET,
) -> None:
    face = ImageFont.truetype(ARIAL_BOLD if bold else ARIAL, size)
    ascent, descent = face.getmetrics()
    glyphs = []
    for char in charset:
        if char == " ":
            advance = max(2, int(round(face.getlength(" "))))
            glyphs.append((ord(char), None, 0, 0, 0, 0, advance))
            continue
        bbox = face.getbbox(char)
        width = max(1, bbox[2] - bbox[0])
        height = max(1, bbox[3] - bbox[1])
        plate = Image.new("L", (width, height), 0)
        ImageDraw.Draw(plate).text((-bbox[0], -bbox[1]), char, font=face, fill=255)
        glyphs.append((ord(char), plate, width, height, 0, max(0, bbox[1]), max(width, int(round(face.getlength(char))))))

    line_height = ascent + descent
    x = 1
    y = 1
    row_h = 1
    placed = []
    for item in glyphs:
        code, plate, width, height, xoff, yoff, advance = item
        if plate is None:
            placed.append((code, 1, 1, 0, 0, 0, 0, advance))
            continue
        if x + width + 1 > 512:
            x = 1
            y += row_h + 1
            row_h = 1
        placed.append((code, x, y, width, height, xoff, yoff, advance))
        row_h = max(row_h, height)
        x += width + 1

    used_w = 2
    used_h = 2
    for _code, gx, gy, width, height, _xoff, _yoff, _advance in placed:
        used_w = max(used_w, gx + width + 1)
        used_h = max(used_h, gy + height + 1)
    sheet = Image.new("RGBA", (used_w, used_h), (255, 255, 255, 0))
    for code, gx, gy, width, height, _xoff, _yoff, _advance in placed:
        if width == 0:
            continue
        plate = next(item[1] for item in glyphs if item[0] == code)
        for py in range(height):
            for px in range(width):
                if plate.getpixel((px, py)) > 128:
                    sheet.putpixel((gx + px, gy + py), (255, 255, 255, 255))

    png_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(png_path)
    lines = [
        f'info face="Fluida" size={size} bold={1 if bold else 0} italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=0 padding=0,0,0,0 spacing=1,1 outline=0',
        f"common lineHeight={line_height} base={ascent} scaleW={sheet.width} scaleH={sheet.height} pages=1 packed=0 alphaChnl=0 redChnl=0 greenChnl=0 blueChnl=0",
        f'page id=0 file="{png_path.name}"',
        f"chars count={len(placed)}",
    ]
    for code, gx, gy, width, height, xoff, yoff, advance in placed:
        lines.append(
            f"char id={code:<4} x={gx:<4} y={gy:<4} width={width:<4} height={height:<4} "
            f"xoffset={xoff:<3} yoffset={yoff:<3} xadvance={advance:<3} page=0 chnl=15"
        )
    fnt_path.write_text("\n".join(lines) + "\n")
