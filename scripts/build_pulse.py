#!/usr/bin/env python3
"""Build pulse.html: what the field is saying about Jev, gathered weekly.

Reads signals.json (seeded here, extended by the Tuesday sweep and by
scripts/add_signal.py) and renders it as a timeline. The look is a feed; the
reading is set for someone who finds dense text hard, via pulse.css.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIGNALS = ROOT / "signals.json"
OUT = ROOT / "pulse.html"

KINDS = {
    "gap": "Jobs no case covers yet",
    "insight": "New learning",
    "usecase": "Working example",
    "resource": "Where to read more",
}


def esc(t):
    return html.escape(str(t if t is not None else ""), quote=True)


def nice_date(stamp):
    """2026-10-05 -> 5 October 2026, so a date reads the same everywhere."""
    months = ("January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(stamp))
    if not m:
        return stamp
    y, mo, d = m.groups()
    return "%d %s %s" % (int(d), months[int(mo) - 1], y)


def initials(author):
    name = (author or "?").replace("@", "").replace("/", " ").replace("\u00b7", " ")
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def post_html(it, titles):
    near = it.get("near")
    if near:
        where = ('<a class="chip chip--near" href="index.html#case-%s">Touches case %02d: %s</a>'
                 % (near, int(near), esc(titles.get(int(near), "a case on the site"))))
    elif it["kind"] == "gap":
        where = '<span class="chip chip--missing">No case on the site covers this today</span>'
    else:
        where = ""
    takes = "".join("<li>%s</li>" % esc(t) for t in it.get("takeaways", []))
    tags = "".join('<span class="tag">#%s</span>' % esc(t) for t in it.get("tags", []))
    name = it.get("author") or it.get("source") or "source"
    return "\n".join([
        '<article class="post" id="%s" data-kind="%s">' % (esc(it["id"]), esc(it["kind"])),
        '  <div class="post__ava ava--%s" aria-hidden="true">%s</div>' % (esc(it["kind"]), esc(initials(it.get("handle") or name))),
        '  <div class="post__body">',
        '    <p class="post__who"><span class="post__name">%s</span>' % esc(name),
        '      <span class="post__handle">%s</span>' % esc(it.get("source")),
        '      <span class="post__date">%s</span></p>' % esc(it.get("date")),
        '    <h2 class="post__title">%s</h2>' % esc(it["title"]),
        '    <p class="post__sum">%s</p>' % esc(it["summary"]),
        '    <p class="post__label">Key takeaways</p>',
        '    <ul class="post__take">%s</ul>' % takes,
        '    <p class="post__meta">%s' % where,
        '      <span class="chip chip--kind">%s</span>' % esc(KINDS[it["kind"]]),
        '      <span class="post__tags">%s</span>' % tags,
        '      <a class="post__link" href="%s" rel="noreferrer">Read the source &rarr;</a></p>' % esc(it["url"]),
        '  </div>',
        '</article>',
    ])


def main():
    data = json.loads(SIGNALS.read_text())
    items = data["items"]
    content = json.loads((ROOT / "content.json").read_text())
    cases = content["cases"] if isinstance(content, dict) else content
    titles = {int(c["n"]): c["title"] for c in cases}

    order = {"gap": 0, "insight": 1, "usecase": 2, "resource": 3}
    items = sorted(items, key=lambda i: (order.get(i["kind"], 9), i.get("date", "")))
    counts = {k: sum(1 for i in items if i["kind"] == k) for k in KINDS}
    gaps = counts["gap"]

    chips = ['<button type="button" class="filt" data-filter="all" aria-pressed="true">Everything <b>%d</b></button>'
             % len(items)]
    for k in ("gap", "insight", "usecase", "resource"):
        if counts[k]:
            chips.append('<button type="button" class="filt" data-filter="%s" aria-pressed="false">%s <b>%d</b></button>'
                         % (k, esc(KINDS[k]), counts[k]))

    head = [
        '<!DOCTYPE html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>Pulse: what the field is saying about Jev</title>',
        '<meta name="description" content="A weekly sweep of what people write about the Jev decision model: new use cases, new findings, and the jobs the nineteen cases do not cover yet.">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
        '<link rel="stylesheet" href="pulse.css">', '</head>', '<body>',
        '<div class="bar">',
        '<a class="mark" href="index.html">Jev <span aria-hidden="true">/</span> use cases</a>',
        '<span class="spacer"></span>',
        '<span class="sizelabel" aria-hidden="true">Text size</span>',
        '<button type="button" data-size-btn="0" aria-pressed="true" aria-label="Normal text size">A</button>',
        '<button type="button" data-size-btn="1" aria-pressed="false" aria-label="Larger text">A+</button>',
        '<button type="button" data-size-btn="2" aria-pressed="false" aria-label="Largest text">A++</button>',
        '<a class="btn" href="about.html">About Jev</a>',
        '<a class="btn" href="index.html">The cases</a>',
        '</div>', '<main>',
        '<div class="hero"><img src="assets/forest/hero.webp" width="2000" height="1125" alt="">',
        '<h1>Pulse</h1></div>',
        '<p class="lede">What people are writing, building and arguing about with the Jev decision model: the jobs nobody has listed yet, the findings from the first independent tests, and the places to read more. <strong>Every entry links to its source.</strong> The sweep runs each Tuesday morning, so this page is always the most recent pass.</p>',
        '<p class="count">Last collected %s. %d entries, and %d of them are jobs no case here covers yet.</p>'
        % (nice_date(data.get("updated", "")), len(items), gaps),
        '<p class="count">%s</p>'
        % esc(data.get("collector", "")),
        '<hr class="rule">',
        '<div class="controls" role="group" aria-label="Filter the entries">', "".join(chips), '</div>',
        '<p class="count" id="shown" aria-live="polite">All %d entries are shown.</p>' % len(items),
        '<div class="feed" id="feed">',
    ]
    body = [post_html(it, titles) for it in items]
    tail = [
        '</div>', '</main>', '<footer>',
        '<p>Gathered from X, YouTube, Reddit, Hacker News, the official documentation and the blogs that cover the model. Nothing here is repeated from the nineteen cases unless it adds something to them; a link marked as not covered is a job the collection is missing.</p>',
        '<p>Jev is made by TypeSafe AI. This page is an independent reading of public sources and is not affiliated with TypeSafe.</p>',
        '</footer>', '<script>',
        'var btns = document.querySelectorAll("[data-size-btn]"), html = document.documentElement;',
        'function setSize(l){ if(l==="0"){html.removeAttribute("data-size");} else {html.setAttribute("data-size", l);}',
        '  btns.forEach(function(b){ b.setAttribute("aria-pressed", String(b.getAttribute("data-size-btn")===l)); });',
        '  try { localStorage.setItem("jev-text-size", l); } catch(e){} }',
        'btns.forEach(function(b){ b.addEventListener("click", function(){ setSize(b.getAttribute("data-size-btn")); }); });',
        'try { var s = localStorage.getItem("jev-text-size"); if (s) setSize(s); } catch(e){}',
        'var posts = document.querySelectorAll(".post"), filts = document.querySelectorAll(".filt"), shown = document.getElementById("shown");',
        'var words = {all:"Showing all", gap:"Showing the jobs not covered", insight:"Showing new learnings", usecase:"Showing working examples", resource:"Showing further reading"};',
        'filts.forEach(function(f){ f.addEventListener("click", function(){',
        '  var want = f.getAttribute("data-filter"), n = 0;',
        '  filts.forEach(function(o){ o.setAttribute("aria-pressed", String(o===f)); });',
        '  posts.forEach(function(p){ var on = (want==="all") || (p.getAttribute("data-kind")===want); p.hidden = !on; if(on) n++; });',
        '  shown.textContent = (words[want] || "Showing") + " " + n + (n===1 ? " entry" : " entries");',
        '}); });',
        '</script>', '</body>', '</html>',
    ]
    OUT.write_text("\n".join(head + body + tail))
    print("wrote %s, %d bytes, %d items (%d gaps)" % (OUT.name, OUT.stat().st_size, len(items), gaps))


if __name__ == "__main__":
    main()
