# Exploratory Charters

A charter is a written mission for one testing session. It says *"in the next 60 minutes, this tester, acting as this persona, explores this surface looking for these failures."* Charters are what separate exploratory testing from ad-hoc clicking around — they bound the session, force a focus, and produce a debrief that can be acted on.

> "Exploratory testing is not ad hoc testing. Skilled exploratory testers use charters, time-boxes, and structured note-taking to ensure their sessions are focused and reproducible." — TestCollab, *Software Testing Strategies 2026*

## Contents

- Charter anatomy (mission + persona + surface + tour + time-box)
- Charter template (YAML)
- Charter types/modes (Freestyle, Strategy-Based, Scenario-Based, Collaborative, Charter-With-Tour)
- Time-box guidance (30 / 60 / 90 min)
- Worked examples (CH-01 through CH-04)
- The debrief is mandatory
- Anti-patterns
- Sources

## Charter anatomy

Every charter has five parts:

1. **Mission** — a one-sentence statement of what to investigate and why.
2. **Persona** — who you are while testing (`user-personas.md`).
3. **Surface** — which part of the product is in scope.
4. **Tour** — which test tour drives the session (`test-tours.md`). Pick one; mixing dilutes findings.
5. **Time-box** — a hard ceiling, typically 30 / 60 / 90 minutes. The box forces prioritization.

## Charter template

```yaml
charter:
  id: CH-<NN>
  mission: "<one sentence — what we're looking for and why it matters>"
  persona:
    name: <see references/user-personas.md>
    device: <desktop | tablet | phone-small | phone-large>
    network: <wifi-fast | 4g | flaky>
    locale: <en-US | pt-BR | ...>
  surface:
    feature: <name of the area under test>
    entry_url: <full URL or deep link>
    out_of_scope: <surfaces deliberately excluded>
  tour: <see references/test-tours.md — pick exactly one>
  time_box_minutes: 30 | 60 | 90
  guidance:
    must_try: <2-4 specific things to attempt>
    must_avoid: <known-broken or out-of-scope areas>
  debrief:
    started_at: <ISO timestamp>
    ended_at: <ISO timestamp>
    findings:
      - <finding 1, with severity rationale>
    bugs_filed: [BUG-NNN, BUG-NNN]
    surprises: <unexpected observations that informed the session>
    suggested_next_charter: <what should be explored next>
```

## Charter types (modes)

Each charter belongs to one of these modes; pick before writing the mission:

### Freestyle (unstructured)

- No specific guidance beyond mission + persona + time-box.
- Tester improvises based on what they observe.
- **Use when:** the feature is new and edge cases aren't yet understood.
- **Example mission:** *"As a New User on an iPhone with flaky 4G, see if you can sign up for an account in under 5 minutes."*

### Strategy-Based

- Tester applies a specific technique throughout the session: boundary value analysis, error guessing, state transition modeling.
- **Use when:** the feature is input-heavy or has known stateful behavior.
- **Example mission:** *"As a Power User on desktop, apply boundary-value analysis to the order quantity field, including 0, 1, max, max+1, max+10, and negatives."*

### Scenario-Based

- Tester walks through a realistic end-to-end user scenario described in plain language.
- **Use when:** validating a journey (`journey-maps.md`) under realistic conditions.
- **Example mission:** *"As a Casual User who got an email coupon, click through, sign in to a 6-month-dormant account, apply the coupon, and complete a purchase."*

### Collaborative (mob / pair)

- Two or more testers run the charter together. One drives, others observe and propose.
- **Use when:** the feature crosses domain boundaries or a new tester is being onboarded.
- **Example mission:** *"As mixed personas (one New User, one Power User), pair-test the new bulk-edit feature. New User drives; Power User suggests stress patterns."*

### Charter-Based with Tour (recommended default)

- Mission is constrained by one specific tour from `test-tours.md` (Feature Tour, Money Tour, Back-Button Tour, etc.).
- **Use when:** in doubt — this is the most productive default.
- **Example mission:** *"As a Mobile User on a phone-small viewport with slow 3G, run the Back-Button Tour through the checkout flow. Confirm that pressing back at every step does something sensible."*

## Time-box guidance

