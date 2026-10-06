#!/usr/bin/env python3
"""The case artwork, drawn with muse-image on Venice.

One idea, told nineteen ways: the decision itself, as a forest. A seed of light
enters and becomes a stem; the stem divides into exactly as many vine branches as
the case has candidate answers, all of them equal; one branch carries a single
amber bloom, the answer that was chosen. The presence behind it is Gaia-like and
never a face: roots, radiance and blossom standing in for a figure.

  python3 scripts/forest_art.py            # everything missing
  python3 scripts/forest_art.py 01 07      # only these cases
  python3 scripts/forest_art.py hero       # just the opening artwork
"""
import concurrent.futures as futures
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_plates import generate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lab" / "art"
OUT.mkdir(parents=True, exist_ok=True)

STYLE = (
    "A luminous mystical fantasy artwork: a classical oil painting fused with modern digital glow, "
    "chiaroscuro depth, fine engraving linework, risograph grain and soft halftone texture. "
    "Palette: enchanted emerald and jade greens, glowing amber and burnt orange, pale gold light, "
    "misty pearlescent highlights. The ground stays pale and luminous so the picture dissolves into "
    "cream paper at the edges. Painterly, ornate, serene, museum quality, wide even margins, "
    "no border, no frame. "
)

PRESENCE = (
    "No human face anywhere and no visible human figure. The living presence is Gaia-like: a vast "
    "earth-mother spirit of the forest, felt as radiance, roots and blossom rather than shown as a body. "
)

MOTIF = (
    "The decision, told as a forest: a single seed of light enters from the left and becomes one stem; "
    "the stem divides into exactly {n} healthy vine branches of equal standing, each ending in its own "
    "cluster of leaves, and all {n} of them are possible answers; one branch carries a single luminous "
    "amber bloom with a warm glow, the answer chosen. Branching vines, hanging roots, mossy archways "
    "and cathedral-like forest structures frame the whole composition. {flavour} "
)

# Lettering is now wanted inside these pictures: words painted into the artwork, in
# the painter's own brush. A few letters will come out wrong and that is accepted.
NOTEXT_ALLOWED = (
    " Hand-painted lettering woven into the picture is wanted here. Still: no watermark, "
    "no signature, no initials, no logo, no user interface, no chart, no diagram, no caption bar."
)

CASES = {
    1: "a wide ledger of leaves, rows of identical ferns along a mossy shelf",
    2: "three separate vines braiding past one another before parting, orchids in the mist",
    3: "many small vines climbing one great trunk, each with its own leaf cluster",
    4: "clips of light falling through a canopy, a handful of vines catching them",
    5: "vines at different stages of growth along a sunlit slope, from seedling to ancient root",
    6: "a web of vines linking one mossy stone to many others across a dark hollow",
    7: "a single vine flowering among thousands of plain leaves",
    8: "two vines twining around each other, one pale one amber, in quiet water light",
    9: "many vines gathered at one junction, one of them taking the light",
    10: "several different trunks of different ages and sizes, vines choosing between them",
    11: "a mossy gate of roots with vines passing through it, most turned away into fog",
    12: "vines stripped of dead growth, clean stems rising out of a bed of decaying leaves",
    13: "one flower hidden among many look-alike leaves, found by the light",
    14: "a single luminous leaf among a wall of identical foliage",
    15: "a stream of falling petals, each caught and sorted as it passes",
    16: "an old root system surfacing to touch one remembered stone, no flower invented",
    17: "one blossom chosen from a rack of dormant buds, opening as it is picked",
    18: "vines assembling a lattice arbour in the order a visitor walks through it",
    19: "a long winding path of vines with a few cut away, the rest still growing",
    20: "a single vine meeting one vertical gate of light, one branch passing through it and one stopped dead",
    21: "a vine winding to the right through a row of small gates, stopping at the fourth where an amber bloom opens",
    22: "one seed resting at the left of an open field of short plain stems, a thin amber thread reaching a distant gate",
}

HERO = (
    "Subject: an enchanted forest canopy seen from within, where hundreds of vines braid outward into "
    "countless branches of equal standing, every branch ending in a pale cluster of leaves and a few of "
    "them carrying a single glowing amber bloom. Drifting spores of gold light, hanging roots, mossy "
    "arches, deep jade shadow thinning to pale mist so the picture dissolves into cream paper. "
    "Wide, calm, generous, no focal face, the meaning carried by the branching itself. "
)


def option_count(case):
    """How many candidate answers this case's own code declares, so the number of
    vine branches in the artwork is the number of choices in the decision."""
    blob = json.dumps(case.get("prompts", [])) + json.dumps(case.get("code", {}))
    for m in re.finditer(r"choice:[^'\"|]*\|([^'\"]+)", blob):
        opts = [o for o in re.split(r",\s*", m.group(1)) if ":" in o]
        if 2 <= len(opts) <= 9:
            return len(opts)
    if "score:" in blob:
        return 5
    if "yes:" in blob or "noul" in blob:
        return 2
    return 4


def build(case):
    n = option_count(case)
    flavour = CASES.get(case["n"], "vines and moss in soft mist")
    prompt = STYLE + PRESENCE + MOTIF.format(n=n, flavour=flavour)
    return prompt + (
        " Absolutely no text, no letters, no numbers, no words, no captions, no labels, no signature, "
        "no watermark, no logo, no user interface, no chart, no diagram."
    )


def draw(name, prompt):
    out = OUT / ("%s.png" % name)
    if out.exists() and out.stat().st_size > 50_000:
        return "%s already drawn" % name
    generate(prompt, out)
    return "%s ok %d KB" % (name, out.stat().st_size // 1024)


def main():
    want = sys.argv[1:]
    cases = json.load(open(ROOT / "content.json"))["cases"]
    jobs = []
    if not want or "hero" in want:
        jobs.append(("hero", STYLE + HERO + " Absolutely no text, no letters, no numbers, no words, "
                                          "no captions, no labels, no signature, no watermark, no logo."))
    for case in cases:
        tag = "%02d" % case["n"]
        if want and tag not in want:
            continue
        jobs.append(("case-%s" % tag, build(case)))
    print("drawing %d artworks" % len(jobs), flush=True)
    with futures.ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(lambda j: draw(*j), jobs):
            print(result, flush=True)


if __name__ == "__main__":
    main()
