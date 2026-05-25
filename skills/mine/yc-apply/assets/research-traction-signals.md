# Research Slice 05 — Traction & Demand Signals

Compose this into an Agent (general-purpose) call in Phase 3. Substitute `{{...}}` from the workspace. Dispatch in parallel with the other four slices in a single message.

---

You are hunting for evidence — in the wild — that the problem this startup solves is real and painful. Your single deliverable is ONE markdown file.

**Startup:** {{COMPANY_NAME}} — {{ONE_LINE_DESCRIPTION}}
**Problem:** {{PROBLEM_STATEMENT}}

**Write to (the ONLY path you may write):** `{{WORKSPACE}}/04_research/05_traction-signals.md`
**Do NOT write anywhere else. Do NOT edit existing files.**

**Investigate** (use WebSearch + WebFetch):
- Where do people complain about this problem? Hacker News, Reddit, X/Twitter, niche forums, G2/Capterra reviews, Product Hunt comments.
- Verbatim pain quotes from real users ("I wish there were a tool that…", "I hate that X forces me to…").
- Search-volume / community-size proxies for demand (subreddit sizes, forum activity, recurring threads).
- Any public traction the startup ITSELF already has (launches, press, waitlist mentions, social following).

**Output schema (fill all six sections):**

```
# Traction & Demand Signals — {{COMPANY_NAME}}

## Findings
(Where the pain shows up, how loud it is, what the demand proxies suggest.)

## Verbatim Quotes
(Real user pain quotes — these are gold for the "how do you know people need this?" answer. Cite the URL.)

## Signal Strength
(Strong / moderate / weak evidence that the problem is real and urgent.)

## Risks
(Signs the pain is niche, occasional, or a vitamin rather than a painkiller.)

## Open Questions
(Demand you suspect but couldn't quantify; what the founder should validate with users.)

## Evidence URLs
(Every source URL, one per line.)
```

Feed the YC answer "How do you know people need what you're making?" Prefer verbatim user pain over your own inference. Stay within this slice; do not size the market or profile founders (other agents own those).
