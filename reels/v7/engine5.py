"""Sumisura reel engine v5 = engine4 + sauna/running visuals + retention devices.

Visuals: cedar-plank sauna background with drifting steam, heat shimmer and condensation drops; an animated runner
(real gait cycle, motion ghosts, streaming ground) and a seated sauna figure.
Retention devices (each one is a scene type or overlay):
  hook2  pattern interrupt inside the hook: runner -> flash -> sauna, switched on a spoken word (orienting response)
  guess  viewer predicts the number before the reveal (curiosity gap + generation effect)
  race   the stat as a race: control runner stops at 100%, sauna runner keeps going to +N% (open loop, payoff late)
  timer  the dose as a filling sauna timer            clock  finish clock that ticks down to the new time
  story bar on top: one segment per scene (goal-gradient / completion drive); end scene loops back to the hook look.
python3 engine5.py <id|all> [still]      (SPECS=specs6 by default)
"""
import math, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine4 as e
from engine4 import (W, H, FPS, SR, INK, PAPER, GOLD, OUT, GAP, F, T, fit, fade, ease, A, light, label, source, captions,
                     LOGO, tts, word_times, mix, tone, noise, drone, zoom, Clip, BOOM, WHOOSH, TICK)

yy, xx = e.yy, e.xx
STEAMC = np.array((250, 240, 226), np.float32)
SKIN = (244, 226, 200)

