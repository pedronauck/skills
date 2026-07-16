# Output Contracts

Exact templates for every artifact. Placeholders in `<angle brackets>`; keep section order and marker strings byte-stable — fingerprints and upserts depend on them. walkthrough.md is orchestrator-authored; review.md and state.json are rendered from findings.json by `scripts/render_review.py`, which implements these templates and the verdict rule — this file is the contract it must keep.

## walkthrough.md

```markdown
<!-- deep-review:walkthrough -->
## Walkthrough

<one dense paragraph: what the change does across the stack, in prose>

## Changes

| Cohort / File(s) | Summary |
| --- | --- |
| **<cohort name>** <br> `<path>`, `<path>`, `<dir>/{a,b}.go` | <what changed there, 1–2 sentences> |

## Sequence Diagram(s)

<only when the change alters a multi-actor flow (request path, event flow, lifecycle);
one mermaid sequenceDiagram per flow, actors = real components>

## Estimated code review effort

🎯 <1-5> (<label>) | ⏱️ ~<minutes> minutes

## Review details

- **Scope**: <base sha short> → <head sha short> (<incremental round N | full review>)
- **Files**: <n> selected · <n> ignored by filters · <n> skipped (trivial/similar)
- **Profile**: <chill|assertive> · **Mode**: <workflow|agent-fallback|subagent:runtime>
- **Rubric**: <sources consulted, comma-separated paths>
- **Linters**: <lane: ran/unavailable, ...>
```

Effort scale (calibrate on *reviewable surface* — selected source, not raw file count):

| 🎯 | Label | ⏱️ | When |
| --- | --- | --- | --- |
| 1 | Trivial | ~5 min | mechanical or config-only |
| 2 | Simple | ~12 min | small localized change |
| 3 | Moderate | ~25 min | one subsystem, some cross-file reasoning |
| 4 | Complex | ~60 min | multiple subsystems or a contract change |
| 5 | Critical | ~120 min | core invariants, storage, security, or wide blast radius |

## Finding block (used in review.md and PR comments)

```markdown
_<category badge>_ | _<severity badge>_[ | _<effort badge>_]

**<Imperative one-line claim ending in a period.>**

<Evidence paragraph: the concrete failure mode or improvement, referencing real
symbols and line numbers. State what happens, under which input/state, and why.>

[Also applies to: <path>:<lines>, <path>:<lines>]
[As per coding guidelines [R<NN>] (`<source path>`): "<verbatim rule>"]
[Verification: <first evidence[] entry — command or file:line → what it showed>]

<details>
<summary>📝 Committable suggestion</summary>

> ‼️ **IMPORTANT**: review before committing — generated against lines <X>–<Y>.

```suggestion
<exact replacement for lines X–Y, only when the fix is mechanical and complete>
```
</details>

<details>
<summary>🤖 Prompt for AI Agents</summary>

```
Verify this finding against the current code and fix it only if still valid.
In <path> around lines <X>-<Y>, <imperative remediation steps naming exact
symbols and the target behavior>. Reference symbols: <sym1>, <sym2>.
```
</details>
<!-- deep-review:fp:<fingerprint> -->
```

Bracketed lines appear only when they apply. The committable `suggestion` block only when the replacement is exact and self-contained; otherwise nothing. The AI-agents prompt only on **Critical and Major** findings.

## review.md

```markdown
# Deep Review — <target> (round <N>)

**Verdict: <SHIP | FIX_BEFORE_SHIP | REWORK>** — <one-line rationale>
**Actionable findings: <n>** (🔴 <n> · 🟠 <n> · 🟡 <n>) · nitpicks: <n> · duplicates: <n> · resolved since last round: <n> · merged duplicate reports: <n>

<walkthrough.md content, inlined>

## Findings

### <path>

<finding blocks for this file, severity-descending>

## Outside diff range

<finding blocks with in_diff: false, grouped per file; "None.">

## Spec conformance

<only with --spec; one row per contract artifact from the context pack:>
| Artifact | Assessment |
| --- | --- |
| `<path>` | conforms — no divergence found \| <n> violation(s): <finding claims> |

## Duplicates (unresolved from round <N-1>)

<one-line entries: badge · claim · original round; "None.">

## Nitpicks

<details><summary>🧹 <n> nitpicks</summary>
<compact one-liners: `path:line` — claim [— suggestion]>
</details>
```

`review.md` orders files by max severity, then path.

## ReportFindings mapping

When the harness exposes the ReportFindings tool, call it once after review.md is written: one entry per actionable finding, ranked most-severe first — `file`/`line` from the anchor, `summary` = the claim line, `failure_scenario` = the evidence paragraph's failure mode, `category` = kebab-case (`potential-issue`, `refactor`, `nitpick`). Omit `verdict` — no separate verify pass runs; the reviewer's own `evidence[]` is the confidence signal.

## Verdict rule

Derive after Step 4's merge from the open findings:

- **SHIP** — no Critical or Major open; Minors and nitpicks ship as follow-ups. With `--spec`: additionally requires the Spec conformance section complete (every artifact assessed) with zero open parity violations — a review that never assessed conformance cannot SHIP.
- **FIX_BEFORE_SHIP** — at least one open Critical/Major, and remediation is local: the change's shape is right and each finding names a bounded fix.
- **REWORK** — the findings show structural failure needing redesign (often a new TechSpec): a parity violation the implementation approach cannot express, the same root cause reported across ≥ 3 cohorts, or a Critical whose fix rewrites the change's core. REWORK always carries a named rationale in the verdict line; when no structural trigger holds, FIX_BEFORE_SHIP is the ceiling.

The verdict lands in review.md's header line, the round's state.json entry, and the final message. render_review.py derives SHIP / FIX_BEFORE_SHIP mechanically (open = findings with round status new or duplicate) and only accepts REWORK through `--rework "<rationale>"`; it rejects a report whose verdict contradicts the open findings.
