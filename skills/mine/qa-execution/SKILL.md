---
name: qa-execution
description: >-
  Executes real-user QA sessions through public interfaces using personas,
  journeys, exploratory charters, test tours, edge-case probes, CFR checks, and
  browser evidence. Reads qa-report artifacts from <qa-output-path>/qa/ when
  present, captures issues/screenshots/reports under the same output tree, and
  classifies bugs by user impact. Use when validating a release candidate,
  migration, refactor, or user-facing change against production-like behavior.
  Do not use for AI implementation audits, task-status reconciliation, CI gate
  runs, integration/security/performance templates, or flaky-test triage; use
  agent-output-audit for those.
argument-hint: "[qa-output-path]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Real-User QA Execution

QA the way a real person would experience the product: assigned a persona, walking a journey, exercising charters bound to specific tours, probing the edges users actually hit, and validating CFRs that no single feature owns.

## Required Reading Router

Match your task to the row. Read the listed files **in full before** producing output. They are not appendices — they are load-bearing. Inline content in this SKILL.md is a pointer, not a substitute.

| Task                                                                 | MUST read                                                                                  |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Assigning personas to sessions (Step 2)                              | `references/user-personas.md`                                                              |
| Selecting high-value journeys (Step 2)                               | `references/journey-maps.md`                                                               |
| Writing exploratory charters and picking tours (Step 3)              | `references/exploratory-charters.md` + `references/test-tours.md`                          |
| Executing browser flows (Step 4)                                     | `references/web-ui-qa.md`                                                                  |
| Probing off-script user edge cases (Step 5)                          | `references/test-tours.md` + `references/user-edge-cases.md`                               |
| Running the Cross-Functional Requirement pass (Step 6)               | `references/cfr-checks.md`                                                                 |
| Classifying bug severity by user impact (Step 7)                     | `references/bug-severity-by-user-impact.md`                                                |
| Building the QA scope checklist                                      | `references/checklist.md`                                                                  |

## Reference Index

- `references/user-personas.md` — Canonical persona set (New User / Power User / Casual User / Mobile User / Accessibility-Reliant / Recovering User), attributes, and assignment rules.
- `references/journey-maps.md` — Journey anatomy (entry → actions → goal → exit + abandonment), high-value journey selection, mapping template.
- `references/exploratory-charters.md` — Charter format (mission + persona + surface + tour + time-box), charter modes (freestyle / strategy-based / scenario-based / collaborative / charter-with-tour), worked examples, debrief format.
- `references/test-tours.md` — Canonical tour catalog: Feature, Money, Garbage, Back-Button, Multi-Tab, Network, Locale, Paste, Autofill, Interrupt. One tour per charter.
- `references/user-edge-cases.md` — Catalog of non-technical edge cases real users hit (navigation, form, session, network, device, locale, accessibility, interrupt, trust/recovery).
- `references/cfr-checks.md` — 45-minute CFR pass: usability (Nielsen short list), accessibility (WCAG AA quick check), perceived performance, compatibility, error recoverability, production parity.
- `references/bug-severity-by-user-impact.md` — User-impact rubric (Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic) with mapping to legacy severity/priority.
- `references/web-ui-qa.md` — `agent-browser` command set, snapshot/interact/verify loop, auth flows, viewport testing, anti-smoke guardrails.
- `references/checklist.md` — Real-user QA checklist by category: persona coverage, journey coverage, charter coverage, off-script & edge case coverage, CFR coverage, bug filing, browser evidence, final report.

## Required Inputs

- **qa-output-path** (optional): Directory where QA artifacts (issues, screenshots, verification reports) are stored. When provided, create the directory if it does not exist and use it for all QA outputs. When omitted, fall back to repository conventions or `/tmp/qa-execution-<slug>`.

## Procedures

**Step 1: Resolve Output Directory and Read qa-report Artifacts**

1. Resolve the QA artifact directory. If the user provided a `qa-output-path` argument, use it. Otherwise use repository conventions, falling back to `/tmp/qa-execution-<slug>`. Create the `qa/` subdirectory and `qa/screenshots/`, `qa/issues/` under it.
2. Check whether `<qa-output-path>/qa/test-plans/`, `<qa-output-path>/qa/test-cases/`, and any persona/journey/charter artifacts exist from a prior `qa-report` run. If they do, read them to seed Steps 2-3: persona assignments, journey maps, charter missions, and TC-* test cases prioritized by qa-report.
3. Confirm the dev server URL or the runtime entry point is reachable in a production-parity build before any test runs. **Do not run QA on a build that hasn't passed CI** — that's `agent-output-audit`'s job, not this skill's. If CI hasn't been confirmed green, surface the gap and stop.

**Step 2: Assign Personas and Select Journeys**

