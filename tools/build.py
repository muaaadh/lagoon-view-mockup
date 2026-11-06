#!/usr/bin/env python3
"""Builds the Lagoon View mockup: every page from the data below, one shared header and footer.

Facts come from the client's 2027 fact sheet first, then their live site. Conflicts between the
two are listed in NOTES.md. Run from anywhere: python3 tools/build.py
"""
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = json.load(open(os.path.join(ROOT, "assets/img/_meta.json")))
VERSION = "1"

# ---------------------------------------------------------------- data

CONTACT = {
    "email": "booking@lagoonviewmaldives.com",
    "reservations": "+960 797 9011",
    "reception": "+960 797 9016",
    "airport": "+960 797 9017",
    "address": ["AA. Bodufolhudhoo", "North Ari Atoll", "Republic of Maldives"],
}

# slug, name, group, from-price, one line, facts, photos
ROOMS = [
    dict(slug="ocean-view-with-pool", name="Ocean View with Pool", group="beach", rate=250, short="pool",
         line="A private plunge pool and sundeck, with the ocean straight ahead.",
         size="30 m²", sleeps="2 adults", bed="Queen or twin", view="Ocean", floor="Ground floor",
         photos=["r-pool-1", "r-pool-2", "r-pool-5", "r-pool-4", "r-pool-6", "r-pool-3"],
         alts=["Sundeck and plunge pool facing the ocean", "Plunge pool beside the villa", "Villa entrance with plunge pool",
               "Veranda seating and plunge pool", "Bed with folded towels and dusk through the windows", "Sunset over the plunge pool and deck"]),
    dict(slug="romantic-beach-villa", name="Romantic Beach Villa", group="beach", rate=240, short="romantic",
         line="Barefoot privacy, with a private plunge pool and your own stretch of beach.",
         size="30 m²", sleeps="2 adults", bed="Queen", view="Sea", floor="Ground floor",
         photos=["r-romantic-1", "r-romantic-2", "r-romantic-3", "r-romantic-4", "r-romantic-5", "r-romantic-6"],
         alts=["The beach through the villa's window", "Villa entrance among beach greenery", "Bedroom with sea view",
               "Bed, minibar and open door to the terrace", "Bed facing the beach", "Bathroom with vessel basin"]),
    dict(slug="deluxe-ocean-view", name="Deluxe Ocean View", group="beach", rate=200, short="ocean",
         line="First-floor room with a king bed, work desk and balcony over the Indian Ocean.",
         size="30 m²", sleeps="3 adults", bed="King", view="Ocean", floor="First floor",
         photos=["r-ocean-1", "r-ocean-2", "r-ocean-3", "r-ocean-4", "r-ocean-5"],
         alts=["King bed and desk", "Bed with balcony doors behind", "Bedroom with television and balcony door",
               "Bed made up with towel swans", "Bathroom with walk-in shower"]),
    dict(slug="deluxe-beach-villa", name="Deluxe Beach Villa", group="beach", rate=110, short="deluxe",
         line="Sea views and direct beach access under the coconut palms.",
         size="20 m²", sleeps="3 adults", bed="Queen or twin", view="Sea", floor="Ground floor",
         photos=["r-deluxe-1", "r-deluxe-2", "r-deluxe-3", "r-deluxe-4", "r-deluxe-5", "r-deluxe-6"],
         alts=["Villa terrace on the sand", "Sun loungers and the sea from the room", "The beach through the bedroom window",
               "Bedroom with desk and sea-view window", "Bed with striped beach towel", "Bathroom with stone basin"]),
    dict(slug="family-beach-villa", name="Family Beach Villa", group="beach", rate=168, short="family",
         line="Steps from the beach, with room for two adults and two children.",
         size="30 m²", sleeps="2 adults, 2 children", bed="Queen and single", view="Sea", floor="Ground floor",
         photos=["r-family-1", "r-family-2", "r-family-3", "r-family-4", "r-family-5"],
         alts=["Queen and single beds", "Villa front with garden planting", "Bedroom with desk and wardrobe",
               "Desk, mirror and wardrobe", "Bathroom with bath tub"]),
    dict(slug="inter-connect-villa", name="Inter-connect Villa", group="beach", rate=250, short="connect",
         line="Two rooms and two bathrooms with a connecting door, on the beachfront.",
         size="60 m²", sleeps="5 adults", bed="2 queens", view="Sea", floor="Ground floor",
         photos=["r-connect-1", "r-connect-2", "r-connect-3"],
         alts=["Two beds and the door to the terrace", "Bedroom with garden view", "Bathroom with long vanity"]),
    dict(slug="two-bedroom-villa", name="Two Bedroom Villa", group="beach", rate=240, short="two",
         line="Two bedrooms, a kitchenette and a large balcony over the ocean.",
         size="60 m²", sleeps="5 guests", bed="2 queens", view="Ocean", floor="First floor",
         photos=["r-two-1", "r-two-2", "r-two-3", "r-two-4", "r-two-5"],
         alts=["Large balcony with loungers", "Master bedroom", "Master bedroom with sofa and balcony doors",
               "Second bedroom", "Balcony view over the palms to the sea"]),
    dict(slug="garden-room", name="Garden Room", group="garden", rate=90, short="garden",
         line="Warm wood and quiet, in the tropical garden.",
         size=None, sleeps="2 adults", bed="Queen", view="Garden", floor="Ground floor",
         photos=["r-garden-1", "r-garden-2", "r-garden-3", "r-garden-4", "r-garden-5", "r-garden-6"],
         alts=["Sandy garden path under the trees", "Bedroom with wood-panelled headboard", "Bed with striped towels",
               "Room entrance and veranda chairs", "Tropical garden planting", "Stone basin and mirror"]),
    dict(slug="two-room-bungalow", name="Two Room Bungalow", group="garden", rate=200, short="bung2",
         line="Two rooms with their own garden area.",
         size=None, sleeps="4 adults", bed="Queen beds", view="Garden", floor="Ground floor",
         photos=["r-bung2-1", "r-bung2-2", "r-bung2-3"],
         alts=["Bungalow courtyard with shaded seating", "Covered terrace among garden beds", "Bedroom with wood headboard"]),
    dict(slug="four-room-bungalow", name="Four Room Bungalow", group="garden", rate=330, short="bung4",
         line="Four double rooms with a private kitchen, BBQ area and smart-lock entrance.",
         size=None, sleeps="8 adults, 2 children", bed="4 queens", view="Garden", floor="Ground floor",
         photos=["r-bung4-1", "r-bung4-2", "r-bung4-3"],
         alts=["Covered outdoor lounge", "Outdoor seating on the sand", "Bungalow rooms beside the garden"]),
]
for i, r in enumerate(ROOMS):
    r["url"] = f"rooms/{r['slug']}/index.html"

