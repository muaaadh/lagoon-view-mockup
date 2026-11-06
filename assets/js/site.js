/* Lagoon View Maldives, mockup.
   One rAF loop drives everything scroll-related: geometry is cached in measure() and only
   scrollY is read per frame. Reveals are a sweep (top < vh * .92), not an observer threshold,
   so a fast flick can never strand a section invisible. */
(function () {
  "use strict";
  var d = document, root = d.documentElement;
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var wide = matchMedia("(min-width: 900px)");
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var pageTop = function (el) { return el.getBoundingClientRect().top + window.scrollY; };
  var smooth = function (t) { return t * t * (3 - 2 * t); };

  var vh = innerHeight, vw = innerWidth, y = window.scrollY, last = -1, first = true, dirty = true;
  var scenes = [];
  var scene = function (s) { scenes.push(s); return s; };

  /* smooth wheel on mouse and trackpad; touch keeps native momentum */
  var lenis = null;
  if (!reduce && window.Lenis && matchMedia("(pointer: fine)").matches) {
    lenis = new window.Lenis({ lerp: 0.11, wheelMultiplier: 0.95 });
  }

  /* lazy images fade in rather than pop */
  $$(".fig > img").forEach(function (im) {
    if (im.complete && im.naturalWidth) { im.classList.add("ld"); return; }
    im.addEventListener("load", function () { im.classList.add("ld"); }, { once: true });
    im.addEventListener("error", function () { im.classList.add("ld"); }, { once: true });
  });

  /* header */
  (function () {
    var hd = $(".hd"); if (!hd) return;
    var overUntil = 0, prev = 0, film = d.body.dataset.top;
    scene({
      measure: function () {
        if (film === "hero") overUntil = vh * 0.06;
        else if (film === "photo") overUntil = ($(".ph") ? $(".ph").offsetHeight : vh) - 90;
        else overUntil = -1;
      },
      update: function () {
        hd.classList.toggle("over", y < overUntil);
        if (d.body.classList.contains("menu-open")) return;
        if (y > prev + 4 && y > 140) hd.classList.add("up");
        else if (y < prev - 4 || y <= 140) hd.classList.remove("up");
        prev = y;
      }
    });
    var btn = $(".hd__menu"), menu = $("#menu");
    if (btn && menu) {
      var toggle = function (open) {
        menu.classList.toggle("open", open);
        d.body.classList.toggle("menu-open", open);
        btn.setAttribute("aria-expanded", String(open));
        btn.textContent = open ? "Close" : "Menu";
        hd.classList.remove("up");
        if (lenis) { open ? lenis.stop() : lenis.start(); }
        root.style.overflow = open ? "hidden" : "";
      };
      btn.addEventListener("click", function () { toggle(!menu.classList.contains("open")); });
      d.addEventListener("keydown", function (e) { if (e.key === "Escape" && menu.classList.contains("open")) { toggle(false); btn.focus(); } });
    }
  })();

  /* word masks on headings */
  $$("[data-split]").forEach(function (el) {
    if (reduce) return;
    var n = 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var frag = d.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (t) {
            if (!t) return;
            if (/^\s+$/.test(t)) { frag.appendChild(d.createTextNode(" ")); return; } /* real spaces keep the wrap identical */
            var w = d.createElement("span"); w.className = "w";
            var i = d.createElement("span"); i.textContent = t; i.style.setProperty("--n", n++);
            w.appendChild(i); frag.appendChild(w);
          });
          node.replaceChild(frag, c);
        } else if (c.nodeType === 1) walk(c);
      });
    };
    el.setAttribute("aria-label", el.textContent.trim());
    walk(el);
  });

  /* reveal sweep */
  (function () {
    var items = $$(".rv, [data-split]").map(function (el) { return { el: el, top: 0 }; });
    var groups = $$("[data-stagger]");
    groups.forEach(function (g) { $$(".rv", g).forEach(function (el, i) { if (!el.style.getPropertyValue("--i")) el.style.setProperty("--i", i); }); });
    scene({
      measure: function () { items.forEach(function (o) { o.top = pageTop(o.el); }); },
      update: function () {
        var edge = y + vh * (first ? 1 : 0.92);
        items = items.filter(function (o) {
          if (o.top < edge) { o.el.classList.add("in"); return false; }
          return true;
        });
      }
    });
  })();

  /* photo parallax, inside its frame */
  if (!reduce) (function () {
    var items = $$(".fig[data-p]").map(function (f) { return { f: f, im: $("img", f), top: 0, h: 0 }; });
    scene({
      measure: function () { items.forEach(function (o) { o.top = pageTop(o.f); o.h = o.f.offsetHeight; }); },
      update: function () {
        items.forEach(function (o) {
          if (y + vh < o.top || y > o.top + o.h) return;
          var t = (y + vh - o.top) / (vh + o.h);
          o.im.style.transform = "translate3d(0," + ((t - 0.5) * 11).toFixed(2) + "%,0)";
        });
      }
    });
  })();

  /* free-floating scrub, used on the dive collage */
  if (!reduce) (function () {
    var items = $$("[data-shift]").map(function (el) { return { el: el, top: 0, h: 0, a: parseFloat(el.dataset.shift) }; });
    scene({
      measure: function () { items.forEach(function (o) { o.el.style.transform = ""; o.top = pageTop(o.el); o.h = o.el.offsetHeight; }); },
      update: function () {
        if (!wide.matches) return;
        items.forEach(function (o) {
          if (y + vh < o.top - 200 || y > o.top + o.h + 200) return;
          var t = (y + vh - o.top) / (vh + o.h);
          o.el.style.transform = "translate3d(0," + ((t - 0.5) * o.a).toFixed(1) + "px,0)";
        });
      }
    });
  })();

  /* page heroes settle as you leave them */
  if (!reduce) $$(".ph").forEach(function (ph) {
    var m = $(".ph__m", ph), t = $(".ph__t", ph), h = 0;
    scene({
      measure: function () { h = ph.offsetHeight; },
      update: function () {
        if (y > h) return;
        var p = y / h;
        m.style.transform = "translate3d(0," + (p * 12).toFixed(2) + "%,0) scale(" + (1.04 - p * 0.04).toFixed(4) + ")";
        if (t) t.style.opacity = (1 - p * 1.6).toFixed(3);
      }
    });
  });

  /* home hero: the film draws in as you leave */
  (function () {
    var hero = $(".hero"); if (!hero || reduce) return;
    var frame = $(".hero__frame"), film = $("video, img", frame), copy = $(".hero__copy"), bar = $(".bar"), tog = $(".filmbtn", hero), h = 0;
    scene({
      measure: function () { h = hero.offsetHeight - vh; },
      update: function () {
        var p = clamp(y / h, 0, 1), s = smooth(p);
        frame.style.transform = "scale(" + (1 - s * 0.13).toFixed(4) + ")";
        film.style.transform = "scale(" + ((wide.matches ? 1.17 : 1) + s * 0.09).toFixed(4) + ")";
        var f = clamp(1 - p * 2.4, 0, 1);
        copy.style.opacity = f.toFixed(3);
        copy.style.transform = "translate3d(0," + (-p * 70).toFixed(1) + "px,0)";
        if (bar) { bar.style.opacity = f.toFixed(3); bar.style.visibility = f < 0.02 ? "hidden" : ""; }
        if (tog) tog.style.opacity = f.toFixed(3);
      }
    });
  })();

  /* statement: words fill as they reach you */
  (function () {
    var el = $("[data-fill]"); if (!el || reduce) return;
    var parts = el.textContent.trim().split(/\s+/);
    el.setAttribute("aria-label", el.textContent.trim());
    el.textContent = "";
    var words = parts.map(function (w, i) {
      var s = d.createElement("span"); s.className = "fw"; s.textContent = w; s.setAttribute("aria-hidden", "true");
      el.appendChild(s); if (i < parts.length - 1) el.appendChild(d.createTextNode(" "));
      return s;
    });
    var top = 0, h = 0, lit = 0;
    scene({
      measure: function () { top = pageTop(el); h = el.offsetHeight; },
      update: function () {
        var p = clamp((y + vh * 0.82 - top) / (h + vh * 0.32), 0, 1);
        var n = Math.round(p * words.length);
        if (n === lit) return;
        words.forEach(function (w, i) { w.classList.toggle("on", i < n); });
        lit = n;
      }
    });
  })();

  /* rooms: vertical scroll drives the rail */
  (function () {
    var sec = $(".strip"); if (!sec || reduce) return;
    var rail = $(".strip__rail"), top = 0, travel = 0;
    scene({
      layout: function () {
        if (!wide.matches) { sec.style.height = ""; rail.style.transform = ""; travel = 0; return; }
        rail.style.transform = "";
        travel = Math.max(0, rail.getBoundingClientRect().width - vw);
        sec.style.height = Math.round(travel + vh * 1.05) + "px";
      },
      measure: function () { top = pageTop(sec); },
      update: function () {
        if (!travel) return;
        var p = clamp((y - top) / travel, 0, 1);
        rail.style.transform = "translate3d(" + (-p * travel).toFixed(1) + "px,0,0)";
      }
    });
  })();

  /* the waterline: the surface rises through the frame and you go under */
  (function () {
    var sec = $(".wl"); if (!sec || reduce) return;
    var over = $(".wl__over"), overImg = $("img", over), under = $(".wl__under video, .wl__under img");
    var path = $(".wl__line path"), a = $(".wl__t--a"), b = $(".wl__t--b"), tog = $(".filmbtn", sec), top = 0, h = 0;
    var N = 56;
    scene({
      always: true,
      measure: function () { top = pageTop(sec); h = sec.offsetHeight; },
      update: function (t) {
        if (y + vh < top - 40 || y > top + h + 40) return;
        var p = clamp((y - top) / (h - vh), 0, 1);
        var q = smooth(clamp((p - 0.16) / 0.56, 0, 1));
        var base = (1 - q) * vh * 1.08 - q * vh * 0.1;
        var swell = 7 + 13 * Math.sin(Math.PI * q);
        var s = t / 1000, pts = "", dd = "";
        for (var i = 0; i <= N; i++) {
          var u = i / N, x = u * vw;
          var yy = base + swell * Math.sin(u * 7 + s * 0.9) + swell * 0.45 * Math.sin(u * 17 - s * 1.3);
          pts += x.toFixed(1) + "px " + yy.toFixed(1) + "px,";
          dd += (i ? "L" : "M") + x.toFixed(1) + " " + yy.toFixed(1);
        }
        /* walk the wave right-to-left so the polygon closes around the top */
        var rev = pts.slice(0, -1).split(",").reverse().join(",");
        over.style.clipPath = "polygon(0 0," + vw + "px 0," + rev + ")";
        path.setAttribute("d", dd);
        path.style.opacity = q > 0.995 ? 0 : 1;
        if (tog) { tog.style.opacity = q > 0.6 ? 1 : 0; tog.style.pointerEvents = q > 0.6 ? "" : "none"; }
        overImg.style.transform = "translate3d(0," + (-q * 10).toFixed(2) + "%,0)";
        if (under) under.style.transform = "scale(" + (1.12 - q * 0.12).toFixed(4) + ")";
        a.style.opacity = (clamp((p - 0.015) / 0.05, 0, 1) * (1 - clamp((p - 0.17) / 0.12, 0, 1))).toFixed(3);
        b.style.opacity = clamp((p - 0.6) / 0.14, 0, 1).toFixed(3);
        b.style.transform = "translate3d(0," + ((1 - clamp((p - 0.6) / 0.14, 0, 1)) * 26).toFixed(1) + "px,0)";
      }
    });
  })();

  /* days out: the row nearest the middle of the screen owns the picture */
  (function () {
    var sec = $(".days"); if (!sec) return;
    var rows = $$(".day", sec), pics = $$(".days__pic .fig", sec), tops = [], cur = -1;
    scene({
      measure: function () { tops = rows.map(function (r) { return pageTop(r) + r.offsetHeight / 2; }); },
      update: function () {
        if (!wide.matches) return;
        var mid = y + vh * 0.5, best = 0, dist = 1e9;
        tops.forEach(function (t, i) { var dd = Math.abs(t - mid); if (dd < dist) { dist = dd; best = i; } });
        if (best === cur) return;
        cur = best;
        rows.forEach(function (r, i) { r.classList.toggle("on", i === best); });
        pics.forEach(function (f, i) { f.classList.toggle("on", i === best); });
      }
    });
  })();

  /* ambient film: loads as it nears, plays only in view, always has a stop control */
  (function () {
    var films = $$("video[data-film]").map(function (v) { return { v: v, box: v.closest("section") || v, top: 0, h: 0, set: false, stopped: false }; });
    if (reduce) { films.forEach(function (f) { f.v.removeAttribute("autoplay"); var b = $(".filmbtn", f.box); if (b) b.hidden = true; }); return; }
    films.forEach(function (f) {
      var b = $(".filmbtn", f.box); if (!b) return;
      b.addEventListener("click", function () {
        f.stopped = !f.stopped;
        b.textContent = f.stopped ? "Play film" : "Pause film";
        if (f.stopped) f.v.pause(); else f.v.play().catch(function () {});
      });
    });
    scene({
      measure: function () { films.forEach(function (f) { f.top = pageTop(f.box); f.h = f.box.offsetHeight; }); },
      update: function () {
        films.forEach(function (f) {
          var near = y + vh * 2 > f.top && y < f.top + f.h + vh;
          if (near && !f.set) {
            f.set = true;
            f.v.src = f.v.getAttribute(vw < 900 ? "data-720" : "data-1080"); /* hyphen-digit names are not camel-cased */
            f.v.muted = true;
            f.v.load();
          }
          var on = y + vh > f.top && y < f.top + f.h;
          if (!f.set || f.stopped) return;
          if (on && f.v.paused) f.v.play().catch(function () {});
          else if (!on && !f.v.paused) f.v.pause();
        });
      }
    });
  })();

  /* back to the surface */
  $$("[data-surface]").forEach(function (b) {
    b.addEventListener("click", function () {
      if (lenis) lenis.scrollTo(0, { duration: 2.6, easing: function (t) { return 1 - Math.pow(1 - t, 3); } });
      else scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
    });
  });

  /* dates: always local parts, the Maldives is UTC+5 and toISOString() would give yesterday */
  var iso = function (x) { return x.getFullYear() + "-" + String(x.getMonth() + 1).padStart(2, "0") + "-" + String(x.getDate()).padStart(2, "0"); };
  var parse = function (s) { if (!s) return null; var p = s.split("-"); var x = new Date(+p[0], +p[1] - 1, +p[2]); return isNaN(x) ? null : x; };
  var MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var short = function (x) { return x.getDate() + " " + MON[x.getMonth()].slice(0, 3) + " " + x.getFullYear(); };
  var nightsBetween = function (a, b) { return Math.round((b - a) / 864e5); };

  function Calendar(host, state, onChange) {
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var view = new Date((state.a || today).getFullYear(), (state.a || today).getMonth(), 1);
    var min = new Date(today.getFullYear(), today.getMonth(), 1);
    function month(m) {
      var wrap = d.createElement("div"); wrap.className = "cal__m";
      var h = d.createElement("h3"); h.textContent = MON[m.getMonth()] + " " + m.getFullYear(); wrap.appendChild(h);
      var g = d.createElement("div"); g.className = "cal__g";
      ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"].forEach(function (n) { var s = d.createElement("span"); s.textContent = n; g.appendChild(s); });
      var lead = (new Date(m.getFullYear(), m.getMonth(), 1).getDay() + 6) % 7;
      for (var i = 0; i < lead; i++) g.appendChild(d.createElement("i"));
      var n = new Date(m.getFullYear(), m.getMonth() + 1, 0).getDate();
      for (var day = 1; day <= n; day++) (function (day) {
        var x = new Date(m.getFullYear(), m.getMonth(), day);
        var b = d.createElement("button"); b.type = "button"; b.className = "cal__d"; b.textContent = day;
        b.setAttribute("aria-label", short(x));
        if (x < today) b.disabled = true;
        if (state.a && +x === +state.a) b.classList.add("a");
        if (state.b && +x === +state.b) b.classList.add("b");
        if (state.a && state.b && x > state.a && x < state.b) b.classList.add("mid");
        b.addEventListener("click", function () {
          if (!state.a || state.b || x <= state.a) { state.a = x; state.b = null; }
          else state.b = x;
          render(); onChange();
        });
        g.appendChild(b);
      })(day);
      wrap.appendChild(g);
      return wrap;
    }
    function render() {
      host.textContent = "";
      var l = d.createElement("button"); l.type = "button"; l.className = "cal__nav cal__nav--l"; l.textContent = "‹"; l.setAttribute("aria-label", "Previous month");
      l.disabled = view <= min;
      l.addEventListener("click", function () { view = new Date(view.getFullYear(), view.getMonth() - 1, 1); render(); });
      var r = d.createElement("button"); r.type = "button"; r.className = "cal__nav cal__nav--r"; r.textContent = "›"; r.setAttribute("aria-label", "Next month");
      r.addEventListener("click", function () { view = new Date(view.getFullYear(), view.getMonth() + 1, 1); render(); });
      host.appendChild(l); host.appendChild(r);
      host.appendChild(month(view));
      host.appendChild(month(new Date(view.getFullYear(), view.getMonth() + 1, 1)));
    }
    render();
    return { render: render };
  }

  function guestLabel(s) { return s.adults + (s.adults === 1 ? " adult" : " adults") + (s.kids ? ", " + s.kids + (s.kids === 1 ? " child" : " children") : ""); }
  function steppers(host, s, onChange) {
    $$("[data-step]", host).forEach(function (row) {
      var k = row.dataset.step, min = k === "adults" ? 1 : 0, out = $("output", row);
      $$("button", row).forEach(function (b) {
        b.addEventListener("click", function () {
          s[k] = clamp(s[k] + (+b.dataset.d), min, 10);
          out.textContent = s[k]; onChange();
        });
      });
    });
  }

  /* hero booking bar */
  (function () {
    var bar = $(".bar"); if (!bar) return;
    var s = { a: null, b: null, adults: 2, kids: 0 };
    var calPop = $(".pop--cal", bar), gPop = $(".pop--guests", bar);
    var fIn = $("[data-f=in] b", bar), fOut = $("[data-f=out] b", bar), fG = $("[data-f=guests] b", bar);
    var sync = function () {
      fIn.textContent = s.a ? short(s.a) : "Add date";
      fOut.textContent = s.b ? short(s.b) : "Add date";
      fG.textContent = guestLabel(s);
      var q = new URLSearchParams();
      if (s.a) q.set("in", iso(s.a)); if (s.b) q.set("out", iso(s.b));
      q.set("a", s.adults); q.set("c", s.kids);
      $("a.btn", bar).href = $("a.btn", bar).getAttribute("data-href") + "?" + q.toString();
      if (s.a && s.b) close();
    };
    var btns = $$(".bar__f", bar);
    function close() { [calPop, gPop].forEach(function (p) { p.classList.remove("open"); }); btns.forEach(function (b) { b.setAttribute("aria-expanded", "false"); }); }
    Calendar($(".cal", calPop), s, sync);
    steppers(gPop, s, sync);
    btns.forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var pop = b.dataset.f === "guests" ? gPop : calPop, open = pop.classList.contains("open") && b.getAttribute("aria-expanded") === "true";
        close();
        if (!open) { pop.classList.add("open"); b.setAttribute("aria-expanded", "true"); }
      });
    });
    [calPop, gPop].forEach(function (p) { p.addEventListener("click", function (e) { e.stopPropagation(); }); });
    d.addEventListener("click", close);
    d.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    sync();
  })();

  /* tabs: dining menus */
  $$("[data-tabs]").forEach(function (g) {
    var tabs = $$(".tab", g), wrap = g.parentNode;
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () {
        tabs.forEach(function (x, k) { x.setAttribute("aria-selected", String(k === i)); });
        $$(".menu-p", wrap).forEach(function (p, k) { p.classList.toggle("on", k === i); });
        measureAll();
      });
    });
  });

  /* packages: one season at a time */
  (function () {
    var g = $("[data-seasons]"); if (!g) return;
    var tabs = $$(".tab", g);
    var show = function (s) {
      tabs.forEach(function (t) { t.setAttribute("aria-pressed", String(t.dataset.s === s)); });
      $$("[data-price]").forEach(function (el) {
        var v = el.getAttribute("data-" + s);
        el.firstChild.textContent = v ? "$" + v : "Ask us";
        var note = $("small", el); if (note) note.hidden = !v;
      });
    };
    tabs.forEach(function (t) { t.addEventListener("click", function () { show(t.dataset.s); }); });
    show(tabs[0].dataset.s);
  })();

  /* gallery lightbox */
  (function () {
    var lb = $(".lb"); if (!lb) return;
    var btns = $$(".grid-g button"), img = $("img", lb), cap = $(".lb__c", lb), i = 0;
    var show = function (n) {
      i = (n + btns.length) % btns.length;
      var src = btns[i].dataset.full; img.src = src; img.alt = btns[i].dataset.alt;
      cap.textContent = (i + 1) + " of " + btns.length;
    };
    btns.forEach(function (b, n) { b.addEventListener("click", function () { show(n); lb.showModal(); if (lenis) lenis.stop(); }); });
    $(".lb__x", lb).addEventListener("click", function () { lb.close(); });
    $(".lb__p", lb).addEventListener("click", function () { show(i - 1); });
    $(".lb__n", lb).addEventListener("click", function () { show(i + 1); });
    lb.addEventListener("close", function () { if (lenis) lenis.start(); btns[i].focus(); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(i - 1);
      if (e.key === "ArrowRight") show(i + 1);
    });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
  })();

  /* mock forms */
  $$("form[data-mock]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = d.createElement("p"); msg.className = "done t3"; msg.textContent = f.dataset.mock; msg.tabIndex = -1;
      f.replaceWith(msg); msg.focus();
      measureAll();
    });
  });

  /* booking page */
  (function () {
    var bk = $(".bk"); if (!bk) return;
    var q = new URLSearchParams(location.search);
    var s = { a: parse(q.get("in")), b: parse(q.get("out")), adults: clamp(+(q.get("a") || 2), 1, 10), kids: clamp(+(q.get("c") || 0), 0, 10), room: q.get("room") };
    var opts = $$(".opt", bk), out = {};
    ["dates", "nights", "guests", "room", "rate", "total"].forEach(function (k) { out[k] = $("[data-o=" + k + "]", bk); });
    var send = $("[data-send]", bk);
    var sync = function () {
      var n = s.a && s.b ? nightsBetween(s.a, s.b) : 0;
      var pick = opts.filter(function (o) { return o.dataset.room === s.room; })[0];
      opts.forEach(function (o) { o.setAttribute("aria-pressed", String(o === pick)); });
      out.dates.textContent = s.a ? short(s.a) + (s.b ? " to " + short(s.b) : "") : "Choose dates";
      out.nights.textContent = n ? n + (n === 1 ? " night" : " nights") : "None yet";
      out.guests.textContent = guestLabel(s);
      out.room.textContent = pick ? pick.dataset.name : "Choose a room";
      var rate = pick ? +pick.dataset.rate : 0;
      out.rate.textContent = rate ? "$" + rate + " a night" : "None yet";
      out.total.textContent = rate && n ? "$" + (rate * n).toLocaleString("en-US") : "$0";
      send.disabled = !(n && pick);
    };
    Calendar($(".cal", bk), s, sync);
    steppers(bk, s, sync);
    $$("[data-step]", bk).forEach(function (row) { $("output", row).textContent = s[row.dataset.step]; });
    opts.forEach(function (o) { o.addEventListener("click", function () { s.room = o.dataset.room; sync(); }); });
    sync();
  })();

  /* driver */
  function measureAll() {
    vh = innerHeight; vw = innerWidth;
    scenes.forEach(function (s) { if (s.layout) s.layout(); });
    scenes.forEach(function (s) { if (s.measure) s.measure(); });
    if (lenis) lenis.resize();
    dirty = true;
  }

  function frame(t) {
    if (lenis) lenis.raf(t);
    y = window.scrollY;
    var moved = y !== last || dirty;
    for (var i = 0; i < scenes.length; i++) {
      var s = scenes[i];
      if (s.update && (moved || s.always)) s.update(t);
    }
    last = y; dirty = false; first = false;
    requestAnimationFrame(frame);
  }

  root.classList.add("ready");
  measureAll();
  requestAnimationFrame(frame);
  addEventListener("resize", measureAll);
  addEventListener("load", measureAll);
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(measureAll);
})();
