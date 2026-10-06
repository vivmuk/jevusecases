#!/usr/bin/env python3
"""Build README.md from the same data the site is built from.

The case list in the README is generated, not typed, so adding case twenty updates
the README and the page together.

  python3 scripts/build_readme.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = "https://jevusecases-production.up.railway.app"
REPO = "https://github.com/vivmuk/jevusecases"
VIDEO = "https://youtube.com/watch?v=3iDiWTt8lok"

TIERS = [
    ("easy", "Easy", "A single call sits in front of work you already do."),
    ("intermediate", "Intermediate", "A queue, an index, or a small service appears."),
    ("advanced", "Advanced", "A part of your stack starts making its own choices."),
]



WORDS = {19: "Nineteen", 20: "Twenty", 21: "Twenty-one", 22: "Twenty-two",
         23: "Twenty-three", 24: "Twenty-four", 25: "Twenty-five"}


def count_word(n):
    """The number of cases as a word, so no sentence is left claiming nineteen."""
    return WORDS.get(n, str(n))


def main():
    cases = json.load(open(ROOT / "content.json"))["cases"]
    lines = []
    add = lines.append

    add("# Jev use cases")
    add("")
    add("**%s jobs a decision model can take over, each with its code and its prompts.**"
        % count_word(len(cases)))
    add("")
    add("![The shape of the work: one state, a set of fixed answers, one decision, drawn as "
        "vines across a cream sheet](assets/readme/overview.jpg)")
    add("")
    add("A language model writes an answer, and then your program has to read it, hope it is in the "
        "right shape, and cope when it is not. Jev does not write. You send it a piece of text and a "
        "set of questions whose answers you already know how to list, and it sends back one of your "
        "answers with a probability your code can test.")
    add("")
    add("This site is a reference to what that is good for: %s jobs, grouped by how much of "
        "your stack they touch, each one written in plain words as well as in code. The original "
        "nineteen come from one video; the rest were found in the field afterwards."
        % count_word(len(cases)).lower())
    add("")
    add("- **Live:** <%s>" % LIVE)
    add("- **Plain-language guide:** [about.html](about.html) — what Jev is, how to call it, and "
        "where it goes wrong, set for readers who find dense text hard work.")
    add("- **Source of the first nineteen jobs:** <%s> (Jay E | RoboNuggets)" % VIDEO)
    add("- **The later jobs:** found in the field; each case card links the article that named it.")
    add("")

    add("## What is here")
    add("")
    add("Every case carries the same five things:")
    add("")
    add("1. **The decision** — the state it reads, the question it answers, the answer it returns.")
    add("2. **In plain words** — what comes in, what you hand over, what it does, what you get back, "
        "with green marking what you supply and orange marking what the model decides and returns.")
    add("3. **One runnable snippet** — the smallest honest version of the call.")
    add("4. **Two or three example prompts** — the state and the question, ready to paste.")
    add("5. **A drawn plate** — the decision itself as a forest: a seed of light enters, the stem "
        "splits into exactly as many vine branches as the case has candidate answers, and one branch "
        "carries the amber bloom that was chosen.")
    add("")

    for key, label, blurb in TIERS:
        group = [c for c in cases if c["tier"] == key]
        if not group:
            continue
        add("## %s" % label)
        add("")
        add("_%s_" % blurb)
        add("")
        for c in group:
            at = (c.get("at") or "").strip()
            if at:
                add("- **%02d. %s** — `%s` · [watch at %s](%s&t=%ds)" % (
                    c["n"], c["title"], at, at, VIDEO,
                    int(at[:2]) * 60 + int(at[3:])))
            else:
                add("- **%02d. %s** — [%s](%s)" % (
                    c["n"], c["title"], c.get("source_name") or "the field",
                    c.get("source") or ""))
        add("")

    add("## How the page is made")
    add("")
    add("| Piece | Tool |")
    add("| --- | --- |")
    add("| Scroll engine | `scrollcraft` (pinned, panning and flowing acts) |")
    add("| Page build | `scripts/build_page.py` — reads `content.json`, writes `index.html` |")
    add("| Plain-language guide | `scripts/build_about.py` — writes `about.html` |")
    add("| Artwork | `scripts/forest_art.py` and `scripts/forest_art_text.py`, drawn with "
        "`muse-image` on the Venice API |")
    add("| Plate pipeline | `scripts/forest_plates.py` — resize, feather the edges onto real "
        "transparency, write webp |")
    add("| This readme | `scripts/build_readme.py` — generated from `content.json` |")
    add("")
    add("The plates are feathered rather than framed: a generated picture has a hard rectangular "
    "edge baked into its pixels, so each one is masked onto a transparent background. Without that "
    "it reads as a rectangle pasted on the paper, whatever the CSS blend does.")
    add("")

    add("## Run it locally")
    add("")
    add("```bash")
    add("python3 scripts/build_page.py      # data -> index.html")
    add("python3 scripts/build_about.py     # -> about.html")
    add("python3 scripts/build_readme.py    # -> README.md")
    add("python3 -m http.server 4500 --bind 127.0.0.1")
    add("```")
    add("")
    add("Drawing new art needs a Venice API key in `HERMES_CUSTOM_API_VENICE_AI_API_KEY`. "
        "Nothing else in the build touches the network.")
    add("")

    add("## Adding a case")
    add("")
    add("This site is meant to grow, so adding a case is a data edit, not a code change. Add an "
        "object to `content.json` with `n`, `title`, `tier`, `at`, `what`, `shape`, `use`, `code`, "
        "`prompts`, `caption`, `plain` and `plate`, then:")
    add("")
    add("```bash")
    add("python3 scripts/forest_art_text.py NN   # draw its plate")
    add("python3 scripts/forest_plates.py        # feather and compress every plate")
    add("python3 scripts/build_page.py           # rebuild the page")
    add("python3 scripts/build_readme.py         # keep this file true")
    add("```")
    add("")
    add("The tier headings on the page (\"Cases 01 to 08\") are computed from the case numbers in "
    "each tier, so no count is ever baked into a title.")
    add("")

    add("## About the words in the pictures")
    add("")
    add("The plates carry hand-painted lettering. A drawing model mangles a few letters, and that "
    "is accepted here on purpose: the picture is atmosphere, and the real labels live in the page's "
    "own type, where they are selectable, searchable and readable by a screen reader.")
    add("")

    add("## Credits")
    add("")
    add("The nineteen jobs come from [Jay E | RoboNuggets](%s). Jev itself is made by "
        "[TypeSafe AI](https://typesafe.ai); the plain-language guide cites the maker's "
        "documentation alongside independent notes and worked implementations. This site is an "
        "independent reference and is not affiliated with TypeSafe." % VIDEO)
    add("")

    out = ROOT / "README.md"
    out.write_text("\n".join(lines))
    print("wrote README.md, %d bytes, %d cases" % (out.stat().st_size, len(cases)))


if __name__ == "__main__":
    main()
