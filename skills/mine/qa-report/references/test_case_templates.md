# Test Case Templates

Standard templates for real-user QA test cases. Variants are framed around what the user is doing, not what the technology is doing.

## Contents

- Standard Test Case Template (header, persona, real-user conditions, steps, edge cases)
- Automation Metadata block (parsed by `qa-execution`)
- Functional Test Case Template (TC-FUNC-*)
- UI/Visual Test Case Template (TC-UI-*)
- Regression Test Case Template (TC-REG-*)
- Smoke Test Case Template (SMOKE-*)
- Persona Test Case Template (TC-PERSONA-*)
- Journey Test Case Template (TC-JOURNEY-*)
- Charter Test Case Template (TC-CHARTER-*)
- Tour Test Case Template (TC-TOUR-*)
- CFR Test Case Template (TC-CFR-*)

> Removed deliberately: TC-INT (integration), TC-SEC (security), TC-PERF (performance), TC-API. Those belong to integration tests in code, SAST/DAST tooling, and load-testing tools. See SKILL.md Error Handling for routing.

---

## Standard Test Case Template

```markdown
## TC-[ID]: [Test Case Title]

**Priority:** P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)
**Type:** Functional | UI | Regression | Smoke | Persona | Journey | Charter | Tour | CFR
**Status:** Not Run | Pass | Fail | Blocked | Skipped
**Estimated Time:** X minutes
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Persona:** New User | Power User | Casual User | Mobile User | Accessibility-Reliant | Recovering User
**Journey:** <J-NN journey name, or "n/a">
**Automation Target:** E2E | Manual-only
**Automation Status:** Existing | Missing | Blocked | N/A
**Automation Command/Spec:** [spec path, suite name, or command]
**Automation Notes:** [why this should be automated, remain manual, or is blocked]

---

### Objective

[Clear statement of what this test validates from the user's perspective and why it matters to them]

---

### Preconditions

- [ ] [Setup requirement 1]
- [ ] [Setup requirement 2]
- [ ] [Test data/accounts needed]
- [ ] [Environment configuration]

---

### Real-User Conditions

| Dimension | Value |
|-----------|-------|
| Network | wifi-fast \| wifi-slow \| 4g \| 3g \| flaky |
| Device | desktop \| laptop \| tablet \| phone-small \| phone-large |
| Browser | <Chrome / Safari / Firefox / iOS Safari / Android Chrome> |
| Locale | en-US \| pt-BR \| de-DE \| ar-EG \| ja-JP \| ... |
| Timezone | <IANA tz, e.g. America/New_York> |
| Autofill | empty \| stale-credentials \| current-credentials \| saved-card |
| Modality | mouse-keyboard \| touch \| screen-reader \| keyboard-only \| voice |

---

### Test Steps

1. **[User action in plain language]**
   - Input: [specific data if any]
   - **Expected:** [What the user should observe within their patience window]

2. **[User action in plain language]**
   - Input: [specific data if any]
   - **Expected:** [What the user should observe]

3. **[User action in plain language]**
   - Input: [specific data if any]
   - **Expected:** [Goal observable or next-step affordance]

---

### Edge Cases & Variations

(Pick from `../qa-execution/references/user-edge-cases.md` — non-technical edges only)

| Variation | Action | Expected Result |
|-----------|--------|-----------------|
| Refresh mid-submit | Click submit, refresh before response | No double-submit; clear feedback |
| Back after success | Press back from success screen | Sensible state; no re-fire |
| Slow 3G | Throttle to 3G, repeat steps | All actions feel responsive within targets |

---

### Post-conditions

- [System state after successful test]
- [Cleanup required]
- [Data to verify/restore]

---

### Related Test Cases

- TC-XXX: [Related scenario]
- TC-YYY: [Prerequisite test]

---

### Execution History

| Date | Tester | Build | Result | Bug ID | Notes |
|------|--------|-------|--------|--------|-------|
| | | | | | |

---

### Notes

[Additional context, known issues, or considerations]
```

---

## Automation Metadata

Apply these fields to every test case variant:

- **Automation Target**
  - `E2E` — public flow through browser, HTTP, CLI, or worker entrypoints; user-observable behavior.
  - `Manual-only` — exploratory, usability, visual-judgment, or accessibility-via-real-AT work that should stay manual.
- **Automation Status**
  - `Existing` — matching automated coverage already exists.
  - `Missing` — repository supports automation for this flow but coverage is absent.
  - `Blocked` — harness exists but credentials, data, or environment block automation.
  - `N/A` — automation is intentionally not applicable.
