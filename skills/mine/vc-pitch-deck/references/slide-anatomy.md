# Slide Anatomy — craft rules and per-slide requirements

Apply the affected slide type. Word/visual/number counts guide legibility; they are not universal failures. Preserve clear, verifiable meaning when the content needs a different shape.

Universal craft rules first; then every standard slide. Attributions dated where the claim is time-sensitive.

## Craft rules (every slide)

- **Headline = the takeaway, never the category.** "Market size" says nothing; "$10bn market with an immediate $2bn SAM" leaves something concrete (NFX). A rubbish headline written in five seconds still beats a placeholder label (Jarvis).
- **One point per slide.** If two ideas compete, split the slide (Kevin Hale; Waveup). "If you're trying to make more than one point per slide, your slide is too complicated" (YC Series A guide).
- **≤30 words of body + one visual** (preuve.ai 2026; Waveup 2026). Visual hierarchy: headline → key signal → supporting context — investors scan, they don't read.
- **Clarity over beauty.** Simple and bare-bones; whitespace "10×es the appearance of any deck"; body font never larger than the header font (Jarvis). "I hate when founders get designers to make fancy shizzle. It always gets worse" (Jarvis). Avoid diagrams that don't illustrate the point — "diagrams are like little mazes for ideas" (Hale, on Hick's Law).
- **Charts:** understandable at first glance, single axis, y-axis starts at zero, caption states the conclusion. Cumulative charts and double-axis charts read as concealment — "almost every time I've seen cumulative numbers in a Series A deck, it's because founders are hiding their monthly numbers" (YC Series A guide). Only use a graph that goes up and to the right, and include how long it took — "without the time, I'm not impressed" (Seibel).
- **A number in every sentence, preferably two** (NFX). Name units exactly: users = MAU or DAU? revenue = gross or net? (YC Series A guide).
- **Forwardability:** every slide must survive being forwarded to a partner who has never met the founder, with zero verbal context (Garry Tan: an investor who doesn't understand "won't even email to ask"). Anything unforwardable belongs in conversation or the data room — assume no NDA, assume circulation.
- **Identify the hero facts** — the headline numbers the champion will repeat when pitching the company to their partners (YC Series A guide).
- **In presented decks:** text near the top of the slide (readable from the back); no animations, transitions, memes, per-slide branding, caveats, or walls of text (Hale). One deliberate exception: overwhelm as the point (Magic's grid of every on-demand service it abstracts).
- **Screenshots:** in a presented/demo-day slide, a bulleted list of steps beats a screenshot (Hale — illegible at distance); in a reading deck, screenshots and product evidence beat diagrams (Indy Pixels, 2026). Route by artifact.

## Title / cover

Company name + **what it does in one concrete, layperson sentence** ("we build and operate robot greenhouses", not "reinventing agriculture"). Never leave slide 1 without the reader knowing what the company does (Seibel; Garry Tan: "we're on slide 11 and still had to do a lot of sleuthing"). Tagline ≤7 words (Slidebean).

## Problem

State the problem as a data-backed headline, never the word "Problem" ("Everyone uses email, but it sucks for teams" — Jarvis). 2–3 problem slides maximum (Slidebean's Brex teardown: two of three problem slides muddled = anti-pattern). Qualify it with the Four U's — unworkable, unavoidable, urgent, underserved (Underscore VC). Aim for nodding momentum: the pain articulated so precisely the investor nods before the solution appears. In a presented pitch, land the pain in under a minute — "you meet the villain first" (Griffit).

## Solution & product

One use case solved 10× better, not a feature tour (Waveup 2026). Lead with WHAT, not why or how (Hale). Feature-detail slides with no customer context are appendix slides (Garry Tan). For the product: engineer one "wow moment"; product triad — core workflow, moment of delight, reason they return (Indy Pixels, 2026).

## Demo

Shot from a first-time user's perspective, not the founder's power-user flow (Griffit). In-room: live demo beats video beats screenshots; have the video fallback ready. Devtools: the demo can carry proof weight the traction slide can't yet — place it early.

## Why now

The inflection-point slide — for AI/deep tech "the strongest slide in the deck" (Waveup 2026). Name the axis that changed (customer behaviour, competition, feasibility, cost) with an external, checkable data point. Answer both "why this year" and "why this decade" (Oren Jacob). A missing why-now beats a fake one — "if you don't have a good reason for timing, just cut the slide; don't look stupid" (50Folds).

## Market

Bottom-up only: number of *your* customers × *your* de-risked price, narrowed by segment/geography/ICP; show the math on the slide ("how you calculate the number is what's important, not the number" — Seibel). Full method and credibility test: `proof-slides.md`. A credible $2B TAM beats an unsourced $50B TAM (preuve.ai 2026). Go global if the US opportunity is under $2B (NFX).

## Competition

Skip the 2×2 with the magic empty top-right — investors read it as a tell (preuve.ai 2026; Dreamit: 50% of founders arrive with a Magic Quadrant). Use Dreamit's **Power Grid**: company in the leftmost column, 3 best-known competitors next (most-asked-about first), 5–10 benefit rows in customer-priority order, quantified ("30% faster", not "much faster"), checkmark/number in your cell, blank in theirs; benefits may be product, business-model, distribution, or GTM. Name what competitors do *well*, then position in the gap (Front's Series A competition slide — the most-praised slide in the corpus). Acceptance test: show the slide to the competitors; they should agree with it (Jarvis). "We have no competitors" = "I didn't do the research" — doing nothing, spreadsheets, and consultants are real alternatives. Never disparage a competitor aloud: someone in the room may be their investor (Griffit).

## Business model & GTM

Business model → path to category leadership, with the unit economics that make a dollar in produce more than a dollar out. GTM: **one core growth strategy that is already working** (two at most), with its numbers — a list of channels reads as "no strategy" ("90% of pitch decks get this wrong" — Slidebean, 2024).

## Team

Titles + **who writes code** — "if I'm trusting the CEO with money, who am I trusting?" (Seibel). One specific accomplishment each ("built flight software for the Mars rover" — the founder who left that off was making a mistake); logos, degrees, years — quantified, no advisor filler, no 12-employee headshot walls (YC Series A guide). Weave in how the founders personally experienced the problem (Seibel). Position: end of deck by default; slide 2–3 only when the team is the comparative advantage — prior exit >$100M or one of few people equipped to build this (YC Series A guide; Slidebean). **Leave existing-investor logos off** — a listed fund invites "are they leading?" where yes means why pitch me and no is a bad signal (YC Series A guide). Capital-efficiency proof lives well here ("$1M spent to reach $1.2M ARR").

## Traction

Full spec in `proof-slides.md` — headline metric, 4–6 numbers max, trend lines not points, incremental beside cumulative, one acknowledged weakness with the fix. A bad traction slide is worse than no traction slide (Seibel).

## The ask

~70% of pitches never actually ask for money (Seibel, 2023) — the ask is the climax of the deck. Amount + allocation + **the milestone it buys in 18–24 months** — milestones, not headcount: "hiring is a means to an end; the end is revenue and usage" (Seibel). "We'll use it to grow" is not a plan (preuve.ai 2026). The amount and milestone plan are vc-strategy outputs — render them, don't derive them here.

## Appendix

Start with 2 slides, reach ≥10 by mid-process (NFX): one slide per predictable objection, financial projections and use-of-funds detail, cohort tables, unit-economics derivations, security/compliance, architecture deep-dives, feature detail. Anything that made a first-pass reader slow down without being load-bearing for the story moves here.
