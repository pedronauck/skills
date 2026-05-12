# Test Tours Catalog — Planning Reference

This file is the planning view of the test tour catalog. The **canonical tour definitions** (themes, off-script actions, what to look for, sample evidence) live in `../qa-execution/references/test-tours.md`. Read both before generating a TC-TOUR-*.

To avoid drift, this file does **not** duplicate the canonical definitions. It provides the surface-to-tour selection matrix and the planning-side reminders.

## Tour selection matrix

For each surface in your test plan, pick a first-choice tour and (optionally) a second-choice tour for a follow-up charter:

| Surface | First-choice tour | Second-choice tour |
|---|---|---|
| Onboarding / signup | Feature Tour | Network Tour |
| Checkout / payment | Money Tour | Network Tour |
| Settings | Back-Button Tour | Multi-Tab Tour |
| Bulk operations | Garbage Tour | Multi-Tab Tour |
| Forms (any) | Autofill Tour | Paste Tour |
| Search / filter | Garbage Tour | Locale Tour |
| File upload | Network Tour | Garbage Tour |
| Wizard / multi-step | Back-Button Tour | Interrupt Tour |
| Mobile-only flow | Interrupt Tour | Network Tour |
| International rollout | Locale Tour | Paste Tour |
| Recovery / error page | Back-Button Tour | Network Tour |

## TC-TOUR-* one-per-tour rule

A TC-TOUR-* binds **exactly one tour** to **exactly one surface × persona** with a time-box. Running two tours in one box dilutes both — split them into separate charters.

## Persona × Tour pairing hints

Some tours work better with certain personas:

| Tour | Best persona | Why |
|---|---|---|
| Feature Tour | New User | First-time visitor surfaces missing onboarding affordances |
| Money Tour | Power User | Power Users hit edge billing paths real users don't reach |
| Garbage Tour | Power User | Power Users naturally paste large/messy data |
| Back-Button Tour | Casual User | Casual Users use back as their primary navigation |
| Multi-Tab Tour | Power User | Power Users live in many tabs |
| Network Tour | Mobile User | Mobile users hit flaky networks daily |
| Locale Tour | International persona (any locale ≠ en-US) | Surfaces translation, RTL, timezone bugs |
| Paste Tour | Casual User | Casual Users copy-paste from external apps |
| Autofill Tour | Returning user (any) | Autofill state is non-empty for returning users |
| Interrupt Tour | Mobile User | Mobile users get interrupted (calls, notifications, app-switch) |

## What this file deliberately omits

These live in `../qa-execution/references/test-tours.md` and must be read there:

- The theme statement for each tour.
- The off-script actions to attempt.
- The "what to look for" list per tour.
- The sample evidence to capture.
- Anti-patterns per tour.

Duplicating any of those here would cause drift. Use the canonical file.

## Planning-side reminders

- One tour per charter; one charter per TC-TOUR-*.
- Time-box governs. If the tour's bullet list isn't fully exercised at box end, file a follow-up charter — don't extend.
- Bullets in the canonical catalog are **prompts**, not a checklist. The mission is *to find bugs in the theme*, not to execute every bullet.
- If you find yourself inventing a tour mid-session (e.g., "double-tap then refresh"), note it in the debrief and propose it for the canonical catalog. Do not pivot mid-box.

## Sources

- `../qa-execution/references/test-tours.md` — canonical tour catalog (this file's source of truth).
- Testlio — *Exploratory Testing 101: Going Off-Script*.
- James Whittaker — *Exploratory Software Testing*: original "tour" framing modernized in the canonical catalog.
