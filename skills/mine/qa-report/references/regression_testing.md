# Journey-Driven Regression Testing

This file defines the regression suite structure for real-user QA. Suites are organized around **user journeys**, not around test cases. Each tier picks N journeys; the test cases are derived from those journeys.

When executing regression suites against a live build, use the `qa-execution` companion skill — it follows the same execution order and priority scheme.

## Contents

- What is journey-driven regression?
- Regression Suite Tiers (Smoke / Targeted / Full / Sanity)
- Building a Regression Suite (high-value journey selection, prioritization, automation tagging)
- Execution Strategy (order, pass/fail/conditional criteria)
- Regression Test Management (maintenance, automation considerations)
- Regression Test Execution Report (user-impact framing)

---

## What is journey-driven regression?

**Definition:** Re-validating that high-value user journeys still reach their goal observable after code changes. Not "did the test pass?" but "would a real user, walking this journey today, end up where they wanted to go?"

**When to run:**
- Before every release.
- After bug fixes that touched journey-relevant code.
- After new features that added or modified journeys.
- After refactoring that crossed journey boundaries.
- Weekly / nightly for the Smoke tier.

---

## Regression Suite Tiers

### Smoke Suite (15-30 min)

**Purpose:** Quick sanity check that the build hasn't broken its most critical journeys.

**When:** Daily, on every build, before detailed testing.

**Journey count:** 2-4 P0 journeys.

**Coverage:**
- Authentication / signup entry
- The product's primary value-delivering journey (the "verb" — search, send, post, buy, save)
- Recovery from one common failure path
- Build stability (does it deploy at all)

**Example Smoke Suite (e-commerce):**

```
SMOKE-J01: Sign in and reach dashboard
SMOKE-J02: Complete a purchase (happy path)
SMOKE-J03: Recover from a declining card and complete purchase
SMOKE-J04: Sign out and re-sign-in (session persistence)
```

### Targeted Suite (30-60 min)

**Purpose:** Validate the journeys touching the changed surface.

**When:** Per change / per PR / per release-candidate.

**Journey count:** Every journey that touches the change, plus one regression-critical journey **not** touching the change (canary).

**Coverage:**
- Modified surfaces (every journey the change touches)
- Cross-feature journeys with touchpoints near the change
- One unrelated P0 journey as canary

### Full Regression Suite (2-4 hours)

**Purpose:** Comprehensive journey coverage before a release.

**When:** Weekly / before release.

**Journey count:** All P0 + P1 journeys, every persona at least once.

**Coverage:**
- All P0 journeys with primary persona
- All P1 journeys with at least one persona
- All cross-feature journeys
- All CFR categories the release affects (TC-CFR-* execution)
- At least one charter per major surface

### Sanity Suite (10-15 min)

**Purpose:** Post-hotfix validation.

**When:** Immediately after deploying a hotfix.

**Journey count:** The single journey affected by the hotfix, plus the journey adjacent to it.

**Coverage:**
- The journey the hotfix targets — happy path AND the abort path the bug was on.
- One adjacent journey to verify the fix didn't introduce a side effect.

---

## Building a Regression Suite

### Step 1: Identify High-Value Journeys

**Questions** (from `../qa-execution/references/journey-maps.md`):

- What generates revenue? (Checkout, subscription, refund.)
- What handles sensitive data? (Auth, settings, account deletion.)
- What's used most frequently? (Product's "verb".)
- What's the first impression? (Onboarding.)
- What's the recovery path? (Failed payment, session expiry, 5xx recovery.)

**Example High-Value Journeys (e-commerce):**

- J-01: First-time purchase on mobile.
- J-02: Returning customer Apple Pay express checkout.
- J-03: Resume abandoned cart from email.
- J-04: Refund and re-order.
- J-05: Subscription upgrade with prorated billing.

### Step 2: Prioritize Journeys by User Impact

Use the user-impact rubric (`../qa-execution/references/bug-severity-by-user-impact.md`):

**P0 (Must Run):**
- Journeys whose failure causes `Blocks-Completion` or `Data-Loss` for paying users.
- Public flows that should already be covered by E2E when the harness exists.

**P1 (Should Run):**
- Journeys whose failure causes `Trust-Damage` or repeated `Friction` for any persona.
- Cross-feature journeys with touchpoints in the change.
- Bug-prone public regressions that should become E2E candidates.

**P2 (Nice to Run):**
- Secondary journeys, edge personas, lower-traffic surfaces.
- Cosmetic-impact journeys (off-brand styling, minor inconsistency).

### Step 3: Group by Persona × Surface

For each persona × surface, pick the journey that best validates the combination:

