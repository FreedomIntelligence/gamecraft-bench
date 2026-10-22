#!/usr/bin/env python3
"""Create a labeled contact sheet from candidate raster game assets."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover - clear runtime guidance
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def discover(inputs: list[Path], recursive: bool) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        if item.is_file() and item.suffix.lower() in RASTER_EXTENSIONS:
            files.append(item)
        elif item.is_dir():
            iterator = item.rglob("*") if recursive else item.glob("*")
            files.extend(path for path in iterator if path.is_file() and path.suffix.lower() in RASTER_EXTENSIONS)
    return sorted(set(path.resolve() for path in files), key=lambda path: str(path).lower())


def checkerboard(size: tuple[int, int], square: int = 12) -> Image.Image:
    image = Image.new("RGB", size, "#252932")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2 == 0:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill="#343945")
    return image


def shorten(value: str, maximum: int) -> str:
    return value if len(value) <= maximum else value[: maximum - 1] + "…"


def build_sheet(
    paths: list[Path], output: Path, columns: int, thumb: int, label_height: int, background: str
) -> tuple[int, int]:
    rows = math.ceil(len(paths) / columns)
    cell_width = thumb + 20
    cell_height = thumb + label_height + 20
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), background)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, path in enumerate(paths):
        column = index % columns
        row = index // columns
        x0 = column * cell_width
        y0 = row * cell_height
        board = checkerboard((thumb, thumb))
        try:
            with Image.open(path) as source:
                source.seek(0)
                image = source.convert("RGBA")
                image = ImageOps.contain(image, (thumb - 12, thumb - 12), Image.Resampling.LANCZOS)
                px = (thumb - image.width) // 2
                py = (thumb - image.height) // 2
                board.paste(image, (px, py), image)
        except (OSError, ValueError) as exc:
            draw.rectangle((x0 + 10, y0 + 10, x0 + thumb, y0 + thumb), outline="#d65a5a", width=2)
            draw.text((x0 + 16, y0 + 16), shorten(str(exc), 22), font=font, fill="#ffb4b4")
        else:
            sheet.paste(board, (x0 + 10, y0 + 10))
        label = shorten(path.name, max(12, thumb // 7))
        draw.text((x0 + 10, y0 + thumb + 14), label, font=font, fill="#f0f2f5")

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    return sheet.size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="Raster images or directories")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--columns", type=int, default=6)
    parser.add_argument("--thumb", type=int, default=160)
    parser.add_argument("--label-height", type=int, default=28)
    parser.add_argument("--limit", type=int, default=120)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--background", default="#171a20")
    args = parser.parse_args()

    if args.columns <= 0 or args.thumb < 32 or args.limit <= 0:
        parser.error("columns and limit must be positive; thumb must be at least 32")
    paths = discover([path.expanduser() for path in args.inputs], not args.no_recursive)[: args.limit]
    if not paths:
        print("No supported raster images found.", file=sys.stderr)
        return 1
    output = args.output.expanduser().resolve()
    width, height = build_sheet(paths, output, args.columns, args.thumb, args.label_height, args.background)
    print(f"Wrote {output} with {len(paths)} image(s), {width}x{height}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
