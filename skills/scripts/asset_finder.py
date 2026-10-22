#!/usr/bin/env python3
"""Search mounted game-asset libraries by semantic path tokens and file type."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


KINDS = {
    "image": {".png", ".jpg", ".jpeg", ".webp", ".svg"},
    "font": {".ttf", ".otf", ".woff", ".woff2"},
    "audio": {".wav", ".ogg", ".mp3", ".flac"},
    "data": {".json", ".xml", ".csv", ".tsx", ".tmx", ".tres", ".tscn"},
}
ALL_EXTENSIONS = set().union(*KINDS.values())
LICENSE_PATTERN = re.compile(r"(?i)^(license|copying|attribution|credits)(\..*)?$")


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    for kind, extensions in KINDS.items():
        if suffix in extensions:
            return kind
    return "other"


def tokenize(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", value.lower()) if token}


def score_path(path: Path, terms: list[str]) -> tuple[float, set[str]]:
    lower = str(path).lower()
    tokens = tokenize(lower)
    matched: set[str] = set()
    score = 0.0
    for term in terms:
        if term in tokens:
            score += 4.0
            matched.add(term)
        elif term in lower:
            score += 2.0
            matched.add(term)
        elif any(token.startswith(term) or term.startswith(token) for token in tokens if len(token) >= 3):
            score += 0.75
            matched.add(term)
    return score, matched


def nearest_license(path: Path, root: Path) -> Path | None:
    current = path.parent
    while True:
        try:
            entries = list(current.iterdir())
        except OSError:
            entries = []
        for entry in entries:
            if entry.is_file() and LICENSE_PATTERN.match(entry.name):
                return entry
        if current == root or root not in current.parents:
            break
        current = current.parent
    return None


def scan_files(roots: list[Path], requested_kind: str) -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or any(part.startswith(".") for part in path.relative_to(root).parts):
                continue
            kind = file_kind(path)
            if requested_kind == "any" and path.suffix.lower() not in ALL_EXTENSIONS:
                continue
            if requested_kind != "any" and kind != requested_kind:
                continue
            files.append((root, path))
    return files


def pack_key(root: Path, path: Path) -> str:
    relative = path.relative_to(root)
    return relative.parts[0] if relative.parts else path.parent.name


def build_results(
    roots: list[Path], files: list[tuple[Path, Path]], terms: list[str], mode: str
) -> list[dict[str, Any]]:
    scored_files: list[dict[str, Any]] = []
    for root, path in files:
        score, matched = score_path(path.relative_to(root), terms)
        if terms and not matched:
            continue
        scored_files.append(
            {
                "root": root,
                "path": path,
                "score": score,
                "matched": matched,
                "kind": file_kind(path),
            }
        )

    if mode == "files":
        results: list[dict[str, Any]] = []
        for item in sorted(scored_files, key=lambda row: (-row["score"], str(row["path"]).lower())):
            license_path = nearest_license(item["path"], item["root"])
            results.append(
                {
                    "score": round(item["score"], 2),
                    "kind": item["kind"],
                    "matched": sorted(item["matched"]),
                    "path": str(item["path"]),
                    "license": str(license_path) if license_path else None,
                }
            )
        return results

    groups: dict[tuple[Path, str], list[dict[str, Any]]] = defaultdict(list)
    for item in scored_files:
        groups[(item["root"], pack_key(item["root"], item["path"]))].append(item)

    results = []
    for (root, pack), items in groups.items():
        items.sort(key=lambda row: (-row["score"], str(row["path"]).lower()))
        matched = set().union(*(item["matched"] for item in items))
        score = max(item["score"] for item in items) + len(matched) * 1.5 + math.log2(len(items) + 1) * 0.2
        kind_counts: dict[str, int] = defaultdict(int)
        for item in items:
            kind_counts[item["kind"]] += 1
        license_path = None
        for item in items:
            license_path = nearest_license(item["path"], root)
            if license_path:
                break
        results.append(
            {
                "score": round(score, 2),
                "pack": str(root / pack),
                "matched": sorted(matched),
                "files": len(items),
                "kinds": dict(sorted(kind_counts.items())),
                "samples": [str(item["path"]) for item in items[:5]],
                "license": str(license_path) if license_path else None,
            }
        )
    return sorted(results, key=lambda row: (-row["score"], row["pack"].lower()))


def render_human(results: list[dict[str, Any]], mode: str) -> None:
    if not results:
        print("No matching assets found.")
        return
    for index, row in enumerate(results, 1):
        if mode == "packs":
            print(f"{index:>2}. score={row['score']:<5} files={row['files']:<4} {row['pack']}")
            print(f"    matched={','.join(row['matched']) or '-'} kinds={row['kinds']}")
            for sample in row["samples"]:
                print(f"    sample: {sample}")
        else:
            print(f"{index:>2}. score={row['score']:<5} kind={row['kind']:<5} {row['path']}")
        if row.get("license"):
            print(f"    license: {row['license']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path, help="Asset-library roots")
    parser.add_argument("--query", required=True, help="Space- or comma-separated search terms")
    parser.add_argument("--kind", choices=["any", *KINDS], default="any")
    parser.add_argument("--mode", choices=["packs", "files"], default="packs")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    roots = [root.expanduser().resolve() for root in args.roots]
    missing = [str(root) for root in roots if not root.is_dir()]
    if missing:
        print(f"warning: missing roots: {', '.join(missing)}", file=sys.stderr)
    terms = sorted(tokenize(args.query))
    files = scan_files(roots, args.kind)
    results = build_results(roots, files, terms, args.mode)[: max(args.limit, 0)]
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        render_human(results, args.mode)
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
