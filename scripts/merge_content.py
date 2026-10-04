#!/usr/bin/env python3
"""Merge the content parts into one content.json and report what is in it."""
import json
import pathlib

root = pathlib.Path(__file__).resolve().parent.parent
cases = []
for part in sorted((root / "content").glob("part*.json")):
    cases.extend(json.loads(part.read_text()))

cases.sort(key=lambda c: c["n"])
assert len(cases) == 19, "expected 19 cases, found %d" % len(cases)
assert len({c["slug"] for c in cases}) == 19, "duplicate slugs"
for c in cases:
    for field in ("n", "slug", "title", "tier", "at", "what", "shape", "use", "code", "prompts", "plate"):
        assert field in c, "case %s missing %s" % (c["n"], field)
    assert c["tier"] in ("easy", "intermediate", "advanced"), c["tier"]
    assert c["code"]["lang"] in ("python", "bash", "javascript"), c["code"]["lang"]

out = {"cases": cases}
(root / "content.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print("merged %d cases" % len(cases))
for c in cases:
    print("  %2d %-26s %-12s %s  prompts=%d code=%s" % (
        c["n"], c["slug"], c["tier"], c["at"], len(c["prompts"]), c["code"]["lang"]))
