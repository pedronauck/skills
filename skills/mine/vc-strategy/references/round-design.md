# Round Design — when to raise, how much, at what price

Use the worksheet when round sizing is in scope. Milestone/scenario counts and percentage convergence are heuristics; explain divergent assumptions rather than forcing estimates to agree.

Sizing, timing, and valuation methods. Current-market numbers live in `stage-benchmarks.md`; this file carries the methods.

## Raise-now-or-wait readiness test

1. **Runway** — ≥6 months of cash *after* accounting for a 3–6-month process? Runway is negotiating leverage; below that the raise starts from weakness (Allied VC; a16z).
2. **Milestone alignment** — the value-inflection point this money buys, named in a metric an investor recognizes. "18 months of runway" fails: **"Time is not a fundable milestone. Investors want to buy learning. They want to buy goals"** (Dreamit).
3. **Next-round clearance** — at the intended price, is a 2–3× step-up raiseable in 18–24 months? If not, the price is wrong or the raise is early (Lemkin ⅓ rule below).
4. **Step, not slope** — has something new been unlocked or de-risked since the last price, or is it just more of the same? (Hustle Fund staircase: 10 SMB customers → 20 SMB customers is the same step; 10 SMB + 1 enterprise at 10× ACV is a new step at identical revenue, because it proves a new motion.)
5. **Demand** — enough investor interest to create competition? In non-competitive rounds investors price from their own check size and ownership target, largely independent of performance (Forum Ventures, 2024) — the fix for an arbitrary-feeling valuation is more demand, not a better deck.
6. **Preparation** — deck, 24-month monthly model, data room, and cap-table model ready to survive diligence.
7. **Market realism** — plan as if in the 39% that take 3+ years seed→A (Carta, Oct 2025), not the 15% that make it in ≤12 months.
8. **Fundraising-mode discipline** (Paul Graham): be in fundraising mode or out of it. Outside the mode, take only no-convincing, no-negotiation money; "one meeting with some partners" *is* fundraising — decline or enter the mode.

## Round-sizing worksheet

1. Name **3–5 measurable go/no-go milestones for the next round** — Underscore's four axes: Team / Market / Product / GTM ("$1M ARR is a *result*, not the bar" — the bar is minimum viable segment, GTM repeatability beyond outlier logos, land-and-expand with rising dollar retention, CAC payback trending to 12 months). For heavy-build products, make the milestone ladder's steps maniacally small — the failure mode is a step too large to fundraise past (Jared Friedman, YC).
2. Phase the milestones month by month over 12–18 months (24–36 in the current market).
3. Build bottom-up monthly burn: headcount (salaries are 60–70% of an early budget; load gross +25–35% for payroll tax/benefits; founder salary $50–75K signals capital efficiency; SV engineer ≈ $15K/month all-in), infra, tools, legal, marketing.
4. Multiply by runway months; add **15–25% contingency**; add **3–6 months of cash for the next raise itself**.
5. Cross-check all three sizing methods — they should converge within ~20%:
   - **Milestone-first** (YC): price the path to the next *fundable* milestone.
   - **Burn-first** (CRV): monthly burn × desired runway.
   - **Runway-first** (NFX): 18–24 months backed by a 24-month monthly model — stretched to ~36 in the current seed→A market.
