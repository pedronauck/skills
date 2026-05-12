# User Personas

A persona is the answer to *"who am I being right now while I test this?"* A real-user QA session without a persona drifts into developer mindset — testing what the system can do instead of what a user would actually try.

This reference defines the canonical persona set, their attributes, and how to assign one to each charter (`exploratory-charters.md`) and journey (`journey-maps.md`).

## Contents

- Why personas
- Canonical persona set (New User / Power User / Casual User / Mobile User / Accessibility-Reliant / Recovering User)
- Persona attributes for QA notes (YAML schema)
- Picking the right persona for a charter (surface-to-persona matrix)
- Anti-patterns
- Sources

## Why personas

- A test session run as "anyone" optimizes for the tester's reflexes, not the user's needs.
- Different personas surface different defects: a new user finds onboarding friction; a power user finds keyboard-shortcut bugs; a mobile user finds touch-target failures.
- Personas force you to stay in role — when you catch yourself fixing the test instead of reporting the bug, the persona is the leash.

## Canonical persona set

Pick at least one persona before any QA session begins. For a release-candidate QA pass, cover **at least 3** personas across the planned sessions.

### New User (first-time visitor)

- **Familiarity:** zero. Has not seen the product before.
- **Motivation:** evaluating whether to use it; will leave if confused within 60 seconds.
- **Device:** whatever they happened to be on — often mobile.
- **Patience:** very low. A spinner over 3 seconds feels broken; an unclear error sends them to a competitor.
- **What they reveal:** onboarding gaps, missing empty-state guidance, confusing copy, unclear primary action, broken first-impression flows.

### Power User (returning expert)

- **Familiarity:** uses the product daily. Knows shortcuts, edge features, and how to "abuse" the UI.
- **Motivation:** ship work fast. Will tolerate ugly UI if it's efficient.
- **Device:** desktop, keyboard-driven, multiple tabs open.
- **Patience:** zero for regressions on speed; high for visual rough edges.
- **What they reveal:** keyboard shortcut breakage, regressions on bulk operations, performance degradations, state-loss across tabs, undo/redo bugs, autocomplete failures.

### Casual User (returning, infrequent)

- **Familiarity:** has used the product a few times. Remembers the goal, not the steps.
- **Motivation:** complete a specific task and leave.
- **Device:** mixed. Often switching between phone and laptop mid-task.
- **Patience:** moderate. Tolerates load if the goal is in sight.
- **What they reveal:** discoverability issues ("where did that button go?"), session continuity across devices, save-and-resume bugs, half-remembered shortcuts that no longer work.

### Mobile User (touch-first)

- **Familiarity:** any. Defined by device, not history.
- **Motivation:** quick action — often in transit, often with one hand.
- **Device:** small viewport, touch, possibly slow network, possibly with notch/safe-area cutouts.
- **Patience:** low. Will close the tab on a layout shift.
- **What they reveal:** touch-target size, layout breaks at 375px, sticky elements covering content, autofocus stealing input, unintended zoom, gesture conflicts, network-failure handling.

### Accessibility-Reliant User (assistive tech)

- **Familiarity:** any. Defined by interaction modality.
- **Motivation:** use the product on equal terms with sighted/mouse users.
- **Device:** screen reader (VoiceOver / NVDA / TalkBack), keyboard only, magnifier, voice control, or high-contrast mode.
- **Patience:** task-bounded. Will abandon if the screen reader announcement is incomprehensible.
- **What they reveal:** missing ARIA labels, focus traps, broken tab order, color-only signaling, missing alt text, modal escape failures, dynamic content not announced, contrast failures.

### Recovering User (returning after problem)

- **Familiarity:** any. Defined by emotional context — last visit ended badly.
- **Motivation:** see if it's been fixed; trust is fragile.
- **Device:** often the same device that experienced the failure.
- **Patience:** very low. Any sign of the previous failure causes immediate abandonment.
- **What they reveal:** stale error states, cached failure screens, unresolved data corruption, half-applied fixes, "we're sorry" pages that loop back to the same error.

## Persona attributes for QA notes

When recording session output, capture the persona row alongside every test case and bug:

```yaml
persona:
  name: <New User | Power User | Casual User | Mobile User | Accessibility-Reliant | Recovering User>
  familiarity: <zero | familiar | expert>
  motivation: <evaluate | complete-task | ship-work-fast | one-handed-action | use-on-equal-terms | trust-check>
  device: <desktop | laptop | tablet | phone-small | phone-large>
  network: <wifi-fast | wifi-slow | 4g | 3g | flaky>
  modality: <mouse-keyboard | touch | screen-reader | keyboard-only | voice>
  locale: <en-US | pt-BR | de-DE | ...>
  patience_seconds: <how long they wait before abandoning>
```

The bug report's `Persona Affected:` field uses the same `name` value.

## Picking the right persona for a charter

Match the persona to the surface under test:

| Surface | Mandatory persona | Recommended additional |
|---|---|---|
| Onboarding / first-run | New User | Mobile User |
| Settings / account | Casual User | Power User |
| Bulk operations / dashboards | Power User | Casual User |
| Mobile-only feature | Mobile User | Accessibility-Reliant |
| Recovery / error pages | Recovering User | New User |
| Public marketing / landing | New User | Accessibility-Reliant |
| Form-heavy flow | Casual User | Mobile User (autofill) |
| Multi-step wizard | New User | Power User (skip patterns) |

When in doubt, ask: *"who is most likely to be hurt by this surface failing?"* — that's the mandatory persona.

## Anti-patterns

- **"Just a user"** — generic personas produce generic tests. Pick one of the six above.
- **Persona-of-convenience** — picking the persona that matches what you already want to test. Inverts the practice: pick the persona, then let it pick the test.
- **Single-persona-per-release** — release-candidate QA should cover at least 3 personas across the planned sessions; otherwise large user segments go unverified.
- **Mixing personas mid-charter** — switch costs are real. Run one persona to completion before changing; record the switch in the charter debrief.

## Sources

- Testlio — *Exploratory Testing 101: Step 3 — Adopt User Personas and Pair Testing*. The "new user / power user / casual user" tri-persona model originates in this guide.
- Thoughtworks — *10 tips for an Agile QA mindset, Tip 7 (Cross-Functional Requirements)*: persona-aware testing surfaces UX/usability/accessibility/compatibility CFRs that scripted tests miss.
- Sahipro — *Exploratory Testing Best Practices*: persona adoption as Step 3 of structured exploratory testing.
