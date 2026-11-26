"""Sumisura science reel engine v4 (V3 retention model, rebuilt).
Faster voice, karaoke word captions, hook slam + boom, flash/whoosh cuts, slow zoom,
count ticks, loop question. Adds: pain-point hook, cleaner premium typography.
python3 engine4.py <id|all> [still]
"""
import math, os, subprocess, sys, json
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
W, H, FPS, SR = 1080, 1920, 30, 24000
INK = (21, 20, 19); PAPER = (246, 244, 240)
SPEED = 1.12; GAP = 0.14
OUT = os.environ.get("OUT", os.path.join(REPO, "out")); os.makedirs(OUT, exist_ok=True)
FD = os.environ.get("FONTS", os.path.join(REPO, "assets", "fonts"))
def F(w, s): return ImageFont.truetype(f"{FD}/bvp-{w}.ttf", s)
_lp = os.path.join(REPO, "assets", "logo.png")
if not os.path.exists(_lp):
    try: subprocess.run(["rsvg-convert", "-w", "300", "-h", "300", os.path.join(REPO, "assets", "logo.svg"), "-o", _lp], check=True)
    except FileNotFoundError:  # no librsvg: pip install cairosvg
        import cairosvg; cairosvg.svg2png(url=os.path.join(REPO, "assets", "logo.svg"), write_to=_lp, output_width=300, output_height=300)
LOGO = Image.open(_lp).convert("RGBA")

def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def fade(t, a, d=.3): return ease((t - a) / d)
def A(c, a): return tuple(c[:3]) + (int(255 * max(0, min(1, a))),)
def light(c, k=.45): return tuple(int(v + (255 - v) * k) for v in c)

