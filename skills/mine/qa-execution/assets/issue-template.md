# BUG-<num>: <short-title>

**Impact (user-side):** Blocks-Completion | Data-Loss | Trust-Damage | Friction | Cosmetic
**Severity:** Critical | High | Medium | Low
**Priority:** P0 | P1 | P2 | P3
**Type:** Functional | UI | Accessibility | Usability | Data | Crash
**Status:** pending | resolved | invalid
**Persona Affected:** <New User | Power User | Casual User | Mobile User | Accessibility-Reliant | Recovering User>
**Journey Step:** <J-NN journey name, Step N (verb)>

> Severity is the engineering-triage view. Impact is the user-side view. Both must be filled.
> See `references/bug-severity-by-user-impact.md` for the mapping rubric.
> Status values:
> - `pending` — issue is open and unresolved
> - `resolved` — fixed during this QA run and verified by re-run
> - `invalid` — triaged as non-actionable (not a defect, duplicate, environmental)

## Environment

- **Build:** <version or commit, production-parity status>
- **OS:** <operating system and version>
- **Browser:** <browser and version>
- **Viewport:** <width × height>
- **Network:** <wifi-fast | wifi-slow | 4g | 3g | flaky>
- **Locale:** <en-US | pt-BR | ...>
- **URL:** <page or endpoint where bug occurs>

## Summary

<Describe the observable failure from the persona's perspective in one short paragraph. What did the user try, what did they see, what did they expect?>

## Reproduction

Charter: <CH-NN that surfaced this, or "off-script" / "CFR pass" / "journey execution">
Tour: <if surfaced inside a tour, name it>

Steps:

1. <plain-language user action>
2. <plain-language user action>
3. <where it failed>

Observed:

- <what the user saw / heard / felt>
- <screenshot path>

## Expected

<Describe the correct user-side behavior. Cite the journey goal observable when relevant.>

## Root cause

<Describe the actual source of the failure (when known), not the symptom. Engineering fills this in during fix.>

## Fix

<Describe the production change that resolved the root cause. Engineering fills this in.>

## Verification

- <narrow reproduction rerun>
- <re-run of the affected journey from `references/journey-maps.md`>
- <CFR pass on the affected category, if applicable>

## Impact

- **Users Affected:** <all of <persona> | subset described | specific role>
- **Frequency:** <always | sometimes | rare>
- **Workaround:** <describe or "none">
- **Trust cost:** <one sentence on what this signals to the user about the product>

## Related

- Test Case: <TC-ID from qa-report, if applicable>
- Figma Design: <URL if UI bug>
- Related journeys: <J-NN list>
- Related charters: <CH-NN list>