- **Automation Command/Spec:** existing spec path or canonical command when known.
- **Automation Notes:** rationale, blocker, or handoff expectation for `qa-execution`.

---

## Functional Test Case Template (TC-FUNC-*)

```markdown
## TC-FUNC-[ID]: [Feature] - [Scenario]

**Priority:** P[0-3]
**Type:** Functional
**Persona:** [pick one]
**Module:** [Feature/Module name]
**Journey:** [J-NN journey name or "n/a"]
**Automation Target:** E2E | Manual-only
**Automation Status:** Existing | Missing | Blocked | N/A
**Automation Command/Spec:** [spec path or command]
**Automation Notes:** [why this case should or should not be automated]

### Objective
From the [persona]'s perspective, verify [feature] behaves correctly when [scenario].

### Preconditions
- User logged in as [persona]
- [Feature prerequisite]
- Test data: [dataset]

### Real-User Conditions
| Dimension | Value |
|-----------|-------|
| Device | [device profile] |
| Network | [network profile] |
| Locale | [locale] |

### Test Steps

1. Navigate to [page/feature]
   **Expected:** [what the persona sees]

2. Perform [user-language action]
   **Input:** [test data]
   **Expected:** [user-observable outcome]

3. Verify [user-observable result]
   **Expected:** [goal observable]

### Boundary User Behaviors
- Empty input: [test]
- Maximum input length: [test]
- Special characters from paste: [test]

### Negative User Behaviors
- Invalid input the user might paste: [test]
- Attempt action without preconditions: [test]
- Submit while missing required fields: [test]
```

---

## UI/Visual Test Case Template (TC-UI-*)

```markdown
## TC-UI-[ID]: [Component/Page] Visual Validation

**Priority:** P[0-3]
**Type:** UI/Visual
**Persona:** [pick one — usually Mobile User or Accessibility-Reliant for visual checks]
**Figma Design:** [URL]
**Breakpoints:** Desktop | Tablet | Mobile
**Automation Target:** E2E | Manual-only
**Automation Status:** Existing | Missing | Blocked | N/A

### Objective
Verify [component] matches Figma design specifications across viewports.

### Preconditions
- Browser: [Chrome/Firefox/Safari]
- Screen resolution: [specified]
- Theme: [Light/Dark]

### Visual Specifications

**Layout:**
| Property | Expected | Actual | Status |
|----------|----------|--------|--------|
| Width | XXXpx | | [ ] |
| Height | XXXpx | | [ ] |
| Padding | XX XX XX XX | | [ ] |
| Margin | XX XX XX XX | | [ ] |

**Typography:**
| Property | Expected | Actual | Status |
|----------|----------|--------|--------|
| Font | [Family] | | [ ] |
| Size | XXpx | | [ ] |
| Weight | XXX | | [ ] |
| Line-height | XXpx | | [ ] |
| Color | #XXXXXX | | [ ] |

**Colors:**
| Element | Expected | Actual | Status |
|---------|----------|--------|--------|
| Background | #XXXXXX | | [ ] |
| Border | #XXXXXX | | [ ] |
| Text | #XXXXXX | | [ ] |

**Interactive States:**
- [ ] Default state matches design
- [ ] Hover state matches design
- [ ] Active/pressed state matches design
- [ ] Focus state matches design (focus indicator visible)
- [ ] Disabled state matches design

### Responsive Checks

**Desktop (1280px):**
- [ ] Layout correct
- [ ] All elements visible

**Tablet (768px):**
- [ ] Layout adapts correctly
- [ ] Touch targets adequate

**Mobile (375px):**
- [ ] Layout stacks correctly
- [ ] Content readable
- [ ] Navigation accessible
- [ ] No content covered by sticky elements
```

---

## Regression Test Case Template (TC-REG-*)

```markdown
## TC-REG-[ID]: [Journey] Regression

**Priority:** P[0-3]
**Type:** Regression
**Persona:** [pick one]
**Journey:** [J-NN name — regression is journey-driven]
**Last Modified:** [Date]
**Automation Target:** E2E | Manual-only
**Automation Status:** Existing | Missing | Blocked | N/A

### Objective
Verify [journey] still reaches its goal observable after recent changes.

### Context
Recent changes that may affect this journey:
- [Change 1]
- [Change 2]

### Critical Path (user-language)

1. [ ] Entry point still reachable
2. [ ] Each step delivers its expected observable
3. [ ] Goal observable still appears
4. [ ] Exit path still natural
5. [ ] At least one abandonment path tested

### Cross-Journey Touchpoints
- [ ] [Dependent journey 1] still works
- [ ] [Dependent journey 2] still works

### Perceived Performance Baseline
- Expected entry-to-goal time: < Xs
- Expected per-step feedback: < 100ms
```

