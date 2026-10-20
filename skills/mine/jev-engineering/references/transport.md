# Transport: three routes, one model

All three expose the same model id family, but the version actually served, the rounding and the metadata differ by route and can change independently; treat route equivalence as a hypothesis to re-check per model version. Pick by billing, observability and where your keys already live; keep the route in the decision log and the cache key, and re-run your labeled set when you switch (one internal comparison of 150 documents × 6 decisions across two routes gave 135/150 identical answers and no polarity inversion; that is encouraging, not proof).

| | TypeSafe API | OpenRouter Decisions | Vercel AI Gateway |
|---|---|---|---|
| Endpoint | `POST https://api.typesafe.ai/v1/systemone` | `POST https://openrouter.ai/api/alpha/decisions` | `POST https://ai-gateway.vercel.sh/v4/ai/evaluation-model` |
| Auth | `Authorization: Bearer <TYPESAFE_API_KEY>` | `Authorization: Bearer <OPENROUTER_API_KEY>` | `Authorization: Bearer <gateway key>` + headers below |
| Model id | `jev-1.14.0`, `jev-1.13.0`, or the aliases `jev-latest` (→ 1.13 until about 2026-10-21, then 1.14) and `jev-preview` (→ 1.14) | `typesafe/jev-1.14` or `typesafe/jev-1.13` (`jev-latest`, `jev-preview`, `jev-1.14.0` and `typesafe-ai/jev` are not valid here) | header `ai-model-id: typesafe-ai/jev`, `typesafe-ai/jev-1.13.0` or `typesafe-ai/jev-1.14.0` (listed 2026-10-17; the alias returns no dated version) |
| Body | `{model, state, questions}` | `{model, state, questions}` | `{state, questions}` with every `noul` question sent as `type: "boolean"` |
| Extra headers | optional `TypeSafe-Danger-Zone-Images: true`, `TypeSafe-Danger-Zone-Long-Context: true` | optional `HTTP-Referer`, `X-Title` | `ai-gateway-protocol-version: 0.0.1`, `ai-evaluation-model-specification-version: 4`, `ai-gateway-auth-method: api-key` |
| Answers | native shape (below) | native shape; probabilities may be rounded to two decimals and can appear as float noise (`0.9299999999999999`); a `rounding` object may declare the precision | `boolean` answers carry `probability`; `choice`/`score` may omit `confidence`, observed under `providerMetadata.typesafe.confidence[id]` (observed behavior, not a documented guarantee of the generic v4 contract); `score.legend` may be absent |
| Usage | `usage.input_tokens`, `usage.output_tokens` | same, plus `usage.cost` (USD) | `usage.inputTokens`, `usage.outputTokens`; cost in `providerMetadata.gateway.cost` as a string, often `"0"` during promotions or missing |
| Model in response | `model` = versioned id | `model` = versioned id (e.g. `typesafe/jev-1.14-20261014`) | `response.modelId` when present |
| Images and Box | yes, with the images header (multipart or base64 JSON) | **no**: `assets` dropped silently, a Box answers with garbage (live 2026-10-17) | not tested; the bundled clients refuse |
| Dominant failure seen | 429 under burst | 503/524 rare; 400 `invalid_union` when the question schema is wrong | 503 in bursts; timeouts |

## Native answer shape (what the reference clients return on every route)

```json
{
  "is_urgent":  { "type": "noul",   "noul": 0.95 },
  "department": { "type": "choice", "choice": "billing", "probabilities": { "billing": 0.88, "technical": 0.12, "sales": 0.0 }, "confidence": 0.81 },
  "frustration":{ "type": "score",  "score": 1.05, "legend": { "0": "Calm", "1": "Frustrated", "2": "Very angry" }, "probabilities": { "0": 0.0, "1": 0.95, "2": 0.05 }, "confidence": 0.92 }
}
```

