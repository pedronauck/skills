# Bug Severity by User Impact

Real-user QA classifies bugs by what they do to the user, not by what they do to the technology. A "critical security vulnerability" can be invisible to users; a "minor UI bug" can cost the company a customer. This file defines the user-impact severity rubric used by `qa-execution`, `qa-report`, and the shared `assets/issue-template.md`.

## Contents

- Why a user-impact rubric
- The five user-impact tiers (Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic)
- Mapping to technical severity (back-compat)
- Field in the bug template
- Verification report rollup
- Anti-patterns
- Sources

## Why a user-impact rubric

> "There is one important way of determining whether software you've delivered is successful: its acceptance by end users." — Thoughtworks, *10 tips for an Agile QA mindset*

Technical severity (Critical/High/Medium/Low) is useful for engineering triage. But two bugs with the same technical severity can have radically different effects on real users — a Medium-severity copy bug on a checkout button can be worse than a High-severity exception in an admin dashboard. The user-impact rubric forces the question: *"what does this do to a real person trying to use the product?"*

## The five user-impact tiers

Pick exactly one tier per bug. When in doubt between tiers, pick the higher impact.

### Blocks-Completion

- **Definition:** A user trying to complete a value-delivering journey cannot complete it. They either give up or use a workaround that produces incorrect state.
- **Examples:**
  - Submit button does nothing on the only payment screen.
  - Login fails for valid credentials.
  - "Save" appears to succeed but data is lost on reload.
  - 404 on a critical journey URL with no recovery path.
- **Defaults:** `Severity: Critical`, `Priority: P0`.
- **Release impact:** A `Blocks-Completion` open on a P0 journey is a release blocker.

### Data-Loss

- **Definition:** A user's data (entered, uploaded, configured) is destroyed, corrupted, or made inaccessible without their consent. The user may not notice immediately.
- **Examples:**
  - Form submission silently drops a field.
  - File upload reports success but the file is empty/missing in the destination.
  - Settings revert to defaults on save.
  - Account deletion removes data marked "keep on deletion".
- **Defaults:** `Severity: Critical`, `Priority: P0`.
- **Release impact:** A `Data-Loss` open on any journey is a release blocker — silent loss is worse than visible failure because users can't recover from what they don't notice.

### Trust-Damage

- **Definition:** Nothing is technically broken, but the user's confidence in the product is eroded. They wonder if they can rely on this for important work.
- **Examples:**
  - Confirmation email says "Order #abc123" when the UI says "Order #xyz789".
  - Error message: "An unexpected error occurred. Please try again." (with no actionable next step).
  - Login page redirects to an HTTP page briefly during OAuth.
  - "Last saved" indicator shows future timestamp.
  - Different currency symbols on the same page.
  - Broken alt text announced by screen readers ("image image image").
- **Defaults:** `Severity: High`, `Priority: P1`.
- **Release impact:** Multiple `Trust-Damage` findings on the same journey is a release blocker even if no single one is.

### Friction

- **Definition:** Users can complete the journey, but with extra effort, confusion, or repetition. The product feels harder to use than it should.
- **Examples:**
  - Form requires re-entering data that was already provided.
  - Hover-only controls on mobile (no touch equivalent).
  - 3-second delay before button feedback.
  - "Continue" appears below the fold on mobile.
  - Validation fires only on submit, not inline.
  - Modal closes when clicking inside it (instead of only outside).
- **Defaults:** `Severity: Medium`, `Priority: P2`.
- **Release impact:** Not a release blocker individually. Track patterns — repeated `Friction` in the same area is a redesign signal.

### Cosmetic

- **Definition:** Visual or wording issues that don't affect the user's ability to complete the journey or trust the product. Often platform-specific.
- **Examples:**
  - Typo in a help tooltip.
  - 2px misalignment of an icon.
  - Hover state slightly off-brand color.
  - Slightly inconsistent capitalization in a list of headings.
- **Defaults:** `Severity: Low`, `Priority: P3`.
- **Release impact:** Never a release blocker. Batch into a "polish" follow-up.

## Mapping to technical severity (back-compat)

The bug report keeps the legacy `Severity:` and `Priority:` fields for tooling continuity. Use this mapping when filling them in:

| User-impact tier | Default Severity | Default Priority | Override when… |
|---|---|---|---|
| Blocks-Completion | Critical | P0 | The blocked journey is P2/P3 in `journey-maps.md` → Severity High |
| Data-Loss | Critical | P0 | The data is reproducible from another source → Severity High |
| Trust-Damage | High | P1 | Damage is reversible without user effort (auto-correct) → Severity Medium |
| Friction | Medium | P2 | Friction occurs on a P0 journey → Severity High |
| Cosmetic | Low | P3 | Cosmetic on hero/onboarding surface → Severity Medium (first-impression risk) |

## Field in the bug template

`assets/issue-template.md` adds an `Impact (user-side):` field. Fill it with the tier name:

```markdown
**Impact (user-side):** Blocks-Completion
**Severity:** Critical
**Priority:** P0
```

Persona and journey context are also required:

```markdown
**Persona Affected:** New User
**Journey Step:** Complete first purchase, Step 4 (payment)
```

These two fields let product owners read the issue queue and immediately understand *who is hurt* and *when*, without reading the full bug.

## Verification report rollup

In the verification report, summarize issues filed by user-impact tier alongside the legacy severity count:

```
ISSUES FILED
------------
Total: 12
By user impact:
  - Blocks-Completion: 1
  - Data-Loss: 0
  - Trust-Damage: 4
  - Friction: 6
  - Cosmetic: 1
By severity (back-compat):
  - Critical: 1
  - High: 4
  - Medium: 6
  - Low: 1
```

The user-impact totals drive the release-go/no-go conversation. The severity totals drive engineering triage.

## Anti-patterns

- **"Cosmetic" on hero surface** — first-impression bugs are at minimum Friction, often Trust-Damage.
- **"Friction" on P0 journey** — if the friction is bad enough to make users abandon, it's Blocks-Completion.
- **Underrating Trust-Damage** — engineering often discounts these because "the feature works". Product, support, and growth teams disagree.
- **"Critical" on every bug** — devalues the severity scale. Reserve Critical for actual Blocks-Completion or Data-Loss.

## Sources

- Thoughtworks — *10 tips for an Agile QA mindset*: end-user acceptance as the success criterion; quality is a whole-team responsibility.
- Incredibuild — *A Comprehensive Guide to E2E Testing*: bugs that span features are higher impact than feature-isolated bugs.
- TestCollab — *Software Testing Strategies for QA Teams in 2026*: risk-based prioritization weighted by user impact.
