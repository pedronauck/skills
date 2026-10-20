# Mechanisms catalogue

Building blocks that recur across the archetypes in `use-cases.md`. Each entry: what it does, the shape, when to use it, what it replaces. Combine freely; they are code around typed questions, not features of the model.

## Building the unit

- **Unit builder.** Bursts of messages (gap ≤ 30 min, ≤ 25 messages, ≤ 2,200 chars), paragraphs of a turn, hunks of a diff ± 20 lines, windows of a transcript. Filter trivial units in code (≥ 8 words, or a link, or a transcript) before any call. Replaces "judge the whole document".
- **Dedicated semantic state.** Build `{guidance, document{authorText, quotedText, replyingTo, attachedImages}, candidates{aliases, notThisPerson}}` from your records; never the row. Replaces "dump the JSON".
- **Structured field first.** If the record already says it (`ffe_included: true`, a material/service flag, a product code), read it in code and skip the question; use it as a free sanity label for the model's answer.
- **Excerpt selection.** Send the sections a question needs and mark omissions; head + tail is one policy, right for chats; a byte cap with explicit `insufficient_context` beats silent truncation.

## Choosing among candidates

- **Candidate builder.** Time window (45 days), same topic first, cap (6–20), stable ids, `none` as an option. Code proposes; Jev chooses. Measure shortlist recall separately from choice accuracy: a selector cannot pick what was filtered out.
- **Menu from observation.** For agents: rebuild the option list from the current page or the available workers on every step; a decision on a stale menu is `not_checked`.
- **Hydrated Choice.** Put the candidates' labels into `criteria` at runtime (`{id: "dd/mm · title — what"}`); 255 options max.
- **Hierarchical selection (lists over 255 or catalogues).** Contract: (1) code partitions candidates into groups of ≤ 254 with a one-line description each; (2) Choice over the groups plus `none`; (3) Choice within the chosen group plus `none`; (4) code records both choices and their probabilities; an abstention at either level ends the descent as `abstained`, and the final probability reported is the product of the two levels. Alternative for ranked shortlists: Score each candidate's applicability in batches, sort in code, then Choice among the top-k with `none`. The official hierarchical-classification cookbook implements a search over alternatives: https://docs.typesafe.ai/cookbooks/hierarchical_classification.md.
- **Per-id cloned questions.** In a batch, clone `changes_{id}` from a template and say "Evaluate only candidate `{id}`"; without the id the model answers about the wrong item.
- **Relation + target pair.** Choice `new | updates | repeats | contradicts | resolves | supersedes` plus Choice `target` among the candidates with `none`; `new` or `none` resets the target. Exclude same-day continuations from candidates when "updates" inflates.
- **Closure over follow-ups.** For a promise or an open thread: Choice `done | postponed | cancelled | open` plus Choice `evidence` among the following units within a window; `open` means "no trace here", never "not done".
- **Gray-zone dedupe.** Contract: code computes cosine for candidate pairs; pairs above the upper bound merge without a call, pairs below the lower bound stay separate, the middle band (e.g. 0.50–0.80 for ideas, 0.90–0.92 for notes) goes to Jev with the Noul `adds_something(newer, older)` asked in both orientations; merge only when both orientations say no (P < 0.5). When packing a ranked list greedily, stop asking for the current item after two consecutive candidates were judged distinct, and move on.

## Questions as instruments

- **Closed taxonomy in criteria.** Kinds, stances, topics as options with one-line descriptions and an escape (`chat`, `absent`, `other`). Aliases and abbreviations inside the option text. A generative pass can propose the taxonomy from a sample; Jev applies it.
- **Question bank with weights and dimensions.** Hundreds of criteria, each with rubric, weight, dimension, kind (`quality | risk`), applicability, source; `partial` / `not_applicable` from templates; loader builds the API map and hashes the bank.
- **Level descriptors.** Four parallel paragraphs per ordinal criterion; "clear or correct does not mean strong"; insufficiency is an abstention, not the lowest level.
- **Verification pair.** `support: supported | unsupported | ambiguous` on the exact bounded claim, then `nature: declared | inferred` (provenance, not correctness). Comparisons need both sides cited before `contradictory`.
- **Meta-questions over generated questions.** Frozen, versioned: "does the proposed violation condition require something the rule does not?" (invented condition), "would it flag behaviour the rule permits?" (lost exception), "do question and criteria describe conflicting conditions?" (contradiction), plus omission per section. The generator never writes its own exam.
- **Speculative fan-out.** Ask branch-specific questions up front ("if this is a refund, is the amount within policy?") and consume only the answers of the branch taken.
- **Double gate.** A fact exists only when Jev says so **and** an extractor found the literal (who owes + the `what`); prevents obligations without a statement.

