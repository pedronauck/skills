---
name: qa-report
description: >-
  Plans real-user QA deliverables: personas, journey maps, exploratory
  charters, persona/journey/tour/CFR test cases, regression suites, Figma
  validation checks, automation intent, and user-impact bug reports. Writes
  artifacts under <qa-output-path>/qa/ for qa-execution to consume. Use when
  planning QA before execution, documenting journey-driven test strategy,
  marking flows that need E2E follow-up, or filing structured bug reports. Do
  not use for live execution, AI implementation audits, CI gate ownership, or
  technical integration/security/performance suites; use qa-execution or
  agent-output-audit instead.
trigger: explicit
argument-hint: "[qa-output-path]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Real-User QA Planner

Plan and document the deliverables that drive real-user QA execution — personas, journey maps, exploratory charters, persona/journey/tour test cases, regression suites, Figma fidelity validations, and user-impact bug reports.

## Required Reading Router

Match your task to the row. Read the listed files **in full before** producing the deliverable. They are not appendices — they are the templates and contracts the deliverable must conform to. Inline content in this SKILL.md is a pointer, not a substitute.

| Task                                              | MUST read                                                                                  |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Defining personas (Step 3 — persona deliverable)  | `references/persona_test_cases.md` + `../qa-execution/references/user-personas.md`         |
| Mapping a journey (Step 3 — journey deliverable)  | `references/journey_test_plans.md` + `../qa-execution/references/journey-maps.md`          |
| Writing an exploratory charter (Step 3)           | `references/exploratory_charters.md` + `../qa-execution/references/exploratory-charters.md` |
| Planning a tour-driven test case (Step 4)         | `references/test_tours_catalog.md` + `../qa-execution/references/test-tours.md`            |
| Generating standard / functional / UI test cases  | `references/test_case_templates.md`                                                        |
| Generating CFR test cases (Step 4)                | `references/cfr_test_cases.md` + `../qa-execution/references/cfr-checks.md`                |
| Building a regression suite (Step 5)              | `references/regression_testing.md`                                                         |
| Validating against Figma (Step 6)                 | `references/figma_validation.md`                                                           |
| Filing a bug report (Step 7)                      | `references/bug_report_templates.md` + `assets/issue-template.md` + `../qa-execution/references/bug-severity-by-user-impact.md` |

## Reference Index

- `references/test_case_templates.md` — Test case variants for real-user QA: Standard, Functional, UI/Visual, Regression, Smoke, Persona, Journey, Charter, Tour, CFR. The Automation Metadata block parsed by `qa-execution`.
- `references/persona_test_cases.md` — TC-PERSONA-* template and persona attributes recording schema.
- `references/journey_test_plans.md` — TC-JOURNEY-* template and journey-driven plan structure.
- `references/exploratory_charters.md` — Charter planning template plus worked examples for common product surfaces.
- `references/test_tours_catalog.md` — Planning view of the test tour catalog. Each tour generates one TC-TOUR-*. Canonical tour definitions live in `../qa-execution/references/test-tours.md` (avoid drift).
- `references/cfr_test_cases.md` — TC-CFR-* template for usability / accessibility / perf-perception / compatibility / recoverability test cases.
- `references/regression_testing.md` — Journey-driven regression suite tiers (Smoke / Targeted / Full / Sanity), prioritization, automation tagging, pass/fail criteria.
- `references/figma_validation.md` — Figma MCP queries, spec → inspect → document workflow, responsive checks at 1280 / 768 / 375.
- `references/bug_report_templates.md` — Standard, UI/Visual, and User-Friction bug variants with full required-field sets. `assets/issue-template.md` is the minimum-viable subset bundled for in-skill use and shared with `qa-execution`.

## Required Inputs

- **qa-output-path** (optional): Directory where all QA artifacts are stored. When provided, create the directory if it does not exist. When omitted, use the current working directory. This path must match the same argument passed to `qa-execution` when both skills are used together.

## Shared Output Structure

All artifacts follow this directory layout, shared with `qa-execution`:

```
<qa-output-path>/qa/
├── test-plans/          # Test plan documents (journey plans, regression suites, persona docs)
│   └── charters/        # Charter drafts (CH-NN-*.md)
├── test-cases/          # Individual test case files (TC-*.md)
├── issues/              # Bug reports (BUG-*.md)
├── screenshots/         # Visual evidence and Figma comparisons
└── verification-report.md  # Generated by qa-execution
```

