---
name: agent-output-audit
description: >-
  Audits AI-implemented work for honest completion. Runs independent-evaluator
  checks against task artifacts, transcripts, tests, CI evidence,
  requirement-to-test mapping, status front matter, and quality gates; flags
  skipped tests, weakened assertions, mock-only confidence, snapshot drift,
  happy-path-only coverage, flaky retries, and status/evidence mismatches. Use
  when validating completed Compozy tasks, AI-authored PRs, or codex-loop
  iterations. Do not use for real-user QA, persona/journey testing,
  exploratory charters, or product usability sessions; use qa-execution for
  those.
argument-hint: "[audit-output-path]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Agent Output Audit

Independent verification of AI-implemented work. The skill that asks: *"Did the implementing agent actually do what `task_NN.md` says it did?"* — not *"Would a real user succeed at this product?"* (that's `qa-execution`).

## Required Reading Router

Match your task to the row. Read the listed files **in full before** producing output. They are not appendices — they are load-bearing. Inline content in this SKILL.md is a pointer, not a substitute.

| Task                                                                 | MUST read                                                                                |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Discovering install/lint/test/build/start commands (Step 1)          | `references/project-signals.md`                                                          |
| Deciding E2E support and classifying coverage (Step 1)               | `references/e2e-coverage.md`                                                             |
| Building the audit scope checklist (Step 2)                          | `references/checklist.md`                                                                |
| Holding independent-evaluator stance on AI tasks (Step 3)            | `references/independent-evaluator-protocol.md`                                           |
| Scanning test diffs for AI hygiene red flags (Step 4)                | `references/ai-implementation-audit.md`                                                  |
| Diagnosing a test that passed on retry without a code change         | `references/flaky-triage.md`                                                             |

## Reference Index

- `references/project-signals.md` — Heuristics for picking install/lint/test/build/start commands across ecosystems when the repo lacks an umbrella gate.
- `references/e2e-coverage.md` — Taxonomy for `existing-e2e` / `needs-e2e` / `manual-only` / `blocked` and how to detect harness support.
- `references/checklist.md` — Audit checklist by category: contract discovery, baseline, task audit, AI hygiene, flaky detection, quality gates.
- `references/ai-implementation-audit.md` — Red Flag scanners (RF-1..RF-6), Requirement→Test mapping, verdict matrix for completed tasks.
- `references/independent-evaluator-protocol.md` — What counts (and doesn't count) as evidence; transcript classification (`genuine-failure` / `grader-bug` / `ambiguous-task` / `bypass-exploit`).
- `references/flaky-triage.md` — Taxonomy, diagnosis protocol, and quarantine workflow for retry-passes-without-code-change failures.

## Required Inputs

- **audit-output-path** (optional): Directory where audit artifacts (bugs, audit report, evidence) are stored. When provided, create the directory if it does not exist and use it for all audit outputs. When omitted, fall back to repository conventions or `/tmp/agent-output-audit-<slug>`.

## Procedures

**Step 1: Discover the Repository Verification Contract**

1. Read root instructions, repository docs, and CI/build files before running commands.
2. Execute `python3 scripts/discover-project-contract.py --root .` to surface candidate install, verify, build, test, lint, start commands, and E2E signals.
3. **STOP. Read `references/project-signals.md` in full before picking commands when discovery surfaces more than one plausible gate or the repo mixes ecosystems.**
4. **STOP. Read `references/e2e-coverage.md` in full before classifying any flow.**
5. Prefer repository-defined umbrella commands such as `make verify`, `just verify`, or CI entrypoints over language-default commands.
6. Resolve the audit artifact directory. If the user provided an `audit-output-path` argument, use it. Otherwise use repository conventions, falling back to `/tmp/agent-output-audit-<slug>`. Create the `audit/` subdirectory; store all bugs and reports under `<audit-output-path>/audit/`.
7. **Detect Compozy mode.** If `.compozy/tasks/<slug>/` exists, record the slug and switch into Compozy-aware audit:
   - Read `state.yaml` **(read-only — never write to it; `scripts/update-state.py` owns mutation per the cy-codex-loop contract)**.
   - Read `_techspec.md` (deliverable source of truth) and `_tasks.md` (task roster) when present.
   - List every `task_NN.md` and capture its frontmatter `status:` value (allowed: `pending`, `in_progress`, `completed`). When `task_NN.md` frontmatter disagrees with `state.yaml`, treat frontmatter as the source of truth.
   - Note the canonical memory slot `.compozy/tasks/<slug>/memory/qa-execution.md` — Step 4 writes audit notes there before any status flips.

**Step 2: Run the Baseline Verification Gate**

1. Install dependencies with the repository-preferred command.
2. Run the canonical verification gate once before any audit work. Execute in fastest-first order: lint and type-check, then build, then unit tests, then integration tests.
3. If the E2E command is separate from the umbrella gate, decide whether to run it now or after runtime prerequisites are ready, then record that plan explicitly.
4. If the baseline fails, read the first failing output carefully and determine whether it is pre-existing or introduced by current work before moving on.
4a. **Flaky-failure protocol.** When a baseline command fails, before classifying as pre-existing or new, run the failing test in isolation 3-5 times on the same SHA. If it passes at least once without code changes, classify as `flaky-suspect`, record in `audit-report.md` under `SUITE HEALTH SNAPSHOT` (test name, attempts, retry outcome, suspected category), and **do NOT promote to PASS via retry**. **STOP. Read `references/flaky-triage.md` in full before assigning a suspected category or proposing a quarantine.**

**Step 3: Audit Task Implementations (Compozy mode and any AI-implemented tasks)**

Skip this step only when no task, phase, PRD, tech spec, or implementation-plan artifacts exist.

1. **STOP. Read `references/independent-evaluator-protocol.md` in full before forming any task verdict.** Tripwire summary: never accept the implementing agent's transcript, success message, or memory note as evidence. In Compozy mode, read the implementing agent's `.compozy/tasks/<slug>/memory/<phase>.md` artifacts and classify anomalies (`genuine-failure` / `grader-bug` / `ambiguous-task` / `bypass-exploit`) in the `Errors / Corrections` section of `memory/qa-execution.md` **before** judging the task.
2. Read each `task_NN.md` and its body. Summarize each task into a Task Implementation Matrix (column names mirror cy-codex-loop frontmatter):
   - `task_path` (e.g., `.compozy/tasks/<slug>/task_07.md`)
   - `declared_status` — literal frontmatter `status:` value
   - `title`, `type`, `complexity`, `dependencies` — mirrored from frontmatter
   - `techspec_deliverable` — linked section in `_techspec.md` when present
   - Requirements, subtasks, checklist items, success criteria, dependent files
   - `implementation_evidence` — files, modules, routes, commands, migrations, seeds, tests
   - `verification_evidence` — commands executed, exit codes, output summaries
   - `qa_verdict` — `PASS` | `PARTIAL` | `FAIL` | `REOPEN` | `BLOCKED` (distinct from `declared_status`)
   - `ai_audit_findings` — red flag IDs that fired in Step 4 with verdict
   - `action` — `none` | `fixed` | `reopened-frontmatter` | `BUG-NNN.md filed`
   - `linked_bugs` — BUG IDs
3. Do not treat a task `declared_status`, checked checkbox, memory note, or prior agent summary as proof. Verify every completed or claimed-complete task against actual files, public behavior, automated tests, and acceptance criteria.
4. Classify each task with `qa_verdict`:
   - `PASS`: every material requirement and success criterion has implementation and fresh verification evidence.
   - `PARTIAL`: implementation exists but one or more non-critical requirements, tests, or evidence are missing.
   - `FAIL`: claimed behavior does not work or a critical requirement is absent.
   - `REOPEN`: the source `task_NN.md` has `status: completed` in frontmatter but the QA verdict is `PARTIAL` or `FAIL`.
   - `BLOCKED`: audit cannot continue because a concrete prerequisite is missing.

**Step 4: AI Test-Hygiene Scan (RF-1..RF-6)**

1. **STOP. Read `references/ai-implementation-audit.md` in full before scanning the test diff of any task with `declared_status: completed`.** That file owns the Red Flag scanners (RF-1..RF-6), the Requirement→Test mapping rules, and the verdict matrix.
2. Run the scans against the diff since the task baseline (`git log --follow <test_file>`, `git diff <baseline_sha>..HEAD`).
3. Emit verdict `FAIL` automatically when scanners detect:
   - Weakened assertions on P0/P1 Success Criterion (RF-2).
   - `.skip` / `.only` / `xit` / `t.Skip` inserted in the diff (RF-1).
   - Mocks inserted in tests whose corresponding TC declared `External Dependencies` as Integration/E2E (RF-3).
   - Snapshot drift on P0/P1 with no requirement-change justification (RF-4).
4. Record findings in the Task Implementation Matrix column `ai_audit_findings` and in the per-task block of `audit-report.md`.
5. Apply the Requirement → Test mapping table from `references/ai-implementation-audit.md`. For every Success Criterion in `task_NN.md` (frontmatter or body) and every linked bullet in `_techspec.md`, find the corresponding test by name, reference, or assertion content. Mark each criterion `covers` / `weak` / `missing`. A checked item or `status: completed` without a `covers` row is an audit failure.

**Step 5: Reopen, File Bugs, Write Memory**

1. Mark incomplete completed tasks as `REOPEN` in the matrix.
2. **In Compozy mode**, write audit notes to `.compozy/tasks/<slug>/memory/qa-execution.md` using the canonical sections required by cy-codex-loop: `Objective Snapshot`, `Important Decisions`, `Learnings`, `Files / Surfaces`, `Errors / Corrections`, `Ready for Next Run`. This file must be written **before** any `task_NN.md` frontmatter is flipped (memory-precedes-status invariant).
3. Edit the offending `task_NN.md` frontmatter `status:` back to `pending` (or `in_progress` if salvageable). **Never write to `state.yaml`** — cy-codex-loop's `update-state.py` owns mutation; frontmatter wins because the next iteration reconciles from it.
4. File `BUG-<num>.md` under `<audit-output-path>/audit/issues/` using `assets/issue-template.md`. Include:
   - The task path under `Reopens task:`.
   - The failed Success Criterion under `Summary:`.
   - The original strict assertion (when RF-2 fired) under `Root cause:`.
   - The red flag ID and verdict under `Automation Follow-up:` notes.
   - The transcript anomaly classification (when applicable) under `Related:`.
5. When the missing work is a bounded root-cause fix inside the audit scope, you may implement it, add regression coverage, and rerun the task proof. Otherwise reopen the task — do not silently pass it.

**Step 6: Quality Gates Verdict**

1. Re-run the canonical verification gate from scratch after the last code change made during the audit.
2. Compile the Quality Gates section of `audit-report.md`. Each gate is `PASS` / `FAIL` / `N/A`:
   - Flaky rate <2% in canonical suite.
   - Zero `FAIL` from AI test-hygiene audit on P0/P1 tasks.
   - Zero `Critical` / `High` issues open.
   - Coverage delta ≥ baseline (no regression).
   - Zero unresolved `flaky-suspect` on P0 flows.
3. A `FAIL` on any gate blocks an unconditional PASS verdict for the run.

**Step 7: Write the Audit Report**

1. Summarize the audit using `assets/audit-report-template.md` and write the report to `<audit-output-path>/audit/audit-report.md`.
2. Mandatory sections:
   - **Claim / Command / Exit code / Verdict** per command executed in Step 2 and Step 6.
   - **AUTOMATED COVERAGE** — support detected, harness, canonical command, required flows with classification, specs added or updated.
   - **TASK IMPLEMENTATION AUDIT** — Compozy slug, plan sources, matrix totals, per-task verdicts, reopened/fixed/blocked tasks, links to bugs.
   - **SUITE HEALTH SNAPSHOT** — flaky rate, flaky events list, mutation score (when harness exists), coverage delta vs baseline, blocked count, manual-only count, AI audit findings count.
   - **QUALITY GATES** — PASS/FAIL/N/A per gate.
   - **ISSUES FILED** — total, by severity, with `Reopens task:` annotations.
3. When running in a Compozy slug, the final `audit-report.md` PASS feeds cy-codex-loop's `verify.last_status=PASS` precondition for Phase E — **do not call `update-state.py`**; cy-codex-loop owns that mutation.
4. Report blocked scenarios, missing credentials, or environment gaps with the exact command or prerequisite that stopped execution.

## Error Handling

- If command discovery returns multiple plausible gates, prefer the broadest repository-defined command and explain the tie-breaker.
- If E2E support signals are weak or contradictory, prefer explicit config files and runnable commands before claiming the repository supports E2E.
- If no canonical verify command exists, read `references/project-signals.md`, choose the broadest safe install, lint, test, and build commands for the detected ecosystem, and state that assumption explicitly.
- If a required live dependency is unavailable, validate every local boundary that does not require the missing dependency and report the blocked live validation separately.
- If a failure appears unrelated to the audited tasks, prove that with a clean reproduction before excluding it from the audit scope.
- If the repository has an E2E harness but credentials, runtime services, or test data prevent execution, keep the affected flow classified as `blocked` and report the exact prerequisite that is missing.
- If `task_NN.md` files are marked `status: completed` but contain unchecked subtasks, missing deliverables, or unverified criteria, do not call the audit a pass. Write `memory/qa-execution.md` first, then edit frontmatter `status:` back to `pending` or `in_progress`, and file `BUG-<num>.md` per Step 5. Never write to `state.yaml`.
- If a test fails and passes on retry without a code change, do not promote to PASS. Register as `flaky-suspect` per `references/flaky-triage.md`, record the event in the Suite Health Snapshot, and treat any unresolved `flaky-suspect` on a P0 flow as a blocker for the final verdict.
- If the AI test-hygiene scan (Step 4) detects weakened assertions, skipped tests, or mocks hiding integration in a task with `declared_status: completed`, do not call the audit a pass. Apply the verdict matrix in `references/ai-implementation-audit.md`, file `BUG-<num>.md` with Type `Functional`, and flip frontmatter `status:` per Step 5.

## Companion: qa-execution

`agent-output-audit` validates that the implementing AI agent did what it claimed. `qa-execution` validates that a real human user can succeed at the product. They are complementary, not redundant:

- Run `agent-output-audit` to certify that `task_NN.md status: completed` reflects real work.
- Run `qa-execution` to certify that the product, taken as a whole, is acceptable to end users.

A Compozy slug typically wants both: audit the task implementations, then exercise the resulting product through user-flow QA. They share no output directory, no bug taxonomy, and no procedures — keep them separate.
