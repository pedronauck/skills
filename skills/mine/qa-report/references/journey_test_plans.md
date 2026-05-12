# Journey Test Plans — Planning Reference

This file is the planning view of journey-driven QA. The canonical journey anatomy and high-value-journey selection criteria live in `../qa-execution/references/journey-maps.md`. Read both files before writing a TC-JOURNEY-* or a journey-driven test plan.

## Contents

- What a journey test plan is
- Why journey-driven planning beats feature-driven planning
- TC-JOURNEY-* template
- Journey-driven test plan structure (Executive Summary, Personas Covered, Journeys Mapped, Charters Planned, CFR Scope, Test Strategy, Automation Strategy, Entry/Exit Criteria, Retesting vs Regression, Risk Assessment)
- Worked example (Mobile-first Checkout Redesign)
- Anti-patterns
- Sources

## What a journey test plan is

A journey test plan is the **plan document** for exercising one or more user journeys end-to-end. It is the unit of release-candidate QA that product owners can read and understand. A test plan that lists 200 individual TC-FUNC-* cases does not answer the question *"are we ready to ship?"* — a plan organized around 5-7 journeys does.

## Why journey-driven planning beats feature-driven planning

- **Features pass; journeys fail.** A feature can work in isolation while the journey it lives in is broken at a seam.
- **Product owners read journeys.** A plan in journey language is reviewable by non-engineering stakeholders.
- **Personas live in journeys.** A journey + persona × tour gives you the assignment grid; a feature × persona gives you nothing actionable.
- **Regression risk lives in journeys.** Most release-blocking bugs are journey-level: cart resets, auth handoff failures, multi-tab corruption, locale-specific layout breaks.

## TC-JOURNEY-* template

See `test_case_templates.md` for the full template. The mandatory sections are:

1. **Journey Value** — one sentence: what does the user gain when this journey succeeds?
2. **Entry** — URL + origin (direct / email / search / in-app-nav / push / external-share).
3. **Actions** — user-language verbs with expected observable and time budget per step.
4. **Goal** — exact user-side state that proves success + system-side side effects.
5. **Exit** — natural exit + abandonment paths to test.
6. **Branches** — conditional alternatives at each step.
7. **Cross-feature** — teams, services, external dependencies the journey crosses.
8. **Failure Modes** — journey-level failure modes (not feature-level).

## Journey-driven test plan structure

For the test plan document itself (not the individual TC-JOURNEY-*), write:

```markdown
# Journey Test Plan: <Release / Feature / Initiative>

## Executive Summary

- **User value delivered:** [one paragraph in user language]
- **Personas affected:** [list]
- **Journeys exercised:** [count]
- **Highest user-impact risk:** [one sentence on what could go wrong for users]

## Personas Covered

For each persona, list:
- Why this persona is relevant to this change
- How many TC-PERSONA-* / TC-JOURNEY-* cover it
- Any persona that is intentionally **not** covered (with reasoning)

## Journeys Mapped

For each J-NN:
- One-sentence value statement
- Persona assigned (primary + secondary)
- Charter(s) planned: CH-NN
- TC-JOURNEY-* cases: TC-JOURNEY-NN
- Cross-feature touchpoints
- Abandonment paths to cover

## Charters Planned

For each CH-NN:
- Mission
- Persona × Tour × Time-box
- Surface
- Out-of-scope

## CFR Scope

For each CFR category, declare:
- Affected by this change? (yes / no — and why)
- TC-CFR-* generated? (list)

## Test Strategy

- How will the journeys be exercised? (qa-execution → agent-browser? manual?)
- Where do mocks stop and real integrations start?
- Who runs which charters (when multi-tester)?

## Automation Strategy

Tag each journey × persona combination:
- `E2E candidate` — repo has harness, journey is P0/P1 public.
- `Manual-only` — exploratory, visual, accessibility-AT-driven.
- `Blocked` — harness exists but env/data/credentials missing.

## Entry Criteria (all must hold)

- [ ] Build is reachable in a production-parity environment
- [ ] CI gate has run separately and is green (`agent-output-audit` ran or CI is green)
- [ ] Test data and fixture state matches journey preconditions
- [ ] Personas, journeys, and charters are documented
- [ ] Browser tooling (`agent-browser`) is available when Web UI is in scope

## Exit Criteria (all must hold)

- [ ] Every P0 journey reached its goal observable
- [ ] Zero open `Blocks-Completion` or `Data-Loss` bugs on P0 journeys
- [ ] CFR pass completed on at least 2 journeys with no critical findings open
- [ ] Automation follow-up registered for every `Missing` or `Blocked` annotation
- [ ] Verification report filed at `<qa-output-path>/qa/verification-report.md`

## Retesting vs Regression

- **Retesting** — re-validates the fix of a specific reported defect. Scope: BUG and its narrow reproduction.
- **Regression** — validates that the change did not break unrelated journeys. Scope: the journey-driven suite (`regression_testing.md`).

State explicitly which mode applies to each suite execution.

## Risk Assessment

| Risk | Probability | User Impact | Mitigation |
|------|-------------|-------------|------------|
| <journey-level risk> | low/med/high | Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic | <mitigation> |

## Timeline and Deliverables

- Charters drafted by: <date>
- TC-* generated by: <date>
- Execution window: <date range>
- Verification report due: <date>
```

