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
    var bounds = null, lastDocH = 0;

    function measure() {
      bounds = cases.map(function (c) {
        var r = c.getBoundingClientRect();
        var top = r.top + window.scrollY;
        return { top: top, bottom: top + r.height };
      });
      lastDocH = document.documentElement.scrollHeight;
    }

    function whichCase() {
      /* One layout read per frame, not nineteen: the case boundaries only move
         when the page re-lays out, and the document height catches that. Lazy
         plate images changing height is the common case. */
      var docH = document.documentElement.scrollHeight;
      if (!bounds || docH !== lastDocH) measure();
      /* The playhead sits a third of the way down, not at the middle: a reader
         who can see a card's heading has arrived at that card, and a counter that
         waits for the midpoint reads as lagging behind the page. */
      var playhead = window.scrollY + window.innerHeight * 0.35, best = 0, bestD = Infinity;
      for (var i = 0; i < bounds.length; i++) {
        var b = bounds[i];
        var d = b.top > playhead ? b.top - playhead : (b.bottom < playhead ? playhead - b.bottom : 0);
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

    function setOpen(open, keepFocus) {
      panel.setAttribute("data-open", open ? "true" : "false");
      openers.forEach(function (b) { b.setAttribute("aria-expanded", open ? "true" : "false"); });
      if (open) {
        var first = panel.querySelector("a");
        if (first) first.focus({ preventScroll: true });
      } else if (!keepFocus) {
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
      var a = e.target.closest("a");
      if (!a) return;
      /* A jump should leave the caret at the case, not back on the button at the
         top of the page: the reader's next keystroke belongs to what they chose. */
      setOpen(false, true);
      var id = (a.getAttribute("href") || "").slice(1);
      var target = id ? document.getElementById(id) : null;
      if (target) {
        if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
      }
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

  /* ------------------------------------------------------------ the artwork viewer
     Each plate is a real button. Activating it opens the drawing at full size in a
     <dialog>, which brings the focus trap, Escape and the modal semantics with it,
     so none of that has to be hand-rolled. */
  function viewer() {
    var openers = document.querySelectorAll(".plate__open");
    var probe = document.createElement("dialog");
    if (!openers.length || typeof probe.showModal !== "function") return;
    var dlg = document.createElement("dialog");
    dlg.className = "viewer";
    dlg.setAttribute("aria-label", "Artwork at full size");
    dlg.innerHTML =
      '<div class="viewer__bar">' +
        '<p class="viewer__title"></p>' +
        '<p class="viewer__hint">Turn your phone to read it</p>' +
        '<button class="viewer__turn" type="button" aria-pressed="false">Rotate</button>' +
        '<button class="viewer__close" type="button">Close</button>' +
      '</div>' +
      '<img alt="">';
    document.body.appendChild(dlg);
    var pic = dlg.querySelector("img");
    var name = dlg.querySelector(".viewer__title");
    var last = null;

    function shut() { dlg.close(); }

    openers.forEach(function (b) {
      b.addEventListener("click", function () {
        var inner = b.querySelector("img");
        var src = b.getAttribute("data-full") || (inner ? inner.currentSrc || inner.src : "");
        if (!src) return;
        pic.src = src;
        pic.alt = inner ? inner.alt : "";
        var card = b.closest("article.case");
        var no = card ? card.getAttribute("data-case") : "";
        var title = card ? card.getAttribute("data-title") : "";
        name.textContent = no ? "Case " + no + (title ? " \u2014 " + title : "") : "";
        last = b;
        document.documentElement.setAttribute("data-viewer", "open");
        dlg.showModal();
      });
    });
    dlg.querySelector(".viewer__close").addEventListener("click", shut);
    /* A 16:9 drawing on a portrait phone is a thin band across the middle, with the
       lettering too small to read. Turning it a quarter turn makes it fill the
       screen; the button only appears where that helps. */
    var turn = dlg.querySelector(".viewer__turn");
    turn.addEventListener("click", function () {
      var on = dlg.getAttribute("data-turned") === "true";
      dlg.setAttribute("data-turned", on ? "false" : "true");
      turn.setAttribute("aria-pressed", on ? "false" : "true");
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) shut(); });
    dlg.addEventListener("close", function () {
      document.documentElement.removeAttribute("data-viewer");
      pic.removeAttribute("src");
      if (last) last.focus();
    });
  }

  function boot() {
    ledger();
    indexPanel();
    copyButtons();
    viewer();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
