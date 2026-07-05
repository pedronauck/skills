# Analysis: qa-report-skill

Read-only exploration of the slice `qa-report-skill` (ordinal `01`) for the research prompt:

> Map QA skills context: qa-report/qa-execution skills structure, real-scenario-qa complementary skill, AGH QA folder sprawl, feature-status.csv tracking pattern, docs/_memory specs about QA dogfooding

## Scope

- Slice question: How is the `qa-report` skill structured today — what deliverables, templates, and workflow does it prescribe; where does its output-layout contract assume per-round isolated artifacts under `<qa-output-path>/qa/`; and where does its design bias toward technical test-case coverage instead of real-user dogfooding?
- Primary sources: `/Users/pedronauck/Dev/compozy/skills/skills/mine/qa-report/` — `SKILL.md`, all 9 files in `references/` (`bug_report_templates.md`, `cfr_test_cases.md`, `exploratory_charters.md`, `figma_validation.md`, `journey_test_plans.md`, `persona_test_cases.md`, `regression_testing.md`, `test_case_templates.md`, `test_tours_catalog.md`), `assets/issue-template.md`, and `scripts/` (`create_bug_report.sh`, `generate_test_cases.sh`). Diff-compare against the deployed copy at `/Users/pedronauck/dev/compozy/agh/.agents/skills/qa-report/`.
- Sources read in full vs. sampled: ALL 13 files in the source skill read in full (SKILL.md 247 lines, 9 references totaling ~2,419 lines, 1 asset 78 lines, 2 scripts 694 lines). Deployed copy verified byte-for-byte via `diff -r` + SHA-1, not re-read line-by-line.
- Total candidate sources surveyed: 13 files in source skill + 13 files in deployed copy (verified identical) = 13 unique sources.

## Overview

The `qa-report` skill is the **planning** half of a two-skill QA system (the other being `qa-execution`). Its front matter (`SKILL.md:1-18`) names it a "Real-User QA Planner" and prescribes deliverables: personas, journey maps, exploratory charters, persona/journey/tour/CFR test cases, regression suites, Figma validation checks, and user-impact bug reports. It is explicitly a *planner*, not an executor: it writes artifacts under `<qa-output-path>/qa/` for `qa-execution` to consume (`SKILL.md:7`, `224`). The skill is router-shaped — a 247-line `SKILL.md` plus 9 reference files, 1 asset template, and 2 interactive bash scripts.

Rhetorically the skill is already strongly anti-technical-case. It repeatedly states that integration / security / performance / API test cases (TC-INT, TC-SEC, TC-PERF, TC-API) are **out of scope** and were "removed deliberately" (`SKILL.md:11-12`, `247`; `references/test_case_templates.md:19`; `scripts/generate_test_cases.sh:76`). Everything is framed around personas, journeys, charters, tours, CFR categories, and a five-tier user-impact rubric (Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic). So at the language level the redesign goal "make QA behave like a real user dogfooding" is largely already adopted.

The bias the operator should act on is **structural, not rhetorical**: the skill removed the *technical test types* but kept the *test-case-centric artifact model*. The atomic unit the skill produces is a `TC-*.md` file (9 prefixes: TC-FUNC / TC-UI / TC-REG / SMOKE / TC-PERSONA / TC-JOURNEY / TC-CHARTER / TC-TOUR / TC-CFR). Even persona sessions, journeys, and charters get reduced to a TC-* file. Completeness is enforced as "every persona has at least one test case" (`SKILL.md:216-218`), not "every journey was walked by a real user this cycle." This is a coverage-matrix instinct wearing a persona costume — and it is the main thing standing between the current skill and a true dogfooding model.