# ---------- sauna background ----------
def _planks():
    r = np.random.default_rng(11); base = np.zeros((H, W), np.float32); y = 0
    while y < H:
        h = int(r.integers(88, 108)); base[y:y + h] = r.uniform(.80, 1.06)
        base[y:y + 3] *= .30; base[y + 3:y + 5] *= 1.14; y += h
    g = r.normal(0, 1, (H // 3, 16)).astype(np.float32)
    base *= 1 + .05 * np.asarray(Image.fromarray(g).resize((W, H), Image.BICUBIC))
    lamp = np.exp(-(((xx - 540) / 880) ** 2 + ((yy - 760) / 1150) ** 2) * 1.7)
    arr = (base * lamp)[..., None] * np.array((176, 104, 54), np.float32) * .62 + np.array(INK, np.float32) * .6
    top = np.clip(1 - yy / 760, 0, 1)[..., None]            # darker behind the headline
    return arr * (1 - .42 * top)
PLANKS = _planks()
def _tex(seed):
    n = np.random.default_rng(seed).random((15, 9)).astype(np.float32)
    return Image.fromarray(np.tile(n, (2, 2))).resize((288, 480), Image.BICUBIC)
TEX = [_tex(1), _tex(2), _tex(5)]
VG = .22 + .78 * (yy / H) ** 1.25
XI = np.arange(W)[None, :].repeat(H, 0)
YI = np.arange(H)[:, None]
GR = [np.random.default_rng(i).normal(0, 4, (H // 2, W // 2)).astype(np.float32) for i in range(4)]

def sauna_bg(t, fi, k=1.0, bright=1.0):
    """k = amount of steam (1 = calm, 3 = burst)."""
    arr = PLANKS * bright
    for tex, sp, dr, th in ((TEX[0], 40, 6, .50), (TEX[1], 66, -9, .54), (TEX[2], 100, 12, .58)):
        oy = (t * sp) % 240; ox = (t * dr) % 144
        m = np.asarray(tex.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + 144, oy + 240)))
        al = np.clip((m - th + .12) * 1.7, 0, 1) ** 1.5 * VG * min(.34 * k, .7)
        arr = arr + (STEAMC - arr) * al[..., None]
    arr += np.repeat(np.repeat(GR[fi % 4], 2, 0), 2, 1)[..., None]
    u8 = np.clip(arr, 0, 255).astype(np.uint8)
    dy = (2.6 * np.sin(xx / 61 + yy / 97 + t * 3.3) * (.25 + .75 * yy / H)).astype(np.int32)   # heat shimmer
    return Image.fromarray(u8[np.clip(YI + dy, 0, H - 1), XI])

_dr = np.random.default_rng(4)
DROPS = [(float(x), float(_dr.uniform(0, H)), float(_dr.uniform(25, 70)), float(_dr.uniform(6, 10)))
         for x in list(_dr.uniform(20, 120, 4)) + list(_dr.uniform(960, 1060, 4))]
def drops(d, t):
    for x, y0, sp, r in DROPS:
        y = (y0 + t * sp) % (H + 200) - 100
        d.line((x, y - 70, x, y), fill=A(PAPER, .05), width=3)
        d.ellipse((x - r, y - r, x + r, y + r * 1.3), fill=A(PAPER, .15)); d.ellipse((x - r * .4, y - r * .5, x, y - r * .1), fill=A(PAPER, .38))

# ---------- figures ----------
def _limb(d, pts, w, c):
    d.line(pts, fill=c, width=int(w), joint="curve")
    for x, y in pts: d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=c)
def _pol(p, ang, ln): return (p[0] + math.sin(ang) * ln, p[1] + math.cos(ang) * ln)

def _run_pose(cx, cy, s, ph):
    hip = (cx, cy - abs(math.sin(ph)) * s * .07); lean = .17
    neck = (hip[0] + math.sin(lean) * s * .92, hip[1] - math.cos(lean) * s * .92)
    head = (neck[0] + s * .07, neck[1] - s * .27); sh = (neck[0] - s * .03, neck[1] + s * .08)
    legs, arms = [], []
    for off in (math.pi, 0):                       # far side first
        p = ph + off
        th = .12 + .66 * math.sin(p); fx = .18 + 1.35 * max(0., math.cos(p + .35)) ** 1.4
        kn = _pol(hip, th, s * .5); an = _pol(kn, th - fx, s * .5)
        legs.append([hip, kn, an, (an[0] + s * .17 * math.cos(min(.9, max(-.4, fx - th)) * .6), an[1] + s * .04)])
        ua = -.78 * math.sin(p); el = _pol(sh, ua, s * .34)
        arms.append([sh, el, _pol(el, ua + 1.45, s * .3)])
    return hip, neck, head, legs, arms

def runner(d, cx, cy, s, t, col, a=1., ghosts=True, cad=2.9):
    """cy = hip height; feet land about s below it. Faces right."""
    ph = t * 2 * math.pi * cad / 2
    if ghosts:
        for k, ga in ((3, .07), (2, .13), (1, .22)):
            hip, neck, head, legs, arms = _run_pose(cx - k * s * .42, cy, s, ph - k * .5)
            c = A(col, ga * a)
            for L in legs: _limb(d, L, s * .13, c)
            _limb(d, [hip, neck], s * .19, c); d.ellipse((head[0] - s * .15, head[1] - s * .15, head[0] + s * .15, head[1] + s * .15), fill=c)
    hip, neck, head, legs, arms = _run_pose(cx, cy, s, ph)
    far = A(tuple(int(v * .62) for v in col), a); c = A(col, a)
    _limb(d, legs[0], s * .13, far); _limb(d, arms[0], s * .10, far)
    _limb(d, [hip, neck], s * .19, c); d.ellipse((head[0] - s * .155, head[1] - s * .155, head[0] + s * .155, head[1] + s * .155), fill=c)
    _limb(d, legs[1], s * .13, c); _limb(d, arms[1], s * .10, c)

def ground(d, y, t, a=1., speed=820, x0=0, x1=W):
    d.line((x0, y, x1, y), fill=A(PAPER, .22 * a), width=3)
    for k in range(9):
        x = x1 - ((t * speed + k * 170) % (x1 - x0 + 160)) + 80
        if x0 < x < x1 - 90: d.line((x, y + 16, x + 90, y + 16), fill=A(PAPER, .30 * a), width=5)
    for k in range(4):                              # speed streaks at body height
        x = x1 - ((t * speed * 1.5 + k * 310) % (x1 - x0 + 300)) + 100; yk = y - 120 - k * 70
        if x0 < x < x1 - 140: d.line((x, yk, x + 140, yk), fill=A(PAPER, .13 * a), width=4)

def sitter(d, cx, cy, s, t, col, a=1.):
    """Seated in the sauna on a bench, breathing, sweating. cy = seat height."""
    c = A(col, a); far = A(tuple(int(v * .62) for v in col), a); wood = A((120, 74, 40), a); wood2 = A((86, 52, 30), a)
    d.rounded_rectangle((cx - s * 1.25, cy + s * .10, cx + s * 1.25, cy + s * .24), radius=8, fill=wood)      # bench
    d.rounded_rectangle((cx - s * 1.05, cy + s * .24, cx - s * .93, cy + s * .72), radius=6, fill=wood2)
    d.rounded_rectangle((cx + s * .93, cy + s * .24, cx + s * 1.05, cy + s * .72), radius=6, fill=wood2)
    d.rounded_rectangle((cx - s * 1.35, cy + s * .66, cx + s * 1.35, cy + s * .76), radius=8, fill=wood)      # floor step
    br = 1 + .018 * math.sin(t * 2.4)
    hip = (cx - s * .22, cy); lean = .26
    neck = (hip[0] + math.sin(lean) * s * .9, hip[1] - math.cos(lean) * s * .9 * br)
    head = (neck[0] + s * .10, neck[1] - s * .24); sh = (neck[0] - s * .02, neck[1] + s * .09)
    for o, cc in ((-s * .07, far), (0, c)):
        kn = (hip[0] + s * .52 + o, hip[1] - s * .02); an = (kn[0] + s * .04, cy + s * .56)
        _limb(d, [(hip[0] + o, hip[1]), kn, an, (an[0] + s * .17, an[1] + s * .04)], s * .13, cc)
        el = (sh[0] + s * .16 + o, sh[1] + s * .34); _limb(d, [sh, el, (kn[0] - s * .06, kn[1] - s * .09)], s * .10, cc)
    _limb(d, [hip, neck], s * .19, c)
    d.ellipse((head[0] - s * .155, head[1] - s * .155, head[0] + s * .155, head[1] + s * .155), fill=c)
    for k in range(3):                              # sweat
        p = (t * .9 + k * .37) % 1; x = head[0] + s * (.2 + .12 * k); y = head[1] + p * s * .9
        r = s * .028; d.ellipse((x - r, y - r * 1.4, x + r, y + r * 1.4), fill=A((190, 226, 255), a * (1 - p) * .9))

def figure(d, fig, t, acc, a=1.):
    if not fig: return
    name, cx, cy, s = fig[:4]
    if name == "runner": ground(d, cy + s * 1.06, t, a); runner(d, cx, cy, s, t, SKIN, a)
    elif name == "sitter": sitter(d, cx, cy, s, t, SKIN, a)

# ---------- new scenes ----------
def sc_hook2(d, sc, t, dur, acc):
    sw = sc["_sw"]; l = sc["head"]; slam = ease(t / .18)
    f1 = fit(F(800, 104), l[0]); T(d, (540, 360), l[0], f1.font_variant(size=int(f1.size * (1 + .25 * (1 - slam)))), slam)
    if t < sw:
        ground(d, 1066, t); runner(d, 520, 890, 168, t, SKIN)
    else:
        pop = 1 + .2 * (1 - ease((t - sw) / .16)); f2 = fit(F(600, 86), l[1])
        T(d, (540, 492), l[1], f2.font_variant(size=int(f2.size * pop)), 1, GOLD)
        sitter(d, 540, 900, 175, t - sw, SKIN)

def sc_guess(d, sc, t, dur, acc):
    for i, s in enumerate(sc["head"]):
        T(d, (540, 318 + i * 96), s, fit(F(700 if i == 0 else 400, 70), s), fade(t, i * .25, .2), PAPER if i == 0 else light(acc, .6))
    for i, o in enumerate(sc["opts"]):
        t0 = .55 + i * .3; a = ease((t - t0) / .14); y = 610 + i * 152; g = 10 * (1 - a)
        if a <= 0: continue
        d.rounded_rectangle((290 - g, y - g, 790 + g, y + 118 + g), radius=59, fill=A(INK, .5 * a), outline=A(PAPER, .75 * a), width=4)
        T(d, (350, y + 34), "ABC"[i], F(600, 40), a, light(acc, .55), "la"); T(d, (560, y + 16), o, F(800, 70), a)
    p = 1 - max(0, min(1, (t - .6) / max(.4, dur - .75)))
    d.rounded_rectangle((290, 1096, 790, 1106), radius=5, fill=A(PAPER, .15))
    if p > .01: d.rounded_rectangle((290, 1096, 290 + 500 * p, 1106), radius=5, fill=A(GOLD, .95))

def sc_race(d, sc, t, dur, acc):
    T(d, (540, 296), sc["top"], fit(F(700, 62), sc["top"]), fade(t, 0, .2))
    x0 = 130; L = 620; x100 = x0 + L; n = sc["count"]; xe = x0 + L * (1 + n / 100)
    T1, T2 = sc["_T1"], sc["_T2"]
    p1 = max(0, min(1, (t - .2) / (T1 - .2))); k = ease((t - T1) / (T2 - T1)) if t > T1 else 0
    for y in range(440, 880, 24): d.line((x100, y, x100, y + 11), fill=A(PAPER, .32), width=3)
    for i, (lab, p, col, gy) in enumerate(((sc["lanes"][0], p1, PAPER, 618), (sc["lanes"][1], p1 + n / 100 * k, GOLD, 862))):
        stop = i == 0 and t >= T1; xr = x0 + L * p
        T(d, (x0, gy - 196), lab, F(600, 38), fade(t, .05 + i * .12, .2), col, "la")
        d.rounded_rectangle((x0, gy + 10, xe, gy + 24), radius=7, fill=A(PAPER, .10))
        d.rounded_rectangle((x0, gy + 10, max(x0 + 14, xr), gy + 24), radius=7, fill=A(col, .5 if stop else 1))
        runner(d, xr, gy - 62, 58, T1 if stop else t, SKIN if i == 0 else GOLD, .42 if stop else 1, ghosts=not stop)
        if stop: T(d, (xr + 44, gy - 96), sc.get("stop", "exhausted"), F(500, 30), fade(t, T1, .2) * .8, PAPER, "la")
    if t >= T1:
        pop = 1 + .18 * (1 - ease((t - T2) / .18)) if t >= T2 else 1
        T(d, (540, 905), sc["fmt"].format(n * k), F(800, int(196 * pop)), fade(t, T1, .12), GOLD)
        T(d, (540, 1140), sc["sub"], fit(F(500, 46), sc["sub"]), fade(t, T1 + .3, .25))

def sc_timer(d, sc, t, dur, acc):
    for i, s in enumerate(sc["head"]):
        s2 = s.lstrip("*"); T(d, (540, 318 + i * 104), s2, fit(F(700 if i == 0 or s.startswith("*") else 300, 80), s2),
                              fade(t, i * .3, .22), GOLD if s2 in sc.get("gold", []) else PAPER)
    cx, cy, r = 540, 850, 176; k = ease((t - .3) / 1.25); m = sc.get("mins", 30)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(INK, .45), outline=A(PAPER, .2), width=16)
    if k > 0: d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * k, fill=A(GOLD, 1), width=16)
    for q in range(12):
        ang = q * math.pi / 6; d.line((cx + (r - 34) * math.sin(ang), cy - (r - 34) * math.cos(ang), cx + (r - 22) * math.sin(ang), cy - (r - 22) * math.cos(ang)), fill=A(PAPER, .35), width=3)
    T(d, (cx, cy - 92), f"{m * k:.0f}", F(800, 132), fade(t, .1, .15), GOLD if k > .98 else PAPER)
    T(d, (cx, cy + 58), sc.get("unit", "minutes"), F(500, 36), fade(t, .2, .2))

