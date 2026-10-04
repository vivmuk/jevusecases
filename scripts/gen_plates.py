#!/usr/bin/env python3
"""Generate the 19 infographic plates with the muse-image model.

One style preamble reused verbatim in every prompt is what makes the set look
like one shoot. Writes assets/plates/plate-NN.png, skips files that already
exist, and refuses to keep a blank render (blank = flat image, sd ~ 0).
"""
import base64
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "plates"
OUT.mkdir(parents=True, exist_ok=True)
MODEL = os.environ.get("PLATE_MODEL", "muse-image")
ENDPOINT = "https://api.venice.ai/api/v1/image/generate"

STYLE = (
    "Minimalist editorial diagram printed on light paper, flat vector geometry only. "
    "Thin even strokes, solid fills, no gradients, no perspective, no photographic shading, "
    "no 3D, no clay, no glow, no drop shadow. Palette: near-black ink #15181C lines on a "
    "cool light grey paper ground #F1F2F4, with a single deep amber #B4721A accent used on "
    "exactly one element. Generous negative space, centred composition, wide even margins, "
    "quiet and precise, like a page from a technical manual. Scene: {scene} "
    "Absolutely no text, no letters, no numbers, no words, no captions, no labels, no "
    "watermark, no logo, no signature, no initials, no people, no faces, no emoji. "
    "The picture is unsigned, unlettered and unlabelled."
)


def key():
    for name in ("VENICE_API_KEY", "VENICE_INFERENCE_KEY",
                 "HERMES_CUSTOM_API_VENICE_AI_API_KEY"):
        if os.environ.get(name):
            return os.environ[name].strip()
    env = pathlib.Path.home() / ".hermes" / ".env"
    for line in env.read_text().splitlines():
        k, _, v = line.partition("=")
        if k.strip() in ("VENICE_API_KEY", "VENICE_INFERENCE_KEY",
                         "HERMES_CUSTOM_API_VENICE_AI_API_KEY"):
            return v.strip().strip('"').strip("'")
    raise SystemExit("no Venice key found")


def generate(prompt, dest, tries=3):
    body = json.dumps({"model": MODEL, "prompt": prompt,
                       "aspect_ratio": "16:9", "format": "png",
                       "safe_mode": False}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Authorization": "Bearer " + key(),
                 "Content-Type": "application/json"})
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            images = data.get("images") or []
            if not images:
                raise RuntimeError("no images in response: %s" % str(data)[:200])
            raw = base64.b64decode(images[0])
            tmp = dest.with_suffix(".tmp.png")
            tmp.write_bytes(raw)
            # guard: a blank render answers HTTP 200 with a flat picture
            probe = subprocess.run(
                ["magick", "identify", "-format", "%w %h %[standard-deviation]",
                 str(tmp)], capture_output=True, text=True)
            w, h, sd = probe.stdout.split()
            if int(w) < 400 or int(h) < 200 or float(sd) < 500:
                raise RuntimeError("blank or tiny render (w=%s h=%s sd=%s)" % (w, h, sd))
            tmp.replace(dest)
            return int(w), int(h), os.path.getsize(dest)
        except Exception as exc:  # noqa: BLE001
            print("  attempt %d failed for %s: %s" % (attempt, dest.name, exc),
                  flush=True)
            time.sleep(3 * attempt)
    return None


def main():
    cases = json.loads((ROOT / "content.json").read_text())["cases"]
    only = sys.argv[1:] or None
    ok, failed = 0, []
    for case in cases:
        if only and str(case["n"]) not in only:
            continue
        dest = OUT / ("plate-%02d.png" % case["n"])
        if dest.exists():
            print("%2d skip (exists) %s" % (case["n"], dest.name), flush=True)
            ok += 1
            continue
        print("%2d %s" % (case["n"], case["slug"]), flush=True)
        res = generate(STYLE.format(scene=case["plate"]), dest)
        if res:
            print("   ok %dx%d %.0f KB" % (res[0], res[1], res[2] / 1024), flush=True)
            ok += 1
        else:
            print("   FAILED", flush=True)
            failed.append(case["n"])
    print("done: %d ok, failed %s" % (ok, failed or "none"), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
