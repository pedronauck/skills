# Finding Taxonomy

The grammar every finding carries, the gates that decide what gets reported, and the suppression rules that keep the review high-signal. Reviewer and sweep prompts embed this file.

## Badge grammar

Every finding renders a badge line of italic, pipe-separated segments — category, severity, then the optional effort modifier:

```
_⚠️ Potential issue_ | _🟠 Major_ | _⚡ Quick win_
```

## Categories

| Badge | Meaning | Decision rule |
| --- | --- | --- |
| `⚠️ Potential issue` | Correctness, security, data loss, races, resource leaks, broken contracts | The code can produce a wrong result, crash, leak, or vulnerability under a concrete input/state. Name that failure mode. |
| `🛠️ Refactor suggestion` | Design or maintainability improvement, not a bug | The code works but a specific structural change measurably improves it (dedup, decompose, correct layer). |
| `🧹 Nitpick` | Clarity, naming, docs, small idiom | Cheap to fix, low stakes. Never rendered inline — collapsed in the report/review body. |

## Severity

| Badge | Bar | Examples |
| --- | --- | --- |
| `🔴 Critical` | Production incident or data/security compromise on a plausible path | auth bypass, injection, cross-tenant leak, data loss, crash on hot path, unbounded resource growth |
| `🟠 Major` | Wrong behavior, user-visible degradation, or a bug awaiting its trigger | logic error, swallowed error on a critical path, missing rollback, race under concurrency, O(n²) on unbounded input, API contract drift |
| `🟡 Minor` | Real defect with narrow blast radius, or a gap that erodes safety | unhandled edge case, missing validation on an internal boundary, test that cannot fail, misleading error message |
| `🔵 Trivial` | Correct but improvable | naming, small dedup, doc gap, idiom |

Severity measures **impact if unfixed**, not confidence and not effort. When torn between two levels, pick the lower one — inflated severity is how reviews lose trust.

## Effort modifier

`⚡ Quick win` — the suggested fix is local and mechanical (≤ ~15 lines, one site). `🏗️ Heavy lift` — the fix spans files or needs design. Omit when neither clearly applies.

## Source attribution

Every finding names what produced it, one or more of: `guideline` (a rubric rule — cite its registry id and quote it verbatim with its source path), `learning` (an entry from learnings.md), `linter` (folded tool output that needed interpretation), `verification` (a command run against the checkout — include the command and result), `review` (reviewer reasoning over the code itself).

## Evidence certificate

Every finding's first `evidence[]` entry is a checkout-grounded certificate:

```
Premise: <observed fact at file:line> → Path: <named caller/input/control flow> → Verdict: <resulting failure or measurable improvement>
```

The premise names code actually read, the path connects the diff to a concrete input or state, and the verdict states the resulting behavior. Later entries record the commands and file reads that tried to refute the certificate. A certificate such as `looks wrong → may fail → bug` is not evidence.

## Profile gates

| | `chill` (default) | `assertive` |
| --- | --- | --- |
| Critical / Major | reported | reported |
| Minor | reported when category is `⚠️ Potential issue`; otherwise folded into nitpicks | reported |
| Trivial | dropped | reported as nitpick |
| Nitpicks | only ⚡ Quick wins, collapsed | all, collapsed |

## Outside-diff findings

A finding on lines the diff did not touch is allowed only when: (a) the diff breaks that code (changed contract, renamed symbol, altered invariant), or (b) the code is a sibling path that should mirror a fix the diff makes elsewhere. Anything else on untouched code is pre-existing debt — out of scope. Mark these findings `in_diff: false`; they render in their own section, never as inline PR comments.

## Suppression rules

Drop the finding before recording it when any of these hold:

1. **Linter overlap** — a linter/typechecker lane that ran in the context pack already reports it.
2. **Intentional** — an adjacent comment, `nolint`/`eslint-disable` with justification, ADR, or a test asserting the behavior shows the pattern is deliberate.
3. **Generated or vendored** — the manifest ignored the file; findings there are void.
4. **Formatting** — whitespace, import order, or style a formatter owns.
5. **Speculative** — the claim has no concrete failure mode ("could be fragile", "might be slow"). Either produce the failing scenario or let it go.
6. **Pre-existing** — outside the diff and matching neither outside-diff clause above.
7. **Phantom knowledge** — the certificate depends on code that was not inspected, or a true framework fact does not cause the claimed result in this diff. Trace the repository path that connects premise to verdict or drop it (for example: SMTP commonly times out is irrelevant when this caller bounds the operation; environment parsing is risky in general but not when this value is validated before use).

## Volume discipline

No numeric cap — the gates above are the cap. **Find broadly, refute, report narrowly:** each reported finding must survive an active attempt to disprove its certificate, carry a concrete failure mode (or measurable improvement), clear every suppression, and receive severity only afterward. One root cause = one finding; search for every occurrence, report the representative instance, and list all others under `also_applies`.
