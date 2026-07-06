---
name: spec-peer-review
description: >-
  Runs an optional cross-LLM peer review of a spec (TechSpec, design doc, RFC, or detailed
  PRD) via `compozy exec` and requires the reviewer to write one scoped Markdown findings
  artifact for user-directed incorporation. The reviewer runtime is configurable through
  --ide / --model / --reasoning (defaults claude / opus / xhigh). Project-agnostic: works in
  any repo, auto-discovers project rule files (CLAUDE.md, AGENTS.md, .cursor/rules,
  CONTRIBUTING.md), and writes artifacts to --out, an auto-detected .compozy/tasks/<slug>/qa/
  layout, or a .peer-reviews/<timestamp>/ fallback. Use when a spec draft has already been
  approved by the user and they want an external review round, especially for
  autonomy/network/security/migration-impacting designs. Do not use for implementation/diff
  review (use impl-peer-review), automatic approval gates, or auto-looped review cycles.
trigger: explicit
argument-hint: "[spec-path] [--context p1,p2] [--out dir] [--ide <ide>] [--model <model>] [--reasoning <effort>]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---

# Spec Peer Review

A capable authoring model drafts a spec; a second, independent model pressure-tests it. This
skill runs that cross-LLM pressure-test only when the user explicitly asks for a review round
after approving the current draft. It does not auto-run, auto-incorporate findings, or
auto-loop additional rounds.

The skill is harness-agnostic and project-agnostic. It uses **Compozy as the review engine**:
each round runs one `compozy exec` against a configurable runtime (`--ide`/`--model`/
`--reasoning`). The review result is a direct-written Markdown findings file. `compozy exec`
stdout/stderr is operational evidence only; never parse it as the review source of truth.

## Required Reading Router

Match your step to the row. Read the listed file **in full before** acting. These files are
load-bearing, not appendices — the inline text in this SKILL.md is a pointer, not a substitute.

| Step                                            | MUST read                                |
| ----------------------------------------------- | ---------------------------------------- |
| Step 1.4 — assessing spec readiness             | `references/quality-markers.md`          |
| Step 2 — composing the review prompt            | `references/peer-review-prompt.md`       |
| Step 4 — validating findings                    | `scripts/validate-findings.sh` (run it)  |

## Reference Index

- `references/quality-markers.md` — the six tech-agnostic markers a spec must carry before
  review (scope boundary, architectural boundaries, concrete contracts, data-model/migration
  rationale, ownership decisions, numbered safety invariants). The Step 1 readiness gate; the
  markers are **not** inlined here.
- `references/peer-review-prompt.md` — the canonical executable reviewer prompt template,
  including the scoped-write contract and the exact findings-file format. Its placeholders are
  substituted verbatim; never paraphrase it.
- `scripts/validate-findings.sh` — read-only structural validator for the findings artifact
  (frontmatter, required sections, no placeholders). Run it; never edit it.

## User Decisions

When this skill instructs the agent to ask whether to incorporate findings or run another
round, it MUST use the runtime's dedicated interactive question tool — the tool or function
that presents a question to the user and pauses execution until the user responds (for
example AskUserQuestion).

If the runtime does not provide such a tool, present the question as the complete assistant
message and stop generating. Do not answer the question on the user's behalf.

## Bundled Path Rule

Resolve every bundled helper relative to the directory that holds this `SKILL.md`. When a
command below appears as `scripts/<name>` or `references/<name>`, expand it to the absolute
skill directory before reading or running it:

```bash
bash <skill-dir>/scripts/validate-findings.sh --kind techspec --round <N> --path <findings-path>
```

The validator is a read-only helper: it inspects the findings artifact and exits non-zero on
structural contract violations.

## Inputs

- **spec-path** (optional): explicit path to the spec under review (a TechSpec, design doc,
  RFC, or detailed PRD). When omitted, auto-resolve to the most recently modified
  `.compozy/tasks/<slug>/_techspec.md` **if** that layout exists; otherwise ask the user for
  a path. Never invent a path.
- `--context <p1,p2,...>` (optional): additional context files to feed the reviewer (ADRs,
  related specs, RFCs, research, design docs). The skill never assumes any of these exist.
- `--out <dir>` (optional): output directory for round artifacts. See Output Directory.
- `--ide <ide>` (optional, default `claude`): reviewer runtime, forwarded to `compozy exec
  --ide`. Accepted values mirror `compozy exec`: `codex`, `claude`, `cursor-agent`, `droid`,
  `opencode`, `pi`, `gemini`, `copilot`. Reject an invalid value rather than falling back.
- `--model <name>` (optional, default `opus`): forwarded to `compozy exec --model`. Do not
  pre-validate; let `compozy` surface incompatibilities.
- `--reasoning <effort>` (optional, default `xhigh`): forwarded to `compozy exec
  --reasoning-effort`. Accepted: `low`, `medium`, `high`, `xhigh`.

## Output Directory

Resolve `<out>` in this order:

1. `--out` if provided.
2. Otherwise, if the spec resolves under a `.compozy/tasks/<slug>/` layout, use that task's
   `qa/` directory: `.compozy/tasks/<slug>/qa/`.