## Procedures

**Step 1: Resolve Output Directory**

1. If the user provided a `qa-output-path` argument, use that path.
2. Otherwise, default to the current working directory.
3. Create the `qa/` subdirectory under the resolved path, then `qa/test-plans/`, `qa/test-plans/charters/`, `qa/test-cases/`, `qa/issues/`, `qa/screenshots/`.

**Step 2: Identify the Deliverable Type**

Parse the user request to determine which deliverable to generate:

| Request Pattern | Deliverable | Output Path |
|-----------------|-------------|-------------|
| "Define personas for…" | Persona document | `test-plans/personas.md` |
| "Map the journey for…" | Journey map | `test-plans/<journey-slug>-map.md` |
| "Plan exploratory session for…" | Charter draft | `test-plans/charters/CH-<NN>-<slug>.md` |
| "Create test plan for…" | Test Plan (journey-centric) | `test-plans/<feature-slug>-test-plan.md` |
| "Generate test cases for…" | Test cases (TC-FUNC / TC-UI / TC-REG / SMOKE / TC-PERSONA / TC-JOURNEY / TC-TOUR / TC-CFR) | `test-cases/` |
| "Build regression suite…" | Journey-driven regression suite | `test-plans/<suite-name>-regression.md` |
| "Compare with Figma…" | Figma fidelity TC | `test-cases/TC-UI-*.md` |
| "Document bug…" | Bug report (user-impact framing) | `issues/BUG-*.md` |

**Step 3: Generate Test Plans (Journey-Centric)**

1. **STOP. Read `references/journey_test_plans.md` in full before drafting the plan.** That file owns the section structure, the Automation Metadata block, and the entry/exit criteria framed by user impact.
2. Generate a test plan document with these mandatory sections:
   - Executive summary with the user value the change delivers and the journey-level risks.
   - **Personas covered** (cite each from `../qa-execution/references/user-personas.md`).
   - **Journeys mapped** (cite each from `../qa-execution/references/journey-maps.md`; include abandonment paths).
   - **Charters planned** (mission + persona + tour + time-box for each).
   - **CFR scope** (which of the six CFR categories the change affects).
   - Test strategy and approach.
   - Automation strategy — which journeys should become E2E, which remain manual-only, which are blocked.
   - **Entry criteria** (all must hold before execution begins):
     - Build is reachable in a production-parity environment.
     - CI gate has run separately and is green (this skill does not run it — see `agent-output-audit`).
     - Test data and fixture state matches journey preconditions.
     - Personas, journeys, and charters are documented.
   - **Exit criteria** (all must hold before execution concludes):
     - Every P0 journey reached its goal observable.
     - Zero open `Blocks-Completion` or `Data-Loss` bugs on P0 journeys.
     - CFR pass completed on at least 2 journeys with no critical findings open.
     - Automation follow-up registered for every `Missing` or `Blocked` automation annotation.
   - **Retesting vs Regression** distinction:
     - **Retesting** — re-validates the fix of a specific reported defect. Scope is the BUG and its narrow reproduction.
     - **Regression** — validates that a change did not break unrelated journeys. Scope is the journey-driven suite.
   - Risk assessment table (Risk, Probability, User-Impact, Mitigation).
   - Timeline and deliverables.
3. Write the plan to `<qa-output-path>/qa/test-plans/<feature-slug>-test-plan.md`.

**Step 4: Generate Test Cases**

1. **STOP. Read `references/test_case_templates.md` in full before writing any test case.** Variant selection (Functional / UI / Regression / Smoke / Persona / Journey / Charter / Tour / CFR) and per-variant required fields live there.
2. Assign each test case an ID following the naming scheme:

   | Type | Prefix | Example |
   |------|--------|---------|
   | Functional | TC-FUNC- | TC-FUNC-001 |
   | UI/Visual | TC-UI- | TC-UI-045 |
   | Regression | TC-REG- | TC-REG-089 |
   | Smoke | SMOKE- | SMOKE-001 |
   | Persona-driven | TC-PERSONA- | TC-PERSONA-012 |
   | Journey-driven | TC-JOURNEY- | TC-JOURNEY-007 |
   | Charter (planning artifact) | TC-CHARTER- | TC-CHARTER-003 |
   | Tour-driven (off-script) | TC-TOUR- | TC-TOUR-014 |
   | CFR (usability / a11y / perf-perception / compat / recovery) | TC-CFR- | TC-CFR-008 |

