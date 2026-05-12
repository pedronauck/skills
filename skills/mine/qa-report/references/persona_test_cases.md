# Persona Test Cases — Planning Reference

This file is the planning view of persona-driven QA. The canonical persona definitions live in `../qa-execution/references/user-personas.md`. Read both files before writing a TC-PERSONA-*.

## Contents

- What a persona test case is
- Persona attributes (recorded per TC — YAML schema)
- TC-PERSONA-* template
- Friction hypotheses (per persona type)
- Persona × Surface coverage matrix
- Worked example (TC-PERSONA-012: New User signs up on mobile with flaky 4G)
- Anti-patterns
- Sources

## What a persona test case is

A persona test case validates that a **specific user role** can succeed at a **specific surface** under **realistic conditions for that role**. It is *not* a generic feature test with a persona name slapped on.

Examples:

- **Good:** *"A New User on a phone-small viewport with 4G can sign up for an account in under 3 minutes without consulting the help link."*
- **Bad:** *"A user can sign up."* (no persona, no conditions, no patience window)
- **Bad:** *"As a Power User, verify the signup form renders correctly."* (Power Users don't sign up; persona-of-convenience)

The persona is the constraint that surfaces the bug; without it, you're testing the system, not the user.

## Persona attributes (recorded per TC)

Every TC-PERSONA-* must capture this row before the test steps:

```yaml
persona:
  name: <New User | Power User | Casual User | Mobile User | Accessibility-Reliant | Recovering User>
  familiarity: <zero | familiar | expert>
  motivation: <evaluate | complete-task | ship-work-fast | one-handed-action | use-on-equal-terms | trust-check>
  device: <desktop | laptop | tablet | phone-small | phone-large>
  network: <wifi-fast | wifi-slow | 4g | 3g | flaky>
  modality: <mouse-keyboard | touch | screen-reader | keyboard-only | voice>
  locale: <en-US | pt-BR | de-DE | ...>
  patience_seconds: <abandonment threshold>
```

The schema mirrors `../qa-execution/references/user-personas.md` so `qa-execution` can parse it without re-mapping.

## TC-PERSONA-* template

See `test_case_templates.md` for the full template. The mandatory sections are:

1. **Persona Attributes** — the YAML block above.
2. **Objective** — phrased from the persona's perspective.
3. **Friction Hypotheses** — 3 specific things the persona is likely to hit on this surface (predict before the session).
4. **Test Steps** — user-language actions, expected observables within the persona's patience window.
5. **Pass Criteria** — the persona reaches their goal without Blocks-Completion friction and without Trust-Damage observations.

## Friction hypotheses

The hypotheses are the heart of a persona TC. They force you to anticipate, not just observe. Write 3 hypotheses before the session:

- **For New User:** unclear primary action; confusing copy; required field with no example.
- **For Power User:** missing keyboard shortcut; bulk operation that resets state; missing undo.
- **For Casual User:** "where did that button go?"; logged-out unexpectedly; auto-saved draft missing.
- **For Mobile User:** sticky element covers content; modal escape doesn't work; touch target under 44px.
- **For Accessibility-Reliant:** missing label on a critical field; focus trap in modal; dynamic content not announced.
- **For Recovering User:** stale error message; cached failure screen; "we're sorry" with no next step.

If all three hypotheses turn out clean during execution, that's a finding too — the persona had a friction-free experience worth celebrating in the verification report.

## Persona × Surface coverage matrix

A release-candidate QA plan should cover each surface against at least the matching persona. Use this matrix to spot gaps:

| Surface | Mandatory persona | Recommended additional |
|---|---|---|
| Onboarding / first-run | New User | Mobile User |
| Settings / account | Casual User | Power User |
| Bulk operations / dashboards | Power User | Casual User |
| Mobile-only feature | Mobile User | Accessibility-Reliant |
| Recovery / error pages | Recovering User | New User |
| Public marketing / landing | New User | Accessibility-Reliant |
| Form-heavy flow | Casual User | Mobile User |
| Multi-step wizard | New User | Power User |

A plan that covers fewer than 3 personas across the release leaves a persona blindspot — call it out in the test plan's Risk Assessment.

## Worked example

```markdown
## TC-PERSONA-012: New User signs up on mobile with flaky 4G

**Priority:** P0
**Type:** Persona
**Persona:** New User
**Surface:** /signup
**Automation Target:** Manual-only

### Persona Attributes

| Attribute | Value |
|---|---|
| Name | New User |
| Familiarity | zero |
| Motivation | evaluate |
| Device | phone-small |
| Network | 4g (flaky — simulated drops every 30s) |
| Modality | touch |
| Locale | en-US |
| Patience (seconds) | 60 |

### Objective
Verify a brand-new visitor on a phone with flaky 4G can complete signup and reach the dashboard within 3 minutes without consulting external help.

### Friction Hypotheses
1. Password field's complexity rules aren't visible until after the first invalid submit.
2. The 6-digit email code input may not be touch-friendly (tap targets too small).
3. A flaky network during the verify-email step may strand the user with no retry.

### Test Steps

1. Open https://app.example.com/ from a fresh device (no cookies, no autofill).
   **Expected:** Landing page within 2 seconds; signup CTA visible above the fold.

2. Tap "Sign up" CTA.
   **Expected:** Signup form within 1 second; primary fields visible without scroll.

3. Enter realistic test email + password (12 chars, mixed case, one digit).
   **Expected:** Password field shows complexity rules inline (not after submit); submit button enabled.

4. Submit form during simulated network drop.
   **Expected:** Spinner appears within 100ms; on network resume, request retries automatically OR user gets an obvious retry button. No double-submit. No silent failure.

5. Receive email; enter 6-digit code on phone.
   **Expected:** Code input has 44px+ touch targets; can paste 6-digit code from email app; advances on completion.

6. Reach dashboard.
   **Expected:** Goal observable visible within 3 minutes total from Step 1.

### Pass Criteria
- All 3 friction hypotheses cleared (or filed as bugs).
- Total time from landing to dashboard < 180 seconds.
- No `Blocks-Completion` or `Data-Loss` observations.
- No `Trust-Damage` observations on the verify-email step under network drop.
```

## Anti-patterns

- **Persona-as-label** — adding `persona: Power User` to a generic test without changing the test. The persona must change what you do.
- **Single-persona-for-everything** — running every test as Power User because that's the developer's mental model. Mix personas.
- **No friction hypotheses** — without predictions, the session degrades to feature verification.
- **Patience-window violations not flagged** — if the persona's patience is 60s and a step takes 90s, that's a finding even if the step "works".

## Sources

- `../qa-execution/references/user-personas.md` — canonical persona definitions (this file's source of truth for the six-persona model).
- Testlio — *Exploratory Testing 101*: persona adoption as a tester technique.
- Thoughtworks — *10 tips for an Agile QA mindset*: CFR validation through persona-aware lenses.
