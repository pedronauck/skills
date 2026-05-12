# Bug Report Templates

Unified templates shared with `qa-execution`. All bug reports use the `BUG-<num>` ID scheme and follow the structure in `assets/issue-template.md`. The user-impact rubric (Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic) is defined in `../qa-execution/references/bug-severity-by-user-impact.md` — read it before classifying any bug.

## Contents

- Standard Bug Report (canonical format)
- UI/Visual Bug Variant (adds Design vs Implementation section)
- User Friction Bug Variant (adds persona perspective + abandonment risk)

> Removed deliberately: Performance Bug Variant. Performance metrics (CPU %, throughput, memory, page-load milliseconds) belong to load-testing and performance-monitoring tools. When a user **feels** slowness during QA, file it as `Trust-Damage` or `Friction` using the Standard or User Friction template — the CFR check in `cfr_test_cases.md` (Perceived-Performance category) is the planning artifact for this.

---

## Standard Bug Report

The canonical format. See `assets/issue-template.md` for the exact template.

```markdown
# BUG-<num>: <short-title>

**Impact (user-side):** Blocks-Completion | Data-Loss | Trust-Damage | Friction | Cosmetic
**Severity:** Critical | High | Medium | Low
**Priority:** P0 | P1 | P2 | P3
**Type:** Functional | UI | Accessibility | Usability | Data | Crash
**Status:** pending | resolved | invalid
**Persona Affected:** New User | Power User | Casual User | Mobile User | Accessibility-Reliant | Recovering User
**Journey Step:** J-NN journey name, Step N (verb)

## Environment
- **Build:** <version or commit>
- **OS:** <operating system if relevant>
- **Browser:** <browser and version>
- **Viewport:** <width × height>
- **Network:** <profile>
- **Locale:** <locale>
- **URL:** <page or endpoint where bug occurs>

## Summary
<One paragraph from the persona's perspective.>

## Reproduction
Charter: CH-NN (or "off-script" / "CFR pass" / "journey execution")
Tour: <if surfaced inside a tour, name it>

Steps:
1. <plain-language user action>
2. <plain-language user action>
3. <where it failed>

Observed:
- <user-side observation>
- <screenshot path>

## Expected
<Correct user-side behavior. Cite the journey goal observable when relevant.>

## Root cause
<Engineering fills this in during fix.>

## Fix
<Engineering fills this in.>

## Verification
- <narrow reproduction rerun>
- <re-run of the affected journey>
- <CFR pass on the affected category, if applicable>

## Impact
- **Users Affected:** <all of <persona> | subset | specific role>
- **Frequency:** <always | sometimes | rare>
- **Workaround:** <describe or "none">
- **Trust cost:** <one sentence on what this signals to the user about the product>

## Related
- Test Case: <TC-ID if applicable>
- Figma Design: <URL if UI bug>
- Related journeys: <J-NN list>
- Related charters: <CH-NN list>
```

---

## UI/Visual Bug Variant

Extend the standard template with a design-vs-implementation comparison table when reporting Figma discrepancies.

```markdown
# BUG-<num>: [Component] Visual Mismatch

**Impact (user-side):** Cosmetic | Trust-Damage (when it breaks brand consistency on hero/onboarding surface)
**Severity:** Low | Medium
**Priority:** P3 | P2
**Type:** UI
**Status:** pending
**Persona Affected:** Mobile User (most likely — visual bugs at small viewports are highest impact)
**Journey Step:** <J-NN, Step N>

## Environment
- **Build:** v2.5.0
- **Browser:** Chrome 120
- **Viewport:** 1280 × 800
- **URL:** /components/button

## Summary
On the primary button on /components/button, the background color and font weight diverge from the Figma spec at the [URL]. The persona sees a button that doesn't match the brand styling other buttons use, which damages the impression of polish on this surface.

## Design vs Implementation

| Property | Figma (Expected) | Implementation (Actual) | Match |
|----------|-------------------|--------------------------|-------|
| Background | #0066FF | #0052CC | No |
| Font Size | 16px | 16px | Yes |
| Font Weight | 600 | 400 | No |
| Padding | 12px 24px | 12px 24px | Yes |
| Border Radius | 8px | 8px | Yes |

## Reproduction
Charter: CH-NN (or "Figma fidelity check")
Steps:
1. Navigate to /components/button
2. Compare the primary button against the Figma frame at [URL]

Observed:
- Background and font weight diverge per the table above.
- Screenshot: <path>

## Expected
Button matches Figma design at [Figma URL] within tolerance defined in `figma_validation.md`.

## Root cause
[Engineering fills this in.]

## Fix
[Engineering fills this in.]

## Verification
- [ ] Visual comparison with Figma after fix
- [ ] Check at viewports: 375px, 768px, 1280px

## Impact
- **Users Affected:** All who see this button
- **Frequency:** Always
- **Workaround:** None (visual inconsistency)
- **Trust cost:** Signals lack of attention to detail on a brand-visible surface.

## Related
- Test Case: TC-UI-001
- Figma Design: [URL]
- Related journeys: <J-NN list>
```

