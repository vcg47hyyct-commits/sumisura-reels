from specs2 import hook, text, stat, bars, grid, HEAT, OXY, CELL, NS, COLD
import specs2
_old = {r["id"]: r for r in specs2.REELS}

REELS = [
# ---------------- HEAT / SAUNA CYCLING ----------------
dict(id="41_heat_arteries_bp", accent="heat", series=HEAT, key="A", scenes=[
  hook(["8 weeks of heat.", "Your arteries changed."], ["Eight weeks of heat. Look what happened to the arteries."], ("heartline", 540, 900, 130)),
  text(["Sedentary adults.", "*Hot-water immersion, 8 weeks."], ["Sedentary adults sat in hot water, regularly, for eight weeks. No training."],
       ("drop", 540, 880, 160), label="THE STUDY", src="Brunt et al., J Physiol 2016"),
  bars(["Artery function (FMD)."], [("Before", 5.6, "5.6%", True), ("After 8 weeks", 10.9, "10.9%", True)],
       ["Artery function nearly doubled, from 5.6 to 10.9 percent."], src="Brunt et al., J Physiol 2016"),
  bars(["Mean blood pressure", "*in mmHg."], [("Before", 83, "83", True), ("After 8 weeks", 78, "78", True)],
       ["Mean arterial pressure dropped from 83 to 78."], src="Brunt et al., J Physiol 2016"),
  text(["Heat as an adjunct.", "*Not a replacement."], ["Heat as an extra tool for your vessels. Not a replacement for training."], ("sun", 540, 880, 150)),
]),
dict(id="42_heat_38_5_core", accent="heat", series=HEAT, key="C", scenes=[
  hook(["Hotter isn't", "better."], ["Hotter isn't better. There's a ceiling."], ("sun", 540, 880, 170)),
  stat(["The target:", "core temperature."], "{}°C", ["For heat adaptation, the target is a core temperature of about 38.5 degrees."], count=38.5, dec=1, src="Gibson et al., Temperature 2020"),
  text(["About 30 minutes", "*to get there."], ["About thirty minutes of work to get there. Then you hold it."], ("bike", 540, 900, 200), src="Gibson et al., Temperature 2020"),
  text(["Above 38.5°C:", "*no extra benefit."], ["Going above it added no extra benefit. Just extra strain."], ("sun", 540, 880, 150), src="Gibson et al., Temperature 2020"),
  text(["Dose it.", "*Don't max it."], ["So we dose heat. We don't max it."], ("heartline", 540, 880, 120)),
]),
dict(id="43_heat_fades_daily", accent="heat", series=HEAT, key="E", scenes=[
  hook(["Heat adaptation", "fades. Fast."], ["Heat adaptation fades. And it fades fast."], ("sun", 540, 880, 170)),
  stat(["Lost per day", "without heat."], "~{}%", ["Without exposure, adaptations decay by roughly 2.5 percent per day."], count=2.5, dec=1, src="Gibson et al., Temperature 2020"),
  text(["Frequency", "*beats intensity."], ["Frequency beats intensity. Daily or near-daily sessions build it."], ("bike", 540, 900, 200), src="Gibson et al., Temperature 2020"),
  text(["One session a week", "*to keep it."], ["After that, one session a week helps you keep what you built."], ("sun", 540, 880, 150)),
]),
dict(id="44_heat_not_mitochondria", accent="heat", series=HEAT, key="G", scenes=[
  hook(["What heat", "does NOT do."], ["Here's what heat does not do."], ("mito", 540, 880, 170)),
  text(["8 weeks of local heat.", "*90 minutes a day."], ["Researchers heated one thigh, ninety minutes a day, for eight weeks."], ("sun", 540, 880, 150),
       label="THE STUDY", src="Kim et al., J Appl Physiol 2020"),
  text(["Mitochondrial content:", "*no change."], ["Mitochondrial content didn't change."], ("mito", 540, 880, 170), src="Kim et al., J Appl Physiol 2020"),
  text(["Want more", "*mitochondria? Train."], ["For that, you need training. Zone 2 and intervals."], ("bike", 540, 900, 200)),
  text(["Honest science.", "*Every tool its job."], ["Honest science. Every tool has its own job."], ("heartline", 540, 880, 120)),
]),
dict(id="45_heat_thigh_torque", accent="heat", series=HEAT, key="D", scenes=[
  hook(["One thigh heated.", "One thigh not."], ["One thigh heated. The other one not. Eight weeks later."], ("sun", 540, 880, 170)),
  text(["90 min a day.", "*5 days a week. 8 weeks."], ["Ninety minutes a day, five days a week, for eight weeks."], ("sun", 540, 880, 150),
       label="THE STUDY", src="Kim et al., J Appl Physiol 2020"),
  bars(["Peak torque gain."], [("Heated thigh", 7.8, "+7.8 Nm", True), ("Other thigh", 1.8, "+1.8 Nm", True)],
       ["Peak torque rose by 7.8 newton metres in the heated thigh. Only 1.8 in the other."], src="Kim et al., J Appl Physiol 2020"),
  text(["Heat adds a signal.", "*To muscle, too."], ["Heat adds a signal. To muscle, too."], ("sun", 540, 880, 150)),
]),
dict(id="46_heat_muscle_fibres", accent="heat", series=HEAT, key="F", scenes=[
  hook(["Bigger muscle fibres.", "No training."], ["Bigger muscle fibres. Without any training."], ("sun", 540, 880, 170)),
  text(["10 weeks of heat", "*on the thigh."], ["Ten weeks of heat on the front of the thigh. No training."], ("sun", 540, 880, 150),
       label="THE STUDY", src="Goto et al., Eur J Appl Physiol 2011"),
  stat(["Muscle fibre size."], "+{}%", ["Muscle fibre cross-sectional area rose by 8.3 percent."], count=8.3, dec=1, src="Goto et al., Eur J Appl Physiol 2011"),
  text(["Not instead of lifting.", "*On top of it."], ["Not instead of lifting. On top of it."], ("sun", 540, 880, 150)),
]),
dict(id="47_heat_time_to_exhaustion", accent="heat", series=HEAT, key="A", scenes=[
  hook(["3 weeks of sauna.", "+32% endurance."], ["Three weeks of sauna. Thirty-two percent more endurance."], ("runner", 540, 900, 200)),
  text(["Sauna right after", "*every run."], ["Runners took a sauna straight after training, for three weeks."], ("sun", 540, 880, 150),
       label="THE STUDY", src="Scoon et al., J Sci Med Sport 2007"),
  stat(["Time to exhaustion."], "+{}%", ["Their time to exhaustion rose by 32 percent."], count=32, src="Scoon et al., J Sci Med Sport 2007"),
  text(["In a race:", "*about 1.9% faster."], ["Translated to a race: about 1.9 percent faster."], ("runner", 540, 900, 200), src="Scoon et al., J Sci Med Sport 2007"),
]),
dict(id="48_heat_sleep_safety", accent="heat", series=HEAT, key="C", scenes=[
  hook(["Slept badly?", "Skip the heat."], ["Slept badly? Think twice before a heavy heat session."], ("bed", 540, 900, 160)),
  text(["Sleep loss", "*impairs thermoregulation."], ["Short-term sleep loss impairs how your body handles heat."], ("bed", 540, 900, 160), src="Keramidas & Botonis, Exp Physiol 2021"),
  text(["So we check", "*readiness first."], ["That's why we check readiness before Sauna Cycling."], ("heartline", 540, 880, 120)),
  text(["Bad night?", "*Lower dose, or postpone."], ["Bad night? Lower the dose, or postpone."], ("sun", 540, 880, 150)),
]),
# ---------------- IHHT ----------------
dict(id="49_ihht_cardiac_patients", accent="oxygen", series=OXY, key="E", scenes=[
  hook(["Can't train hard?", "Oxygen can still help."], ["Can't train hard? Low oxygen might still be a stimulus."], ("o2", 540, 900, 160)),
  text(["Older cardiac patients.", "*5 weeks of IHHT, at rest."], ["Older cardiac outpatients did five weeks of IHHT, lying at rest."], ("o2", 540, 900, 160),
       label="THE STUDY", src="Glazachev et al., Clin Cardiol 2018"),
  text(["Fitness improved", "*from baseline."], ["Their cardiorespiratory fitness improved significantly from baseline."], ("heartline", 540, 880, 120), src="Glazachev et al., Clin Cardiol 2018"),
  text(["For low tolerance.", "*Not a shortcut."], ["A low-strain stimulus for people who can't train hard. Not a shortcut for those who can."], ("o2", 540, 900, 160)),
]),
dict(id="50_ihht_no_multiplier", accent="oxygen", series=OXY, key="C", scenes=[
  hook(["Training + IHHT.", "Better than training?"], ["Training plus IHHT. Is it better than training alone?"], ("o2", 540, 900, 160)),
  text(["Older patients.", "*Training, with or without IHHT."], ["Older patients trained, with or without IHHT added."], ("runner", 540, 900, 200),
       label="THE STUDY", src="Bayer et al., BMC Geriatr 2019"),
  text(["No extra gain", "*from IHHT."], ["Adding IHHT gave no extra improvement in mobility or perceived health."], ("o2", 540, 900, 160), src="Bayer et al., BMC Geriatr 2019"),
  text(["We tell you that.", "*Upfront."], ["So we tell you that upfront. Who it's for, and who it isn't."], ("heartline", 540, 880, 120)),
]),
# ---------------- BREATHING ----------------
dict(id="51_breathing_slow_defined", accent="breath", series=NS, key="F", scenes=[
  hook(["How fast", "do you breathe?"], ["How fast do you breathe right now?"], ("breath", 540, 900, 170)),
  bars(["Breaths per minute."], [("Normal", 20, "10–20", True), ("Slow breathing", 10, "4–10", True)],
       ["Normal is ten to twenty breaths a minute. Slow breathing is four to ten."], src="Russo et al., Breathe 2017"),
  text(["Slow breathing", "*shifts many systems."], ["Slow breathing affects your lungs, your heart and your nervous system."], ("breath", 540, 900, 170), src="Russo et al., Breathe 2017"),
  text(["Count yours.", "*One minute."], ["Count yours for one minute. That's your baseline."], ("heartline", 540, 880, 120)),
]),
dict(id="52_breathwork_stressor", accent="breath", series=NS, key="A", scenes=[
  hook(["Fast breathwork", "isn't relaxation."], ["Fast, forced breathwork is not relaxation."], ("breath", 540, 900, 170)),
  text(["Over-breathing", "*lowers your CO2."], ["Breathing beyond what you need lowers carbon dioxide in your blood."], ("breath", 540, 900, 170)),
  text(["Less brain blood flow.", "*More stress drive."], ["That narrows blood vessels in the brain and raises your stress drive."], ("heartline", 540, 880, 120)),
  text(["It's a stressor.", "*Program it like one."], ["It's a stressor. Program it like one. Not in your recovery slot."], ("breath", 540, 900, 170)),
]),
dict(id="53_breathhold_water_safety", accent="cold", series=COLD, key="G", scenes=[
  hook(["Breath holds", "and cold water."], ["Breath holds and cold water. Never together."], ("snowflake", 540, 880, 170)),
  text(["Hyperventilate,", "*then hold?"], ["Hyperventilating before a breath hold delays the urge to breathe."], ("breath", 540, 900, 170)),
  text(["Real risk", "*of blacking out."], ["That carries a real risk of blacking out."], ("heartline", 540, 880, 120)),
  text(["Never in water.", "*Never alone."], ["Never in water. Never unsupervised. Never with cold immersion."], ("snowflake", 540, 880, 150)),
]),
# ---------------- VO2MAX / ZONE 2 ----------------
dict(id="54_zone2_watch_wrong", accent="vo2", series=OXY, key="D", scenes=[
  hook(["Your watch's zone 2", "might be wrong."], ["Your watch says zone 2. It might be wrong."], ("heartline", 540, 900, 130)),
  text(["Real zone 2:", "*just below threshold 1."], ["Experts place zone 2 just below your first lactate or ventilatory threshold."], ("runner", 540, 900, 200),
       label="EXPERT CONSENSUS", src="Sitko et al., IJSPP 2025"),
  bars(["Blood lactate."], [("Zone 2", 2, "1–2 mmol/L", True), ("Often mistaken", 4, "3.5–4.5", True)],
       ["Lactate stays around one to two. Many people train at the second threshold and call it easy."], src="Sitko et al., IJSPP 2025"),
  text(["Test it.", "*Don't guess it."], ["So we test your real threshold. Not an age formula."], ("heartline", 540, 880, 120)),
]),
dict(id="55_zone2_not_everything", accent="vo2", series=OXY, key="F", scenes=[
  hook(["Zone 2", "isn't everything."], ["Zone 2 is great. But it isn't everything."], ("bike", 540, 900, 200)),
  text(["Zone 2", "*builds the base."], ["Zone 2 builds the base: your heart's stroke volume and your aerobic engine."], ("heartline", 540, 880, 120), src="Sitko et al., IJSPP 2025"),
  text(["Intensity", "*raises the ceiling."], ["Intervals and threshold work raise the ceiling of your VO2max."], ("runner", 540, 900, 200)),
  text(["The mix", "*is the prescription."], ["Most of your time easy, some of it hard. The mix is the prescription."], ("bike", 540, 900, 200)),
]),
dict(id="56_vo2_vital_sign", accent="vo2", series=OXY, key="A", scenes=[
  hook(["Stronger predictor", "than smoking."], ["A stronger predictor of death than smoking."], ("heartline", 540, 900, 130)),
  text(["Fitness is", "*a clinical vital sign."], ["The American Heart Association calls fitness a clinical vital sign."], ("heartline", 540, 880, 120),
       label="AHA STATEMENT", src="Ross et al., Circulation 2016"),
  text(["Stronger than smoking,", "*blood pressure, cholesterol."], ["It predicts mortality more strongly than smoking, high blood pressure, high cholesterol or type 2 diabetes."],
       ("heartline", 540, 880, 120), src="Ross et al., Circulation 2016"),
  text(["Yet rarely measured.", "*We measure it."], ["Yet it's rarely measured. We measure it."], ("runner", 540, 900, 200)),
]),
dict(id="57_vo2_first_steps", accent="vo2", series=OXY, key="G", scenes=[
  hook(["The least fit", "gain the most."], ["If you're the least fit, you gain the most."], ("runner", 540, 900, 200)),
  stat(["Of the drop in", "heart deaths..."], ">{}%", ["More than half of the drop in cardiovascular deaths comes from a very modest increase in fitness."],
       count=50, label="FROM A MODEST GAIN", src="Ross et al., Circulation 2016"),
  text(["First steps", "*matter most."], ["The first steps matter most."], ("runner", 540, 900, 200)),
  text(["Start with volume.", "*Then intensity."], ["Start with volume and consistency. Intensity comes later."], ("bike", 540, 900, 200)),
]),
# ---------------- re-renders in the faster voice ----------------
dict(_old["12_redlight_wavelengths"], id="58_redlight_wavelengths"),
dict(_old["15_shiftwave_pressure_breath_sound"], id="59_shiftwave_pressure_breath_sound"),
dict(_old["17_vo2max_bed_rest"], id="60_vo2max_bed_rest"),
]