```
Authentication & Authorization (all personas)
├─ J-S1: New User signup → first task
├─ J-S2: Casual User session resume after 30-day gap
├─ J-S3: Power User SSO sign-in
└─ J-S4: Recovering User password reset after failed login

Payment Processing
├─ J-P1: First-time mobile purchase (New User)
├─ J-P2: Apple Pay express (Power User)
├─ J-P3: Recovery after declining card (Recovering User)
└─ J-P4: Refund flow (Casual User)

User Management
├─ J-U1: Update notification preferences and verify delivery
├─ J-U2: Account export
└─ J-U3: Account deletion with data retention check
```

### Step 4: Tag Automation Candidates

When the repository already supports E2E, mark these as automation candidates:

- Changed P0 / P1 journeys (`Automation Target: E2E`)
- Release-critical smoke journeys
- Bug-driven regressions reproduced through browser, HTTP, CLI, or worker entrypoints

Keep journeys `Manual-only` when they are:

- Exploratory (charters, tours, persona-driven CFRs)
- Usability-focused (Nielsen-style checks)
- Visual-design judgment (Figma fidelity beyond computed-style comparisons)
- Accessibility via real AT (VoiceOver / NVDA / TalkBack journeys)

---

## Execution Strategy

### Test Execution Order

**1. Smoke first**

- If smoke fails → stop, fix build, do not proceed.
- If smoke passes → proceed to targeted or full regression depending on scope.

**2. P0 journeys next**

- Critical journeys with primary persona.
- Must pass before continuing.

**3. P1 then P2**

- Complete remaining journeys.
- Track friction findings even when goal is reached.

**4. Exploratory charters**

- Off-script tours.
- Persona-driven sessions.
- Find unexpected issues.

**5. CFR pass**

- 45-minute time-box.
- Cover the six CFR categories on the two most-trafficked journeys.

### Pass / Fail / Conditional Criteria

**PASS:**

- All P0 journeys reach their goal observable.
- ≥ 90% of P1 journeys reach their goal observable.
- Zero open `Blocks-Completion` / `Data-Loss` bugs on P0 journeys.
- No critical CFR finding open.

**FAIL (Block Release):**

- Any P0 journey fails to reach goal.
- Any `Blocks-Completion` / `Data-Loss` bug discovered.
- Critical CFR finding open (e.g., signup unusable for Accessibility-Reliant persona).
- Production-parity gap that invalidates the QA result.

**CONDITIONAL PASS:**

- P1 friction findings with documented workarounds.
- Known `Trust-Damage` findings on isolated surfaces with fix plan in place.
- Cosmetic findings batched into a polish follow-up.

---

## Regression Test Management

### Test Suite Maintenance

**Monthly Review:**

- Remove obsolete journeys (features that no longer exist).
- Update changed personas (new audience segment, retired one).
- Add new high-value journeys.
- Optimize slow / repetitive journeys.

**After Each Release:**

- Update test data.
- Fix broken journey expectations.
- Add regression journeys for bugs found.
- Add or update E2E coverage for public regressions when the harness exists.
- Document journey changes.

### Automation Considerations

**Good Candidates for Automation:**

- Stable P0 journeys with deterministic goals (signup, sign-in, single-item checkout).
- Smoke journeys.
- API-driven journey segments (cart-add, save-settings).
- Cross-browser journey checks (one journey × 5 browsers).
- Changed P0 / P1 public journeys when the harness exists.
- Bug reproductions that should never regress.

**Keep Manual:**

- Exploratory charters and tours.
- Persona-driven usability evaluation.
- Accessibility-via-real-AT journeys.
- Figma fidelity beyond computed-style comparisons.
- Complex multi-persona scenarios with real human judgment.

---

## Regression Test Execution Report

Aligns with the verification report generated by `qa-execution`. When both skills are used, the verification report includes JOURNEY EXECUTION LOG and TEST CASE COVERAGE sections that cross-reference J-* and TC-* IDs from this regression suite.

