#!/usr/bin/env python3
"""Render one use case's plate at three levels of detail, for a side-by-side pick.

The shipped plates are deliberately abstract: pure geometry, no recognisable
objects. That reads well in a row of nineteen, but it describes nothing about
the job on the card. This script renders the same case three ways so the level
of description can be chosen deliberately instead of by accident.

  python3 scripts/plate_variants.py 11            # all three levels
  python3 scripts/plate_variants.py 11 detailed   # just one

Writes lab/variants/case-NN-<level>.png. Nothing here touches assets/plates, so
running it can never change what the site ships.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_plates import generate  # noqa: E402  (same request plumbing, key lookup, blank guard)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lab" / "variants"
OUT.mkdir(parents=True, exist_ok=True)

BASE = (
    "Flat vector editorial illustration printed on light paper. Thin even strokes of uniform "
    "weight, solid fills, no gradients, no perspective, no photographic shading, no 3D, no clay, "
    "no glow, no drop shadow, no texture. Palette: near-black ink #15181C line work on a cool "
    "light grey paper ground #F1F2F4. The deep amber #B4721A accent marks only the flagged or "
    "chosen items named in the scene, never anything else. Wide even margins, the drawing fills "
    "the frame, quiet and precise, like a diagram in a technical manual. "
)

NOTEXT = (
    " Absolutely no text, no letters, no numbers, no words, no symbols that read as writing, "
    "no captions, no labels, no watermark, no logo, no signature, no people, no faces, no hands, "
    "no emoji. Any document, screen or envelope is drawn blank or as plain ruled lines. "
)

# Three deliberate distances from the job. Level 1 is the house style: pure
# geometry, no objects. Level 3 is a narrative of the actual workflow.
LEVELS = {
    "minimal": (
        "Abstract minimal diagram: {n} geometric elements and nothing else, no recognisable "
        "objects, no scene, pure geometry. Even spacing, mostly empty paper. Subject: {scene}"
    ),
    "readable": (
        "A simple readable scene made of recognisable flat objects, about {n} elements in total, "
        "still hairline strokes, no interiors, no detail smaller than a grain of rice. Clear "
        "left-to-right flow. Subject: {scene}"
    ),
    "detailed": (
        "A detailed narrative illustration of the whole workflow, about {n} elements: "
        "recognisable objects, containers, connectors with arrowheads, and small instrument "
        "icons where the scene calls for them. Objects have outline interiors (ruled lines, "
        "dividers, trays) but stay flat and unshaded. Clear left-to-right before-and-after flow. "
        "Subject: {scene}"
    ),
}

COUNTS = {"minimal": "four to six", "readable": "nine to fourteen", "detailed": "twenty to thirty"}


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: plate_variants.py <case number> [minimal|readable|detailed]")
    n = int(sys.argv[1])
    wanted = sys.argv[2:] or list(LEVELS)
    cases = json.loads((ROOT / "content.json").read_text())["cases"]
    case = next((c for c in cases if c["n"] == n), None)
    if case is None:
        raise SystemExit("no case %d in content.json" % n)

    scenes = case.get("plate_levels") or {}
    print("case %d  %s" % (n, case["title"]))
    for level in wanted:
        scene = scenes.get(level) or case["plate"]
        prompt = (BASE
                  + LEVELS[level].format(n=COUNTS[level], scene=scene)
                  + NOTEXT)
        dest = OUT / ("case-%02d-%s.png" % (n, level))
        print("  %-9s -> %s" % (level, dest.name), flush=True)
        res = generate(prompt, dest)
        if res:
            print("     ok %dx%d %.0f KB" % (res[0], res[1], res[2] / 1024), flush=True)
        else:
            print("     FAILED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
