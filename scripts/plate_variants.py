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

# Labelled plates are allowed text, but only the labels the brief names, spelled
# the way the brief spells them. Anything longer comes back as invented glyphs.
LABELS = (
    " The only lettering in the picture is these exact short labels, each spelled letter for "
    "letter, with no extra words and no invented text anywhere else: {labels}. Set each label in "
    "a plain bold sans-serif face inside or beside the object it names, in near-black ink except "
    "for the one amber label the scene describes. Every other surface, list row, document and "
    "screen is drawn as plain ruled lines or left blank. No other writing, no captions, no "
    "watermark, no logo, no signature, no people, no faces, no hands, no emoji."
)

DEFAULT_LABELS = {"detailed_text": "INBOX, SPAM, DRAFT"}

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
    "detailed_text": (
        "A detailed illustration of the whole workflow that depicts the working software itself, "
        "about {n} elements: a flat product-style window with a title bar, clearly separated list "
        "rows, panels and buttons drawn as simple outlined shapes, plus connectors with "
        "arrowheads showing what happens to each item. Clear left-to-right before-and-after flow. "
        "Subject: {scene}"
    ),
}

COUNTS = {"minimal": "four to six", "readable": "nine to fourteen",
          "detailed": "twenty to thirty", "detailed_text": "eighteen to twenty-eight"}


def labels_for(level, case):
    return case.get("plate_labels", {}).get(level) or DEFAULT_LABELS.get(level, "")


def prompt_for(level, case, scene):
    tail = LABELS.format(labels=labels_for(level, case)) if level == "detailed_text" else NOTEXT
    return BASE + LEVELS[level].format(n=COUNTS[level], scene=scene) + tail


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: plate_variants.py <case number> [minimal|readable|detailed]")
    n = int(sys.argv[1])
    wanted = sys.argv[2:] or list(LEVELS)
    cases = json.loads((ROOT / "content.json").read_text())["cases"]
    case = next((c for c in cases if c["n"] == n), None)
    if case is None:
        raise SystemExit("no case %d in content.json" % n)

    scenes_by_level = case.get("plate_levels") or {}
    print("case %d  %s" % (n, case["title"]))
    for level in wanted:
        if level not in LEVELS:
            raise SystemExit("unknown level %r (have: %s)" % (level, ", ".join(LEVELS)))
        raw = scenes_by_level.get(level) or case["plate"]
        scenes = raw if isinstance(raw, list) else [raw]
        for i, scene in enumerate(scenes, 1):
            tag = "" if len(scenes) == 1 else "-%d" % i
            dest = OUT / ("case-%02d-%s%s.png" % (n, level, tag))
            print("  %-14s %s" % (level + tag, dest.name), flush=True)
            res = generate(prompt_for(level, case, scene), dest)
            if res:
                print("     ok %dx%d %.0f KB" % (res[0], res[1], res[2] / 1024), flush=True)
            else:
                print("     FAILED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
