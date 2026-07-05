# Plan: qa-report / qa-execution redesign (generic, session-centric, living docs)

Approved by Pedro on 2026-07-05. Research base: `.claude/research/qa-skills-revamp/analysis/` (6 slices + summary.md).

## Direction (approved)

- Skills are **generic** — AGH is one consumer. No AGH-specific constraints (memory directives, vocabulary, home policy, cy-qa-workflow plumbing) may shape the design. AGH adapts later.
- Keep the two-skill pair with a re-cut boundary:
  - **qa-report** = QA Planner & living-docs owner. Owns the canonical `docs/qa/` tree: state tracker CSV, global bug registry, personas, journey flows, session charters, taxonomy, automation backlog.
  - **qa-execution** = Dogfooding Session Runner. Runs persona-driven sessions through public interfaces, files bugs into the global registry, updates the tracker, writes incremental per-run reports.
- Dependency direction reversed: qa-execution links to qa-report references (one-way, zero duplication). qa-report stands alone.

## Core design decisions

1. **Living home**: `<qa-docs-path>` (default `docs/qa/` in the target repo; `/tmp` fallback removed). Durable knowledge is committed; bulky evidence is kept lean and indexed by path, never copied.
2. **Atomic unit = session charter** (persona + journey + tour + time-box + flow), not TC-* files. TC-* prefixes retired. Completeness = "every planned journey walked by a persona this cycle".
3. **Flows before matrix** (from ce-dogfood): map user-visible change as Mermaid journey flowcharts (entry → actions → branches → side effects → true end state), derive scenarios by walking flows.
4. **state.csv** generalized from feature-status.csv: stable `<AREA>-NNN` ids, enum-disciplined lifecycle columns, split `bug_ids`/`fix_commit`/`evidence` columns, prose only in `notes`, sorted-by-id merge convention.
5. **Global bug registry** `docs/qa/bugs/BUG-NNNN.md`: monotonic ids minted from registry max, never reset; dedup-before-file; 5-tier user-impact rubric (Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic) as the single severity model.
6. **6-value session status enum**: Pending | Pass | Fixed | Skipped | Blocked (needs human verify) | Blocked (human decision).
7. **Fix-loop governor** replaces fix-forward: auto-fix only small/contained/low-risk, regression test red-before/green-after, one logical fix per commit, re-run impacted + adjacent journeys; everything else → "Decisions for a Human". Exit gate: full automated suite once before Final Status.
8. **Persona-fidelity guardrails** (generalized from real-scenario-qa): in-persona interaction only via public interfaces, forbidden evaluator framings, no dev shortcuts to "verify", stall/error is an observation to record not a thing to patch around, evidence standard (action visible + independent read path + survives refresh/deep-link).
9. **Paper cuts**: experiential findings per persona with severity; sharp paper cuts enter the fix loop.
10. **Reports**: `docs/qa/reports/<YYYY-MM-DD>-<scope>.md` created as soon as the session matrix exists, updated incrementally, never overwritten across runs.
11. **Templates seeded into the project**: qa-report bootstrap writes `docs/qa/templates/{bug,report,charter}.md`; both skills prefer project-local templates, falling back to bundled assets.

## File plan

### skills/mine/qa-report/
- `SKILL.md` — rewrite (planner & registry owner; router; bootstrap/adopt procedure; cycle planning; completeness inversion)
- `references/qa-docs-layout.md` — canonical tree + bootstrap/adopt procedure
- `references/state-schema.md` — CSV columns, enums, update & merge rules
- `references/bug-registry.md` — minting, dedup, statuses, 5-tier impact rubric (canonical severity home)
- `references/personas.md` — persona authoring methodology (instance data lives in docs/qa/)
- `references/journeys-and-flows.md` — flows-before-matrix, journey anatomy, abandonment paths
- `references/session-charters.md` — charter as atomic unit, cycle planning
- `references/taxonomy.md` — 5-dimension coverage taxonomy
- `references/automation-backlog.md` — automation intent in one backlog doc
- `assets/state.csv` — header + example row (seed template)
- `assets/bug-template.md`, `assets/charter-template.md`
- DELETE: `scripts/create_bug_report.sh`, `scripts/generate_test_cases.sh`, all 9 old references, old asset `issue-template.md`

### skills/mine/qa-execution/
- `SKILL.md` — rewrite (session runner; reads docs/qa; governor; exit gate; writes back)
- `references/session-protocol.md` — persona session loop, evidence standard, paper cuts
- `references/persona-fidelity.md` — guardrails + forbidden framings + allowlist
- `references/tours.md` — 10-tour catalog (preserved content, canonical here)
- `references/edge-cases.md` — user edge-case catalog (technical pockets pruned)
- `references/lenses.md` — 6 experiential lenses (from cfr-checks, reframed as what a user feels)
- `references/fix-loop.md` — governor, regression-test-per-fix, exit gate
- `references/status-and-reporting.md` — enum, report lifecycle, tracker write-back, round-close checklist
- `assets/report-template.md` — 11-section dogfood report
- DELETE: `autoresearch-systematic-qa/` (fossil), old references (bug-severity-by-user-impact, cfr-checks, checklist, exploratory-charters, journey-maps, test-tours, user-edge-cases, user-personas, web-ui-qa), old assets (issue-template, verification-report-template)

### Repo
- Update `README.md` entries for both skills if descriptions are listed.

## Out of scope (AGH-side, later, by Pedro)
- real-scenario-qa absorption/retirement, agh-qa-bootstrap, cy-qa-workflow template, cy-tasks-tail-qa-pair, discover-project-contract.py, memory directive SD-012, migration of historical per-round trees.
