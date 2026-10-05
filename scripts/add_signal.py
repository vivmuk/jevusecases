#!/usr/bin/env python3
"""Add findings to the Pulse feed, then rebuild the pages that show them.

Usage
    python3 scripts/add_signal.py new-items.json      # {"items": [ ... ]} or one item
    cat new-items.json | python3 scripts/add_signal.py -

Each item needs: kind (gap | insight | usecase | resource), source, author, title,
url, date, summary, takeaways (a list). "near" is the case number it touches, or
null when nothing on the site covers it, and "tags" is a short list of words.

The script is deliberately strict about the parts the page cannot render without,
and it refuses duplicates by url, so a weekly run can be re-run safely.
"""
import datetime
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIGNALS = ROOT / "signals.json"
REQUIRED = ("kind", "source", "author", "title", "url", "date", "summary")
KINDS = {"gap", "insight", "usecase", "resource"}


def key(url):
    return (url or "").strip().rstrip("/").lower()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raw = sys.stdin.read() if sys.argv[1] == "-" else pathlib.Path(sys.argv[1]).read_text()
    payload = json.loads(raw)
    incoming = payload.get("items", [payload]) if isinstance(payload, dict) else payload
    if not isinstance(incoming, list):
        sys.exit("expected a list of items, or an object with an items list")

    store = json.loads(SIGNALS.read_text())
    have = {key(i["url"]) for i in store["items"]}
    nxt = max([int(i["id"].split("-")[-1]) for i in store["items"]] or [0])

    added, skipped, bad = [], [], []
    for item in incoming:
        missing = [k for k in REQUIRED if not str(item.get(k, "")).strip()]
        if missing:
            bad.append((item.get("title", "?"), "missing " + ", ".join(missing)))
            continue
        if item["kind"] not in KINDS:
            bad.append((item.get("title", "?"), "kind must be one of " + ", ".join(sorted(KINDS))))
            continue
        if not isinstance(item.get("takeaways"), list) or not item["takeaways"]:
            bad.append((item.get("title", "?"), "needs a non-empty takeaways list"))
            continue
        if key(item["url"]) in have:
            skipped.append(item["title"])
            continue
        nxt += 1
        item = dict(item)
        item["id"] = "sig-%03d" % nxt
        item.setdefault("near", None)
        item.setdefault("tags", [])
        store["items"].append(item)
        have.add(key(item["url"]))
        added.append(item)

    if bad:
        print("refused %d item(s):" % len(bad))
        for t, why in bad:
            print("  -", t, ":", why)
    if not added:
        print("nothing new (duplicates skipped: %d)" % len(skipped))
        return sys.exit(1 if bad else 0)

    store["updated"] = datetime.date.today().isoformat()
    store["items"].sort(key=lambda i: i.get("date", ""), reverse=True)
    SIGNALS.write_text(json.dumps(store, indent=2, ensure_ascii=False) + "\n")
    print("added %d item(s), skipped %d duplicate(s), feed now holds %d"
          % (len(added), len(skipped), len(store["items"])))
    for s in ("scripts/build_pulse.py", "scripts/build_page.py", "scripts/build_readme.py"):
        r = subprocess.run([sys.executable, str(ROOT / s)], cwd=str(ROOT), capture_output=True, text=True)
        print(" ", s, "->", (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else "ok")


if __name__ == "__main__":
    main()