---

## User Friction Bug Variant

Extend the standard template when reporting friction that doesn't block completion but degrades the experience. Friction bugs benefit from explicit abandonment-risk reasoning.

```markdown
# BUG-<num>: [Surface] [Friction Pattern]

**Impact (user-side):** Friction | Trust-Damage (when friction repeats across the journey)
**Severity:** Medium
**Priority:** P2
**Type:** Usability
**Status:** pending
**Persona Affected:** <pick the persona this friction hurts most>
**Journey Step:** J-NN journey name, Step N

## Environment
- **Build:** v2.5.0
- **Browser:** Safari 17 on iPhone 14
- **Viewport:** 393 × 852
- **Network:** 4G
- **Locale:** en-US
- **URL:** /signup

## Summary
A New User completing signup on mobile must re-enter their email after the verify-code step fails on the first 6-digit code, because the email field is cleared on the error reload. The user can still complete signup but at a cost of frustration and a 30-second restart penalty.

## Reproduction
Charter: CH-01 (New User × Feature Tour × 30min)
Tour: Feature Tour

Steps:
1. As a New User on a phone, navigate to /signup
2. Enter email and password, submit
3. On the verify-code step, enter an intentionally wrong 6-digit code
4. Observe the error
5. Press back to the email step (or follow the "go back" link)

Observed:
- Email field is cleared.
- User must re-enter email from scratch.
- Screenshot: <path>

## Expected
Email field retains the previously-entered value when returning from the verify step. The Recovering User shouldn't pay a restart cost.

## Persona perspective
The New User's patience window for signup is 60 seconds. This friction adds 20-30 seconds of re-typing on a mobile keyboard. For a user evaluating the product, this is the difference between completing signup and abandoning.

## Abandonment risk
- Friction occurs on a P0 journey (signup).
- Friction occurs at the verify-code step — the highest-anxiety moment of the flow.
- Friction is recoverable but at a real time cost.
- Estimated abandonment risk increase: **high** based on industry benchmarks for re-entry friction on mobile signup.

## Root cause
[Engineering fills this in.]

## Fix
[Engineering fills this in.]

## Verification
- Re-run J-01 (Complete signup on mobile) as New User
- Confirm email persists across the verify-code error → back navigation

## Impact
- **Users Affected:** All New Users on mobile who hit a verify-code error
- **Frequency:** Always when the user enters a wrong code
- **Workaround:** Re-type email
- **Trust cost:** Signals carelessness during the most critical step of onboarding.

## Related
- Test Case: TC-PERSONA-012 (New User signs up on mobile with flaky 4G)
- Related journeys: J-01
- Related charters: CH-01
```

---

## Bug Title Best Practices

**Good titles** (state the surface + the persona observation):

- "[Signup] Email field cleared on verify-code error — mobile New User must re-type"
- "[Checkout] Cart total shows $0 when discount code applied twice — Casual User"
- "[Settings] VoiceOver doesn't announce save confirmation — Accessibility-Reliant"

**Bad titles**:

- "Bug in login" (no surface specificity, no observation)
- "It doesn't work" (no information)
- "Please fix ASAP!!!" (emotional, no information)

---

## Severity / Priority / Impact crosswalk

The user-impact rubric is the source of truth. See `../qa-execution/references/bug-severity-by-user-impact.md` for the full crosswalk. Quick reference:

| Impact (user-side) | Default Severity | Default Priority | Release impact |
|---|---|---|---|
| Blocks-Completion | Critical | P0 | Blocker on any P0 journey |
| Data-Loss | Critical | P0 | Blocker on any journey |
| Trust-Damage | High | P1 | Multiple on same journey = blocker |
| Friction | Medium | P2 | Tracked as redesign signal |
| Cosmetic | Low | P3 | Batched into polish follow-up |

When in doubt between two tiers, pick the higher impact. Engineering can downgrade after triage; QA should err toward user-side honesty.
