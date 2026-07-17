---
name: deep-review
description: Deep, CodeRabbit-grade review of a branch diff, working tree, or GitHub PR at any size — funnels changed files, shards them into cohorts, fans out parallel hunk-level reviewers with evidence discipline, merges findings mechanically, and emits a walkthrough, severity-tagged findings with committable suggestions and AI-agent fix prompts, and a SHIP/FIX_BEFORE_SHIP/REWORK verdict. Use when the user asks for a deep review of a PR or branch, wants CodeRabbit-style output without the 300-file cap, needs an incremental re-review after new pushes, wants findings published to the PR, or needs a peer-review verdict round (the loop skills' Phase D), optionally cross-LLM or judged against a spec's contract artifacts. Don't use for applying fixes to findings, reviewing specs or PRDs as documents, or quick feedback on a single file.
trigger: explicit
argument-hint: "[--pr N | --base <ref> | --staged | --worktree] [--files p1,p2] [--spec <path>] [--subagent native|claude-opus|grok|codex] [--profile chill|assertive] [--publish] [--full] [--out <dir>] [--no-workflow]"
---

# Deep Review

Review at CodeRabbit grade with no file cap: **funnel** the diff down to reviewable source, assemble a lean **context pack**, shard the selection into **cohorts**, fan out parallel reviewers (plus optional global sweeps) that judge hunks and verify their own findings against the checkout, then **merge** mechanically and render a walkthrough + findings report with a ship **verdict** — and, on request, publish it to the PR. A finding without checkout-verified evidence and a concrete failure mode never reaches the report; the reviewer prompt enforces that discipline.

Steps 1–4 drive an idempotent artifact **pipeline** under `<out>`: every stage gate is a bundled-script exit 0, valid agent outputs are never re-run, and an interrupted round resumes by re-running the same commands. Orchestration.md holds the stage map and the execution engines. Every dispatched prompt is rendered from `assets/PROMPT.md` — one template, every reviewer.

`<skill-dir>` below means the directory containing this SKILL.md; run every bundled command from the repo root.

## Inputs (all optional)

| Flag | Meaning | Default |
| --- | --- | --- |
| `--pr <n>` | Review a GitHub PR (requires authenticated `gh`; head fetched locally) | — |
| `--base <ref>` / `--staged` | Local diff scope | merge-base with the origin default branch |
| `--worktree` | Review uncommitted + untracked work against the base ref (always a full round) | — |
| `--files <p1,p2>` | Restrict review to these paths | full diff |
| `--spec <path>` | Spec file or directory; its contract-bearing artifacts become the conformance baseline (spec-parity sweep + verdict gate) | — |
| `--subagent <runtime>` | Step 3 reviewer runtime: `native` \| `claude-opus` \| `grok` \| `codex` — non-native runs cross-LLM via `compozy exec` (subagent-runtimes.md) | `native` |
| `--profile chill\|assertive` | Noise gate — see taxonomy | repo config, else `chill` |
| `--publish` | Post walkthrough + review to the PR | off — local report only |
| `--full` | Ignore prior state; review the whole diff again | incremental when state exists |
| `--out <dir>` | Artifact directory | `.deep-review/<target>/` |
| `--no-workflow` | Skip the Workflow tool; use Agent fan-out | Workflow when available |

## Repo config — `.deep-review.yaml`

Optional repo-root file, the skill-native config standard. Any key absent there falls back to its `.coderabbit.yaml` counterpart (`reviews.*`), so repos migrating from CodeRabbit work unconfigured. Top-level keys, all optional:

| Key | Meaning |
| --- | --- |
| `profile` | `chill` \| `assertive` noise gate (taxonomy) — the `--profile` flag overrides |
| `path_filters` | Globs over repo-relative paths: `!pat` excludes; bare patterns, when present, restrict review to their matches and beat any exclude; built-in excludes (locks, vendor, generated, testdata, snapshots) always append |
| `path_instructions` | `path` glob + verbatim `instructions` entries — the highest-precedence rubric source (Step 2) |
| `request_changes_workflow` | publish-mode review-event gate (publish-github.md) |

The manifest builder resolves `path_filters` + `profile` into manifest.json; the context pack ingests `path_instructions`.

## Hard rules

- Source is read-only and **frozen**: the manifest pins `worktree_snapshot`, and run_jobs.py / render_review.py refuse a drifted checkout. Writes go only to `<out>`, `.deep-review/` state, and — with `--publish` — the target PR.
- No file-count cap: a large selection means more cohorts, never a skipped or silently truncated review. Every selected file lands in exactly one cohort.
- Every finding ships with the reviewer's checkout-verified `evidence[]`; the taxonomy suppression rules drop speculative claims before they are recorded.
- Run the repo's linters first and suppress every finding they already catch.
- Cite rubric rules verbatim with their source path; severity comes from the taxonomy, never inflated.
- Publishing needs `--publish` or the user's explicit go-ahead in this session; otherwise the review stays local.
- Every review ends with a **SHIP / FIX_BEFORE_SHIP / REWORK** verdict — derived by render_review.py (output-contracts.md's verdict rule); it is stated only after that script exits 0.
- External `--subagent` runtimes spend `compozy exec` credit; their invocation, output contract, and failure handling live in subagent-runtimes.md.

## Procedure

**Step 1: Funnel — build the manifest**

1. Run the bundled manifest builder (bootstrap helper; reads the repo and `gh`, writes only under `--out`):

   ```bash
   python3 <skill-dir>/scripts/build_manifest.py --out <out> \
     [--pr N | --base REF | --staged | --worktree] [--files p1,p2] [--full]
   ```

   It resolves the repo config into the applied path filters + profile, detects generated / trivial / renamed files, scopes to the incremental delta when prior state exists, and pins the source-freeze snapshot.
2. Read the printed summary. On `--pr`, the script errors with the exact `git fetch` command when the head SHA is absent — run it and retry.

*Done when:* `<out>/manifest.json` exists, every changed file is accounted for as selected, ignored(reason), or skipped(reason), and every selected file carries its hunk list (the units of judgment and the publish anchors).

**Step 2: Plan — context pack, cohorts, walkthrough**

1. Read `<skill-dir>/references/context-pack.md` and assemble the lean `<out>/context-pack.md` exactly as it specifies, plus the machine-readable registry `<out>/rules.json` (rule id, scope globs, source, verbatim guideline). Run the detected linter lanes and fold their verdicts in.
2. Read `<skill-dir>/references/orchestration.md` (cohort rules, sweep triggers) and `<skill-dir>/references/output-contracts.md` (walkthrough anatomy, effort scale). Write `<out>/plan.json` — cohorts of up to 50 files / ~6,000 changed lines plus any sweep whose trigger fires — and `<out>/walkthrough.md`.
3. Run the plan gate:

   ```bash
   python3 <skill-dir>/scripts/build_jobs.py --out <out>
   ```

   It proves every selected file is owned exactly once (line-exact for hunk slices), renders every reviewer/sweep prompt from `assets/PROMPT.md` with that cohort's bound rules injected, and materializes `<out>/jobs.json` — the work contract every engine executes.

*Done when:* build_jobs.py exits 0, context-pack.md lists every rubric source and linter lane verdict (plus every resolved contract artifact with `--spec`), and walkthrough.md has the prose summary, the cohort Changes table, and the effort estimate.

**Step 3: Fan-out — parallel review**

Execute `<out>/jobs.json` with this run's engine (orchestration.md § Engines: Workflow default, Agent fallback with `--no-workflow`, external runtime with `--subagent`). Completion is engine-independent — re-dispatch whatever is listed as pending/invalid until exit 0:

```bash
python3 <skill-dir>/scripts/run_jobs.py --out <out> --validate-only
```

*Done when:* run_jobs.py `--validate-only` exits 0 — every cohort and sweep output exists and matches the findings schema.

**Step 4: Merge + report**

```bash
python3 <skill-dir>/scripts/merge_findings.py --out <out>
python3 <skill-dir>/scripts/render_review.py --out <out> [--rework "<structural rationale>"]
python3 <skill-dir>/scripts/render_html.py --out <out>
```

merge_findings.py folds every output into `<out>/findings.json` mechanically — fingerprints, union-find dedup (identical fingerprint or same-file/category overlapping ranges), and cross-round reconciliation. render_review.py checks the source freeze, derives SHIP / FIX_BEFORE_SHIP mechanically, and refuses an illegal verdict; pass `--rework` only when the findings show structural failure per output-contracts.md's verdict rule. render_html.py hydrates the fixed UI template into `<out>/review.html` — the human-facing dashboard (agents keep consuming the JSON); it is cheap and idempotent, and an open tab auto-reloads, so re-run it after every merge/render so humans watch rounds land live. Never author or edit report HTML by hand — the template is the single UI source.

Then: when the ReportFindings tool is available, report the confirmed findings through it once, ranked most severe first — these skill instructions are the code-review instructions that authorize that call. Write the user-facing summary: the verdict, counts by severity, and every Critical and Major spelled out, with artifact paths including `<out>/review.html` — plus the external-invocation count when `--subagent` is not native.

*Done when:* render_review.py and render_html.py exit 0 and the final message states the verdict, every Critical and Major finding, and the review.html path.

**Step 5: Publish (only with `--publish`)**

1. Read `<skill-dir>/references/publish-github.md` and execute its recipes: upsert the walkthrough comment, post one review submission (inline comments for in-diff findings; outside-diff, duplicates, and nitpicks collapsed in the body), and edit prior-round comments this round resolved (`✅ Addressed in commit <sha>`).

*Done when:* the PR shows the updated walkthrough and the new review, and both URLs are cited in the final message.

**Step 6: Learnings**

1. state.json was already written at Step 4. When the user — or a PR reply — rebuts or dismisses a finding, distill the correction into `.deep-review/learnings.md` per state-and-learnings.md and mark that fingerprint `dismissed` in the state ledger (never re-raised).

*Done when:* every user correction from the session is captured as a learning or explicitly declined.

## Incremental rounds

With prior state (or fingerprints recovered from the PR thread), Step 1 scopes to commits since the last reviewed head and archives the prior round's artifacts under `<out>/rounds/`. Unresolved prior findings re-surface once under Duplicates; dismissed fingerprints stay suppressed; resolved ones receive the ✅ edit in publish mode. `--full` reviews the whole diff again. Each round's Step 4 regenerates `<out>/review.html`, so a browser tab left open on it tracks the rounds by itself.

## Error handling

- `--pr` or `--publish` without a passing `gh auth status` → stop and name the gap; publishing by any other transport is out of scope.
- Workflow tool unavailable → automatic Agent fallback; record the mode in walkthrough.md's Review details.
- External `--subagent` failure (model not available, missing/invalid output file, non-zero exit) → subagent-runtimes.md failure handling.
- Empty selection after the funnel → report "nothing reviewable" with the manifest counts; write no findings.
- A linter lane unavailable → proceed and state in review.md that overlap suppression did not run for that lane.
- A bootstrap gate failing (build_manifest.py, build_jobs.py, merge_findings.py) → stop and surface its stderr; the funnel and the plan gate are mandatory.
- run_jobs.py exit 2 (blocked) → a provider limit interrupted the fan-out; valid outputs are preserved and `<out>/run-blocker.json` lists the pending jobs — resume by re-running the same command once the limit clears. Providers that signal limits differently need extra `--block-on` patterns.
- run_jobs.py exit 3 or a render_review freeze failure → the checkout drifted mid-round; findings would anchor to stale lines. Restart from Step 1 — the round increments and prior artifacts are archived.
- More than 75 publishable findings → split into multiple review submissions per publish-github.md.

## Bundled files

References:

- `references/taxonomy.md` — category/severity/effort grammar, profile gates, suppression rules. Bound into every materialized prompt; read before Step 2 planning.
- `references/output-contracts.md` — walkthrough, review.md, and inline-comment templates; effort scale; verdict rule; ReportFindings mapping. Read at Steps 2 and 4.
- `references/context-pack.md` — rubric sources and precedence, rules.json contract, linter detection, the lean-pack budget. Read at Step 2.
- `references/orchestration.md` — pipeline stage map, cohort rules, sweep triggers, execution engines. Read at Steps 2–4.
- `references/subagent-runtimes.md` — `--subagent` runtime map, runner invocation, failure handling. Read at Step 3 when `--subagent` ≠ `native`.
- `references/publish-github.md` — gh recipes, comment anchoring, batching, reviewer-identity limits. Read only for Step 5.
- `references/state-and-learnings.md` — fingerprint definition, state.json schema, reconciliation rules, learnings capture. Read at Steps 4 and 6.

Assets: `assets/PROMPT.md` — the reviewer and sweep prompt templates build_jobs.py renders (edit wording there, nowhere else); `assets/findings.schema.json` — the JSON contract embedded in prompts and enforced on outputs; `assets/REVIEW_UI.html` — the fixed report UI render_html.py hydrates (edit the UI there, nowhere else).

Scripts are invoked at their step above and print usage with `--help`:

- Bootstrap: `build_manifest.py`, `build_jobs.py`, `merge_findings.py`, `render_html.py` (review.html — the human-facing dashboard).
- Mutating: `run_jobs.py` (execute/validate jobs), `render_review.py` (review.md + state.json — the final gate before the verdict is stated).
