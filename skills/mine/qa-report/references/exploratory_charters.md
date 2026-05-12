# Exploratory Charters — Planning Reference

This file is the planning view of exploratory testing. The canonical charter format, mode definitions, time-box guidance, and debrief structure live in `../qa-execution/references/exploratory-charters.md`. Read both before drafting a TC-CHARTER-*.

## Contents

- What a charter is in planning
- Charter modes (Freestyle / Strategy-Based / Scenario-Based / Collaborative / Charter-With-Tour)
- TC-CHARTER-* drafting checklist
- Worked examples by surface (auth, checkout, search, file upload, settings)
- Anti-patterns
- Charter draft → execution handoff
- Sources

## What a charter is in planning

In planning, a charter is a **commitment**: who tests what, for how long, in which mode, looking for what. The charter draft lives at `<qa-output-path>/qa/test-plans/charters/CH-<NN>-<slug>.md` until `qa-execution` picks it up.

The charter format is the same as in execution — planning just produces the draft; execution adds the debrief.

## Charter modes (pick before writing)

Five modes. Each has its own use case:

| Mode | Use when | Time-box default |
|---|---|---|
| Freestyle | New surface, edge cases not yet understood | 30 min |
| Strategy-Based | Input-heavy or stateful feature | 60 min |
| Scenario-Based | Validating a journey under realistic conditions | 60 min |
| Collaborative (pair/mob) | Cross-team feature, onboarding a tester | 90 min |
| Charter-With-Tour | Default for any other case | 60 min |

When in doubt, pick Charter-With-Tour with a 60-min box — most productive depth-vs-fatigue balance.

## TC-CHARTER-* drafting checklist

Before saving a charter draft to `charters/CH-<NN>-<slug>.md`:

- [ ] **Mission** is one sentence in user terms (not "test the login form" — *"verify a new user with flaky 4G can sign in within 60 seconds without a password manager"*).
- [ ] **Persona** is one of the six canonical personas (see `../qa-execution/references/user-personas.md`).
- [ ] **Surface** names the feature/area; **Entry URL** is filled.
- [ ] **Out-of-scope** explicitly lists what the tester should **not** drift into.
- [ ] **Tour** is exactly one (see `test_tours_catalog.md`).
- [ ] **Time-box** is 30 / 60 / 90 minutes; longer than 90 is forbidden.
- [ ] **Must try** lists 2-4 specific things to attempt (avoid generic prompts).
- [ ] **Must avoid** lists any known-broken areas.

## Worked examples by surface

### Auth — sign in / sign up

**CH-01 (New User × Feature Tour × 30min):**
*"Verify a brand-new visitor on a phone with flaky 4G can complete signup and reach the dashboard within 3 minutes without consulting external help."*

**CH-02 (Recovering User × Back-Button Tour × 30min):**
*"Verify a user who hit yesterday's verify-email bug can return today, see clean state, and complete signup successfully."*

### Checkout / payment

**CH-03 (New User × Money Tour × 60min):**
*"Find any way to cause a double-charge, ghost order, or silent payment failure during first-time mobile checkout with a card requiring 3DS."*

**CH-04 (Mobile User × Network Tour × 60min):**
*"Verify the checkout flow is recoverable when the network drops at the payment-confirm step on mobile Safari."*

### Search / filter

**CH-05 (Casual User × Garbage Tour × 60min):**
*"Stress the search input with copy-paste from external apps (Word, Excel, markdown), emoji, RTL text, and very long queries. Find anything that silently fails or corrupts results."*

**CH-06 (Mobile User × Locale Tour × 30min):**
*"Switch to pt-BR with timezone São Paulo. Search for date-sensitive content. Find any locale-specific layout breaks or date-format bugs."*

### File upload

**CH-07 (Power User × Garbage Tour × 60min):**
*"Upload 0-byte, 1GB, wrong-MIME, executable, and emoji-named files. Find any state where the UI says 'success' but the file is missing or corrupted."*

**CH-08 (Mobile User × Interrupt Tour × 60min):**
*"Start a large upload on mobile, lock the phone for 5 minutes, return. Repeat with airplane-mode toggle. Find any silent upload failures."*

### Settings

**CH-09 (Casual User × Back-Button Tour × 30min):**
*"Verify every settings save can be undone via back button without losing user input or stranding the user mid-flow."*

**CH-10 (Power User × Multi-Tab Tour × 60min):**
*"Open settings in two tabs, edit different fields in each, save both. Find any lost-update bugs or stale-state confusion."*

## Anti-patterns

- **No mission** — a charter without a one-sentence mission is just unstructured exploration. Add the mission first.
- **Mission too broad** — *"Test the whole app"* is not a mission. Constrain by surface + persona + tour.
- **Multiple tours** — running Feature Tour + Garbage Tour + Locale Tour in one box dilutes all three.
- **Persona-of-convenience** — picking the persona that matches what you already want to test. Invert: pick persona, then let it pick the test.
- **No out-of-scope** — without explicit boundaries, charters drift into adjacent surfaces and the debrief becomes useless.

## Charter draft → execution handoff

Once `qa-execution` picks up the charter:

1. Tester reads the draft and confirms they understand the mission and out-of-scope.
2. Time-box starts; tester executes as the persona.
3. At box end, tester writes the debrief (started/ended/findings/bugs/surprises/suggested-next) into the same file.
4. Filed bugs reference `CH-NN` in the `Reproduction:` section of `assets/issue-template.md`.

## Sources

- `../qa-execution/references/exploratory-charters.md` — canonical charter format (this file's source of truth).
- Testlio — *Exploratory Testing 101: Charter-Based and Time-Boxed Testing*.
- Sahipro — *Exploratory Testing Process: Create Test Charter, Set Time Box, Review Results*.
- TestCollab — *Software Testing Strategies for QA Teams in 2026*: "skilled exploratory testers use charters, time-boxes, and structured note-taking".
