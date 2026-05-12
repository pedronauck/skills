# Cross-Functional Requirement Checks

Cross-Functional Requirements (CFRs) are the user-perceivable qualities of the product that no single feature owns: usability, accessibility, perceived performance, browser/device compatibility, error recoverability, production parity. Real-user QA validates CFRs *during* user-flow execution — not as a separate phase.

> "It's the QA's duty to also check the user journey and user experience of the application. Of the CFRs, user experience, performance, security and compatibility are most important." — Thoughtworks, *10 tips for an Agile QA mindset*

This reference defines the short-form CFR pass that runs in Step 6 of `qa-execution`. It is intentionally lightweight — full audits (WCAG conformance reports, Lighthouse runs, perf budgets) belong to dedicated tools and stages.

## Contents

- CFR scope (the six mandatory categories)
- 1. Usability — Nielsen short list
- 2. Accessibility — WCAG AA quick check (keyboard / screen reader / visual)
- 3. Perceived performance (paint, TTI, spinner, button feedback)
- 4. Compatibility (browser × device × version smoke)
- 5. Error recoverability
- 6. Production parity
- How to run the CFR pass (45-minute time-box)
- Anti-patterns
- Sources

## CFR scope

Six CFR categories are mandatory for every release-candidate QA pass:

1. **Usability** — Nielsen heuristics short list.
2. **Accessibility** — WCAG 2.1 AA quick check.
3. **Perceived performance** — what the user *feels*, not what Lighthouse reports.
4. **Compatibility** — browser × device × version smoke.
5. **Error recoverability** — what happens when something breaks.
6. **Production parity** — does the build behave like real production will.

Skipping a category is allowed only with explicit reasoning recorded in the verification report.

## 1. Usability — Nielsen short list

Walk the changed surface and answer each, citing the journey step:

- [ ] **Visibility of system status** — is there feedback within 1 second of every user action?
- [ ] **Match with the real world** — does the copy use the user's language, not the system's? (No "Entity created", no "Request 200 OK".)
- [ ] **User control and freedom** — can the user undo, cancel, or back out of every committed action?
- [ ] **Consistency** — same noun for the same thing across the surface? Same icon for the same action?
- [ ] **Error prevention** — confirmation prompts on irreversible actions? Inline validation before submit?
- [ ] **Recognition over recall** — does the user have to remember anything from a previous screen?
- [ ] **Flexibility for power users** — keyboard shortcuts for repeated actions?
- [ ] **Aesthetic and minimalist** — is every word, button, image earning its place?
- [ ] **Help users recover from errors** — error messages in plain language with a specific next step?
- [ ] **Help and documentation** — is there a path to help from the failing state?

For each unmet heuristic, file a `Friction` or `Trust-Damage` bug (see `bug-severity-by-user-impact.md`).

## 2. Accessibility — WCAG AA quick check

Quick check, not a conformance audit. The full audit belongs to a dedicated accessibility skill.

### Keyboard

- [ ] Every interactive element is reachable with Tab.
- [ ] Tab order matches visual order.
- [ ] Visible focus indicator on every focusable element.
- [ ] Escape closes modals; Enter activates primary actions.
- [ ] No keyboard trap — can always Tab back out.

### Screen reader (run with VoiceOver on macOS or NVDA on Windows)

- [ ] Page has a logical heading hierarchy (one `<h1>`).
- [ ] Form fields have associated labels (not just placeholders).
- [ ] Buttons have an accessible name that describes their action.
- [ ] Images have alt text (or are explicitly marked decorative).
- [ ] Dynamic content (toasts, modals) is announced.
- [ ] Status messages use `aria-live` appropriately.

### Visual

- [ ] Color is not the only signal (errors aren't red-only; success isn't green-only).
- [ ] Text contrast ≥ 4.5:1 against background (3:1 for large text).
- [ ] UI doesn't break at 200% zoom or with OS-level text scaling.
- [ ] Reduce-motion respected (no auto-playing decorative animation).

For each violation, file an `Accessibility` bug under `Trust-Damage` severity unless it blocks a core journey (then `Blocks-Completion`).

## 3. Perceived performance

Measure what the user feels, not what synthetic tools report.

