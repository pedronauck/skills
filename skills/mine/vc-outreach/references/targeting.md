# Targeting — who to pitch, who to cut

Size and research the list for the actual raise and founder capacity. Counts, tier percentages, research times, and funnel rates below are historical heuristics; no quota or target must be reached before a useful list can be delivered.

List construction is 80% of the raise's outcome variance — "80% of fundraising work happens before the first call" (Techstars × Metal, 2025). Target partners, not firms; qualify hard; the list should *shrink* as learning accumulates ("if it only grows, your qualification standard is too weak" — Metal, 2026).

## Self-qualification gate (before building any list)

(a) VC-fundable at all — market size, scalability, capital efficiency, traction; (b) ≥1 positive signal — strong traction, significant IP, a lead secured, or an exited founder on the team. "A prototype or a waitlist is usually not enough. If you're too early, consider accelerators or angels instead" (OpenVC, 2026). When this gate fails, route to vc-strategy's fundability verdict rather than outreach.

## List construction

- Size: build **100–200 partner-level names**, work ~50–70 actively, drive to 15–25 first meetings (Metal 2026; converges with Hustle Fund's 50–100 and Foundersuite's 100–200-then-cut).
- Persona first: geography (where incorporated) × vertical × stage/maturity × check size (OpenVC).
- Sources to sweep: investor databases (OpenVC, VC Sheet, Crunchbase, PitchBook, Foundersuite) · **portfolio archaeology** — run 10–12 adjacent-but-not-competitive companies through Crunchbase, record who funded them *at this stage* and who those firms co-invest with · LinkedIn 2nd-degree with geo filter · funding newsletters read for **who just raised a fund** (fresh dry powder) · conference speaker lists · angel groups · university and company alumni funds.
- Partner-level data model per row (VC Sheet's fields): stages, sectors, **average check**, **does the fund lead**, contact route, plus a `Connector` field.
- Inclusion test: they love this problem, invest at this stage, can write this check size (Hustle Fund). Skip reflexive brand-first targeting: "Andreessen and Sequoia and Benchmark may not actually be the best fit."
- Timing signals as a targeting axis: a new fund close or fresh partner hire = active deployment (Qubit, 2026). Prefer investors who **made money** in the category over ones who merely list it — the "prepared mind" segment (a rejected-by-30 Series A got a term sheet in 12 days after switching to category-winners — Techstars × Metal, 2025).

## Disqualification pass (expect to cut ~30%)

- **Competing portfolio company → delete immediately.** "If they're ethical they won't want to talk to you; if they're unethical they'll send your deck to your competitor. I've seen it happen many times" (Foundersuite, 2022).
- **Fund vintage / dry powder:** no new fund in ~2 years → mostly follow-on reserves; demote to practice tier. Structural: funds run 8–12-year lives with new investments in years 3–5 (CRV).
- **Check-size arithmetic:** typical check ≈ 2% of fund for 10–20% ownership. If the round is >5% of their fund, or their check is 5–10× the round, cut ("so many times a deal could have happened if the founders had just asked for less" — Lemkin).
- **Stage share, not stage claim:** require ≥10% of their recent deals at this stage — "one pre-seed out of 65 investments means they don't really do pre-seed" (Techstars × Metal). Pre-seed and seed are different asset classes, not adjacent ones.
- **Dormant angels** (no deals in 5+ years) → demote. **"Growth capital" = Series B+**, not a seed compliment.
- **Won't lead** when a lead is needed → deprioritize. **Reputation red flags** from founder back-channels → cut ("you're going to spend the next 6–8 years with these investors").
- Angel-pushed intros to ill-fitting friends' funds → cut; future-round investors → defer the meeting until after this round closes (Antler).

## Tiering

~30 Tier A (dream fit) / ~30 Tier B / ~40 Tier C (Xfund via Fidelity, 2024), **crossed with access quality**: the strongest warm paths go to Tier A; B/C absorb outreach where no warm path exists (Metal). **Never open with Tier A** — pitch imperfect matches first, arrive at Tier A "locked and loaded." Humility caveat: Tier C often becomes Tier A on contact — "very few companies can afford to be extremely picky."

## Per-investor research (~10–15 min before any contact; ~1 hour of qualifying saves ~10 later)

- Last 2 years of deals: stage mix, check sizes, lead vs follow.
- Portfolio scanned for competitors and near-adjacents.
- Which **partner** owns this sector — bio, blog, podcasts, X feed; one specific nameable signal to open with.
- Fund vintage; lead behavior; ownership target.
- Mutual connections mapped; `Connector` filled.
- Tier A only: back-channel with 1–2 of their portfolio founders.

## Funnel math (set expectations with real numbers)

- Averages: 58 contacted / 40 meetings (DocSend); 40–60 pitched at sub-10% conversion (CRV, 2026).
- Real funnels: Copybara 100+ firms → 80 met → 16 docs → 7 offers → 3 agreed (Fidelity, 2024); Beckord 200 pitched → 1 fund + 10 angels ≈ 5% (Foundersuite); founder accounts of 49–70 no's before the yes.
- Rejection base rate 90–95% — "it's not because of you or your business; that's just the nature of the game."
- Cold vs warm: 1–3% response cold vs 15–20% via trusted intro (Metal, 2026); NFX's blunt "a warm intro is 100× more effective"; the hardest number in the corpus: **2 of 760** Uncork portfolio companies arrived via cold email, while a known partner receives 50–100 warm intros a day.
- Devtools-specific starting points — with a caveat: the corpus's only dedicated list (Rho, 2026: boldstart, Tola, MAGIC Fund, Vela, Expa, Trajectory, 500 EE; EU: Point Nine, Seedcamp; Boston: .406, Glasswing) is thin — only boldstart is a genuine day-one devtools/infra fund and the canonical devtools names are missing. Treat it as a seed for portfolio archaeology on adjacent devtools companies, plus VC Sheet's devtools and infrastructure sheets (43 + 40 funds). Homebrew-shaped funds pattern-match **bottom-up adoption + top-down sales**.

## Known corpus gap

Non-US founders raising from US funds — Delaware flip, redomiciliation, remote diligence, LatAm specifics — is absent from the 625-source corpus (zero substantive hits). Source that guidance externally (counsel, current incorporation-platform docs) and label it as un-corpus-backed.

## Pipeline schema (minimum viable)

`Partner · Firm (stage/thesis note) · Tier · Status · Owner · Connector(s) · Next step + date · Key objections · Notes`. A row with no dated next step is a row losing momentum. Full stage vocabulary and review cadence: `process-and-pipeline.md`.
