---
name: impl-peer-review
description: >-
  Runs an optional cross-LLM peer review of an implemented change (the diff) via `compozy
  exec` and requires the reviewer to write one scoped Markdown findings artifact for
  user-directed remediation. The reviewer runtime is configurable through --ide / --model /
  --reasoning (defaults claude / opus / xhigh) and the verification gate through --verify.
  Project-agnostic: works in any repo and any language, auto-discovers project rule files
  (CLAUDE.md, AGENTS.md, .cursor/rules, CONTRIBUTING.md), auto-detects the verify command, and
  writes artifacts to --out, an auto-detected .compozy/tasks/<slug>/qa/ layout, or a
  .peer-reviews/<timestamp>/ fallback. Use after any implementation pass (feature, bug fix,
  refactor) when the user explicitly asks for an external review of the diff before commit or
  PR. Do not use for spec/TechSpec review (use spec-peer-review), automatic remediation, or
  auto-looped review cycles.
trigger: explicit
argument-hint: "[--files p1,p2] [--context p1,p2] [--base ref] [--staged] [--out dir] [--verify cmd] [--ide <ide>] [--model <model>] [--reasoning <effort>]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---

# Implementation Peer Review

An independent model pressure-tests an implementation diff. This skill runs that
cross-LLM pressure-test only when the user explicitly asks for a review round after an
implementation pass. It is decoupled from any task-tracking system — the scope is the diff
itself plus any optional context files the user names. The skill never auto-runs,
auto-incorporates findings, auto-commits, or auto-loops additional rounds.

The skill is harness-agnostic and project-agnostic. It uses **Compozy as the review engine**:
each round runs one `compozy exec` against a configurable runtime (`--ide`/`--model`/
`--reasoning`). The review result is a direct-written Markdown findings file. `compozy exec`
stdout/stderr is operational evidence only; never parse it as the review source of truth.

## Required Reading Router

Match your step to the row. Read the listed file **in full before** acting. These files are
load-bearing, not appendices — the inline text in this SKILL.md is a pointer, not a substitute.

| Step                                            | MUST read                                |
| ----------------------------------------------- | ---------------------------------------- |
| Step 1.5 — gating readiness before review       | `references/readiness-checks.md`         |
| Step 2 — composing the review prompt            | `references/impl-review-prompt.md`       |
| Step 4 — validating findings                    | `scripts/validate-findings.sh` (run it)  |

## Reference Index

- `references/readiness-checks.md` — the language-agnostic readiness markers that gate whether
  review credit is spent at all (build/test gate, non-empty diff, no stray artifacts, no WIP
  markers, generated-artifact co-ship, reviewable size). The highest-value forced read in this
  skill; the markers are **not** inlined here.