1. **STOP. Read `references/user-personas.md` in full before picking personas.** The six canonical personas (New User / Power User / Casual User / Mobile User / Accessibility-Reliant / Recovering User) and their attribute schema live there. The persona-of-convenience anti-pattern is the most common QA failure mode.
2. Pick **at least 3 personas** for this release-candidate QA pass, covering the product's actual audience. Include at least one Mobile User when a mobile surface exists; include at least one Accessibility-Reliant persona unless explicitly out of scope (record the skip reasoning).
3. **STOP. Read `references/journey-maps.md` in full before selecting journeys.** Journey anatomy (entry → actions → goal → exit + abandonment paths), high-value journey selection criteria, and the journey-map template live there.
4. Pick **3-7 high-value journeys** for this pass. Use these prompts: what generates revenue, what handles sensitive data, what's used most frequently, what's the first impression, what's the recovery path. Include at least one cross-feature journey when the product has them.
5. For each journey, document at least one **abandonment path** — the realistic way a real user gives up partway through. Abandonment paths surface the highest-impact bugs.
6. Record persona × journey assignments in working notes. Each journey gets at least one persona; each persona gets at least one journey.

**Step 3: Plan Exploratory Charters**

1. **STOP. Read `references/exploratory-charters.md` in full before writing any charter.** Charter anatomy (mission + persona + surface + tour + time-box), charter modes, time-box guidance, debrief format. Charters are the single biggest predictor of whether the session finds real bugs.
2. **STOP. Read `references/test-tours.md` in full before picking tours.** The 10-tour catalog (Feature / Money / Garbage / Back-Button / Multi-Tab / Network / Locale / Paste / Autofill / Interrupt) and the surface-to-tour matrix live there.
3. For each persona × journey × surface, write a charter with: a one-sentence mission, the persona, the entry URL, **exactly one tour**, and a time-box (30 / 60 / 90 minutes). Save charter drafts to `<qa-output-path>/qa/test-plans/charters/` when applicable.
4. Mix charter modes deliberately: at least one charter-with-tour for each P0 journey, at least one freestyle for new surfaces, at least one scenario-based for cross-feature journeys.
5. Order the session list by risk: highest-impact journey × highest-blast-radius tour first. Run the most fragile combinations while tester attention is fresh.

**Step 4: Execute Journey Sessions (Web UI primary)**

Skip this step's Web UI portion if the project has no Web UI surface — but still run CLI/HTTP journeys against the same persona × journey × charter plan.

1. **STOP. Read `references/web-ui-qa.md` in full before opening a browser.** That file owns the complete `agent-browser` command surface, the snapshot-driven core loop, auth flows, and the viewport testing matrix.
2. For each charter from Step 3, in the order set there:
   - **Stay in persona.** If a New User wouldn't know about a feature, don't use it. If a Power User would use a keyboard shortcut, use it.
   - Navigate to the entry URL: `agent-browser open <url>`. Confirm the persona's device profile (viewport, throttle, locale) via `--session` + `--viewport` flags as appropriate.
   - Snapshot interactively: `agent-browser snapshot -i`.
   - Walk the journey verb by verb. After every interaction, re-snapshot and verify the expected observable for that step. Time each step against the journey's time budget.
   - Capture a screenshot at every verification checkpoint: `agent-browser screenshot <qa-output-path>/qa/screenshots/<journey-id>-step<N>.png`.
   - Record observed time-to-feedback for any action that should feel fast (button clicks, form validation).
   - When the journey forks into a branch or an abandonment path, follow it and record outcome.
3. For CLI / HTTP journeys, drive workflows through the same interfaces real operators or end-users would use, not internal test helpers. Capture exact command, input, and observable result for each scenario.
4. Close the browser session after all flows complete: `agent-browser close`.

**Step 5: Run Off-Script Tours & User Edge Cases**

1. **STOP. Read `references/test-tours.md` in full before launching tours.** Each tour names off-script actions specific to its theme — they are not interchangeable.
2. **STOP. Read `references/user-edge-cases.md` in full before probing edges.** That file's catalog (navigation, form, session, network, device, locale, accessibility, interrupt, trust/recovery) is the canonical edge-case list — not unit-level edge cases.
3. For each charter from Step 3, run the assigned tour against the surface:
   - Stay in persona, stay in time-box.
   - Execute the tour's off-script actions, asking *"would this matter for this tour's theme?"* at each one.
   - Pick 5-10 relevant entries from `user-edge-cases.md` that match the surface and persona. Don't try every edge case — the time-box governs.
4. For every finding, capture the persona felt (not just the technical observation): *"a mobile user with one hand could not reach the submit button"* is more actionable than *"button is 8px out of touch target"*.
5. Document attempted edge cases in the charter debrief whether they fired or not — confirmed-clean is also evidence.

**Step 6: Cross-Functional Requirement Pass**

