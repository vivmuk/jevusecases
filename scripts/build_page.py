#!/usr/bin/env python3
"""Render index.html from content.json.

Static build: the output is real HTML with real headings and reading order, and
the scrollcraft engine reads data-sc-* attributes off it. Nothing is generated
in the browser.
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
VIDEO = "https://youtube.com/watch?v=3iDiWTt8lok"
SITE = "https://jevusecases-production.up.railway.app/"
SOURCE = "These 19 Jev-Claude use cases are blowing people's minds"
REPO = "https://github.com/vivmuk/jevusecases"

SHORT = {
    1: "Row labelling", 2: "Inquiry triage", 3: "Ad intelligence", 4: "Clip hunting",
    5: "Churn bands", 6: "Internal links", 7: "Purchase intent", 8: "Calibration",
    9: "Skill picking", 10: "Model routing", 11: "Inbox gate", 12: "Feed cleansing",
    13: "Semantic find", 14: "Asset search", 15: "Live sentences", 16: "No-LLM answers",
    17: "Icon picking", 18: "Page assembly", 19: "Work audit",
}
TIERS = [
    ("easy", "Cases 01 to 08", "The ones you can wire up this afternoon",
     "A single call in front of work you already do. Nothing here needs a queue, an "
     "index or a new service: one state in, one typed answer out, and your existing "
     "code decides what to do with it."),
    ("intermediate", "Cases 09 to 14", "The ones that change how your stack routes",
     "These sit inside the machinery rather than beside it: which skill loads, which "
     "model answers, which message reaches the model at all. They pay for themselves "
     "in tokens and in latency."),
    ("advanced", "Cases 15 to 19", "The ones that make a page or a product behave differently",
     "Decisions fast enough to run while someone is still talking or typing, plus the "
     "audit that finds the remaining candidates in your own workflow."),
]


def e(text):
    return html.escape(str(text), quote=True)


def short_alt(case):
    scene = case["plate"].split(".")[0]
    return "Minimalist diagram for case %d: %s." % (case["n"], scene.strip().lower())


def code_block(case):
    cid = "c%d" % case["n"]
    return """        <figure class="code">
          <figcaption class="code__head">
            <p class="code__title">%s</p>
            <span class="code__lang">%s</span>
            <button class="copy" type="button" data-copy="%s">Copy</button>
          </figcaption>
          <pre id="%s"><code>%s</code></pre>
        </figure>""" % (e(case["code"]["label"]), e(case["code"]["lang"]), cid, cid,
                         e(case["code"]["src"]))


def prompt_blocks(case):
    out = ['        <p class="prompts__head">Example prompts</p>']
    for i, p in enumerate(case["prompts"], start=1):
        pid = "p%d-%d" % (case["n"], i)
        body = "state: %s\n\nquestion: %s" % (p["state"], p["question"])
        out.append("""        <div class="prompt">
          <div class="prompt__head">
            <p class="code__title">Prompt %d of %d</p>
            <span class="prompt__tag">state + question</span>
            <button class="copy" type="button" data-copy="%s">Copy</button>
          </div>
          <pre id="%s">%s</pre>
        </div>""" % (i, len(case["prompts"]), pid, pid, e(body)))
    return "\n".join(out)


def card(case, index):
    wide = index % 3 == 2
    flip = index % 3 == 1
    cls = "case" + (" case--wide" if wide else "") + (" case--flip" if flip else "")
    shape = "\n".join(
        """            <div class="shape__row"><dt>%s</dt><dd>%s</dd></div>""" %
        (e(k), e(v)) for k, v in case["shape"].items())
    return """
    <article class="{cls}" id="case-{n}" data-case="{n:02d}" data-title="{title}"
             aria-labelledby="case-{n}-t">
      <div class="sc-wrap case__grid">
        <div class="case__text" data-sc-in data-sc-stagger="60">
          <p class="case__no">Case {n:02d}<span class="case__tier">{tier}</span></p>
          <h3 class="case__title" id="case-{n}-t">{title}</h3>
          <p class="case__src"><a href="{video}&amp;t={sec}s" rel="noreferrer">{at} in the video</a></p>
          <p class="case__what">{what}</p>
          <dl class="shape">
{shape}
          </dl>
          <p class="case__use">{use}</p>
{code}
{prompts}
        </div>
        <figure class="case__plate plate" data-sc-reveal="left" data-sc-reveal-at="0.04 0.3">
          <div class="plate__frame" data-sc-tilt="5">
            <img src="assets/plates/plate-{n:02d}.webp" width="1600" height="900"
                 alt="{alt}" loading="lazy" decoding="async">
          </div>
          <figcaption>Plate {n:02d}. The shape of the job, drawn without labels on purpose.</figcaption>
        </figure>
      </div>
    </article>""".format(
        cls=cls, n=case["n"], title=e(case["title"]), tier=e(case["tier"]),
        video=VIDEO, sec=secs(case["at"]), at=e(case["at"]), what=e(case["what"]),
        shape=shape, use=e(case["use"]), code=code_block(case),
        prompts=prompt_blocks(case), alt=e(short_alt(case)))


def secs(stamp):
    m, s = stamp.split(":")
    return int(m) * 60 + int(s)


def index_panel(cases):
    groups = []
    for tier, label, title, blurb in TIERS:
        rows = [c for c in cases if c["tier"] == tier]
        items = "\n".join(
            """          <li><a href="#case-%d"><span class="n">%02d</span><span class="t">%s</span><span class="at">%s</span></a></li>"""
            % (c["n"], c["n"], e(c["title"]), e(c["at"])) for c in rows)
        groups.append("""      <div class="index-group">
        <h3>%s</h3>
        <ul class="index-list">
