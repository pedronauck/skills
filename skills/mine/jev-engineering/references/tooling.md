# Combining Jev with tools

Jev supplies judgments. Everything around it is ordinary software, and the division of labour is the design. This is what each class of tool owns, how the built integrations wired it, and the traps.

## Division of labour

| Owner | Does | Never does |
|---|---|---|
| **Code** | state builders, candidate lists, arithmetic, dates, counts, thresholds, transitions, dedup, entity extraction by regex, aggregation, budgets, receipts, execution, verification | ask the model to sum, rank N items in one question, or decide permission |
| **Jev** | typed judgments over supplied evidence: which option, whether a condition holds, which level, which candidate, which span supports a claim | generate text, establish truth, prove a side effect, remember across calls |
| **Generative model** | writes artifacts and literals: variants, titles, a `what`, a due-date phrase, a taxonomy proposal, hypotheses citing existing ids, suggestions, JSON extraction from prose | decide anything that code or Jev decides; be the source of a quote's existence; run unbounded |
| **Perception tools** | vision description into labeled fields, speech-to-text with word timestamps, PDF/HTML extraction of sections and spans | classify; their output is evidence labeled as model output |
| **Retrieval** | FTS/BM25, embeddings, graph activation, time windows: the shortlist | the final relevance judgment (Jev) or the gray-zone merge (Jev) |
| **Workflow / queue** | durable steps, leases, retries, concurrency, budgets per round, dispatch rates, cron | hide a failed item as a success |

## Workflow engines and queues

- Model each round as a durable step: research → generate → judge → select → judge whole → decide next round. `do-until` loops with a max-rounds guard; quotas per family stop the loop, not the model.
- Decide retry ownership per step: judgment steps that already return a tri-state usually run with step retries at zero; one malformed item must not abort a batch (fail-open per item), one malformed **schema** must (fail-closed per receipt).
- Concurrency per unit sized by the slowest dependency, which was the generative model or the scraper, not Jev, in every built case (2 pieces, 8 documents, 12 dossiers were the observed settings).
- Observed job settings, to calibrate rather than copy: 3-minute leases with 3 attempts; permanent provider errors pausing the provider instead of consuming attempts; budget or missing-key conditions deferring an hour without counting as a failure; rate limits waiting 60 s; dispatch capped at 150 jobs/min with collection before analysis and rubric-change reanalysis of the last 7 days at 100/min.
- Hooks (IDE stop hooks, CI, pre-commit): fail-open adapter (any error → empty output and a log line), fail-closed ledger (reserve cost before the call), a hard time budget (3 s read timeout inside a 15 s hook), at most one or two interventions per turn, and a switch that turns the hook off.

## Generative models beside Jev

- Delegate only what needs text: variants to be judged, titles, literal fields (`what`, `due_text`), a taxonomy from a 120-excerpt sample, ≤ 3 hypotheses that must cite existing excerpt ids, suggestions for gaps, structured extraction from prose in JSON mode.
- Constrain: temperature 0 where possible, JSON mode, reasoning off or low (a flash-class model that reasons by default ate the whole output budget; one provider refuses to disable reasoning and costs 10× for it), timeouts longer than Jev's (minutes, not seconds), a spend cap per round.
- Gate by what the output claims: a proposal that asserts something about the evidence (a hypothesis, an extracted field, a fidelity claim) goes back through Jev or code (route `interpret vs missing`, verify hypotheses at a high floor, verify a literal quote in code before Jev judges fidelity); free-text suggestions that assert nothing are labeled as generated text and left to human review. Rejected proposals stay in the JSON, not in the UI.
- Never feed it the previous score as evidence of quality; send the failed criteria instead.
- Cost shape: the generator is where the money and the wall-clock go (65 s of a 104 s run in one pipeline); Jev in parallel with 6 workers was not the bottleneck.

## Perception and extraction

- Images: describe into `{description, visibleText}` with an instruction not to infer stance, label the field as model output, cap at a few images, video stays a declared gap. Since jev-1.14 the image itself can go to Jev (and a Box can locate a target) behind a danger-zone header on the TypeSafe API; run it in shadow beside the described path and compare on labeled cases before switching (`references/images.md`). Fetch a parent message only after an abstention says the context is missing, then re-judge as a new version.
- Audio: STT with word timestamps; cache by file hash; diarization from a separate service; treat one-segment outputs as a bug of the tool, not of the text.
- Documents: native-text PDF extraction is fast and shuffles tables; regex the units you need (µmol/L, mUI/mL) or the chain silently drops lines; scanned PDFs need OCR or a declared skip; sections by heading with length caps. In two integrations every remaining error was extraction, not judgment: look at the extractor's output before touching a question.
- Web: mirrors over official APIs that 500 for hours; daily CSV dumps over rate-limited endpoints; strip random ports from CDN URLs; dedup amended notices by their solicitation id.

## Retrieval and memory

- Candidates from FTS5 (≤ 30), vectors (≤ 30 per model, union), a project lane, graph activation (decay 0.8 per hop, 3 hops), open threads; superseded items excluded; old lexical hits resolve to the current version.
- Jev for the informed batch over the shortlist and for the gray cosine band; code for the rank, the budget and the fixed layer that never depends on the model.
- Vectors on disk per model, FTS in SQLite WAL, a decision log with hash + answers + cost + latency + `by ∈ {jev, jev-error, embedding, review, code}`.
- Measure shortlist recall separately (does the right item reach the candidates?) before measuring the final choice.

## Storage and corpora

- Receipts: SQLite WAL for a POC, Postgres with an advisory lock for reservations in a service; the raw request and response per call; atomic writes (`.tmp` + rename) for status files.
- Corpora: monthly dumps → Parquet → DuckDB for millions of rows; classify only the slice that survives code filters; cache by `(unit_id, payload hash)` so reruns only touch pending pairs.
- Versions: rubric name in the state, bank hash in every run, `policyVersion` in every record; old runs are labeled "old evaluation", never re-scored silently.

## Interfaces for people

- Lead with coverage and confirmed share, then the score; grey out thin dimensions; show the probability distribution as a diagnostic, never as "quality".
- Human decisions (publish / reject / keep / pin / supersede) live in their own table and log; they promote rules and seed regression cases; they never move a score.
- Views derived from labels in code (what I owe, what changed, what is stale) cost no calls; a period selector defaults to the last 90 days of the source, with "today" = the last event in the source.

## Operating numbers seen across integrations (cases, not limits)

| | |
|---|---|
| Latency per call | p50 0.32–0.56 s at 1–4k tokens; ~0.75 s at 20k tokens with 43 questions; 178 ms median inside a browser loop |
| Throughput | 6 workers ≈ 16 calls/s; 12 ≈ 33 calls/s; zero 429s over 10,840 calls on one route |
| Cost | ~US$ 0.00004–0.0002 per call; 244 µ$ per document for 30 questions; US$ 0.0085 for 334 criteria; under US$ 2 for a seven-year chat export |
| Failure modes | 503 bursts on one gateway; timeouts on slow bodies; 400 on a wrong question schema; reported cost `"0"` on promotional routes |
