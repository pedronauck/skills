---
name: agent-exploration
description: >-
  Dispatches scoped-write explorer subagents in parallel for general research
  and exploration of any codebase, topic, or domain. The operator passes
  --path (output directory), --agents (parallel count), and --prompt (research
  question). The parent scouts the territory first to divide work, dispatches
  N explorer subagents that each write one analysis file at
  <path>/analysis/NN_analysis_<slug>.md following a seven-section schema, then
  synthesizes <path>/analysis/summary.md. The skill self-contains the explorer
  subagent definition and prompts the operator to install it at
  .claude/agents/explorer.md when absent. Use when running parallel multi-area
  research that must produce written artifacts. Do not use for competitor-only research
  already covered by cy-research-competitors, single-file lookups answerable
  by Explore, or edits to existing code.
trigger: explicit
argument-hint: "[--path <dir>] [--agents <num>] [--prompt <text>]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Agent Exploration

Generic parallel-research workflow. Use when a question requires deep reads across multiple distinct areas and the operator needs written artifacts (not chat output). The skill dispatches `explorer` subagents in parallel; each writes one analysis file. The parent then synthesizes a final summary.

The skill is self-contained. It ships two explorer subagent definitions side by side so the same skill works on both major harnesses:

- **Claude Code**: `assets/explorer-agent.md` → installed to `.claude/agents/explorer.md` (Markdown with YAML frontmatter).
- **OpenAI Codex CLI**: `assets/explorer-agent.toml` → installed to `.codex/agents/explorer.toml` (single TOML document with `sandbox_mode = "workspace-write"` and the scoped-write contract carried in `developer_instructions`).

The parent verifies installation for the active harness before every dispatch.

## Required Reading Router

Match your step to the row. Read the listed files **in full before** producing output. They are not appendices — they are load-bearing. Inline content in this SKILL.md is a pointer, not a substitute.

| Step                                                    | MUST read                                                              |
| ------------------------------------------------------- | ---------------------------------------------------------------------- |
| Step 4 — composing every subagent prompt                | `references/dispatch-rules.md` + `assets/analysis-template.md`         |
| Step 5 — verifying outputs                              | `references/checklist.md` + `assets/analysis-template.md`              |
| Step 6 — synthesizing `summary.md`                      | every `<path>/analysis/NN_analysis_<slug>.md` from this round          |
| Any contract violation, fabricated evidence, or retry   | `references/dispatch-rules.md` (re-read; do not paraphrase from memory)|

## Reference Index

- `references/dispatch-rules.md` — the scoped-write contract: what the subagent may write, may read, may run; tool allow/forbid lists; parent responsibilities; parallelism cap; failure handling. **Must be embedded verbatim in every subagent prompt.**
- `references/checklist.md` — seven-section output validation checklist (installation, inputs, scout, dispatch, files, schema, summary). Run before authoring `summary.md`.
- `assets/analysis-template.md` — the canonical seven-section schema every subagent fills (Overview, Mechanisms/Patterns, Relevant Sources, Transferable Patterns, Risks/Mismatches, Open Questions, Evidence) plus a Scope header.
- `assets/explorer-agent.md` / `assets/explorer-agent.toml` — the bundled subagent definitions for Claude Code and Codex CLI. Installed by `scripts/install-explorer.sh`.
- `scripts/install-explorer.sh` — bootstrap helper. Writes the explorer definition to the active harness's expected path. Refuses to overwrite.

## Bundled Path Rule

Resolve every bundled helper relative to the directory that holds this `SKILL.md`. When a command appears below as `scripts/<name>`, treat the actual invocation as `<agent-exploration-dir>/scripts/<name>` — expand `<agent-exploration-dir>` to the absolute skill directory before running.

## Required Inputs

- `--path <dir>` (required): Output directory. Analysis files are written under `<path>/analysis/`. Any project-relative or absolute directory works (for example `docs/research/<topic>/`, `tasks/<slug>/`, or a path outside the repo). The skill is not tied to any specific project layout.
- `--agents <num>` (optional, default 3, hard cap 8): Number of explorer subagents to dispatch in parallel. Caps prevent runaway dispatch when the prompt is vague.
- `--prompt <text>` (required): The research question. Quoted multi-line strings are supported. If omitted, the parent asks the operator before continuing.

If `--path` or `--prompt` is missing, the parent asks the operator a single clarification before continuing. Never invent defaults for either.

## Output Layout