STRIP = ["ocean-view-with-pool", "deluxe-ocean-view", "romantic-beach-villa", "deluxe-beach-villa", "two-bedroom-villa", "garden-room"]

# keys: aug = Aug to 20 Dec 2026, jan = Jan to Mar 2027, apr = Apr to Jul 2027 (read from the client's October 2026 offer cards)
PACKAGES = [
    dict(name="5 Nights Honeymoon", per="for two", photo="couple-sand", alt="A couple on a sandbank",
         stay="Deluxe Beach Villa", inc=["Breakfast and dinner", "Candle-light beach dinner", "1 excursion", "Speedboat transfers"],
         aug="1,570", jan="2,055", apr=None, low=1570),
    dict(name="5 Nights Romance", per="for two", photo="r-pool-3", alt="Sunset from the plunge pool deck",
         stay="Ocean View with Pool", inc=["Breakfast and dinner", "2 excursions", "Speedboat transfers"],
         aug="2,050", jan="2,550", apr="1,700", low=1700),
    dict(name="Family Get-Away", per="2 adults, 1 child", photo="x-sand", alt="A child walking on a sandbank",
         stay="Family Beach Villa", inc=["Breakfast and dinner", "2 excursions", "Speedboat transfers"],
         aug="1,950", jan="2,377", apr="1,640", low=1640),
    dict(name="Get-Away with Friends", per="for two", photo="x-boat", alt="A speedboat on the lagoon",
         stay="Deluxe Beach Villa", inc=["Breakfast and dinner", "2 excursions", "Speedboat transfers"],
         aug="1,390", jan="1,950", apr="999", low=999),
    dict(name="Scuba Escape", per="per diver", photo="d-pair", alt="Two divers over the reef",
         stay="Garden Room", inc=["8 dives", "Breakfast and dinner", "Speedboat transfers"],
         aug="1,090", jan="1,290", apr="800", low=800),
]
SEASONS = [("aug", "Aug to Dec 2026"), ("jan", "Jan to Mar 2027"), ("apr", "Apr to Jul 2027")]

DAYS = [
    ("Snorkeling", "Mantas, turtles, wrecks and nurse sharks", "x-manta-swim", "A swimmer among manta rays", "snorkeling"),
    ("Sandbanks", "Picnics on the nearby sandbanks", "sandbank-walk", "A person walking along a sandbank from the air", "islands"),
    ("Nurse sharks", "Snorkel with them at Gangehi, 30 minutes away", "x-sharks", "Nurse sharks and a snorkeler in the shallows", "snorkeling"),
    ("Water sports", "Jet-ski, tubing, wakeboard, windsurf", "x-tube", "Tubing behind a speedboat", "water-sports"),
    ("Island hopping", "Local islands and neighbouring resorts", "x-boat", "A speedboat on the lagoon", "islands"),
]

CHAPTERS = [
    dict(id="snorkeling", name="Snorkeling", photo="x-mantas", alt="Manta rays and a swimmer over the reef",
         line="Guided trips of one to two hours. The house reef costs nothing extra.",
         items=["Turtle reef", "Manta rays", "Nurse sharks at Gangehi", "Mathiveri wreck", "House reef at night"]),
    dict(id="islands", name="Sandbanks and islands", photo="sandbank-spit", ar="4/5", alt="A sandbank curving through the lagoon from the air",
         line="Picnic on the sand, or spend a day on a local island.",
         items=["Mathiveri Sandbank", "Dhinnolhu Sandbank", "Mathiveri, Feridhoo and Maalhos", "Day visits to Nika and Gangehi"]),
    dict(id="search", name="Manta and dolphin search", photo="x-turtle", alt="A turtle over the reef with snorkelers above",
         line="One to two hours within a 10 mile radius. Two people minimum.",
         items=["Manta ray search", "Dolphin search", "Lobster hunt"]),
    dict(id="water-sports", name="Water sports", photo="x-wind", alt="Windsurfing on the lagoon",
         line="Twenty-minute rides, plus kayaks and paddleboards.",
         items=["Jet-ski", "Fun tube", "Wakeboard", "Windsurf", "Kayak and paddleboard"]),
    dict(id="fishing", name="Fishing", photo="x-fishing", alt="Guests with the evening catch",
         line="Your catch can go straight to the kitchen.",
         items=["Sunset fishing, 2 hours", "Deep bottom fishing, 2 hours", "Jigging and popping, 3 hours", "Big game, 4 hours"]),
    dict(id="cruises", name="Cruises", photo="x-cruise", alt="Guests waving from a speedboat",
         line="One to two hours, with sandbank stops and dolphin spotting.",
         items=["Sunset cruise", "Celebration cruise"]),
]

