# Research Slice 02 — Competitive Landscape

Compose this into an Agent (general-purpose) call in Phase 3. Substitute `{{...}}` from the workspace. Dispatch in parallel with the other four slices in a single message.

---

You are mapping the competitive landscape for a startup applying to Y Combinator. Be skeptical and specific. Your single deliverable is ONE markdown file.

**Startup:** {{COMPANY_NAME}} — {{ONE_LINE_DESCRIPTION}}
**Space:** {{PROBLEM_SPACE}}

**Write to (the ONLY path you may write):** `{{WORKSPACE}}/04_research/02_competitive-landscape.md`
**Do NOT write anywhere else. Do NOT edit existing files.**

**Investigate** (use WebSearch + WebFetch):
- Direct competitors (same problem, same buyer). For each: positioning, traction signals, funding, founding year.
- Indirect competitors / substitutes (the status-quo workaround, the spreadsheet, the incumbent tool).
- Recent funding rounds and recent shutdowns in this space (last 24 months).
- What each competitor does well and where the specific, exploitable gap is.

**Output schema (fill all six sections):**

```
# Competitive Landscape — {{COMPANY_NAME}}

## Findings
(Named competitors with positioning, funding, traction. The status-quo alternative. The specific gap.)

## Verbatim Quotes
(Quotes from competitor marketing, reviews, or user complaints that reveal the gap. Cite the URL.)

## Signal Strength
(Is this a crowded, nascent, or contested space? What does that imply for the application's "competitors" answer?)

## Risks
(Well-funded incumbents, recent failures suggesting the market is hard, "no competitors = no market" risk.)

## Open Questions
(Competitors you suspect but couldn't confirm; the founder should validate.)

## Evidence URLs
(Every source URL, one per line.)
```

Frame findings to feed the YC answer "Who are your competitors? What do you understand that they don't?" Never conclude "no competitors" — find the substitute. Stay within this slice; do not size the market or profile founders (other agents own those).
