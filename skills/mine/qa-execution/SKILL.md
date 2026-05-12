---
name: qa-execution
description: Executes full-project QA like a real user by auditing task/spec completion against implementation, discovering the repository verification and E2E contracts, running build, lint, test, and startup commands, exercising core workflows end-to-end through CLI, HTTP, and browser interfaces, requiring automated regression coverage for supported critical flows, fixing root-cause regressions, reopening incomplete work, and rerunning the full gate. Uses the agent-browser companion skill for Web UI validation when a web surface exists. Integrates with cy-codex-loop slugs at `.compozy/tasks/<slug>/` — reads `state.yaml`, audits `task_NN.md` frontmatter, writes audit memory to `memory/qa-execution.md`. Use when validating a branch, release candidate, migration, refactor, risky commit, or a completed task set. Do not use for static code review only, one-off unit test edits, planning test cases, or architecture brainstorming without execution — use qa-report for planning and documentation.
argument-hint: "[qa-output-path]"
---

# Systematic Project QA

## Required Reading Router

Match your task to the row. Read the listed files **in full before** producing output. They are not appendices — they are load-bearing. Inline content in this SKILL.md is a pointer, not a substitute.

| Task                                                                 | MUST read                                                                                |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Discovering install/lint/test/build/start commands (Step 1)          | `references/project-signals.md`                                                          |
| Deciding E2E support and classifying flows (Step 1)                  | `references/e2e-coverage.md`                                                             |
| Building the QA scope checklist (Step 2)                             | `references/checklist.md`                                                                |
| Exercising any Web UI surface (Step 5)                               | `references/web-ui-qa.md`                                                                |
| Holding independent-evaluator stance on AI tasks (Step 4A.3a)        | `references/independent-evaluator-protocol.md` + `references/ai-implementation-audit.md` |
| Test-hygiene fraud audit on `status: completed` tasks (Step 4A.3b)   | `references/ai-implementation-audit.md`                                                  |
| Diagnosing a test that passed on retry without a code change         | `references/flaky-triage.md`                                                             |

## Reference Index

