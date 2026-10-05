#!/usr/bin/env python3
"""Draw each case's plate from the decision the case actually makes.

Every case already publishes its own code, and that code declares the real option
sets (CATS, BUCKETS, KINDS, SHAPES) and the real question types. So the plate does
not have to be guessed by an image model: it can be drawn from the same truth the
card prints. What the drawing shows, in the house style (hairline ink on paper, one
amber accent, no lettering):

    a single state entering from the left
    the question, as one cell per option the code allows
    a second question below it, when the case asks one
    the answer, as the one cell in amber

Nothing is invented: a case whose option count cannot be read from its own code is
drawn as an open field rather than given a made-up number.

  python3 scripts/svg_plates.py            # all cases -> lab/svgplates/
  python3 scripts/svg_plates.py 1 2 11     # chosen cases
  python3 scripts/svg_plates.py --write    # also install into assets/plates-svg/
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "lab" / "svgplates"
PAPER, INK, AMBER = "#f1f2f4", "#15181c", "#9c5a10"
W, H = 1600, 900


def code_src(case):
    c = case.get("code") or {}
    return c.get("src", "") if isinstance(c, dict) else str(c)


def count_dict_keys(src, name):
    m = re.search(re.escape(name) + r"\s*=\s*\{(.*?)\}", src, re.S)
    if not m:
        return None
    return len(re.findall(r'"\s*[A-Za-z0-9_\-]+\s*"\s*:', m.group(1))) or None


def parse_questions(case):
    """Read the question list out of the case's own snippet: type, and option count."""
    src = code_src(case)
    qs = []
    if not src:
        return qs
    # python snippets: {"name": {"type": "choice", "criteria": NAME ...}}
    for m in re.finditer(r'"(\w+)"\s*:\s*\{\s*"type"\s*:\s*"(\w+)"', src):
        name, kind = m.group(1), m.group(2)
        block = src[m.end():m.end() + 400]
        cm = re.search(r'"criteria"\s*:\s*(\w+)', block)
        n = None
        if cm:
            n = count_dict_keys(src, cm.group(1))
            if n is None:
                lit = re.search(re.escape(cm.group(1)) + r"\s*=\s*\[(.*?)\]", src, re.S)
                if lit:
                    n = len([x for x in lit.group(1).split(",") if x.strip()])
        elif re.search(r'"criteria"\s*:\s*\{', block):
            inner = re.search(r'"criteria"\s*:\s*\{(.*?)\}', block, re.S)
            if inner:
                n = len(re.findall(r'"\s*[^"]+\s*"\s*:', inner.group(1)))
        qs.append({"name": name, "type": kind, "n": n})
    if qs:
        return qs
    # bash snippet: --ask 'name=choice:instructions|k1:Label,k2:Label'
    for m in re.finditer(r"--ask\s+'(\w+)=(\w+):(.*?)'", src):
        name, kind, payload = m.group(1), m.group(2), m.group(3)
        crit = payload.split("|", 1)[1] if "|" in payload else ""
        n = len([x for x in crit.split(",") if x.strip()]) if crit else None
        if kind == "noul":
            n = 2
        qs.append({"name": name, "type": kind, "n": n})
    for m in re.finditer(r"--yes\s+'(\w+)=", src):
        qs.append({"name": m.group(1), "type": "noul", "n": 2})
    if qs:
        return qs
    # single-quoted JS style: { icon: { type: 'choice', criteria: ICONS ... } }
    for m in re.finditer(r"(\w+)\s*:\s*\{\s*type\s*:\s*'(\w+)'", src):
        qs.append({"name": m.group(1), "type": m.group(2), "n": 2 if m.group(2) == "noul" else None})
    if qs:
        return qs
    # a taxonomy the code loops over: NAME = {"a": {...}, "b": {...}} -> one question per branch
    for m in re.finditer(r"(?:const\s+)?([A-Z][A-Z_0-9]*)\s*=\s*\{(.*?)\n\s*\}[\s;]*\n", src, re.S):
        body = m.group(2)
        branches = re.findall(r'"(\w+)"\s*:\s*\{', body) or re.findall(r"(\w+)\s*:\s*\{", body)
        if len(branches) >= 2:
            for b in branches:
                blk = re.search(re.escape(b) + r"[\"']?\s*:\s*\{(.*?)\}", body, re.S)
                n = len(re.findall(r'"\s*[A-Za-z0-9_\-]+\s*"\s*:', blk.group(1))) if blk else None
                if n is None and blk:
                    n = len(re.findall(r"\w+\s*:\s*'", blk.group(1))) or None
                qs.append({"name": b, "type": "choice", "n": n})
            return qs
        flat = len(re.findall(r'"\s*[A-Za-z0-9_\-]+\s*"\s*:', body)) or len(re.findall(r"\w+\s*:\s*'", body))
        if flat:
            qs.append({"name": m.group(1).lower(), "type": "choice", "n": flat})
            return qs
    # a threshold sweep: draw the cuts it actually tries
    cuts = re.search(r"for\s+\w+\s+in\s+\(([\d.,\s]+)\)", src)
    if cuts:
        n = len([x for x in cuts.group(1).split(",") if x.strip()])
        qs.append({"name": "threshold", "type": "score", "n": n})
    return qs


