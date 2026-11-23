"""Sumisura reel engine v3: the V3_cold_14C retention model applied to the spec library.
Faster voice, karaoke word captions, hook slam + boom, flash/whoosh cuts, slow zoom, count ticks, loop question.
python3 engine3.py <ids|all>   (SPECS env selects spec module, CAPS env the captions json)"""
import json, math, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/rl")
import reel as R
from reel import W, H, FPS, PAPER, txt, fade, ease, HB, fit
import engine2 as E
import v3 as V

ROOT = "/home/claude/rl/v5"; os.makedirs(f"{ROOT}/final", exist_ok=True)
SPEED = 1.12; GAP = 0.16; SR = 48000

def tts(text, path):
    if E._k is None:
        from kokoro_onnx import Kokoro
        E._k = Kokoro("/home/claude/tts/kokoro-v1.0.onnx", "/home/claude/tts/voices-v1.0.bin")
    s, sr = E._k.create(E.vo_text(text), voice="am_michael", speed=SPEED, lang="en-us")
    sf.write(path, s, sr); return len(s) / sr

def zoom(im, t, dur, k=.05, shake=0.0, punch=0.0):
    s = 1 + k * (t / max(dur, .1)) + punch
    w2, h2 = int(W / s), int(H / s)
    ox = (W - w2) / 2 + shake * 18 * math.sin(t * 90); oy = (H - h2) / 2 + shake * 18 * math.cos(t * 77)
    return im.crop((int(ox), int(oy), int(ox) + w2, int(oy) + h2)).resize((W, H), Image.BILINEAR)

YEL = (255, 214, 102)
def loop_scene(q, acc):
    words = q.split(); mid = (len(words) + 1) // 2
    l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
    sc = dict(type="text", head=[], vo=[q])
    def draw(t):
        im = R.bg(acc, .45 + .05 * math.sin(t * 2), big=True); d = ImageDraw.Draw(im)
        E.particles(d, t, fade(t, 0, .4))
        f = HB.font_variant(size=84)
        txt(d, (540, 560), l1, fit(f, l1, 940), fade(t, 0, .2), anchor="ma")
        txt(d, (540, 670), l2, fit(f, l2, 940), fade(t, .25, .2), col=YEL, anchor="ma")
        return im
    return sc, draw

def question(cap):
    qs = [ln for ln in cap.split("\n") if ln.strip().endswith("?") and not ln.startswith("#")]
    return qs[-1].strip() if qs else "Did you know this?"

def build(r, cap):
    rid, acc = r["id"], R.ACCENTS[r["accent"]]; out = f"{ROOT}/{rid}"; os.makedirs(out, exist_ok=True)
    scenes = [(sc, None) for sc in r["scenes"]] + [loop_scene(question(cap), acc)]
    sr = 24000; t0 = 0.0; tl = []; words = []; clips = []
    for k, (sc, drawfn) in enumerate(scenes):
        st = t0 + .12
        for j, ph in enumerate(sc["vo"]):
            p = f"{out}/vo_{k}_{j}.wav"; dur = tts(ph, p); clips.append((p, st))
            ws = ph.split(); lens = np.array([len(w) + 2 for w in ws], float); cs = np.cumsum(lens) / lens.sum(); prev = 0
            for w, c in zip(ws, cs):
                words.append((st + prev * dur, st + c * dur, w, (k, j))); prev = c
            st += dur + GAP
        sd = max(st - t0 + .1, 1.6); tl.append((sc, drawfn, t0, sd)); t0 += sd
    total = t0 + 2.4
    vo = np.zeros(int(total * sr) + sr)
    for p, st in clips:
        x, _ = sf.read(p); i = int(st * sr); vo[i:i + len(x)] += x
    sf.write(f"{out}/vo.wav", vo[:int(total * sr)], sr)
    fx = np.zeros(int(total * SR) + SR)
    def add(sig, at):
        i = int(at * SR); fx[i:i + len(sig)] += sig[:len(fx) - i]
    add(V.sfx_boom(), .02)
    for (sc, dfn, s0, sd) in tl[1:]: add(V.sfx_whoosh(), max(0, s0 - .15))
    for (sc, dfn, s0, sd) in tl:
        if sc.get("type") == "stat" and "count" in sc:
            for q in range(14): add(V.sfx_tick(), s0 + .4 + q * 1.4 / 14)
        if sc.get("type") == "bars":
            for q in range(10): add(V.sfx_tick(), s0 + .6 + q * 1.2 / 10)
    add(V.sfx_whoosh(), total - 2.5)
    sf.write(f"{out}/sfx.wav", fx[:int(total * SR)], SR)
    files = []
    for k, (sc, dfn, s0, sd) in enumerate(tl):
        fn = f"{out}/s{k}.mp4"; files.append(fn)
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", fn + ".tmp.mp4"], stdin=subprocess.PIPE)
        for i in range(int(round(sd * FPS))):
            t = i / FPS
            im = (dfn(t) if dfn else E.scene(sc, t, acc)).convert("RGBA")
            if k == 0:
                im = zoom(im, t, sd, .06, max(0, 1 - t / .4), punch=.18 * max(0, 1 - ease(t / .25)))
            else:
                sh = .5 * max(0, 1 - (t - .4) / 1.0) if (sc.get("type") == "stat" and .4 < t < 1.4) else 0
                im = zoom(im, t, sd, .05, sh)
                if t < .12: im = Image.blend(im, Image.new("RGBA", (W, H), (255, 255, 255, 255)), .5 * (1 - t / .12))
            V.captions(im, words, s0 + t)
            p.stdin.write(im.convert("RGB").tobytes())
        p.stdin.close(); assert p.wait() == 0; os.rename(fn + ".tmp.mp4", fn)
    fn = f"{out}/end.mp4"; files.append(fn)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", fn], stdin=subprocess.PIPE)
    for i in range(int(2.4 * FPS)): p.stdin.write(R.s_end({"series": r["series"]}, i / FPS, acc).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    with open(f"{out}/list.txt", "w") as f:
        for fn in files: f.write(f"file '{os.path.basename(fn)}'\n")
    R.music(f"{out}/music.m4a", total, r.get("key", "A"), seed=sum(map(ord, rid)))
    tmp = f"{ROOT}/final/{rid}.tmp.mp4"
    subprocess.run(f"ffmpeg -v error -y -f concat -safe 0 -i {out}/list.txt -i {out}/vo.wav -i {out}/music.m4a -i {out}/sfx.wav -filter_complex "
                   f"\"[1:a]aresample=48000,highpass=f=70,loudnorm=I=-15:TP=-1.5,aformat=channel_layouts=stereo,asplit=2[v1][v2];[2:a]aresample=48000,volume=0.6[m];"
                   f"[m][v1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=400[md];[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.8[fx];"
                   f"[md][v2][fx]amix=inputs=3:normalize=0[a]\" -map 0:v -map \"[a]\" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart {tmp}",
                   shell=True, check=True)
    os.rename(tmp, f"{ROOT}/final/{rid}.mp4")
    return round(total, 1)

if __name__ == "__main__":
    import importlib
    REELS = importlib.import_module(os.environ.get("SPECS", "specs3")).REELS
    caps = json.load(open(os.environ.get("CAPS", "/home/claude/sumisura-reels/reels/b2/captions.json")))
    if "C" in caps: caps = caps["C"]
    which = sys.argv[1]
    for r in REELS:
        if which == "all" or r["id"] in which.split(","):
            print(r["id"], build(r, caps.get(r["id"], "")), flush=True)
