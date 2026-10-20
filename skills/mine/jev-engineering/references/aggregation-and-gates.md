# Aggregation and gates in code

Persist the raw answers (probabilities, confidence, usage) and compute policy afterwards. Changing a weight or a threshold must not require re-inference; changing a question must.

## Name the quantity before the number

| Quantity | Where | Means | Typical use |
|---|---|---|---|
| Noul probability | `answers.x.noul` | P(yes) | the gate itself for binary checks |
| Argmax probability | `max(answers.x.probabilities)` | mass on the chosen option | eligibility floors ("position counts only above 0.8") |
| `confidence` | `answers.x.confidence` (Choice/Score) | concentration of the distribution | routing to review; never as accuracy |
| Expected level | `answers.x.score` | probability-weighted level, 0-indexed | threshold comparisons, ordinal notes |

Thresholds seen in production integrations span 0.5 (triage), 0.65 (attribute), 0.8 (identity, stance), 0.85 (block, place match), 0.9 (event clustering), each on a **different** quantity and each chosen from that workload's labeled cases. There is no universal number. Choose per action risk from your own labeled set: a reversible tag can act at a lower floor than a payment, a block or an identity match, and irreversible actions usually deserve a second, independent check.

The docs' own example: below 0.5 confidence go to a human; a read-only screen is recoverable and proceeds; a transfer proceeds only above 0.9 and still with confirmation; in between, ask the user.

## Patterns (copy the one that matches; each snippet runs as written)

**1. Ordinal expectation with veto** (rubrics with levels `absent/weak/functional/strong`; any other option, such as `unknown` or a missing answer, blocks):

```python
LEVELS = ("absent", "weak", "functional", "strong")

def level_value(probs, levels=LEVELS):
    n = len(levels) - 1
    return min(100.0, 100.0 * sum(i * probs.get(l, 0.0) for i, l in enumerate(levels)) / n)

def evaluate(answers, groups, threshold=70, floor=60, veto_groups=("integrity",), levels=LEVELS):
    """groups: {group: [question ids]}. Every veto group must be present and non-empty; a rubric that
    omits its integrity questions cannot pass. Returns score, per-group scores, blockers, passed, coverage."""
    scores, blockers, assessed, total = {}, [], 0, 0
    for g in veto_groups:
        if not groups.get(g):
            blockers.append(f"{g}: required veto group missing or empty")
    for group, ids in groups.items():
        vals = []
        for qid in ids:
            total += 1
            a = answers.get(qid)
            if not a or a.get("type") != "choice" or a.get("choice") not in levels:
                blockers.append(f"{qid}: missing or non-level answer ({(a or {}).get('choice')})")
                continue                                    # unknown/abstained is a block, not a zero
            assessed += 1
            if a["choice"] in ("weak", "absent"):
                blockers.append(f"{qid}: {a['choice']}")    # any weak/absent blocks
            vals.append(level_value(a["probabilities"], levels))
        scores[group] = sum(vals) / len(vals) if vals else None
        if group in veto_groups and scores[group] is None:
            blockers.append(f"{group}: veto group not assessed")
        elif group not in veto_groups and scores[group] is not None and scores[group] < floor:
            blockers.append(f"{group}: below floor")
    creative = [v for g, v in scores.items() if g not in veto_groups and v is not None]
    score = sum(creative) / len(creative) if creative else None
    coverage = assessed / total if total else 0.0
    return {"score": score, "groups": scores, "blockers": blockers, "coverage": coverage,
            "passed": score is not None and coverage == 1.0 and score >= threshold and not blockers}
```

Why: in one integration a mean of P(compatible) over 40 yes/no questions approved with 94.9 a text a human had rejected; the ordinal expectation with a veto for integrity scored the same text 61.9, with the hook and the ending below the floor. Confidence is not part of the score.

**2. Conservative gate = minimum of components**, documented as not a joint probability:

```python
gate = min(p["digital"]["explicit"], p["verifiable"]["yes"], p["support"]["support"])
```

Look at the table before choosing the threshold: in one run, at 0.8 this gate selected "use accounting software" (0.99) and dropped "reconcile accounts" (0.64), the more valuable task.

**3. Multiplicative fit with two tiers** (a Noul, a 5-level Score indexed 0–4, and a Noul for barriers):

```python
fit = fits_scope * (adherence / 4) * (1 - barrier)   # adherence is a 0–4 expected level; divide by (levels − 1)
tier = "lead" if fit >= 0.5 else "look" if fit >= 0.35 else "ignore"
if size_check in ("too_large", "too_small") or barrier >= 0.5:
    tier = "ignore"
```

