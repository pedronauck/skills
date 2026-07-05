---
name: qa-execution
description: >-
  Runs real-user dogfooding sessions through public interfaces: persona-driven
  journey walks via browser, thematic tours, edge probes, experiential lenses,
  and paper-cut hunting. Reads plans from the living QA docs tree
  (<qa-docs-path>, default docs/qa/), dedups against the global bug registry
  before filing, applies the fix-loop governor (auto-fix only small and
  contained, with a regression test; escalate the rest to a human), updates
  state.csv verdicts, and writes an incremental per-run report created the
  moment the session matrix exists. Use when validating a release candidate,
  branch diff, migration, or user-facing change against production-like
  behavior. Do not use for CI gate runs, AI implementation audits, or
  integration/security/performance suites; use agent-output-audit for those.
argument-hint: "[qa-docs-path]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Real-User QA Execution

QA the way a real person experiences the product: a persona walks a journey through public interfaces, feels the friction, hits the edges, and reports what happened. The session is the work; the living docs remember it.

Three rules define everything here:

1. **Stay in persona.** Every interaction goes through what a real user can see and touch. No dev-tools shortcuts to "verify", no reading code to decide what should happen mid-session, no patching over a stall. What the persona can't reach, the session can't use.
2. **Claims carry proof.** A `pass` means the expected observable was seen, confirmed through an independent read path, and survives refresh — with evidence captured. A green matrix nobody can audit is a lie with extra steps.
3. **Write back or it didn't happen.** Every session updates the living tree: charter debrief, `state.csv` verdicts, bug registry, dated report. A round that leaves no trace in the tree did not run.

## Required Reading Router

Match your task to the row. Read the listed files **in full before** producing output. They are not appendices — they are load-bearing. Inline content in this SKILL.md is a pointer, not a substitute.

| Task                                                        | MUST read                                                            |
| ----------------------------------------------------------- | -------------------------------------------------------------------- |
| Starting any run: scope, matrix, report creation (Steps 1-2)| `references/status-and-reporting.md`                                 |
| Walking a journey session in persona (Step 3)               | `references/session-protocol.md` + `references/persona-fidelity.md`  |
| Running tours and edge probes (Step 4)                      | `references/tours.md` + `references/edge-cases.md`                   |
| Running the experiential lens pass (Step 5)                 | `references/lenses.md`                                               |
| Filing or updating bugs (Step 6)                            | `../qa-report/references/bug-registry.md`                            |
| Deciding whether to fix now or escalate (Step 7)            | `references/fix-loop.md`                                             |
| Updating `state.csv` verdicts (Step 8)                      | `../qa-report/references/state-schema.md`                            |
| Drafting a charter missing from the plan (Step 2)           | `../qa-report/references/session-charters.md`                        |

## Reference Index

- `references/session-protocol.md` — the persona session loop: browser driving, snapshot/act/verify cycle, the evidence standard (independent read path, survives refresh), paper-cut capture, session logging.
- `references/persona-fidelity.md` — the guardrails that keep the session real: public-interfaces-only rule, forbidden evaluator framings, stall-is-a-finding, the allowlist.
- `references/tours.md` — canonical 10-tour catalog (Feature, Money, Garbage, Back-Button, Multi-Tab, Network, Locale, Paste, Autofill, Interrupt) with the surface-to-tour matrix.
- `references/edge-cases.md` — the non-technical edge cases real users hit: navigation, form, session, network, device, locale, accessibility, interrupt, trust/recovery.
- `references/lenses.md` — six experiential lenses a dogfooder holds during the walk: usability, accessibility, perceived performance, compatibility, error recoverability, production parity.
- `references/fix-loop.md` — the governor: what may be fixed inside the run, regression-test-per-fix, one logical fix per commit, "Decisions for a Human", and the exit gate.
- `references/status-and-reporting.md` — the 6-value session status enum, report lifecycle (created at matrix time, updated incrementally), tracker write-back, and the round-close checklist.
- `assets/report-template.md` — the per-run report (seeded to `<qa-docs-path>/templates/report.md` at bootstrap; prefer the project copy).
- Cross-skill canonicals (one-way dependency, zero duplication): `../qa-report/references/bug-registry.md` (bug ids, dedup, impact rubric), `../qa-report/references/state-schema.md` (tracker columns and enums), `../qa-report/references/session-charters.md` (charter format this skill consumes).

## Required Inputs

- **qa-docs-path** (optional): Root of the living QA docs tree. Defaults to `docs/qa` at the repository root. If the tree does not exist, run `qa-report` first (or bootstrap the minimal tree per `../qa-report/references/qa-docs-layout.md`) — this skill never writes to a temp directory.

## Procedures

**Step 1: Resolve the Tree, the Scope, and the Preconditions**

1. Resolve `<qa-docs-path>` and read, in order: `README.md` (entry points, dev-server command, area codes), `state.csv`, open bugs in `bugs/`, and the charters planned for this cycle. The tree is the memory — running without reading it recreates the duplication this design exists to kill.
2. Determine the scope:
   - **Branch/PR run:** diff against the trunk and enumerate the user-visible changes; the run covers the journeys they touch plus one adjacent canary journey. No user-visible change → report that and stop; there is nothing to dogfood.
   - **Release/full run:** the journeys and charters the cycle plan marked in scope.
3. Preconditions: the automated suite is green (CI is a precondition, not a QA step — gaps route to `agent-output-audit`), and the product is reachable in a production-parity build (dev server per README, real auth path, no mocks). Not reachable → surface the exact gap and stop.

