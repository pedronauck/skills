# Add Explicit E2E Coverage Enforcement to QA Skills

## Summary
- Make `qa-execution` the enforcement point for automated E2E regression coverage, using a balanced policy: when the repository already supports E2E, require new or updated E2E coverage for changed P0/P1 flows and critical regressions; when support does not exist, record the blocker and keep manual evidence explicit.
- Make `qa-report` annotate test plans and test cases with automation intent so `qa-execution` does not need to infer which flows should become automated.
- Keep the main `SKILL.md` files lean and move detailed detection and enforcement rules into references, following `skill-best-practices`.

## Key Changes
- **`qa-execution`**
  - Extend repository contract discovery to surface a dedicated E2E capability object instead of hiding `test:e2e` inside generic test commands.
  - Add an explicit step that classifies each changed or regression-critical flow as `existing-e2e`, `needs-e2e`, `manual-only`, or `blocked`.
  - Require adding or updating E2E coverage when the repo already has a usable harness and the flow is P0/P1, browser-critical, or a reproduced regression.
  - Re-run the narrow E2E spec plus the canonical E2E command after fixes, and include that evidence in the final verification gate.
  - Add a focused reference for E2E support detection and enforcement rules; update the checklist and verification report template to make this mandatory and auditable.
- **`qa-report`**
  - Update test plan generation to include an **Automation Strategy** section that lists which flows are expected to become E2E, which stay manual-only, and which are blocked by environment gaps.
  - Update test case guidance and templates to add explicit automation metadata:
    - `Automation Target:` `E2E | Integration | Manual-only`
    - `Automation Status:` `Existing | Missing | Blocked | N/A`
    - `Automation Command/Spec:` existing spec path or command, when known
    - `Automation Notes:` rationale or blocker
  - Update regression suite guidance so P0/P1 and bug-driven regression cases are marked as automation candidates, not just manual execution items.
  - Keep `qa-report` as a planning and documentation skill; it should not generate E2E code, only the coverage expectation.
- **Shared artifacts and helper flows**
  - Update the shared issue template used by both skills to record `Automation Follow-up` (`Added`, `Pending`, `Blocked`) plus the related spec or command when applicable.
  - Update the interactive helper scripts so generated test cases and bug reports prompt for the new automation fields instead of producing stale artifacts.
  - Refresh skill descriptions to mention the new automation behavior, then re-run the metadata validator from `skill-best-practices`.

## Public Interface / Artifact Changes
- The discovery script output gains a dedicated E2E section with at least: support detected, framework or tooling signal, canonical commands, and detection reason.
- Verification reports gain an **Automated Coverage** section with: support detected, required flows, specs added or updated, commands rerun, and manual-only or blocked items.
- Test plans and TC files gain automation annotations that `qa-execution` can read directly.
- “E2E” should be treated as public-interface regression coverage across browser, HTTP, or CLI flows, not browser-only.

## Test Plan
- Validate updated metadata for both skills with the existing validation script.
- Verify both `SKILL.md` files stay under the 500-line guideline and keep all paths relative.
- Run shell syntax checks for the updated helper scripts.
- Review four representative scenarios end to end:
  - repo with existing Playwright or Cypress support and changed critical flow
  - repo with Web UI but no E2E harness
  - API or CLI-only repo with public end-to-end commands
  - bug discovered during QA that now requires automation follow-up in the issue and verification report

## Assumptions and Defaults
- Default policy is balanced, not strict release-blocking for every flow.
- The skills should not bootstrap a brand-new E2E framework when the repository lacks one; they should document the gap and keep manual QA evidence explicit.
- Manual and browser QA remains part of the process even when E2E exists; automated coverage supplements final proof, it does not replace live validation.
- `qa-report` should annotate cases rather than introducing a separate standalone automation artifact unless later usage shows the annotations are insufficient.