## Staging

- **Two rounds with `when`.** Cheap questions over the original state; a second request only for items above a threshold, with the evidence that answer justified fetching. Add rounds only on a measured gain.
- **Cascade.** One cheap Noul over everything, the rest only for survivors above a low bar (0.3). Halves cost in the design; implement it and measure it before claiming it.
- **State machine.** States and transitions in code (regime → sector → pair; triage → judge → relate → close); predicates are Jev; each state has its own gate and its own labeled set; states code can resolve make zero calls.
- **Informed batch.** Retrieve first, then ask the gate question with the candidates in the state; the gate sees the subject instead of guessing.
- **Triage by description with bypass.** "Does this rule set apply to the changed code? Prefer applying when uncertain" per pack; broad or mandatory packs skip triage; companion files (`go.mod`) must not turn off a pack's globs.
- **Static checks beside Jev items.** Membership tests (file A changed without file B), regex extractions, structured flags: probability 1.0 or 0.0, no call.

## Aggregating

- **Ordinal expectation with veto.** Score from the distribution over levels; integrity groups block and never raise the mean; any `weak/absent` blocks; coverage = 1 required.
- **Min of components.** Conservative gate for "all of these must hold"; not a joint probability; inspect the table before choosing 0.6 / 0.8 / 0.9.
- **Multiplicative fit with tiers.** `fits × adherence/(levels−1) × (1 − barrier)`; `lead / look / ignore`; magnitudes as separate code predicates with warning tiers.
- **Composite with signal groups.** 100/50/0 → group → dimension → equal weights; risk as flags; coverage published; thin dimensions greyed.
- **Rank with named exclusions.** Recency decay, access log, kind priors, anchor and activation boosts; per-item exit gate and window; every drop labeled.
- **Evidence-gated promotion.** Value only with quote + supported check ≥ τ; published confidence = min(proposal, check).
- **Eligibility predicate.** Known author ∧ full text ∧ relevant ∧ sufficient ∧ attributable ∧ stance argmax ≥ 0.8; comparisons need both sides determined; missing is `null`, never zero.
- **Quantification (PACC).** Contract: input = a labeled reference set with ≥ N examples per class (N chosen from your variance; one integration used 10) and the model's probability vectors on it; calibration = the matrix `M[pred | true]` of mean predicted probabilities per true class; estimation = solve `shares = argmin ||M·s − mean_pred||` on the simplex for a new window; validity = an expiry (e.g. 14 days) and a refusal when the fit error on held-out mixtures exceeds a threshold or a class has fewer than N examples; output = class shares with the calibration id. Never publish raw counts of predicted labels as shares.

## Keeping it honest

- **Receipts and decision trace.** Raw answers, model id, question version, route, latency, tokens, cost or cost-unknown, cache hit, status, verified outcome; store the request too.
- **Cache by request hash; question files with versions.** A changed word is a new decision; replay is free, cold runs give the real cost.
- **Regression suite with allowed sets.** Synthetic states with the set of acceptable answers per question, one added per fixed failure, reused receipts; assistant-written expectations stay regression.
- **Judges ceiling.** Two cheap LLM judges over the same state: their agreement bounds what a judge can measure; a judge that generalizes ("a hospital distributor sells instruments") measures a different thing than the literal model.
- **Bitemporal replay.** Contract: input = a frozen manifest (session id, corpus commit at that time, prompts in order, sha256 of the question files); procedure = reconstruct the corpus at that commit in an isolated worktree, run the read path per prompt with the same config, persist the first attempt; gold per turn = items actually read or edited with an unambiguous reference in the turn's output; metrics = recall@k and precision@k with a fixed denominator of k, latency p95, cost or cost-unknown per session; compare against baselines (lexical, embeddings, union) on the same manifest; refuse to conclude on fewer than a few dozen positives.
- **Independent checker.** For agents and generators: a verifier outside the loop reads the world (file, row, page) and decides `verified / not verified`; a selected `DONE` is a proposal.
- **Human feedback beside, not inside.** A separate table for "would publish / would not", never a term in the score; one negative is a regression case, not a calibration.
