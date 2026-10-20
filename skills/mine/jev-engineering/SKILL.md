---
name: jev-engineering
description: >-
  Design and build use cases, POCs and production systems with TypeSafe's Jev decision model (System One): choose a design mode and a use-case archetype, build decision state, write typed questions, combine Jev with generative models, durable workflows, retrieval and perception tools, aggregate and gate in code, keep failures and costs visible, evaluate and roll out; covers the jev-1.14 danger-zone features (images, Box, long context). Use when building anything with Jev, from a first POC to a product, or when reviewing an existing Jev integration. Ships dependency-free reference clients (TypeSafe API, OpenRouter Decisions, Vercel AI Gateway) and a POC skeleton. For primitives and live docs alone use TypeSafe's typesafe-ai skill; not for generic LLM prompting.
---

# Jev Engineering

Jev judges the text (and, behind a danger-zone header, the images) you send against the criteria you write and returns typed answers with probabilities: Noul (P of yes), Choice (option + distribution + confidence), Score (expected level + distribution + confidence), and on jev-1.14 Box (one bounding box + confidence). It does not generate text, count, do arithmetic, read dates as quantities, establish truth, confer permission, or prove that a side effect happened. Everything else is ordinary software you own: state builders, candidate lists, arithmetic and dates, policy and thresholds, workflows, execution and verification. Generative models write artifacts and literals; Jev routes before and checks after. That division is what makes use cases like editorial studios, diagnostic banks, obligation trackers, dossiers, corpus atlases, rule packs, memory judges, signal observatories and agent loops cheap, fast and inspectable.

## Facts to design around (jev-1.13 and jev-1.14, checked live 2026-10-17; re-check https://docs.typesafe.ai/models.md when they matter)