- `references/impl-review-prompt.md` — the canonical executable reviewer prompt template,
  including the scoped-write contract and the exact findings-file format. Its placeholders are
  substituted verbatim; never paraphrase it. (Over 100 lines — has its own `## Contents`.)
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
bash <skill-dir>/scripts/validate-findings.sh --kind implementation --round <N> --path <findings-path>
```

The validator is a read-only helper: it inspects the findings artifact and exits non-zero on
structural contract violations.

## Inputs

All inputs are optional. Defaults make the common path `impl-peer-review` with no arguments.

- `--files <p1,p2,...>` — scope the review to explicit paths instead of the full branch diff.
- `--context <p1,p2,...>` — additional context files to feed the reviewer (a spec, ADR, design
  doc, RFC, README). The skill never assumes any of these exist.
- `--base <git-ref>` — base ref for the diff. Defaults to `main`. Use `--base HEAD~N` for a
  narrower scope.
- `--staged` — review staged changes only (`git diff --staged`) instead of a branch diff.
- `--out <dir>` — output directory for round artifacts. See Output Directory.
- `--verify <cmd>` — the verification command (build/tests) used as the readiness gate and the
  post-remediation gate. When omitted, auto-detect (see `references/readiness-checks.md`); if
  none can be resolved, ask the user.
- `--ide <ide>` (default `claude`): reviewer runtime, forwarded to `compozy exec --ide`.
  Accepted values mirror `compozy exec`: `codex`, `claude`, `cursor-agent`, `droid`,
  `opencode`, `pi`, `gemini`, `copilot`. Reject an invalid value rather than falling back.
- `--model <name>` (default `opus`): forwarded to `compozy exec --model`. Do not pre-validate;
  let `compozy` surface incompatibilities.
- `--reasoning <effort>` (default `xhigh`): forwarded to `compozy exec --reasoning-effort`.
  Accepted: `low`, `medium`, `high`, `xhigh`.

## Output Directory

Resolve `<out>` in this order:

1. `--out` if provided.
2. Otherwise, if the repo exposes an unambiguous `.compozy/tasks/<slug>/` layout for the
   current work, use that task's `qa/` directory: `.compozy/tasks/<slug>/qa/`.
3. Otherwise, default to `.peer-reviews/<UTC-timestamp-YYYYMMDDTHHMMSSZ>/` at the repository
   root.

Create the directory if it does not exist.

## Findings Artifact Contract

Each review round has exactly one authoritative findings file:

```
<out>/impl-review-findings-roundN.md
```

The reviewer may write exactly that file and no other file. If the target path is missing,
ambiguous, unwritable, or outside the resolved `<out>` directory, the reviewer must refuse and
stop. It must not print findings to stdout as a fallback.

The findings file MUST use this structure:

```markdown
---
schema_version: 1
review_kind: implementation
round: N
verdict: SHIP|FIX_BEFORE_SHIP|REWORK
reviewer_runtime: claude
reviewer_model: opus
generated_at: <ISO-8601 timestamp>
---

# Summary

# Blockers

# Risks

# Nits

# Evidence

