# Summary: qa-skills-revamp research round

## Research Question

> Map QA skills context: qa-report/qa-execution skills structure, real-scenario-qa complementary skill, AGH QA folder sprawl, feature-status.csv tracking pattern, docs/_memory specs about QA dogfooding

## Slice Map

| Slice | Question | One-line finding |
| --- | --- | --- |
| 01 – qa-report-skill | Structure, output contract, technical-case bias of qa-report | Rhetorically anti-technical, structurally test-case-centric: 9 TC-* prefixes as the atomic artifact, per-round `<qa-output-path>/qa/` tree, timestamp BUG IDs, zero cross-round primitives; deployed AGH copy byte-identical. |
| 02 – qa-execution-skill | Session workflow, output layout, divergences of qa-execution | Strongest real-user engine (persona×journey×charter×tour matrix) but no cross-round memory (BUG-NNN resets, `/tmp` fallback, report overwritten), fix-forward allowance breaks role fidelity; stray `autoresearch-systematic-qa/` fossil in skills repo; AGH-only `discover-project-contract.py` is a CI-gate vestige. |
| 03 – real-scenario-qa | Mechanisms that force real-user behavior | Enforces realism mechanically: playbook-as-product (fictional startup), single in-persona kickoff then observer silence, forbidden-phrase blocklist scanned by auditor (C15), non-markdown deliverable minimums (C16), collaboration gates (C17), stall-as-bug (C18) — but is itself a sprawl offender (qa-labs per-slug trees). |
| 04 – memory-specs | Standing constraints from docs/_memory | SD-005 defines the QA layering; hard constraints: home policy (L-016), parallel isolation (L-009), forensic-first evidence (SD-006), surface enumeration (L-011); "dogfood" absent from vocabulary (use "real-scenario QA"); committed `docs/qa/` crosses the "tracking artifacts stay local unstaged" line (P-T2.27) — needs an explicit class decision. |
| 05 – qa-artifact-sprawl | Inventory of QA artifact locations | ~9.5 GB / ~181k files across 5 artifact flavors; 29 archived per-round `qa/` trees; BUG-001 means 168 different bugs (no global registry); `feature-status.csv` is the only working cross-round tracker; trigger plumbing is `cy-tasks-tail-qa-pair` + `cy-qa-workflow` (`COMPOZY_QA_EVIDENCE_ROOT_TEMPLATE`). |
| 06 – csv-tracking-ce-dogfood | Target patterns: CSV tracker + ce-dogfood | CSV schema works but drifts (33 distinct qa_status values, packed evidence cells, merge-fragile single file); ce-dogfood wins on flows-before-matrix, 5-dimension taxonomy, persona paper cuts, fix-loop governor, 6-value status enum, durable per-run report created at matrix time. |

## Convergences

- **Per-round isolated output is the root cause of the sprawl.** qa-report mandates a fresh tree per run with no append path (01); qa-execution has zero cross-round memory and defaults to `/tmp` (02); real-scenario-qa materializes a new lab per slug (03); the result is 29 archived trees + 30 labs with colliding IDs (05). All four slices independently converge: the fix is a canonical durable home plus per-run evidence that is *indexed, not copied*.
- **The skills talk real-user but count test cases.** The TC-* file is the atomic artifact and Step 8 enforces "every persona has ≥1 TC" (01); qa-execution retains technical pockets (CRUD/boundary checks in web-ui-qa.md) and a fix-forward allowance (02); real-scenario-qa exists precisely because that structural bias kept producing evaluator-shaped output (03); the memory's L-018 confirms "PASS is not evidence" (04).
- **feature-status.csv is the proven tracking pattern to generalize.** 05 identifies it as "the exception that works"; 06 dissects its schema and its failure modes (free-text drift, packed evidence, merge fragility); 04 supplies the lessons-registry structure (index + one-file-per-case) as the repo's own living-doc precedent.
- **Enforcement must be mechanical, not prose.** Forbidden-phrase auditor + deliverable/collaboration/stall checks (03), the `cy-qa-workflow` audit hook seam (05), ce-dogfood's fix-loop governor and "green matrix with a red suite is not ready" exit gate (06), SD-006 forensic-first reproduction (04).
- **Reference duplication between qa-report and qa-execution.** 5 of qa-report's 9 references defer canonically to qa-execution while restating planning views; the surface→tour matrix and persona YAML schema physically duplicate (01, 02). Both slices recommend a single canonical home.
- **Stable global IDs are a precondition for centralization.** Timestamp BUG IDs (01), per-run BUG-NNN resets (02), 85 distinct BUG- ids where BUG-001 names 168 different bugs (05), CSV's BUG-NNN join key threading 4 lifecycle columns (06).

## Divergences