3. Each test case must include:
   - **Priority:** P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low).
   - **Persona:** the user role acting (`../qa-execution/references/user-personas.md`).
   - **Objective:** what is being validated, from the user's perspective.
   - **Preconditions:** setup requirements, test data, environment.
   - **Real-User Conditions:** network profile, device, browser, locale, timezone, autofill state. (Replaces the technical `External Dependencies` field.)
   - **Test Steps:** numbered actions in user-language with an `**Expected:**` observable for each.
   - **Edge Cases:** boundary user behaviors (not technical edge cases — see `../qa-execution/references/user-edge-cases.md`).
   - **Automation Target:** `E2E` | `Manual-only`.
   - **Automation Status:** `Existing` | `Missing` | `Blocked` | `N/A`.
   - **Automation Command/Spec:** existing spec path or command when known.
   - **Automation Notes:** why the case should be automated, remain manual, or is blocked.
4. Write each test case to `<qa-output-path>/qa/test-cases/<TC-ID>.md`.
5. When generating test cases interactively, execute `scripts/generate_test_cases.sh <qa-output-path>/test-cases`.

**Step 5: Build Journey-Driven Regression Suites**

1. **STOP. Read `references/regression_testing.md` in full before classifying tiers, prioritizing, or defining pass/fail criteria.** Tier definitions, prioritization rubric, automation-tagging rules, execution-order contract, and `PASS` / `FAIL` / `CONDITIONAL` thresholds live there.
2. Suite tiers are **journey-driven**, not test-case-driven. Each tier picks N journeys, then derives the test cases from those journeys:

   | Suite | Duration | Frequency | Journey count |
   |-------|----------|-----------|---------------|
   | Smoke | 15-30 min | Daily/per-build | 2-4 P0 journeys |
   | Targeted | 30-60 min | Per change | Journeys touching the changed surface |
   | Full | 2-4 hours | Weekly/Release | All P0 + P1 journeys, every persona |
   | Sanity | 10-15 min | After hotfix | The single journey affected by the hotfix |

3. Prioritize journeys using the user-impact lens:
   - **P0:** journeys whose failure causes `Blocks-Completion` or `Data-Loss` for paying users.
   - **P1:** journeys whose failure causes `Trust-Damage` or repeated `Friction` for any persona.
   - **P2:** secondary journeys, edge personas, lower-traffic surfaces.
4. Mark automation candidates explicitly:
   - Tag changed or regression-critical P0/P1 public journeys as `Automation Target: E2E` when the repository already has an E2E harness.
   - Tag bug-driven public regressions as `Automation Status: Missing` until `qa-execution` confirms the spec was added or updated.
   - Tag exploratory, visual-judgment, or unsupported flows as `Manual-only` or `Blocked` with a reason.
5. Define execution order: Smoke first (fail-fast) → P0 journeys → P1 journeys → P2 journeys → exploratory charters.
6. Define pass/fail criteria framed by user impact:
   - **PASS:** every P0 journey reaches its goal; zero `Blocks-Completion` / `Data-Loss` open.
   - **FAIL:** any P0 journey fails to reach goal; any `Blocks-Completion` or `Data-Loss` discovered.
   - **CONDITIONAL:** P1 journeys with documented workarounds; `Friction` / `Trust-Damage` findings with fix plan in place.
7. Write the suite document to `<qa-output-path>/qa/test-plans/<suite-name>-regression.md`.

**Step 6: Validate Against Figma Designs**

Skip this step if Figma MCP is not configured.

1. **STOP. Read `references/figma_validation.md` in full before issuing any Figma MCP query.** Spec→inspect→document workflow, MCP query catalog, responsive checks at 1280/768/375, common-discrepancies catalog.
2. Extract design specifications from Figma using MCP queries: dimensions, colors (exact hex), typography, spacing, border radius/shadows, interactive states.
3. Generate UI test cases (TC-UI-*) that compare each property against the implementation.
4. Test responsive behavior at the standard viewports: 375 / 768 / 1280.
5. When validation reveals discrepancies, generate a bug report following Step 7. Most Figma-fidelity gaps are `Cosmetic` or `Trust-Damage` — promote to `Friction` only when the gap blocks comprehension.
6. Use `agent-browser` (the `qa-execution` companion skill) when browser-based verification is needed.

