#!/usr/bin/env python3
"""Lagoon View image pipeline.

Source of truth for every photograph on the site: which original it came from, whether its
GoPro lens bow gets corrected, and which grade it gets. Output is WebP tiers in assets/img,
never upscaled (a tier only exists if the source can honestly fill it).

usage: images.py <source-root> <out-dir> [key ...]
"""
import glob, json, os, sys
import cv2
import numpy as np
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None
TIERS = [640, 1024, 1600, 2400]
Q = 80

# key: (filename pattern under orig/ or a path, grade, lens-correct, crop l,t,r,b as fractions)
M = {
    # island, from the air
    "aerial-reef":    ("docs/fsimg/i-000.jpg", "air"),
    "aerial-hotel":   ("2025_12_Untitled-design-2.png", "air"),
    "sandbank-walk":  ("2026_01_DJI_0120.jpg", "air"),
    "sandbank-spit":  ("2025_04_DJI_0485.jpg", "air"),
    "dhoni":          ("2025_03_DJI_0833.jpg", "air"),
    # on the beach
    "beach-pano":     ("2025_12_IMG_1244_Cut.jpg", "sun"),
    "private-beach":  ("2025_04_3-Private-beach-area-for-the-Room.jpg", "sun"),
    "couple-sand":    ("2026_05_DJI_0950.jpg", "sun"),
    "swimmers":       ("2025_04_20251229_143656.jpg", "sun"),
    # ocean view with pool
    "r-pool-1":  ("2026_01_20251229_111329.jpg", "sun"),
    "r-pool-2":  ("2026_01_20251229_143923.jpg", "sun"),
    "r-pool-3":  ("2026_01_20251229_173038.jpg", "dusk"),
    "r-pool-4":  ("2026_01_20251229_115809.jpg", "room"),
    "r-pool-5":  ("2025_04_25-Room-Exterior.jpg", "sun"),
    "r-pool-6":  ("2025_12_Untitled-design-4.png", "room"),
    # deluxe ocean view (first floor)
    "r-ocean-1": ("2026_01_20251229_142520.jpg", "room"),
    "r-ocean-2": ("2026_01_20251229_142406.jpg", "room"),
    "r-ocean-3": ("2025_04_2-Room-Interior.jpg", "room"),
    "r-ocean-4": ("2025_12_Untitled-design-7.png", "room"),
    "r-ocean-5": ("2026_01_20251229_143606.jpg", "room"),
    # romantic beach villa
    "r-romantic-1": ("2025_04_9-View-from-Room.jpg", "room"),
    "r-romantic-2": ("2025_04_1-Room-Exterior.jpg", "sun"),
    "r-romantic-3": ("2025_04_4-Room-Interior.jpg", "room"),
    "r-romantic-4": ("2025_04_IMG_1204.jpg", "room"),
    "r-romantic-5": ("2025_11_IMG_1192.jpg", "room"),
    "r-romantic-6": ("2025_04_IMG_1118.jpg", "room"),
    # deluxe beach villa
    "r-deluxe-1": ("2025_08_20240316_131634-2.jpg", "sun"),
    "r-deluxe-2": ("2025_04_20240316_124530.jpg", "sun"),
    "r-deluxe-3": ("2025_04_20240316_123559.jpg", "room"),
    "r-deluxe-4": ("2025_04_20240316_124958.jpg", "room"),
    "r-deluxe-5": ("2025_04_20240316_130540.jpg", "room"),
    "r-deluxe-6": ("2025_04_20240316_130341.jpg", "room"),
    # family beach villa
    "r-family-1": ("2025_08_family-room.jpg", "room", True),
    "r-family-2": ("2025_04_Room-Facade-1.jpg", "sun"),
    "r-family-3": ("2025_04_GOPR3110.jpg", "room", True),
    "r-family-4": ("2025_04_GOPR3105.jpg", "room", True),
    "r-family-5": ("2025_04_GOPR3140.jpg", "room", True),
    # inter-connect villa
    "r-connect-1": ("2025_04_GOPR3089.jpg", "room", True),
    "r-connect-2": ("2026_05_GOPR3097.jpg", "room", True),
    "r-connect-3": ("2025_04_GOPR3142.jpg", "room", True),
    # two bedroom villa
    "r-two-1": ("2025_04_13-Balcony.jpg", "room", True),
    "r-two-2": ("2025_04_1-Master-Room.jpg", "room", True),
    "r-two-3": ("2025_04_2-Master-Room-View.jpg", "room", True),
    "r-two-4": ("2025_04_6-Sstandard-Room-View.jpg", "room", True),
    "r-two-5": ("2025_04_15-Balcony.jpg", "room", True),
    # garden room
    "r-garden-1": ("2025_05_20241019_161547.jpg", "sun"),
    "r-garden-2": ("2025_05_20241019_164208.jpg", "room"),
    "r-garden-3": ("2025_05_20241019_164849.jpg", "room"),
    "r-garden-4": ("2025_05_20241019_161200.jpg", "sun"),
    "r-garden-5": ("2025_05_20241019_160912.jpg", "sun"),
    "r-garden-6": ("2025_05_20241019_165214.jpg", "room"),
    # garden bungalows
    "r-bung2-1": ("2026_10_20241019_155029.jpg", "sun"),
    "r-bung2-2": ("2026_10_20241019_155104.jpg", "sun"),
    "r-bung2-3": ("2025_11_20241019_164418.jpg", "room"),
    "r-bung4-1": ("2026_10_20241019_155016.jpg", "sun"),
    "r-bung4-2": ("2026_01_20241019_162126.jpg", "sun"),
    "r-bung4-3": ("2025_11_20241019_161044.jpg", "sun"),
    # in the water
    "x-mantas":     ("2026_10_GOPR3718.jpg", "sea"),
    "x-manta-swim": ("2026_10_GOPR3745-1.jpg", "sea"),
    "x-sharks":     ("2026_10_GOPR1111.jpg", "sea"),
    "x-turtle":     ("2026_10_photo_9_2026-05-20*", "sea"),
    "x-snorkel":    ("2025_04_GOPR7666.jpg", "sea"),
    "x-nurse":      ("2025_04_GOPR7663.jpg", "sea"),
    # on the water
    "x-tube":    ("2025_04_Water-Tube.jpg", "sun"),
    "x-wind":    ("2025_04_Wind-Surfing.jpg", "sun"),
    "x-wake":    ("2025_04_Wake-boarding.jpg", "sun"),
    "x-cruise":  ("2025_04_Cruise-Adventure.jpg", "sun"),
    "x-fishing": ("2025_04_Fishing.jpg", "sun"),
    "x-sand":    ("2025_04_Full-Day-Excursions.jpg", "sun"),
    "x-boat":    ("2025_04_Half-Day-Excursions.jpg", "sun"),
    # diving
    "d-wreck":  ("2026_03_WRECK-DIVE-2.webp", "sea"),
    "d-wreck2": ("2026_03_WRECK-DIVE.webp", "sea"),
    "d-school": ("2025_04_Dive-11-1-2.jpg", "sea"),
    "d-shark":  ("2025_11_GOPR8675.jpg", "deep"),
    "d-pair":   ("2026_05_photo_8_2026-05-10*", "sea"),
    "d-team":   ("docs/fsimg/i-058.jpg", "sun"),
    # dining: the two plates are stock (see CREDITS.md), the building is theirs
    "f-fish":       ("stock/1665401015549-712c0dc5ef85.jpg", "food"),
    "f-platter":    ("stock/1768322264423-4b0adf0cf31b.jpg", "food"),
    "f-restaurant": ("2025_04_Lagoon-View-Maldives-4.jpg", "sun"),
}


