---
name: spec-peer-review
description: "Run one requested external review of an approved spec, design doc, RFC, or detailed PRD; produce findings for user-selected incorporation. Excludes implementation reviews and automatic or looping approval gates."
disable-model-invocation: true
argument-hint: "[spec-path] [--context p1,p2] [--out dir] [--ide <ide>] [--model <model>] [--reasoning <effort>]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---

# Spec Peer Review

Review a saved design only when the user requests an independent review. Honor existing approval to review it as-is. Incorporate only selected findings; additional rounds remain opt-in.

## Inputs and output

- Resolve the spec from the request or active context. Ask only when ambiguous.
- Accept additional context and an output directory. Default to the spec's `qa/` directory for `.compozy/tasks/<slug>/`, otherwise `.peer-reviews/<UTC-timestamp>/`.
- Use the configured reviewer runtime/model and reasoning. Explicit overrides win; never pin a historical model or silently replace a user-selected model.
- Keep one findings artifact per round: `<out>/peer-review-findings-roundN.md`. Preserve prior rounds.

## Review

1. Read the spec and its linked contract index. Include relevant requirements, concrete examples, test contracts, ADR decisions, and the instructions for affected surfaces. Expand into other context when a dependency or contradiction needs it; do not load every memory file.
2. Use the applicable markers in `references/quality-markers.md`; missing contracts become findings, not an automatic stop before a requested review.
3. Read `references/peer-review-prompt.md` and fill its placeholders, including exact findings path, round, resolved runtime/model, and context paths. The reviewer may write only that findings file.
4. Launch through the available independent reviewer runtime (a configured native reviewer, Compozy session, or herdr TUI). Use that runtime's documented commands; do not assume a retired `compozy exec` API. Preserve existing worker identity for follow-up rounds when available.
5. Inspect the findings, cited evidence, and changed paths. Validate the artifact:

   ```bash
   bash <skill-dir>/scripts/validate-findings.sh --kind techspec --round <N> --path <out>/peer-review-findings-roundN.md
   ```

6. Report the verdict, material findings, limitations, and artifact path. Missing/malformed output is an incomplete review, never `READY`. Repair an operational failure within the authorized round; do not start additional substantive rounds automatically.
7. Apply only user-selected findings and record the disposition with changed paths. Reuse authorization already given; ask only for a selection that is still missing. On an explicitly requested next round, send changed files, prior findings/disposition, and the new output path rather than the unchanged corpus again.

This skill does not authorize commits, publishing, or approving a design. A real product/security/compatibility constraint can block readiness; missing ritual sections and stylistic preferences cannot.
