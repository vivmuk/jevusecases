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


def plate_command(png, webp):
    """Trim to the drawing, re-pad evenly, then resize.

    The model frames its diagram with a lot of empty paper, and it does so
    unevenly (one plate's subject covers a tenth of the frame, another fills it).
    At card scale that means identical strokes end up at different apparent
    weights, and the small subjects dissolve into the paper. Trimming to the
    content and re-padding by a fixed share of the frame normalises every plate
    to the same subject scale, which is what makes the set read as one shoot.
    """
    probe = subprocess.run(
        ["magick", "identify", "-format", "%w %h", str(png)],
        capture_output=True, text=True, check=True)
    w, h = (int(v) for v in probe.stdout.split())
    trimmed = subprocess.run(
        ["magick", str(png), "-fuzz", "6%", "-trim", "-format", "%w %h", "info:"],
        capture_output=True, text=True, check=True)
    try:
        tw, th = (int(v) for v in trimmed.stdout.split())
    except ValueError:
        tw, th = w, h
    # A trim that took almost everything is a failed read, not a tight subject.
    if tw < w * 0.25 or th < h * 0.25:
        tw, th = w, h
        trim = False
    else:
        trim = True
    pad = round(max(tw, th) * 0.09)
    # Re-pad to a 16:9 frame, so every plate on the page keeps the same shape
    # while the drawing inside it fills as much of that frame as its own aspect
    # allows.
    cw = max(tw + 2 * pad, round((th + 2 * pad) * 16 / 9))
    ch = round(cw * 9 / 16)
    args = ["magick", str(png)]
    if trim:
        args += ["-fuzz", "6%", "-trim", "+repage"]
    args += ["-bordercolor", "#f1f2f4", "-border", f"{pad}",
             "-background", "#f1f2f4", "-gravity", "center",
             "-extent", f"{cw}x{ch}"]
    args += ["-resize", f"{WIDTH}x", "-strip", "-quality", str(QUALITY),
             "-define", "webp:method=6", str(webp)]
    return args


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
        subprocess.run(plate_command(png, webp), check=True)
        done += 1
    total = sum(p.stat().st_size for p in PLATES.glob("plate-*.webp"))
    raw = sum(p.stat().st_size for p in PLATES.glob("plate-*.png"))
    print(f"webp: {done} written, {skipped} up to date, {total/1e6:.1f} MB total "
          f"(from {raw/1e6:.1f} MB of png)")
    return 0


if __name__ == "__main__":
    sys.exit(main(force="--force" in sys.argv))