The output-layout contract is the second clear target. The skill mandates a fresh `<qa-output-path>/qa/` tree per run (`SKILL.md:56-69`, `72-76`), with timestamp-based bug IDs (`scripts/create_bug_report.sh:62` — `BUG-$(date +%Y%m%d%H%M%S)`) and user-entered TC IDs. There is **no** append, update, dedup, or cross-round state primitive anywhere in the skill. This directly conflicts with the redesign's "centralize QA artifacts as living repo docs (docs/qa/ with CSV state tracking)" goal. The deployed copy at `/Users/pedronauck/dev/compozy/agh/.agents/skills/qa-report/` is byte-for-byte identical to the source (all 13 SHA-1 checksums match; `diff -r` exits 0) — so the redesign can treat the source as the single canonical text and does not need to reconcile divergence.

## Mechanisms / Patterns

- **Required Reading Router (`SKILL.md:24-38`):** A task→file table that mandates reading named reference files *in full before* producing each deliverable. Each row pairs an in-skill planning reference with a canonical definition in `../qa-execution/references/`. Effective as a fidelity gate, but it creates a heavy read tax (Step 3 can require 3 files; Step 7 requires 3 files) and couples this skill to 6 sibling files in `qa-execution`.

- **Shared Output Structure (`SKILL.md:56-69`):** The mandated artifact tree: `<qa-output-path>/qa/{test-plans/, test-plans/charters/, test-cases/, issues/, screenshots/, verification-report.md}`. `verification-report.md` is the only file this skill does NOT own (qa-execution generates it). Every other artifact is written fresh per run.

- **Per-round resolve-and-create (`SKILL.md:72-76`):** Step 1 resolves the output dir (argument or CWD) and `mkdir -p`s the full subtree. There is no "open existing tree and append" path — the procedure assumes a fresh tree each invocation. `SKILL.md:242` even frames a creation failure as "fall back to the current working directory", reinforcing the per-run isolation model.

- **Deliverable parse table (`SKILL.md:82-91`):** Step 2 maps request patterns to deliverable types and their exact write paths. This is the skill's full deliverable taxonomy: persona doc, journey map, charter draft, test plan, test cases (8 prefixes), regression suite, Figma TC, bug report.

- **9-prefix test-case ID scheme (`SKILL.md:124-136`, `references/test_case_templates.md` "Quick Reference"):** TC-FUNC / TC-UI / TC-REG / SMOKE / TC-PERSONA / TC-JOURNEY / TC-CHARTER / TC-TOUR / TC-CFR. Each produces an individual `<TC-ID>.md` file under `test-cases/`. This makes the *test case* the atomic artifact of the skill — even for persona/journey/charter/tour work, which are conceptually sessions but get persisted as TC-* files.

- **Automation Metadata block (`SKILL.md:138-149`, `references/test_case_templates.md` "Automation Metadata"):** Every test case carries `Automation Target: E2E | Manual-only`, `Automation Status: Existing | Missing | Blocked | N/A`, `Automation Command/Spec`, `Automation Notes`. This is a coverage-tracking field set borrowed from technical test management and attached to every case, pulling the planner toward "which cases should become E2E specs" — a technical concern — even on persona/charter cases.

- **Coverage-completeness enforcement (`SKILL.md:211-220`, Step 8):** "Verify every persona has at least one test case. Verify every journey has at least one test case. Verify every CFR category planned for the change has at least one TC-CFR-*." The unit of completeness is "has a TC file." This is the explicit lever that turns the persona vocabulary back into test-case accumulation.

- **Coverage matrices in references:** `references/persona_test_cases.md:69` ("Persona × Surface coverage matrix"), `references/cfr_test_cases.md` ("CFR coverage strategy" — "at least one TC-CFR-* per category"), `references/regression_testing.md` (Smoke/Targeted/Full/Sanity tier tables with journey counts and pass-rate %). These encode the "fill every cell" instinct.

- **Journey-driven regression tiers (`SKILL.md:153-178`, `references/regression_testing.md`):** Smoke (2-4 P0 journeys, 15-30min) / Targeted (changed surface + 1 canary) / Full (all P0+P1, every persona) / Sanity (hotfix journey + 1 adjacent). Pass/fail framed by user impact (P0 goal reached, zero Blocks-Completion/Data-Loss open). The tier *concept* is dogfooding-friendly (cadence of re-walking journeys); the *report* is a coverage dashboard (per-tier pass-rate %).

