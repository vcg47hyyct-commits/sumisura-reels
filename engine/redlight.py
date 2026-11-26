"""Light-therapy trial reels for @lucarobertopotti: ACNE and WRINKLES (V3 retention model, fixed 15 s grid).

    python3 engine/redlight.py acne A            -> output/acne_v3_A.mp4        (own animation for the abstract visuals)
    python3 engine/redlight.py acne A hf         -> output/acne_v3_A_hf.mp4     (Higgsfield shots for the abstract visuals)
    python3 engine/redlight.py all               -> all reels, hooks A/B/C, both versions that have their inputs
    add "preview" to render with grey MISSING placeholders into out/preview/ (internal timing check only, never deliver)

Own footage: footage/redlight/<name>.mp4. A missing clip stops the render and is listed; it is never replaced.
Higgsfield shots (abstract only, max 3 per reel): footage/ai/<reel>/<name>.mp4, prompts in HF_SHOTS below.
Rules built in: text only inside the safe zone (y 230-1440, x < 850), white text with soft shadow, cuts <= 2 s,
voice at -14 LUFS, no music, last second replays the opening shot backwards so the last frame matches the first.
"""
import math, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE); sys.path.insert(0, HERE)
import engine4 as e
from engine4 import W, H, FPS, SR, INK, PAPER, GOLD, F, fit, ease, fade, A, mix, tone, noise, Clip, BOOM, WHOOSH, TICK

OUTDIR = os.path.join(REPO, "output"); DUR = 15.0
CX = 435; MAXW = 770                      # text column: x 50..820, clear of the right 230 px
WHITE = (255, 255, 255); BLUE = (70, 120, 255); RED = (255, 60, 50)
yy, xx = e.yy, e.xx

HOOKS = dict(
    acne=dict(A="ACNE THAT WON'T GO AWAY?", B="TRIED EVERY CREAM?", C="SPOTS BACK EVERY MONTH?"),
    wrinkles=dict(A="FINE LINES SHOWING UP?", B="TIRED SKIN, EVERY MORNING?", C="SKIN LOOKS OLDER THAN YOU?"))
HOOK_VO = dict(
    acne=dict(A="Acne that won't go away?", B="Tried every cream?", C="Spots back every month?"),
    wrinkles=dict(A="Fine lines showing up?", B="Tired skin, every morning?", C="Skin looks older than you?"))

# Higgsfield prompts: abstract visuals only. No faces, no rooms, no people.
HF_STYLE = ("Abstract macro, photorealistic, vertical 9:16, 5 seconds, dark background, slow smooth motion, shallow depth of field. "
            "No face, no person, no room, no device, no text, no logo.")
HF_SHOTS = dict(
    acne=[("skin_waves", "Extreme macro of smooth human skin texture filling the frame, unrecognisable, pores visible. Soft waves of blue light and red light sweep slowly across the surface, one after the other, blue and red clearly both present."),
          ("cells", "Microscopic view of round translucent skin cells drifting slowly. Blue light and red light pulse gently through them in alternating waves."),
          ("waves", "Two smooth ribbons of light, one blue and one red, flowing side by side in slow sine waves across a black background.")],
    wrinkles=[("skin_red", "Extreme macro of human skin texture with fine lines, unrecognisable, filling the frame. A soft wave of warm red light sweeps slowly across the surface."),
              ("fibres", "Microscopic abstract view of fine pale fibres forming a dense woven network, slowly drifting, lit by soft red light."),
              ("red_waves", "Smooth ribbons of red light flowing in slow sine waves across a black background.")])