- Probabilities and scores arrive rounded to two decimals on every route observed (docs examples, live receipts); some routes declare it in a `rounding` object. The bundled clients validate sums and expectations with that contract (a valid declaration overrides it) and never infer precision from the values; the chosen option must be the exact argmax, because rounding cannot reorder options.
- Score levels are **0-indexed**. If your policy talks in 1–N, add 1 in code once, at the boundary.
- Noul has no `confidence`; its probability is the whole answer.
- Choice/Score `confidence` is derived from the distribution (concentration). It is not accuracy and not permission to act.

## Request schema reminders

- `questions` is a map; the key is yours and is **not shown to the model**. Naming a question `safe_to_publish` adds no instruction. Put the meaning in `instructions`.
- `instructions` may be a string, an object (`{task, target, rubric, boundaries}`) or an array. `criteria`: Choice = map option → description (≤ 255 options); Score = ordered array of 2–10 level descriptions; Noul = optional `{true, false}` descriptions.
- Limits: 32k tokens for `state` + the longest question; 64k for `state` + all questions; 262k for both with `TypeSafe-Danger-Zone-Long-Context: true`. Reference nested fields with backticks (`ticket.messages[0].text`).
- Images (danger zone): a top-level `assets` map `{"<uuid ref>": {"type": "image", "format": "jpg", "data_base64": "..."}}` and the reference written anywhere in `state`, `instructions` or `criteria`; `{"type": "box", "instructions": "the mug in `photo`"}` returns `{"type": "box", "box": {"top", "bottom", "left", "right"}, "confidence"}` on jev-1.14 only. Details in `references/images.md`.
- Bodies may be compressed with `Content-Encoding: gzip` or `zstd` (one layer, zstd window ≤ 8 MiB); the 32 MiB limit applies before and after decompression.
- Every question in a request is evaluated independently against the same `state`; no question sees another's answer. Anything that needs an earlier answer (fetch a document, build new candidates) is a second request.

## Rate and cost facts (checked 2026-09-20; price unchanged for jev-1.14 on 2026-10-17)

- List price US$ 0.042 per million input tokens for both 1.13 and 1.14; output free; image tokens and long-context tokens cost the same. Rate limits published as 250k tokens/s and 1,200 requests/min and described as dynamic.
- Observed in production-style runs: p50 0.3–0.6 s per call at 1–4k tokens; 6 workers ≈ 16 calls/s, 12 workers ≈ 33 calls/s with zero 429s over 10k calls on OpenRouter; batches of ~20k input tokens ≈ 0.75 s.
- The Gateway's promotion reported cost `"0"` (its model page dated the promotion's end to 2026-09-25); one 177-million-token internal run showed US$ 0 while the list price would be ≈ US$ 7.45. A reported zero is a reported zero; a margin needs an invoice.

## Minimal curl (OpenRouter)

```bash
curl -sS https://openrouter.ai/api/alpha/decisions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"typesafe/jev-1.13","state":"Help! My payouts have been failing for 3 days.",
       "questions":{"is_urgent":{"type":"noul","instructions":"Does this convey urgency?",
       "criteria":{"true":"Explicitly time-sensitive","false":"No urgency expressed"}}}}'
```

## Docs

- TypeSafe API and models: https://docs.typesafe.ai/api.md, https://docs.typesafe.ai/models.md
- OpenRouter Decisions: https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-questions-and-answers-request.md
- Vercel AI Gateway model page and the evaluation-model v4 protocol: https://vercel.com/ai-gateway/models/jev, https://github.com/vercel/ai/tree/main/packages/provider/src/evaluation-model/v4

## SDKs

TypeSafe publishes Python and JavaScript SDKs with retries and typed helpers (`Choice`, `Score`, `Noul`, and since 2026-10-14 `Box` and `Image`); see https://docs.typesafe.ai/sdk. Python `typesafe-sdk` 0.7.5 and JavaScript `@typesafe-ai/sdk` 0.7.0 add images (sent as multipart, references generated for you), Box, and zstd request compression by default; the JS 0.7.0 requires Node.js 22+ and no longer exports request payload types. Danger-zone headers go through `extra_headers` (Python) or `{ headers }` (JS) per call. The bundled clients exist for the two proxy routes and for environments without dependencies; they normalize all three routes to the native shape so the rest of the code never branches on the route.
