#!/usr/bin/env python3
"""Two labelled, lightly coloured plate samples for one use case, for a pick.

Differs from the shipped plates on three axes, all of them requested:
  * the use case name is printed on the picture
  * a highlighted JEV badge marks the exact step where the decision happens
  * muted colour fills instead of ink-and-one-amber

Lettering is the risky part. These models invent glyphs the moment a prompt asks
for a long string, so each sample states the exact text and bans everything else,
and the result gets read back with vision before it is shown to anyone.

  python3 scripts/plate_samples.py          # both samples
  python3 scripts/plate_samples.py a        # just one
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_plates import generate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lab" / "samples"
OUT.mkdir(parents=True, exist_ok=True)

STYLE = (
    "A flat vector editorial infographic on a light paper ground #F1F2F4, in the manner of a "
    "clean technical poster. Muted colour fills, no gradients, no photographic shading, no 3D, "
    "no glow, no drop shadow, no texture, no perspective. Palette: near-black ink #15181C for "
    "all line work and text, deep amber #B4721A for the highlighted badge, slate blue #3E5C76, "
    "muted teal #2F6F63 and brick red #A4443C as the only other fills, all flat. Wide even "
    "margins, composition fills the frame, one clear left-to-right flow. "
)

RULES = (
    " The picture contains only these words, each spelled letter for letter, in a plain bold "
    "sans-serif, with no other writing, no captions, no watermark, no logo, no signature, no "
    "people, no faces, no hands, no emoji, and no invented letterforms anywhere: {words}."
)

SAMPLE_A = (
    " Subject: the title {title} is set large across the top left of the picture. Below it, a "
    "mail application window in slate blue with six white message rows inside, each row a flat "
    "bar. From the window a thick arrow enters a small amber rounded badge sitting at the centre "
    "of the picture, and the badge carries the word {badge} in bold near-black letters. Two "
    "arrows leave the badge: one drops down from it into a brick red open bin whose message "
    "rows carry a white X, and one continues right into a muted teal panel holding a white "
    "document sheet with ruled lines and a small outlined button. A small bold label {left} sits "
    "above the window and a small bold label {right} sits above the teal panel."
)

SAMPLE_B = (
    " Subject: the title {title} is set large across the top of the picture. Below it, three "
    "flat stages joined by thick arrows. Stage one is a slate blue tray holding six white "
    "message bars, with the small bold label {left} above it. Stage two is a narrow vertical "
    "amber badge in the middle of the picture carrying the word {badge} in bold near-black "
    "letters, with two message bars marked by a white X dropping from its base into a brick red "
    "bin below. Stage three is a muted teal desk holding a white document sheet with ruled lines "
    "and a small outlined button, with the small bold label {right} above it."
)

SAMPLES = {
    "a": (SAMPLE_A, "INBOX PRE FILTERING FOR AI AGENTS", "INBOX, JEV, DRAFT"),
    "b": (SAMPLE_B, "11 INBOX FILTER", "INBOX, JEV, DRAFT"),
}


def prompt_for(key):
    body, title, words = SAMPLES[key]
    words = ", ".join([title] + [w.strip() for w in words.split(",")])
    return STYLE + body.format(title=title, badge="JEV", left="INBOX", right="DRAFT") + RULES.format(words=words)


def main():
    wanted = sys.argv[1:] or list(SAMPLES)
    for key in wanted:
        if key not in SAMPLES:
            raise SystemExit("unknown sample %r (have: %s)" % (key, ", ".join(SAMPLES)))
        dest = OUT / ("inbox-%s.png" % key)
        print("sample %s -> %s" % (key, dest.name), flush=True)
        res = generate(prompt_for(key), dest)
        if res:
            print("   ok %dx%d %.0f KB" % (res[0], res[1], res[2] / 1024), flush=True)
        else:
            print("   FAILED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
