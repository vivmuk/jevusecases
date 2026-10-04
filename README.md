# Jev use cases

Nineteen closed-answer jobs for a decision model, one card each: what the decision
is, the code that asks it, and the prompts that run it. The site is a single static
page whose scroll is the timeline, with one generated diagram per case.

## What is in here

| Path | What it is |
|---|---|
| `index.html` | the built page (generated, do not hand-edit) |
| `scrollcraft.js`, `scrollcraft.css` | the scroll engine, copied from the scrollcraft skill and never edited per project |
| `site.css`, `site.js` | the page's own layer: tokens, the ledger rail, the index panel, copy buttons |
| `content/part*.json` | the nineteen cases, written by hand, merged by `scripts/merge_content.py` |
| `content.json` | the merged source of truth for the cards |
| `data/anatomy.json` | a real Jev response, captured live, used by the anatomy act |
| `scripts/gen_plates.py` | generates the nineteen plates with the `muse-image` model |
| `scripts/build_page.py` | renders `index.html` from `content.json` |
| `server.js` | zero-dependency static server used in production |

## Rebuild

```bash
python3 scripts/merge_content.py      # content/part*.json -> content.json
python3 scripts/gen_plates.py         # assets/plates/plate-NN.png (skips what exists)
python3 scripts/build_page.py         # content.json -> index.html
node server.js                        # serve on $PORT, default 3000
```

Plate generation reads a Venice key from `VENICE_API_KEY` or from `~/.hermes/.env`.
It refuses to keep a blank render, and every plate is checked for a live standard
deviation before it lands.

## The numbers on the page

The case list, its order and the running times come from
"These 19 Jev-Claude use cases are blowing people's minds" (youtube.com/watch?v=3iDiWTt8lok).
Anything quoted from the video says so on the card that uses it. The latency, token
count and cost figures were measured on the machine that built the page, against the
live route.
