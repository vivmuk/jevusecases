#!/usr/bin/env python3
"""Build about.html: what Jev is, and how to put it into a program.

Written for a reader who has not used a model before, and set for a reader who
finds dense text hard work: Atkinson Hyperlegible at a large size, wide line
spacing, short lines, no italics in the body, and a control that makes the text
bigger. The content is grounded in TypeSafe's own documentation and in the
independent notes and worked repositories listed at the foot of the page.

  python3 scripts/build_about.py
"""
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://jevusecases-production.up.railway.app"

SOURCES = [
    ("TypeSafe: launch note and docs", "https://docs.typesafe.ai/introduction",
     "The maker's own reference for the endpoint, the question types and the limits."),
    ("TypeSafe: jaggedness notes for Jev 1.13", "https://docs.typesafe.ai/model-jaggedness/jev-1.13",
     "The list of things Jev is known to get wrong, published by the maker."),
    ("Jev Model Guide", "https://jevmodel.org/use-cases",
     "Independent notes with runnable examples. Not affiliated with TypeSafe."),
    ("kenhuangus/jev-usecases", "https://github.com/kenhuangus/jev-usecases",
     "Worked implementations of most published use cases, with thresholds in code."),
    ("DataCamp: System One models explained", "https://www.datacamp.com/blog/system-one-models-jev",
     "A plain-language explainer of the category, the price and the latency claims."),
    ("The video this site is built from", "https://youtube.com/watch?v=3iDiWTt8lok",
     "Jay E | RoboNuggets walks the nineteen jobs with prompts."),
]

QUESTIONS = [
    ("choice", "Pick one option from a list you write out.",
     "Between 1 and 255 options. You get back the option that won, a probability for every "
     "option, and a confidence value."),
    ("score", "Place the text on an ordered scale.",
     "Between 2 and 10 levels. The answer can land between two levels. You also get the "
     "probability of each level."),
    ("noul", "Answer a yes or no statement.",
     "One number between 0 and 1: the estimated chance that the statement is true. There is no "
     "separate confidence value here."),
]

PREP = [
    ("A key, and somewhere to send the request",
     "The maker's endpoint is POST https://api.typesafe.ai/v1/systemone. Jev is also reachable "
     "through Venice and through OpenRouter, and the twenty prompts on this site use those routes."),
    ("The state", "The text you want judged, gathered from records you already have: one email, one "
                  "row, one meeting sentence, one comment."),
    ("The questions", "The closed sets of answers, written out in advance. If you cannot list the "
                      "answers, Jev is the wrong tool."),
    ("A rule for each probability", "What happens at 0.95, what happens at 0.6, what happens when it "
                                    "is unclear. That rule lives in your code, never in the model."),
]

RULES = [
    ("Keep the state clean.", "Fields the question does not need lower the accuracy. Send the "
                              "sentence, not the whole record."),
    ("Do not ask it to count, compare dates, or add up numbers.", "Jev reads instructions literally "
                                                                 "and is not reliable at those. Do "
                                                                 "them in code and pass the result in."),
    ("Test any text your users can write.", "A user-written field in the state can change the "
                                            "answer, so test that path before you trust it."),
    ("Raise the bar for expensive actions.", "A read-only lookup can run at a lower probability than "
                                             "a refund, a deletion, or a change of access."),
    ("If the probabilities come back flat, rewrite the options.", "A flat spread means your "
                                                                  "descriptions do not separate "
                                                                  "the choices well enough."),
]

WRONG_TOOL = [
    "Anything that has to be written: replies, code, summaries, reports. Use a writing model, then "
    "let Jev check the draft.",
    "Questions where the answers are not known in advance.",
    "Working out your own categories. You have to name them; it will not invent a good set for you.",
]

