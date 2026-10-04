/* Jev use cases: the page's own behaviour.
   The engine owns the scroll devices. This file owns three things:
   the ledger rail (the signature move), the index panel, and copy buttons. */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------ the ledger
     Scroll position is the playhead. Passing a case stamps its tick for good,
     the tick under the playhead is the accent one, and every tick jumps. */
  function ledger() {
    var track = document.querySelector(".ledger__track");
    var now = document.querySelector(".ledger__now");
    var cases = Array.prototype.slice.call(document.querySelectorAll(".case"));
    if (!track || !cases.length) return;

    var visited = Object.create(null);
    var ticks = [];

    cases.forEach(function (el, i) {
      var n = el.getAttribute("data-case");
      var title = el.getAttribute("data-title") || "";
      var b = document.createElement("button");
      b.type = "button";
      b.className = "rail__tick";
      b.setAttribute("aria-label", "Case " + n + ", " + title);
      b.innerHTML = "<i></i><span>Case " + n + "</span>";
      b.addEventListener("click", function () {
        el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
        el.setAttribute("tabindex", "-1");
        el.focus({ preventScroll: true });
      });
      track.appendChild(b);
      ticks.push(b);
      el.addEventListener("focus", function () { stamp(i); });
    });

    function stamp(i) {
      ticks.forEach(function (t, j) {
        t.setAttribute("data-current", j === i ? "true" : "false");
        if (j === i) visited[j] = true;
        t.setAttribute("data-visited", visited[j] ? "true" : "false");
      });
      var el = cases[i];
      if (now) {
        /* Short on purpose: a long string truncates at the right edge on a
           laptop, and the title is already on every tick's tooltip. */
        now.innerHTML = "case <b>" + el.getAttribute("data-case") + "</b> of " + cases.length;
        now.setAttribute("title", el.getAttribute("data-title") || "");
      }
    }

    /* Which case is the reader on? Geometry beats an IntersectionObserver here:
       the collection has 19 tall articles with acts between them, and the
       midpoint test answers "which case is under the reader" in every state,
       including the gaps where nothing intersects at all. */
    var current = -1;

    function whichCase() {
      var mid = window.innerHeight / 2, best = 0, bestD = Infinity;
      for (var i = 0; i < cases.length; i++) {
        var r = cases[i].getBoundingClientRect();
        var d = r.top > mid ? r.top - mid : (r.bottom < mid ? mid - r.bottom : 0);
        if (d < bestD) { bestD = d; best = i; }
      }
      return best;
    }

    function sync() {
      var i = whichCase();
      if (i !== current) { current = i; stamp(i); }
    }

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () { ticking = false; sync(); });
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    sync();
  }

  /* ------------------------------------------------------- the index panel */
  function indexPanel() {
    var panel = document.querySelector(".index-panel");
    var openers = Array.prototype.slice.call(document.querySelectorAll("[data-index-toggle]"));
    if (!panel) return;

    function setOpen(open) {
      panel.setAttribute("data-open", open ? "true" : "false");
      openers.forEach(function (b) { b.setAttribute("aria-expanded", open ? "true" : "false"); });
      if (open) {
        var first = panel.querySelector("a");
        if (first) first.focus({ preventScroll: true });
      } else {
        var btn = document.querySelector("[data-index-toggle]");
        if (btn) btn.focus({ preventScroll: true });
      }
    }

    openers.forEach(function (b) {
      b.addEventListener("click", function () {
        setOpen(panel.getAttribute("data-open") !== "true");
      });
    });
    panel.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.getAttribute("data-open") === "true") setOpen(false);
    });
    setOpen(false);
  }

  /* ---------------------------------------------------------- copy buttons */
  function copyButtons() {
    var buttons = Array.prototype.slice.call(document.querySelectorAll(".copy"));
    if (!buttons.length) return;

    function flash(b) {
      var was = b.textContent;
      b.setAttribute("data-done", "true");
      b.textContent = "Copied";
      window.setTimeout(function () {
        b.removeAttribute("data-done");
        b.textContent = was;
      }, 1600);
    }

    function fallback(text, b) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); flash(b); } catch (err) { /* nothing to do */ }
      document.body.removeChild(ta);
    }

    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        var id = b.getAttribute("data-copy");
        var src = id ? document.getElementById(id) : null;
        var text = src ? src.innerText : "";
        if (!text) return;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () { flash(b); },
            function () { fallback(text, b); });
        } else {
          fallback(text, b);
        }
      });
    });
  }

  function boot() {
    ledger();
    indexPanel();
    copyButtons();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