- **Five-tier user-impact rubric (`SKILL.md:228-238`, `references/bug_report_templates.md` "Severity / Priority / Impact crosswalk"):** Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic → default Severity/Priority. Stated 2× in this skill AND canonically in `../qa-execution/references/bug-severity-by-user-impact.md`. Drift-prone triple statement.

- **Two-source-of-truth reference pattern:** 5 of 9 references (`cfr_test_cases.md`, `exploratory_charters.md`, `journey_test_plans.md`, `persona_test_cases.md`, `test_tours_catalog.md`) explicitly defer canonical definitions to `../qa-execution/references/*.md` and carry only a "planning view" here. Each says "read both." This is a deliberate anti-drift measure (don't duplicate canonical text), but it makes `qa-report` unable to stand alone and doubles the places QA truth lives.

- **Triple-stated bug template:** The canonical bug template appears (1) in `assets/issue-template.md` (78 lines), (2) inlined as the "Standard Bug Report" code block in `references/bug_report_templates.md`, and (3) inlined again in `references/figma_validation.md` ("Bug Report for UI Discrepancies"). Three drift surfaces for one template.

- **Interactive bash wizards (`scripts/create_bug_report.sh` 299 lines, `scripts/generate_test_cases.sh` 395 lines):** TTY `read -r` prompt loops that walk a human through filing a bug / writing a TC. Bug ID is `BUG-$(date +%Y%m%d%H%M%S)` (timestamp-based, so the same bug filed in two rounds gets two IDs — no dedup). TC ID is user-entered. Both scripts `mkdir -p` the output dir and write one file per artifact. Anachronistic for an agent-driven flow — an agent writes the file directly and does not need a prompt wizard.

- **Explicit out-of-scope routing (`SKILL.md:11-12`, `225`, `247`):** Technical integration / security / performance / API cases are routed away to code tests, SAST/DAST, load tools, and `agent-output-audit`. This is the skill's strongest real-user-QA signal and the cleanest part of the current design.

## Relevant Sources

- `skills/mine/qa-report/SKILL.md:1-18` — front matter / description / trigger / argument-hint (`[qa-output-path]`)
- `skills/mine/qa-report/SKILL.md:24-38` — Required Reading Router (task→file table, pairs in-skill refs with qa-execution canonicals)
- `skills/mine/qa-report/SKILL.md:40-50` — Reference Index (9 reference files summarized)
- `skills/mine/qa-report/SKILL.md:52-54` — Required Inputs (qa-output-path optional, defaults to CWD)
- `skills/mine/qa-report/SKILL.md:56-69` — Shared Output Structure (the mandated `<qa-output-path>/qa/` tree)
- `skills/mine/qa-report/SKILL.md:72-76` — Step 1: Resolve Output Directory (per-round mkdir)
- `skills/mine/qa-report/SKILL.md:82-91` — Step 2: deliverable parse table (full deliverable taxonomy + write paths)
- `skills/mine/qa-report/SKILL.md:93-119` — Step 3: Generate Test Plans (mandatory sections, entry/exit criteria)
- `skills/mine/qa-report/SKILL.md:121-151` — Step 4: Generate Test Cases (9-prefix ID scheme, required fields, Automation Metadata)
- `skills/mine/qa-report/SKILL.md:153-178` — Step 5: Build Regression Suites (Smoke/Targeted/Full/Sanity tiers, pass/fail by user impact)
- `skills/mine/qa-report/SKILL.md:180-189` — Step 6: Validate Against Figma (TC-UI-*, viewports 375/768/1280)
- `skills/mine/qa-report/SKILL.md:191-209` — Step 7: Create Bug Reports (BUG- IDs, required fields, scripts hook)
- `skills/mine/qa-report/SKILL.md:211-220` — Step 8: Validate Completeness (coverage-completeness enforcement — "every persona has at least one TC")
- `skills/mine/qa-report/SKILL.md:222-226` — Companion Skills (qa-execution / agent-output-audit / agent-browser handoff)
- `skills/mine/qa-report/SKILL.md:228-238` — Bug Severity vs User Impact (5-tier rubric restated)
- `skills/mine/qa-report/SKILL.md:240-247` — Error Handling (out-of-scope routing for TC-INT/SEC/PERF/API)
- `skills/mine/qa-report/assets/issue-template.md:1-78` — canonical bug-report template (BUG-* fields, Environment/Summary/Reproduction/Expected/Root cause/Fix/Verification/Impact/Related)
- `skills/mine/qa-report/references/bug_report_templates.md:1-261` — Standard / UI-Visual / User-Friction bug variants; removed Performance variant; rubric crosswalk restated
- `skills/mine/qa-report/references/cfr_test_cases.md:1-216` — TC-CFR-* template, 6 CFR categories, persona×CFR pairing, 6 worked examples
- `skills/mine/qa-report/references/exploratory_charters.md:1-112` — charter modes (Freestyle/Strategy-Based/Scenario-Based/Collaborative/Charter-With-Tour), CH-NN drafting checklist, 10 worked examples
- `skills/mine/qa-report/references/figma_validation.md:1-386` — Figma MCP workflow, discrepancy catalog, TC-UI template, inlined bug-report section (third copy of bug template)
- `skills/mine/qa-report/references/journey_test_plans.md:1-211` — TC-JOURNEY-* template, journey-driven test plan structure, entry/exit criteria, worked example (Mobile-first Checkout)
- `skills/mine/qa-report/references/persona_test_cases.md:1-156` — TC-PERSONA-* template, persona YAML schema, friction hypotheses, persona×surface coverage matrix, worked example
- `skills/mine/qa-report/references/regression_testing.md:1-420` — Smoke/Targeted/Full/Sanity tiers, journey prioritization by user impact, automation tagging, pass/fail/conditional criteria, regression execution report (coverage dashboard)
- `skills/mine/qa-report/references/test_case_templates.md:1-588` — Standard TC template + Automation Metadata + 9 variant templates (TC-FUNC/UI/REG/SMOKE/PERSONA/JOURNEY/CHARTER/TOUR/CFR); removed TC-INT/SEC/PERF/API
- `skills/mine/qa-report/references/test_tours_catalog.md:1-69` — tour selection matrix, one-tour-per-charter rule, persona×tour hints; defers canonical tour definitions to qa-execution
- `skills/mine/qa-report/scripts/create_bug_report.sh:1-299` — interactive bug wizard; `BUG_ID="BUG-$(date +%Y%m%d%H%M%S)"` at line 62 (timestamp ID, no dedup)
- `skills/mine/qa-report/scripts/generate_test_cases.sh:1-395` — interactive TC wizard; user-entered TC-ID; writes one `<TC_ID>.md` per case

## Transferable Patterns

- **Five-tier user-impact rubric → canonical docs/qa/severity.md** because it is already the cleanest "user-side honesty" model in the skill and is referenced from 3 places; promote it to ONE living doc and have bug_report_templates.md + SKILL.md point at it instead of restating it. Replaces the triple-stated crosswalk (`SKILL.md:228-238`, `references/bug_report_templates.md` crosswalk, `../qa-execution/references/bug-severity-by-user-impact.md`).
- **Charter as the atomic dogfooding unit → docs/qa/sessions/** because a charter (mission + persona + tour + time-box, `references/exploratory_charters.md`) IS a real-user session spec. Promote `TC-CHARTER-*` from a sub-type to the primary artifact; demote the other 8 TC-* prefixes to optional structured follow-ups filed *from* a session. This directly serves goal (1) — dogfooding, not case accumulation.
- **Persona × journey × tour assignment grid → docs/qa/matrix.md** because it is the right "which real user walks which journey under what conditions" model (`references/persona_test_cases.md:69`, `references/test_tours_catalog.md` pairing hints, `references/cfr_test_cases.md` persona×CFR table). It is dogfooding assignment, not test coverage — reframe the cells as "sessions to run this cycle" instead of "TCs to generate."
- **Regression tiers as re-dogfood cadence → docs/qa/cadence.md** because Smoke/Targeted/Full/Sanity (`references/regression_testing.md`) cleanly answer "how often do we re-walk each journey." Keep the cadence model; drop the per-tier pass-rate-% dashboard framing, which is coverage-matrix thinking.
- **CFR 6-category set as a dogfooder's "what to feel for" lens → docs/qa/lenses.md** because Usability/Accessibility/Perceived-Performance/Compatibility/Error-Recoverability/Production-Parity (`references/cfr_test_cases.md`) are exactly the qualities a real user *feels*. Keep as a checklist a dogfooder holds during a session; retire TC-CFR-* as a separate file type.
- **Tour catalog as dogfooding prompt set → docs/qa/tours.md** because the 10 tours (Feature/Money/Garbage/Back-Button/Multi-Tab/Network/Locale/Paste/Autofill/Interrupt) are high-quality "missions" for off-script exploration (`references/test_tours_catalog.md`). Keep as session prompts; the canonical definitions currently in qa-execution should fold into the same docs/qa/ file (resolves the two-source-of-truth split).
- **Entry/exit criteria + risk assessment → docs/qa/release-readiness.md** because the journey_test_plans structure (`references/journey_test_plans.md` "Journey-driven test plan structure") is a good "are we safe to ship" gate. Keep as a living release-readiness doc updated each cycle, not a per-round file.
- **Explicit out-of-scope routing → docs/qa/scope.md** because `SKILL.md:240-247` already cleanly routes technical integration/security/performance/API work away to code tests, SAST/DAST, load tools, and `agent-output-audit`. Keep this boundary statement verbatim in the centralized docs.

## Risks / Mismatches

- **`<qa-output-path>/qa/` per-round tree conflicts with "living repo docs".** `SKILL.md:56-69` + `72-76` mandate creating a fresh subtree each run; there is no append/update path. The redesign wants one canonical `docs/qa/` that accumulates. The skill provides zero primitives for the latter — this is a replace, not an evolve.
- **Timestamp-based BUG-ID + user-entered TC-ID conflict with "CSV state tracking".** `scripts/create_bug_report.sh:62` (`BUG-$(date +%Y%m%d%H%M%S)`) means the same bug filed across two rounds gets two IDs — no dedup, no stable key for a CSV row. The skill's per-file `Status: pending|resolved|invalid` is per-round-per-file, not a shared ledger. A CSV state tracker needs stable IDs and a single status column updated in place; the skill has neither.
- **9-prefix TC-* model + Step 8 completeness checks conflict with "dogfooding not test cases" (goal 1).** `SKILL.md:216-218` enforces "every persona/journey/CFR has at least one TC" — i.e., case accumulation as the success metric. A dogfooding model would enforce "every journey was walked by a real persona this cycle" (a session log). Keeping the TC-* file model as-is would re-import the coverage instinct the redesign is trying to shed.
- **Automation Metadata block on every case pulls toward technical coverage.** `SKILL.md:138-149` + `references/test_case_templates.md` "Automation Metadata" attach `Automation Target: E2E | Manual-only` / `Automation Status: Existing|Missing|Blocked` to every case. In a dogfooding model this belongs in a separate automation-backlog doc, not on every session note — otherwise the planner is constantly asked "should this be an E2E spec?" which is a technical concern.
- **Two-source-of-truth reference pattern conflicts with "centralize as living repo docs" (goal 2).** 5 references (`cfr_test_cases`, `exploratory_charters`, `journey_test_plans`, `persona_test_cases`, `test_tours_catalog`) defer canonical definitions to `../qa-execution/references/*.md`. This DOUBLES the places QA truth lives. The redesign wants ONE `docs/qa/`; the current split must be collapsed (move canonicals in, point both skills at the same files).
- **Triple-stated bug template is a drift surface.** `assets/issue-template.md`, `references/bug_report_templates.md` (Standard section), and `references/figma_validation.md` (UI Discrepancies section) each carry a full copy of the bug template. A living docs model needs exactly one template file referenced by the others; keeping three copies guarantees drift.
- **Interactive bash wizards assume a human TTY operator.** `scripts/create_bug_report.sh` (299 lines) and `scripts/generate_test_cases.sh` (395 lines) are `read -r` prompt loops. In an agent-driven dogfooding flow the agent writes files directly; the wizards are dead weight, and their timestamp-ID scheme actively blocks cross-round dedup.
- **Heavy read-before-write tax may survive the redesign poorly.** The Required Reading Router (`SKILL.md:24-38`) mandates reading 2-3 files in full before each deliverable. Fidelity-correct, but if the redesign centralizes into `docs/qa/`, the router must be re-pointed at the new paths or it will silently reference moved files.
- **"Production parity" CFR assumes an environment that may not exist.** `references/cfr_test_cases.md` TC-CFR-006 requires "real auth path, no local mocks, realistic extension set, Slow 3G." If the dogfooding model runs against a staging/preview env, this check's value depends on env parity the skill cannot itself guarantee — needs an environment contract elsewhere.

## Open Questions

- Does `qa-execution` (slice 02) own the canonical persona/journey/tour/cfr/bug-severity definitions today, and should those move into the new `docs/qa/` as the single source of truth? This skill currently treats `../qa-execution/references/*.md` as canonical for 5 of its 9 references — the redesign cannot collapse the two-source split without confirming where qa-execution points.
- Is there an existing `feature-status.csv` pattern elsewhere in the repo (the research prompt names it, plus "AGH QA folder sprawl" and "docs/_memory specs about QA dogfooding" — those are other slices)? This skill has NO csv/state-tracking today; the redesign's CSV model must be imported from elsewhere, not evolved from here.
- Should the charter/session replace TC-* as the atomic artifact, and what happens to the 9 TC-* prefixes — retired, or kept as optional structured follow-ups filed *from* a session? The skill currently makes TC-* primary and charters a planning sub-type; the redesign's dogfooding goal suggests inverting that, but the inversion is a design decision the parent must make.
- Where does the Automation Metadata block live in the new model — on each session note, in a separate automation-backlog doc, or retired entirely? This skill attaches it to every TC; the redesign needs to decide whether "should this be an E2E spec" is even a planning-time question.
- Does `agent-output-audit` (named as the companion for CI gate / AI-test-hygiene at `SKILL.md:225`) overlap with the redesigned dogfooding model, or is it cleanly separable? This skill defers AI-implementation-audit work to it; the redesign should confirm that boundary still holds.
- What env-parity contract does the redesigned dogfooding model assume (production vs staging vs preview)? `references/cfr_test_cases.md` TC-CFR-006 (Production-Parity) and `references/journey_test_plans.md` entry criteria both assume "production-parity environment" — the centralized docs need an environment contract that may live outside QA.

## Evidence

- `skills/mine/qa-report/SKILL.md`
- `skills/mine/qa-report/assets/issue-template.md`
- `skills/mine/qa-report/references/bug_report_templates.md`
- `skills/mine/qa-report/references/cfr_test_cases.md`
- `skills/mine/qa-report/references/exploratory_charters.md`
- `skills/mine/qa-report/references/figma_validation.md`
- `skills/mine/qa-report/references/journey_test_plans.md`
- `skills/mine/qa-report/references/persona_test_cases.md`
- `skills/mine/qa-report/references/regression_testing.md`
- `skills/mine/qa-report/references/test_case_templates.md`
- `skills/mine/qa-report/references/test_tours_catalog.md`
- `skills/mine/qa-report/scripts/create_bug_report.sh`
- `skills/mine/qa-report/scripts/generate_test_cases.sh`
- `dev/compozy/agh/.agents/skills/qa-report/` (deployed copy — verified byte-for-byte identical to source via `diff -r` exit 0 and matching SHA-1 checksums on all 13 files; no content divergence)