- **One skill or two (or four)?** ce-dogfood merges planning + execution + fix into one 7-phase skill (06); the current design splits planning (qa-report) and execution (qa-execution) (01, 02); AGH practice layers real-scenario-qa on top, delegating to the pair, plus agh-qa-bootstrap for labs (03, 04-SD-005). No slice resolves the topology; SD-005 mandates the pair exists as task tail, which constrains full merging.
- **Fix during QA?** qa-execution half-allows bounded fixes (02); real-scenario-qa forbids the observer from touching anything (03); ce-dogfood embraces an auto-fix loop bounded by a governor with regression-test-per-fix (06). Three incompatible postures — a deliberate design decision is required.
- **Committed living docs vs local-unstaged tracking.** 05 and 06 recommend promoting the CSV + plans + bug registry into a committed `docs/qa/`; 04 flags P-T2.27 ("tracking artifacts stay local unstaged") as a class barrier requiring an explicit new posture (e.g., an SD-012) before committing QA state.
- **Vocabulary.** The external pattern says "dogfood" (06); the project memory exclusively says "real-scenario QA" and never uses "dogfood" (04).
- **Browser availability.** ce-dogfood presumes agent-browser + dev server (06); AGH QA evidence shows 27+ CSV rows blocked on exactly that (06-Risks), while qa-execution's Step 4 already assumes agent-browser (02).

## Risks & Open Questions (consolidated)

1. **Class decision (blocking):** is `docs/qa/` a committed living doc or a local tracking artifact? Requires a standing-directive-level decision; without it the redesign silently violates recorded convention (04).
2. **ID migration integrity:** naive concatenation of per-round BUG-/TC- IDs corrupts a global registry; must mint stable global IDs and record per-round aliases (05).
3. **Fix-loop topology:** remove fix-forward, fence it, or adopt ce-dogfood's governor? Also conflicts with SD-004 (subagents read-only by default) (02, 03, 04, 06).
4. **Journey-log dependency:** real-scenario-qa's observer/auditor need the product to emit structured journey events; a generalized skill needs an equivalent event contract per product (03).
5. **Enum discipline:** define canonical status enums per lifecycle column before migrating CSV history (33→6-ish values) (06).
6. **agent-browser gating:** real-browser dogfooding is partially inert until the browser env + dev-server command are wired (06).
7. **Home policy + parallel isolation must not regress** (L-016, L-015, L-009) in any new bootstrap/lab logic (04).
8. **Scope exclusions for docs/qa:** codex-loop peer-review JSONL and `.codex/loop/*` are NOT QA evidence; qa-labs (8.1 GB) and `final-qa/_runs/` (1.2 GB) must be indexed, never moved (05).
9. **Which copy is canonical for a round's evidence** when both `<workflow>/qa/` and lab-side `qa-artifacts/qa/` exist with the same run ID (05).
10. **Stray artifacts:** delete/relocate `autoresearch-systematic-qa/` from the skills repo; decide fate of AGH-only `discover-project-contract.py`; retire `init-scenario-workspace.sh` and the interactive bash wizards (01, 02, 03).

## Recommended Next Steps

1. **Decide the docs/qa class posture first** (new standing directive distinguishing committed QA living docs from per-run tracking artifacts) — supported by 04, 05, 06.
2. **Define the canonical `docs/qa/` layout** — tracker CSV with disciplined enums + stable BUG registry + plans + taxonomy + per-run reports dir; index (don't move) bulk evidence — supported by 05, 06.
3. **Re-cut the two skills around sessions, not cases:** qa-report becomes the living-docs planner/registry owner (charters/journeys as atomic units, TC-* demoted); qa-execution becomes the dogfooding session runner adopting flows-before-matrix, persona paper cuts, the 6-value enum, and the exit gate — supported by 01, 02, 06.
4. **Absorb real-scenario-qa's enforcement guardrails** (forbidden-phrase blocklist retuned to the new vocabulary, evidence auditor, kickoff-then-silence for observer-mode runs) into the redesigned pair — supported by 03.
5. **Honor the memory's hard constraints** (home policy, parallel isolation, forensic-first, surface enumeration, "real-scenario QA" vocabulary) — supported by 04.
6. **Update trigger plumbing** (`COMPOZY_QA_EVIDENCE_ROOT_TEMPLATE`, `cy-tasks-tail-qa-pair`, audit hook) so rounds cannot close without a tracker row — supported by 05.
7. **Clean the fossils** (stray dirs, wizards, vestigial scripts) in the same change per SD-002 hard-cut — supported by 01, 02, 03, 04.

## Index

- `/Users/pedronauck/Dev/compozy/skills/.claude/research/qa-skills-revamp/analysis/01_analysis_qa-report-skill.md`
- `/Users/pedronauck/Dev/compozy/skills/.claude/research/qa-skills-revamp/analysis/02_analysis_qa-execution-skill.md`
- `/Users/pedronauck/Dev/compozy/skills/.claude/research/qa-skills-revamp/analysis/03_analysis_real-scenario-qa.md`
- `/Users/pedronauck/Dev/compozy/skills/.claude/research/qa-skills-revamp/analysis/04_analysis_memory-specs.md`
- `/Users/pedronauck/Dev/compozy/skills/.claude/research/qa-skills-revamp/analysis/05_analysis_qa-artifact-sprawl.md`
- `/Users/pedronauck/Dev/compozy/skills/.claude/research/qa-skills-revamp/analysis/06_analysis_csv-tracking-ce-dogfood.md`
