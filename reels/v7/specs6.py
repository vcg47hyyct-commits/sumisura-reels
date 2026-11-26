"""Batch 66-68: three remakes of the winner "3 weeks of sauna. +32% endurance." (Scoon et al., 2007).
Same pattern (runners + one big number + one action), three different hooks. 68 uses Higgsfield atmosphere shots."""
HEAT = (196, 108, 58)
SRC = "Scoon et al., J Sci Med Sport 2007 · 6 runners"

REELS = [
 # A: group called out in the first word, action as the hook
 dict(id="66_runners_dont_skip_sauna", acc=HEAT, scenes=[
   dict(type="hook", head=["Runners:", "don't skip the sauna."], icon=("runner", 540, 900, 200),
        vo="Runners. Don't skip the sauna."),
   dict(type="stat", top="3 weeks of sauna after training", count=32, fmt="+{:.0f}%", sub="time to exhaustion",
        sub2="competitive male runners", icon=("heat", 540, 1060, 80), src=SRC, label="The data",
        vo="Three weeks of sauna after training. Time to exhaustion: plus thirty-two percent."),
   dict(type="text", head=["In a race:", "*about 1.9% faster."], gold=["about 1.9% faster."], icon=("runner", 540, 900, 170), src=SRC,
        vo="In a race, that's about one point nine percent faster."),
   dict(type="text", head=["30 minutes.", "*Right after the run."], gold=["Right after the run."], label="The dose",
        icon=("heat", 540, 900, 150), src=SRC,
        vo="The dose? Thirty minutes. Right after the run."),
   dict(type="end", q="Sauna after your run?", vo="Sauna after your run?", caps=False),
 ], caption="Runners: don't skip the sauna.\nCompetitive runners who sat in a sauna for about 30 min right after training, for 3 weeks: time to exhaustion +32%, roughly 1.9% faster in a race (Scoon et al., 2007). A small study: 6 runners.\nSame training. Plus heat.\nSauna after your run?\n#sumisura #sauna #running #endurance #brussels"),

 # B: race-time pain point, the number translated to a 10K
 dict(id="67_faster_10k_sauna", acc=HEAT, scenes=[
   dict(type="hook", head=["Want a faster 10K?", "Sit in a sauna."], icon=("runner", 540, 900, 200),
        vo="Want a faster ten K? Sit in a sauna."),
   dict(type="text", head=["Run first.", "*Then 30 min of sauna.", "*For 3 weeks."], gold=["Then 30 min of sauna."], label="The study",
        icon=("heat", 540, 1000, 130), src=SRC,
        vo="Runners trained as usual. Then thirty minutes of sauna. For three weeks."),
   dict(type="stat", top="They lasted", count=32, fmt="+{:.0f}%", sub="longer before exhaustion",
        icon=("runner", 540, 1060, 90), src=SRC, label="The data",
        vo="They lasted thirty-two percent longer before exhaustion."),
   dict(type="stat", top="About 1.9% in a race. On a 50-min 10K:", count=57, fmt="~{:.0f} s", sub="faster",
        sub2="if the 1.9% holds for you", src="Race estimate from " + SRC, label="In a race",
        vo="In a race, that's about one point nine percent. On a fifty minute ten K: nearly a minute."),
   dict(type="text", head=["No extra kilometres.", "*Just heat."], gold=["Just heat."], icon=("heat", 540, 900, 150),
        vo="No extra kilometres. Just heat."),
   dict(type="end", q="What's your 10K time?", vo="What's your ten K time?", caps=False),
 ], caption="Want a faster 10K? Sit in a sauna.\nRunners who added about 30 min of sauna right after training for 3 weeks lasted 32% longer before exhaustion, which the researchers put at roughly 1.9% in a race (Scoon et al., 2007). On a 50-minute 10K that would be close to a minute. Small study: 6 runners.\nNo extra kilometres. Just heat.\nWhat's your 10K time?\n#sumisura #sauna #running #10k #brussels"),

 # C: footage version, Higgsfield atmosphere shots as hook and dose scene, animation for the data
 dict(id="68_run_isnt_over_sauna", acc=HEAT,
   shots=[
     dict(name="stones_steam", seconds=5,
          prompt="Extreme close-up of dark sauna stones in a wooden Finnish sauna, a ladle of water is poured over the hot stones, "
                 "a thick burst of white steam rises and fills the frame, warm low light on cedar wood in the background."),
     dict(name="shoes_door", seconds=5,
          prompt="A pair of used road running shoes, slightly dusty, left on a dark stone floor in front of a closed glass sauna door, "
                 "warm light and soft steam visible behind the glass, cedar wood sauna interior out of focus, no people."),
     dict(name="sand_timer", seconds=5,
          prompt="Close-up of a wooden sand timer mounted on a cedar sauna wall, sand slowly running down, a folded linen towel on the "
                 "wooden bench below, thin steam drifting through warm low light, no people."),
   ],
   scenes=[
   dict(type="clip", file="footage/ai/68_run_isnt_over_sauna/stones_steam.mp4", start=0.6,
        head=["Your run isn't over.", "Go sit in the sauna."], gold=["Go sit in the sauna."],
        vo="Your run isn't over. Go sit in the sauna."),
   dict(type="stat", top="Runners. 3 weeks of sauna after training", count=32, fmt="+{:.0f}%", sub="time to exhaustion",
        icon=("runner", 540, 1060, 90), src=SRC, label="The data",
        vo="Runners did it for three weeks. Time to exhaustion: plus thirty-two percent."),
   dict(type="clip", file="footage/ai/68_run_isnt_over_sauna/shoes_door.mp4", start=0.5,
        head=["In a race:", "about 1.9% faster."], gold=["about 1.9% faster."], src=SRC,
        vo="In a race, that's about one point nine percent faster."),
   dict(type="clip", file="footage/ai/68_run_isnt_over_sauna/sand_timer.mp4", start=0.5, label="The dose",
        head=["30 minutes.", "Right after the run."], gold=["Right after the run."], src=SRC,
        vo="The dose? Thirty minutes. Right after the run."),
   dict(type="end", q="Sauna after your run?", vo="Sauna after your run?", caps=False),
 ], caption="Your run isn't over. Go sit in the sauna.\nCompetitive runners who sat in a sauna for about 30 min right after training, for 3 weeks: time to exhaustion +32%, roughly 1.9% faster in a race (Scoon et al., 2007). A small study: 6 runners.\nThe run is the work. The heat is the extra.\nSauna after your run?\n#sumisura #sauna #running #endurance #brussels"),
]
