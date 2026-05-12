# Dispatch Rules

Subagents launched by this skill (`explorer`, defined at `.claude/agents/explorer.md` after install from `assets/explorer-agent.md`) operate under a strict **scoped-write** contract — exactly one `Write` to the named target path, every other action read-only. The rules below MUST be embedded in every subagent prompt verbatim.

## Scoped-Write Contract

1. The parent prompt MUST name three things:
   - The slice scope (primary source paths, directories, URLs, or topical bounds).
   - The slug and ordinal (`NN_analysis_<slug>`).
   - The exact target analysis file path (`<path>/analysis/NN_analysis_<slug>.md`).
     If any of the three is missing or ambiguous, the subagent returns a clarification request and writes nothing.
2. The subagent MAY call `Write` exactly once, and only at the target path the parent named.
3. The subagent MUST NOT call `Edit`. MUST NOT call `Write` against any other path. MUST NOT create directories outside the named analysis directory.
4. The subagent reads only the slice scope the parent named (local paths or URLs). For web-scoped slices, `WebFetch` and `WebSearch` are allowed but must stay aligned with the slice question.
5. The subagent MUST NOT run state-mutating shell commands: no `git`, `make`, `bun`, `npm`, `pnpm`, `mv`, `rm`, `cp` of non-trivial trees, `>`, `>>`, or any command that touches the working tree outside `<path>/analysis/`.
6. If the subagent encounters a source that requires interpretation by another tool (compiled binary, encrypted blob, paywalled URL), it records a note in the **Open Questions** section and continues.

## Tool Restrictions

- **Allowed:** `Read`, `Grep`, `Glob`, `Bash` for read-only operations (e.g., `wc -l`, `find`, `head`, `cat`, `ls`, `file`, `rg`), `WebFetch`, `WebSearch`, `Write` (exactly once, only at the named target path).
- **Forbidden:** `Edit` anywhere; `Write` to any path other than the named target; `Bash` commands that mutate state (`rm`, `mv`, `>`, `>>`, `git`, `make`, package managers).

## Parent Responsibilities

- The parent agent MUST verify the explorer subagent is installed for the active harness before dispatch:
  - Claude Code: `.claude/agents/explorer.md` exists.
  - Codex CLI: `.codex/agents/explorer.toml` exists.
  If absent for the active harness, the parent MUST offer to install from `assets/explorer-agent.md` / `assets/explorer-agent.toml` via `scripts/install-explorer.sh` before continuing.
- The parent agent MUST ensure `<path>/analysis/` exists before dispatch (the subagent will refuse to write into a missing directory rather than creating it).
- The parent agent MUST set `subagent_type: explorer` on every Agent dispatch in the research round.
- The parent agent MUST embed all three names — slice scope, slug+ordinal, target file path — explicitly in the subagent prompt.
- The parent agent MUST scout the territory itself first (Step 3 of the SKILL.md) so each slice is non-overlapping and independently answerable.

## Parallelism

- All subagents in a research round dispatch in the same parallel batch. Do not stagger.
- Wait for every subagent to complete before verification. A partial set is unacceptable.
- The hard cap is 8 subagents per round. Use fewer when the scout reveals fewer non-overlapping slices.

## Output Validation

Each subagent writes a file containing all seven sections from `assets/analysis-template.md` (Overview, Mechanisms/Patterns, Relevant Sources, Transferable Patterns, Risks/Mismatches, Open Questions, Evidence). After dispatch the parent:

1. Lists `<path>/analysis/` and confirms one file per dispatched slice at the expected `NN_analysis_<slug>.md` path.
2. Re-reads each file to confirm all seven sections are present.
3. Sample-checks at least one cited source per file — `Read` for local paths, well-formedness check for URLs — to confirm evidence is real, not fabricated.
4. If any section is empty or any cited source is fake, re-dispatches the offending subagent with the schema and a request to fill the gap. The parent never authors the missing content — the subagent owns the write.

## Failure Handling

- If a subagent crashes or returns malformed output, retry once with a stricter prompt restating the scoped-write contract.
- If a subagent reports the slice scope is empty or unreachable, the subagent returns a clarification request and writes nothing. The parent decides whether to merge that slice into an adjacent slice or drop it.
- If a subagent violates the scoped-write contract (writes outside the named path, calls `Edit`, runs `git`/`make`/etc.), treat it as a contract violation: stop, re-read this file, and re-dispatch with the contract restated verbatim in the subagent prompt.
- Do not synthesize a missing slice as if its analysis succeeded.