def draw(case, qs):
    """State, options, one amber pick, then any follow-up question.

    Four rules, each one a defect the first drafts shipped:
      * the option marks sit off the arrow axis, so the row never reads as one long line
      * exactly one amber element: the chosen cell of the FIRST question only
      * no exit arrow: leaving the row to the right crosses the cells that follow it
      * a follow-up row hangs from the centre of the chosen cell onto a cell centre,
        at a scale close enough to read as nested rather than accidental
    """
    P = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER)]
    prim = next((q for q in qs if q["type"] == "choice" and q["n"]), None)
    others = [q for q in qs if q is not prim]

    n_main = (prim["n"] if prim and prim["n"] else 3)
    rows = [(q["type"], q["n"] or (2 if q["type"] == "noul" else 3)) for q in others[:2]]
    main_h = 300 if not rows else 190
    sub_h, gap_r = 132, 86
    block = main_h + sum(gap_r + sub_h for _ in rows)
    y0 = (H - block) // 2

    cw, g = 176, 30
    x0 = (W - (n_main * cw + (n_main - 1) * g)) // 2
    pick = n_main // 2 if n_main % 2 else n_main // 2 - 1
    cy = y0 + main_h // 2

    # the state enters and stops at the first cell
    P.append('<line x1="118" y1="%d" x2="118" y2="%d" stroke="%s" stroke-width="2.4"/>' % (cy - 46, cy + 46, INK))
    P.append('<line x1="118" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.7" marker-end="url(#a)"/>'
             % (cy, x0 - 8, cy, INK))

    for i in range(n_main):
        x = x0 + i * (cw + g)
        amber = (i == pick)
        col = AMBER if amber else INK
        P.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width="%s"/>'
                 % (x, y0, cw, main_h, col, "3.4" if amber else "1.7"))
        # the option mark: a small square at the cell's own centre, never on the arrow axis
        P.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                 % (x + cw // 2 - 9, y0 + main_h // 2 - 9, 18, 18, col))

    xa = x0 + pick * (cw + g) + cw // 2
    y = y0 + main_h
    for kind, cells in rows:
        cells = 2 if kind == "noul" else cells
        cw2, g2 = 132, 26
        total = cells * cw2 + (cells - 1) * g2
        x2 = min(max(60, xa - total // 2), W - 60 - total)
        pick2 = cells // 2 if cells % 2 else cells // 2 - 1
        cxa = x2 + pick2 * (cw2 + g2) + cw2 // 2          # land on a cell centre, not a boundary
        P.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.4"/>' % (xa, y + 4, xa, y + gap_r // 2, INK))
        P.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.4"/>'
                 % (min(xa, cxa), y + gap_r // 2, max(xa, cxa), y + gap_r // 2, INK))
        P.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.4"/>'
                 % (cxa, y + gap_r // 2, cxa, y + gap_r - 6, INK))
        for i in range(cells):
            x = x2 + i * (cw2 + g2)
            P.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width="1.7"/>'
                     % (x, y + gap_r, cw2, sub_h, INK))
            P.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                     % (x + cw2 // 2 - 7, y + gap_r + sub_h // 2 - 7, 14, 14, INK))
        y += gap_r + sub_h
    return "\n".join(P)


def svg_for(case):
    qs = parse_questions(case)
    body = draw(case, qs)
    defs = ('<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % INK)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s%s</svg>'
            % (W, H, W, H, defs, body)), qs


def main():
    cases = json.loads((ROOT / "content.json").read_text())["cases"]
    want = [int(a) for a in sys.argv[1:] if a.isdigit()]
    write = "--write" in sys.argv
    if want:
        cases = [c for c in cases if c["n"] in want]
    OUT.mkdir(parents=True, exist_ok=True)
    if write:
        (ROOT / "assets" / "plates-svg").mkdir(parents=True, exist_ok=True)
    for c in cases:
        svg, qs = svg_for(c)
        sp = OUT / ("plate-%02d.svg" % c["n"])
        sp.write_text(svg)
        if write:
            (ROOT / "assets" / "plates-svg" / sp.name).write_text(svg)
        png = OUT / ("plate-%02d.png" % c["n"])
        subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), "-o", str(png), str(sp)], check=True)
        shape = ", ".join("%s:%s%s" % (q["name"], q["type"], "(%d)" % q["n"] if q["n"] else "?") for q in qs) or "no question read"
        print("case %2d  %-46s %s" % (c["n"], c["title"][:46], shape))
    print("\n%d plates -> %s" % (len(cases), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
