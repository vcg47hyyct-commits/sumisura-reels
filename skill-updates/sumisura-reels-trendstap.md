# Update for the sumisura-reels skill: trend step

Two changes in claude.ai → Skills → sumisura-reels:

1. Replace the `description` in the header with the one below.
2. Paste the section "## Trend step" right after the "## Claims (hard rules)" section.

---

## 1. New description (header)

```
description: "Research what is trending on a health topic (last 30 days, hooks, angles), then edit Instagram reels and captions for the Sumisura brand account (@sumisura.brussels) using Sumisura's brand guidelines, logo and serious premium tone."
```

---

## 2. New section

```markdown
## Trend step (research first, then the reel)

Run this step before every **new** reel topic, and whenever Luca asks "what's trending", "trend", "idea for a reel" or gives only a topic.
Skip it when Luca delivers footage plus a fixed script and only wants the edit.

### 1. Pick the topic
- Link the topic to Sumisura: one of the four systems (Structure, Oxygen, Metabolic & Cellular, Nervous System) and an offer Luca has confirmed Sumisura provides. Never invent a service.
- If Luca gives no topic: scan 3–5 topics that fit the four systems and suggest the one with the most current interest.

### 2. Research the last 30 days
- If the `last30days` skill is available, run it on the topic for social signals (Reddit, X, TikTok, YouTube).
- Otherwise, or in addition, search the web for:
  - **News and launches** (last 30 days): new devices, campaigns, celebrity or athlete use.
  - **Research**: new studies, meta-analyses (use PubMed if connected). Note the study type and size.
  - **Social**: which formats and hooks get views and comments on this topic (TikTok, Instagram, YouTube Shorts).
  - **Skeptical coverage**: myths, criticism, regulator or safety warnings.
- Weigh sources: primary studies and serious media over vendor press releases and affiliate sites. Flag promotional sources as such.
- Always state the date of each finding; leave out anything older than 30 days unless it is background.

### 3. Analyse the hooks
- List the 5–8 most-used hooks or formats around the topic (e.g. "I tried it for 30 days", "hype vs. evidence", "doctor reacts", "3 mistakes").
- Point out the **gap**: what the loud content is missing and where Sumisura's precise, evidence-based angle wins (nuance, real dose or protocol, elite-sport method, myth correction).
- Translate the hooks into Sumisura tone: no clickbait, no hype words, short statements. Examples of patterns:
  - "Most people get [X] wrong."
  - "What the research actually says about [X]."
  - "Not a gimmick. Not a miracle."
  - "Elite athletes use [X]. Here's why."
  - "[X]: hype or adaptation?"

### 4. Claims filter
- Give every claim an evidence level: **strong / moderate / weak / none**.
- Only strong or moderate claims go on screen, phrased carefully ("studies suggest", "may support"). Weak or none → leave out, or use only as a myth to correct.
- Every claim about Sumisura itself (protocols, numbers, results) must be confirmed by Luca. Ask, don't guess.
- The hard rules in "Claims" always apply (no cures, no detox, no invented numbers).

### 5. Trend brief (deliverable before the edit)
Give a short brief in chat:
- **What's trending** (3–5 bullets, with date and source)
- **3 angles**, each with: on-screen hook (max 6 words), why now, evidence level, fit with the four systems, suggested series (e.g. "THE [X] ADAPTATION")
- **Recommendation**: the strongest angle + which claims Luca still needs to confirm
- **Sources** as links

Then ask Luca: which angle, and are the claims correct? Only when Luca asks for "full auto" do you go straight to the edit with the recommended angle; list the unconfirmed claims at the top in that case.

### 6. From brief to reel
- Build the reel according to "Reel format" below. The hook from the brief is the first on-screen line (first second).
- When making several versions: give each version a different hook from the brief (A/B trial reels).
- Caption: echo the hook, one line of context from the research, brand line, one question that invites comments, 3–5 hashtags (#sumisura #brussels #toutaxis + topic; add one current topic hashtag if it is relevant and not spam).

### 7. Log
- Save the trend brief as `trends/YYYY-MM-DD-<topic>.md` in the sumisura-reels repo (or next to the footage in Luca's folder), so topics and hooks don't repeat and results can be compared later with `trial-reel-analysis`.
```

---

## Optional: automation

If you want this to run on its own, a recurring scheduled task can do it, e.g.
every Monday morning: "Run the trend step of sumisura-reels: scan 3–5 topics that fit
the four systems, deliver a trend brief with 3 angles and hooks, and save it in trends/."
Then you only have to pick an angle and deliver footage.