MENUS = [
    ("Mains", [("Fisherman's Catch", 12), ("Spicy Green Fish Curry", 10), ("Nasi Goreng", 10), ("Thai Green Chicken Curry", 10),
               ("Spaghetti Alla Frutti Di Mare", 12), ("Tender Beef Burger", 10), ("Lagoon View Stuffed Chicken", 40), ("Australian T-Bone Steak", 60)]),
    ("Starters", [("Tom Yum", 10), ("Cream of Mushroom", 8), ("Caesar's Salad", 10), ("Chunky Greek Salad", 10),
                  ("Grilled Vegetable Salad", 10), ("Seafood Salad", 19)]),
    ("Breakfast", [("Lagoon View Breakfast", 10), ("Lagoon View Continental", 10), ("Lagoon View English Breakfast", 10), ("Lagoon View Traditional Breakfast", 10)]),
    ("Snacks and drinks", [("Grilled Tuna Sandwich", 6), ("Fillet-O-Fish Sandwich", 7), ("Passion Mojito", 7), ("Mango Colada", 8),
                           ("Lagoon Blue Ocean", 8), ("Fresh juice", 7), ("Iced Lemon Tea", 5), ("Milkshake", 7)]),
]

GALLERY = [
    ("aerial-reef", "The hotel and house reef from the air"), ("r-pool-1", "Plunge pool deck facing the ocean"),
    ("x-mantas", "Manta rays and a swimmer"), ("r-pool-3", "Sunset from the deck"), ("sandbank-walk", "A sandbank from the air"),
    ("beach-pano", "The private beach seen from the water"), ("x-sharks", "Nurse sharks in the shallows"),
    ("r-romantic-1", "The beach through a villa window"), ("dhoni", "A dhoni moored in the lagoon"), ("d-school", "A diver in a school of fish"),
    ("r-ocean-1", "Deluxe Ocean View bedroom"), ("sandbank-spit", "A sandbank curving through the lagoon"),
    ("x-turtle", "A turtle on the reef"), ("r-deluxe-1", "Deluxe Beach Villa terrace"), ("r-garden-1", "The garden path"),
    ("d-shark", "A reef shark from below"), ("private-beach", "Sunbeds on the private beach"), ("x-tube", "Tubing on the lagoon"),
    ("r-two-1", "The Two Bedroom Villa balcony"), ("x-snorkel", "Snorkelers on the reef"),
]

NAV = [("Stay", "rooms/index.html"), ("Dining", "dining/index.html"), ("Activities", "activities/index.html"), ("Dive", "dive/index.html"),
       ("Packages", "packages/index.html"), ("Gallery", "gallery/index.html"), ("Contact", "contact/index.html")]

# ---------------------------------------------------------------- helpers

esc = html.escape
PAGES = {}


def rel(prefix, url):
    return prefix + url


class P:
    """One page being written: knows how deep it sits so every link stays relative."""

    def __init__(self, path):
        self.path = path
        self.r = "../" * path.count("/")

    def u(self, url):
        return self.r + url

    def src(self, key, w):
        return self.r + f"assets/img/{key}-{w}.webp"

    def img(self, key, alt, sizes="100vw", eager=False, cap=None):
        m = META[key]
        tiers = [t for t in m["tiers"] if not cap or t <= cap] or m["tiers"][:1]
        srcset = ", ".join(f"{self.src(key, t)} {t}w" for t in tiers)
        mid = min(tiers, key=lambda t: abs(t - 1024))
        load = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return (f'<img src="{self.src(key, mid)}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}" '
                f'alt="{esc(alt)}" {load} decoding="async">')

    def fig(self, key, alt, sizes="100vw", ar="3/2", para=True, cls="", pos=None, attrs="", eager=False):
        style = f"--bg:{META[key]['avg']};--ar:{ar}" + (f";--pos:{pos}" if pos else "")
        c = "fig" + ("" if para else " fig--still") + (f" {cls}" if cls else "")
        return f'<figure class="{c}" style="{style}"{" data-p" if para else ""} {attrs}>{self.img(key, alt, sizes, eager)}</figure>'

    def film(self, name, poster_alt=""):
        f = self.r + f"assets/film/{name}"
        return (f'<video data-film data-1080="{f}-1080.mp4" data-720="{f}-720.mp4" poster="{f}-poster.jpg" '
                f'muted loop playsinline preload="none" aria-label="{esc(poster_alt)}"></video>')


def header(p, current, top):
    nav = "".join(f'<a href="{p.u(u)}"{" aria-current=page" if u == current else ""}>{n}</a>' for n, u in NAV)
    menu = "".join(f'<a href="{p.u(u)}">{n}</a>' for n, u in NAV)
    over = " over" if top in ("hero", "photo") else ""
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="hd{over}">
  <a class="hd__logo" href="{p.u('index.html')}" aria-label="Lagoon View Maldives home"><span class="logo"></span></a>
  <nav class="hd__nav" aria-label="Main">{nav}</nav>
  <a class="btn" href="{p.u('book/index.html')}">Book</a>
  <button class="hd__menu" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