```
<path>/analysis/
├── 01_analysis_<slug-a>.md
├── 02_analysis_<slug-b>.md
├── 03_analysis_<slug-c>.md
└── summary.md
```

- File numbering is zero-padded to two digits (`01`, `02`, …, `08`).
- Each slug is a short kebab-case identifier the parent assigns during the scout (Step 3), reflecting that slice's focus.
- `summary.md` is parent-authored synthesis, not a subagent output.

## Procedures

**Step 1: Verify the explorer subagent is installed**

1. Detect the active harness:
   - If the runtime is Claude Code (project contains `.claude/` or `CLAUDE.md`), the expected install path is `.claude/agents/explorer.md`.
   - If the runtime is Codex CLI (project contains `.codex/` or `AGENTS.md`), the expected install path is `.codex/agents/explorer.toml`.
   - If both are present, both targets must be installed (or the operator must opt out per-target).
2. For each expected target, check whether the file exists.
3. If every expected target is present, proceed to Step 2.
4. If any expected target is missing, ask the operator a single question naming the missing targets: e.g. "The `explorer` subagent is not installed for Claude Code (.claude/agents/explorer.md) and Codex CLI (.codex/agents/explorer.toml). Install both now? [yes/no/claude-only/codex-only]". Do not proceed silently.
5. On any "yes" answer, run the bundled bootstrap helper (`scripts/install-explorer.sh` — **bootstrap helper, writes one or two files**) with the matching `--target`:
   - `<agent-exploration-dir>/scripts/install-explorer.sh --target both` (default)
   - `<agent-exploration-dir>/scripts/install-explorer.sh --target claude`
   - `<agent-exploration-dir>/scripts/install-explorer.sh --target codex`
   Add `--user` to install into `$HOME` instead of the nearest project root. The helper refuses to overwrite existing files and prints `OK` / `SKIP` per target.
6. On "no", abort the dispatch with a one-line message. Do not dispatch the `explorer` subagent before installation completes — the dispatch will fail with "agent not found".
7. After installation, re-check that the expected target file(s) exist before continuing.

**Step 2: Resolve inputs**

1. Parse `--path`, `--agents`, `--prompt` from the invocation. If `--path` or `--prompt` is missing, ask the operator and stop.
2. Default `--agents` to `3` when omitted. Reject values below 1 or above 8 — ask the operator to choose a value in range.
3. Resolve `--path` to an absolute path. If the directory does not exist, ask the operator whether to create it before continuing.
4. Create `<path>/analysis/` if absent. The subagents refuse to write into a missing directory.

**Step 3: Parent-led initial scout (MANDATORY — do not skip)**

The scout is the load-bearing step that prevents wasted parallel dispatch. The parent must do this work itself before any subagent is launched.

1. Perform a brief read-only exploration of the problem space using `Glob`, `Grep`, and targeted `Read` calls. The scout's job is to learn enough about the territory to divide it well — not to produce analysis content. Cap the scout at 8–15 tool calls; deep reading belongs to the subagents.
2. From the scout, identify exactly `--agents` distinct slices that are:
   - **Non-overlapping** — two slices should not require reading the same primary files for the same purpose.
   - **Independently answerable** — a slice's analysis must not depend on another slice's output.
   - **Aligned with the operator's `--prompt`** — every slice serves the original research question.
3. For each slice, assign:
   - A two-digit ordinal (`01`..`08`).
   - A short kebab-case slug (≤ 4 words) reflecting that slice's focus (e.g. `state-machine`, `event-bus`, `auth-boundaries`).
   - A focused per-slice prompt that names the slice question, the primary source paths/URLs to read, and any cross-references the subagent should use.
4. Briefly tell the operator the slice list (one line per slice: `NN – slug – focus`) before dispatching. Do not ask for approval unless the slices look thin or overlap; just announce and proceed.

If the scout reveals that fewer than `--agents` non-overlapping slices exist, reduce the dispatch count and tell the operator. Do not pad slices to hit the requested count.

**Step 4: Dispatch explorer subagents in parallel**

Gist tripwires — the contract items the parent must enforce in every prompt:

- The prompt names three things: slice scope, slug+ordinal, exact target file path. If any is missing, the subagent must refuse and ask back.
- The subagent gets exactly one `Write` — at the named target path — and nothing else. No `Edit`, no `git`/`make`/package managers, no writes outside `<path>/analysis/`.
- All subagents dispatch in the same parallel batch with `subagent_type: explorer`. Wait for the full set before continuing.

