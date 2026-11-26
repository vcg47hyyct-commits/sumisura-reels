"""Batch 66-68: three remakes of the winner "3 weeks of sauna. +32% endurance." (Scoon et al., 2007).
Same pattern (runners + one big number + one action), three different hooks. 68 uses Higgsfield atmosphere shots."""
HEAT = (196, 108, 58)
SRC = "Scoon et al., J Sci Med Sport 2007 · 6 runners"

REELS = [
 # A: group in the first word; viewer guesses the number, the race reveals it
 dict(id="66_runners_dont_skip_sauna", acc=HEAT, scenes=[
   dict(type="hook2", head=["Runners:", "don't skip the sauna."], switch=1,
        vo="Runners. Don't skip the sauna."),
   dict(type="guess", head=["3 weeks of sauna after training.", "How much longer did they last?"], opts=["+8%", "+16%", "+32%"],
        label="Guess", src=SRC,
        vo="Three weeks of sauna, after training. Guess how much longer they lasted."),
   dict(type="race", top="Run to exhaustion", lanes=["Training only", "Training + sauna"], count=32, fmt="+{:.0f}%",
        sub="longer before exhaustion", src=SRC,
        vo="Training only: exhausted. With sauna: thirty-two percent longer."),
   dict(type="text", head=["In a race:", "*about 1.9% faster."], gold=["about 1.9% faster."], fig=("runner", 520, 880, 150), src=SRC,
        vo="In a race, that's about one point nine percent faster."),
   dict(type="timer", head=["30 minutes.", "*Right after the run."], gold=["Right after the run."], label="The dose", src=SRC,
        vo="The dose? Thirty minutes. Right after the run."),
   dict(type="end", q="Sauna after your run?", fig=("sitter", 540, 880, 150), vo="Sauna after your run?", caps=False),
 ], caption="Runners: don't skip the sauna.\nCompetitive runners who sat in a sauna for about 30 min right after training, for 3 weeks: time to exhaustion +32%, roughly 1.9% faster in a race (Scoon et al., 2007). A small study: 6 runners.\nSame training. Plus heat.\nSauna after your run?\n#sumisura #sauna #running #endurance #brussels"),

 # B: race-time pain point; the number becomes a finish clock
 dict(id="67_faster_10k_sauna", acc=HEAT, scenes=[
   dict(type="hook2", head=["Want a faster 10K?", "Sit in a sauna."], switch=5,
        vo="Want a faster ten K? Sit in a sauna."),
   dict(type="timer", head=["Run first.", "*Then 30 min of sauna."], gold=["Then 30 min of sauna."], label="The study", src=SRC,
        vo="Runners trained as usual. Then thirty minutes of sauna. For three weeks."),
   dict(type="race", top="Run to exhaustion", lanes=["Training only", "Training + sauna"], count=32, fmt="+{:.0f}%",
        sub="longer before exhaustion", src=SRC,
        vo="Without sauna: exhausted. With sauna: thirty-two percent longer."),
   dict(type="clock", top="About 1.9% in a race. On a 50-min 10K:", start_s=3000, gain_s=57, sub="about 57 seconds faster",
        sub2="if the 1.9% holds for you", src="Race estimate from " + SRC, label="In a race",
        vo="In a race, that's about one point nine percent. On a fifty minute ten K: nearly a minute."),
   dict(type="text", head=["No extra kilometres.", "*Just heat."], gold=["Just heat."], fig=("sitter", 540, 900, 160),
        vo="No extra kilometres. Just heat."),
   dict(type="end", q="What's your 10K time?", fig=("runner", 520, 880, 140), vo="What's your ten K time?", caps=False),
 ], caption="Want a faster 10K? Sit in a sauna.\nRunners who added about 30 min of sauna right after training for 3 weeks lasted 32% longer before exhaustion, which the researchers put at roughly 1.9% in a race (Scoon et al., 2007). On a 50-minute 10K that would be close to a minute. Small study: 6 runners.\nNo extra kilometres. Just heat.\nWhat's your 10K time?\n#sumisura #sauna #running #10k #brussels"),

 # C: footage version. One MAGI-2 clip (Higgsfield app, 9:16, 15 s, 1080p) cut into three beats; animation for the data.
 # Generate in the Higgsfield app with MAGI_PROMPT, save as footage/ai/68_run_isnt_over_sauna/magi2.mp4
 dict(id="68_run_isnt_over_sauna", acc=HEAT, scenes=[
   dict(type="clip", file="footage/ai/68_run_isnt_over_sauna/magi2.mp4", start=0.3,
        head=["Your run isn't over.", "Go sit in the sauna."], gold=["Go sit in the sauna."],
        vo="Your run isn't over. Go sit in the sauna."),
   dict(type="race", top="3 weeks of sauna after training", lanes=["Training only", "Training + sauna"], count=32, fmt="+{:.0f}%",
        sub="longer before exhaustion", src=SRC,
        vo="Runners, three weeks. Training only: exhausted. With sauna: thirty-two percent longer."),
   dict(type="clip", file="footage/ai/68_run_isnt_over_sauna/magi2.mp4", start=5.2,
        head=["In a race:", "about 1.9% faster."], gold=["about 1.9% faster."], src=SRC,
        vo="In a race, that's about one point nine percent faster."),
   dict(type="clip", file="footage/ai/68_run_isnt_over_sauna/magi2.mp4", start=10.2, label="The dose",
        head=["30 minutes.", "Right after the run."], gold=["Right after the run."], src=SRC,
        vo="The dose? Thirty minutes. Right after the run."),
   dict(type="end", q="Sauna after your run?", fig=("sitter", 540, 880, 150), vo="Sauna after your run?", caps=False),
 ], caption="Your run isn't over. Go sit in the sauna.\nCompetitive runners who sat in a sauna for about 30 min right after training, for 3 weeks: time to exhaustion +32%, roughly 1.9% faster in a race (Scoon et al., 2007). A small study: 6 runners.\nThe run is the work. The heat is the extra.\nSauna after your run?\n#sumisura #sauna #running #endurance #brussels"),
]

# MAGI-2 prompt for reel 68 (model magi_2: 9:16, duration 15, 1080p, audio on, enhance_prompt off)
MAGI_PROMPT = """One continuous 15-second vertical video in three beats, photorealistic, handheld documentary feel, natural skin, no text, no logos.
0-5 s: Dusk on a quiet wet city street. A lean runner in a dark long-sleeve top and shorts, seen from behind and slightly to the side, runs the last metres at a steady pace, slows to a stop, hands on hips, breath visible in the cold air. Sound: fast footsteps on wet asphalt, heavy breathing.
5-10 s: Close-up. The same runner's hand pushes open a heavy cedar sauna door, warm amber light and thick steam roll out. Running shoes are left on a dark stone floor by the door. Sound: door creak, a low hiss.
10-15 s: Inside a small Finnish cedar sauna, warm low light. A ladle of water lands on dark hot stones and a cloud of steam rises. The runner sits down on the wooden bench with a linen towel, seen from the side in soft focus, shoulders glistening, breathing slowing down. A wooden sand timer on the wall. Sound: sharp hiss of water on stones, slow calm breathing.
Slow controlled camera, shallow depth of field, ink-black shadows and warm paper-white highlights, subtle film grain. No bikes, no gym equipment, no glowing effects, no exaggerated sweat."""
