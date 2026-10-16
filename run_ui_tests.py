#!/usr/bin/env python3
"""Fluida visual regression and layout report.

Draws the spec layout at each round size, checks the well and the two
columns, and writes test_output/visual_report.html.

  python3 run_ui_tests.py
  python3 run_ui_tests.py --device fenix7
  python3 run_ui_tests.py --full
  python3 run_ui_tests.py --update-baselines
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from dial_plate import render_plate  # noqa: E402
from fluid_art import HOUR, MINUTE, render_sprite  # noqa: E402
from layout import MENISCUS, PALETTES, at, bore_box, pixel, scale_span, tube_box, well_center, well_radius  # noqa: E402
from test_ui.image_utils import make_3panel_diff  # noqa: E402
from ui_report import generate_report  # noqa: E402

REPORT_PATH = os.path.join(ROOT, "test_output", "visual_report.html")
BASELINES_DIR = os.path.join(ROOT, "test_output", "baselines")
DIFFS_DIR = os.path.join(ROOT, "test_output", "diffs")

DEVICES = [
    ("fenix7s", 240, "240×240 MIP", "Fenix 7S"),
    ("fenix7", 260, "260×260 MIP", "Fenix 7"),
    ("enduro3", 280, "280×280 MIP", "Enduro 3"),
    ("venu2s", 360, "360×360 AMOLED", "Venu 2S"),
    ("epix2pro42mm", 390, "390×390 AMOLED", "Epix Pro 42mm"),
    ("venu2", 416, "416×416 AMOLED", "Venu 2"),
    ("venu3", 454, "454×454 AMOLED", "Venu 3"),
]

PASSES = [
    {"id": "oceanic", "name": "Dual Oceanic", "palette": 0, "description": "Sapphire hours and emerald minutes."},
    {"id": "ember", "name": "Solar Ember", "palette": 1, "description": "Ruby hours and amber minutes."},
    {"id": "neon", "name": "Cyberpunk Neon", "palette": 2, "description": "Amethyst hours and lime minutes."},
    {"id": "ice", "name": "Glacier Ice", "palette": 3, "description": "Navy hours and ice minutes."},
]
PASS_BY_ID = {item["id"]: item for item in PASSES}


def get_current_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def render_face(size: int, palette: int) -> Image.Image:
    image = render_plate(size).convert("RGB")
    if palette == 0:
        _paste_fluid(image, size, "hour", render_sprite(size, HOUR), (10.58 - 1.0) / 11.0)
        _paste_fluid(image, size, "minute", render_sprite(size, MINUTE), 35.0 / 60.0)
        return image
    hours, minutes, _seconds = PALETTES[palette]
    draw = ImageDraw.Draw(image)
    for side, color in (("hour", hours), ("minute", minutes)):
        left, top, right, bottom = tube_box(size, side)
        fluid = int(round(0.72 * (bottom - top)))
        inset = max(1, at(size, 2))
        draw.rectangle((left + inset, bottom - fluid, right - inset, bottom), fill=color)
    return image


def _paste_fluid(image: Image.Image, size: int, side: str, sprite: Image.Image, fill: float) -> None:
    left, _top, right, bottom = bore_box(size, side)
    span_top, span_bottom = scale_span(size)
    men_y = span_bottom - int(round(fill * (span_bottom - span_top)))
    men_offset = max(3, at(size, MENISCUS))
    draw_top = men_y - men_offset
    clip_h = bottom - draw_top
    if clip_h > 0:
        cropped = sprite.crop((0, 0, right - left, clip_h))
        image.paste(cropped.convert("RGB"), (left, draw_top), cropped)


def annotate(image: Image.Image) -> Image.Image:
    marked = image.copy()
    draw = ImageDraw.Draw(marked)
    size = image.width
    draw.rectangle(tube_box(size, "hour"), outline=(74, 222, 128), width=2)
    draw.rectangle(tube_box(size, "minute"), outline=(74, 222, 128), width=2)
    cx, cy = well_center(size)
    radius = well_radius(size)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(251, 146, 60), width=2)
    band = pixel(size, 0.150)
    draw.ellipse((size // 2 - band, size // 2 - band, size // 2 + band, size // 2 + band), outline=(56, 189, 248), width=2)
    return marked


def validate(image: Image.Image, palette: int) -> list[str]:
    issues = []
    size = image.width
    if image.getpixel((1, 1)) != (0, 0, 0):
        issues.append("FIELD: a corner pixel is lit outside the dial.")
    cx, cy = well_center(size)
    ring = image.getpixel((cx, cy))
    if sum(ring) > 180:
        issues.append("SECONDS: the ring center is not the dark dial.")
    hours, minutes, _seconds = PALETTES[palette]
    hx = (tube_box(size, "hour")[0] + tube_box(size, "hour")[2]) // 2
    hy = tube_box(size, "hour")[3] - max(4, size // 40)
    mx = (tube_box(size, "minute")[0] + tube_box(size, "minute")[2]) // 2
    if palette == 0:
        hour = image.getpixel((hx, hy))
        minute = image.getpixel((mx, hy))
        edge = image.getpixel((bore_box(size, "hour")[0], hy))
        if hour[2] < 140 or hour[2] < edge[2]:
            issues.append("HOUR: the column is not the volumetric sapphire core.")
        if minute[1] < 140:
            issues.append("MINUTE: the column is not the volumetric mint core.")
    else:
        if image.getpixel((hx, hy)) != hours:
            issues.append("HOUR: the left column is not the palette hour color.")
        if image.getpixel((mx, hy)) != minutes:
            issues.append("MINUTE: the right column is not the palette minute color.")
    return issues


def selected_passes(full_mode: bool) -> list[dict]:
    if full_mode:
        return list(PASSES)
    return [PASS_BY_ID["oceanic"], PASS_BY_ID["ember"]]


def run_device(dev_id, size, output_dir, full_mode) -> list[dict]:
    results = []
    for spec in selected_passes(full_mode):
        print(f"  [{spec['id']}] {spec['name']}")
        image = render_face(size, spec["palette"])
        issues = validate(image, spec["palette"])
        img_path = os.path.join(output_dir, f"{dev_id}_{spec['id']}.png")
        zones_path = os.path.join(output_dir, f"{dev_id}_{spec['id']}_zones.png")
        image.save(img_path)
        annotate(image).save(zones_path)
        results.append({
            "id": spec["id"],
            "pass_name": spec["name"],
            "description": spec["description"],
            "current_img": img_path,
            "zones_img": zones_path,
            "passed": not issues,
            "issues": issues,
            "slots": [f"Palette: {spec['name']}", f"Screen: {size}px"],
        })
    return results


def process_result_baseline(result, dev_id, update_baselines=False):
    pass_id = result["id"]
    img_path = result.get("current_img")
    base_path = os.path.join(BASELINES_DIR, f"{dev_id}_{pass_id}.png")
    diff_path = os.path.join(DIFFS_DIR, f"{dev_id}_{pass_id}.png")
    if update_baselines:
        if img_path and os.path.exists(img_path) and result.get("passed", False):
            os.makedirs(BASELINES_DIR, exist_ok=True)
            shutil.copy2(img_path, base_path)
            print(f"    [BASELINE SAVED] {os.path.basename(base_path)}")
            result["has_baseline"] = True
            result["baseline_img"] = base_path
            result["diff_img"] = None
            result["diff_pct"] = 0.0
        else:
            reasons = ", ".join(result.get("issues", [])) or "layout validation failed"
            print(f"    [BASELINE FAILED] {dev_id}_{pass_id}: {reasons}")
            result["has_baseline"] = False
            result["passed"] = False
            result["issues"] = list(result.get("issues", [])) + [f"CAPTURE FAILED: {reasons}"]
        return result

    has_baseline = os.path.exists(base_path)
    result["has_baseline"] = has_baseline
    result["baseline_img"] = base_path if has_baseline else None
    result["issues"] = list(result.get("issues", []))
    if not has_baseline:
        result["issues"].insert(0, f"MISSING BASELINE: {base_path}. Run ./run_tests.sh ui --update-baselines")
        result["passed"] = False
        result["diff_img"] = None
        result["diff_pct"] = None
        return result
    diff = make_3panel_diff(base_path, img_path, diff_path)
    result["diff_img"] = diff.get("composite_path")
    result["diff_pct"] = diff.get("diff_pct")
    if diff.get("diff_pct") is not None and diff["diff_pct"] > 5.0:
        result["issues"].append(f"VISUAL REGRESSION: {diff['diff_pct']:.2f}% pixel variance from baseline.")
        result["passed"] = False
    return result


def backup_baselines() -> None:
    if not os.path.isdir(BASELINES_DIR) or not os.listdir(BASELINES_DIR):
        return
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(ROOT, "test_output", f"baselines_backup_{stamp}")
    shutil.copytree(BASELINES_DIR, dest)
    print(f"Backed up baselines to {dest}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fluida visual regression report")
    parser.add_argument("--device", action="append", default=[])
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--update-baselines", action="store_true")
    args = parser.parse_args()
    os.chdir(ROOT)
    chosen = [item for item in DEVICES if not args.device or item[0] in args.device]
    if args.device and len(chosen) != len(args.device):
        known = ", ".join(item[0] for item in DEVICES)
        print(f"Unknown device. Choose from: {known}")
        return 2
    if args.update_baselines:
        backup_baselines()
    output_dir = os.path.join(ROOT, "test_output", "current")
    os.makedirs(output_dir, exist_ok=True)
    all_results = []
    failures = 0
    for dev_id, size, res_info, dev_name in chosen:
        print(f"\n{dev_name} ({dev_id}, {res_info})")
        raw = run_device(dev_id, size, output_dir, args.full)
        processed = [process_result_baseline(item, dev_id, args.update_baselines) for item in raw]
        failures += sum(1 for item in processed if not item.get("passed"))
        all_results.append((dev_id, res_info, dev_name, processed))
    generate_report(all_results, get_current_branch(), REPORT_PATH, ROOT, args.update_baselines)
    print(f"Failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