def sc_clock(d, sc, t, dur, acc):
    T(d, (540, 300), sc["top"], fit(F(500, 54), sc["top"]), fade(t, 0, .2))
    k = ease((t - .5) / 1.2); s = int(round(sc["start_s"] - sc["gain_s"] * k)); done = k > .98
    pop = 1 + .12 * (1 - ease((t - 1.7) / .18)) if t >= 1.7 else 1
    T(d, (540, 392), f"{s // 60}:{s % 60:02d}", F(800, int(222 * pop)), fade(t, .05, .15), GOLD if done else PAPER)
    T(d, (540, 668), sc["sub"], fit(F(600, 52), sc["sub"]), fade(t, 1.7, .2), GOLD)
    if sc.get("sub2"): T(d, (540, 744), sc["sub2"], fit(F(300, 42), sc["sub2"]), fade(t, 2.0, .3), light(acc, .6))
    gy = 1120; xf = 850; ground(d, gy, t)
    d.line((xf, gy - 250, xf, gy), fill=A(PAPER, .8), width=8)
    for r_ in range(3):
        for c_ in range(4):
            if (r_ + c_) % 2 == 0: d.rectangle((xf + 6 + c_ * 22, gy - 250 + r_ * 22, xf + 28 + c_ * 22, gy - 228 + r_ * 22), fill=A(PAPER, .85))
    runner(d, 200 + 610 * min(1, t / max(1.6, dur - .4)), gy - 78, 74, t, SKIN)

