"""Higgsfield API: atmosphere shots for reels (max 3 per topic).

Credentials (never commit them): put in `.env` at the repo root
    HF_API_KEY=...
    HF_API_SECRET=...
Get them at cloud.higgsfield.ai (separate API product, prepaid USD balance).

Shots are defined in the spec file per reel:
    dict(id="66_...", shots=[dict(name="ice_macro", prompt="...", seconds=5, image="path/or/url.jpg"), ...], ...)

Usage
    python3 engine/higgsfield.py 66_cold_runners            # dry run: shows what would be generated
    python3 engine/higgsfield.py 66_cold_runners --go       # really generate (spends API balance)
    SPECS=specs6 python3 engine/higgsfield.py all --go
Results: footage/ai/<reel_id>/<name>.mp4 (git-ignored) + footage/ai/log.jsonl (spend log).
Then use them in the reel with a scene: dict(type="clip", file="footage/ai/<reel_id>/<name>.mp4", ...)
"""
import importlib, json, os, sys, time, urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
MAX_SHOTS_PER_TOPIC = 3
# Default models (change here if Higgsfield renames them; see cloud.higgsfield.ai model pages).
MODEL_T2V = os.environ.get("HF_MODEL_T2V", "bytedance/seedance-2.0/text-to-video")
MODEL_I2V = os.environ.get("HF_MODEL_I2V", "bytedance/seedance-2.0/image-to-video")

# House style appended to every prompt: premium, real, not "AI".
STYLE = ("Photorealistic, shot on a cinema camera, natural skin texture, subtle film grain, calm premium health clinic, "
         "dark warm interior, ink-black (#151413) and warm paper-white (#F6F4F0) tones, soft practical light, shallow depth "
         "of field, slow controlled camera move, vertical 9:16. No text, no logos, no fire, no glowing effects, "
         "no sci-fi, no exaggerated sweat, no plastic skin.")

def load_env():
    p = os.path.join(REPO, ".env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"'))

def find_url(obj):
    """First video URL in the result JSON (format differs per model)."""
    if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in (".mp4", ".mov", "video")):
        return obj
    if isinstance(obj, dict):
        for k in ("video", "videos", "url", "output", "outputs", "result"):
            if k in obj:
                u = find_url(obj[k])
                if u: return u
        for v in obj.values():
            u = find_url(v)
            if u: return u
    if isinstance(obj, list):
        for v in obj:
            u = find_url(v)
            if u: return u
    return None

def run(reel, go):
    shots = reel.get("shots", [])
    if len(shots) > MAX_SHOTS_PER_TOPIC:
        sys.exit(f"{reel['id']}: {len(shots)} shots, max is {MAX_SHOTS_PER_TOPIC} per topic. Cut some.")
    out = os.path.join(REPO, "footage", "ai", reel["id"]); os.makedirs(out, exist_ok=True)
    for s in shots:
        dst = os.path.join(out, f"{s['name']}.mp4")
        if os.path.exists(dst):
            print("exists, skip:", dst); continue
        img = s.get("image")
        model = s.get("model") or (MODEL_I2V if img else MODEL_T2V)
        args = {"prompt": f"{s['prompt'].strip()} {STYLE}", "duration": s.get("seconds", 5), "aspect_ratio": "9:16"}
        args.update(s.get("args", {}))
        print(f"\n[{reel['id']}/{s['name']}] {model}\n  {args['prompt'][:160]}...")
        if not go:
            continue
        import higgsfield_client as hf
        if img:
            args["image_url"] = img if img.startswith("http") else hf.upload_file(img)
        t0 = time.time()
        result = hf.subscribe(model, arguments=args)
        url = find_url(result)
        if not url:
            print("  no video URL in result:", json.dumps(result)[:400]); continue
        urllib.request.urlretrieve(url, dst)
        with open(os.path.join(REPO, "footage", "ai", "log.jsonl"), "a") as f:
            f.write(json.dumps(dict(at=datetime.now().isoformat(timespec="seconds"), reel=reel["id"], shot=s["name"],
                                    model=model, seconds=args["duration"], took=round(time.time() - t0))) + "\n")
        print("  saved", dst)
    if not go:
        print("\nDry run. Nothing generated. Add --go to spend API balance.")

if __name__ == "__main__":
    load_env()
    if "--go" in sys.argv and not (os.environ.get("HF_KEY") or (os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET"))):
        sys.exit("Missing HF_API_KEY / HF_API_SECRET in .env")
    REELS = importlib.import_module(os.environ.get("SPECS", "specs5")).REELS
    ids = sys.argv[1].split(",")
    for r in REELS:
        if ids == ["all"] or r["id"] in ids:
            run(r, "--go" in sys.argv)
