# Evaluation and rollout

## Three kinds of tests, none substitutes for another

1. **Fixtures** for parsing, policy and fallback: fake receipts (valid, malformed, timeout, 503, empty, argmax mismatch) drive the code paths. No network.
2. **Regression cases** for judgment: 8–20 short synthetic states with the set of allowed answers per question (`author_stance ∈ {support}`), run through the real route, receipts reused by hash. Add a case for every production failure you fix. Assistant-written expectations are regression, not gold.
3. **Labeled evaluation**: human labels with abstention as a class; the only thing that measures quality.

## Gold sets

- Labels per question, including `unknown` and `not_applicable` as legitimate labels. Reviewers blind to the model output; when you can afford more than one, adjudicate disagreements and keep them.
- Split by entity (company, author, session), never by row. Include accepted and rejected outcomes.
- Metrics that stay honest with sparse labels: accuracy on completed decisions, accuracy on known targets, selective accuracy + selective coverage (abstentions excluded and counted), abstention rate, per-label matrix with error/pending columns. Any ratio with a zero denominator is `null`, never 100 %. Ship the harness with an empty case file rather than pretend.
- Do not use an LLM as human gold. Two LLM judges agreeing at 99 % on decisions still disagreed with each other at Spearman 0.02 on a barrier dimension; measure the ceiling between judges before measuring anything against them. Judges generalize ("a hospital distributor sells surgical instruments") where Jev is literal; precision 1.0 against judges is not precision against humans.
- One human negative justifies a rubric fix and a regression case. It is not a calibration set. A threshold needs a held-out set; once a held-out failure guided a change, that case is development data and the next final test needs fresh cases. Precision 0.96 in-sample became 0.40–0.46 on 130 unseen files in one code-review integration.

## Change = re-evaluate

Model version (log the versioned id from the response), route, language of the rubric, question wording, candidate construction, thresholds, policy. Replay the regression cases and re-score the labeled set; compare against the previous version's receipts, which the cache keeps.

## Known failure modes to test for explicitly

- **Polarity**: compliance wording vs violation wording on labeled positives and negatives; check that `criteria.true` and the question agree.
- **Batch effect**: N candidates in one state vs one per request on 50 items (expect shifts; decide the cap).
- **Injected instructions** inside the evidence: measure how often and how far answers move with and without the guard prefix; the docs promise no invariance, so gate unsafe actions on more than one signal.
- **Confidence-gate inflation**: report score with and without the low-confidence exclusion and the coverage.
- **Aggregator choice**: mean of P(yes) vs ordinal expectation with veto on the same texts.
- **Rubric contract**: "does the text report X" vs "is X plausible" (expect different worlds).
- **Route equivalence** when you can switch routes (expect near-identical decisions; verify).
- **Vocabulary recall**: remove one synonym from the profile/criteria and watch a true positive vanish; the fix is the vocabulary, not the threshold.

## Shadow mode before active

Same event, two decisions, one execution: the existing handler stays authoritative and runs once; the Jev branch logs a proposal with the same decision-time state and evidence ids; a comparison job scores agreement, review rate, wrong routes, critical misses and coverage. Modes `off / shadow / active` with a tested rollback. Shadow cannot measure effects that only exist after acting (a queue that moves, a customer who replies); use an A/B for those. If the model can trigger tools, record the intended action instead of executing it.

## What to measure before expanding

Wrong routes, critical misses, human review rate, automatic-decision coverage, API failures by status, verified task outcomes, sample sizes. And the economics: cost per **successful** task (all model, tool, retry and review costs ÷ verified acceptable completions, failures in the numerator). A faster decision is a fraction of the task: with decisions at 40 % of wall time, a 20× faster judge gives 1.6× end to end; a real browser agent got its 25 % gain from cutting protocol calls 1,092 → 101 with the same models. Adopt when the whole workflow improves at the quality you need, not when the judge is fast.