def sc_text(d, sc, t, dur, acc):
    for i, s in enumerate(sc["head"]):
        bold = i == 0 or s.startswith("*"); s = s.lstrip("*")
        T(d, (540, 330 + i * 112), s, fit(F(700 if bold else 300, 84), s), fade(t, i * .3, .22), GOLD if s in sc.get("gold", []) else PAPER)
    figure(d, sc.get("fig"), t, acc, fade(t, .1, .3))

def sc_end(im, d, sc, t, dur, acc):
    q = sc["q"]; words = q.split(); mid = (len(words) + 1) // 2
    T(d, (540, 430), " ".join(words[:mid]), fit(F(700, 88), " ".join(words[:mid])), fade(t, 0, .2))
    T(d, (540, 548), " ".join(words[mid:]), fit(F(700, 88), " ".join(words[mid:])), fade(t, .2, .2), GOLD)
    figure(d, sc.get("fig"), t, acc, fade(t, .1, .3))
    lg = LOGO.resize((150, 150)); a = fade(t, .5, .4); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
    im.paste(lg, (465, 1210), lg)

def _shade():                                       # lighter than engine4: footage stays visible, text stays readable
    g = np.full((H, W), .04, np.float32)
    g[:720] = np.maximum(g[:720], np.linspace(.56, .04, 720)[:, None]); g[H - 860:] = np.maximum(g[H - 860:], np.linspace(.04, .5, 860)[:, None])
    g[1180:1380] = np.maximum(g[1180:1380], .34)   # band behind the captions
    return Image.fromarray(np.dstack([np.full((H, W), c, np.uint8) for c in INK] + [(g * 255).astype(np.uint8)]), "RGBA")
