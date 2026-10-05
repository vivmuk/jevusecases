#!/usr/bin/env python3
"""The README's opening picture: the whole project in one image.

Same forest language as the case artwork, but wide and summary: one great cream
sheet of vines where many branches lead to a single amber bloom, with the project's
own words painted in.

  python3 scripts/readme_art.py
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_plates import generate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST_DIR = ROOT / "assets" / "readme"
DEST_DIR.mkdir(parents=True, exist_ok=True)
RAW = ROOT / "lab" / "art" / "readme-overview.png"

PROMPT = (
    "A luminous mystical fantasy watercolour artwork: a classical botanical painting fused with modern "
    "digital glow, chiaroscuro depth, fine engraving linework, risograph grain, soft halftone texture. "
    "Palette: enchanted emerald and jade greens, glowing amber and burnt orange, pale gold light, misty "
    "pearl highlights, on a pale luminous cream ground. Museum quality, serene, ornate. "
    "Subject: a wide banner showing one idea told nineteen ways. A single seed of light enters at the "
    "left and becomes a stem; the stem divides into a great many vine branches of equal standing that "
    "sweep across the whole picture, every branch ending in its own cluster of leaves, and a handful of "
    "them carrying one glowing amber bloom each. Branching vines, hanging roots, mossy archways and "
    "cathedral-like forest structures frame the scene. A vast Gaia-like earth-mother presence is felt as "
    "radiance and roots, never shown as a face or a body. "
    "Painted into the artwork as part of the scene, hand-lettered in warm cream capitals: a large title "
    'reading "JEV USE CASES", and smaller lettering on ribbons of light reading "EVERY JOB A MODEL CAN '
    'ANSWER IN HALF A SECOND". Three small painted plaques read "STATE", "CHOICE" and "ANSWER", and one '
    "plaque beside the chosen bloom is picked out in glowing amber. The lettering is painted in the same "
    "brush as the vines, part of the painting, not an overlay. "
    "No watermark, no signature, no logo, no user interface, no chart, no diagram, no caption bar."
)


def main():
    generate(PROMPT, RAW)
    out = DEST_DIR / "overview.jpg"
    subprocess.run(["magick", str(RAW), "-resize", "1800x", "-strip", "-quality", "86", str(out)], check=True)
    print("readme image:", out, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