| | |
|---|---|
| Models | `jev-1.14.0` (released 2026-10-14: small gains everywhere, largest in non-English) and `jev-1.13.0`, same price and limits. `jev-preview` → 1.14; `jev-latest` → 1.13 until TypeSafe moves it to 1.14 (announced for about 2026-10-21). 1.13 gets 60 days' notice before deprecation, 1.14 gets 30. OpenRouter slug `typesafe/jev-1.14`; Gateway lists `typesafe-ai/jev-1.14.0` |
| Request | `state` (string or JSON) + a map of typed questions evaluated independently against the same state in one call; no question sees another's answer; optional `assets` map of images referenced from state, instructions or criteria |
| Limits | 32k tokens for state + longest question, 64k for state + all questions (262k for both with the long-context header); Choice ≤ 255 options; Score 2–10 levels; English is the primary language |
| Answers | Noul has no separate confidence. Choice/Score `confidence` is distribution concentration, not accuracy. Score levels are 0-indexed. Box returns four edges as fractions and has no "not found" answer |
| Danger zone (not production-grade by TypeSafe's own word) | `TypeSafe-Danger-Zone-Images: true` for images and Box (Box needs 1.14), `TypeSafe-Danger-Zone-Long-Context: true` for 262k; TypeSafe API only for images (OpenRouter drops `assets` silently). See `references/images.md` |
| Speed, price | 0.2–0.6 s per call at 1–4k tokens in production runs; list price US$ 0.042 per million input tokens, output free, images billed as input (≈ width × height / 390 tokens); tens of parallel calls sustained; hundreds of questions per text and thousands of texts per dollar are the normal design space |
| Documented weaknesses | counting; numeric comparison; large state full of irrelevant detail (accuracy falls); adversarial text in the state (can move answers); instructions that contradict criteria; extra levels of indirection; literal reading of the question you wrote; images are worse than text on every model, so decompose them further |

## Procedure

Read by task: a new idea → `references/design-modes.md` and the closest archetype in `references/use-cases.md`; a transport or reliability review → `references/transport.md` and `references/reliability.md`; question or rubric work → `references/questions.md`; scoring or gates → `references/aggregation-and-gates.md`; images, Box, long context or a model upgrade → `references/images.md`. The steps below are the full build path; take only the ones the request needs.

1. **Choose the mode and the archetype.** Read `references/design-modes.md` (whole decision in one state · question bank as instrument · multi-stage state machine, and how they combine) and pick the closest shape in `references/use-cases.md` (twelve built archetypes with loop, state, questions, code, tools, gates, evaluation and observed numbers).
2. **Define one decision with known outcomes**, an existing fallback and examples you can label. Write it as: given [named evidence], decide [one property] using [explicit criteria].
3. **Build the state in code** (`references/state.md`): what the decision needs, nothing else, provenance fields, candidates proposed by code.
4. **Write the questions in a versioned file** (`references/questions.md`; bank shape in `assets/question-bank.example.json`): guard prefix, polarity that matches the criteria, an abstention with a distinct meaning, counter-examples inside the criteria, no double negatives.
5. **Pick mechanisms and tools** (`references/mechanisms.md`, `references/tooling.md`): unit and candidate builders, relation/closure pairs, staging, aggregators; what a generative model, a workflow engine, retrieval, vision/STT/PDF extraction and storage each own.
6. **Run the POC** with `assets/poc_skeleton.py` (question map over a JSONL, cache, table of distributions, confidence, cost, latency) on ~100 items; read the table; label ~30; fix vocabulary and criteria before thresholds.
7. **Aggregate and gate in code** (`references/aggregation-and-gates.md`): persist raw answers, name the gate quantity, thresholds per action risk from labeled cases, publish coverage.
8. **Harden** with a reference client (`assets/jev_client.py`, `assets/jev-client.ts`), routes in `references/transport.md`, statuses/budget/cache/log in `references/reliability.md`.
9. **Evaluate and roll out** (`references/evaluation.md`): fixtures, regression cases, a labeled set, `off / shadow / active` with active off until compared.

Done when the requested deliverable exists and its checks ran:
- **POC**: state builder, question file, results table and a written note of what was measured (sample, rubric version, route, cost, coverage, failures).
- **Build or change**: a decision can be replayed from its log row (request hash, question version, requested and reported model ids, route, latency, tokens, cost or cost-unknown, cache hit, status, verified outcome); fixtures cover parsing, policy and fallback; regression cases pass.
- **Activate**: additionally, a labeled set scored against the current path, a shadow run compared, the rollback switch exercised.
- **Review**: findings cite file and line, name the rule below, and propose the concrete change.

## Rules that earned their place

Each rule comes from a failure observed in a built integration; the numbers are those cases, not universal limits, and the references say what was measured.

1. **Numbers, dates, counts, rankings and thresholds live in code.** Give Jev candidate spans and ask which applies; parse and compare in code.
2. **Start from the whole decision, not a sentence.** The state can carry the taxonomy, the neighbours, the open obligations and the goals; a bank can carry hundreds of weighted questions; a chain can gate stages. The naive "one sentence, one label" wastes what makes Jev different.
3. **State carries what the decision needs and nothing else.** The docs say irrelevant detail lowers accuracy; one integration measured a mean probability shift of 0.12 when 20 candidates shared a state. Partition per question group, cap candidates, compare batch against single on your own sample.
4. **Every question has a guard, a polarity that matches its criteria, and an exit.** Content is evidence, never instructions. Yes means the condition you act on (a compliance wording and a violation wording are different questions; one integration saw 0.76–0.85 versus 0.03–0.22 on the same clean code). `unknown`, `none`, `other`, `not_applicable` mean different things; code decides what each does.
5. **Generative models write; claims get checked.** Titles, literals, taxonomies, hypotheses with ids, variants: a generator produces them; code verifies literals, Jev verifies claims about the evidence, and free-text suggestions that assert nothing are labeled as generated and left to human review.
6. **Name the gate quantity before the number.** Noul probability, argmax probability and Choice/Score `confidence` are three quantities. Choose thresholds and coverage floors from your labeled cases. Dropping low-confidence answers from an average inflates it (one run: 96/100 at 39 % coverage); always publish coverage.
7. **Failure stays visible.** Timeout ≠ no. Missing evidence ≠ false. Malformed ≠ pass. Cost missing ≠ zero. Each is a status with a reason, and the existing fallback runs.
8. **Validate the receipt**: complete answer set, matching types, argmax equals `choice` within the route's rounding, distributions sum to one, score equals its expectation, box edges in [0, 1] and not inverted, confidence in [0, 1]. Reject; never coerce to neutral.
9. **Cache and version.** Key = hash(route, model, revision, sanitized state, questions, image digests, danger-zone flags); store the request; hand out copies; pin a versioned model id for active use (`jev-latest` moves from 1.13 to 1.14 in October 2026: re-run the labeled set on `jev-1.14.0` before it does).
10. **"Done" is a receipt read from the world**, not a Jev answer; before retrying an action that may have executed, inspect the target.
11. **A negative example is not a calibration set.** One or two labels justify a rubric fix and a regression case; a threshold needs a held-out set, and a held-out failure that guided tuning has become development data.
12. **Danger zone stays out of the action path until measured.** Images, Box and long context are TypeSafe's own "not for production yet": POC and shadow first, a text fallback beside them, and a receipt check that the image actually reached the model (input tokens grow by its size).

## References

- Design modes, checklist, a POC in a day: `references/design-modes.md`
- Twelve use-case archetypes with loop, state, questions, code, tools, gates, evaluation, observed numbers: `references/use-cases.md`
- Mechanisms catalogue (unit and candidate builders, relation/closure pairs, staging, aggregators, honesty tools): `references/mechanisms.md`
- Combining Jev with workflow engines, generative models, perception, retrieval, storage and UIs: `references/tooling.md`
- State, sizing, provenance, candidates, freshness: `references/state.md`
- Instructions and criteria, polarity, abstention, banks and the bank loader: `references/questions.md`; bank format: `assets/question-bank.example.json`
- Scores, composites, gates and their quantities (runnable snippets): `references/aggregation-and-gates.md`
- Routes, request and response shapes, per-route gotchas, doc links: `references/transport.md`
- Statuses, retries and the shared deadline, verify-before-retry, budget, cache, decision log, secrets: `references/reliability.md`
- Fixtures, regression, gold sets, shadow mode, cost per successful task: `references/evaluation.md`
- Code: `assets/poc_skeleton.py` (run a question map over items; edit three functions), `assets/jev_client.py` (stdlib; CLI `decide | validate | estimate`, `--assets`, `--long-context`; `image_asset()` checks image limits locally), `assets/jev-client.ts` (no dependencies, Node 18+/Bun; `imageAsset()`, `longContext`)
- Images, Box, long context, routes that drop images, token costs, patterns: `references/images.md`
- Live docs: https://docs.typesafe.ai/llms.txt (index), `/api.md`, `/models.md`, `/images.md`, `/primitives/box.md`, `/confidence.md`, `/model-jaggedness/jev-1.13.md`, `/patterns/composite-scoring.md`, `/patterns/confidence-routing.md`, `/cookbooks`