# ---------- reels: (start, end, visual, on-screen lines, voice-over) ----------
def reel(name, v, hf):
    h, hv = HOOKS[name][v], HOOK_VO[name][v]
    ai = lambda n: ("ai", f"footage/ai/{name}/{n}.mp4")
    if name == "acne":
        panel = os.path.exists(os.path.join(REPO, "footage/redlight/BLUE_OK.txt"))
        return [
            (0, 2, ("clip", "footage/redlight/mirror_chin.mp4"), dict(hook=h), hv),
            (2, 4, ("clip", "footage/redlight/creams.mp4"), dict(lines=["Tried every cream?"]), "Tried every cream?"),
            (4, 6, ai("skin_waves") if hf else ("anim", "skin", (BLUE, RED)), dict(lines=["Blue + red light."], grp=0), "One study: blue plus red light."),
            (6, 8, ai("cells") if hf else ("anim", "cells", (BLUE, RED)), dict(lines=["Blue + red light.", "15 min a day.", "12 weeks."], grp=0, src="Papageorgiou et al., Br J Dermatol 2000"),
             "Fifteen minutes a day. Twelve weeks."),
            (8, 10, ("anim", "bar", dict(vals=[(76, "-76%", RED)], sub="inflamed spots", count=True)), dict(src="Papageorgiou et al., Br J Dermatol 2000 · 107 people"),
             "Inflamed spots: minus seventy-six percent,"),
            (10, 12, ("anim", "bar", dict(vals=[(76, "-76%", RED)], sub="inflamed spots", count=False, zoom=True)), dict(src="Papageorgiou et al., Br J Dermatol 2000 · 107 people"),
             "on average."),
            (12, 14, ("clip", "footage/redlight/panel_on.mp4") if panel else (ai("waves") if hf else ("anim", "waves", (BLUE, RED))),
             dict(lines=["Mild to moderate acne.", "Not a cure."]), "Mild to moderate acne. Not a cure."),
            (14, 15, ("loop", "footage/redlight/mirror_chin.mp4"), dict(hook=h), None)]
    return [
        (0, 2, ("clip", "footage/redlight/mirror_eyes.mp4"), dict(hook=h), hv),
        (2, 4, ("clip", "footage/redlight/cream_close.mp4"), dict(lines=["Another cream?"]), "Another cream?"),
        (4, 6, ("clip", "footage/redlight/panel_on.mp4"), dict(lines=["Red light."], grp=0), "One study: red light."),
        (6, 8, ("clip", "footage/redlight/panel_sit.mp4"), dict(lines=["Red light.", "2x a week.", "30 sessions."], grp=0, src="Wunsch & Matuschka, Photomed Laser Surg 2014"),
         "Twice a week. Thirty sessions."),
        (8, 10, ("anim", "bar", dict(vals=[(69, "69%", RED), (4, "4%", WHITE)], labs=["Red light", "Control group"], top="Fewer wrinkles:", count=True, bg=ai("fibres") if hf else None)),
         dict(src="Wunsch & Matuschka, Photomed Laser Surg 2014 · 136 people"), "Fewer wrinkles in sixty-nine percent."),
        (10, 12, ("anim", "bar", dict(vals=[(69, "69%", RED), (4, "4%", WHITE)], labs=["Red light", "Control group"], top="Fewer wrinkles: 69% vs 4%", count=False, zoom=True, bg=ai("red_waves") if hf else None)),
         dict(src="Wunsch & Matuschka, Photomed Laser Surg 2014 · 136 people"), "Versus four percent, without light."),
        (12, 14, ("clip", "footage/redlight/face_glow.mp4"), dict(lines=["Not a miracle.", "A dose."]), "Not a miracle. A dose."),
        (14, 15, ("loop", "footage/redlight/mirror_eyes.mp4"), dict(hook=h), None)]

# ---------- text: white with a soft shadow, always inside the safe zone ----------
def TS(im, xy, s, font, a=1., col=WHITE, anchor="ma"):
    if a <= .01: return
    box = ImageDraw.Draw(im).textbbox(xy, s, font=font, anchor=anchor)
    assert box[0] >= 40 and box[2] <= W - 230 and box[1] >= 230 and box[3] <= 1440, f"text outside safe zone: {s!r} {box}"
    pad = 30; x0, y0 = int(box[0]) - pad, int(box[1]) - pad
    sh = Image.new("L", (int(box[2] - box[0]) + 2 * pad, int(box[3] - box[1]) + 2 * pad), 0)
    ImageDraw.Draw(sh).text((xy[0] - x0, xy[1] - y0 + 4), s, font=font, fill=int(215 * a), anchor=anchor)
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    im.paste(Image.new("RGB", sh.size, (0, 0, 0)), (x0, y0), sh)
    ImageDraw.Draw(im, "RGBA").text(xy, s, font=font, fill=A(col, a), anchor=anchor)

def lines(im, ls, t, y=300, size=78, grp_t=None):
    """Lines stack up; with grp_t (time since the group started) earlier lines stay on screen across the cut."""
    for i, s in enumerate(ls):
        new = i == len(ls) - 1 if grp_t is not None and len(ls) > 1 else True
        t0 = 0 if (i == 0 or not new) else .0
        if grp_t is not None and len(ls) > 1 and i >= 1: t0 = (i - 1) * .75      # 2nd line at 0 s, 3rd at .75 s of this cut
        a = 1. if (grp_t is not None and i == 0 and len(ls) > 1) else ease((t - t0) / .12)
        TS(im, (CX, y + i * 104), s, fit(F(700, size), s, MAXW), a)

