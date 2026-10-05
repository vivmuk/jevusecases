#!/usr/bin/env python3
"""The nineteen case artworks, redrawn with the words actually in the picture.

Same style as the agreed direction (luminous forest, vines carrying the decision,
Gaia-like presence, no face), but now the artwork also carries the case's own
wording: its title, the three shape words, and the candidate answers beside the
branches. A hand-painted sign in the picture is a normal thing to want; the model
will mangle a few letters and that has been explicitly accepted, so nothing here
tries to spell-check the render.

  python3 scripts/forest_art_text.py          # every case
  python3 scripts/forest_art_text.py 04 11    # just these
"""
import concurrent.futures as futures
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import forest_art as fa  # noqa: E402
from gen_plates import generate  # noqa: E402

ROOT = fa.ROOT
OUT = fa.OUT


def option_labels(case, limit=6):
    """The candidate answers this case declares, for labelling the branches."""
    blob = json.dumps(case.get("prompts", [])) + json.dumps(case.get("code", {}))
    for m in re.finditer(r"choice:[^'\"|]*\|([^'\"]+)", blob):
        labels = [o.split(":")[0].strip() for o in re.split(r",\s*", m.group(1)) if ":" in o]
        labels = [re.sub(r"[^A-Za-z ]", "", l).strip() for l in labels]
        labels = [l for l in labels if l]
        if 2 <= len(labels) <= 9:
            return labels[:limit]
    return []


def prompt_for(case):
    shape = case.get("shape", {})
    plain = case.get("plain", {})
    state = re.sub(r"\s+", " ", str(shape.get("state", "")))[:70]
    question = re.sub(r"\s+", " ", str(shape.get("question", "")))[:70]
    answer = re.sub(r"\s+", " ", str(shape.get("answer", "")))[:70]
    what = re.sub(r"\s+", " ", str(case.get("what", "")))[:120]
    labels = option_labels(case)

    words = (
        'Across the picture, painted into the artwork as part of the scene, a hand-lettered sign in '
        'elegant warm cream capitals reads the title: "%s". Smaller hand-lettered lettering on ribbons '
        'of light reads: "%s". Three small painted plaques read "STATE", "QUESTION" and "ANSWER". '
        % (case["title"].upper(), what)
    )
    if labels:
        words += ("Each vine branch carries a small hand-painted leaf plaque with its own word, reading "
                  "in order: " + ", ".join('"%s"' % l.upper() for l in labels) + ". ")
    words += ("One plaque is picked out in glowing amber: the answer that was chosen. "
              "The lettering is part of the painting, painted in the same brush as the vines, "
              "not a separate overlay.")

    detail = ("This picture explains one job for a decision model. State: %s. Question: %s. Answer: %s. "
              % (state, question, answer))

    return (fa.STYLE + fa.PRESENCE + fa.MOTIF.format(n=max(2, fa.option_count(case)),
                                                    flavour=fa.CASES.get(case["n"], "vines and moss in soft mist"))
            + detail + words + fa.NOTEXT_ALLOWED)


def draw(name, prompt):
    out = OUT / ("%s.png" % name)
    generate(prompt, out)
    return "%s ok %d KB" % (name, out.stat().st_size // 1024)


def main():
    want = sys.argv[1:]
    cases = json.load(open(ROOT / "content.json"))["cases"]
    jobs = [("case-%02d" % c["n"], prompt_for(c)) for c in cases if not want or ("%02d" % c["n"]) in want]
    print("drawing %d artworks with words in them" % len(jobs), flush=True)
    with futures.ThreadPoolExecutor(max_workers=5) as pool:
        for result in pool.map(lambda j: draw(*j), jobs):
            print(result, flush=True)


if __name__ == "__main__":
    main()