## Worked example

```markdown
# Journey Test Plan: Mobile-first Checkout Redesign

## Executive Summary

- **User value delivered:** First-time mobile shoppers can complete checkout in under 90 seconds without leaving the funnel for help.
- **Personas affected:** New User, Mobile User, Casual User, Recovering User.
- **Journeys exercised:** 5.
- **Highest user-impact risk:** A regression in cart persistence on mobile Safari could lose orders silently (`Data-Loss`).

## Personas Covered

- **New User** (primary on this change) — 4 TC-PERSONA-* + 2 TC-JOURNEY-*
- **Mobile User** (primary on this change) — 5 TC-PERSONA-* + 3 TC-JOURNEY-*
- **Casual User** (returning mobile) — 2 TC-JOURNEY-*
- **Recovering User** (came back after a previous abandoned cart) — 1 TC-JOURNEY-*
- **Power User** — NOT covered (Power Users rarely use this surface; documented in Risk Assessment)
- **Accessibility-Reliant** — 1 TC-PERSONA-* + 1 TC-CFR-* (a11y category)

## Journeys Mapped

- J-01: Complete first purchase on mobile (New User, phone-small, 4G)
  - Charters: CH-01, CH-02
  - TC-JOURNEY-: TC-JOURNEY-007
  - Cross-feature: cart → checkout → payment → confirmation
  - Abandonment: surprise shipping cost (J-01a), payment fail (J-01b), tab-close (J-01c)
- J-02: Resume abandoned cart 3 days later (Casual User, phone-large)
  - ...
- J-03: Recovery after failed payment (Recovering User)
  - ...
- J-04: Apple Pay express checkout (Power User, mobile)
  - ...
- J-05: Screen-reader checkout (Accessibility-Reliant)
  - ...

## Charters Planned

- CH-01: New User × Feature Tour × 60min on /signup→/cart→/checkout
- CH-02: Mobile User × Network Tour × 60min on the same flow with 3G + flaky
- CH-03: Power User × Money Tour × 60min on Apple Pay
- CH-04: Accessibility-Reliant × Locale Tour × 60min in pt-BR with VoiceOver

## CFR Scope

- Usability: yes — TC-CFR-001 (Nielsen short list on checkout)
- Accessibility: yes — TC-CFR-002 (WCAG AA quick check)
- Perceived performance: yes — TC-CFR-003 (TTI / spinner / button feedback)
- Compatibility: yes — TC-CFR-004 (iOS Safari + Android Chrome)
- Error recoverability: yes — TC-CFR-005 (payment failure → retry)
- Production parity: yes — explicitly tested with real auth and cookies

## Risk Assessment

| Risk | Probability | User Impact | Mitigation |
|------|-------------|-------------|------------|
| Cart resets on tab close (mobile Safari) | high | Data-Loss | J-01c abandonment path exercises this |
| Payment double-charge under flaky network | med | Trust-Damage + financial | CH-02 Network Tour + J-01b |
| Apple Pay sheet height obscures total | low | Trust-Damage | CH-03 Money Tour |
| VoiceOver doesn't announce step transitions | med | Blocks-Completion (a11y) | CH-04 + TC-CFR-002 |
| Power User experience not covered | low | Friction | Documented; intentional scope cut |
```

## Anti-patterns

- **Feature-named journeys** — *"Settings page test"* is a feature test mislabeled. Rename to the value: *"Update notification preferences and confirm they arrive"*.
- **No abandonment paths** — a journey plan without abort paths cannot find the bugs that matter most (silent loss, ghost state, broken recovery).
- **Goal = "click submit"** — the goal is the user-side observable, not the action. Re-write until the goal is something the user wanted.
- **Single-persona-per-journey** — most journeys have a primary AND secondary persona; missing one halves the coverage.
- **No risk assessment** — without naming the user-impact risks, the test plan is unreviewable.

## Sources

- `../qa-execution/references/journey-maps.md` — canonical journey anatomy (this file's source of truth).
- Martin Fowler — *The Practical Test Pyramid*: high-value user journeys as the unit of E2E coverage.
- Incredibuild — *A Comprehensive Guide to E2E Testing*: journey-driven E2E catches cross-feature regressions.
- TestCollab — *Software Testing Strategies for QA Teams in 2026*: black-box behavioral testing maps to journeys.