</header>
<div class="menu" id="menu">{menu}<a class="btn btn--light" href="{p.u('book/index.html')}">Book</a></div>
'''


def footer(p, flat=False):
    c = CONTACT
    return f'''<footer class="ft{' ft--flat' if flat else ''}">
  <div class="ft__cta"><h2 class="t2 rv">Plan your stay</h2><a class="btn btn--light rv" href="{p.u('book/index.html')}">Check availability</a></div>
  <div class="ft__grid">
    <div><h3>Reservations</h3><a href="tel:{c['reservations'].replace(' ', '')}">{c['reservations']}</a><br><a href="mailto:{c['email']}">{c['email']}</a></div>
    <div><h3>Reception</h3><a href="tel:{c['reception'].replace(' ', '')}">{c['reception']}</a><br>6am to 11pm</div>
    <div><h3>Find us</h3>{'<br>'.join(c['address'])}</div>
    <div><h3>Follow</h3><a href="https://www.instagram.com/lagoon_view_maldives/" rel="noopener">Instagram</a><br><a href="https://www.facebook.com/lagoonviewmaldives/" rel="noopener">Facebook</a><br><a href="https://www.tripadvisor.ch/Hotel_Review-g7777553-d7761871-Reviews-Lagoon_View_Maldives-Bodufolhudhoo.html" rel="noopener">Tripadvisor</a></div>
  </div>
  <div class="ft__end"><span>© 2026 Lagoon View Maldives</span><button type="button" data-surface>Back to the surface</button></div>
</footer>
'''


def page(path, title, desc, body, current="", top="plain", cls="", flat_footer=False):
    p = P(path)
    html_ = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0a6283">
<link rel="icon" href="{p.u('assets/logo/favicon.svg')}" type="image/svg+xml">
<link rel="preload" href="{p.u('assets/fonts/host-grotesk.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p.u('assets/css/site.css')}?v={VERSION}">
<script>document.documentElement.classList.add("js")</script>
</head>
<body data-top="{top}"{f' class="{cls}"' if cls else ''}>
{header(p, current, top)}<main id="main">
{body(p)}</main>
{footer(p, flat_footer)}<script src="{p.u('assets/js/lenis.min.js')}"></script>
<script src="{p.u('assets/js/site.js')}?v={VERSION}"></script>
</body>
</html>
'''
    PAGES[path] = html_


def room(slug):
    return next(r for r in ROOMS if r["slug"] == slug)


# ---------------------------------------------------------------- home

def home(p):
    slides = ""
    for i, s in enumerate(STRIP):
        r = room(s)
        ar = "4/5" if i % 2 == 0 else "3/2"
        slides += (f'<a class="slide" href="{p.u(r["url"])}">{p.fig(r["photos"][0], r["alts"][0], "(min-width:900px) 52vw, 78vw", ar, para=False)}'
                   f'<span class="slide__t"><span>{r["name"]}</span><span class="soft sm">From ${r["rate"]}</span></span></a>')
    rows = ""
    pics = ""
    for i, (n, dsc, ph, alt, anchor) in enumerate(DAYS):
        on = " on" if i == 0 else ""
        rows += (f'<a class="day{on}" href="{p.u("activities/index.html#" + anchor)}">{p.fig(ph, alt, "100vw", "3/2", para=False)}'
                 f'<span class="day__n">{n}</span><span class="day__d">{dsc}</span></a>')
        pics += p.fig(ph, alt, "(min-width:900px) 54vw, 1px", "auto", para=False, cls=on.strip())
    pk = ""
    for k in PACKAGES:
        pk += (f'<a href="{p.u("packages/index.html")}"><span class="row__n">{k["name"]}</span>'
               f'<span class="row__s soft">{k["stay"]}</span><span class="row__p">From ${k["low"]:,} {k["per"]}</span></a>')
    return f'''<section class="hero" aria-label="Lagoon View Maldives">
  <div class="hero__stage">
    <div class="hero__frame">{p.film("lagoon", "Drone film flying across the lagoon towards the hotel jetty")}</div>
    <div class="hero__copy"><h1 class="t1"><span class="ln">Private beach. Living reef.</span> <span class="ln">Right outside your room.</span></h1></div>
    <div class="bar">
      <button class="bar__f" type="button" data-f="in" aria-expanded="false"><small>Check in</small><b>Add date</b></button>
      <button class="bar__f" type="button" data-f="out" aria-expanded="false"><small>Check out</small><b>Add date</b></button>
      <button class="bar__f" type="button" data-f="guests" aria-expanded="false"><small>Guests</small><b>2 adults</b></button>
      <a class="btn" href="{p.u('book/index.html')}" data-href="{p.u('book/index.html')}">Check availability</a>
      <div class="pop pop--cal"><div class="cal"></div></div>
      <div class="pop pop--guests">
        <div class="step" data-step="adults"><span>Adults</span><span class="step__c"><button type="button" data-d="-1" aria-label="Fewer adults">−</button><output>2</output><button type="button" data-d="1" aria-label="More adults">+</button></span></div>
        <div class="step" data-step="kids"><span>Children<small>2 to 11 years</small></span><span class="step__c"><button type="button" data-d="-1" aria-label="Fewer children">−</button><output>0</output><button type="button" data-d="1" aria-label="More children">+</button></span></div>
      </div>
    </div>
    <button class="filmbtn" type="button">Pause film</button>
  </div>
</section>

<section class="say">
  <p class="say__t" data-fill>A beachfront hotel on Bodufolhudhoo, a local island in North Ari Atoll.</p>
  <ul class="say__tags soft" data-stagger><li class="rv">Private bikini beach</li><li class="rv">Free house reef snorkeling</li><li class="rv">PADI dive centre</li><li class="rv">Tripadvisor Travelers' Choice 2025</li></ul>
</section>

<section class="strip" aria-label="Rooms and villas">
  <div class="strip__stage">
    <div class="strip__head"><h2 class="t2">Rooms and villas</h2><a class="lnk" href="{p.u('rooms/index.html')}">See all rooms</a></div>
    <div class="strip__rail">{slides}</div>
  </div>
</section>

<section class="split">
  {p.fig("f-fish", "Whole grilled fish with lemon", "(min-width:900px) 58vw, 100vw", "3/2")}
  <div class="split__txt">
    <h2 class="t2" data-split>Lagoon Breeze</h2>
    <p class="lead rv">Fresh seafood, Maldivian plates and Western favourites.</p>
    <a class="lnk rv" href="{p.u('dining/index.html')}">See the menus</a>
  </div>
</section>

<section class="wl" aria-label="From the beach to the house reef">
  <div class="wl__stage">
    <div class="wl__under">{p.film("shark", "Nurse shark swimming over the reef")}</div>
    <div class="wl__over">{p.img("beach-pano", "The private beach seen from the water", "(max-aspect-ratio: 2/1) 245vh, 100vw")}</div>
    <svg class="wl__line" aria-hidden="true"><path d=""/></svg>
    <p class="wl__t wl__t--a">Your private beach.</p>
    <p class="wl__t wl__t--b">The house reef, 15 metres from shore.</p>
    <button class="filmbtn" type="button">Pause film</button>
  </div>
</section>

<section class="days on-dark" aria-label="Activities">
  <div class="days__grid">
    <div class="days__list">{rows}<a class="lnk" href="{p.u('activities/index.html')}">See all activities</a></div>
    <div class="days__pic">{pics}</div>
  </div>
</section>

<section class="dv on-dark">
  <div class="dv__grid">
    <div class="dv__a">{p.fig("d-wreck", "Divers at a wreck", "(min-width:900px) 64vw, 100vw", "16/9")}</div>
    <div class="dv__txt">
      <span class="logo-dive" role="img" aria-label="Lagoon Dive Club logo" style="display:block"></span>
      <h2 class="t2" data-split>Lagoon Dive Club</h2>
      <p class="lead rv">A PADI dive centre with over 35 dive sites nearby.</p>
      <a class="btn btn--light rv" href="{p.u('dive/index.html')}">Dive with us</a>
    </div>
    <div class="dv__b" data-shift="-56">{p.fig("d-school", "A diver in a school of fish", "(min-width:900px) 30vw, 62vw", "4/5", para=False)}</div>
    <div class="dv__c" data-shift="46">{p.fig("d-shark", "A reef shark from below", "(min-width:900px) 56vw, 100vw", "3/2", para=False)}</div>
  </div>
</section>

<section class="pk on-dark">
  <div class="pk__head"><h2 class="t2" data-split>Packages</h2><a class="lnk" href="{p.u('packages/index.html')}">See all packages</a></div>
  <div class="rowlist">{pk}</div>
</section>
'''