The middle tier collects "neighbors of the trade" that a compressed scale (in one dataset exact matches landed at 3.4–3.6 of 4) would otherwise lose. Thresholds go into the output JSON so re-cutting is free.

**4. Composite over a question bank** (hundreds of criteria, several dimensions; bank items carry `id`, `dimension`, optional `scoring_dimension`, `kind` = `quality` | `risk`, optional `signal_group`):

```python
VALUE = {"strong": 100, "partial": 50, "weak": 0}

def composite(judgments, bank, confidence_floor=0.65):
    """judgments: {id: {status, choice, confidence}}. Quality questions feed the score; risk questions become flags.
    Returns score, per-dimension scores, risk flags, and the counts needed to publish coverage."""
    by_dim, risks, assessed, eligible = {}, [], 0, 0
    for q in bank:
        j = judgments.get(q["id"])
        if q.get("kind", "quality") == "risk":
            if j and j.get("status") == "decided" and j.get("choice") in ("weak", "partial"):
                risks.append(q["id"])
            continue
        if j and j.get("status") == "decided" and j.get("choice") == "not_applicable":
            continue                                        # out of the denominator
        eligible += 1
        if not j or j.get("status") != "decided" or j.get("choice") not in VALUE:
            continue                                        # unknown / error / pending: not assessed
        if j.get("confidence", 0.0) < confidence_floor:
            continue                                        # excluded → must be shown as coverage
        assessed += 1
        dim = q.get("scoring_dimension") or q["dimension"]
        by_dim.setdefault(dim, {}).setdefault(q.get("signal_group") or q["id"], []).append(VALUE[j["choice"]])
    dims = {d: sum(sum(v) / len(v) for v in g.values()) / len(g) for d, g in by_dim.items()}
    return {"score": sum(dims.values()) / len(dims) if dims else None, "dimensions": dims, "risks": risks,
            "assessed": assessed, "eligible": eligible, "coverage": assessed / eligible if eligible else None}
```

Group semantically redundant questions first (three questions about "what the product is" vote once), then weigh dimensions equally so 54 execution questions do not swamp 7 reapplication questions. Risk questions never enter the mean; they become flags.

**Coverage is part of the answer.** Excluding low-confidence answers inflates the mean: one real run scored 96.2/100 with 38.6 % coverage, because the model tends to be confident exactly when the evidence is clearly positive. Publish assessed / eligible next to the score, grey out dimensions with too few assessed answers (pick the floor from your bank size; one integration used fewer than 5 or under 30 %), and warn when the score is high and coverage is low.

**5. Evidence-gated promotion** (a value becomes a fact only with a quote and an independent check):

```python
FALLBACKS = {"unknown", "ambiguous", "not_applicable", "none"}

def verified(proposal, quote, check, tau=0.65):
    ok = proposal["choice"] not in FALLBACKS and quote is not None \
         and check["choice"] == "supported" and check["confidence"] >= tau
    return {"value": proposal["choice"] if ok else None,
            "confidence": min(proposal["confidence"], check["confidence"]) if ok else None}
```

The gate is the check, not the first-pass confidence; a proposal at 0.40 with a supported check at 0.90 passes. Keep a comment saying the model cannot bypass these requirements, and a test that tries.

**6. Rank with named exclusions** (memory / retrieval):

```
rank = p_changes × (1 + 0.5·p_binding) × 0.5^(days/90) × (1 + log1p(access_count)) × prior(kind)
keep if p_changes ≥ exit_gate and p_changes ≥ best − window; then top-N; each drop labeled
(low-probability | confidence-gap | item-limit | already-injected | budget | redundant | needs-review)
```

Rank orders; it never vetoes a useful item for lack of history. Every exclusion has a name the operator can see.

**7. Two rounds with a `when` threshold**: ask the cheap questions over the original state; run a second request only for items whose first answer crossed a threshold, with the extra evidence that answer justified fetching. Add further rounds only when a measured gain justifies them.

## Things the model is not for

- Counting, sums, date arithmetic, magnitude comparison ("is 476 within 30–400?"): code. Ask which range applies; compare in code.
- Ranking N items in one question: score each item with the same rubric, sort in code.
- Structural invariance: P(noul) and 1 − P(not-noul) are not the same number; a threshold tuned on a Noul does not transfer to a Choice; a Choice over options and one Noul per option answer different questions.
- Truth: a supported claim is supported by the evidence you supplied; it is not verified against the world.

## Signals for the operator, not verdicts

Findings carry probability, the rule that produced them and the evidence span. Surface them as advisory unless the quantity crossed the action-specific threshold and the action is authorized; an "exit 0" or a "no finding" is never a certificate of compliance.
