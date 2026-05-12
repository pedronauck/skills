# CFR Test Cases — Planning Reference

This file is the planning view of Cross-Functional Requirement (CFR) test cases. The **canonical CFR check definitions** (the six categories, targets, and the 45-minute time-box) live in `../qa-execution/references/cfr-checks.md`. Read both before generating a TC-CFR-*.

## Contents

- What a CFR test case is
- TC-CFR-* template
- CFR coverage strategy (per release-candidate)
- Persona × CFR pairing
- Worked examples (Usability / Accessibility / Perceived-Performance / Compatibility / Error-Recoverability / Production-Parity)
- Anti-patterns
- Sources

## What a CFR test case is

A CFR test case validates one of the six user-perceivable qualities of the product:

1. **Usability** — Nielsen short list.
2. **Accessibility** — WCAG 2.1 AA quick check.
3. **Perceived performance** — what the user *feels*, not what synthetic tools report.
4. **Compatibility** — browser × device × version smoke.
5. **Error recoverability** — graceful failure with actionable recovery.
6. **Production parity** — production-realistic conditions (no incognito-only tests).

CFR test cases are deliberately lightweight. The full audits (WCAG conformance, Lighthouse runs, perf budgets) belong to dedicated tools, not this skill.

## TC-CFR-* template

See `test_case_templates.md` for the full template. Mandatory fields:

- `CFR Category` — exactly one of: Usability | Accessibility | Perceived-Performance | Compatibility | Error-Recoverability | Production-Parity.
- `Persona` — match the persona to the CFR (Accessibility-Reliant for a11y, Mobile User for touch perceived-perf, Recovering User for recoverability, etc.).
- `Surface` — the feature/area under test.
- `Checklist` — pick the relevant subset of items from `../qa-execution/references/cfr-checks.md` for this CFR category.
- `Targets` — concrete observable targets for measurable CFRs (paint time, TTI, spinner threshold, contrast ratio).

## CFR coverage strategy

For a release-candidate test plan:

- **Mandatory** — at least one TC-CFR-* per category that the change affects.
- **Recommended** — at least two TC-CFR-* on each of the two most-trafficked journeys (Usability + one other).
- **Production parity** — always include at least one TC-CFR-* explicitly for production parity (no incognito, real auth, realistic extension set).

## Persona × CFR pairing

| CFR Category | Best persona | Why |
|---|---|---|
| Usability | Casual User | Casual users surface "where did that go?" friction better than experts |
| Accessibility | Accessibility-Reliant | The only persona that exercises real assistive tech |
| Perceived performance | Mobile User | Mobile users have lower patience and worse networks |
| Compatibility | Mobile User + Casual User | Cover iOS Safari + Android Chrome at minimum |
| Error recoverability | Recovering User | The only persona explicitly modeling post-failure trust |
| Production parity | New User | New users come in fresh; surfaces incognito-only bugs immediately |

## Worked examples

### TC-CFR-001: Usability quick check on /checkout

```markdown
**CFR Category:** Usability
**Persona:** Casual User
**Surface:** /checkout

### Checklist (from cfr-checks.md)
- [ ] Visibility of system status (feedback within 1s)
- [ ] Match with real world (no "Entity created" copy)
- [ ] User control and freedom (undo / cancel on every step)
- [ ] Consistency (same noun for same thing)
- [ ] Error prevention (inline validation before submit)
- [ ] Recognition over recall (no need to remember prior screen state)
- [ ] Help users recover from errors (plain language + specific next step)

### Pass criteria
- All checklist items mark `pass` or `friction`.
- No `fail` on any checklist item.
- No `Friction`-class or higher CFR finding surfaces.
```

### TC-CFR-002: Accessibility WCAG AA quick check on /checkout