| Box | When to use |
|---|---|
| 30 min | New surface, narrow scope, sanity check. Expect 2-5 findings. |
| 60 min | Default for charter-based + tour. Most productive depth-vs-fatigue balance. |
| 90 min | Complex multi-step journey, collaborative session, or first-pass exploration of a new product area. Plan a 5-min break in the middle. |

**Hard rule:** the box ends when it ends. If findings are piling up at 60 minutes, file a follow-up charter for the next session instead of extending. Tester fatigue produces false positives.

## Worked examples

### CH-01: Onboarding fidelity (New User × Feature Tour)

```yaml
charter:
  id: CH-01
  mission: "Verify a brand-new visitor on mobile can complete onboarding and reach their first 'aha' moment in under 3 minutes."
  persona:
    name: New User
    device: phone-small
    network: 4g
    locale: en-US
  surface:
    feature: onboarding
    entry_url: https://app.example.com/
    out_of_scope: post-onboarding billing setup
  tour: Feature Tour
  time_box_minutes: 30
  guidance:
    must_try:
      - "Sign up with email; skip optional fields where allowed."
      - "Find the primary action on the landing screen within 5 seconds."
    must_avoid:
      - "Pre-filled test account paths (qa-account-1, etc.)"
```

### CH-02: Bulk-edit resilience (Power User × Garbage Tour)

```yaml
charter:
  id: CH-02
  mission: "Find ways to corrupt or lose data via the new bulk-edit feature using realistic copy-paste and undo patterns."
  persona:
    name: Power User
    device: desktop
    network: wifi-fast
  surface:
    feature: bulk-edit
    entry_url: https://app.example.com/items?bulk=true
  tour: Garbage Tour
  time_box_minutes: 60
  guidance:
    must_try:
      - "Paste 200 rows from a spreadsheet with mixed formatting."
      - "Edit 50 rows, undo to row 25, edit forward — verify state."
      - "Edit, refresh mid-save, return — verify nothing is lost or partially applied."
```

### CH-03: Settings continuity (Recovering User × Back-Button Tour)

```yaml
charter:
  id: CH-03
  mission: "Verify that a user who hit yesterday's settings-save bug can return today, see clean state, and successfully save."
  persona:
    name: Recovering User
    device: laptop
    network: wifi-fast
  surface:
    feature: notification-settings
    entry_url: https://app.example.com/settings/notifications
  tour: Back-Button Tour
  time_box_minutes: 30
```

### CH-04: Mobile accessibility (Accessibility-Reliant × Locale Tour)

```yaml
charter:
  id: CH-04
  mission: "Verify the checkout flow is usable via VoiceOver on iOS with a pt-BR locale and BRL pricing."
  persona:
    name: Accessibility-Reliant
    device: phone-large
    network: wifi-fast
    locale: pt-BR
    modality: screen-reader
  surface:
    feature: checkout
    entry_url: https://app.example.com/cart
  tour: Locale Tour
  time_box_minutes: 60
```

## The debrief is mandatory

A session without a debrief is wasted exploration. After the time-box ends:

1. **Stop the timer.** Do not "just finish this one thing".
2. **Write findings within 5 minutes.** Memory fades. Capture the surprises before they normalize.
3. **File bugs.** Use `assets/issue-template.md`; severity by user impact (see `bug-severity-by-user-impact.md`).
4. **Suggest the next charter.** What did this session not cover that should be next?
5. **Note suspected new tours.** If you found yourself improvising a pattern (e.g., "double-tap then refresh"), record it — that's a candidate for `test-tours.md`.

## Anti-patterns

- **No mission** — a charter without a one-sentence mission isn't a charter; it's tab-clicking.
- **Multi-tour charter** — running Feature Tour + Garbage Tour + Locale Tour at once dilutes all three. Pick one per box.
- **Drift outside surface** — interesting bugs in another surface go to a follow-up charter, not into this debrief.
- **Skipping the debrief** — finding bugs without recording them is the same as not finding them.
- **No persona** — see `user-personas.md`. Picking one is mandatory.

## Sources

- Testlio — *Exploratory Testing 101: Charter-Based and Time-Boxed Testing*.
- Sahipro — *Exploratory Testing: Process — Create a Test Charter, Set a Time Box, Review Results*.
- TestCollab — *Software Testing Strategies for QA Teams in 2026*: "charters, time-boxes, and structured note-taking".
- Thoughtworks — *10 tips for an Agile QA mindset*: mind-maps for test scenarios complement charters.