# Deferred Or Follow-Up
```

Every blocker, risk, and nit must include an ID, a real file path and line when applicable,
the issue, and a concrete suggested fix. Blockers must also include the rationale for why the
issue blocks shipment.

## Procedures

**Step 0: Verify Compozy is available**

1. Confirm the `compozy` binary is on `PATH` (e.g. `command -v compozy`). If missing, abort
   with a one-line message instructing the user to install Compozy. Do not fall back to a
   harness-native subagent — the cross-LLM independence is the point.
2. No agent install is required: this skill calls `compozy exec` directly (no `--agent`).

**Step 1: Validate Input and Compute Scope**

1. Confirm the user has just completed (or paused) the implementation pass and explicitly
   asked to review the current state. Do not run review rounds during active editing.
2. Resolve the diff scope:
   - If `--files` is provided, verify each path exists and limit the diff to those paths.
   - If `--staged` is provided, use `git diff --staged`.
   - Otherwise run `git diff <base>...HEAD --name-only` (default `<base>` is `main`) to compute
     the changed file set. If the diff is empty, abort and tell the user there is nothing to
     review.
3. Resolve `<out>` (see Output Directory) and create it if needed.
4. Resolve the verification command (`--verify`, else auto-detect, else ask the user).
5. **STOP. Read `references/readiness-checks.md` in full before running the review — a red gate
   wastes external credit.** Verify every readiness marker passes (build/tests green via the
   resolved verify command, non-empty diff, no stray tracking artifacts, no WIP markers,
   generated-artifact co-ship if codegen sources touched, reviewable size). The marker details
   live in that file, not here. If any marker fails, report the failed markers and abort —
   external review on a broken or incomplete change wastes credit and produces noise.
6. Determine the next review round number by listing existing
   `<out>/impl-review-findings-round*.md` and `<out>/impl-review-summary-round*.md` files.
   Start at `round1` when none exist.

**Step 2: Compose the Review Prompt**

1. **STOP. Read `references/impl-review-prompt.md` in full before composing the prompt.** It is
   the canonical executable reviewer prompt template; substitute its placeholders verbatim and
   do not paraphrase it. The assembled prompt must start with the reviewer instructions, not
   with a Markdown wrapper describing the template.
2. Capture the diff payload:
   - Run `git diff <base>...HEAD -- <changed-files>` (or `git diff --staged -- <changed-files>`
     for `--staged`) and write the raw patch to `<out>/impl-review-diff-roundN.patch`.
   - Run `git log --oneline <base>...HEAD -- <changed-files>` and capture the commit list
     (empty string if `--staged`).
3. Define the round artifact paths under `<out>/`: `impl-review-findings-roundN.md`,
   `impl-review-events-roundN.jsonl` (event log), `impl-review-result-roundN.err` (stderr),
   `impl-review-status-before-roundN.txt`, `impl-review-status-after-roundN.txt`, and
   `impl-review-validation-error-roundN.md` (only when needed).
4. Discover project rule files that exist to populate `{project_rules}`: root-level
   `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.cursorrules`, `CONTRIBUTING.md`, PLUS
   nested `CLAUDE.md`/`AGENTS.md` files in the directories the diff touches, PLUS any
   project memory/directive docs the repo keeps (e.g. `docs/_memory/`, standing directives,
   lessons indexes). Nested and memory rules are where load-bearing invariants usually live —
   root-only discovery misses them.
5. Substitute the placeholders in the prompt template:
   - `{scope_summary}` — one-paragraph description of what was implemented. Derive from the
     user's brief, the commit messages, or — if `--context` was passed — the linked spec/PRD.
   - `{context_paths}` — newline-separated repo-root paths from `--context`, or `none`.
     **Spec-workflow rule:** when the reviewed diff implements a task from a spec directory
     (e.g. `.compozy/tasks/<slug>/`, `specs/<name>/`, `docs/rfcs/<name>/`), resolve that
     spec's contract-bearing sibling artifacts — canonical example documents, input/schema
     tables, QA seeds, test contracts, parity maps — and include them here even when the
     user passed no `--context`. Passing only the task file is insufficient: a task-file
     paraphrase must never be the reviewer's only contract source.
   - `{project_rules}` — newline-separated discovered rule-file paths, or `none`.
   - `{changed_files}` — newline-separated repo-root paths.
   - `{diff_path}` — repo-root path to the patch file from step 2.
   - `{commit_list}` — captured `git log --oneline` output, or `none` if `--staged`.
   - `{findings_path}` — exact absolute path to `<out>/impl-review-findings-roundN.md`.
   - `{round}` — numeric review round `N`.
6. Write the assembled prompt to `<out>/impl-review-prompt-roundN.md`.

**Step 3: Execute the Cross-LLM Review**

1. Capture the pre-run status snapshot:

   ```bash
   git status --short > <out>/impl-review-status-before-roundN.txt
   ```

2. Run (substitute the resolved `--ide`/`--model`/`--reasoning`, defaults `claude`/`opus`/`xhigh`):

   ```bash
   compozy exec --ide <ide> --model <model> --reasoning-effort <reasoning> --format json --prompt-file <out>/impl-review-prompt-roundN.md > <out>/impl-review-events-roundN.jsonl 2> <out>/impl-review-result-roundN.err
   ```

3. Capture the post-run status snapshot:

   ```bash
   git status --short > <out>/impl-review-status-after-roundN.txt
   ```

4. If the command returns a non-zero exit code, fail loudly. Do not retry silently. Inspect
   stderr for model misconfiguration (see Error Handling).
5. Treat `impl-review-events-roundN.jsonl` as operational evidence only. Do not parse it for
   the verdict or findings.
6. Require the findings target file to exist after the command exits. If missing, the round is
   invalid even when `compozy exec` exited 0.

**Step 4: Validate and Summarize Findings**

1. Run the bundled read-only validator:

   ```bash
   bash <skill-dir>/scripts/validate-findings.sh --kind implementation --round N --path <out>/impl-review-findings-roundN.md
   ```

2. Manually inspect the findings file and verify the semantic contract:
   - every finding has a real file path/line or an explicit reason it is not applicable;
   - blockers include a rationale tied to project rules or architecture constraints;
   - no `TBD`, placeholder text, invented paths, or stdout-only findings;
   - when spec contract artifacts were passed in `{context_paths}`, the findings explicitly
     assess contract parity (deliverable vs each canonical artifact, field by field) — a
     `SHIP` verdict with no contract-parity assessment is an invalid round;
   - comparing the pre/post status snapshots shows no changes outside the expected review
     artifact/log paths.
3. If validation fails, write `<out>/impl-review-validation-error-roundN.md` with the failed
   checks, command, exit status, and artifact paths. Do not summarize the round as `SHIP`.
4. Write `<out>/impl-review-summary-roundN.md` from the validated findings file with: the
   verdict (`SHIP` / `FIX_BEFORE_SHIP` / `REWORK`); one-line rationale per blocker; the risks
   list; the nits list; files most likely affected by remediation; and the operational
   artifact paths.
5. Present a concise user-facing summary: verdict, blocker/risk/nit counts, main themes, and
   the artifact paths written for the round.
6. Do NOT modify any source code, tests, configs, docs, or commits yet.

**Step 5: User-Directed Remediation**

1. Ask the user which findings to incorporate:
   - A) all blockers
   - B) selected blockers/risks/nits
   - C) nothing — keep the review as a record only
   - D) manual edits before any remediation
2. Apply only the findings the user selected. Do not silently apply all blockers, all risks,
   or all nits.
3. Re-run the resolved verification command after applying any code change. Do not declare
   remediation done if verification fails — fix the new failure or surface it back to the user.
4. Record the remediation decision in `<out>/impl-review-remediation-roundN.md`, listing:
   incorporated items with the new commit/diff range; deferred items; files changed; and the
   verification command and outcome with a timestamp.
5. Show the user what changed and what remains deferred. Do not commit or push without an
   explicit user instruction.

**Step 6: Optional Additional Rounds**

1. Ask whether the user wants another peer-review round against the updated code or wants to
   stop with the current state.
2. If the user requests another round, re-run from Step 2 against the new diff and create a
   fresh `roundN+1` artifact set in the same `<out>` directory.
3. Do not auto-loop. The user explicitly requests further rounds.

## Critical Rules

- This skill never commits, pushes, or opens PRs. Remediation is local-only; commit/PR steps
  belong to the user.
- The skill is not bound to any task-tracking directory layout. Every artifact lives under the
  resolved `<out>` directory and is versioned with `-roundN`. Never overwrite a prior round.
- The `compozy exec` call is the only place this skill spends external review credit. Do not
  invoke it more than once per round unless the round is explicitly invalid and the user
  requests a rerun.
- The bundled helper paths (`references/impl-review-prompt.md`, `references/readiness-checks.md`,
  `scripts/validate-findings.sh`) are read-only templates/helpers — read or run them, never
  edit them during a review round.
- For spec-workflow diffs, a round whose `{context_paths}` omitted the spec's contract-bearing
  artifacts is an invalid round: engineering quality alone can never produce `SHIP`. Real
  incident: seven rounds reached `SHIP` on a deliverable that contradicted the spec's canonical
  example document because no round ever received it.

## Error Handling

- **Compozy not found:** abort with a one-line install hint rather than swallowing or falling
  back to a harness-native subagent.
- **Model misconfiguration (`The model 'X' does not exist`):** stop and surface the configured
  model. The runtime may be set to a stale name. Do not mutate the call to substitute a
  model — verify with the user.
- **`--ide` invalid:** list the accepted values and ask the user to choose; do not fall back
  silently to `claude`.
- **Verify command unresolved:** if `--verify` is absent and auto-detection finds nothing, ask
  the user for the command instead of skipping the gate.
- **Readiness markers missing:** if Step 1 readiness checks fail, do not run the review. Print
  the failed markers and exit so the user can fix the underlying problem first.
- **Empty diff:** if `git diff` yields no changes, abort. There is nothing to review.
- **Oversized diff (`> 5000` changed lines or `> 80` files):** warn the user, ask whether to
  scope down with `--files`, and proceed only on explicit confirmation. Review on a sprawling
  diff produces shallow findings.
- **Missing findings file:** treat as an invalid round, not a clean review. Write a
  validation-error artifact and ask whether to rerun.
- **Malformed findings frontmatter or missing required sections:** treat as an invalid round.
  Do not infer the verdict from stdout.
- **Existing peer-review files for the round:** never overwrite. Increment to the next
  `roundN` instead.
- **Verification failing during remediation:** stop and surface the new failure. Do not commit
  broken code to preserve the review trail.