**STOP. Read `references/dispatch-rules.md` in full before composing any subagent prompt.** That file contains the complete scoped-write contract, tool allow/forbid lists, parent responsibilities, and failure handling. The bullets above are tripwires, not the contract — the contract must be embedded verbatim in every subagent prompt.

**STOP. Read `assets/analysis-template.md` in full before composing any subagent prompt.** That file is the canonical seven-section schema every subagent fills. The schema must be embedded in the prompt; do not paraphrase it.

Compose one `explorer` subagent prompt per slice. Every prompt MUST include:
- The operator's original `--prompt` verbatim, prefixed by a short orientation line.
- The slice's focused question and the primary sources to read.
- The exact target path: `<path>/analysis/NN_analysis_<slug>.md` (absolute path).
- `references/dispatch-rules.md` content embedded verbatim (copy-paste, do not paraphrase).
- The seven-section schema from `assets/analysis-template.md`.

Dispatch all subagents in the same `Agent` batch with `subagent_type: explorer` on every call. Wait for every subagent to return before continuing — a partial set is unacceptable.

**Step 5: Verify outputs**

Gist tripwires — the floor items that catch most failures:

- Exactly `N` files at the expected `NN_analysis_<slug>.md` paths under `<path>/analysis/`.
- All seven schema sections present in each file; no empty sections without a gap-note + Open Question.
- At least one cited source per file sample-checked (Read for local paths, well-formedness for URLs).

**STOP. Read `references/checklist.md` in full before declaring outputs verified.** That file is the seven-section output validation checklist (installation, inputs, scout, dispatch, files, schema, summary). Every item must pass; failing items trigger a re-dispatch of the offending slice. The three bullets above are tripwires, not the contract.

If a section is empty, a file is missing, a cited path is fake, or the schema is incomplete, re-dispatch the offending subagent with the schema embedded and a request to fill the gap. The parent never authors the missing analysis content — the subagent owns the write.

**Step 6: Synthesize `summary.md`**

1. Read every `<path>/analysis/NN_analysis_<slug>.md` in full.
2. Author `<path>/analysis/summary.md` with these sections:
   - **Research Question** — the operator's `--prompt`, verbatim.
   - **Slice Map** — table mapping each `NN – slug` to its slice question and one-line finding.
   - **Convergences** — patterns or risks that appear in two or more analyses, with cross-citations to the slice files.
   - **Divergences** — places where slices disagree or where one slice surfaces a finding the others miss.
   - **Risks & Open Questions** — consolidated, deduplicated list pulled from each analysis's Open Questions and Risks/Mismatches sections.
   - **Recommended Next Steps** — short, actionable list. Each step cites the slice file(s) that support it.
   - **Index** — bullet list of `<path>/analysis/NN_analysis_<slug>.md` paths so a future reader can drill in.
3. `summary.md` is parent-authored. Do not dispatch a subagent for this step.

## When Not To Use

- **Single-file lookups** ("where is X defined?", "what does function Y return?"): use `Explore` or direct `Grep`/`Read`. This skill is overkill.
- **Edits to existing code**: explorer is scoped-write — it can only create new analysis files, not modify anything else.
- **Tightly scoped competitor / reference-repo research** in projects that already ship a more specialized variant (for example a project-local skill that mirrors a fixed competitor catalog). Use that variant when it exists; use this skill as the generic fallback.

## Error Handling

Operational tripwires only — the full failure taxonomy lives in `references/dispatch-rules.md` (Failure Handling) and `references/checklist.md`.

- **Active-harness target missing and operator declines install:** abort the dispatch with a one-line message. Do not attempt to inline-define the subagent in the dispatch prompt.
- **`--path` directory cannot be created:** stop and report the filesystem error. Do not fall back to the current working directory silently.
- **`--agents` out of range:** ask the operator for an in-range value. Do not auto-clamp.
- **Scout cannot find `--agents` non-overlapping slices:** reduce the dispatch count, inform the operator, and proceed with the smaller set.
- **Contract violation, schema-incomplete analysis, fabricated evidence, or ambiguous-prompt refusal:** **STOP. Re-read `references/dispatch-rules.md` in full** before re-dispatching. The parent never authors the missing content; the subagent owns the write.
- **Network/disk error during dispatch:** fail the round entirely. Do not produce a half-set of analyses. Re-dispatch after the error is resolved.
