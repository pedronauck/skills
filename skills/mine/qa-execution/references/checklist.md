# Real-User QA Checklist

Mark every item as complete before claiming the QA pass is done. Categories mirror the procedures in SKILL.md. Skipping any category requires explicit reasoning in the verification report.

## Persona Coverage

- [ ] At least 3 personas were assigned across the planned sessions (see `references/user-personas.md`)
- [ ] Each charter has exactly one persona assigned and the tester stayed in role
- [ ] At least one Accessibility-Reliant persona session was attempted (or skip reasoning documented)
- [ ] At least one Mobile User session was attempted when the product has a mobile surface
- [ ] Persona attributes (familiarity, motivation, device, network, modality, locale) are recorded for every session

## Journey Coverage

- [ ] 3-7 high-value journeys were identified for this release-candidate (`references/journey-maps.md`)
- [ ] Every journey names its **value** (not just its steps) and its **goal observable**
- [ ] Every journey has at least one **abandonment path** documented
- [ ] Cross-feature journeys are marked and prioritized
- [ ] Every journey was executed end-to-end with screenshots at each step

## Charter Coverage

- [ ] Every charter has mission + persona + surface + tour + time-box recorded (`references/exploratory-charters.md`)
- [ ] Time-boxes were honored — no charter ran past its box
- [ ] Each charter ended with a debrief written within 5 minutes of the box ending
- [ ] Each charter's findings are linked to filed bugs
- [ ] Each charter's debrief named a suggested next charter

## Off-Script & Edge Case Coverage

- [ ] At least one off-script tour was executed per major surface (`references/test-tours.md`)
- [ ] User edge cases relevant to each surface were attempted (`references/user-edge-cases.md`)
- [ ] Navigation edges (refresh-during-submit, back-after-success, deep-link-mid-flow) covered for multi-step flows
- [ ] Form edges (double-click, autofill, paste-from-Word) covered for input-heavy surfaces
- [ ] Session edges (expiry mid-form, multi-tab, logout-in-another-tab) covered for auth-bearing surfaces
- [ ] Network edges (Slow 3G, offline mid-submit) covered for any I/O-bearing surface
- [ ] Locale edges (non-en-US language, RTL, timezone) covered when the surface renders text or dates

## CFR Coverage

Run a 45-minute CFR pass covering at least 2 journeys (`references/cfr-checks.md`):

- [ ] Usability (Nielsen short list) — pass / friction / fail recorded per heuristic
- [ ] Accessibility (WCAG AA quick check) — keyboard, screen reader, visual
- [ ] Perceived performance — feedback within targets (paint, interactive, spinner, button)
- [ ] Compatibility — smoke across Chrome + Safari + Firefox + iOS Safari + Android Chrome
- [ ] Error recoverability — every failure path tested has an actionable recovery UX
- [ ] Production parity — no incognito-only tests; cookies enabled; realistic extension set

## Bugs Filed by User Impact

- [ ] Every bug is classified by user-impact tier (`references/bug-severity-by-user-impact.md`)
- [ ] Every bug has `Persona Affected:` and `Journey Step:` fields filled in
- [ ] `Blocks-Completion` and `Data-Loss` bugs on P0 journeys are flagged as release blockers
- [ ] Multiple `Trust-Damage` findings on the same journey were called out in the verification report

## Browser Evidence

When Web UI flows were tested (`references/web-ui-qa.md`):

- [ ] Dev server was reachable in a production-parity build before any test ran
- [ ] Each journey followed the open/snapshot/interact/re-snapshot/verify loop
- [ ] Screenshots were captured at every verification checkpoint and stored in `<qa-output-path>/qa/screenshots/`
- [ ] Each journey's screenshot set includes start, mid-flow decision point(s), and goal-achieved frame
- [ ] Responsive behavior was tested at 1280 / 768 / 375 viewports for surfaces with layout changes
- [ ] Authentication flow was exercised or state was loaded; same auth path real users will take
- [ ] Browser sessions were closed after all flows completed

## Final Verification Report

- [ ] Report produced from fresh evidence at `<qa-output-path>/qa/verification-report.md`
- [ ] Persona Coverage section lists every persona × journey × charter combination
- [ ] Journey Execution Log includes per-step verdicts and screenshot paths
- [ ] Charter Log includes mission, time-box, debrief, and suggested-next for every charter
- [ ] Off-Script Findings section names each edge case attempted and its outcome
- [ ] CFR Findings section gives pass/friction/fail per CFR category per journey
- [ ] Browser Evidence section captures dev server URL, flows tested, viewports, auth method, blocked flows
- [ ] Issues Filed section rolls up by user-impact tier and by legacy severity
- [ ] Blocked sessions or missing prerequisites are disclosed explicitly with the exact gap

## What this checklist deliberately omits

These belong to the `agent-output-audit` companion skill, not real-user QA:

- CI verification gate execution (lint, build, unit, integration baseline)
- Task implementation matrix and frontmatter status reconciliation
- AI test-hygiene red flag scans (RF-1..RF-6)
- Independent evaluator protocol for AI transcripts
- Flaky test triage and quarantine workflow
- Compozy `state.yaml` / `task_NN.md` interactions

If a real-user QA session uncovers a finding that requires one of these, file the bug and recommend the right skill, but don't pivot mid-session.