# ---------------------------------------------------------------- rooms

def rooms_index(p):
    def group(g):
        out = ""
        for r in [x for x in ROOMS if x["group"] == g]:
            facts = [r["sleeps"]] + ([r["size"]] if r["size"] else [])
            out += (f'<a class="ritem" href="{p.u(r["url"])}">{p.fig(r["photos"][0], r["alts"][0], "(min-width:900px) 64vw, 100vw", "3/2")}'
                    f'<div class="ritem__t"><h3 class="t3 rv">{r["name"]}</h3><p class="soft rv">{r["line"]}</p>'
                    f'<p class="rv">From ${r["rate"]} a night</p><p class="soft sm rv">{", ".join(facts)}</p></div></a>')
        return out
    return f'''<div class="page-top"><h1 class="t1" data-split>Rooms and villas</h1><p class="lead soft rv">On the beach and in the garden. From $90 a night, plus taxes and fees.</p></div>
<div class="rgroup"><h2 class="t2 rv">On the beach</h2></div>
<div class="rlist">{group("beach")}</div>
<div class="rgroup"><h2 class="t2 rv">In the garden</h2><p class="soft rv">A five-minute walk from the beach</p></div>
<div class="rlist">{group("garden")}</div>
'''


AMENITIES = ["Air conditioning and fan", "Free Wi-Fi", "Safe", "Mini-freezer", "Kettle and coffee set", "Beach towels and bathrobes"]


def room_page(r, nxt):
    def body(p):
        rows = [("From", f'${r["rate"]} a night'), ("Sleeps", r["sleeps"]), ("Bed", r["bed"]), ("View", r["view"]), ("Level", r["floor"])]
        if r["size"]:
            rows.insert(2, ("Size", r["size"]))
        dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)
        gal = "".join(p.fig(k, a, "(min-width:900px) 92vw, 100vw") for k, a in list(zip(r["photos"], r["alts"]))[1:])
        amen = "".join(f"<li>{a}</li>" for a in AMENITIES)
        return f'''<section class="ph"><div class="ph__m">{p.img(r["photos"][0], r["alts"][0], "(max-aspect-ratio: 4/3) 136vh, 100vw", eager=True)}</div>
  <div class="ph__t"><h1 class="t1">{r["name"]}</h1></div></section>
<section class="facts">
  <div class="facts__p"><p class="t3 rv">{r["line"]}</p><a class="btn rv" href="{p.u('book/index.html')}?room={r['slug']}">Book this room</a></div>
  <dl class="rv">{dl}</dl>
</section>
<section class="gal" aria-label="Photos">{gal}</section>
<section class="amen"><h2 class="t2 rv">In every room</h2><ul class="rv">{amen}</ul></section>
<a class="next" href="{p.u(nxt["url"])}">{p.fig(nxt["photos"][0], nxt["alts"][0], "(max-aspect-ratio: 4/3) 90vh, 100vw", "auto")}<span class="next__t"><small>Next room</small><span class="t2">{nxt["name"]}</span></span></a>
'''
    return body