SHADE = _shade()
NEW = dict(hook2=sc_hook2, guess=sc_guess, race=sc_race, timer=sc_timer, clock=sc_clock, text=sc_text)

def draw_scene(sc, t, dur, acc, fi, tg):
    typ = sc["type"]
    if typ == "clip":                               # footage with text on top, properly alpha-blended
        im = sc["_clip"].frame(); im.paste(SHADE, (0, 0), SHADE); d = ImageDraw.Draw(im, "RGBA")
        if sc.get("label"): label(d, t, sc["label"], acc)
        for i, s_ in enumerate(sc.get("head", [])):
            f = fit(F(800 if i == 0 else 600, 96 if i == 0 else 78), s_)
            if i == 0: slam = ease(t / .18); f = f.font_variant(size=int(f.size * (1 + .22 * (1 - slam)))); a = slam
            else: a = fade(t, sc.get("_sw2", .35), .15)
            T(d, (543, 335 + i * 124), s_, f, a * .75, INK)
            T(d, (540, 330 + i * 124), s_, f, a, GOLD if s_ in sc.get("gold", []) else PAPER)
        source(d, t, sc.get("src"))
        if sc.get("_words") is not None: captions(d, sc["_words"], t, acc)
        return im
    if typ not in NEW and typ != "end": return e.draw_scene(sc, t, dur, acc, fi, False)   # stat, compare, dots...
    k = 1.0; bright = 1.0
    if typ == "hook2":
        sw = sc["_sw"]; k = .7 if t < sw else 1.2 + 2.6 * math.exp(-(t - sw) * 1.5); bright = .9 if t < sw else 1.12
    elif typ == "timer": k = 1.3 + 1.6 * math.exp(-t * 1.4)
    elif typ == "end": k = 1.5
    im = sauna_bg(tg, fi, k, bright); d = ImageDraw.Draw(im, "RGBA"); drops(d, tg)
    if sc.get("label"): label(d, t, sc["label"], acc)
    if typ == "end": sc_end(im, d, sc, t, dur, acc)
    else: NEW[typ](d, sc, t, dur, acc)
    source(d, t, sc.get("src"))
    if sc.get("_words") is not None: captions(d, sc["_words"], t, acc)
    return im

