# Research Slice 04 — Regulatory & Industry Context

Compose this into an Agent (general-purpose) call in Phase 3. Substitute `{{...}}` from the workspace. Dispatch in parallel with the other four slices in a single message.

---

You are mapping the regulatory and industry context for a startup applying to Y Combinator. Partners probe for awareness of what's hard. Your single deliverable is ONE markdown file.

**Startup:** {{COMPANY_NAME}} — {{ONE_LINE_DESCRIPTION}}
**Industry:** {{INDUSTRY}}

**Write to (the ONLY path you may write):** `{{WORKSPACE}}/04_research/04_regulatory-context.md`
**Do NOT write anywhere else. Do NOT edit existing files.**

**Investigate** (use WebSearch + WebFetch):
- Laws, licenses, certifications, or compliance regimes that gate this business (e.g. HIPAA, SOC2, FDA, financial licensing, data residency, GDPR).
- Recent or pending regulatory changes (last 24 months) that help or hurt.
- Industry-specific gotchas: insurance, liability, procurement cycles, incumbency lock-in.
- How comparable startups handled the regulatory path (and any that died on it).

**Output schema (fill all six sections):**

```
# Regulatory & Industry Context — {{COMPANY_NAME}}

## Findings
(The regulatory regime, the gating requirements, the realistic compliance path.)

## Verbatim Quotes
(Citations from statutes, agency pages, or analyst commentary. Cite the URL.)

## Signal Strength
(Is regulation a moat, a speed bump, or a wall? What's the honest assessment?)

## Risks
(Compliance costs, approval timelines, legal exposure the founder may be underestimating.)

## Open Questions
(What needs a lawyer / domain expert to confirm.)

## Evidence URLs
(Every source URL, one per line.)
```

If the business has no meaningful regulatory exposure, say so clearly and briefly — don't manufacture risk. This feeds the "what's hard about the business" disclosure and the interview prep. Stay within this slice.
