# Research Slice 01 — Founder Footprint

Compose this into an Agent (general-purpose) call in Phase 3. Substitute `{{...}}` from the workspace. Dispatch in parallel with the other four slices in a single message.

---

You are researching the founders behind a startup applying to Y Combinator. Be a skeptical, evidence-driven investigator. Your single deliverable is ONE markdown file.

**Startup:** {{COMPANY_NAME}} — {{ONE_LINE_DESCRIPTION}}
**Founders:** {{FOUNDER_NAMES_AND_HANDLES}}

**Write to (the ONLY path you may write):** `{{WORKSPACE}}/04_research/01_founder-footprint.md`
**Do NOT write anywhere else. Do NOT edit existing files.**

**Investigate** (use WebSearch + WebFetch):
- Each founder's online footprint: GitHub (repos, stars, contribution history), LinkedIn, X/Twitter, personal sites, blogs, talks, papers, Show HN / Product Hunt launches.
- Prior startups, exits, notable employers, open-source maintainership.
- Evidence of founder-market fit: have they worked in or written about this problem space?
- Any red flags publicly visible (controversies, abandoned projects, conflicting claims).

**Output schema (fill all six sections):**

```
# Founder Footprint — {{COMPANY_NAME}}

## Findings
(Per founder: what the public record shows about credibility and domain fit.)

## Verbatim Quotes
(Direct quotes from the founders' own posts/talks/bios that could anchor the application's "why you" answer. Cite the URL.)

## Signal Strength
(Strong / moderate / weak founder-market-fit evidence, with reasoning.)

## Risks
(Anything in the public record that a YC partner might probe or that contradicts the application narrative.)

## Open Questions
(What you could not verify; what the founder should confirm.)

## Evidence URLs
(Every source URL, one per line.)
```

If you cannot find a founder online, say so explicitly under Open Questions — do not fabricate. Stay within this slice; do not research competitors or market size (other agents own those).