CODE = """import json, urllib.request

state = "I was charged twice for order A-104 and I want my money back."

questions = {
    "route":    "choice:billing:Payments,technical:Bugs,account:Login",
    "urgency":  "score:Calm,Concerned,Urgent,Emergency",
    "refund":   "yes:Is the customer asking for a refund?",
}

req = urllib.request.Request(
    "https://api.venice.ai/api/v1/decisions",
    data=json.dumps({"state": state, "questions": questions}).encode(),
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})

answer = json.loads(urllib.request.urlopen(req).read())

route = answer["route"]["choice"]          # the option that won
sure  = answer["route"]["probability"]     # how sure, from 0 to 1

if route == "billing" and sure > 0.9:
    refund_now()                           # your code acts, not the model
elif sure > 0.6:
    queue_for_review()
else:
    send_to_a_person()                     # low confidence goes to a human
"""


def dl(items, cls=""):
    rows = "\n".join(
        '      <div class="row"><dt>%s</dt><dd>%s</dd></div>' % (html.escape(t), d)
        for t, d in items)
    return '    <dl class="rows%s">\n%s\n    </dl>' % (cls, rows)


def page():
    q_rows = "\n".join(
        '      <div class="row"><dt><code>%s</code></dt><dd><strong>%s</strong> %s</dd></div>' % (k, t, d)
        for k, t, d in QUESTIONS)
    prep = "\n".join(
        '      <li><strong>%d. %s</strong><span>%s</span></li>' % (i, t, d)
        for i, (t, d) in enumerate(PREP, start=1))
    rules = "\n".join('      <li><strong>%s</strong> %s</li>' % (t, d) for t, d in RULES)
    wrong = "\n".join('      <li>%s</li>' % w for w in WRONG_TOOL)
    srcs = "\n".join(
        '      <li><a href="%s" rel="noreferrer">%s</a><span>%s</span></li>' % (u, html.escape(t), d)
        for t, u, d in SOURCES)

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>About Jev: what it is and how to use it</title>
<meta name="description" content="Jev is a decision model: you send text and a closed set of questions, and it returns one of your answers with a probability. A plain-language guide to what it is, how to call it, and where it goes wrong.">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#f5f1e8">
<link rel="canonical" href="{site}/about.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Lexend:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%%23f5f1e8'/><rect x='9' y='7' width='3' height='18' fill='%%231a2332'/><rect x='15' y='7' width='8' height='3' fill='%%23c25a17'/><rect x='15' y='14' width='8' height='3' fill='%%231a2332'/><rect x='15' y='21' width='5' height='3' fill='%%232c6b4f'/></svg>">
<style>
  :root {
    --paper: #f5f1e8; --ink: #1a2332; --ink-soft: #454d5a;
    --green: #245741; --orange: #b5500f; --line: rgba(26,35,50,.16);
    --read: 'Atkinson Hyperlegible', system-ui, sans-serif;
    --head: 'Lexend', system-ui, sans-serif;
    --mono: 'IBM Plex Mono', ui-monospace, monospace;
    --size: 1.24rem; --lead: 1.85;
  }
  html[data-size="1"] { --size: 1.4rem; }
  html[data-size="2"] { --size: 1.58rem; }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--paper); color: var(--ink);
    font-family: var(--read); font-size: var(--size); line-height: var(--lead);
    letter-spacing: .01em; -webkit-font-smoothing: antialiased;
  }
  .bar {
    position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 1rem;
    padding: .9rem clamp(1rem, 3vw, 2.5rem); background: color-mix(in oklab, var(--paper) 92%%, white);
    border-bottom: 1px solid var(--line); flex-wrap: wrap;
  }
  .bar a.mark { font-family: var(--head); font-weight: 500; text-decoration: none; font-size: 1.02rem; }
  .bar .spacer { margin-left: auto; }
  .bar a.btn, .bar button {
    font-family: var(--read); font-size: .95rem; text-decoration: none; color: var(--ink);
    border: 1px solid var(--line); background: transparent; border-radius: 100px;
    padding: .45rem .95rem; cursor: pointer;
  }
  .bar button[aria-pressed="true"] { border-color: var(--green); color: var(--green); font-weight: 700; }
  main { max-width: 40rem; margin: 0 auto; padding: clamp(2rem, 6vh, 4rem) clamp(1rem, 4vw, 2rem) 5rem; }
  h1, h2, h3 { font-family: var(--head); font-weight: 600; line-height: 1.25; text-wrap: balance; }
  h1 { font-size: clamp(1.9rem, 5vw, 2.7rem); margin: 0 0 .6rem; }
  h2 { font-size: clamp(1.35rem, 3.4vw, 1.7rem); margin: 3rem 0 .8rem; }
  h3 { font-size: 1.1rem; margin: 2rem 0 .5rem; }
  p { margin: 0 0 1.15rem; }
  .lede { color: var(--ink-soft); font-size: 1.06em; }
  strong { font-weight: 700; }
  a { color: var(--green); text-underline-offset: .2em; }
  .box { border: 2px solid var(--green); border-radius: 14px; padding: 1.2rem 1.3rem; margin: 1.8rem 0; }
  .box h2 { margin: 0 0 .6rem; font-size: 1.2rem; }
  .box ul { margin: 0; padding-left: 1.3rem; }
  .box li { margin-bottom: .6rem; }
  dl.rows { margin: 1.2rem 0; }
  dl.rows .row { border-top: 2px solid var(--line); padding: .9rem 0 .2rem; }
  dl.rows .row:nth-child(1), dl.rows .row:nth-child(2) { border-top-color: var(--green); }
  dl.rows .row:nth-child(3), dl.rows .row:nth-child(4) { border-top-color: var(--orange); }
  dl.rows dt { font-weight: 700; margin-bottom: .35rem; }
  dl.rows dd { margin: 0 0 .6rem; color: var(--ink-soft); }
  ol.steps { padding-left: 1.4rem; }
  ol.steps li { margin-bottom: 1rem; }
  ol.steps strong { display: block; }
  ol.steps span { color: var(--ink-soft); }
  ul.tight li { margin-bottom: .8rem; }
  code { font-family: var(--mono); font-size: .92em; background: rgba(26,35,50,.06);
          padding: .1rem .35rem; border-radius: 5px; }
  pre { font-family: var(--mono); font-size: .82rem; line-height: 1.7; background: #fbf9f4;
         border: 1px solid var(--line); border-left: 4px solid var(--green); border-radius: 12px;
         padding: 1rem 1.1rem; overflow-x: auto; }
  .note { border-left: 4px solid var(--orange); padding-left: 1rem; color: var(--ink-soft); }
  .srcs { list-style: none; padding: 0; }
  .srcs li { border-top: 1px solid var(--line); padding: .8rem 0; }
  .srcs span { display: block; color: var(--ink-soft); }
  footer { border-top: 1px solid var(--line); margin-top: 3rem; padding-top: 1.2rem;
            color: var(--ink-soft); }
  @media (max-width: 34rem) { :root { --size: 1.2rem; } }
