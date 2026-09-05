# Proof Slides — traction, market sizing, projections, the ask

Use for relevant metrics, market, financials, and ask slides. Numeric presentation/market thresholds below are corpus heuristics, not eligibility gates; verify dated market claims and disclose assumptions.

The proof layer of the deck: every number dated, sourced, with time context. Stage bars and round-size norms are vc-strategy territory (see `../../vc-strategy/references/stage-benchmarks.md` when installed; otherwise the calibration table below) — this file governs how proof is *rendered*.

## Declare the stage before the numbers

Round labels are a bad approximation of company stage. Use a16z's maturity ladder (Martin Casado, 2018) and present only that stage's evidence class:

- **Team** (pre-product-in-market): long-form founder/market fit; 15–20 min of a 50-min pitch on team is fine.
- **Product**: prove PMF with real market signal — production deployments, engagements with real decision-makers, internal projects mirroring the solution. "Potential customer quotes are effectively useless." Don't oversell exploratory PoCs, OEM talks, or one-offs.
- **Repeatable Sale**: similar buyer + similar use case + growing pipeline (investors call customers to check sales-cycle duration vs pent-up demand).
- **Unit Economics**: ACV, CAC, NDR; enterprise gross margin gets diligenced as *actual* effort to sell and implement.

The governing failure is **signalling more maturity than the evidence justifies** — not being early. This ladder is the best frame for devtools/infra founders because it works pre-monetization.

## Traction slide checklist

1. Stage declared explicitly (ladder stage or pre-seed/seed/A).
2. One headline metric on top: `$2.4M ARR | 18% MoM | 127% NRR`.
3. 2–3 supporting quality metrics — **4–6 numbers total, maximum**; ten metrics reads as hiding weakness behind complexity.
4. A trajectory chart: growth over time (y at zero, consistent intervals, annotated inflections); waterfall for the revenue bridge (new / expansion / churn).
5. **Incremental beside cumulative** — net new ARR beside ARR, new logos/month beside total logos. Net new ARR (new + upsell − downsell − churn) is what separates linear from J-curve: "$100K net new last quarter, $300K this quarter" is a fundable sentence at seed (Molly Alter, Index, 2022).
6. Time context on every number: start point, current point, elapsed months. "Trend lines, not points" (Dreamit).
7. Benchmark comparison where the company beats it ("DAU/MAU 58% vs 20% category average").
8. One acknowledged weakness with the fix and result ("churn 8% → 4% after X") — diligence will find it anyway.
9. Revenue composition split honestly: true ARR vs services vs transaction volume ("no need to force everything into an ARR framework if it's not really ARR" — Alter). Call a $5M/5-yr TCV "a $1M ARR contract with upside."
10. Metric class matched to business model (table below) — no DAU for B2B SaaS.
11. The handoff sentence: traction → what capital accelerates → resulting milestone ("With $2.4M ARR growing 18% monthly, we've proven PMF; a $12M Series A funds 25 reps, reaching $15M ARR in 18 months").
12. Retention shown as the **spread**, not one level: logo retention vs gross dollar retention vs net dollar retention — GDR > logo means big contracts stick; high NDR over low GDR means a subset upsells hard while the rest lack PMF (Alter: GDR is "criminally underrated"). Cohort tables only when a dated product change made later cohorts stack better.
13. Command of the numbers: be ready to explain *what drove* every number — Index passed on a company at $10M ARR tripling YoY because the team couldn't (Alter, 2022).

## Pre-revenue proof stack (strongest → weakest)