1. **STOP. Read `references/cfr-checks.md` in full before starting the CFR pass.** That file owns the six CFR categories (usability, accessibility, perceived performance, compatibility, error recoverability, production parity) and the 45-minute time-box.
2. Pick **2 journeys** from your charters that exercise the largest surface area. Re-walk them as a CFR audit, not a journey verification.
3. At each step, ask the six CFR categories. Mark each `pass`, `friction`, or `fail`.
4. Run the WCAG AA quick check (keyboard, screen reader, visual) on the changed surface. The full conformance audit is out of scope — short check only.
5. Run the compatibility smoke (latest Chrome + Safari + Firefox + iOS Safari + Android Chrome) on any surface that touched layout or forms.
6. Validate production parity: not in incognito, cookies enabled, realistic extension set, real auth path, realistic worst-case network.
7. File one bug per CFR finding using the severity rubric in `references/bug-severity-by-user-impact.md`. Most CFR findings are `Friction` or `Trust-Damage`; promote to `Blocks-Completion` only when the failure abandons the user.

**Step 7: File Bugs by User Impact**

1. **STOP. Read `references/bug-severity-by-user-impact.md` in full before classifying any bug.** The five-tier user-impact rubric and the mapping to legacy Severity/Priority live there.
2. Use `assets/issue-template.md` to write issue files under `<qa-output-path>/qa/issues/`. Name each `BUG-<NNN>.md`.
3. For every bug, fill:
   - `Impact (user-side):` — Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic.
   - `Severity:` and `Priority:` — via the mapping rubric.
   - `Persona Affected:` — the persona whose session surfaced the bug.
   - `Journey Step:` — the J-NN journey name and the step number where it fired.
   - Cite the charter (CH-NN) and tour in `Reproduction:`.
4. When a bug ties to a `qa-report` test case, include the TC-ID in `Related`. The `Automation Follow-up:` block (audit-only) does not apply to this skill — leave it out.
5. Reproduce each failure consistently before proposing a fix. For bounded root-cause fixes inside the QA scope, apply the fix, re-run the impacted journey, and update the bug to `resolved`. For larger features, file and move on; do not silently pass.

**Step 8: Write the Verification Report**

1. Re-run the most critical journeys from Step 4 after any code change made during the QA pass.
2. Summarize evidence using `assets/verification-report-template.md` and write the report to `<qa-output-path>/qa/verification-report.md`.
3. Mandatory sections (per the template):
   - **PERSONA COVERAGE** — every persona × charter combination.
   - **JOURNEY EXECUTION LOG** — per-step verdicts, screenshot paths, abandonment paths covered.
   - **CHARTER LOG** — mission, tour, time-box, debrief, suggested-next per charter.
   - **OFF-SCRIPT FINDINGS** — edge cases attempted and outcomes.
   - **CFR FINDINGS** — pass/friction/fail per CFR category per journey.
   - **BROWSER EVIDENCE** — dev server, flows, viewports, auth, blocked flows.
   - **ISSUES FILED** — totals by user impact tier and by legacy severity.
4. Disclose blocked sessions, missing credentials, or environment gaps explicitly with the exact prerequisite that stopped execution.
5. Do not claim PASS without fresh evidence from the current state of the build. The verification report is the contract — if a section is empty, that's a coverage gap, not a green light.

## Companion Skills

- **qa-report** — Plans the deliverables this skill consumes: personas, journey maps, charters, test cases, regression suites, Figma fidelity validation. The shared output directory `<qa-output-path>/qa/` is the contract between them.
- **agent-output-audit** — Audits AI-implemented work / Compozy task slugs. Owns the CI verification gate, AI test-hygiene scans (RF-1..RF-6), the independent evaluator protocol, flaky-test triage, task-status reconciliation, and quality gates. **Do not duplicate that work here**; if a real-user QA session uncovers AI-implementation concerns, file the bug and recommend running `agent-output-audit` separately.
- **agent-browser** (curated) — Web UI driver used in Step 4 and Step 5. The command set is documented in `references/web-ui-qa.md`.

## Error Handling

- If the build is not reachable in a production-parity environment, stop and surface the gap. Do not test against local mocks or a CI-only artifact — the QA result will not generalize.
- If the dev server fails to start or `agent-browser` is unavailable, skip Web UI flows, document the blocker in the verification report, and continue with CLI/HTTP journeys when applicable.
- If a browser flow hangs or times out, close the session with `agent-browser close`, record the failure, and attempt the flow once more from a clean session before marking it as blocked.
- If credentials, test data, or environment access are missing for a planned journey, classify it as `blocked`, document the exact prerequisite, and proceed with the remaining journeys.
- If the persona × journey × charter list exceeds the available QA window, prioritize by user-impact risk (Blocks-Completion candidates first, then Data-Loss, then Trust-Damage). Defer lower-impact journeys to a follow-up pass and record the deferral.
- If a session uncovers something out of scope for real-user QA (CI failure, test code looking suspicious, task status mismatched, flaky test in an automated suite), file the bug, name the right gate (`agent-output-audit` or the CI pipeline), and do not pivot mid-session.
- If a CFR pass exceeds the 45-minute box, stop and file a follow-up CFR charter. Tester fatigue at hour 2 produces false positives.
- If the dev server requires real third-party services (payment, email, SSO) and they are unavailable, validate every reachable boundary and record the live-step blockers explicitly. Do not substitute mocks for the final user proof.