</style>
</head>
<body>
<div class="bar">
  <a class="mark" href="index.html">Jev <span style="font-family:var(--mono);font-size:.8em">/</span> use cases</a>
  <span class="spacer"></span>
  <button type="button" data-size-btn="0" aria-pressed="false">Text size A</button>
  <button type="button" data-size-btn="1" aria-pressed="false">A+</button>
  <button type="button" data-size-btn="2" aria-pressed="false">A++</button>
  <a class="btn" href="index.html">Back to the cases</a>
</div>

<main>
  <h1>About Jev</h1>
  <p class="lede">Jev is a decision model. You send it a piece of text, and a set of questions whose
  answers you already know how to list. It sends back one of your answers, with a number that says how
  sure it is. It does not write sentences, and it cannot invent an answer you did not offer.</p>

  <div class="box">
    <h2>The one-minute version</h2>
    <ul>
      <li>Jev returns a <strong>typed decision</strong>, not text.</li>
      <li>Pick one from a list is a <strong>choice</strong>. Rate on a scale is a <strong>score</strong>.
        Yes or no is a <strong>noul</strong>.</li>
      <li>Every answer arrives with a <strong>probability</strong> your code can test.</li>
      <li>It is fast and cheap: the maker quotes 70 to 500 milliseconds, and 0.042 US dollars for a
        million words of input, with the answer itself free.</li>
      <li>Use it when the possible answers are known in advance. Use a writing model for anything that
        has to be written.</li>
    </ul>
  </div>

  <h2>Why it exists</h2>
  <p>A normal language model writes out an answer, and then a program has to read that answer, hope it
  is in the right shape, and cope when it is not. For a great many jobs, the shape is known already:
  a department, a priority, a yes or no. Jev is built for exactly those jobs. You declare the answers
  in advance, so a program can use the result straight away, without parsing anything.</p>
  <p class="note">The confidence is the point. A number that means what it says lets you decide what to
  do: act on the sure ones, pass the unsure ones to a person.</p>

  <h2>The three kinds of question</h2>
  <p>You can ask several at once. They are judged in parallel against the same text, so a tenth
  question costs a few extra words and almost no extra time. The answers are not passed to each other.</p>
  <dl class="rows">