def storybar(im, timeline, tg):
    d = ImageDraw.Draw(im, "RGBA"); n = len(timeline); x0, x1, gap = 90, 990, 10; w = (x1 - x0 - gap * (n - 1)) / n
    for i, (t0, dur, sc, _) in enumerate(timeline):
        xa = x0 + i * (w + gap); p = max(0, min(1, (tg - t0) / dur))
        d.rounded_rectangle((xa, 190, xa + w, 197), radius=3, fill=A(PAPER, .22))
        if p > 0: d.rounded_rectangle((xa, 190, xa + max(7, w * p), 197), radius=3, fill=A(PAPER if p >= 1 else GOLD, .92))

# ---------- audio ----------
STEP = tone(120, 55, .09, .2, 32); STEP[:700] += noise(.03, .05, .5, "dec")[:700]
HISS = noise(1.5, .26, .7, "dec") + np.resize(noise(.75, .10, .9, "dec"), int(SR * 1.5)) * .5
DING = tone(1175, 1175, .7, .10, 5) + tone(1760, 1760, .7, .05, 7)
def riser(dur):
    n = int(SR * dur); tt = np.linspace(0, 1, n)
    return .09 * tt ** 2 * np.sin(2 * np.pi * np.cumsum(np.linspace(180, 760, n)) / SR) + noise(dur, .07, .25) * tt
def steps(audio, a, b, vol=1.):
    t = a
    while t < b: mix(audio, STEP * vol, t); t += 1 / 2.9