def caps(im, words, t):
    if not words: return
    idx = 0
    for i, (w, a0, a1) in enumerate(words):
        if t >= a0: idx = i
    c0 = (idx // 3) * 3; chunk = words[c0:c0 + 3]; f = F(700, 58)
    while sum(f.getlength(w) for w, _, _ in chunk) + 18 * (len(chunk) - 1) > MAXW: f = f.font_variant(size=f.size - 4)
    sz = [f.getlength(w) for w, _, _ in chunk]; x = CX - (sum(sz) + 18 * (len(chunk) - 1)) / 2
    for (w, a0, a1), s in zip(chunk, sz):
        if t >= a0: TS(im, (x, 1210), w, f, 1., GOLD if a0 <= t < a1 + .05 else WHITE, "la")
        x += s + 18

# ---------- own animations (the "Fable" version) ----------
_rs = np.random.default_rng(3)
def _skin():
    n = np.asarray(Image.fromarray(_rs.random((96, 54)).astype(np.float32)).resize((W, H), Image.BICUBIC))
    p = np.asarray(Image.fromarray(((_rs.random((H // 3, W // 3)) > .985) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))) / 255
    return (np.array((196, 150, 128), np.float32) * (.82 + .3 * n)[..., None]) * (1 - .5 * p[..., None])
SKIN = _skin()
U = (xx * .45 + yy) / (W * .45 + H)                      # diagonal coordinate 0..1

def _ribbons(d, t, cols, y0, amp=120, n=2, a=1.):
    for i, c in enumerate(cols):
        for k in range(n):
            pts = [(x, y0 + i * 150 + k * 26 + amp * math.sin(x / 150 + t * (3.2 + i) + i * 1.7 + k * .5)) for x in range(-20, W + 21, 20)]
            d.line(pts, fill=A(c, a * (.95 - k * .4)), width=12 - k * 5, joint="curve")

def anim(kind, arg, t, fi):
    if kind == "skin":                                   # blue + red light waves sweeping over skin
        arr = SKIN * .30
        for i, c in enumerate(arg):
            pos = ((t * .55 + i * .5) % 1.3) - .15
            band = np.exp(-((U - pos) / .16) ** 2)[..., None]
            arr = arr + (SKIN * .55 + 60) * band * (np.array(c, np.float32) / 255)
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im, "RGBA")
        _ribbons(d, t, arg, 760, amp=70, a=.75); return im
    if kind == "cells":                                  # cells pulsing under alternating blue and red light
        im = Image.new("RGB", (W, H), (10, 10, 16)); d = ImageDraw.Draw(im, "RGBA"); r = np.random.default_rng(9)
        for k in range(46):
            x, y = r.uniform(-40, W + 40), r.uniform(-40, H + 40); rad = r.uniform(60, 130); ph = r.uniform(0, 6.28)
            c = arg[k % len(arg)]; pu = .5 + .5 * math.sin(t * 5 + ph + (0 if k % 2 else math.pi)); y -= t * 22
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=A(c, .10 + .30 * pu), outline=A(c, .55 + .4 * pu), width=5)
            d.ellipse((x - rad * .3, y - rad * .3, x + rad * .3, y + rad * .3), fill=A(c, .25 + .5 * pu))
        return im.filter(ImageFilter.GaussianBlur(1.2))
    if kind == "waves":                                  # blue + red waves on dark
        im = Image.new("RGB", (W, H), (9, 9, 13)); d = ImageDraw.Draw(im, "RGBA")
        _ribbons(d, t, arg, 620, amp=150, n=3)
        g = im.filter(ImageFilter.GaussianBlur(26)); return Image.blend(im, Image.eval(g, lambda v: min(255, int(v * 2.2))), .5)
    raise ValueError(kind)

def bars(im, o, t, tg, fi, bg=None):
    """One bar (acne: -76%) or two bars (wrinkles: 69% vs 4%). Numbers are fixed strings; only the bar grows."""
    d = ImageDraw.Draw(im, "RGBA"); vals = o["vals"]; k = ease(t / 1.25) if o.get("count") else 1.
    if o.get("top"): TS(im, (CX, 300), o["top"], fit(F(700, 66), o["top"], MAXW), ease(t / .12))
    if len(vals) == 1:
        v, s, c = vals[0]; TS(im, (CX, 330), s, F(800, 230), 1., WHITE)      # the number is never animated: every frame shows the exact claim
        d.rounded_rectangle((70, 640, 800, 700), radius=30, fill=A(WHITE, .16))
        d.rounded_rectangle((70, 640, 70 + max(60, 730 * v / 100 * k), 700), radius=30, fill=A(c, 1))
        TS(im, (CX, 740), o["sub"], F(700, 70), ease((t - .2) / .15) if o.get("count") else 1.)
    else:
        for i, (v, s, c) in enumerate(vals):
            y = 470 + i * 270; kk = ease((t - i * .25) / 1.1) if o.get("count") else 1.
            TS(im, (70, y), o["labs"][i], F(600, 46), 1., WHITE, "la")
            d.rounded_rectangle((70, y + 70, 800, y + 140), radius=35, fill=A(WHITE, .16))
            d.rounded_rectangle((70, y + 70, 70 + max(70, 730 * v / 100 * kk), y + 140), radius=35, fill=A(c, 1))
            TS(im, (800, y - 22), s, F(800, 84), 1., WHITE, "ra")

# ---------- sources ----------
class Missing(Exception): pass
def _path(p): return os.path.join(REPO, p)
def placeholder(name):
    im = Image.new("RGB", (W, H), (60, 60, 64)); ImageDraw.Draw(im).text((CX, 900), "MISSING: " + os.path.basename(name), font=F(700, 44), fill=(255, 80, 80), anchor="ma"); return im

def build(name, v, hf=False, preview=False, still=False):
    segs = reel(name, v, hf)
    need = sorted({s[2][1] for s in segs if s[2][0] in ("clip", "loop", "ai")} | {s[2][2]["bg"][1] for s in segs if s[2][0] == "anim" and s[2][1] == "bar" and s[2][2].get("bg")})
    miss = [p for p in need if not os.path.exists(_path(p))]
    if miss and not preview: raise Missing(miss)
    tag = f"{name}_v3_{v}" + ("_hf" if hf else "")
    out = os.path.join(REPO, "out", "preview") if preview else OUTDIR; os.makedirs(out, exist_ok=True)
    # --- voice: each line must fit its slot; speed goes up (never down) until it does ---
    voice = np.zeros(int(SR * DUR)); words = {}
    for i, (a, b, vis, txt, vo) in enumerate(segs):
        if not vo: continue
        j = i
        while j + 1 < len(segs) and segs[j + 1][4] is None and segs[j + 1][2][0] != "loop": j += 1
        slot = segs[j][1] - a - .12; sp = 1.12
        while True:
            e.SPEED = sp; aud = e.tts(vo); d_ = len(aud) / SR
            if d_ <= slot or sp >= 1.5: break
            sp += .04
        assert d_ <= slot + .25, f"voice line too long for its slot: {vo!r} {d_:.2f}s > {slot:.2f}s"
        mix(voice, aud, a + .04); words[i] = e.word_times(vo, d_, .04)
    e.SPEED = 1.12
    vw = os.path.join(out, tag + "_voice.wav"); sf.write(vw, voice.astype(np.float32), SR)
    sfx = np.zeros(int(SR * DUR)); mix(sfx, BOOM * .5, 0)
    for a, b, vis, txt, vo in segs[1:]: mix(sfx, WHOOSH * .7, a - .12)
    for a, b, vis, txt, vo in segs:
        if vis[0] == "anim" and vis[1] == "bar" and vis[2].get("count"):
            for k in range(10): mix(sfx, TICK * .8, a + .1 + k * .11)
    sw = os.path.join(out, tag + "_sfx.wav"); sf.write(sw, sfx.astype(np.float32), SR)
    # --- picture ---
    clips = {}
    def clipframe(i, p, start=0.):
        if not os.path.exists(_path(p)): return placeholder(p)
        if i not in clips: clips[i] = Clip(p, start)
        return clips[i].frame()
    loop = None
    def frame(tg, fi):
        nonlocal loop
        for i, (a, b, vis, txt, vo) in enumerate(segs):
            if a <= tg < b: break
        t = tg - a; kind = vis[0]
        if kind in ("clip", "ai"): im = clipframe(i, vis[1], 0.3 if kind == "ai" else 0.)
        elif kind == "loop":                              # opening shot played backwards: the last frame equals frame 1
            if loop is None:
                if os.path.exists(_path(vis[1])): c = Clip(vis[1], 0.); loop = [c.frame() for _ in range(int((b - a) * FPS))]
                else: loop = [placeholder(vis[1])] * int((b - a) * FPS)
            im = loop[max(0, len(loop) - 1 - int(round(t * FPS)))].copy()
        elif vis[1] == "bar":
            o = vis[2]; bg = o.get("bg")
            im = clipframe(i, bg[1], 0.3) if bg else Image.new("RGB", (W, H), (12, 11, 12))
            if bg: im = Image.eval(im, lambda v_: int(v_ * .38))
            else:
                d0 = ImageDraw.Draw(im, "RGBA"); _ribbons(d0, tg, [o["vals"][0][2]], 1020, amp=60, a=.35)
        else: im = anim(vis[1], vis[2], tg, fi)
        if kind in ("clip", "ai", "loop"):                # gentle shade so white text reads on any footage
            im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), .16)
        if kind != "loop":                                # punch-in on every cut, slow push after
            s = 1 + .035 * t / (b - a) + (.05 * (1 - ease(t / .18)) if t < .18 and tg > .05 else 0)
            if vis[0] == "anim" and vis[1] == "bar" and vis[2].get("zoom"): pass
            w2, h2 = int(W / s), int(H / s); im = im.crop(((W - w2) // 2, (H - h2) // 2, (W - w2) // 2 + w2, (H - h2) // 2 + h2)).resize((W, H), Image.BILINEAR)
        if vis[0] == "anim" and vis[1] == "bar": bars(im, vis[2], t, tg, fi)
        if "hook" in txt:                                 # visible from frame 1: no fade-in
            ws = txt["hook"].split(); mid = (len(ws) + 1) // 2; l1, l2 = " ".join(ws[:mid]), " ".join(ws[mid:])
            f = F(800, 92)
            while max(f.getlength(l1), f.getlength(l2)) > MAXW: f = f.font_variant(size=f.size - 4)
            TS(im, (CX, 320), l1, f); TS(im, (CX, 320 + f.size + 22), l2, f)
        if "lines" in txt: lines(im, txt["lines"], t, grp_t=t if "grp" in txt else None)
        if txt.get("src"): TS(im, (CX, 1360), txt["src"], fit(F(500, 26), txt["src"], MAXW), .85)
        if i in words: caps(im, words[i], t)
        if t < .07 and tg > .05 and kind != "loop": im = Image.blend(im, Image.new("RGB", (W, H), WHITE), .5 * (1 - t / .07))
        return im
    if still:
        for k, tg in enumerate(still): frame(tg, 0).save(os.path.join(out, f"{tag}_t{tg:04.1f}.jpg"), quality=82)
        return tag
    mp4 = os.path.join(out, tag + ".mp4")
    def lufs(extra=""):                                # integrated loudness of the voice stem (EBU R128)
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", vw, "-af", extra + "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
        return float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    gain = -14 - lufs(); chain = f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false,"
    for _ in range(5):                                 # the limiter takes a little back: correct until within 0.15 LU
        d_ = -14 - lufs(chain)
        if abs(d_) < .15: break
        gain += d_; chain = f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false,"
    print(f"  voice {lufs(chain):.1f} LUFS")
    af = "[1:a]" + chain + "aresample=48000[v];[2:a]aresample=48000,volume=0.5[s];[v][s]amix=inputs=2:normalize=0[a]"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", vw, "-i", sw,
                          "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(DUR), "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
    for fi in range(int(DUR * FPS)): p.stdin.write(frame(fi / FPS, fi).tobytes())
    p.stdin.close(); p.wait(); os.remove(sw)
    if not preview: os.remove(vw)
    print("rendered", mp4); return tag

if __name__ == "__main__":
    args = sys.argv[1:]; preview = "preview" in args; hf_only = "hf" in args
    names = ["acne", "wrinkles"] if args[0] == "all" else [args[0]]
    vs = [a for a in args[1:] if a in ("A", "B", "C")] or ["A", "B", "C"]
    missing = {}
    for n in names:
        for v in vs:
            for hf in ([True] if hf_only else [False, True] if args[0] == "all" else [False]):
                try: build(n, v, hf, preview)
                except Missing as m: missing[f"{n}_v3_{v}" + ("_hf" if hf else "")] = m.args[0]
    if missing:
        print("\nNOT RENDERED, clips missing:")
        for k, m in missing.items(): print(" ", k, "->", ", ".join(m))
        sys.exit(2)