# ---------- background ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def glow(cx, cy, r):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    return np.exp(-d * d * 1.5)[..., None]
G1 = glow(540, 900, 700); G2 = glow(820, 1500, 520)
rng0 = np.random.default_rng(7)
GRAIN = [rng0.normal(0, 5, (H // 2, W // 2, 1)).astype(np.float32) for _ in range(4)]
def make_bg(acc, k):
    ink = np.array(INK, np.float32); a = np.array(acc, np.float32)
    arr = ink + (a - ink) * (G1 * k + G2 * k * .35)
    return arr
def finish_bg(arr, fi):
    g = np.repeat(np.repeat(GRAIN[fi % 4], 2, 0), 2, 1)
    return Image.fromarray(np.clip(arr + g, 0, 255).astype(np.uint8)).convert("RGBA")

def zoom(im, t, dur, k=.045, shake=0.0, punch=0.0):
    s = 1 + k * (t / max(dur, .1)) + punch
    w2, h2 = int(W / s), int(H / s)
    ox = (W - w2) / 2 + shake * 14 * math.sin(t * 83); oy = (H - h2) / 2 + shake * 14 * math.cos(t * 71)
    ox = max(0, min(W - w2, ox)); oy = max(0, min(H - h2, oy))
    return im.crop((int(ox), int(oy), int(ox) + w2, int(oy) + h2)).resize((W, H), Image.BILINEAR)

# ---------- text helpers ----------
def fit(font, s, maxw=920):
    while font.getlength(s) > maxw and font.size > 36: font = font.font_variant(size=font.size - 4)
    return font
def T(d, xy, s, font, a=1., col=PAPER, anchor="ma"):
    if a > 0.01: d.text(xy, s, font=font, fill=A(col, a), anchor=anchor)
def spaced(d, xy, s, font, a, col, track=6):
    w = sum(font.getlength(ch) + track for ch in s) - track; x = xy[0] - w / 2
    for ch in s:
        T(d, (x, xy[1]), ch, font, a, col, "la"); x += font.getlength(ch) + track

def label(d, t, s, acc):  # small tracked label top
    spaced(d, (540, 236), s.upper(), F(600, 28), fade(t, 0, .25) * .9, light(acc, .5), 7)
    a = fade(t, .1, .4); d.line((540 - 40 * a, 286, 540 + 40 * a, 286), fill=A(light(acc, .5), .6 * a), width=2)

def source(d, t, s):
    if s: T(d, (540, 1478), s, F(400, 26), .55 * fade(t, .5), PAPER)

# ---------- karaoke captions ----------
def captions(d, words, t, acc):
    """words: list of (word, t0, t1) for the current scene; show chunk of <=4 words."""
    if not words: return
    idx = 0
    for i, (w, a0, a1) in enumerate(words):
        if t >= a0: idx = i
    c0 = (idx // 4) * 4; chunk = words[c0:c0 + 4]
    f = F(700, 62)
    sz = [f.getlength(w) for w, _, _ in chunk]; gap = 18
    tot = sum(sz) + gap * (len(chunk) - 1)
    if tot > 940: f = F(700, 52); sz = [f.getlength(w) for w, _, _ in chunk]; tot = sum(sz) + gap * (len(chunk) - 1)
    x = 540 - tot / 2; y = 1250
    for (w, a0, a1), s in zip(chunk, sz):
        on = t >= a0; cur = a0 <= t < a1 + .05
        col = (255, 214, 102) if cur else PAPER
        a = 1. if on else .35
        if cur:
            pop = 1 - ease((t - a0) / .12)
            d.rounded_rectangle((x - 10, y - 6 - 4 * pop, x + s + 10, y + 74 + 4 * pop), radius=12, fill=A(INK, .55))
        T(d, (x, y), w, f, a, col, "la"); x += s + gap

# ---------- icons ----------
def ic_ice(d, cx, cy, r, a, t, col):
    for k in range(6):
        ang = k * math.pi / 3 + t * .15
        x2, y2 = cx + r * math.cos(ang), cy + r * math.sin(ang)
        d.line((cx, cy, x2, y2), fill=A(col, a), width=6)
        for f in (.45, .72):
            bx, by = cx + r * f * math.cos(ang), cy + r * f * math.sin(ang)
            for s in (-1, 1):
                b2 = ang + s * .6
                d.line((bx, by, bx + r * .22 * math.cos(b2), by + r * .22 * math.sin(b2)), fill=A(col, a), width=5)
def ic_pulse(d, cx, cy, r, a, t, col, amp=1.0):
    pts = []
    for i in range(121):
        x = cx - r * 2 + i * r * 4 / 120; ph = (i / 120 * 3 - t * 1.4) % 1
        y = cy
        if .40 < ph < .44: y -= r * .25 * amp
        elif .44 < ph < .48: y += r * .9 * amp
        elif .48 < ph < .53: y -= r * 1.1 * amp
        elif .53 < ph < .57: y += r * .3 * amp
        pts.append((x, y))
    d.line(pts, fill=A(col, a), width=6, joint="curve")
def ic_scale(d, cx, cy, r, a, t, col):
    d.rounded_rectangle((cx - r, cy - r * .8, cx + r, cy + r * .8), radius=r * .25, outline=A(col, a), width=6)
    d.arc((cx - r * .55, cy - r * .62, cx + r * .55, cy + r * .3), 200, 340, fill=A(col, a), width=6)
    ang = math.radians(270 + 25 * math.sin(t * 3)); d.line((cx, cy - r * .1, cx + r * .4 * math.cos(ang), cy - r * .1 + r * .4 * math.sin(ang)), fill=A(col, a), width=5)
def ic_grip(d, cx, cy, r, a, t, col):
    sq = .5 + .5 * math.sin(t * 4)
    d.rounded_rectangle((cx - r * .9, cy - r * .35, cx + r * .9, cy + r * .35), radius=r * .3, outline=A(col, a), width=6)
    for k in range(4):
        x = cx - r * .6 + k * r * .4
        d.rounded_rectangle((x - r * .14, cy - r * (.7 + .15 * sq), x + r * .14, cy + r * .1), radius=r * .12, outline=A(col, a), width=5)
def ic_gauge(d, cx, cy, r, a, t, col, v=.7):
    d.arc((cx - r, cy - r, cx + r, cy + r), 150, 390, fill=A(col, .3 * a), width=14)
    d.arc((cx - r, cy - r, cx + r, cy + r), 150, 150 + 240 * v * ease(t / 1.2), fill=A(col, a), width=14)
    ang = math.radians(150 + 240 * v * ease(t / 1.2)); d.line((cx, cy, cx + r * .75 * math.cos(ang), cy + r * .75 * math.sin(ang)), fill=A(PAPER, a), width=6)
def ic_muscle(d, cx, cy, r, a, t, col, keep=1.0):
    # fibre bundle that thins out
    for k in range(9):
        y = cy - r * .8 + k * r * .2
        alive = k / 9 < keep
        d.rounded_rectangle((cx - r * 1.3, y, cx + r * 1.3, y + r * .12), radius=r * .06, fill=A(col, a * (1 if alive else .18)))
def ic_lungs(d, cx, cy, r, a, t, col, gasp=1.0):
    br = 1 + .12 * (gasp * abs(math.sin(t * 9)) + (1 - gasp) * (.5 + .5 * math.sin(t * 2)))
    d.line((cx, cy - r * 1.05, cx, cy - r * .35), fill=A(col, a), width=7)
    for s in (-1, 1):
        d.line((cx, cy - r * .35, cx + s * r * .35, cy - r * .1), fill=A(col, a), width=6)
        x0 = cx + s * r * .18; x1 = cx + s * r * .18 + s * r * .8 * br
        d.rounded_rectangle((min(x0, x1), cy - r * .55 * br, max(x0, x1), cy + r * .85 * br), radius=int(r * .38), outline=A(col, a), width=6)
def ic_heat(d, cx, cy, r, a, t, col):
    # three rising heat waves
    for k in (-1, 0, 1):
        pts = []
        for i in range(41):
            f = i / 40; y = cy + r - f * 2 * r
            x = cx + k * r * .62 + r * .16 * math.sin(f * 2.4 * math.pi - t * 3 + k)
            pts.append((x, y))
        d.line(pts, fill=A(col, a * (.55 + .45 * abs(math.sin(t * 1.5 + k)))), width=7, joint="curve")
def ic_runner(d, cx, cy, r, a, t, col):
    # stick runner, legs and arms swinging
    sw = math.sin(t * 9); c = A(col, a); w = 8
    hip = (cx - r * .05, cy + r * .1); sh = (cx + r * .18, cy - r * .5)
    d.ellipse((sh[0] + r * .02, sh[1] - r * .42, sh[0] + r * .34, sh[1] - r * .1), outline=c, width=w)
    d.line((hip, sh), fill=c, width=w)
    for s_ in (1, -1):
        g = s_ * sw
        kn = (hip[0] + r * .42 * g, hip[1] + r * .42); ft = (kn[0] - r * .28 + r * .2 * g, kn[1] + r * .46 - r * .2 * max(0, -g))
        d.line((hip, kn, ft), fill=c, width=w, joint="curve")
        el = (sh[0] - r * .3 * g, sh[1] + r * .3); hd = (el[0] + r * .3, el[1] + r * .12 - r * .25 * g)
        d.line((sh, el, hd), fill=c, width=w - 2, joint="curve")
    for k in range(3):
        y = cy - r * .35 + k * r * .3; x = cx - r * 1.05 - (t * 260 + k * 40) % (r * .5)
        d.line((x, y, x + r * .32, y), fill=A(col, a * .45), width=5)
ICONS = dict(ice=ic_ice, pulse=ic_pulse, scale=ic_scale, grip=ic_grip, gauge=ic_gauge, muscle=ic_muscle, lungs=ic_lungs, heat=ic_heat, runner=ic_runner)
def icon(d, spec, t, acc, a):
    if not spec: return
    name, cx, cy, r = spec[:4]; kw = dict(spec[4]) if len(spec) > 4 else {}
    col = kw.pop("col", light(acc, .35)); ICONS[name](d, cx, cy, r, a, t, col, **kw)

def particles(d, t, a, n=40, seed=3, fall=False, col=PAPER):
    rng = np.random.default_rng(seed)
    for x, y, s, z in zip(rng.uniform(0, W, n), rng.uniform(0, H, n), rng.uniform(20, 70, n), rng.uniform(2, 5, n)):
        yy_ = (y + t * s) % H if fall else (y - t * s) % H
        xx_ = x + (8 * math.sin(t * 1.5 + y) if fall else 0)
        d.ellipse((xx_ - z, yy_ - z, xx_ + z, yy_ + z), fill=A(col, .28 * a))

def frost(im, a):
    if a <= 0: return
    ov = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(ov)
    for r_, al in ((0, .0),):
        pass
    edge = np.clip((np.minimum(np.minimum(xx, W - xx), np.minimum(yy, H - yy)) / 220.0), 0, 1)
    al = ((1 - edge) ** 2 * 120 * a).astype(np.uint8)[..., 0] if edge.ndim == 3 else ((1 - edge) ** 2 * 120 * a).astype(np.uint8)
    rgba = np.dstack([np.full((H, W), 200, np.uint8), np.full((H, W), 228, np.uint8), np.full((H, W), 255, np.uint8), al])
    im.alpha_composite(Image.fromarray(rgba, "RGBA"))


# ---------- footage clips (own footage or Higgsfield shots) ----------
class Clip:
    """Streams a video file as 1080x1920 RGB frames: cover-crop, HDR->SDR tonemap, loops if too short."""
    def __init__(self, path, start=0.0):
        self.path = path if os.path.isabs(path) else os.path.join(REPO, path); self.start = start; self.p = None
        trc = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                              "-of", "csv=p=0", self.path], capture_output=True, text=True).stdout.strip()
        hdr = trc in ("smpte2084", "arib-std-b67")
        tm = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=rgb24,") if hdr else ""
        self.vf = tm + f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=rgb24"
    def _open(self):
        if self.p: self.p.kill()
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(self.start), "-i", self.path, "-vf", self.vf,
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    def frame(self):
        if self.p is None: self._open()
        b = self.p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: self._open(); b = self.p.stdout.read(W * H * 3)
        return Image.frombytes("RGB", (W, H), b)

_SHADE = None
def shade():
    global _SHADE
    if _SHADE is None:
        g = np.zeros((H, W), np.float32)
        top = np.linspace(.62, 0, 700); g[:700] = np.maximum(g[:700], top[:, None])
        bot = np.linspace(0, .72, 900); g[H - 900:] = np.maximum(g[H - 900:], bot[:, None])
        a = (np.clip(g + .12, 0, 1) * 255).astype(np.uint8)
        _SHADE = Image.fromarray(np.dstack([np.full((H, W), c, np.uint8) for c in INK] + [a]), "RGBA")
    return _SHADE

# ---------- scene drawing ----------
GOLD = (255, 214, 102)
def draw_scene(sc, t, dur, acc, fi, cold):
    typ = sc["type"]
    if typ == "clip":
        im = sc["_clip"].frame().convert("RGBA"); im.alpha_composite(shade()); d = ImageDraw.Draw(im)
        if sc.get("label"): label(d, t, sc["label"], acc)
        for i, s_ in enumerate(sc.get("head", [])):
            bold = i == 0 or s_.startswith("*"); s_ = s_.lstrip("*")
            f = fit(F(800 if i == 0 else 400, 96 if i == 0 else 72), s_)
            a = ease(t / .18) if i == 0 else fade(t, .35, .2)
            T(d, (540, 330 + i * 120), s_, f, a, GOLD if s_ in sc.get("gold", []) else PAPER)
        source(d, t, sc.get("src"))
        if sc.get("_words") is not None: captions(d, sc["_words"], t, acc)
        return im
    k = (.55 + .2 * ease(t / 1.5)) if typ == "hook" else .38
    im = finish_bg(sc["_bg"] if k == .38 else make_bg(acc, k), fi)
    d = ImageDraw.Draw(im)
    if cold: particles(d, t, fade(t, 0, .5), n=55, fall=True, col=(220, 236, 255))
    elif typ in ("hook", "end"): particles(d, t, fade(t, 0, .6))
    if sc.get("label"): label(d, t, sc["label"], acc)
    if typ == "hook":
        slam = ease(t / .18)
        l = sc["head"]
        f1 = fit(F(800, 104), l[0]); s = 1 + .25 * (1 - slam)
        f1s = f1.font_variant(size=int(f1.size * s))
        T(d, (540, 360), l[0], f1s, slam)
        if len(l) > 1:
            f2 = fit(F(300, 86), l[1]); T(d, (540, 500), l[1], f2, fade(t, .45, .2), GOLD)
        icon(d, sc.get("icon"), t, acc, fade(t, .2, .4))
    elif typ == "text":
        for i, s in enumerate(sc["head"]):
            bold = i == 0 or s.startswith("*"); s = s.lstrip("*")
            f = fit(F(700 if bold else 300, 84), s)
            T(d, (540, 330 + i * 112), s, f, fade(t, i * .3, .22), GOLD if s in sc.get("gold", []) else PAPER)
        icon(d, sc.get("icon"), t, acc, fade(t, .2, .4))
    elif typ == "stat":
        a = fade(t, 0, .2)
        T(d, (540, 330), sc["top"], fit(F(500, 54), sc["top"]), a)
        v = sc["count"] * ease((t - .15) / 1.0)
        val = sc["fmt"].format(v)
        T(d, (540, 470), val, F(800, 250), fade(t, .1, .15), GOLD)
        T(d, (540, 790), sc["sub"], fit(F(400, 50), sc["sub"]), fade(t, .6, .3))
        if sc.get("sub2"): T(d, (540, 860), sc["sub2"], fit(F(300, 44), sc["sub2"]), fade(t, .9, .3), light(acc, .5))
        icon(d, sc.get("icon"), t, acc, fade(t, .3, .4))
    elif typ == "compare":
        T(d, (540, 300), sc["top"], fit(F(700, 64), sc["top"]), fade(t, 0, .2))
        mx = max(v for _, v in sc["bars"])
        for i, (lab, v) in enumerate(sc["bars"]):
            y = 560 + i * 230; g = ease((t - .3 - i * .35) / .7)
            T(d, (150, y - 66), lab, F(500, 40), fade(t, .2 + i * .35), PAPER, "la")
            d.rounded_rectangle((150, y, 930, y + 70), radius=35, fill=A(PAPER, .08))
            wv = 780 * v / mx * g
            if wv > 70: d.rounded_rectangle((150, y, 150 + wv, y + 70), radius=35, fill=A(GOLD if i == len(sc["bars"]) - 1 else light(acc, .3), 1))
            T(d, (930, y - 66), sc["vals"][i], F(700, 44), g, GOLD if i == len(sc["bars"]) - 1 else PAPER, "ra")
    elif typ == "dots":
        T(d, (540, 300), sc["top"], fit(F(700, 64), sc["top"]), fade(t, 0, .2))
        n = sc["n"]; cols = min(n, 5)
        for i in range(n):
            r_, c_ = divmod(i, cols); x = 540 + (c_ - (cols - 1) / 2) * 170; y = 560 + r_ * 170
            g = ease((t - .25 - i * .22) / .25)
            d.ellipse((x - 55, y - 55, x + 55, y + 55), outline=A(PAPER, .35), width=4)
            if g > 0: rr = 55 * g; d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=A(light(acc, .3), 1))
        T(d, (540, 560 + ((n - 1) // cols) * 170 + 140), sc["sub"], fit(F(400, 50), sc["sub"]), fade(t, .3 + n * .22, .3))
        icon(d, sc.get("icon"), t, acc, fade(t, .2, .4))
    elif typ == "breath":
        ph = sc["phase"]; g = ease(t / max(dur - .2, .5))
        r = 110 + 150 * (g if ph == "in" else 1 - g)
        cx, cy = 540, 660
        for k in range(3):
            rr = r + k * 26; d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=A(light(acc, .4), .5 - k * .15), width=4)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(acc, .55))
        T(d, (cx, cy - 70), sc["big"], F(800, 120), fade(t, 0, .15))
        T(d, (cx, cy + 70), sc["small"], F(400, 44), fade(t, .1, .2))
        T(d, (540, 300), sc["top"], fit(F(700, 66), sc["top"]), fade(t, 0, .2))
        # heart-rate trace: rising on inhale, falling on exhale
        bpm_vis = (1.2 + 1.4 * g) if ph == "in" else (2.6 - 1.4 * g)
        ic_pulse(d, 540, 1080, 95, fade(t, .1, .3), t * bpm_vis, GOLD if ph == "in" else light(acc, .5))
        T(d, (540, 1150), ("HEART RATE  ↑" if ph == "in" else "HEART RATE  ↓"), F(600, 34), fade(t, .3, .3), GOLD)
    elif typ == "end":
        q = sc["q"]; words = q.split(); mid = (len(words) + 1) // 2
        T(d, (540, 520), " ".join(words[:mid]), fit(F(700, 88), " ".join(words[:mid])), fade(t, 0, .2))
        T(d, (540, 640), " ".join(words[mid:]), fit(F(700, 88), " ".join(words[mid:])), fade(t, .2, .2), GOLD)
        lg = LOGO.resize((150, 150)); a = fade(t, .5, .4)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(lg, (465, 960))
    source(d, t, sc.get("src"))
    if sc.get("_words") is not None: captions(d, sc["_words"], t, acc)
    if cold and typ in ("hook",) or sc.get("frost"): frost(im, .8 if typ == "hook" else .45)
    return im

# ---------- audio ----------
def tone(f0, f1, dur, vol, decay=6.):
    n = int(SR * dur); tt = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(np.linspace(f0, f1, n)) / SR
    return vol * np.sin(ph) * np.exp(-tt * decay)
def noise(dur, vol, lp=.08, env="swell"):
    n = int(SR * dur); x = np.random.default_rng(int(dur * 1000)).normal(0, 1, n)
    y = np.zeros(n); acc_ = 0.
    for i in range(n): acc_ += lp * (x[i] - acc_); y[i] = acc_
    tt = np.linspace(0, 1, n)
    e = np.sin(np.pi * tt) ** 2 if env == "swell" else np.exp(-tt * 5)
    y = y / (np.abs(y).max() + 1e-9); return vol * y * e
BOOM = tone(90, 38, 1.2, .55, 3.5); BOOM[:6000] += noise(.25, .15, .3, "dec")
WHOOSH = noise(.35, .16, .12)
TICK = tone(2400, 2200, .03, .12, 120)
GASP = noise(.5, .22, .35)
def heartbeat(dur, bpm, vol=.25):
    n = int(SR * dur); y = np.zeros(n); per = 60 / bpm; t0 = 0.
    beat = tone(60, 45, .18, vol, 18); beat2 = tone(55, 42, .15, vol * .7, 20)
    while t0 < dur:
        for off, b in ((0, beat), (.22, beat2)):
            i = int((t0 + off) * SR); j = min(n, i + len(b))
            if i < n: y[i:j] += b[:j - i]
        t0 += per
    return y
def drone(dur, f, vol=.035):
    tt = np.arange(int(SR * dur)) / SR
    return vol * (np.sin(2 * np.pi * f * tt) + .5 * np.sin(2 * np.pi * f * 1.5 * tt + .3)) * (0.75 + .25 * np.sin(2 * np.pi * .2 * tt))

_k = None
def tts(text):
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        TD = os.environ.get("TTS_DIR", os.path.join(REPO, "tts"))
        _k = Kokoro(f"{TD}/kokoro-v1.0.onnx", f"{TD}/voices-v1.0.bin")
    s, sr = _k.create(text, voice="am_michael", speed=SPEED, lang="en-us")
    assert sr == SR
    # trim silence
    idx = np.where(np.abs(s) > .01)[0]
    if len(idx): s = s[max(0, idx[0] - 600): idx[-1] + 1200]
    return s

def word_times(text, dur, t0):
    ws = text.split(); wts = [len(w.strip(",.?!:;")) + 2.2 + (3 if w[-1] in ",.?!:;" else 0) for w in ws]
    tot = sum(wts); out = []; t = t0
    for w, k in zip(ws, wts):
        d_ = dur * k / tot; out.append((w, t, t + d_)); t += d_
    return out

def mix(buf, clip, at):
    i = int(at * SR); j = min(len(buf), i + len(clip))
    if 0 <= i < len(buf): buf[i:j] += clip[:j - i]

# ---------- build ----------
def build(spec, still=False):
    acc = spec["acc"]; cold = spec.get("cold", False)
    scenes = spec["scenes"]; timeline = []; t = 0.
    for sc in scenes:
        aud = tts(sc["vo"]); d_ = len(aud) / SR
        dur = d_ + GAP + sc.get("hold", 0)
        if sc["type"] == "end": dur = max(dur, 2.6)
        sc["_bg"] = make_bg(acc, .38)
        if sc["type"] == "clip": sc["_clip"] = Clip(sc["file"], sc.get("start", 0.0))
        sc["_words"] = word_times(sc["vo"], d_, 0.0) if sc.get("caps", True) else None
        timeline.append((t, dur, sc, aud)); t += dur
    total = t
    audio = np.zeros(int(SR * (total + .5)))
    audio += np.resize(drone(total + .5, 55 if cold else 65), len(audio))
    if cold: mix(audio, heartbeat(total, 96, .16), 0)
    for i, (t0, dur, sc, aud) in enumerate(timeline):
        mix(audio, aud * .95, t0 + .03)
        if i == 0: mix(audio, BOOM, 0); mix(audio, GASP if cold else WHOOSH * .5, .05)
        else: mix(audio, WHOOSH, t0 - .12)
        if sc["type"] == "stat":
            for k in range(10): mix(audio, TICK, t0 + .15 + k * .1)
        if sc["type"] == "dots":
            for k in range(sc["n"]): mix(audio, TICK * 1.4, t0 + .25 + k * .22)
        if sc.get("gasp"): mix(audio, GASP, t0 + .1); mix(audio, GASP * .8, t0 + .7)
    audio = np.tanh(audio * 1.3) * .89
    wav = f"{OUT}/{spec['id']}.wav"; sf.write(wav, audio.astype(np.float32), SR)
    if still:
        for i, (t0, dur, sc, aud) in enumerate(timeline):
            im = draw_scene(sc, min(dur * .7, 1.6), dur, acc, 0, cold); im.convert("RGB").save(f"{OUT}/{spec['id']}_s{i}.jpg", quality=80)
        return
    mp4 = f"{OUT}/{spec['id']}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
    n = int(total * FPS)
    for fi in range(n):
        tg = fi / FPS
        for t0, dur, sc, aud in timeline:
            if t0 <= tg < t0 + dur: break
        lt = tg - t0
        im = draw_scene(sc, lt, dur, acc, fi, cold)
        punch = .06 * (1 - ease(lt / .2)) if lt < .2 else 0
        shake = (.9 if cold and sc["type"] == "hook" else 0) * (1 - ease(lt / 1.2)) + (.5 if sc.get("gasp") and lt < 1.2 else 0)
        im = zoom(im.convert("RGB"), lt, dur, punch=punch, shake=shake)
        if lt < .08 and tg > .1:  # flash cut
            im = Image.blend(im, Image.new("RGB", (W, H), PAPER), .55 * (1 - lt / .08))
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    print(spec["id"], round(total, 1), "s")

if __name__ == "__main__":
    sys.path.insert(0, HERE); import importlib; REELS = importlib.import_module(os.environ.get("SPECS", "specs5")).REELS
    ids = sys.argv[1].split(",") if sys.argv[1] != "all" else [r["id"] for r in REELS]
    for r in REELS:
        if r["id"] in ids: build(r, still=len(sys.argv) > 2)
