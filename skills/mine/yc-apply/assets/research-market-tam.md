# Research Slice 03 — Market & TAM

Compose this into an Agent (general-purpose) call in Phase 3. Substitute `{{...}}` from the workspace. Dispatch in parallel with the other four slices in a single message.

---

You are sizing the market for a startup applying to Y Combinator. YC strongly prefers bottom-up sizing over top-down. Your single deliverable is ONE markdown file.

**Startup:** {{COMPANY_NAME}} — {{ONE_LINE_DESCRIPTION}}
**Business model:** {{BUSINESS_MODEL}}

**Write to (the ONLY path you may write):** `{{WORKSPACE}}/04_research/03_market-tam.md`
**Do NOT write anywhere else. Do NOT edit existing files.**

**Investigate** (use WebSearch + WebFetch):
- Number of potential customers (count the actual buyer population, not a vague industry figure).
- Realistic per-customer annual spend.
- A bottom-up TAM: N customers × $X/year × plausible penetration = $Z.
- A top-down sanity check from industry reports (cite the report).
- Market growth rate and any recent shift (regulation, new tech, behavior change) that makes NOW the time.

**Output schema (fill all six sections):**

```
# Market & TAM — {{COMPANY_NAME}}

## Findings
(Bottom-up TAM with the arithmetic shown. Top-down sanity check. Growth rate. "Why now.")

## Verbatim Quotes
(Stats from named industry reports / analyst data. Cite the URL.)

## Signal Strength
(Is the market big enough to interest YC? Is the bottom-up number defensible?)

## Risks
(Top-down-only framing, optimistic penetration assumptions, shrinking or saturated market.)

## Open Questions
(Numbers you estimated vs. sourced; what the founder must verify.)

## Evidence URLs
(Every source URL, one per line.)
```

Feed the YC answers "How big is the market?" and "How much could you make?" Show the arithmetic. Stay within this slice; do not profile founders or map competitors in depth (other agents own those).