def find(root, pat):
    for base in (root, os.path.join(root, "orig")):
        hits = glob.glob(os.path.join(base, pat))
        if hits:
            return max(hits, key=os.path.getsize)
    raise SystemExit(f"no source for {pat}")


def unbow(bgr):
    """Straighten the GoPro wide lens: bowed walls and door frames are the tell of a phone-grade room shot."""
    h, w = bgr.shape[:2]
    K = np.array([[w * .72, 0, w / 2], [0, w * .72, h / 2], [0, 0, 1]], float)
    D = np.array([-.36, .10, 0, 0, 0], float)
    m1, m2 = cv2.initUndistortRectifyMap(K, D, None, K, (w, h), cv2.CV_32FC1)
    out = cv2.remap(bgr, m1, m2, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    c = .045  # trim the stretched rim the remap leaves behind
    return out[int(h * c):int(h * (1 - c)), int(w * c):int(w * (1 - c))]


def window(h, centre, width):
    """Soft hue mask, h and centre in degrees."""
    d = np.abs((h - centre + 180) % 360 - 180)
    return np.clip(1 - d / width, 0, 1) ** .7


def grade(bgr, mode):
    f = bgr.astype(np.float32) / 255
    if mode in ("room", "food"):
        # take most of the yellow cast out of the phone shots; keep some warmth
        m = f.reshape(-1, 3).mean(0)
        f = f * (1 + .45 * (m.mean() / m - 1))
    f = np.clip(f, 0, 1)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    if mode == "room":
        S *= .92
        S *= 1 - .34 * window(H, 352, 30)      # the crimson curtains and bed runners
        S *= 1 - .20 * window(H, 30, 24)       # orange wood
        V = V ** .92                           # lift shadows
        V = 1 - (1 - V) ** 1.06                # keep windows from clipping harder
    elif mode == "sun":
        S *= .95
        S *= 1 - .14 * window(H, 222, 30)      # phone-sky blue
        V = V ** .97
    elif mode == "air":
        S *= .98
    elif mode == "dusk":
        S *= .96
        V = V ** .9
    elif mode == "deep":
        H = (H + 22) % 360                     # pull the green cast towards reef blue
        S *= 1.28
        V = np.clip((V - .06) * 1.12, 0, 1) ** 1.32
    elif mode == "sea":
        S *= .97
        V = V ** .96
    elif mode == "food":
        S *= .84                               # a calm site can't carry stock-photo tomato red
        V = V ** .97
    hsv = cv2.merge([H, np.clip(S, 0, 1), np.clip(V, 0, 1)])
    out = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def run(root, out, only):
    os.makedirs(out, exist_ok=True)
    meta = {}
    mp = os.path.join(out, "_meta.json")
    if os.path.exists(mp):
        meta = json.load(open(mp))
    for key, spec in M.items():
        if only and key not in only:
            continue
        pat, mode = spec[0], spec[1]
        lens = len(spec) > 2 and spec[2]
        crop = spec[3] if len(spec) > 3 else None
        src = find(root, pat)
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")  # drone and phone files carry their rotation in EXIF
        if max(im.size) > 3400:  # work at a sane size: the top tier is 2400
            s = 3400 / max(im.size)
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        bgr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
        if lens:
            bgr = unbow(bgr)
        if crop:
            h, w = bgr.shape[:2]
            l, t, r, b = crop
            bgr = bgr[int(h * t):int(h * b), int(w * l):int(w * r)]
        bgr = grade(bgr, mode)
        rgb = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        w, h = rgb.size
        tiers = sorted({t for t in TIERS if t < w} | {min(w, TIERS[-1])})
        for t in tiers:
            r = rgb.resize((t, round(h * t / w)), Image.LANCZOS) if t < w else rgb
            r.save(os.path.join(out, f"{key}-{t}.webp"), "WEBP", quality=Q, method=5)
        avg = rgb.resize((1, 1), Image.BOX).getpixel((0, 0))
        meta[key] = {"w": w, "h": h, "tiers": tiers, "avg": "#%02x%02x%02x" % avg, "src": os.path.basename(src)}
        print(key, w, h, tiers, flush=True)
    json.dump(meta, open(mp, "w"), indent=0, sort_keys=True)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], set(sys.argv[3:]))