# ---------------------------------------------------------------- experiences

def experiences(p):
    ch = ""
    for c in CHAPTERS:
        items = "".join(f"<li>{i}</li>" for i in c["items"])
        ch += (f'<section class="ch" id="{c["id"]}">{p.fig(c["photo"], c["alt"], "(min-width:900px) 64vw, 100vw", c.get("ar", "3/2"))}'
               f'<div class="ch__t"><h2 class="t3 rv">{c["name"]}</h2><p class="soft rv">{c["line"]}</p><ul class="rv">{items}</ul></div></section>\n')
    return f'''<section class="ph"><div class="ph__m">{p.film("sandbank", "Drone film circling a couple on a sandbank")}</div>
  <div class="ph__t"><h1 class="t1">Activities</h1><p class="lead">Sandbanks, reefs and open water, a short boat ride away.</p></div>
  <button class="filmbtn" type="button">Pause film</button></section>
<div style="height:clamp(30px,6vh,60px)"></div>
{ch}<section class="ch__plain" id="spa">
  <h2 class="t2 rv">Spa and gym</h2>
  <div><p class="rv">Massages, facials, couple treatments and yoga. Open 11am to 11pm.</p><p class="soft rv" style="margin-top:12px">A compact fitness studio for daily workouts.</p></div>
</section>
'''


# ---------------------------------------------------------------- dive

def dive(p):
    courses = "".join(f"<li><span>{a}</span><span class='soft'>{b}</span></li>" for a, b in [
        ("Discover Scuba Diving", "First time"), ("Open Water Diver", "Beginner"), ("Rescue Diver", "Advanced"), ("Divemaster", "Professional")])
    packs = "".join(f'<div><span class="row__n">{a}</span><span class="row__s soft">{b}</span><span class="row__p">From ${c} per diver</span></div>' for a, b, c in [
        ("Scuba Escape", "5 nights, 8 dives", "800"), ("Scuba Diving Holiday", "7 nights, 10 dives", "995"), ("Ocean Explorer Holiday", "10 nights, 16 dives", "1,400")])
    return f'''<section class="ph"><div class="ph__m">{p.img("d-shark", "A reef shark from below, with fish above", "(max-aspect-ratio: 4/3) 136vh, 100vw", eager=True)}</div>
  <div class="ph__t"><h1 class="t1">Lagoon Dive Club</h1><p class="lead">A PADI dive centre with over 35 dive sites nearby.</p></div></section>
<div class="page-deep on-dark">
<section class="two">
  <h2 class="t2" data-split>Learn with us</h2>
  <div><p class="rv">Two morning dives a day, then afternoon or special dives depending on conditions. Open 8am to 6pm.</p><ul class="courses rv">{courses}</ul></div>
</section>
<section class="band">
  <div class="dv__grid">
    <div class="dv__a">{p.fig("d-wreck2", "A diver at a wreck", "(min-width:900px) 64vw, 100vw", "16/9")}</div>
    <div class="dv__txt"><h2 class="t3 rv">Wrecks and reefs</h2><p class="soft rv">Depths from 2 to 25 metres on the house reef, just off the beach.</p></div>
    <div class="dv__b" data-shift="-50">{p.fig("d-pair", "Two divers over the reef", "(min-width:900px) 30vw, 62vw", "4/5", para=False, pos="30% 50%")}</div>
    <div class="dv__c" data-shift="40">{p.fig("d-school", "A diver in a school of fish", "(min-width:900px) 56vw, 100vw", "3/2", para=False)}</div>
  </div>
</section>
<section class="band">
  <div class="h-row"><h2 class="t2" data-split>Dive packages</h2><a class="lnk" href="{p.u('packages/index.html')}">All packages</a></div>
  <div class="rowlist">{packs}</div>
  <p class="soft sm" style="margin-top:18px">Garden Room, breakfast and dinner, boat dives, tank and weights, and speedboat transfers included.</p>
</section>
<section class="two">
  <h2 class="t2" data-split>Coral restoration</h2>
  <div><p class="rv">Divers and marine biologists plant coral frames on Bodufolhudhoo Reef and monitor them. Ask how to join in.</p><p class="soft rv">PADI dive centre. DAN Europe partner.</p><a class="lnk rv" href="mailto:dive@lagoonviewmaldives.com">dive@lagoonviewmaldives.com</a></div>
</section>
<section>{p.fig("d-team", "The Lagoon Dive Club team", "100vw", "21/9", pos="50% 35%")}</section>
</div>
'''


# ---------------------------------------------------------------- dining

