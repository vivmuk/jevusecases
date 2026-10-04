#!/usr/bin/env python3
"""Plates are generated as 2048px PNGs; the site ships WebP.

Flat diagrams compress hard, but a generated PNG carries film grain and a wide
palette, so the raw files run 0.5 to 2 MB each. This pass writes a 1600px WebP
alongside every PNG (q80), which is what index.html links. Run it after
gen_plates.py; it skips any WebP that is newer than its PNG.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLATES = ROOT / "assets" / "plates"
WIDTH = 1600
QUALITY = 80


def main(force=False):
    pngs = sorted(PLATES.glob("plate-*.png"))
    if not pngs:
        print("no plates to compress")
        return 1
    done = skipped = 0
    for png in pngs:
        webp = png.with_suffix(".webp")
        if webp.exists() and not force and webp.stat().st_mtime > png.stat().st_mtime:
            skipped += 1
            continue
        subprocess.run(
            ["magick", str(png), "-resize", f"{WIDTH}x", "-strip",
             "-quality", str(QUALITY), "-define", "webp:method=6", str(webp)],
            check=True,
        )
        done += 1
    total = sum(p.stat().st_size for p in PLATES.glob("plate-*.webp"))
    raw = sum(p.stat().st_size for p in PLATES.glob("plate-*.png"))
    print(f"webp: {done} written, {skipped} up to date, {total/1e6:.1f} MB total "
          f"(from {raw/1e6:.1f} MB of png)")
    return 0


if __name__ == "__main__":
    sys.exit(main(force="--force" in sys.argv))
