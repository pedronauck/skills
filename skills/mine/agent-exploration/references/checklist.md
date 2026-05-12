# Output Validation Checklist

Run this checklist after every research round, before authoring `summary.md`. Every item must pass; failing items trigger a re-dispatch of the offending slice.

## 1. Installation
- [ ] For Claude Code runs: `.claude/agents/explorer.md` exists and matches `assets/explorer-agent.md`.
- [ ] For Codex CLI runs: `.codex/agents/explorer.toml` exists and matches `assets/explorer-agent.toml`.
- [ ] Re-install via `scripts/install-explorer.sh` if either has drifted from the bundled asset.

## 2. Inputs
- [ ] `--path` resolved to an absolute path that exists.
- [ ] `--agents` is between 1 and 8 inclusive.
- [ ] `--prompt` is non-empty and quoted in every subagent dispatch verbatim.
- [ ] `<path>/analysis/` exists before dispatch.

## 3. Scout
- [ ] The parent performed a read-only scout of 8–15 tool calls.
- [ ] Slice count matches `--agents` OR was reduced with operator notice.
- [ ] Slices are non-overlapping and independently answerable.
- [ ] Every slice has a two-digit ordinal and a kebab-case slug.

## 4. Dispatch
- [ ] Every subagent call set `subagent_type: explorer`.
- [ ] Every subagent prompt embedded `references/dispatch-rules.md` verbatim.
- [ ] Every subagent prompt named slice scope, slug+ordinal, and target path.
- [ ] All subagents dispatched in the same parallel batch.

## 5. Files
- [ ] Exactly `N` files exist under `<path>/analysis/` matching the dispatched ordinals/slugs.
- [ ] No file is empty or stub-only.
- [ ] No file was written outside `<path>/analysis/`.

## 6. Schema
- [ ] Every file contains all seven sections (Overview, Mechanisms/Patterns, Relevant Sources, Transferable Patterns, Risks/Mismatches, Open Questions, Evidence).
- [ ] No section is empty without a one-line gap-note and a matching Open Question.
- [ ] At least one cited source per file was sample-checked and confirmed real.

## 7. Summary
- [ ] `summary.md` is parent-authored, not produced by a subagent.
- [ ] `summary.md` cites every slice file by path.
- [ ] Convergences and Divergences sections both have content (or explicit notes that none surfaced).
- [ ] Recommended Next Steps cite the slice file(s) that support them.
