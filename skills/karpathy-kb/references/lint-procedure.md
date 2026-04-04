# Lint and Heal Procedure

The automated `scripts/lint-wiki.py` handles the three most common checks (dead wikilinks, orphans, missing source files). This document covers the deeper LLM-driven checks that require reading articles and applying judgment.

## Automated checks (scripts/lint-wiki.py)

Run: `python3 .claude/skills/karpathy-kb/scripts/lint-wiki.py <topic>/`

Reports:

- **Dead wikilink** — `[[Foo]]` when no file named `Foo.md` exists in the topic (or in linked topics, for cross-topic links).
- **Orphan article** — `wiki/concepts/Foo.md` with zero incoming `[[Foo]]` references from any other file.
- **Missing source file** — `sources:` frontmatter entry pointing at a wikilink that has no corresponding file in `raw/`.

## LLM-driven checks

These require reading articles and applying judgment — run them periodically or after a batch of new content.

### Check 1: Stale content

For each article:

1. Read the article's `updated:` date and `sources:` entries.
2. Check each source file's `scraped:` date (or file mtime).
3. If any source is newer than the article, flag it for recompilation.
4. Also flag articles where the topic has evolved rapidly (e.g., LLM model names, protocol versions) and the article has not been updated in 30+ days.

### Check 2: Inconsistencies across articles

Load groups of related articles (identified via shared tags or wikilinks) and check for:

- Contradictory factual claims (e.g., "H100 has 80GB HBM3" vs "H100 has 80GB HBM2e")
- Inconsistent terminology (same concept called two different names across articles)
- Inconsistent formatting (some articles use tables, others prose, for the same kind of comparison)

Fix by picking the correct/canonical version and updating all affected articles.

### Check 3: Missing coverage

Scan all articles for wikilinks and identify targets that:

- Are referenced in 3+ articles
- Do not have their own article yet

These are strong candidates for new articles. For each:

1. Check whether relevant raw sources exist in `raw/`.
2. If yes, write the article (Procedure 3 in SKILL.md).
3. If no, ingest sources first (Procedure 2) or mark as a research gap in the topic's `CLAUDE.md`.

### Check 4: Format violations

Verify each article has:

- H1 title matching filename
- Lead paragraph
- Sources section at the bottom
- At least 5 wikilinks (outgoing)
- Frontmatter with all required fields (see `references/frontmatter-schemas.md`)

Fix by rewriting or adding the missing elements.

### Check 5: Wikilink audit

For each article:

- Identify concepts mentioned without wikilinks that should have them
- Identify over-wikilinking (same term linked multiple times in close proximity)
- Identify wikilinks to concepts that no longer match the linked article's actual content

### Check 6: Filed-back query absorption

Scan `<topic>/outputs/queries/` for recent query results. For each:

1. Identify the wiki articles listed under `informed_by:`.
2. Check whether the synthesis in the query result adds new insights not yet in those articles.
3. If yes, flag the articles for updates and absorb the insights on the next compile pass.

This is the core compounding mechanism — query answers feeding back into the wiki.

## Lint report format

When running a manual lint pass, produce a report like:

```
LINT REPORT — <topic>/ — YYYY-MM-DD

DEAD LINKS (N)
  - [[Missing Article]] referenced in: Foo.md, Bar.md
    → SUGGEST: Create wiki/concepts/Missing Article.md
    → POTENTIAL SOURCES: raw/articles/relevant-source.md

ORPHAN ARTICLES (N)
  - Token Economics.md — 0 incoming links
    → SUGGEST: Add refs from Agent Infrastructure.md, Fine-Tuning.md

STALE CONTENT (N)
  - MCP article references "MCP spec v0.9" but raw/articles/mcp-spec.md is v1.2
    → UPDATE: Recompile with current spec

INCONSISTENCIES (N)
  - Hardware specs disagree: Agent Infrastructure.md vs Fine-Tuning.md
    → RESOLVE: Verify against authoritative source, pick canonical

MISSING COVERAGE (N)
  - "Inference Optimization" referenced in 4 articles, no article exists
    → SUGGEST: Create wiki/concepts/Inference Optimization.md

FORMAT VIOLATIONS (N)
  - Prompt Engineering Techniques.md — missing Sources section

FILED-BACK INSIGHTS (N)
  - outputs/queries/2026-04-02 memory vs context.md has synthesis not in Memory Systems.md
    → ABSORB: Update Memory Systems.md with the compaction tradeoffs insight
```

## Heal workflow

For each issue the lint report surfaces:

1. **Dead link + source available** → create the article (Procedure 3).
2. **Dead link + no source** → mark in topic `CLAUDE.md` research gaps, or rewrite the link.
3. **Orphan** → add incoming wikilinks, or delete if out-of-scope.
4. **Stale** → re-scrape source, recompile article.
5. **Inconsistency** → find authoritative source, fix all affected articles.
6. **Missing coverage** → ingest sources, write article.
7. **Format violation** → fix formatting.
8. **Filed-back insight** → update affected wiki articles.

Run the cycle regularly. Each pass leaves the knowledge base in a better state than it found it.