%s
  </dl>

  <h2>What you need before the first call</h2>
  <ol class="steps">
%s
  </ol>

  <h2>A call, step by step</h2>
  <p>Text goes in, a typed answer comes out, and your own code decides what happens next. Jev never
  sends the email, moves the money, or runs the command.</p>
  <pre translate="no">%s</pre>

  <h2>Five rules that keep it working</h2>
  <ul class="tight">
%s
  </ul>

  <h2>Where Jev is the wrong tool</h2>
  <ul class="tight">
%s
  </ul>

  <h2>What is claimed, and what is not yet proved</h2>
  <p>The maker claims Jev is 40 to 200 times faster and 40 to 400 times cheaper than the largest
  language models on decision-style work, and that it cannot produce a type error or an invented
  field. Those are the maker's own figures. Independent benchmarking is still thin, so treat them as
  a strong starting point rather than a settled fact.</p>
  <p>One guarantee does hold by construction: <strong>Jev cannot return an option you did not
  declare</strong>. It can still return the wrong option from your list. That is what the probability
  is for, and why the threshold belongs in your code, written after you have looked at real traffic.</p>

  <h2>Reading this page</h2>
  <p>This page is set in Atkinson Hyperlegible, a typeface designed for readers who find letters easy
  to confuse, at a larger size with wide line spacing and short lines. Use the A, A+ and A++ buttons at
  the top if you would like it bigger still.</p>

  <h2>Where to read more</h2>
  <ul class="srcs">
%s
  </ul>

  <footer>
    <p>Jev is made by TypeSafe AI. This site is an independent reference to its use cases and is not
    affiliated with TypeSafe.</p>
  </footer>
</main>

<script>
  var html = document.documentElement, btns = document.querySelectorAll('[data-size-btn]');
  function setSize(level) {
    if (level === '0') { html.removeAttribute('data-size'); } else { html.setAttribute('data-size', level); }
    btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.sizeBtn === level)); });
    try { localStorage.setItem('jev-text-size', level); } catch (e) {}
  }
  btns.forEach(function (b) { b.addEventListener('click', function () { setSize(b.dataset.sizeBtn); }); });
  try { var saved = localStorage.getItem('jev-text-size'); if (saved) { setSize(saved); } } catch (e) {}
</script>
</body>
</html>
""" % (q_rows, prep, html.escape(CODE), rules, wrong, srcs)


def main():
    out = ROOT / "about.html"
    out.write_text(page().replace("{site}", SITE))
    print("wrote about.html, %d bytes" % out.stat().st_size)


if __name__ == "__main__":
    main()