| Observable | Target | When it fails |
|---|---|---|
| Time to first meaningful paint | <2s on wifi, <4s on 3G | Layout shifts after 2s; user sees a blank screen |
| Time to interactive | <3s on wifi, <6s on 3G | User clicks during load and the click is ignored |
| Spinner threshold | Spinner appears within 100ms of an action that will take >300ms | Action looks dead before the spinner appears |
| Button feedback | Visible state change within 50ms of click | User double-clicks because nothing happened |
| Optimistic UI | Where used, must reconcile correctly on failure | "Saved" message followed by silent loss |
| Long-task UX | Actions >2s have progress / cancel / "still working" | User abandons; assumes it's stuck |

For each failure, file a `Friction` bug (rarely `Blocks-Completion` unless the perceived stall causes abandonment).

## 4. Compatibility

Smoke the changed surface across the minimum compatibility matrix:

| Layer | Minimum |
|---|---|
| Browser | Latest Chrome + Safari + Firefox |
| Mobile | Safari on iPhone (latest), Chrome on Android (latest) |
| Viewport | 1280, 768, 375 |
| OS dark mode | Light AND dark |
| Reduced motion | On AND off |

If the change touches CSS or layout, viewport coverage is mandatory. If it touches forms, Safari (especially mobile Safari) is mandatory — autofill behavior diverges.

File any divergence as a bug; severity by user impact, not by which browser.

## 5. Error recoverability

For every failure path discovered during execution, the recovery experience must:

- [ ] Show a plain-language explanation (no stack traces, no error codes alone).
- [ ] Offer a specific next step (retry, go back, contact support, reload).
- [ ] Preserve user input where possible (no "fill out the whole form again").
- [ ] Indicate whether the failure is transient or permanent.
- [ ] For data-loss situations, name what was lost (not "an error occurred").

A failure path without a recoverable UX is a `Trust-Damage` bug at minimum, often `Data-Loss`.

## 6. Production parity

> "We need to make sure that upstream/downstream software systems of lower environments are configured in the same way as the ones that are going to be in production." — Thoughtworks

For the QA session itself:

- [ ] Tested in a build that matches the production deploy artifact (not just "works on my machine").
- [ ] Tested with **third-party cookies enabled** (the default; many QA testers disable them and miss bugs).
- [ ] Tested in a **normal browser profile**, NOT incognito (cache, autofill, extensions interact differently).
- [ ] Tested with a **realistic browser extension set** (one ad blocker, one password manager). Many bugs come from extension injection.
- [ ] Tested with the same auth flow real users will take (SSO, not test bypass).
- [ ] Tested against the same backend services, not local mocks.
- [ ] Network conditions tested at realistic worst case (Slow 3G), not just on office wifi.

Document any deviation in the verification report — production parity gaps invalidate the QA result.

## How to run the CFR pass

After Steps 4-5 of `qa-execution` (journey execution + off-script tours), run a single CFR pass over the changed surface:

1. Pick **2 journeys** from your charters that exercise the largest surface area.
2. Walk them again, this time as a **CFR audit**, not a journey verification.
3. At each step, ask the six categories above. Mark each `pass`, `friction`, or `fail`.
4. File one bug per CFR finding. Use the severity rubric in `bug-severity-by-user-impact.md`.
5. Record the CFR pass results in the verification report under `CFR FINDINGS`.

The CFR pass is time-boxed: **45 minutes total**. Anything not finished in 45 minutes becomes a follow-up CFR charter.

## Anti-patterns

- **Full conformance audit in QA window** — WCAG conformance audits and Lighthouse passes take hours and require dedicated tooling. Do the short check here; queue the deep audit separately.
- **Skipping CFR because "the feature works"** — the feature working and the CFRs holding are different claims.
- **CFR before journey execution** — CFR is a lens on real flows; running it without a flow produces shallow findings.
- **Treating CFR as security testing** — security is its own discipline (SAST/DAST, code review). CFR's "security" notes are about user perception (e.g., does the site feel trustworthy?), not vulnerability scanning.

## Sources

- Thoughtworks — *10 tips for an Agile QA mindset, Tip 7 (CFR tests)*: user experience, performance, security and compatibility as the priority CFRs; user-journey metrics (clicks-to-checkout, accessibility, aesthetic).
- Thoughtworks — *10 tips for an Agile QA mindset, Tip 8 (incognito/cache)*: don't validate in incognito because real users don't use it.
- Thoughtworks — *10 tips for an Agile QA mindset, Tip 9 (production parity)*: upstream/downstream config parity.
- TestCollab — *Software Testing Strategies for QA Teams in 2026*: CFR categories as part of behavioral testing.
- Nielsen Norman Group — *10 Usability Heuristics for User Interface Design*: source for the short list.
- W3C — *WCAG 2.1 Quick Reference*: source for the AA-quick-check items.
