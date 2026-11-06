#!/usr/bin/env python3
"""Static checks on the built site: every local link, asset and #anchor resolves, and no page repeats a photo."""
import collections, glob, os, re, sys
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = [p for p in glob.glob(ROOT + "/**/index.html", recursive=True)]
class H(HTMLParser):
    def __init__(s): super().__init__(); s.urls = []; s.ids = set(); s.imgs = []; s.noalt = 0
    def handle_starttag(s, t, a):
        a = dict(a)
        if "id" in a: s.ids.add(a["id"])
        for k in ("href", "src", "poster", "data-1080", "data-720", "data-href", "data-full"):
            if a.get(k): s.urls.append(a[k])
        if a.get("srcset"): s.urls += [x.split()[0] for x in a["srcset"].split(",")]
        if t == "img":
            if "alt" not in a: s.noalt += 1
            m = re.search(r"img/(.+?)-\d+\.webp", a.get("src") or "")
            if m: s.imgs.append(m[1])
parsed = {}
for p in pages:
    h = H(); h.feed(open(p, encoding="utf-8").read()); parsed[os.path.normpath(p)] = h
bad = 0; total = 0
for p, h in parsed.items():
    if h.noalt: print("NO ALT", p, h.noalt); bad += 1
    for u in h.urls:
        if re.match(r"(https?:|mailto:|tel:|data:)", u): continue
        total += 1
        path, _, frag = u.partition("#"); path = path.split("?")[0]
        t = os.path.normpath(os.path.join(os.path.dirname(p), path)) if path else p
        if os.path.isdir(t): t = os.path.join(t, "index.html")
        if not os.path.exists(t): print("MISSING", os.path.relpath(p, ROOT), u); bad += 1; continue
        if frag and t in parsed and frag not in parsed[t].ids: print("NO ANCHOR", os.path.relpath(p, ROOT), u); bad += 1
    dup = [k for k, n in collections.Counter(h.imgs).items() if n > 1]
    if dup: print("REPEATED PHOTO", os.path.relpath(p, ROOT), dup)
print(len(pages), "pages,", total, "local references,", bad, "problems")
sys.exit(1 if bad else 0)
