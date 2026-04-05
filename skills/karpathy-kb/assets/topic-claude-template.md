# TOPIC_TITLE

**Topic scope:** one-paragraph description of what this topic covers.

**Domain:** `TOPIC_DOMAIN` — all notes in this topic use `domain: TOPIC_DOMAIN` in frontmatter.

This file is the **schema document** for the topic (per Karpathy's LLM Wiki pattern). It tells the LLM how this topic is structured, its conventions, and its current state. Co-evolve it as the topic matures. Follow the shared conventions in the [root CLAUDE.md](../CLAUDE.md) for architecture, frontmatter, lifecycle, and tools — this file captures only topic-specific context.

## Audit log

See [log.md](log.md) for the chronological record of every ingest / compile / query / lint operation. Append an entry there after each operation (skill Procedure 7).

## Current wiki articles

_None yet. See the [karpathy-kb skill](../.claude/skills/karpathy-kb/SKILL.md) Procedure 3 for how to compile new articles._

## Corpus inventory

- `raw/articles/` — 0 files
- `raw/bookmarks/` — 0 clusters
- `raw/github/` — 0 snapshots
- `wiki/concepts/` — 0 articles
- `bases/` — 0 base files

## qmd collection (optional)

At small scale, the topic's Concept Index / Source Index provide sufficient navigation. Once the corpus grows (~20+ sources or ~50+ wiki articles), add a qmd collection for hybrid BM25/vector search. Indexed as collection `TOPIC_SLUG`. Re-index from this directory after changes:

```bash
qmd collection remove TOPIC_SLUG && qmd collection add . --name TOPIC_SLUG && qmd embed
```

See `.claude/skills/karpathy-kb/references/tooling-tips.md` for Obsidian plugin tips (Web Clipper, Dataview, Marp).

## Research gaps

Priority areas to cover first:

- Gap 1
- Gap 2
