# Reliability: failure, budget, cache, logging

## Every decision has one of three statuses

| Status | Meaning | What code does |
|---|---|---|
| `decided` | valid receipt, the answer is usable | apply policy |
| `abstained` | valid receipt, the model chose `unknown` / `none` / `not_applicable` / low probability | the existing fallback, a review path, or "not needed" |
| `not_checked` | no valid receipt: timeout, HTTP error, budget exhausted, state too large, malformed answers, key missing | record the reason, run the existing fallback, never convert into `false` or `pass` |

Timeout ≠ no. Missing evidence ≠ false. Malformed ≠ pass. A selected "done" option ≠ done. Each of these was seen collapsing into a silent success in real integrations; the fix is a status column with a reason, not a retry loop.

## Validate the receipt before anything else

Complete answer set (no missing, no extra ids); type matches the question; Noul in [0, 1]; distributions with the exact option keys, summing to one within the route's rounding contract (half of the last rounded decimal per value; two decimals observed on every route; a valid `rounding` declaration in the receipt overrides, an invalid one is ignored); `choice` equal to the exact argmax (rounding cannot reorder options); `score` equal to the expectation of its distribution and within [0, levels−1]; `confidence` in [0, 1]; booleans are not numbers. Reject the whole receipt on any failure. Both bundled clients do this, never infer precision from the values under validation, refuse to cache an invalid receipt, and attach the reported usage and cost to the error so the call is accounted as unresolved. They also require `probabilities` and `confidence` on Choice/Score answers because the gates below need them, even where a proxy schema marks them optional.

## Retries, timeouts, one deadline

- Retry only on 429, 500, 502, 503, 504, 524, 529 and network errors, with backoff (1, 2, 4, 8 s) capped by the time left. Honor `Retry-After` in both forms (seconds and HTTP-date); if it exceeds the remaining deadline, stop and defer instead of sleeping past it.
- 400, 401, 402, 403, 404, 422 are permanent: fix the key, model id or schema. In a pipeline, pause the route instead of burning the queue.
- One deadline for the whole call bounds the connect, the headers, the body read and every backoff; each attempt gets a share of what is left. Typical decisions take 0.2–0.6 s; a 20–30 s deadline is generous. Interactive hooks should use a 3–10 s deadline and degrade explicitly. The TS client relies on an abort signal for the whole fetch; the Python client caps every socket wait at the time left (urllib has no total timeout, so a wait can overrun by at most one socket operation).
- Do not retry an **action** because a decision timed out. Decisions are idempotent; the actions they trigger are not.

## Actions with side effects: verify before retry

A tool call can execute and still time out on the response. Before repeating any consequential action: give it an operation id before the first attempt; inspect the target's current state; classify as confirmed-complete (return the existing receipt), confirmed-not-executed (retry within scope), retry-safe by idempotency contract (reuse the key, then verify), or outcome-unknown (stop, ask a human). Completion is a receipt read from the world: the exported file, the stored row, the setting re-read. A Jev answer can propose `done`; only the receipt confirms it.

## Budget ledger

- Reserve **before** the HTTP call from a workload-tested estimate with margin; settle from `usage` after. The bundled `estimate_tokens` (bytes / 3.5 × 1.2 + margin) is a starting heuristic, not a proven upper bound: compare it with your first receipts, record the observed error, and provision for retries.
- Settle at zero only when the error provably preceded inference (a 4xx rejected at the edge). A 5xx, a timeout, or an unreadable receipt keeps the reservation as **unresolved** until reconciled against the provider's usage or invoice.
- Keep three cost states apart: reported (a number the route returned, including a reported `"0"`), missing (the route returned nothing), and reconciled (matched to an invoice). The clients return `cost` + `cost_known` for the first two; reconciliation is your ledger's job. Promotions that report `"0"` end (the Vercel Gateway page dated its promotion to 2026-09-25); a zero you have not reconciled is not a margin.
- Daily and monthly caps per route with alerts at levels you choose; `budget_exhausted` is a `not_checked` status with a retry-after, not an error loop.
- A formula that reserved `bytes × 30 + 32000` tokens overestimated 14× against real usage; 394 failed calls then held 46 million reserved tokens and starved 2,758 real analyses. Reserve from evidence, and release reservations on failure paths deliberately.
- Cost per successful task = every model, tool, retry and review cost ÷ verified acceptable completions, failed attempts in the numerator. That is the number that decides adoption, not price per call.

## Cache and versioning

- Key = hash(route, model, revision, sanitized state, questions). Include the questions: changing one word is a new decision. Include a `revision` you bump when policy or rubric semantics change without text changes, or when the alias behind a route moves.
- Aliases (`jev-latest`, `jev-preview`, `typesafe-ai/jev`) move when a release ships (`jev-latest` from 1.13 to 1.14 announced for about a week after 2026-10-14), and a cache keyed on the alias keeps serving the old model's answers. For active use, pin a versioned model id (or bump `revision` on each release) and store the versioned id the response reported next to the answers; a cache hit cannot observe a model change.
- Store the request next to the response; a cache that only keeps answers cannot be audited. Hand out copies, never the stored object (the TS client's memory cache clones on get and set). Decide retention and invalidation before enabling a persistent cache by default.
- Cache hit returns `latency 0` and `cost 0` **flagged as a hit**; a replay of a cached run is not a cost measurement. Keep one cold run per rubric version for the real numbers.
- Never cache an invalid receipt or an error.
- Version question banks in files (`version` field + file hash). Reanalysis policy: when the bank or model changes, re-decide recent items in bounded batches, keep old receipts for audit.

## Decision log (one row per call)

`request_hash`, `question_version`, `route`, `model_requested`, `model` (from the response, null when not reported), `latency_ms`, `input_tokens`, `output_tokens` (null when not reported), `cost`, `cost_known`, `cache_hit`, `status` (decided / abstained / not_checked + reason), `route_taken` (policy branch), and later `verified_outcome`. With these columns you can replay, compare rubric versions, and compute cost per verified task.

## Secrets and content safety

- Keep credentials out of state at the source. The bundled clients add a best-effort layer: configured keys are removed anywhere in the payload (map keys included), values of secret-looking field names (`password`, `token`, `api_key`, `authorization`, …) are replaced, a few token shapes are masked, and the request is refused if a configured key survives. Business text such as `token=invoice` is preserved. Make the field-name policy match your domain and test both false positives and false negatives.
- Keys stay server-side. Browser apps proxy through your backend.
- State is data, and the model does not treat it as hostile; the docs say adversarial content "can move the answer". Keep the guard prefix on every question, test with documents that contain instructions, measure how often the answer moves, and gate unsafe actions on more than one signal.

## Concurrency

Independent decisions run in parallel safely; 6–12 workers were sustained without 429s at 16–33 calls/s in one workload. Batch independent questions about the same state into one request (they run in parallel inside the model and add little latency); stage a second request only when a question needs an earlier answer.
