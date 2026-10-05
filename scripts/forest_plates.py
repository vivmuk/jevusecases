#!/usr/bin/env python3
"""Rebuild the forest plates with a real alpha edge.

Each generated artwork has a hard rectangular edge baked into the pixels, so no CSS
blend can hide it. A vignette onto a transparent background cuts that edge away and
lets the page's own paper show through the fade.
"""
import json
import pathlib
import subprocess

ROOT = pathlib.Path("/home/vivgates/Projects/jevusecases")
ART = ROOT / "lab" / "art"
DEST = ROOT / "assets" / "forest"
DEST.mkdir(parents=True, exist_ok=True)


def plate(src, out, width, vigour):
    subprocess.run(["magick", str(src), "-resize", "%dx" % width, "-background", "none",
                    "-alpha", "set", "-vignette", vigour, "-strip", "-quality", "76",
                    str(out)], check=True)
    print("wrote", out.name, out.stat().st_size // 1024, "KB", flush=True)


# the opener takes the diffuse artwork: a bright focal eye next to the headline
# wins the first glance, and the headline has to win.
plate(ART / "hero.png", DEST / "hero.webp", 2000, "0x170")

cases = json.load(open(ROOT / "content.json"))["cases"]
for case in cases:
    src = ART / ("case-%02d.png" % case["n"])
    plate(src, DEST / ("case-%02d.webp" % case["n"]), 2000, "0x120")

total = sum(f.stat().st_size for f in DEST.glob("*.webp")) // 1024
print("all plates rebuilt, total", total, "KB", flush=True)