```markdown
# Regression Test Report: Release 2.5.0

**Date:** 2026-05-15
**Build:** v2.5.0-rc1
**Tester:** QA Team
**Environment:** Staging (production-parity confirmed)

## Summary

| Suite | Journeys | Goal-reached | Failed | Blocked | Pass Rate |
|-------|----------|--------------|--------|---------|-----------|
| Smoke | 4 | 4 | 0 | 0 | 100% |
| P0 Critical journeys | 8 | 7 | 1 | 0 | 88% |
| P1 High journeys | 12 | 11 | 1 | 0 | 92% |
| P2 Medium journeys | 6 | 5 | 0 | 1 | 83% |
| **TOTAL** | **30** | **27** | **2** | **1** | **90%** |

## Per-journey results

- J-01 (Complete first purchase on mobile): PASS — goal reached in 87s; 2 Friction bugs filed.
- J-02 (Apple Pay express checkout): PASS — goal reached.
- J-03 (Recovery after declining card): FAIL — see BUG-007 (`Blocks-Completion` on retry).
- ...

## Critical Failures (by user impact)

### BUG-007: Payment retry stuck on declining card screen (J-03)
- **Impact:** Blocks-Completion
- **Severity:** Critical
- **Priority:** P0
- **Persona:** Recovering User
- **Journey Step:** J-03, Step 4 (re-submit with new card)
- **Status:** pending

### BUG-014: Settings save doesn't trigger notification delivery (J-U1)
- **Impact:** Trust-Damage
- **Severity:** High
- **Priority:** P1
- **Persona:** Casual User
- **Journey Step:** J-U1, Step 3 (after save)
- **Status:** pending

## CFR findings summary

- Usability: 0 fail, 3 friction, 12 pass
- Accessibility: 0 fail, 1 friction, 14 pass
- Perceived performance: 0 fail, 2 friction, 13 pass
- Compatibility: 0 fail, 0 friction, 15 pass (Chrome + Safari + Firefox + iOS Safari + Android Chrome)
- Error recoverability: 1 fail (BUG-007), 1 friction, 13 pass
- Production parity: 15 pass

## Recommendation

**Verdict:** CONDITIONAL PASS pending BUG-007 fix.

- Fix BUG-007 (payment retry) before release.
- BUG-014 acceptable with documented workaround; queue for next sprint.
- Retest J-03 and J-U1 after fixes.
- Final smoke before production deployment.

## Risks

- Payment retry issue blocks the Recovering User's primary recovery path; impacts revenue and trust.
- Settings → notification delivery gap may erode trust in notification reliability.

## Next Steps

1. Fix BUG-007 by EOD.
2. Retest J-03 with the Recovering User persona on mobile Safari.
3. Document BUG-014 workaround in user-facing release notes.
4. Final smoke + production-parity check before release.
```

---

## Common Pitfalls

**❌ Don't:**

- Run the same journey list every release without updating.
- Skip regression "to save time" — regression is the only line of defense against unseen breakage.
- Ignore Friction-class findings on P0 journeys (they compound into Trust-Damage).
- Test only happy paths — abandonment paths surface highest-impact bugs.
- Forget to update test data for journey preconditions.
- Run regression in incognito or with cleared cache (production parity).

**✅ Do:**

- Maintain the journey list regularly.
- Run smoke daily, full regression weekly.
- Investigate every failure as a real user would interpret it.
- Include abandonment paths in every journey.
- Keep journey time budgets aligned to persona patience windows.
- Validate production parity before treating any result as authoritative.
- Add or update E2E coverage for public regressions when the harness exists.

---

## Regression Checklist

**Before Execution:**

- [ ] Build deployed to a production-parity environment
- [ ] CI gate ran separately and is green (use `agent-output-audit` if AI-implementation audit is required)
- [ ] Test data prepared and matches journey preconditions
- [ ] Previous bugs verified fixed by re-running their journey
- [ ] Journey list reviewed / updated for the release scope

**During Execution:**

- [ ] Follow journey execution order (Smoke → P0 → P1 → P2 → Exploratory → CFR)
- [ ] Document all failures with persona × journey × step
- [ ] Screenshot at every step of every journey
- [ ] Note unexpected behavior (friction, surprises) even when goal is reached
- [ ] Track blockers and missing prerequisites

**After Execution:**

- [ ] Compile results by journey, not by test case
- [ ] File new bugs with Impact (user-side) and Persona Affected fields
- [ ] Update journey time budgets if persona patience was violated
- [ ] Update automation status for P0 / P1 / bug-driven public regressions
- [ ] Report to stakeholders with the user-impact summary
- [ ] Archive artifacts at `<qa-output-path>/qa/`

---

## Quick Reference

| Suite Type | Duration | Frequency | Journey Coverage |
|------------|----------|-----------|------------------|
| Smoke | 15-30 min | Daily | 2-4 P0 journeys |
| Targeted | 30-60 min | Per change | Changed surface journeys + 1 canary |
| Full | 2-4 hours | Weekly/Release | All P0 + P1 journeys, every persona |
| Sanity | 10-15 min | After hotfix | Hotfix journey + 1 adjacent |

**Remember:** Regression testing isn't about test cases passing — it's about real users still reaching their goals.

---

## Sources

- `../qa-execution/references/journey-maps.md` — canonical journey anatomy.
- `../qa-execution/references/bug-severity-by-user-impact.md` — user-impact rubric.
- Martin Fowler — *The Practical Test Pyramid*: high-value user journeys as the unit of E2E coverage.
- TestCollab — *Software Testing Strategies for QA Teams in 2026*: regression-as-protection framing.
- Thoughtworks — *10 tips for an Agile QA mindset, Tip 5*: automate routine regressions; keep exploratory manual.