```markdown
**CFR Category:** Accessibility
**Persona:** Accessibility-Reliant
**Surface:** /checkout

### Checklist (from cfr-checks.md)
Keyboard:
- [ ] Every interactive element reachable with Tab
- [ ] Tab order matches visual order
- [ ] Visible focus indicator
- [ ] Escape closes modals; Enter activates primary
- [ ] No keyboard trap

Screen reader (VoiceOver / NVDA):
- [ ] Logical heading hierarchy (one h1)
- [ ] Form fields have associated labels (not just placeholders)
- [ ] Buttons have accessible name describing action
- [ ] Dynamic content announced via aria-live

Visual:
- [ ] Color is not the only signal
- [ ] Contrast >= 4.5:1 (3:1 for large text)
- [ ] No layout break at 200% zoom
- [ ] reduce-motion respected

### Pass criteria
- All checklist items mark `pass`.
- Any `fail` → `Trust-Damage` bug at minimum, `Blocks-Completion` if it abandons the user.
```

### TC-CFR-003: Perceived performance on /checkout (mobile)

```markdown
**CFR Category:** Perceived-Performance
**Persona:** Mobile User
**Surface:** /checkout
**Real-User Conditions:** phone-small, 4G, autofill empty

### Targets
| Observable | Target | Acceptable | Actual |
|---|---|---|---|
| First meaningful paint | < 2s | < 4s | |
| Time to interactive | < 3s | < 6s | |
| Spinner threshold | < 100ms after click | < 300ms | |
| Button feedback (visible state change) | < 50ms | < 150ms | |

### Pass criteria
- All observables within `Acceptable`.
- Targets met on `wifi-fast` repeat.
```

### TC-CFR-004: Compatibility smoke on /checkout

```markdown
**CFR Category:** Compatibility
**Persona:** Mobile User + Casual User (two passes)
**Surface:** /checkout
**Real-User Conditions:** mixed device profiles

### Browsers
- [ ] Latest Chrome (desktop)
- [ ] Latest Safari (desktop)
- [ ] Latest Firefox (desktop)
- [ ] Safari on iPhone (latest iOS)
- [ ] Chrome on Android (latest Android)

### Viewports
- [ ] 1280
- [ ] 768
- [ ] 375

### Pass criteria
- No browser-specific regression on the journey goal.
- Any divergence filed as a bug; severity by user impact, not by which browser.
```

### TC-CFR-005: Error recoverability on /checkout

```markdown
**CFR Category:** Error-Recoverability
**Persona:** Recovering User
**Surface:** /checkout

### Failure paths to exercise
1. Network drop at /payment-confirm
2. Declining card response
3. 3DS challenge timeout
4. Session expiry mid-form

### Per failure
- [ ] Plain-language explanation (no stack trace, no error code alone)
- [ ] Specific next step (retry / back / contact support)
- [ ] User input preserved
- [ ] Transience indicator (transient vs permanent)
- [ ] Data-loss situations name what was lost

### Pass criteria
- All four failure paths recoverable without restarting from /cart.
- No `Trust-Damage`-class observation.
```

### TC-CFR-006: Production parity on /checkout

```markdown
**CFR Category:** Production-Parity
**Persona:** New User
**Surface:** /checkout

### Conditions
- [ ] Not in incognito mode
- [ ] Third-party cookies enabled
- [ ] Realistic browser extension set: one ad blocker + one password manager
- [ ] Real auth path (SSO or OAuth — not test-bypass)
- [ ] Real backend services — no local mocks
- [ ] Network at realistic worst case (Slow 3G)

### Pass criteria
- No bug surfaces that wouldn't surface in production.
- No deviation from production conditions undocumented.
```

## Anti-patterns

- **Full audit in QA window** — WCAG conformance audits take hours and need dedicated tooling. Stop at the quick check; queue the deep audit separately.
- **Skipping CFR because "the feature works"** — feature working and CFRs holding are different claims.
- **CFR test case without a persona** — every CFR test case names exactly one persona.
- **Treating CFR Security as security testing** — security is its own discipline (SAST/DAST, code review). CFR "security" notes are about user trust perception, not vulnerability scanning.

## Sources

- `../qa-execution/references/cfr-checks.md` — canonical CFR check definitions (this file's source of truth).
- Thoughtworks — *10 tips for an Agile QA mindset, Tip 7*: CFR as a first-class QA concern.
- Nielsen Norman Group — *10 Usability Heuristics*.
- W3C — *WCAG 2.1 Quick Reference*.
