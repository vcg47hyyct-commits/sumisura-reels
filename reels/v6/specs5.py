"""Batch 61-65: simple, self-testable topics, pain-point hooks."""
BREATH = (96, 150, 136); COLD = (60, 125, 190); VO2 = (168, 128, 86); STR = (150, 96, 70); MUS = (120, 110, 150)

REELS = [
 dict(id="61_breath_exhale_heart", acc=BREATH, scenes=[
   dict(type="hook", head=["Breathe out longer.", "Your heart slows down."], icon=("lungs", 540, 900, 170),
        vo="Breathe out longer, and your heart slows down. Try it now."),
   dict(type="breath", phase="in", top="Breathe in.", big="IN", small="4 seconds", label="Try it",
        vo="Breathe in. Your heart rate rises."),
   dict(type="breath", phase="out", top="Now breathe out. Slowly.", big="OUT", small="8 seconds", label="Try it",
        vo="Now breathe out, slowly. It drops."),
   dict(type="text", head=["Every exhale", "*brakes your heart."], gold=["brakes your heart."], label="Why", icon=("pulse", 540, 900, 110),
        src="Respiratory sinus arrhythmia (Hirsch & Bishop, 1981)",
        vo="On every exhale, your vagus nerve brakes the heart. It's called respiratory sinus arrhythmia."),
   dict(type="text", head=["Long exhale:", "*heart rate down.", "Sharp inhales:", "*heart rate up."], gold=["heart rate down."], label="The rule",
        vo="So a long exhale calms you down. Short, sharp inhales do the opposite."),
   dict(type="end", q="Did your heart slow down?", vo="Did your heart slow down?", caps=False),
 ], caption="Breathe out longer. Your heart slows down.\nHeart rate rises when you breathe in and falls when you breathe out: respiratory sinus arrhythmia (Hirsch & Bishop, 1981). A longer exhale gives the brake more time.\nTry it: in for 4, out for 8.\nDid your heart slow down?\n#sumisura #breathwork #heartrate #nervoussystem #brussels"),

 dict(id="62_cold_shock_first_30s", acc=COLD, cold=True, scenes=[
   dict(type="hook", head=["Can't breathe", "in the ice bath?"], icon=("ice", 540, 880, 190), gasp=True,
        vo="Can't breathe in the ice bath? That's not weakness."),
   dict(type="text", head=["It's cold shock.", "*A reflex."], gold=["A reflex."], label="The first 30 seconds", icon=("lungs", 540, 860, 160, {"gasp": 1.0}), gasp=True, frost=True,
        vo="It's cold shock. In the first thirty seconds you gasp, your breathing races and your heart rate jumps."),
   dict(type="dots", n=5, top="5 short immersions.", sub="The cold shock response shrank.", label="It adapts", frost=True,
        src="Tipton et al., J Physiol 1998",
        vo="But it adapts fast. In one study, just five short immersions clearly reduced the cold shock response."),
   dict(type="text", head=["Short.", "*Controlled.", "Never alone."], gold=["Controlled."], label="So we dose it", icon=("ice", 540, 900, 120), frost=True,
        vo="So the first sessions are the hardest. We keep them short, controlled, and never alone."),
   dict(type="end", q="How did your first one feel?", vo="How did your first one feel?", caps=False),
 ], caption="Can't breathe in the ice bath? That's not weakness.\nCold shock: in the first 30 seconds you gasp, breathing races and heart rate jumps. In one study, 5 short immersions clearly reduced that response (Tipton et al., 1998).\nShort. Controlled. Never alone.\nHow did your first one feel?\n#sumisura #icebath #coldplunge #coldexposure #brussels"),

 dict(id="63_grip_vs_blood_pressure", acc=STR, scenes=[
   dict(type="hook", head=["Your doctor checks", "your blood pressure."], icon=("pulse", 540, 880, 120),
        vo="Your doctor checks your blood pressure."),
   dict(type="text", head=["Nobody checks", "*your grip."], gold=["your grip."], icon=("grip", 540, 880, 190),
        vo="Nobody checks your grip."),
   dict(type="stat", top="Every 5 kg less grip strength", count=16, fmt="+{:.0f}%", sub="risk of death", sub2="140,000 adults, 17 countries", icon=("grip", 540, 1060, 90),
        src="Leong et al., The Lancet 2015", label="The data",
        vo="In nearly a hundred and forty thousand adults, every five kilos less grip strength was linked to sixteen percent higher risk of death."),
   dict(type="text", head=["A stronger predictor", "*than blood pressure."], gold=["than blood pressure."], label="Cardiovascular death",
        src="Association, not cause (Leong et al., 2015)",
        vo="And it predicted cardiovascular death better than blood pressure. An association, not a cause. But a signal worth measuring."),
   dict(type="end", q="When did you last test your grip?", vo="When did you last test your grip?", caps=False),
 ], caption="Your doctor checks your blood pressure. Nobody checks your grip.\nIn ~140,000 adults in 17 countries, every 5 kg less grip strength was linked to 16% higher risk of death, and grip predicted cardiovascular death better than systolic blood pressure (Leong et al., 2015). An association, not proof.\nWhen did you last test your grip?\n#sumisura #gripstrength #strength #longevity #brussels"),

 dict(id="64_fit_vs_fat", acc=VO2, scenes=[
   dict(type="hook", head=["You lost the weight.", "Are you safe now?"], icon=("scale", 540, 880, 170),
        vo="You lost the weight. Are you safe now?"),
   dict(type="compare", top="Risk of death", bars=[("Fit, any weight", 1.0), ("Unfit, any weight", 2.0)], vals=["1×", "≈ 2×"],
        src="Barry et al., Prog Cardiovasc Dis 2014 (meta-analysis)", label="Fitness vs weight",
        vo="A meta-analysis compared fitness and body weight. Unfit people had about twice the risk of death, whatever their BMI."),
   dict(type="text", head=["Overweight but fit?", "*Similar risk", "*to normal weight and fit."], gold=["Similar risk"], icon=("gauge", 540, 1000, 130),
        vo="Overweight but fit? A similar risk to normal weight and fit."),
   dict(type="text", head=["The scale tells you one thing.", "*Fitness tells you more."], gold=["Fitness tells you more."], icon=("scale", 540, 900, 120),
        vo="The scale tells you one thing. Your fitness tells you more."),
   dict(type="end", q="What do you track: weight or fitness?", vo="What do you track? Weight, or fitness?", caps=False),
 ], caption="You lost the weight. Are you safe now?\nIn a meta-analysis, unfit people had about twice the risk of death regardless of BMI, while overweight-but-fit people had a similar risk to normal-weight-fit people (Barry et al., 2014).\nThe scale tells you one thing. Fitness tells you more.\nWeight or fitness: what do you track?\n#sumisura #vo2max #fitness #longevity #brussels"),

 dict(id="65_muscle_loss_per_decade", acc=MUS, scenes=[
   dict(type="hook", head=["You're losing muscle.", "Right now. Quietly."], icon=("muscle", 540, 900, 160),
        vo="You're losing muscle. Right now. Quietly."),
   dict(type="stat", top="After 30, per decade", count=1, fmt="3–8%", sub="of muscle mass, lost", sub2="and faster after 60", icon=("muscle", 540, 1080, 80, {"keep": .7}),
        src="Volpi et al., 2004", label="The data",
        vo="After thirty, most adults lose three to eight percent of their muscle mass every decade. After sixty, it goes faster."),
   dict(type="text", head=["You won't see it", "*on the scale."], gold=["on the scale."], icon=("scale", 540, 900, 130),
        vo="And you won't see it on the scale."),
   dict(type="text", head=["Strength training", "*fights it back."], gold=["fights it back."], icon=("muscle", 540, 900, 150), label="The counter",
        vo="Strength training is the best proven way to fight it. So we measure your muscle, and we build it."),
   dict(type="end", q="When did you last measure your muscle?", vo="When did you last measure your muscle?", caps=False),
 ], caption="You're losing muscle. Right now. Quietly.\nAfter 30, adults lose about 3–8% of muscle mass per decade, faster after 60 (Volpi et al., 2004). The scale won't show it.\nStrength training fights it back. Measure, then build.\nWhen did you last measure your muscle mass?\n#sumisura #strengthtraining #muscle #longevity #brussels"),
]