3. Otherwise, default to `.peer-reviews/<UTC-timestamp-YYYYMMDDTHHMMSSZ>/` at the repository
   root.

Create the directory if it does not exist.

## Findings Artifact Contract

Each review round has exactly one authoritative findings file:

```
<out>/peer-review-findings-roundN.md
```

The reviewer may write exactly that file and no other file. If the target path is missing,
ambiguous, unwritable, or outside the resolved `<out>` directory, the reviewer must refuse and
stop. It must not print findings to stdout as a fallback.

The findings file MUST use this structure:

```markdown
---
schema_version: 1
review_kind: techspec
round: N
readiness: READY|BLOCKED|NEEDS_REWORK
reviewer_runtime: claude
reviewer_model: opus
generated_at: <ISO-8601 timestamp>
---

# Summary

# Blockers

# Nits

# Evidence

# Deferred Or Follow-Up
```

Every blocker and nit must include an ID, a real section/path reference, the issue, and a
concrete suggested fix. Blockers must also include the rationale for why the issue blocks
approval.

## Procedures

**Step 0: Verify Compozy is available**

1. Confirm the `compozy` binary is on `PATH` (e.g. `command -v compozy`). If missing, abort
   with a one-line message instructing the user to install Compozy. Do not fall back to a
   harness-native subagent — the cross-LLM independence is the point.
2. No agent install is required: this skill calls `compozy exec` directly (no `--agent`).

**Step 1: Validate Input and Context**

1. Resolve `spec-path` (see Inputs). If omitted and no `.compozy/tasks/<slug>/_techspec.md`
   exists, ask the user for a path and stop.
2. Confirm the user has already approved the current draft or explicitly asked to review the
   saved spec as-is.
3. Read the spec and confirm it is a final-shape design (has sections covering boundaries,
   implementation/plan, and verification/test strategy) — not a rough draft.
4. **STOP. Read `references/quality-markers.md` in full before assessing readiness.** The six
   markers are defined there, not here. Verify the spec carries all six. If any marker is
   missing, report the missing markers and ask the user whether to amend the spec first or
   proceed anyway — do not silently abort, and do not silently proceed.
5. Resolve `<out>` (see Output Directory) and ensure it exists and is writable.
6. Determine the next review round number by listing existing
   `<out>/peer-review-findings-round*.md` and `<out>/peer-review-summary-round*.md` files.
   Start at `round1` when none exist.

**Step 2: Compose the Review Prompt**

1. **STOP. Read `references/peer-review-prompt.md` in full before composing the prompt.** It is
   the canonical executable reviewer prompt template; substitute its placeholders verbatim and
   do not paraphrase it. The assembled prompt must start with the reviewer instructions, not
   with a Markdown wrapper describing the template.
2. Define the round artifact paths under `<out>/`: `peer-review-findings-roundN.md`,
   `peer-review-events-roundN.jsonl` (event log), `peer-review-result-roundN.err` (stderr),
   `peer-review-status-before-roundN.txt`, `peer-review-status-after-roundN.txt`, and
   `peer-review-validation-error-roundN.md` (only when needed).
3. Discover project rule files that exist to populate `{project_rules}`: root-level
   `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.cursorrules`, `CONTRIBUTING.md`, PLUS
   nested `CLAUDE.md`/`AGENTS.md` in the areas the spec touches, PLUS any project
   memory/directive docs the repo keeps (e.g. `docs/_memory/`, standing directives, lessons
   indexes). Nested and memory rules are where load-bearing invariants usually live.
4. Substitute the placeholders:
   - `{spec_path}` — exact path to the spec under review.
   - `{context_paths}` — newline-separated paths from `--context`, or the literal `none`.
     **Spec-corpus rule:** when the spec resolves under a spec directory (e.g.
     `.compozy/tasks/<slug>/`), resolve its sibling corpus artifacts — requirements/use-case
     documents, canonical example documents, input tables, QA seeds, test contracts,
     analysis summaries, ADRs — and include them here even when the user passed no
     `--context`. A spec reviewed in isolation from its own corpus lets paraphrase drift
     and requirement contradictions pass unseen.
   - `{project_rules}` — newline-separated discovered rule-file paths, or `none`.
   - `{findings_path}` — exact absolute path to `<out>/peer-review-findings-roundN.md`.
   - `{round}` — numeric review round `N`.
5. Write the assembled prompt to `<out>/peer-review-prompt-roundN.md`.

**Step 3: Execute the Cross-LLM Review**

1. Capture the pre-run status snapshot:

   ```bash
   git status --short > <out>/peer-review-status-before-roundN.txt
   ```

2. Run (substitute the resolved `--ide`/`--model`/`--reasoning`, defaults `claude`/`opus`/`xhigh`):

   ```bash
   compozy exec --ide <ide> --model <model> --reasoning-effort <reasoning> --format json --prompt-file <out>/peer-review-prompt-roundN.md > <out>/peer-review-events-roundN.jsonl 2> <out>/peer-review-result-roundN.err
   ```

