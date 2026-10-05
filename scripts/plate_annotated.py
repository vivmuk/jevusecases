#!/usr/bin/env python3
"""Annotated plates: a minimalist line drawing labelled the way a biological plate is.

The house plates are abstract and wordless: they carry the shape of a job and
nothing else. This is the other direction, and it is the one that reads as
"technical illustration" rather than "diagram":

  * one hairline ink drawing, uniform stroke, no fills, no shading
  * each part named by a short lowercase label at the end of a thin leader line
  * the step where Jev does the deciding circled in amber, and only that step

Lettering is the risk. Short lowercase single words survive far better than
sentences, so every sample names its labels exactly and bans everything else.
Read the result back with vision before showing it to anyone.

  python3 scripts/plate_annotated.py         # both samples
  python3 scripts/plate_annotated.py c
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_plates import generate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lab" / "samples"
OUT.mkdir(parents=True, exist_ok=True)

STYLE = (
    "A plate from a scientific manual: one fine hairline ink drawing on light warm paper, "
    "uniform single-weight line work, no fills, no shading, no gradients, no hatching, no 3D, "
    "no drop shadow, no texture, no perspective, no border frame. Ink is near-black #15181C. "
    "The drawing is annotated the way a biological illustration is annotated: from each named "
    "part a thin straight leader line runs out to a short lowercase label set in a small plain "
    "sans-serif. Exactly one element in the whole picture carries a thin amber #B4721A outline, "
    "and nothing else in the picture is coloured. Wide even margins, the drawing fills the frame. "
)

RULES = (
    " The only words in the picture are these exact labels, each spelled letter for letter in "
    "lowercase, one word each, with no other writing, no title, no numbers, no captions, no "
    "watermark, no logo, no signature, no people, no faces, no hands, no emoji and no invented "
    "letterforms anywhere: {labels}."
)

SAMPLE_C = (
    " Subject: the anatomy of a mail pipeline. At the left a stack of five envelope shapes drawn "
    "in thin outline. From the stack a single thin line runs right to a small open circle. From "
    "that circle two thin lines diverge: the upper one continues right to a small rectangular "
    "machine shape, the lower one drops into an open bin shape, and two envelopes crossed by a "
    "thin X sit on the lower branch. The small open circle where the lines divide carries a thin "
    "amber outline and is the circled part. Leader lines: the envelope stack is labelled "
    "{l_inbox}, the open circle is labelled {l_jev}, the crossed envelopes are labelled "
    "{l_spam}, and the machine shape is labelled {l_draft}."
)

SAMPLE_D = (
    " Subject: the anatomy of one message. At the centre a single large envelope drawn in thin "
    "outline with its flap open and one short ruled line inside it. From the envelope a thin "
    "leader line runs to the label {l_message}, and from the ruled line inside it a thin leader "
    "line runs to the label {l_filter}. To the right of the envelope stands a small gate drawn "
    "as two short vertical lines with a thin amber outline around it, and from it a thin line "
    "continues right to a small tray holding one sheet of ruled lines labelled {l_reply}. The "
    "gate is the circled part and is labelled {l_jev}."
)

SAMPLES = {
    "c": (SAMPLE_C, {"l_inbox": "inbox", "l_jev": "jev", "l_spam": "spam", "l_draft": "draft"}),
    "d": (SAMPLE_D, {"l_message": "message", "l_filter": "filter", "l_jev": "jev", "l_reply": "reply"}),
}


def prompt_for(key):
    body, labels = SAMPLES[key]
    words = ", ".join(labels.values())
    return STYLE + body.format(**labels) + RULES.format(labels=words)


def main():
    wanted = sys.argv[1:] or list(SAMPLES)
    for key in wanted:
        if key not in SAMPLES:
            raise SystemExit("unknown sample %r (have: %s)" % (key, ", ".join(SAMPLES)))
        dest = OUT / ("annotated-%s.png" % key)
        print("sample %s -> %s" % (key, dest.name), flush=True)
        res = generate(prompt_for(key), dest)
        if res:
            print("   ok %dx%d %.0f KB" % (res[0], res[1], res[2] / 1024), flush=True)
        else:
            print("   FAILED", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