**Step 7: Create Bug Reports**

1. **STOP. Read `references/bug_report_templates.md` in full before filing any bug.** Standard, UI/Visual, and User-Friction variants with required-field sets. `assets/issue-template.md` is the minimum-viable shared subset.
2. **STOP. Read `../qa-execution/references/bug-severity-by-user-impact.md` in full before classifying impact.** The five-tier user-impact rubric (Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic) and the mapping to legacy Severity/Priority live there.
3. Assign a bug ID with the `BUG-` prefix (e.g., `BUG-001`).
4. Every bug report must include:
   - **Impact (user-side):** Blocks-Completion | Data-Loss | Trust-Damage | Friction | Cosmetic.
   - **Severity:** Critical | High | Medium | Low (mapped from impact).
   - **Priority:** P0 | P1 | P2 | P3 (mapped from impact).
   - **Status:** `pending` | `resolved` | `invalid`.
   - **Persona Affected:** the persona whose session surfaced the bug.
   - **Journey Step:** J-NN journey name + step number.
   - **Environment:** build, OS, browser, viewport, network, locale, URL.
   - **Reproduction:** charter (CH-NN), tour name, plain-language steps.
   - **Expected vs Actual:** clear user-side descriptions.
   - **Impact:** users affected, frequency, workaround, trust cost.
   - **Related:** TC-ID if discovered during a test case, Figma URL if UI bug, related journeys/charters.
5. Write each bug report to `<qa-output-path>/qa/issues/<BUG-ID>.md`.
6. When creating bug reports interactively, execute `scripts/create_bug_report.sh <qa-output-path>/issues`.

**Step 8: Validate Completeness**

1. Verify every test case has an expected user-observable result for each step.
2. Verify every bug report has reproducible user-language steps.
3. Verify traceability: test cases cite the persona and journey; bugs cite the test case and charter when applicable.
4. Verify every persona has at least one test case.
5. Verify every journey has at least one test case.
6. Verify every CFR category planned for the change has at least one TC-CFR-*.
7. Verify every planned critical flow has an explicit automation annotation and that `Missing` or `Blocked` states include a reason.
8. Cross-reference against `../qa-execution/references/checklist.md` for coverage gaps before handing off to execution.

## Companion Skills

- **qa-execution** — Executes the deliverables this skill plans. Reads personas, journeys, charters, test cases from `<qa-output-path>/qa/`; writes verification report and bugs back.
- **agent-output-audit** — Audits AI-implemented work / Compozy task slugs / CI gate / flaky test triage. Use for AI test-hygiene scans (RF-1..RF-6), task-status reconciliation, and quality gates — those concerns are explicitly **out of scope for this skill**.
- **agent-browser** (curated) — Web UI driver invoked by `qa-execution` during Step 6 Figma validation when browser-based verification is needed.

## Bug Severity vs User Impact

Severity is the engineering-triage view. Impact is the user-side view. Both must be filled per bug. The full mapping rubric lives in `../qa-execution/references/bug-severity-by-user-impact.md`:

| Impact (user-side) | Default Severity | Default Priority | Release impact |
|---|---|---|---|
| Blocks-Completion | Critical | P0 | Blocker on any P0 journey |
| Data-Loss | Critical | P0 | Blocker on any journey |
| Trust-Damage | High | P1 | Multiple on same journey = blocker |
| Friction | Medium | P2 | Tracked as redesign signal |
| Cosmetic | Low | P3 | Batched into polish follow-up |

## Error Handling

- If the `qa-output-path` directory cannot be created, report the error and fall back to the current working directory.
- If Figma MCP is not configured, skip Figma validation steps and note the gap in the test plan.
- If `agent-browser` is not available for UI validation, generate test cases as documentation for manual execution and note the limitation.
- If the repository does not have a known E2E harness, mark affected cases as `Manual-only` or `Blocked` instead of inventing automation commands.
- If the user provides a feature description that is too vague to generate test cases, ask for specific journeys, personas, or acceptance criteria before proceeding.
- If a request is for a technical integration / security / performance test case (TC-INT, TC-SEC, TC-PERF, TC-API), explain that those types are out of scope for real-user QA planning. Direct the user to integration tests in code, SAST/DAST tools, and load testing tools respectively. If the user wants to audit AI-implemented work, direct them to `agent-output-audit`.
