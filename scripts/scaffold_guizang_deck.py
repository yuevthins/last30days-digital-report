#!/usr/bin/env python3
"""Scaffold a Guizang-style horizontal HTML deck from bundled assets."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
TEMPLATE = SKILL_ROOT / "assets" / "guizang-ppt" / "template.html"
MOTION = SKILL_ROOT / "assets" / "guizang-ppt" / "motion.min.js"

THEMES = {
    "ink": {
        "label": "墨水经典",
        "vars": {
            "ink": "#0a0a0b",
            "ink-rgb": "10,10,11",
            "paper": "#f1efea",
            "paper-rgb": "241,239,234",
            "paper-tint": "#e8e5de",
            "ink-tint": "#18181a",
        },
    },
    "indigo": {
        "label": "靛蓝瓷",
        "vars": {
            "ink": "#0a1f3d",
            "ink-rgb": "10,31,61",
            "paper": "#f1f3f5",
            "paper-rgb": "241,243,245",
            "paper-tint": "#e4e8ec",
            "ink-tint": "#152a4a",
        },
    },
    "forest": {
        "label": "森林墨",
        "vars": {
            "ink": "#1a2e1f",
            "ink-rgb": "26,46,31",
            "paper": "#f5f1e8",
            "paper-rgb": "245,241,232",
            "paper-tint": "#ece7da",
            "ink-tint": "#253d2c",
        },
    },
    "kraft": {
        "label": "牛皮纸",
        "vars": {
            "ink": "#2a1e13",
            "ink-rgb": "42,30,19",
            "paper": "#eedfc7",
            "paper-rgb": "238,223,199",
            "paper-tint": "#e0d0b6",
            "ink-tint": "#3a2a1d",
        },
    },
    "dune": {
        "label": "沙丘",
        "vars": {
            "ink": "#1f1a14",
            "ink-rgb": "31,26,20",
            "paper": "#f0e6d2",
            "paper-rgb": "240,230,210",
            "paper-tint": "#e3d7bf",
            "ink-tint": "#2d2620",
        },
    },
}


def output_path(value: Path) -> Path:
    if value.suffix.lower() == ".html":
        return value
    return value / "index.html"


def apply_theme(html: str, theme_id: str) -> str:
    theme = THEMES[theme_id]["vars"]
    replacement = "\n".join(
        [
            f"    --ink:{theme['ink']};",
            f"    --ink-rgb:{theme['ink-rgb']};",
            f"    --paper:{theme['paper']};",
            f"    --paper-rgb:{theme['paper-rgb']};",
            f"    --paper-tint:{theme['paper-tint']};",
            f"    --ink-tint:{theme['ink-tint']};",
        ]
    )
    pattern = re.compile(
        r"    --ink:#[0-9a-fA-F]+;\n"
        r"    --ink-rgb:[0-9,\s]+;\n"
        r"    --paper:#[0-9a-fA-F]+;\n"
        r"    --paper-rgb:[0-9,\s]+;\n"
        r"    --paper-tint:#[0-9a-fA-F]+;\n"
        r"    --ink-tint:#[0-9a-fA-F]+;"
    )
    themed, count = pattern.subn(replacement, html, count=1)
    if count != 1:
        raise SystemExit("ERROR: could not locate the Guizang theme variable block in template.html")
    return themed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Output .html path or deck directory.")
    parser.add_argument("--title", required=True, help="HTML title for the deck.")
    parser.add_argument("--theme", default="ink", choices=sorted(THEMES), help="Bundled Guizang theme preset.")
    parser.add_argument("--no-images-dir", action="store_true", help="Do not create an images/ directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not TEMPLATE.exists():
        raise SystemExit(f"ERROR: missing template asset: {TEMPLATE}")
    if not MOTION.exists():
        raise SystemExit(f"ERROR: missing motion asset: {MOTION}")

    out = output_path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    assets_dir = out.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    if not args.no_images_dir:
        (out.parent / "images").mkdir(parents=True, exist_ok=True)

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("[必填] 替换为 PPT 标题 · Deck Title", args.title)
    html = apply_theme(html, args.theme)
    out.write_text(html, encoding="utf-8")
    shutil.copy2(MOTION, assets_dir / "motion.min.js")

    print(f"wrote: {out}")
    print(f"copied: {assets_dir / 'motion.min.js'}")
    if not args.no_images_dir:
        print(f"created: {out.parent / 'images'}")
    print(f"theme: {THEMES[args.theme]['label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