- `references/project-signals.md` — heuristics for picking install/lint/test/build/start commands across ecosystems when the repo lacks an umbrella gate.
- `references/e2e-coverage.md` — taxonomy for `existing-e2e` / `needs-e2e` / `manual-only` / `blocked` and how to detect harness support.
- `references/checklist.md` — the QA scope checklist by category: contract discovery, baseline, flaky detection, CLI/API, task audit, AI audit, Web UI, regression, final verify, quality gates.
- `references/web-ui-qa.md` — `agent-browser` command set, core loop, viewport testing, auth flows, anti-smoke guardrails.
- `references/ai-implementation-audit.md` — Red Flag scanners (RF-1..RF-6), Requirement→Test mapping, verdict matrix for completed tasks.
- `references/independent-evaluator-protocol.md` — what counts (and doesn't count) as evidence; transcript classification (`genuine-failure` / `grader-bug` / `ambiguous-task` / `bypass-exploit`).
- `references/flaky-triage.md` — taxonomy, diagnosis protocol, and quarantine workflow for retry-passes-without-code-change failures.

## Required Inputs

- **qa-output-path** (optional): Directory where QA artifacts (issues, screenshots, verification reports) are stored. When provided, create the directory if it does not exist and use it for all QA outputs. When omitted, fall back to repository conventions or `/tmp/codex-qa-<slug>`.

## Procedures

**Step 1: Discover the Repository QA Contract**

1. Read root instructions, repository docs, and CI/build files before running commands.
2. Execute `python3 scripts/discover-project-contract.py --root .` to surface candidate install, verify, build, test, lint, start commands, Web UI signals, and E2E signals.
3. **STOP. Read `references/project-signals.md` in full before picking commands when discovery surfaces more than one plausible gate or the repo mixes ecosystems.** That file is the source of truth for command ownership across Node, Python, Go, Rust, Make/Just, and CI entrypoints.
4. **STOP. Read `references/e2e-coverage.md` in full before classifying any flow.** The four classifications (`existing-e2e` / `needs-e2e` / `manual-only` / `blocked`) and the harness-detection signals live there — the inline mention here is a tripwire, not the contract.
5. Prefer repository-defined umbrella commands such as `make verify`, `just verify`, or CI entrypoints over language-default commands.
6. Identify the changed surface and the regression-critical surface before choosing scenarios.
7. Determine whether the project has a Web UI surface. Indicators include: a `start` or `dev` command that launches a web server, framework config files (`next.config.*`, `vite.config.*`, `nuxt.config.*`, `angular.json`, `svelte.config.*`), or HTML/template entry points. Record the dev server URL (default `http://localhost:3000` unless the project specifies otherwise).
8. Record the E2E contract in working notes: support detected or not, harness name, canonical command, known spec locations, and blockers.
9. Resolve the QA artifact directory. If the user provided a `qa-output-path` argument, use that path. Otherwise, use repository conventions. If neither exists, fall back to `/tmp/codex-qa-<slug>`. Create the `qa/` subdirectory under the resolved path if it does not exist. Store all issues, screenshots, and verification reports under `<qa-output-path>/qa/`.
10. Detect Compozy mode. If `.compozy/tasks/<slug>/` exists, record the slug and switch into Compozy-aware audit:
   - Read `state.yaml` (read-only — never write to it; `scripts/update-state.py` owns mutation per the cy-codex-loop contract).
   - Read `_techspec.md` (deliverable source of truth) and `_tasks.md` (task roster) when present.
   - List every `task_NN.md` and capture its frontmatter `status:` value (allowed values: `pending`, `in_progress`, `completed`). When `task_NN.md` frontmatter disagrees with `state.yaml`, treat frontmatter as the source of truth.
   - Note the canonical memory slot `.compozy/tasks/<slug>/memory/qa-execution.md` so Step 4A can write audit notes there before any status flips.

**Step 2: Define the QA Scope**

1. Check whether `<qa-output-path>/qa/test-cases/` and `<qa-output-path>/qa/test-plans/` contain artifacts from a prior `qa-report` run. If they exist, read the test plans, test case IDs, and automation annotations to seed the execution matrix and prioritize P0/P1 test cases.
2. Discover implementation-plan artifacts before choosing runtime scenarios. Search for task files, phase plans, PRDs, tech specs, migration plans, tracking checklists, and memory/status files under the user-provided path, `.compozy/tasks/<slug>/`, `docs/`, `.github/`, and repository-specific planning directories.
3. Build a Task Implementation Matrix whenever task/phase/spec artifacts exist. For every task or phase, record (column names chosen to mirror cy-codex-loop frontmatter):
   - `task_path` (e.g., `.compozy/tasks/<slug>/task_07.md`)
   - `declared_status` — literal frontmatter `status:` value: `pending`, `in_progress`, or `completed`
   - `title`, `type`, `complexity`, `dependencies` — mirrored from frontmatter
   - `techspec_deliverable` — linked section in `_techspec.md` when present
   - Requirements, subtasks, checklist items, success criteria, dependent files
   - `implementation_evidence` — files, modules, routes, commands, migrations, seeds, tests
   - `verification_evidence` — commands, browser flows, screenshot paths
   - `qa_verdict` — qa-execution's judgment, **distinct** from `declared_status`: `PASS`, `PARTIAL`, `FAIL`, `REOPEN`, or `BLOCKED`
   - `action` — `none`, `fixed`, `reopened-frontmatter`, or `BUG-NNN.md filed`
   - `linked_bugs` — BUG IDs
4. Do not treat a task `declared_status`, checked checkbox, memory note, or prior agent summary as proof. Verify every completed or claimed-complete task against actual files, public behavior, automated tests, and acceptance criteria.
5. Classify each task with `qa_verdict`:
   - `PASS`: every material requirement and success criterion has implementation and fresh verification evidence.
   - `PARTIAL`: implementation exists but one or more non-critical requirements, tests, or evidence are missing.
   - `FAIL`: claimed behavior does not work or a critical requirement is absent.
   - `REOPEN`: the source `task_NN.md` has `status: completed` in frontmatter but the QA verdict is `PARTIAL` or `FAIL`.
   - `BLOCKED`: execution cannot continue because a concrete prerequisite is missing.
6. For every `REOPEN`: prefer a bounded root-cause fix during QA when the fix is scoped and safe. Otherwise edit the offending `task_NN.md` frontmatter `status:` back to `pending` (or `in_progress` if partial work is salvageable) **and** file `BUG-<num>.md` referencing the task path and failed criteria. Do not write to `state.yaml`; the next cy-codex-loop iteration reconciles because frontmatter wins. When the repository has no Compozy slug and no clear reopen convention, leave source task files intact and file `BUG-<num>.md` naming the task path and failed criteria.
7. Build a short execution matrix covering baseline verification, task implementation audit, changed workflows, unchanged business-critical workflows, and automation follow-up.
8. **STOP. Read `references/checklist.md` in full before finalizing the scope.** Every category in that file (Contract Discovery, Baseline, Flaky Detection, CLI/API, Task Audit, AI Audit, Web UI, Regression, Final Verification, Quality Gates) must map to a planned validation — missing a category here means the gate is not real.
9. Prefer public entry points such as CLI commands, HTTP endpoints, browser flows, worker jobs, and documented setup commands over internal test helpers.
10. Classify each changed or regression-critical public flow as `existing-e2e`, `needs-e2e`, `manual-only`, or `blocked`.
11. Require the `needs-e2e` classification when the repository already supports E2E and the flow is P0, P1, release-critical smoke coverage, or a reproduced public regression. Do not downgrade such flows to `manual-only` without a concrete reason.
12. **STOP. When a Web UI surface exists, read `references/web-ui-qa.md` in full before selecting browser flows.** That file owns the `agent-browser` command set, the snapshot/interact/verify loop, the anti-smoke guardrails, viewport testing, and auth flows. Then select 3-5 critical user flows that cover the changed surface and the most business-critical paths.
13. Create the smallest realistic fixture or fake project needed to exercise the workflow when the repository does not already include one.
14. Treat mocks as a local unit-test boundary only. Do not use mocks or stubs as final proof that a user flow works.

**Step 3: Establish the Baseline**

1. Install dependencies with the repository-preferred command before testing runtime flows.
2. Run the canonical verification gate once before scenario testing to establish baseline health. Execute in fastest-first order: lint and type-check, then build, then unit tests, then integration tests.
3. If the E2E command is separate from the umbrella gate, decide whether to run it in baseline now or after runtime prerequisites are ready, then record that plan explicitly.
4. If the baseline fails, read the first failing output carefully and determine whether it is pre-existing or introduced by current work before moving on.
4a. **Flaky-failure protocol**: When a baseline command fails, before classifying it as pre-existing or new, run the failing test in isolation 3-5 times on the same SHA. If it passes at least once without code changes, classify as `flaky-suspect`, record in `verification-report.md` under the `SUITE HEALTH SNAPSHOT` section (test name, attempts, retry outcome, suspected category), and **do NOT promote to PASS via retry**. **STOP. Read `references/flaky-triage.md` in full before assigning a suspected category or proposing a quarantine.** The taxonomy, diagnosis protocol, and quarantine workflow live there — the three bullets here are tripwires, not the contract.
5. When the project has a Web UI surface, start the dev server in the background using the discovered start command. Confirm readiness by waiting for the server to respond (e.g., `curl -sf -o /dev/null http://localhost:<port>` returns 0, or startup logs emit a ready signal).
6. Start services in the closest supported production-like mode and confirm readiness through observable signals such as health checks, startup logs, or successful handshakes.

**Step 4: Execute CLI and API Flows**

1. Drive CLI and API workflows through the same interfaces a real operator or user would use.
2. Capture the exact command, input, and observable result for each scenario.
3. Validate changed features first, then validate at least one regression-critical flow outside the changed surface.
4. Exercise live integrations when credentials and local prerequisites exist. When they do not, validate every reachable local boundary and record the blocked live step explicitly.
5. Record whether each validated flow already has matching automated coverage or should move to `needs-e2e`.
6. Re-run the scenario from a clean state when the first attempt leaves the environment ambiguous.

**Step 4A: Audit Task Implementations**

Skip this step only when no task, phase, PRD, tech spec, or implementation-plan artifacts exist.

1. Read each task/phase/spec file in the discovered plan set. For large plans, summarize each task into the Task Implementation Matrix instead of copying the full text.
2. For each requirement, subtask, deliverable, and success criterion, locate the expected implementation with repository search and direct file reads. Do not use web search for local code. In Compozy mode, map each requirement to expected paths under `.compozy/tasks/<slug>/` and the codebase areas named by `_techspec.md`.
3. Confirm that claimed files, modules, routes, commands, migrations, seeds, tests, browser screens, and integrations actually exist and match the described behavior.
3a. **Independent Evaluator stance**: **STOP. Read `references/independent-evaluator-protocol.md` in full before forming any task verdict.** That file defines what counts and does NOT count as evidence, and the four anomaly classes (`genuine-failure` / `grader-bug` / `ambiguous-task` / `bypass-exploit`). Tripwire summary: do not accept the implementing agent's transcript, success message, or memory note as evidence. In Compozy mode, read the implementing agent's `.compozy/tasks/<slug>/memory/<phase>.md` artifacts and classify anomalies in the `Errors / Corrections` section of `memory/qa-execution.md` **before** judging the task.
3b. **AI test-hygiene audit**: **STOP. Read `references/ai-implementation-audit.md` in full before scanning the test diff of any task with `declared_status: completed`.** That file owns the Red Flag scanners (RF-1 through RF-6), the Requirement→Test mapping rules, and the verdict matrix. Run the scans against the diff since the task baseline (`git log --follow <test_file>`). Emit verdict `FAIL` automatically when the scanners detect weakened assertions, `.skip`/`.only`, or mocks inserted in tests that the corresponding TC declared as `Integration`/`E2E`. Record findings in the Task Implementation Matrix column `ai_audit_findings` and in the per-task block of `verification-report.md`.
4. Execute the smallest public or automated proof for each material task. Use existing tests when they map directly; otherwise exercise CLI, HTTP, browser, worker, or seed flows through public interfaces.
5. Compare checked boxes and `declared_status` against evidence using the **Requirement → Test mapping** table (defined in `references/ai-implementation-audit.md`, loaded in step 3b). For every Success Criterion in `task_NN.md` (frontmatter or body) and every linked bullet in `_techspec.md`, find the corresponding test by name, reference, or assertion content. Mark each criterion `covers` / `weak` / `missing`. A checked item or `status: completed` without a `covers` row is a QA failure.
6. Mark incomplete completed tasks as `REOPEN` in the matrix. When in Compozy mode, edit the offending `task_NN.md` frontmatter `status:` back to `pending` (or `in_progress` if salvageable) — never write to `state.yaml`. Always commit the audit memory file before flipping any status (memory-precedes-status invariant from cy-codex-loop). Create or update a bug report with the task path, failed checklist item, missing implementation, expected behavior, and command/browser evidence.
7. If the missing work is a bounded root-cause fix inside the QA scope, implement it, add regression coverage, and rerun the task proof. If it is a larger feature, do not quietly pass it; reopen the task or file the issue and keep the final verdict `PARTIAL` or `FAIL`.
8. When in Compozy mode, write audit notes to `.compozy/tasks/<slug>/memory/qa-execution.md` using the canonical sections required by cy-codex-loop: `Objective Snapshot`, `Important Decisions`, `Learnings`, `Files / Surfaces`, `Errors / Corrections`, `Ready for Next Run`. This file must be written **before** any `task_NN.md` frontmatter is flipped.
9. Record every reopened task in the final verification report. A QA run with reopened P0/P1 tasks cannot have an unconditional `PASS` verdict.

**Step 5: Execute Web UI Flows**

Skip this step if the project has no Web UI surface.

1. **STOP. Read `references/web-ui-qa.md` in full before opening a browser.** That file owns the complete `agent-browser` command surface, the snapshot-driven core loop, anti-smoke guardrails, auth flows, and the viewport testing matrix. The command list in step 2 below is a tripwire, not the contract.
2. Use the `agent-browser` CLI (from the `agent-browser` companion skill) for all browser interactions. Tripwire — core loop is **open, snapshot, interact, re-snapshot, verify**. Common verbs include `open`, `snapshot -i`, `click @ref`, `fill @ref "text"`, `screenshot`, `close`. Do not invent commands outside the full set in the reference.
3. For each critical user flow identified in Step 2:
   a. Navigate to the entry URL: `agent-browser open <url>`.
   b. Take an interactive snapshot: `agent-browser snapshot -i` to get element refs (`@e1`, `@e2`, etc.).
   c. Execute the planned interactions using refs: `agent-browser click @e1`, `agent-browser fill @e2 "text"`, etc.
   d. Re-snapshot after every navigation or significant DOM change. Refs become stale after page transitions.
   e. Verify the expected outcome by checking element text, page URL, or visible state via snapshot output.
   f. Capture screenshot evidence: `agent-browser screenshot <qa-output-path>/qa/screenshots/<flow-name>.png`.
4. Test critical form flows: fill valid data and verify success, fill invalid data and verify error messages appear.
5. When the changed surface includes responsive behavior, test at multiple viewports per the viewport-testing section of the reference loaded in step 1.
6. Verify navigation flows: page transitions, back/forward, deep links, and 404 handling.
7. Check error and loading states: trigger error conditions and verify the UI handles them gracefully.
8. Map each browser flow to its automation classification. When a harness exists but no matching spec exists, keep the flow in `needs-e2e` until coverage is added or the blocker is documented.
9. Close the browser session after all flows complete: `agent-browser close`.

**Step 6: Diagnose and Fix Regressions**

1. Reproduce each failure consistently before proposing a fix.
2. Activate companion debugging and test-hygiene skills when available, especially root-cause debugging and anti-workaround guidance.
3. Add or update the narrowest regression coverage that proves the bug when the repository supports automated coverage for that surface, after naming the invariant, owning layer, and canonical suite.
4. When the repository already supports E2E and the failure affects a public browser, HTTP, or CLI flow, add or update E2E coverage instead of stopping at unit or integration proof.
5. If the harness does not exist, keep manual proof and record the blocker rather than bootstrapping a new E2E framework during QA.
6. Fix production code or real configuration at the source of the failure. Do not weaken tests to match broken behavior.
7. Re-run the narrow reproduction, updated automated coverage, impacted scenario, and baseline gate after each fix.
8. For Web UI regressions, reproduce the visual failure with `agent-browser`, capture before/after screenshots under `<qa-output-path>/qa/screenshots/`, and verify the fix through the same browser flow.
9. Use `assets/issue-template.md` to write issue files under `<qa-output-path>/qa/issues/`. Create the subdirectory if it does not exist. Name each file using the `BUG-<num>.md` convention (e.g., `BUG-001.md`). Assign Severity (Critical/High/Medium/Low) and Priority (P0-P3) to every issue. When an issue was discovered while executing a test case from `qa-report`, include the TC-ID in the Related section and fill in the automation follow-up fields.
10. Issue Status vocabulary aligns with cy-codex-loop: `pending` (open and unresolved), `resolved` (fixed during this QA run and verified by re-run), `invalid` (triaged as non-actionable), `flaky-suspect` (one run failed, retry passed; awaiting confirmation runs — see `references/flaky-triage.md`), or `quarantined` (confirmed flaky after diagnosis, isolated from merge gate but still monitored; requires named owner and fix-by date). When an issue reopens a task, set Status to `pending` unless the issue was fixed during the same QA run, include a `Reopens task:` entry pointing at the `task_NN.md` path, and include a `Related` entry with the task's original `declared_status`.

**Step 7: Verify the Final State**

1. Re-run the full repository verification gate from scratch after the last code change.
2. Re-run the most important CLI and API scenarios after the full gate passes.
3. Re-run the narrow E2E specs that were added or updated and, when the repository supports E2E, re-run the canonical E2E command or the smallest repository-defined subset that covers the touched critical flows.
4. When Web UI flows were tested, re-run the critical browser flows and capture final screenshot evidence.
5. Summarize the evidence using `assets/verification-report-template.md` and write the report to `<qa-output-path>/qa/verification-report.md`. The report must include these mandatory fields: Claim, Command, Executed timestamp, Exit code, Output summary, Warnings, Errors, Verdict (PASS or FAIL), plus an Automated Coverage section with support detected, required flows, specs added or updated, commands executed, and manual-only or blocked items. When Web UI flows were tested, append a Browser Evidence section with: Dev server URL, Flows tested count, per-flow entry (name, entry URL, final URL, verdict, screenshot path), Viewports tested, Authentication method, and Blocked flows.
5a. **Suite Health Snapshot**: Populate the `SUITE HEALTH SNAPSHOT` section of the verification report with flaky rate, flaky events list (test, attempts, retry outcome, suspected category), mutation score when a harness exists, coverage delta vs baseline, blocked count, manual-only count, and AI audit findings count.
5b. **Quality Gates**: Populate the `QUALITY GATES` section with PASS/FAIL/N/A per gate: flaky rate <2%, zero `FAIL` from AI audit on P0/P1 tasks, zero `Critical`/`High` issues open, coverage delta ≥ baseline (no regression), zero unresolved `flaky-suspect` on P0 flows. A `FAIL` on any gate blocks an unconditional PASS verdict for the run.
6. When task/phase/spec artifacts exist, append a Task Implementation Audit section with matrix totals, per-task verdicts, reopened/fixed/blocked tasks, and links to bugs or evidence. Explicitly state whether any task with `status: completed` in frontmatter was downgraded via `REOPEN`. When running in a Compozy slug, the final `verification-report.md` PASS feeds cy-codex-loop's `verify.last_status=PASS` precondition for Phase E — do not call `update-state.py`; cy-codex-loop owns that mutation.
7. Report blocked scenarios, missing credentials, or environment gaps with the exact command or prerequisite that stopped execution.
8. Do not claim completion without fresh verification evidence from the current state of the repository.

## Error Handling

- If command discovery returns multiple plausible gates, prefer the broadest repository-defined command and explain the tie-breaker.
- If E2E support signals are weak or contradictory, prefer explicit config files and runnable commands before claiming that the repository supports E2E.
- If no canonical verify command exists, read `references/project-signals.md`, choose the broadest safe install, lint, test, and build commands for the detected ecosystem, and state that assumption explicitly.
- If a required live dependency is unavailable, validate every local boundary that does not require the missing dependency and report the blocked live validation separately.
- If a workflow requires data or services absent from the repository, create the smallest realistic fixture outside the main source tree unless the repository has its own fixture convention.
- If a failure appears unrelated to the requested change, prove that with a clean reproduction before excluding it from the QA scope.
- If the repository has an E2E harness but credentials, runtime services, or test data prevent execution, keep the affected flow classified as `blocked` and report the exact prerequisite that is missing.
- If the repository lacks an E2E harness, do not bootstrap a new framework during QA. Keep live manual evidence and document the automation gap as `manual-only` or `blocked`.
- If `agent-browser` is not installed or the dev server fails to start, skip Web UI flows, document the blocker in the verification report, and continue with CLI and API validation only.
- If a browser flow hangs or times out, close the session with `agent-browser close`, record the failure, and attempt the flow once more from a clean session before marking it as blocked.
- If `task_NN.md` files are marked `status: completed` but contain unchecked subtasks, missing deliverables, or unverified criteria, do not call the QA run a pass. In Compozy mode, write `memory/qa-execution.md` first, then edit frontmatter `status:` back to `pending` or `in_progress`, and file `BUG-<num>.md` per Step 4A. Never write to `state.yaml` directly.
- If a test fails and passes on retry without a code change, do not promote to PASS. Register as `flaky-suspect` per `references/flaky-triage.md`, record the event in the Suite Health Snapshot, and treat any unresolved `flaky-suspect` on a P0 flow as a blocker for the final verdict.
- If the AI test-hygiene audit (Step 4A.3b) detects weakened assertions, skipped tests, or mocks hiding integration in a task with `declared_status: completed`, do not call the QA run a pass. Apply the verdict matrix in `references/ai-implementation-audit.md`, file `BUG-<num>.md` with Type `Functional`, and flip frontmatter `status:` per the standard REOPEN flow.