def dining(p):
    tabs = ""
    panes = ""
    for i, (n, items) in enumerate(MENUS):
        tabs += f'<button class="tab" type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}">{n}</button>'
        rows = "".join(f"<li><span>{esc(a)}</span><span>${b}</span></li>" for a, b in items)
        panes += f'<ul class="menu-p{" on" if i == 0 else ""}">{rows}</ul>'
    return f'''<div class="page-top page-top--pic"><div><h1 class="t1" data-split>Lagoon Breeze</h1><p class="lead soft rv">Restaurant and coffee bar, open 6am to 11pm.</p></div>{p.fig("f-restaurant", "The Lagoon Breeze restaurant at dusk", "400px", "3/2", para=False)}</div>
<section class="split" style="background:none;padding-top:0">
  {p.fig("f-fish", "Whole grilled fish with lemon", "(min-width:900px) 58vw, 100vw", "3/2")}
  <div class="split__txt"><p class="t3 rv">Fresh local ingredients, from Maldivian curries to seafood, pasta and steaks.</p><p class="soft rv">Vegetarian and gluten-free menus too.</p></div>
</section>
<section class="hours" aria-label="Meal times" data-stagger>
  <div class="rv"><b style="font-weight:500">Breakfast</b><br><span class="soft">8am to 10am</span></div>
  <div class="rv"><b style="font-weight:500">Lunch</b><br><span class="soft">1pm to 3pm</span></div>
  <div class="rv"><b style="font-weight:500">Dinner</b><br><span class="soft">8pm to 10pm</span></div>
</section>
<section class="band" style="background:var(--foam)">
  <h2 class="t2 rv" style="margin-bottom:clamp(24px,4vh,40px)">From the menu</h2>
  <div><div class="tabs" role="tablist" data-tabs>{tabs}</div>{panes}</div>
</section>
<section class="split" style="grid-template-columns:5fr 7fr;background:none;padding-left:var(--g);padding-right:0">
  <div class="split__txt"><h2 class="t2" data-split>Dinner on the sand</h2><p class="lead soft rv">A candle-lit table on the beach, set up just for you.</p><a class="lnk rv" href="{p.u('contact/index.html')}">Ask us</a></div>
  {p.fig("f-platter", "Grilled fish and octopus platters", "(min-width:900px) 58vw, 100vw", "3/2", pos="50% 70%")}
</section>
'''


# ---------------------------------------------------------------- packages

def packages(p):
    tabs = "".join(f'<button class="tab" type="button" data-s="{k}" aria-pressed="false">{n}</button>' for k, n in SEASONS)
    cards = ""
    for k in PACKAGES:
        inc = "".join(f"<li>{i}</li>" for i in [k["stay"]] + k["inc"])
        data = " ".join(f'data-{s}="{k[s]}"' for s, _ in SEASONS if k[s])
        first = k["aug"]
        cards += (f'<article class="pcard">{p.fig(k["photo"], k["alt"], "(min-width:900px) 42vw, 100vw", "3/2")}'
                  f'<div class="pcard__t"><h2 class="t2 rv">{k["name"]}</h2>'
                  f'<p class="pcard__price rv" data-price {data}>${first}<small>{k["per"]}</small></p>'
                  f'<ul class="rv">{inc}</ul><a class="lnk rv" href="{p.u("book/index.html")}">Enquire</a></div></article>\n')
    return f'''<div class="page-top"><h1 class="t1" data-split>Packages</h1><p class="lead soft rv">Five nights with meals and transfers, priced by season.</p>
  <div class="tabs" data-seasons style="margin:clamp(26px,4vh,40px) 0 0">{tabs}</div></div>
{cards}<div style="height:clamp(30px,6vh,70px)"></div>
'''


# ---------------------------------------------------------------- gallery

def gallery(p):
    cells = ""
    for k, a in GALLERY:
        m = META[k]
        full = p.src(k, m["tiers"][-1])
        cells += f'<button type="button" data-full="{full}" data-alt="{esc(a)}" aria-label="Open photo: {esc(a)}">{p.fig(k, a, "(min-width:900px) 46vw, 100vw", "3/2", para=False)}</button>'
    return f'''<div class="page-top"><h1 class="t1" data-split>Gallery</h1></div>
<div class="grid-g">{cells}</div>
<dialog class="lb" aria-label="Photo viewer"><img alt=""><button class="lb__b lb__x" type="button">Close</button><button class="lb__b lb__p" type="button">Previous</button><span class="lb__c"></span><button class="lb__b lb__n" type="button">Next</button></dialog>
'''


# ---------------------------------------------------------------- contact

FAQ = [
    ("When is check-in and check-out?", "Check-in is at 2pm and check-out at 11am."),
    ("Can I wear a bikini?", "Yes, at the hotel and on our private beach. Outside the hotel, please dress modestly with shoulders and knees covered."),
    ("Is alcohol available?", "Alcohol is not allowed on local islands. Nika and Gangehi resorts are a five-minute boat ride away if you would like a drink."),
    ("Is there Wi-Fi?", "Yes, Wi-Fi is free."),
    ("How can I pay?", "USD, Euro, British Pounds or card. Local shops usually prefer cash."),
    ("Is there a dress code?", "Not at the hotel, but please cover swimwear in the restaurant."),
]