---

## Smoke Test Case Template (SMOKE-*)

```markdown
## SMOKE-[ID]: [Critical Journey] Sanity

**Priority:** P0
**Type:** Smoke
**Persona:** [the most representative persona for this journey]
**Journey:** [J-NN name]
**Automation Target:** E2E | Manual-only

### Objective
A 2-minute sanity check that the [journey] is not catastrophically broken on this build.

### Steps (target: 2 minutes total)

1. [Entry verb] — reach the journey entry within 5 seconds
2. [Mid-flow verb] — see the expected mid-flow observable within 3 seconds
3. [Goal verb] — see the goal observable within journey time budget

### Pass criteria
- All three steps deliver their observable without `Blocks-Completion`-class issues.
```

---

## Persona Test Case Template (TC-PERSONA-*)

```markdown
## TC-PERSONA-[ID]: [Persona] on [Surface]

**Priority:** P[0-3]
**Type:** Persona
**Persona:** [pick one — TC-PERSONA cases are about validating a specific persona's experience]
**Surface:** [feature or screen]
**Automation Target:** Manual-only (persona-driven cases rarely automate well)
**Automation Status:** N/A

### Persona Attributes (record exactly)

| Attribute | Value |
|-----------|-------|
| Name | New User | Power User | Casual User | Mobile User | Accessibility-Reliant | Recovering User |
| Familiarity | zero | familiar | expert |
| Motivation | evaluate | complete-task | ship-work-fast | one-handed-action | use-on-equal-terms | trust-check |
| Device | [device] |
| Network | [profile] |
| Modality | [interaction modality] |
| Locale | [locale] |
| Patience (seconds) | [time until abandonment] |

### Objective
Verify that a [persona] can [user goal] on [surface] within the persona's patience window.

### Friction Hypotheses (what to look for)

1. [Specific friction the persona is likely to hit]
2. [Specific friction the persona is likely to hit]
3. [Specific friction the persona is likely to hit]

### Test Steps

1. **Enter as [persona] would** — [entry method]
   **Expected:** [first-impression observable within X seconds]

2. **Attempt [persona's primary action]**
   **Expected:** [persona-appropriate feedback within their patience]

3. **Encounter the planned friction hypothesis**
   **Expected:** [graceful handling that keeps the persona moving]

### Pass criteria
- The persona reaches their goal without `Blocks-Completion`-class friction.
- No `Trust-Damage`-class observation surfaces.
```

---

## Journey Test Case Template (TC-JOURNEY-*)

```markdown
## TC-JOURNEY-[ID]: [Verb-Noun Journey Name]

**Priority:** P[0-3]
**Type:** Journey
**Persona:** [pick one]
**Journey:** J-[NN] [from `../qa-execution/references/journey-maps.md`]
**Automation Target:** E2E (when harness exists)
**Automation Status:** Existing | Missing | Blocked | N/A

### Journey Value
[One sentence: what does the user gain when this journey succeeds?]

### Entry
- URL: [entry URL]
- Origin: direct | email | search | in-app-nav | push | external-share

### Actions (user-language)

| Step | Verb | Expected observable | Time budget (s) |
|------|------|---------------------|-----------------|
| 1 | [enter] | [observable] | [N] |
| 2 | [act] | [observable] | [N] |
| 3 | [confirm] | [observable] | [N] |
| 4 | [reach goal] | [goal observable] | [N] |

### Goal
- Observable: [the exact user-side state that proves success]
- Side effects: [email-sent, db-row-created, analytics-event-fired]

### Exit
- Natural: [where the user lands after success]
- Abandonment paths to test:
  - Path A: [realistic abandonment 1]
  - Path B: [realistic abandonment 2]

### Branches
- At step [N]: when [condition], the user can [alternative]

### Cross-feature
- Teams crossed: [team-1, team-2]
- Services crossed: [service-1, service-2]
- External dependencies: [provider-1]

### Failure Modes (journey-level, not feature-level)
- [What breaks the whole journey, not just a feature]
```

---

## Charter Test Case Template (TC-CHARTER-*)

