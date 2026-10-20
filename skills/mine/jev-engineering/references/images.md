# Images, Box and long context (danger zone, jev-1.14)

TypeSafe released these on 2026-10-14 behind "danger zone" request headers: features they intend to keep and improve, but too jagged for them to vouch for in production. Design around that. Use them for POCs, prototypes and shadow runs; keep a text path (vision model → labeled fields, `references/state.md`) wherever an image decision acts in the world, until your labeled set says otherwise. Docs: https://docs.typesafe.ai/images.md, https://docs.typesafe.ai/primitives/box.md, https://docs.typesafe.ai/models.md#long-context.

## What is new

| Feature | Header (each request) | Models | Notes |
|---|---|---|---|
| Images anywhere text goes: `state`, `instructions`, `criteria` | `TypeSafe-Danger-Zone-Images: true` | jev-1.13.0 and jev-1.14.0 | without the header the API answers 400 "Images are experimental" |
| `box` question type: one bounding box per question | same images header | jev-1.14.0 only (`jev-preview`) | on jev-1.13.0 a Box answers 400 with a bare "Invalid request." |
| Long context: 262k tokens per request and per question | `TypeSafe-Danger-Zone-Long-Context: true` | both | same price per token; slower and less accurate than the default 64k request / 32k question |
| Opt-in to share queries for debugging | console setting, not a header | — | TypeSafe still does not train on queries |

## Routes (checked live 2026-10-17)

- **TypeSafe API** (`api.typesafe.ai/v1/systemone`): images, Box and long context all work, both as multipart (what the SDKs send) and as base64 inside JSON (what the bundled clients send).
- **OpenRouter Decisions**: `typesafe/jev-1.14` answers text (reports `typesafe/jev-1.14-20261014`), and accepts a Box question, but **silently drops `assets`**: the same request billed 305 input tokens instead of ~1.6k and returned a box at confidence 0.03 in the wrong corner. Never send images there; the bundled clients refuse before the network.
- **Vercel AI Gateway** lists `typesafe-ai/jev-1.14.0`; images there were not tested. The bundled clients refuse images on it until someone verifies it.
- A check that catches a dropped image on any route: `usage.input_tokens` must grow by roughly the image's token cost (below). A receipt with an image that costs text-only tokens is a failure, not an answer.

## Request shape

```json
{
  "model": "jev-1.14.0",
  "state": { "photo": "6e1d0b7c-4f1a-4c55-9d1e-2b9a0f3c7e11" },
  "assets": { "6e1d0b7c-4f1a-4c55-9d1e-2b9a0f3c7e11": { "type": "image", "format": "jpg", "data_base64": "/9j/4AAQ..." } },
  "questions": {
    "mug_visible": { "type": "noul", "instructions": "Is there a coffee mug in `photo`?" },
    "mug": { "type": "box", "instructions": "the coffee mug in `photo`" }
  }
}
```

- References are plain text replaced anywhere in strings (not in object keys), whole values first. Use a fresh UUID per image per request: a short word like `cat` also matches inside `category`.
- Every asset must be referenced (400 otherwise). Each use of a reference adds the image again to what the model reads and to the size limits: an image several questions need goes once in `state`, and the questions point at it by path (`` `frames[2].frame` ``).
- Choice option names stay text; put a picture in the option's description (`{"thumbs_up": "<ref>"}` or `{"open_palm": {"description": "...", "examples": ["<ref1>", "<ref2>"]}}`). Score levels and Noul `true`/`false` take pictures the same way. Answers echo the reference, never the image.
- Box answer: `{"type": "box", "box": {"top", "bottom", "left", "right"}, "confidence"}`, edges as fractions of height/width from the top-left corner. Multiply by the pixel size to crop.

## Limits and preparation

- PNG or JPEG stills; 280–1568 px on each side; 16 MiB per file; request body 32 MiB (base64 adds a third). Outside the range the API rejects, never resizes, and one bad image fails the whole request.
- The API strips EXIF and does not apply orientation: rotate the pixels upright, resize the longest side to ≤ 1568, save as baseline JPEG or PNG before sending. Convert GIF/WebP/HEIC; export video frames as stills.
- Image tokens are billed as input tokens. Measured 2026-10-17 on jev-1.14.0: 280×280 ≈ 216, 800×600 ≈ 1.3k, 1568×1176 ≈ 4.7k, 1568×1568 ≈ 6.3k tokens, i.e. about `width × height / 390`. A full-size image costs ≈ US$ 0.00026 and five of them fill a 32k question. TypeSafe has not published an estimator yet; the bundled `estimate_tokens` uses this fit with a 1.2 margin.

## Patterns that fit Jev

| Pattern | How | Where the image goes |
|---|---|---|
| Presence + location | A Noul "is there a X in `photo`?" next to the Box; ignore the box when the Noul is low. A Box always returns four edges, even for an absent target | `state` |
| Compare with a known picture | "Is the person in `door` the same as in this badge photo: <ref>?" | known picture in `instructions`, live one in `state` |
| Options by example | Choice options defined by one or a few example pictures | `criteria` |
| What changed | A short frame history, oldest first, with `seconds_ago`; ask about arrivals, motion, differences | `state` |
| Look closer when needed | Ask on a small copy first; send a larger copy or a full-resolution crop only when the answer needs it | `state` |
| Search a large image | Tiles as Choice options; recurse into the chosen tile; then Box on the tile and convert edges back to the full image | `criteria`, then `state` |
| Check a box | Crop to the box and ask one Noul per edge ("does X continue past the left edge?"); move out each edge that answers yes. TypeSafe's test: 30/36 cuts caught with four edge Nouls, 26 with one "all inside?" Noul, 20 by drawing the box on the image | crop in `state` |
| Several of the same thing | Describe the one you want ("the mug nearest the sink"); or a Choice `none / one / several` beside the Box and split the image into regions when `several` | `state` |

Rules from the general skill still apply, harder: decompose into the simplest questions (TypeSafe's own warning: every model is worse on images than on text), keep counting and geometry in code (Box returns edges; overlap, area and distance are arithmetic), and tune Box confidence thresholds on your own images (there is no recommended value; one live Box on a clean synthetic red rectangle came back right at confidence 0.46–0.54, so low confidence is not the same as wrong).

## Long context

Turn it on per request, only where splitting would destroy the decision (a whole contract, a full transcript). One live needle test: a 228k-token state with one termination clause among 9,000 distractor lines answered 0.96 (1.14) and 0.97 (1.13) in ~3.9 s for ≈ US$ 0.0096. One needle is not a calibration: the docs and `references/state.md` still hold that irrelevant detail lowers accuracy, so prefer partitioned states and compare long against partitioned on your labeled set before relying on it. Long context changes the request, so it is part of the cache key.

## Logging

Add to the decision log: the image digests (sha256 of the bytes, never the base64), each image's size, which danger-zone headers were sent, and the versioned model id. A rubric that worked on 1.13 images must be re-run on 1.14 before the alias moves.
