---
name: qa-report
description: >-
  Plans real-user QA as living repo docs. Owns the canonical <qa-docs-path>
  tree (default docs/qa/): state.csv scenario tracker, global bug registry with
  stable BUG-NNNN ids, project personas, journey flowcharts, session charters,
  coverage taxonomy, and automation backlog. Maps user-visible change as
  Mermaid journey flows BEFORE deriving scenarios, plans persona-driven
  session charters for the cycle, and enforces "every journey walked by a
  persona" completeness. Use when bootstrapping or updating a project's QA
  docs, planning a QA cycle before execution, or registering bugs into the
  durable registry. Do not use for live session execution, browser evidence
  capture, or fix loops; use qa-execution for those.
trigger: explicit
argument-hint: "[qa-docs-path]"
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Real-User QA Planner

Plan QA the way the product will actually be judged: as journeys real people walk, not as test cases that accumulate. This skill owns the project's **living QA docs** — one canonical tree that survives every QA round — and plans the persona-driven sessions that `qa-execution` runs.

Two rules define everything here:

1. **Living docs, not round artifacts.** All durable QA knowledge lives in one committed tree (`<qa-docs-path>`, default `docs/qa/`). Rounds append to it; they never create parallel trees, never reset ids, never overwrite history.
2. **Sessions, not cases.** The atomic planning unit is the **session charter** (persona + journey + tour + time-box), derived from journey flowcharts. Coverage means "every planned journey was walked by a persona this cycle" — never "every persona has N test cases".

## Required Reading Router

Match your task to the row. Read the listed files **in full before** producing the deliverable. They are not appendices — they are the contracts the deliverable must conform to. Inline content in this SKILL.md is a pointer, not a substitute.

| Task                                                       | MUST read                                              |
| ---------------------------------------------------------- | ------------------------------------------------------ |
| Bootstrapping or adopting the QA docs tree (Step 1)        | `references/qa-docs-layout.md`                         |
| Authoring or updating project personas (Step 2)            | `references/personas.md`                               |
| Mapping journeys and flowcharts (Step 3)                   | `references/journeys-and-flows.md`                     |
| Deriving scenarios and updating the tracker (Step 4)       | `references/state-schema.md` + `references/taxonomy.md`|
| Planning session charters for a cycle (Step 5)             | `references/session-charters.md`                       |
| Registering or updating bugs (Step 6)                      | `references/bug-registry.md`                           |
| Recording automation intent                                | `references/automation-backlog.md`                     |

## Reference Index

- `references/qa-docs-layout.md` — the canonical `<qa-docs-path>` tree, bootstrap procedure for new projects, adoption procedure for projects with existing scattered QA artifacts.
- `references/state-schema.md` — `state.csv` column schema, status enums, id minting, update rules, and the merge convention that keeps a shared CSV diffable.
- `references/bug-registry.md` — global `BUG-NNNN` registry: minting, dedup-before-file, bug statuses, and the five-tier user-impact rubric (the canonical severity model for both skills).
- `references/personas.md` — the seed persona catalog (New / Power / Casual / Mobile / Accessibility-Reliant / Recovering User) and how to derive project-specific personas into `<qa-docs-path>/personas.md`.
- `references/journeys-and-flows.md` — flows before matrix: journey anatomy, abandonment paths, Mermaid flowchart mapping, and how flows (not features) define what gets tested.
- `references/session-charters.md` — the charter as atomic unit, cycle planning, cadence tiers (smoke / targeted / full / sanity), and the coverage inversion.
- `references/taxonomy.md` — the five coverage dimensions every cycle must consider: journeys, functional, experiential, edge/error/empty, cross-cutting.
- `references/automation-backlog.md` — automation intent lives in ONE backlog doc, never as metadata attached to sessions.
- `assets/state.csv` — seed tracker (header + example row).
- `assets/bug-template.md` — seed bug file template (copied to `<qa-docs-path>/templates/bug.md` at bootstrap).
- `assets/charter-template.md` — seed charter template (copied to `<qa-docs-path>/templates/charter.md` at bootstrap).

## Required Inputs

- **qa-docs-path** (optional): Root of the living QA docs tree. Defaults to `docs/qa` at the repository root. This is a durable, committed location — never a temp dir. If the argument points outside the repository, confirm with the operator before proceeding: living docs outside the repo lose review, diff, and history.

## Procedures

**Step 1: Resolve or Bootstrap the QA Docs Tree**

1. Resolve `<qa-docs-path>` (argument or `docs/qa` default).
2. **STOP. Read `references/qa-docs-layout.md` in full before creating or modifying anything.** It owns the canonical tree and the bootstrap/adopt procedures.
3. If the tree exists, read `<qa-docs-path>/README.md` and `state.csv` first — every planning decision below builds on the existing state, never parallel to it.
4. If the tree does not exist, bootstrap it per the layout reference: create the directories, seed `state.csv` from `assets/state.csv`, copy the three templates into `<qa-docs-path>/templates/`, and write the project `README.md`.
5. If the repository has QA artifacts scattered outside the tree (old per-round `qa/` dirs, orphan bug files), follow the adoption procedure in the layout reference: index them, migrate durable knowledge, and never silently duplicate ids.