def contact(p):
    c = CONTACT
    ways = "".join(f'<div><span class="row__n">{a}</span><span class="row__s soft">{b}</span><span class="row__p">{d}</span></div>' for a, b, d in [
        ("Speedboat", "90 minutes. Airport to hotel at 10am, 2pm and 4pm.", "$50 each way"),
        ("Seaplane", "20 minutes to Nika Island, then 5 minutes by boat.", "$300 each way"),
        ("Ferry", "5 to 6 hours, about three days a week.", "About $10 each way")])
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    return f'''<div class="page-top"><h1 class="t1" data-split>Contact</h1></div>
<section class="ctop">
  <ul class="ctop__l">
    <li><span class="soft">Reservations</span><a href="tel:{c['reservations'].replace(' ', '')}">{c['reservations']}</a></li>
    <li><span class="soft">Reception</span><a href="tel:{c['reception'].replace(' ', '')}">{c['reception']}</a></li>
    <li><span class="soft">Airport pick-up</span><a href="tel:{c['airport'].replace(' ', '')}">{c['airport']}</a></li>
    <li><span class="soft">Email</span><a href="mailto:{c['email']}">{c['email']}</a></li>
    <li><span class="soft">Address</span><span style="text-align:right">{'<br>'.join(c['address'])}</span></li>
  </ul>
  <form class="ctop__r fgrid" data-mock="Message sent. We will reply within 24 hours.">
    <label class="field"><span>Name</span><input name="name" required autocomplete="name"></label>
    <label class="field"><span>Email</span><input name="email" type="email" required autocomplete="email"></label>
    <label class="field field--w"><span>Message</span><textarea name="message" required></textarea></label>
    <div class="field--w"><button class="btn" type="submit">Send message</button></div>
  </form>
</section>
<section>{p.fig("aerial-hotel", "The hotel, jetty and lagoon from the air", "100vw", "21/9", pos="50% 45%")}</section>
<section class="ways" style="background:var(--foam)">
  <div class="h-row"><h2 class="t2" data-split>Getting here</h2><p class="soft">73 km from Velana International Airport</p></div>
  <div class="rowlist rowlist--ink">{ways}</div>
</section>
<section class="faq"><h2 class="t2" data-split>Good to know</h2><div class="faq__l">{faq}</div></section>
'''


# ---------------------------------------------------------------- book

def book(p):
    opts = ""
    for r in ROOMS:
        opts += (f'<button class="opt" type="button" data-room="{r["slug"]}" data-name="{r["name"]}" data-rate="{r["rate"]}" aria-pressed="false">'
                 f'{p.fig(r["photos"][0], "", "124px", "4/3", para=False)}<span><b>{r["name"]}</b><span class="soft sm">{r["sleeps"]}</span></span><span>From ${r["rate"]}</span></button>')
    return f'''<div class="page-top"><h1 class="t1" data-split>Book your stay</h1></div>
<section class="bk">
  <div class="bk__m">
    <h2 class="bk__h">Dates</h2>
    <div class="cal"></div>
    <h2 class="bk__h">Guests</h2>
    <div style="max-width:420px">
      <div class="step" data-step="adults"><span>Adults</span><span class="step__c"><button type="button" data-d="-1" aria-label="Fewer adults">−</button><output>2</output><button type="button" data-d="1" aria-label="More adults">+</button></span></div>
      <div class="step" data-step="kids"><span>Children<small>2 to 11 years</small></span><span class="step__c"><button type="button" data-d="-1" aria-label="Fewer children">−</button><output>0</output><button type="button" data-d="1" aria-label="More children">+</button></span></div>
    </div>
    <h2 class="bk__h">Room</h2>
    <div>{opts}</div>
  </div>
  <aside class="bk__s" aria-label="Your stay">
    <h2 class="t3">Your stay</h2>
    <ul class="sum" style="margin-top:14px">
      <li><span class="soft">Dates</span><span data-o="dates" style="text-align:right"></span></li>
      <li><span class="soft">Nights</span><span data-o="nights"></span></li>
      <li><span class="soft">Guests</span><span data-o="guests" style="text-align:right"></span></li>
      <li><span class="soft">Room</span><span data-o="room" style="text-align:right"></span></li>
      <li><span class="soft">Rate</span><span data-o="rate"></span></li>
      <li class="sum__tot"><span>Estimate</span><span data-o="total"></span></li>
    </ul>
    <p class="note" style="margin-top:6px">Plus taxes and fees.</p>
    <form data-mock="Request sent. Reservations will confirm within 24 hours."><button class="btn" type="submit" data-send disabled>Send booking request</button></form>
    <p class="note" style="margin-top:12px">Mockup: no booking is made.</p>
  </aside>
</section>
'''


# ---------------------------------------------------------------- write

def main():
    page("index.html", "Lagoon View Maldives", "A beachfront hotel with a private beach and house reef on Bodufolhudhoo, North Ari Atoll.", home, top="hero")
    page("rooms/index.html", "Rooms and villas | Lagoon View Maldives", "Beach villas and garden rooms from $90 a night.", rooms_index, current="rooms/index.html")
    for i, r in enumerate(ROOMS):
        nxt = ROOMS[(i + 1) % len(ROOMS)]
        page(r["url"], f'{r["name"]} | Lagoon View Maldives', r["line"], room_page(r, nxt), current="rooms/index.html", top="photo")
    page("activities/index.html", "Activities | Lagoon View Maldives", "Snorkeling, sandbanks, water sports, fishing and cruises.", experiences, current="activities/index.html", top="photo")
    page("dive/index.html", "Lagoon Dive Club | Lagoon View Maldives", "A PADI dive centre with over 35 dive sites nearby.", dive, current="dive/index.html", top="photo")
    page("dining/index.html", "Lagoon Breeze | Lagoon View Maldives", "Restaurant and coffee bar, open 6am to 11pm.", dining, current="dining/index.html")
    page("packages/index.html", "Packages | Lagoon View Maldives", "Five nights with meals and transfers, priced by season.", packages, current="packages/index.html")
    page("gallery/index.html", "Gallery | Lagoon View Maldives", "Photos of the hotel, beach and reef.", gallery, current="gallery/index.html")
    page("contact/index.html", "Contact | Lagoon View Maldives", "Contact details, transfers and practical information.", contact, current="contact/index.html")
    page("book/index.html", "Book your stay | Lagoon View Maldives", "Request a stay at Lagoon View Maldives.", book)
    for path, body in PAGES.items():
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(body)
    open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    print(len(PAGES), "pages")


if __name__ == "__main__":
    main()