**Step 2: Build the Session Matrix and Create the Report NOW**

1. **STOP. Read `references/status-and-reporting.md` in full before assembling the matrix or creating the report.** The status enum and the report lifecycle are exact contracts owned by that file.
2. Assemble the session matrix from the planned charters: persona × journey × tour × time-box, ordered by risk. If a charter is missing for an in-scope journey, draft it per `../qa-report/references/session-charters.md` before running — never walk unplanned.
3. Create `<qa-docs-path>/reports/<YYYY-MM-DD>-<scope>.md` from the report template **immediately** — before the first session. Fill scope, personas, flows, and the matrix with every row `Pending`. The report on disk is the source of truth for resume; update it after every session and every fix, not at the end.

**Step 3: Walk Journey Sessions in Persona**

1. **STOP. Read `references/session-protocol.md` and `references/persona-fidelity.md` in full before the first session.** The bullets below are tripwires, not the contract — the evidence standard and the fidelity rules live in those files.
2. For each charter, in matrix order: adopt the persona (device, network, locale profile), enter through the charter's real entry point, and walk the journey verb by verb — verifying each step's expected observable, capturing checkpoint evidence, and following branch and abandonment paths where the flow marks them.
3. Verify to the **true end state**: side effects landed correctly (right recipient, right content, right destination), the result survives refresh and fresh load. Confirm through an independent read path before recording `Pass`.
4. Hunt paper cuts throughout: persona-felt friction that no functional check fails. Record each with persona + severity; sharp ones enter the fix loop as findings.
5. When something is only completable by a human (real payment, external email, SMS), mark the leg `Blocked (needs human verify)` with exact instructions for the human — never fake the leg.
6. End each session at the time-box, append the debrief to the charter file, and update the report's matrix row.

**Step 4: Run Tours and Edge Probes**

1. **STOP. Read `references/tours.md` and `references/edge-cases.md` in full before running any tour or probe.** Each tour names off-script actions specific to its theme — they are not interchangeable.
2. Run each charter's single tour against its surface, in persona, inside the box, asking at each action: *"would this matter for this tour's theme?"*
3. Pick 5-10 edge cases matching the surface and persona; attempt them; record attempted-and-clean as evidence too.

**Step 5: Experiential Lens Pass**

1. **STOP. Read `references/lenses.md` in full before starting the lens pass.** The six lens checklists and their severity defaults live there.
2. Pick the 2 journeys covering the largest changed surface and re-walk them holding the six lenses — a 45-minute box, findings recorded as `pass` / `friction` / `fail` per lens.

**Step 6: File Bugs into the Registry**

1. **STOP. Read `../qa-report/references/bug-registry.md` in full before minting any id.**
2. Dedup first: search `bugs/` and the affected rows' `bug_ids`. Re-found → append `## Re-found`; regressed → reopen with `## Regressed`. Only genuinely new symptoms get a new `BUG-NNNN`.
3. File with the user first: impact tier, persona, journey step, reproduction from the persona's entry point, evidence paths. Link the id into the affected `state.csv` rows.

**Step 7: Fix Loop (governed)**

1. **STOP. Read `references/fix-loop.md` in full before touching any code.**
2. Judge the size of each fix **before** editing: auto-fix only when small, well-understood, low-risk, contained, and free of product trade-offs. Everything else goes to the report's **Decisions for a Human** with options and a recommendation.
3. Every auto-fix ships a regression test that failed before and passes after (or a documented replay with the stated reason no automated test is meaningful), one logical fix per commit, and a re-run of the impacted journey **and its adjacent journeys** under the same persona.

**Step 8: Close the Round**

1. **STOP. Re-read the round-close checklist in `references/status-and-reporting.md`.**
2. Exit gate: run the project's full automated suite once. A green matrix with a red suite is not ready — say so in Final Status.
3. Write back: every matrix row terminal (no `Pending` left), `state.csv` verdicts updated per the schema, bug statuses current, charter debriefs appended, report's Final Status written with totals by impact tier.
4. Never claim PASS without fresh evidence from the current build. An empty report section is a coverage gap, not a green light.

## Companion Skills

- **qa-report** — Plans what this skill runs and owns the living tree's schemas (tracker, bug registry, charters). Results written here feed the next cycle's planning.
- **agent-output-audit** — Owns CI verification gates, AI test-hygiene scans, task-status reconciliation, flaky-test triage. If a session uncovers those concerns, file the finding and name that gate; do not pivot mid-session.
- **agent-browser** — The browser driver used in Steps 3-5; command surface documented in `references/session-protocol.md`.

## Error Handling

- If `<qa-docs-path>` does not exist, stop and run `qa-report` bootstrap first. Never invent a parallel output location.
- If the dev server or browser tooling is unavailable, mark the browser legs `Blocked (needs human verify)` with the exact missing prerequisite, and continue with CLI/HTTP journeys that remain walkable in persona.
- If a browser flow hangs, close the session, record it, retry once from a clean session; then mark blocked. A stall is a finding to file, not a thing to work around (see `persona-fidelity.md`).
- If credentials or test data are missing for a journey, mark its sessions blocked with the exact prerequisite and proceed with the rest.
- If the matrix exceeds the available window, cut by risk (Blocks-Completion candidates first, then Data-Loss, then Trust-Damage), mark the cut sessions `Skipped` with reasoning, and say so in Final Status — never silently shrink coverage.
- If a fix attempt grows beyond the governor's bounds mid-edit, revert it, restore the row to `Fail`, and move the item to Decisions for a Human. Half-applied fixes are worse than open bugs.