```markdown
## TC-CHARTER-[ID]: [Mission in one sentence]

**Priority:** P[0-3]
**Type:** Charter
**Mode:** Freestyle | Strategy-Based | Scenario-Based | Collaborative | Charter-With-Tour
**Persona:** [pick one]
**Surface:** [feature/area]
**Entry URL:** [URL]
**Tour:** [pick exactly one from `../qa-execution/references/test-tours.md`]
**Time-box:** 30 | 60 | 90 minutes
**Automation Target:** Manual-only
**Automation Status:** N/A

### Mission
[One-sentence mission statement — what we're looking for and why it matters]

### Out of scope
[Surfaces or behaviors deliberately excluded so the tester doesn't drift]

### Must try
- [Specific thing the tester must attempt]
- [Specific thing the tester must attempt]

### Must avoid
- [Known-broken or out-of-scope area to skip]

### Debrief template (filled by qa-execution at session end)
- Started: <ISO>
- Ended: <ISO>
- Findings:
  - <bullet>
- Bugs filed: [BUG-NNN]
- Surprises: <what was unexpected>
- Suggested next charter: <one-line proposal>
```

---

## Tour Test Case Template (TC-TOUR-*)

```markdown
## TC-TOUR-[ID]: [Tour Name] on [Surface]

**Priority:** P[0-3]
**Type:** Tour
**Tour:** Feature | Money | Garbage | Back-Button | Multi-Tab | Network | Locale | Paste | Autofill | Interrupt
**Persona:** [pick one]
**Surface:** [feature/area]
**Time-box:** 30 | 60 | 90 minutes
**Automation Target:** Manual-only
**Automation Status:** N/A

### Theme (from tour catalog)
[Copy the tour's theme statement from `../qa-execution/references/test-tours.md`]

### Off-script actions to attempt
[Copy the tour's bullet list from the canonical catalog]

### What to look for
[Copy the tour's "what to look for" from the canonical catalog]

### Sample evidence to capture
[Copy the tour's "sample evidence" from the canonical catalog]

### Pass criteria
- All planned off-script actions attempted.
- Findings documented in the charter debrief or as bugs.
- No `Blocks-Completion` or `Data-Loss` left unfiled.
```

---

## CFR Test Case Template (TC-CFR-*)

```markdown
## TC-CFR-[ID]: [CFR Category] on [Surface]

**Priority:** P[0-3]
**Type:** CFR
**CFR Category:** Usability | Accessibility | Perceived-Performance | Compatibility | Error-Recoverability | Production-Parity
**Persona:** [pick one — Accessibility-Reliant for a11y, Mobile User for perceived-perf on touch, etc.]
**Surface:** [feature/area]
**Automation Target:** Manual-only (most CFR checks resist automation)
**Automation Status:** N/A

### Objective
Verify that [CFR category] holds on [surface] for [persona] within the targets defined in `../qa-execution/references/cfr-checks.md`.

### Checklist (from cfr-checks.md)
- [ ] [Item 1 from the relevant CFR section]
- [ ] [Item 2]
- [ ] [Item 3]

### Targets
| Observable | Target | Acceptable | Actual |
|---|---|---|---|
| [metric] | [target] | [acceptable] | |

### Pass criteria
- All checklist items mark `pass`.
- No `Friction`-class or higher CFR finding surfaces.
- Production-parity items confirmed (not in incognito, cookies enabled, realistic auth path).
```

---

## Quick Reference: Test Case Naming

| Type | Prefix | Example |
|------|--------|---------|
| Functional | TC-FUNC- | TC-FUNC-001 |
| UI/Visual | TC-UI- | TC-UI-045 |
| Regression (journey-driven) | TC-REG- | TC-REG-089 |
| Smoke | SMOKE- | SMOKE-001 |
| Persona-driven | TC-PERSONA- | TC-PERSONA-012 |
| Journey-driven | TC-JOURNEY- | TC-JOURNEY-007 |
| Charter (planning) | TC-CHARTER- | TC-CHARTER-003 |
| Tour-driven | TC-TOUR- | TC-TOUR-014 |
| CFR | TC-CFR- | TC-CFR-008 |

---

## Automation Status Reference

| Status | Meaning | Action |
|--------|---------|--------|
| Existing | Coverage already exists | Reuse and verify it still maps to the journey |
| Missing | Harness exists but coverage does not | `qa-execution` should add or update it |
| Blocked | Harness exists but prerequisites are missing | Report the blocker explicitly |
| N/A | Automation is intentionally not applicable | Keep strong manual evidence |

---

## Priority Definitions

| Priority | Description | When to Run |
|----------|-------------|-------------|
| P0 | Critical journeys; failure causes Blocks-Completion / Data-Loss | Every build |
| P1 | Major journeys; failure causes Trust-Damage / repeated Friction | Daily/Weekly |
| P2 | Secondary journeys, edge personas, lower-traffic surfaces | Weekly/Release |
| P3 | Cosmetic checks, exploratory follow-ups | Release only |