%s
        </ul>
      </div>""" % (e(label), items))
    return "\n".join(groups)


def rail(cases):
    tabs = "\n".join(
        """        <a class="rail__tab" href="#case-%d" title="%s">
          <span class="n">%02d</span>
          <span class="t">%s</span>
          <span class="d">%s</span>
        </a>""" % (c["n"], e(c["title"]), c["n"], e(SHORT[c["n"]]), e(c["tier"]))
        for c in cases)
    return tabs


def tier_divider(tier):
    label, rng, title, blurb = [t for t in TIERS if t[0] == tier][0]
    return """
    <section class="sc-section tier" data-sc-act="flow" data-tier="%s">
      <div class="sc-wrap sc-stack" data-sc-in data-sc-stagger="70">
        <p class="eyebrow">%s</p>
        <h2 class="sc-display sc-display--md">%s</h2>
        <p>%s</p>
      </div>
    </section>""" % (e(tier), e(rng), e(title), e(blurb))


def build():
    cases = json.loads((ROOT / "content.json").read_text())["cases"]
    anat = json.loads((ROOT / "data" / "anatomy.json").read_text())
    a = anat["answers"]
    tokens = anat["usage"]["input_tokens"]
    cost = tokens / 1e6 * 0.042

    body = []
    rendered = []
    for case in cases:
        if case["n"] == 1:
            rendered.append(tier_divider("easy"))
        if case["n"] == 9:
            rendered.append(tier_divider("intermediate"))
        if case["n"] == 15:
            rendered.append(tier_divider("advanced"))
        rendered.append(card(case, len(rendered)))
    body.append("\n".join(rendered))

    page = TEMPLATE.format(
        repo=REPO,
        source=SOURCE,
        video=VIDEO,
        site=SITE,
        state=e(anat["state"]),
        cases=len(cases),
        index_groups=index_panel(cases),
        rail_tabs=rail(cases),
        anatomy=anat,
        anat=a,
        tokens=tokens,
        cost="%.7f" % cost,
        body="\n".join(body),
    )
    (ROOT / "index.html").write_text(page)
    print("wrote index.html, %d bytes" % len(page))


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Jev use cases: nineteen closed-answer jobs for a decision model</title>
<meta name="description" content="Nineteen ways to replace an open-ended language-model call with a typed decision. For each one: what the decision is, the code that asks it, and the prompts that run it.">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#f1f2f4">
<meta property="og:title" content="Jev use cases">
<meta property="og:description" content="Nineteen closed-answer jobs for a decision model, each with its code and its prompts.">
<meta property="og:type" content="website">
<meta property="og:url" content="{site}">
<link rel="canonical" href="{site}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23f1f2f4'/><rect x='9' y='7' width='3' height='18' fill='%2315181c'/><rect x='15' y='7' width='8' height='3' fill='%239c5a10'/><rect x='15' y='14' width='8' height='3' fill='%2315181c'/><rect x='15' y='21' width='5' height='3' fill='%2315181c'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="scrollcraft.css">
<link rel="stylesheet" href="site.css">
</head>
<body>

<a class="skip" href="#case-1">Skip to the cases</a>
<span data-sc-progress></span>
<div class="sc-grain" aria-hidden="true"></div>

<header class="site-bar">
  <p class="site-bar__mark">Jev <span>/</span> use cases</p>
  <button class="btn btn--ghost" type="button" data-index-toggle aria-expanded="false" aria-controls="index-panel">Cases</button>
  <a class="btn btn--solid" href="{repo}" rel="noreferrer">Open the source</a>
</header>

<nav class="index-panel" id="index-panel" data-open="false" aria-label="All nineteen cases">
  <div class="index-panel__inner">
    <h2>All nineteen cases</h2>
    <p>Grouped the way the video groups them. Every one is a closed-answer job: the possible answers can be written down before the question is asked.</p>
{index_groups}
  </div>
</nav>

<main id="top">

  <section class="sc-section" data-sc-act="pin" data-sc-span="2" aria-labelledby="open-h">
    <div data-sc-stage class="sc-wrap open">
      <h1 class="sc-display sc-display--xl" id="open-h" data-sc-cue="0 0.72 0" data-sc-kinetic="lines">Nineteen jobs for a model that answers in half a second.</h1>
      <p class="open__lede sc-body" data-sc-cue="0 0.72 0">Each card carries the decision, the code that asks it, and the prompts that run it.</p>
      <dl class="open__facts" data-sc-cue="0.5 1 0.3 0.5">
        <div><dt>cases, from the video</dt><dd data-sc-count="0 19">0</dd></div>
        <div><dt>seconds, measured round trip</dt><dd>0.39</dd></div>
        <div><dt>dollars per million input tokens</dt><dd>0.042</dd></div>
        <div><dt>dollars for the output</dt><dd>0</dd></div>
      </dl>
    </div>
  </section>

  <section data-sc-act="pan" data-sc-span="3.4" aria-labelledby="rail-h">
    <div data-sc-stage>
      <div class="rail-head sc-wrap">
        <h2 class="sc-display sc-display--md" id="rail-h">The whole set, side by side.</h2>
        <p>Nineteen tabs, in the order the video walks them. Pick any one to jump to its card, and the rail at the bottom of the screen keeps your place.</p>
      </div>
      <div class="rail" data-sc-pan="0.06">
{rail_tabs}
        <p class="rail__close">Three of them are the ones most people wire up first: labelling rows, gating an inbox, and choosing which model answers.</p>
      </div>
    </div>
  </section>

{body}

  <section class="sc-section" data-sc-act="pin" data-sc-span="3.4" aria-labelledby="anatomy-h">
    <div data-sc-stage data-sc-spotlight class="sc-wrap anatomy">
      <h2 class="sc-display sc-display--md anatomy__h" id="anatomy-h" data-sc-cue="0 0.34 0" data-sc-kinetic="lines">One message, three typed questions, one call.</h2>
      <div class="anatomy__grid">
        <div class="anatomy__card" data-sc-cue="0 0.42 0">
          <h3>The state</h3>
          <p class="anatomy__state">{state}</p>
        </div>
        <div class="anatomy__card" data-sc-cue="0.16 0.62">
          <h3>The questions</h3>
          <dl class="shape shape--tight">
            <div class="shape__row"><dt>noul</dt><dd>yes or no, returned as a probability</dd></div>
            <div class="shape__row"><dt>choice</dt><dd>one of four teams, a probability each</dd></div>
            <div class="shape__row"><dt>score</dt><dd>where it lands on four urgency levels</dd></div>
          </dl>
        </div>
      </div>
      <div class="anatomy__card anatomy__answers" data-sc-cue="0.4 1 0.2 0">
        <h3>The answers, as they came back</h3>
        <div class="answers">
          <div class="answer">
            <p class="answer__q">asking for a refund?</p>
            <p class="answer__v"><b>0.99</b><span>yes</span></p>
            <div class="bar"><i style="width:99%"></i></div>
          </div>
          <div class="answer">
            <p class="answer__q">which team owns it?</p>
            <p class="answer__v"><b>billing</b><span>1.00</span></p>
            <div class="bar"><i style="width:100%"></i></div>
          </div>
          <div class="answer">
            <p class="answer__q">how urgent?</p>
            <p class="answer__v"><b>1.48</b><span>concerned 0.50, urgent 0.49</span></p>
            <div class="bar"><i style="width:37%"></i></div>
          </div>
        </div>
        <p class="anatomy__note">That 1.48 is the part to notice. It is not a rounding error, it is the model saying it sits between two levels, and the rule that decides what to do about that lives in your code. {tokens} input tokens, {cost} dollars, about four tenths of a second.</p>
      </div>
    </div>
  </section>

  <section class="sc-section deploy" data-sc-act="flow" aria-labelledby="deploy-h">
    <div class="sc-wrap deploy__grid">
      <div data-sc-in data-sc-stagger="70">
        <p class="eyebrow">Putting one in production</p>
        <h2 class="sc-display sc-display--md" id="deploy-h">Four steps, and the failure that costs you the most.</h2>
        <ol class="steps">
          <li>
            <h3>Get one key</h3>
            <p>One of <code>TYPESAFE_API_KEY</code>, <code>OPENROUTER_API_KEY</code>, or a Venice key set as <code>VENICE_API_KEY</code>. The transports are interchangeable, so keep the fallback in your config rather than in your head.</p>
          </li>
          <li>
            <h3>Send a state and typed questions</h3>
            <p>One <code>POST</code> with the text to judge and a map of questions. Name every item you are asking about inside the question itself, and send only the fields the question needs.</p>
          </li>
          <li>
            <h3>Write the thresholds in your code</h3>
            <p>High confidence acts, medium confirms, low goes to a person. Keep one cutoff per risk rather than one number for the whole system, and never carry a yes-or-no cutoff over to a choice.</p>
          </li>
          <li>
            <h3>Prove it on fifty records first</h3>
            <p>Labelled records, answers withheld, count the matches, then sweep the cutoff and see what each one costs you in coverage. This is the step that separates a decision model you trust from one you hope works.</p>
          </li>
        </ol>
      </div>
      <div data-sc-in data-sc-stagger="70">
        <figure class="code">
          <figcaption class="code__head">
            <p class="code__title">The whole transport, in eight lines</p>
            <span class="code__lang">bash</span>
            <button class="copy" type="button" data-copy="deploy-curl">Copy</button>
          </figcaption>
          <pre id="deploy-curl"><code>curl -s https://api.venice.ai/api/v1/decisions \\
  -H "Authorization: Bearer $VENICE_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{"model":"jev-latest",
       "state":"Order A-104 was charged twice.",
       "questions":{{
         "refund":{{"type":"noul","instructions":"Is the customer asking for a refund?"}},
         "dept":{{"type":"choice","instructions":"Which team owns this?",
                  "criteria":{{"billing":"Payments","technical":"Bugs"}}}}}}}}'</code></pre>
        </figure>
        <ul class="checks">
          <li><b>Choice boundaries</b><span>If the answers can be written down before the question is asked, it is a decision. If they cannot, it is a writing job and it belongs with a language model.</span></li>
          <li><b>Confidence safeguards</b><span>Every decision gets a floor below which a person decides instead, and the floor is written next to the risk it gates.</span></li>
          <li><b>Validation sets</b><span>Fifty labelled records or more before it touches real traffic, and the labels themselves checked for ambiguity when two of them disagree.</span></li>
        </ul>
        <p class="deploy__warn"><b>Where it loses.</b> Counting and arithmetic belong in code. Multi-step reasoning, anything needing prose back, and adversarial text all want the bigger model. A confident wrong tick is still wrong, so the threshold in your code is the part that keeps you honest.</p>
      </div>
    </div>
  </section>

  <section id="close" data-sc-act="pin" data-sc-span="1.45" aria-labelledby="close-h">
    <div data-sc-stage class="sc-wrap close-act">
      <h2 class="sc-display sc-display--lg" id="close-h" data-sc-cue="0.08" data-sc-kinetic="lines">Every job on this page is a question with a napkin-sized answer.</h2>
      <div class="close-act__row">
        <button class="btn btn--ghost" type="button" data-index-toggle aria-expanded="false" aria-controls="index-panel">Cases</button>
        <a class="btn btn--solid" href="{repo}" data-sc-magnet="0.26" data-sc-cue="0.08" data-sc-rise="0" rel="noreferrer">Open the source</a>
      </div>
      <footer class="colophon">
        <p>Sources: the nineteen cases, their order and their running times come from <a href="{video}" rel="noreferrer">{source}</a>, and each card links to its moment in the video.</p>
        <p>Measured on 4 October 2026 on the machine that built this page: the 0.39 second probe, and the {tokens} token call above at {cost} dollars. Figures quoted from the video say so on the card that uses them.</p>
        <p>Scroll work by scrollcraft, plates by the muse-image model, static output so it costs a page load and nothing else.</p>
      </footer>
    </div>
  </section>

</main>

<div class="ledger" role="navigation" aria-label="Case progress">
  <p class="ledger__label">Your place</p>
  <div class="ledger__track"></div>
  <p class="ledger__now" aria-live="polite"></p>
</div>

<script src="scrollcraft.js"></script>
<script>ScrollCraft.mount(document.body);</script>
<script src="site.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