6. Sanity-check the implied price: investors read the ask as ~20% of post-money — raising $3M ⇒ ~$15M post is the silent signal (Dreamit's 20% Ratio). Pick the defensible post-money first and set the ask so both signals agree.
7. Produce **2–3 plans** at different amounts ($1M / $3M / $5M) where more capital buys *faster growth*, not longer runway on the same plan (NFX).
8. **Don't burn a letter**: call it seed-2 or seed extension rather than Series A — letters set metric expectations (Dreamit).

## Valuation methods (the corpus's three usable ones)

- **Lemkin's ⅓ rule** — a seed price is fair at ≤⅓ of what the next round will pay (through ~Series B; ≤½ after). Worked: $6M pre / $7M post ⇒ must credibly raise at $24M+ pre within ~18 months. If that's implausible, the seed price is too high — and a rational investor should pass or wait.
- **Dreamit's 20% ratio** — ask ≈ 20% of post-money; use in reverse to keep ask and valuation signals consistent.
- **Staircase model** (Hustle Fund) — valuation steps when something new is *de-risked*, not linearly with revenue. Decide what to build/prove *before* raising to reach the next step.
- Market mechanics: let demand set the price where possible; name a range from comparables if forced. "Optimal, not highest": high enough for the dilution budget, low enough that the round closes and the next one clears it (Antler). "A lower valuation you over-deliver against beats a higher one you have to explain." Supply/demand is the real pricer: "raising $200K with $500K of interest ⇒ you set the price. Raising $2M with nobody interested ⇒ your valuation is $0" (Hustle Fund). Fund size shapes bids: $1B funds pay up for entry; $100M funds fight for ownership.
- **Ask low, revise up, never down** (PG's underestimate-your-target; Kevin Ryan's auction — ask $3–5M wanting $5–6M): a rising ask signals demand, a falling one starts the exodus. "No one wants to feel like they're getting a deal in venture capital."
- **Valuation vs partner quality** (Ryan): within 5%, take the better partner; at ~10%, still the partner; at ~30%, take the money. Local partner quality matters for round one, much less for rounds two and three.
- AI premium caveat: AI seed valuations run ~42% above non-AI (eqvista, 2026) — the premium prices in the why-now, making the *next* round's bar proportionally harder. Model Series A clearance at the premium price before celebrating it.

## Dilution budget

- Per-round norms: ~20% seed / ~20% A / 15% B / 10–15% C (Carta ~1,200 rounds via Lemkin). YC guidance: 10% excellent, ≤20% common, avoid >25%. PG's ceilings: ≤25% sold in the main early raise, never >40% cumulative before the Series A.
- Founders ≥70% collectively after seed; individual angels capped 2–3%; option pool 10–15% post-money sized to the *hiring plan until the next round*, not a default 20% (pool mechanics in `deal-terms.md`).
- Stacked SAFEs: model every SAFE at its cap before signing the next one — tranches at rising caps silently sell ~20% before the A investor buys anything (Hustle Fund).

## Bridges and alternatives

- Bridge pricing: existing investors 10–25% discount to the next round; a *new* investor entering pre-round should be asked for ~2× step-up to the real round price — otherwise they should rationally wait (Lemkin).
- The bridge is the new normal, not failure — the standard move at month ~24 with ARR short of the A bar (Lemkin/Carta, Oct 2025: "Raise more. Burn less. Plan for 3 years.").
- Below ~$400–500K, an equity round isn't worth the cost/clock — use SAFEs (notes where SAFEs aren't legal). Grants and crowdfunding are real capital but not smart money (Antler).
- When venture math fails the company (fundability verdict "different capital"): angels, revenue-funding, or a smaller round with the milestone map intact — resize the round or change investor class rather than re-arguing the same ask ("when five investors in a row say 'more traction,' you don't get more traction — you resize" — Brett Fox, 2024).
- Type A vs type B raising (PG): because you want to vs because you must — "if you want to raise money, the best thing you can do is get yourself to the point where you don't need to"; keep a plan for raising zero. Zapier's one-and-done ($1.2M in 2012, never again; YC bought for credibility, not capital) is the credible counter-narrative, with stated limits — it doesn't transfer to capital-intensive builds or long enterprise cycles. And seed can be a *phase*, not a round: 2–3 tranches inside the seed phase, then an A run from strength (Hunter Walk).

## Enterprise-infra sizing note

For enterprise-motion infra (long sales cycles), size for ~3 years of runway even pre-revenue and say why: the sales cycle — "as little as humanly possible, but no smaller than you need to show the traction required for the next round" (David Aronchick, Expanso's $7.5M seed, 2023–24; full account in `devtools-positioning.md`).

## Known corpus gap

Cross-border mechanics — the Delaware flip, non-US founders raising from US funds, remote diligence, LatAm specifics — are absent from the 625-source corpus. Source that guidance externally (counsel, current incorporation-platform docs) and label it as un-corpus-backed.
