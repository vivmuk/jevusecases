#!/usr/bin/env python3
"""Forest artwork for the case pages, drawn with the muse-image model on Venice.

Three art directions for the same case, so the look can be chosen rather than
guessed at. All three keep the site's constraints: light paper, green and orange
accents, no lettering anywhere (the model invents glyphs the moment it is asked for
text, and a garbled word is worse than no word).

  python3 scripts/gen_art.py            # the three directions, sample case
  python3 scripts/gen_art.py a          # just one
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_plates import generate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lab" / "art"
OUT.mkdir(parents=True, exist_ok=True)

PAPER = (
    "Artistic editorial illustration for a technical reference site, on a light paper ground "
    "#F1F2F4. Palette: deep forest green #2E6B4F, burnt orange #C4621A, warm cream highlights, "
    "near-black ink #15181C for fine detail. Beautiful, calm, gallery quality. Wide even margins, "
    "the subject fills the frame, no border, no frame line. "
)

NOTEXT = (
    " Absolutely no text, no letters, no numbers, no words, no captions, no labels, no signature, "
    "no initials, no watermark, no logo, no user interface, no chart, no diagram."
)

DIRECTIONS = {
    "a": (PAPER + "Subject: a single jungle animal rendered as a refined flat-colour plate, seen in "
                  "profile, standing among three or four large tropical leaves. Bold simple shapes with "
                  "crisp edges, generous areas of flat forest green and burnt orange, cream paper showing "
                  "through as the background. The mood is quiet and museum-like, like a naturalist plate "
                  "redrawn by a modern poster artist. No texture, no photographic detail." + NOTEXT),
    "b": (PAPER + "Subject: a lush jungle scene, layered leaves and hanging vines in deep green, with a "
                  "single animal half-hidden among them catching a shaft of warm orange light. Painterly "
                  "gouache feel with soft edges inside the shapes, but the composition stays flat and "
                  "poster-like, not photographic and not 3D." + NOTEXT),
    "c": (PAPER + "Subject: one jungle animal built from simple overlapping geometric shapes, like a "
                  "screen print: a few flat greens, two oranges, one cream, hard edges, visible overlaps. "
                  "Very graphic and modern, minimal detail, strong silhouette." + NOTEXT),
}


# ----------------------------------------------------------------- mystical set
# The first three directions were judged too basic and too literal. These go for a
# fantasy register: luminous, ornate, atmospheric, with the creature implied rather
# than plainly shown, while still sitting on a light ground (light bleeds to white)
# so the artwork still belongs on the paper-coloured site.
MYSTIC = (
    "A luminous mystical fantasy artwork, richly painterly and ornate, museum quality, "
    "with deep atmospheric depth. Light bleeds through the composition so the ground reads "
    "pale and airy rather than dark. Palette: enchanted emerald and jade greens, glowing "
    "burnt orange and amber, soft gold light, misty pearlescent highlights. Ethereal, "
    "dreamlike, quietly magical, never cartoonish, never a children's book. "
    "Wide even margins, the subject fills the frame, no border, no frame line. "
)

MYSTIC_DIRECTIONS = {
    "d": (MYSTIC + "Subject: a great forest spirit animal dissolving into mist and light, its form "
                   "half-formed, suggested rather than shown, glowing eyes the only sharp detail. "
                   "Layered translucent foliage and floating spores of light surround it, shafts of pale "
                   "gold falling from above, ornate hanging vines dissolving into haze. "
                   "Painterly, atmospheric, mysterious." + NOTEXT),
    "e": (MYSTIC + "Subject: an enchanted jungle at first light, dense and jewelled, with a hidden "
                   "creature glimpsed between the leaves rather than standing in the open: only a curve of "
                   "shoulder, one glowing eye, a ripple of light. Ornate overlapping foliage, luminous "
                   "blossoms, drifting motes of gold, deep emerald shadows that thin out into pale mist at "
                   "the edges. Highly detailed, decorative, magical." + NOTEXT),
    "f": (MYSTIC + "Subject: a dreamlike double exposure, where a wild animal and luminous jungle "
                   "botanicals merge into one another so neither is fully visible: leaf veins becoming "
                   "fur, light becoming breath. Soft focused, radiant, surreal and serene, glowing amber "
                   "core fading to pale mist at the edges. Painterly, elegant, quietly mystical." + NOTEXT),
}


MYSTIC_DIRECTIONS.update({
    "g": (MYSTIC + "Subject: a great forest guardian whose head and shoulders are assembled from moss, "
                   "ferns and root-tangles, two glowing amber eyes, standing deep in an enchanted jungle "
                   "canopy. Shafts of pale gold light break through; embers drift. Classical oil painting "
                   "with chiaroscuro and 19th century engraving linework, riso grain and fine halftone "
                   "texture. The ground stays pale and misty so the artwork sits on a cream page." + NOTEXT),
    "h": (MYSTIC + "Subject: a mystical jungle clearing in luminous mist, where a creature of leaves and "
                   "light is half revealed, glowing amber eyes and a suggestion of antlers, orange blooms "
                   "and vines dissolving into radiance. Renaissance chiaroscuro meets modern shader glow, "
                   "fine engraving texture, ethereal and ornate, pale luminous ground, dreamlike." + NOTEXT),
})

def main():
    DIRECTIONS.update(MYSTIC_DIRECTIONS)
    want = sys.argv[1:] or list(DIRECTIONS)
    for k in want:
        if k not in DIRECTIONS:
            raise SystemExit("unknown direction %r (have: %s)" % (k, ", ".join(DIRECTIONS)))
        dest = OUT / ("forest-%s.png" % k)
        print("direction %s -> %s" % (k, dest.name), flush=True)
        res = generate(DIRECTIONS[k], dest)
        print("   ok %dx%d %.0f KB" % (res[0], res[1], res[2] / 1024) if res else "   FAILED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