**Step 2: Establish Project Personas**

1. **STOP. Read `references/personas.md` in full before deriving or updating any persona.** The seed catalog and the derivation rules live there.
2. If `<qa-docs-path>/personas.md` exists, update it only when the product's audience changed. Personas are durable instance data — they persist across cycles.
3. If absent, derive 3-6 project personas from the seed catalog, adapted to the product's real audience, and write them to `<qa-docs-path>/personas.md`.

**Step 3: Map Journeys as Flows (before any scenario exists)**

1. **STOP. Read `references/journeys-and-flows.md` in full before mapping any journey.** The flow requirements summarized in point 3 below are a tripwire, not the contract.
2. Scope the mapping: for a branch/PR cycle, enumerate every **user-visible** change in the diff; for a release cycle, cover the product's high-value journeys.
3. For each journey, write or update `<qa-docs-path>/journeys/<journey-id>.md`: the YAML journey map plus a Mermaid flowchart covering entry → actions → branch points (validation error, empty state, permission denied) → side effects (emails, jobs, notifications) → the **true end state**, including at least one abandonment path.
4. Do not write a single scenario before the flow exists. Scenarios derived without a flow test pages; scenarios derived from flows test journeys — and the bugs that matter live between the pages.

**Step 4: Derive Scenarios into the Tracker**

1. **STOP. Read `references/state-schema.md` and `references/taxonomy.md` in full before minting an id or writing any row.** Column names and enums are exact — the schema owns them.
2. Walk each flowchart from Step 3 and derive scenarios: one `state.csv` row per scenario, with a stable `<AREA>-NNN` id minted per the schema rules. Check the five taxonomy dimensions so coverage is deliberate, not accidental.
3. Update existing rows in place (statuses, journey links); never re-create a row that already exists, and record overlaps in the `overlaps` column instead of duplicating.
4. Rows are planning output here — `qa_status` stays `untested` until `qa-execution` runs them.

**Step 5: Plan Session Charters for the Cycle**

1. **STOP. Read `references/session-charters.md` in full before writing any charter.** The charter fields named below are tripwires, not the contract.
2. Pick the cadence tier for this cycle (smoke / targeted / full / sanity) and select journeys accordingly.
3. Write one charter per session to `<qa-docs-path>/charters/CH-<NNN>.md` using the project template: mission, persona, journey, exactly one tour, time-box, must-try guidance.
4. Order charters by risk: highest-impact journey × highest-blast-radius tour first.
5. Every planned journey gets at least one charter with an assigned persona. That is the coverage bar — not case counts.

**Step 6: Register Bugs**

1. **STOP. Read `references/bug-registry.md` in full before minting any bug id.**
2. Before filing, dedup: search `<qa-docs-path>/bugs/` for an existing bug with the same symptom. Update the existing file instead of duplicating — a re-found bug is history worth keeping on one id.
3. Mint the next global `BUG-NNNN` from the registry (max existing + 1, never reset), write the bug file from the project template, and link the id into the affected `state.csv` rows (`bug_ids` column).

**Step 7: Validate Cycle Completeness**

Before handing off to `qa-execution`, verify — and record gaps honestly instead of padding:

1. Every journey in scope for this cycle has a flowchart with at least one abandonment path.
2. Every journey in scope has at least one charter with an assigned persona.
3. Every scenario row in scope has a stable id, a linked journey, and `qa_status` reflecting reality.
4. Every open bug has a registry file and appears in the `bug_ids` of at least one row.
5. The five taxonomy dimensions were considered — a skipped dimension is recorded with reasoning, not silently ignored.

Do NOT verify "every persona has N test cases" or any per-case count. Case accumulation is the failure mode this skill exists to prevent.

## Companion Skills

- **qa-execution** — Runs the sessions this skill plans and writes results back into the same `<qa-docs-path>` tree (statuses, bugs, reports). The living docs tree is the contract between the two skills.
- **agent-output-audit** — Owns CI verification gates, AI test-hygiene scans, and task-status reconciliation. Technical integration/security/performance suites route there or to dedicated tooling — never into this skill's plans.

## Error Handling

- If `<qa-docs-path>` cannot be created (permissions, read-only checkout), stop and surface the error. Never fall back to a temp directory — living docs in `/tmp` are the anti-pattern this skill replaces.
- If `state.csv` fails to parse (malformed row, wrong column count), stop and repair it first — every downstream step depends on the tracker being loadable. Report what was repaired.
- If two rows or two bug files claim the same id, treat it as data corruption: keep the older artifact as canonical, re-mint the newer one, and update references. Record the collision in `<qa-docs-path>/README.md` changelog.
- If the operator asks for technical test suites (integration, security, performance, load), route them to code tests, security review, or load tooling. Record the routing decision; do not absorb the work.
- If the diff for a branch cycle contains no user-visible change, say so and stop — there is nothing to dogfood. Do not invent scenarios to fill a cycle.