3. Capture the post-run status snapshot:

   ```bash
   git status --short > <out>/peer-review-status-after-roundN.txt
   ```

4. If the command returns a non-zero exit code, fail loudly. Do not retry silently. Inspect
   stderr for model misconfiguration (see Error Handling).
5. Treat `peer-review-events-roundN.jsonl` as operational evidence only. Do not parse it for
   readiness or findings.
6. Require the findings target file to exist after the command exits. If missing, the round is
   invalid even when `compozy exec` exited 0.

**Step 4: Validate and Summarize Findings**

1. Run the bundled read-only validator:

   ```bash
   bash <skill-dir>/scripts/validate-findings.sh --kind techspec --round N --path <out>/peer-review-findings-roundN.md
   ```

2. Manually inspect the findings file and verify the semantic contract:
   - every finding has a real section/path reference;
   - blockers include a rationale tied to project rules or architecture constraints;
   - no `TBD`, placeholder text, invented paths, or stdout-only findings;
   - when sibling corpus artifacts were passed in `{context_paths}`, the findings explicitly
     assess the spec's consistency with them (requirements honored, canonical contracts not
     diluted, concrete artifacts wired as required reading for implementers) — a `READY`
     verdict with no corpus-consistency assessment is an invalid round;
   - comparing the pre/post status snapshots shows no changes outside the expected review
     artifact/log paths.
3. If validation fails, write `<out>/peer-review-validation-error-roundN.md` with the failed
   checks, command, exit status, and artifact paths. Do not summarize the round as `READY`.
4. Write `<out>/peer-review-summary-roundN.md` from the validated findings file with: the
   readiness verdict (`READY` / `BLOCKED` / `NEEDS_REWORK`); one-line rationale per blocker;
   the nits list; sections/ADRs likely affected; and the operational artifact paths.
5. Present a concise user-facing summary: verdict, blocker/nit counts, main themes, and the
   artifact paths written for the round.
6. Do NOT modify the spec or any ADRs yet.

**Step 5: User-Directed Incorporation**

1. Ask the user which findings to incorporate:
   - A) all blockers
   - B) selected blockers/nits
   - C) nothing
   - D) manual edits before any incorporation
2. Apply only the findings the user selected. Do not silently apply all blockers or all nits.
3. If incorporation requires an ADR or related-doc update, update only the docs tied to the
   selected findings.
4. Record the incorporation decision in `<out>/peer-review-incorporation-roundN.md`, listing
   incorporated items, deferred items, and files changed.
5. Show the user what changed and what remains deferred.

**Step 6: Optional Additional Rounds**

1. Ask whether the user wants another peer-review round or wants to stop with the current
   saved spec.
2. If the user requests another round, re-run from Step 2 against the updated spec and create
   a fresh `roundN+1` artifact set in the same `<out>` directory.
3. Do not auto-loop. The user explicitly requests further rounds.

## Critical Rules

- This skill never commits, pushes, opens PRs, or auto-approves specs.
- Prompt, event log, findings, summary, incorporation, and status snapshot artifacts are
  versioned with `-roundN`. Never overwrite a prior round.
- The `compozy exec` call is the only place this skill spends external review credit. Do not
  invoke it more than once per round unless the round is explicitly invalid and the user
  requests a rerun.
- The bundled helper paths (`references/peer-review-prompt.md`, `references/quality-markers.md`,
  `scripts/validate-findings.sh`) are read-only templates/helpers — read or run them, never
  edit them during a review round.
- For specs living in a spec directory, a round whose `{context_paths}` omitted the sibling
  corpus is an invalid round. Real incident: a task decomposition paraphrased its spec's
  canonical example document without linking it; the implementer built from the paraphrase,
  seven implementation-review rounds reached `SHIP`, and the shipped result contradicted the
  product contract wholesale. Spec review is the earliest gate that can catch a decomposition
  that fails to wire its canonical artifacts.

## Error Handling

- **Compozy not found:** abort with a one-line install hint rather than swallowing or falling
  back to a harness-native subagent.
- **Model misconfiguration (`The model 'X' does not exist`):** stop and surface the configured
  model. The runtime may be set to a stale name. Do not mutate the call to substitute a
  model — verify with the user and record the failure in the round artifacts.
- **`--ide` invalid:** list the accepted values and ask the user to choose; do not fall back
  silently to `claude`.
- **Quality markers missing:** report the missing markers and ask whether to amend or proceed.
  Do not silently run the review on an incomplete spec.
- **Missing findings file:** treat as an invalid round, not a clean review. Write a
  validation-error artifact and ask whether to rerun.
- **Malformed findings frontmatter or missing required sections:** treat as an invalid round.
  Do not infer readiness from stdout.
- **Empty or placeholder findings:** treat empty `# Blockers` or `# Nits` sections as
  acceptable only when the section explicitly says `None.`; reject `TBD`, `TODO`, or vague
  placeholders.
- **Existing peer-review files:** never overwrite. All round artifacts are versioned with
  `-roundN`.