# ---------- build ----------
def build(spec, still=False):
    acc = spec["acc"]; timeline = []; t = 0.
    for sc in spec["scenes"]:
        aud = tts(sc["vo"]); d_ = len(aud) / SR
        dur = d_ + GAP + sc.get("hold", 0)
        if sc["type"] == "end": dur = max(dur, 2.6)
        sc["_bg"] = e.make_bg(acc, .38)
        if sc["type"] == "clip":
            sc["_clip"] = Clip(sc["file"], sc.get("start", 0.0))
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(sc.get("start", 0.0)), "-t", str(dur), "-i", sc["_clip"].path,
                                "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
            sc["_amb"] = np.frombuffer(r.stdout, np.float32).astype(np.float64)      # the clip's own sound, kept low under the voice
        wt = word_times(sc["vo"], d_, 0.0); sc["_words"] = wt if sc.get("caps", True) else None
        if sc["type"] == "hook2": sc["_sw"] = wt[sc["switch"]][1]
        if sc["type"] == "race": sc["_T1"] = min(1.5, dur * .42); sc["_T2"] = min(dur - .55, sc["_T1"] + 1.15)
        timeline.append((t, dur, sc, aud)); t += dur
    total = t
    audio = np.zeros(int(SR * (total + .5))); audio += np.resize(drone(total + .5, 65), len(audio))
    for i, (t0, dur, sc, aud) in enumerate(timeline):
        typ = sc["type"]; mix(audio, aud * .95, t0 + .03)
        if i == 0: mix(audio, BOOM, 0); mix(audio, WHOOSH * .5, .05)
        else: mix(audio, WHOOSH, t0 - .12)
        if typ == "clip" and len(sc.get("_amb", [])):
            amb = sc["_amb"].copy(); n = min(len(amb), int(SR * .15)); amb[:n] *= np.linspace(0, 1, n); amb[-n:] *= np.linspace(1, 0, n)
            mix(audio, amb * sc.get("amb", .32) / (np.abs(amb).max() + 1e-6) * .5, t0)
        if typ == "hook2": steps(audio, t0 + .05, t0 + sc["_sw"] - .05); mix(audio, HISS, t0 + sc["_sw"]); mix(audio, BOOM * .5, t0 + sc["_sw"])
        if typ == "guess":
            for k in range(len(sc["opts"])): mix(audio, TICK * 1.5, t0 + .55 + k * .3)
            mix(audio, riser(min(1.0, dur - .3)), t0 + dur - min(1.0, dur - .3))
        if typ == "race":
            steps(audio, t0 + .2, t0 + sc["_T2"], .8)
            for k in range(9): mix(audio, TICK, t0 + sc["_T1"] + k * (sc["_T2"] - sc["_T1"]) / 9)
            mix(audio, DING, t0 + sc["_T2"]); mix(audio, BOOM * .45, t0 + sc["_T2"])
        if typ == "timer":
            mix(audio, HISS * .7, t0 + .05)
            for k in range(10): mix(audio, TICK, t0 + .3 + k * .125)
        if typ == "clock":
            steps(audio, t0, t0 + dur - .2, .7)
            for k in range(10): mix(audio, TICK, t0 + .5 + k * .12)
            mix(audio, DING, t0 + 1.7)
        if typ in ("text", "end") and sc.get("fig", ("",))[0] == "runner": steps(audio, t0, t0 + dur - .1, .7)
        if typ == "stat":
            for k in range(10): mix(audio, TICK, t0 + .15 + k * .1)
    audio = np.tanh(audio * 1.3) * .89
    wav = f"{OUT}/{spec['id']}.wav"; sf.write(wav, audio.astype(np.float32), SR)

    def frame(tg, fi):
        for t0, dur, sc, aud in timeline:
            if t0 <= tg < t0 + dur: break
        lt = tg - t0
        im = draw_scene(sc, lt, dur, acc, fi, tg)
        im = zoom(im.convert("RGB"), lt, dur, punch=.06 * (1 - ease(lt / .2)) if lt < .2 else 0)
        fl = 0
        if lt < .08 and tg > .1: fl = .55 * (1 - lt / .08)                       # flash cut
        if sc["type"] == "hook2" and 0 <= lt - sc["_sw"] < .1: fl = .7 * (1 - (lt - sc["_sw"]) / .1)   # pattern interrupt
        if fl: im = Image.blend(im, Image.new("RGB", (W, H), PAPER), fl)
        storybar(im, timeline, tg)
        return im
    if still:
        for i, (t0, dur, sc, aud) in enumerate(timeline):
            for j, f_ in enumerate(sc.get("_stills", (.3, .8))):
                frame(t0 + dur * f_, 0).save(f"{OUT}/{spec['id']}_s{i}{'ab'[j]}.jpg", quality=80)
        return
    mp4 = f"{OUT}/{spec['id']}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
    for fi in range(int(total * FPS)): p.stdin.write(frame(fi / FPS, fi).tobytes())
    p.stdin.close(); p.wait(); print(spec["id"], round(total, 1), "s")

if __name__ == "__main__":
    import importlib; REELS = importlib.import_module(os.environ.get("SPECS", "specs6")).REELS
    ids = sys.argv[1].split(",") if sys.argv[1] != "all" else [r["id"] for r in REELS]
    for r in REELS:
        if r["id"] in ids: build(r, still=len(sys.argv) > 2)