1. Paid pilots — money changed hands.
2. Production deployments with real decision-makers (a16z's bar).
3. Design partners — named counterparties, defined success criteria.
4. Detailed LOIs — scope and price specified; the more specific, the more valuable: "a good LOI literally gives you a roadmap for what you need to build to generate revenue" (Jared Friedman, YC). Hard-tech variant of free pre-revenue proof: named advisors, credible simulations, physical/clickable models that generate documented customer interest.
5. Confirmed willingness to pay at your price point.
6. Qualified, segmented waitlist (raw signups are discounted).
7. Engagement depth on a free/OSS product — weekly active usage, workflow integration, unsolicited integrations, community contributions.
8. Beta feedback / testimonials tied to the claimed pain.
9. Discovery-interview counts with a hit rate ("65 interviews, 89% confirmed").
10. Smoke-test / ad conversion data.

Absence of a traction slide at pre-seed damages more than modesty does — LOIs, pipeline, and beta feedback count (DocSend: only ~11% of funded pre-seeds were at pure idea stage, 2021).

## Metric sets by business model

| Model | North Star | Quality metrics | Notes |
|---|---|---|---|
| B2B SaaS | MRR/ARR | MoM growth, NRR + GDR + logo retention, LTV:CAC, CAC payback, gross margin | monthly logo churn >5% invalidates the MRR chart |
| Usage-based | Consumption revenue + NRR | cohort expansion, gross margin (compute COGS), % revenue from top accounts | split true ARR from usage revenue |
| Open-source / devtools | usage depth (active projects, workloads, API calls) + conversion to paid | retention, in-account expansion, community signals (contributors, unsolicited integrations) | usage evidence substitutes for revenue pre-monetization; the bar is production deployments, not GitHub stars |
| Marketplace | GMV | take rate (stable/rising), liquidity (time-to-fill), two-sided balance | lopsided side-growth reads as future collapse |
| Consumer | DAU/MAU matched to use case | retention curves, engagement depth, K-factor, ARPU | needs ≈5× the SaaS scale for the same round |
| Enterprise | ACV | ARR ÷ ACV ≥80%, sales-cycle direction, pipeline coverage | present TCV as annualized ARR with upside |

North Star discipline: one number that best represents core value delivered + 2–3 that prove its health; choosing it is a strategic declaration of what demand looks like. Pre-PMF, the founder defines the metrics — "nobody knows your business better than you," especially for unusual/infra businesses (Wayne Hu, SignalFire, 2021). Find the one metric with an unfair advantage and name it (Typeform: design virality; Qualtrics: free-to-students).

## Market-sizing credibility test (any failure makes the slide a liability)

- [ ] Bottom-up: customer count × **your** price — not a research-firm headline.
- [ ] Customer count has a citable, verifiable source (Census/BLS/LinkedIn/industry association > Gartner/CB Insights > Statista/Google).
- [ ] Price de-risked by real selling — not a competitor's price ("if the competitor charges $5,000/mo and you'll charge a tenth, your TAM is a tenth" — Steve Barsh, Dreamit).
- [ ] Segment/geography/ICP narrowing explicit; assumptions footnoted on the slide ("show your work").
- [ ] Capture claim ≤ ~20% for horizontal SaaS (Salesforce's ceiling in core CRM — CRV, 2026), or justified by market structure (fragmented marketplace leaders can take 80%+ — Wayne Hu, 2021).
- [ ] Top-down shown only as a sanity check, reconciled with bottom-up before either enters the deck.
- [ ] TAM is *your* market — not the size of the problem ("you make a ski goggle; $3.3B ski-resort revenue is the resorts' TAM" — Barsh), not the customers' industry.
- [ ] TAM ≥ $1B with a credible path to $100M revenue (venture arithmetic — CRV, 2026).
- [ ] Market growth rate stated, mapped to the why-now.
- [ ] One business model, one market — stacked TAMs from adjacent models read as lack of focus (Ed Kang, 2022).
- [ ] Expansion map: how the wedge grows into adjacencies (Brex/Ramp: interchange → expense management → banking — SignalFire, 2021).

Method options: standard bottom-up chain (define customer → count with citable source → × your price = SOM → SAM → TAM); **greenfield sizing** for net-new categories (comparable segments + behavior trends + own early traction — Pitchili, 2025); Wayne Hu's correction — investors actually price *how valuable the business can be* (revenue × industry multiple), and markets get under-sized by ignoring adjacencies, compounding growth ("skate to where the puck is going"), market expansion (Uber halved fares and ate car ownership — $750B, not the $100B taxi market), and new-market creation. "Size isn't everything; the market structure is potentially even more important — is it fragmented, underserved, inefficient?"

## Financial projections

- **3 years standard at seed, 5 at Series A**; Year 1 detailed, Year 3 directional, "nobody believes Year 5 anyway" (preuve.ai, 2026). Dynamic model so assumptions can be flexed live in diligence (Kruze).
- **Skip the 5-year model at pre-seed** — replace with a unit-economics projection ("at $29/mo with 2% monthly churn, 1,000 customers = $348K ARR").
- Build **drivers → conversion rates → costs → revenue**, never revenue-goal-backwards ("you do marketing to get customers and revenue — not the other way around" — Slidebean, 2024, on hockey-stick red flags). Never let the hockey stick begin exactly when the round closes (CRV, 2026).
- Sourced assumptions: Glassdoor for salaries, observed conversion for revenue; include a sensitivity case ("if we grow 30% slower, here's what changes"). What's tested is whether the founder can build a *credible* forecast — everyone knows the numbers are wrong.
- Later-stage investors rebuild the metrics into their own model — interconnection between metrics matters more than any single number (Alter, 2022).

## Ask + use-of-funds checklist

- [ ] Amount stated plainly. (The amount and milestone plan come from vc-strategy's round design — render them.)
- [ ] Allocation at percentage level ("60% product, 25% GTM, 15% ops").
- [ ] The milestone it buys, with a number and a date.
- [ ] Runway produced: 18–24 months, next raise starting with ≥6 months left.
- [ ] Explicit bridge to the next round's bar ("this reaches $1.5M ARR — the Series A door").
- [ ] 15–25% contingency baked in (not shown, defensible if probed — Allied VC, 2025).
- [ ] Non-capital asks named (intros, design partners, hires).
- [ ] Every line traceable to a bottom-up budget openable on request.

## Slide-calibration numbers (fallback table — vintage marked, verify before quoting)

- Seed growth read: 15–20%+ MoM strong, >25% exceptional (CRV/wiki, 2025–26); YC's "10%/week sustained is interesting."
- Best-in-class: $1M ARR within 12 months of launch very good, 9 months excellent; then triple-triple-double-double-double (Index, 2022).
- Traction trend needs ≥4–6 months of history to be believable (YC Series A guide); cohort analysis needs ≥12 months (Jarvis).
- Series A ARR bar is a **range, not a number** — $1M–$2M clears the door (startups.com 2025), $2M–$5M wins a competitive process (CRV 2026); the "$1M ARR rule" is explicitly obsolete. Teach the range and the reason.
- Burn multiple: ~1× very good; 1.5–2.5× normal at A; >3× yellow flag (Index 2022; startups.com 2025).
- Known corpus limitation: no dedicated evidence on OSS-metric proof (stars/downloads as traction) — guidance above is inference from Casado's ladder and usage-depth principles; say so when asked for citations.
