# Architecture and Rationale

The Karpathy Knowledge Base Pattern treats the LLM as a **compiler** that reads raw source documents and produces a structured, cross-linked markdown wiki. No vector database, no embedding pipeline, no retrieval ranking — the wiki itself is the knowledge base, and at personal scale (~100 articles, ~400K words) it fits entirely in a modern context window.

Coined by Andrej Karpathy in April 2026 (see @karpathy on X, "LLM Knowledge Bases"), popularized via dair.ai and observed in practice across the Obsidian community.

## Core thesis

> You never write the wiki. The LLM writes everything. You just steer, and every answer compounds.

Three converging capabilities enable the pattern:

1. **1M+ token context windows** let the full wiki load into a single LLM call.
2. **LLM writing quality** is sufficient to produce technically rigorous reference articles.
3. **Markdown + Obsidian** gives inspectable, editable, scriptable, versionable, renderable files with no lock-in.

The human contributes judgment, taste, and direction. The LLM contributes exhaustive cross-referencing, consistent formatting, tireless compilation, and gap identification.

## The four-phase cycle

```
    ┌──────────────┐
    │ 1. INGEST    │  Scrape / curate → raw/
    └──────┬───────┘
           │
           v
    ┌──────────────┐
    │ 2. COMPILE   │  LLM reads raw/, writes wiki/
    └──────┬───────┘
           │
           v
    ┌──────────────┐
    │ 3. QUERY     │  Q&A against wiki, file back → outputs/
    └──────┬───────┘
           │
           v
    ┌──────────────┐
    │ 4. LINT      │  Find gaps, fix errors, suggest articles
    └──────┬───────┘
           │
           └──────→ back to Phase 1
```

Each phase enhances the next. The cycle runs continuously — the knowledge base is always growing, always improving.

### Phase 1: Ingest

Raw source material enters through multiple channels and is staged immutably:

- **Web clipping** (articles, blog posts, papers) → `raw/articles/`
- **GitHub READMEs, docs, architecture notes** → `raw/github/`
- **Bookmark clusters** (e.g., TweetSmash exports) → `raw/bookmarks/`
- **Manual curation** (diagrams, screenshots, PDFs) → `raw/articles/` or `raw/images/`

Principle: capture broadly, filter later. It is better to ingest something irrelevant than to miss something valuable. Never edit files in `raw/` after ingestion — if a source changes, re-scrape as a new version.

### Phase 2: Compile

The LLM reads raw sources and produces structured wiki articles:

1. Load the topic's Concept Index for orientation.
2. Load the target article (if updating).
3. Load relevant raw sources.
4. Write the article with structured sections, `[[wikilinks]]`, code examples, source attributions, technical depth suitable for senior practitioners.
5. Write to `wiki/concepts/<Article Title>.md`.

Compile foundational articles first so dependent articles can wikilink to them.

### Phase 3: Query and enhance

With 1M+ context, load the full wiki (or a relevant subset) and answer complex cross-article queries that would challenge traditional retrieval:

- "Compare approaches to X across all frameworks discussed."
- "What are the gaps in our coverage of Y?"
- "Synthesize arguments for and against Z."

**Every answer gets filed back** to `outputs/queries/<YYYY-MM-DD> <slug>.md`. On the next compile pass, insights from filed-back queries get absorbed into the wiki articles themselves. This is the compounding mechanism.

### Phase 4: Lint and heal

Scan the wiki for entropy:

- **Dead wikilinks** — links to articles that do not exist
- **Orphan articles** — articles with zero incoming links
- **Stale content** — articles older than their sources
- **Missing coverage** — topics referenced in N articles but lacking their own
- **Inconsistencies** — contradictory claims across articles
- **Format violations** — articles that drift from the standard structure

The lint pass leaves the knowledge base in a better state than it found it. This is the self-healing property.

## Why markdown + Obsidian

Five properties:

- **Inspectable** — plain text, any editor, no opaque database.
- **Editable** — humans can correct errors directly without an API layer.
- **Scriptable** — grep, sed, and programming languages process the corpus trivially.
- **Versionable** — git tracks every change, every compilation can be reviewed.
- **Renderable** — Obsidian gives graph view, backlinks, full-text search, plugin ecosystem.

No lock-in. If Obsidian disappears the files are still markdown. If the LLM changes the files are still text.

## Context window vs RAG

| Concern | RAG | Karpathy KB |
|---------|-----|-------------|
| Retrieval | Embedding + vector DB + ranking | Load into context |
| Relevance | Depends on embedding quality | LLM reads everything relevant |
| Cross-article reasoning | Multi-retrieval with fusion | Natural, all in context |
| Infrastructure | Vector DB, pipeline, tuning | File system + LLM |
| Per-query cost | Low | Higher |
| Answer quality on synthesis | Medium | High |

Karpathy KB trades higher per-query cost for dramatically simpler infrastructure and higher synthesis quality. For personal/team knowledge bases with moderate query volume and a premium on answer quality, the tradeoff is favorable. For high-volume production (millions of queries/day), traditional RAG remains more cost-effective.

## Target scale

A mature knowledge base: 100+ articles, 400K+ words total, dense cross-linking. At this scale, queries produce insights that combine information from articles originally compiled from completely independent raw sources. The knowledge base becomes more than the sum of its inputs.

## Future direction: knowledge in weights

The pattern's trajectory: wiki → synthetic QA pairs → QLoRA fine-tune → domain-expert model. The knowledge moves from context into parameters, enabling faster inference and deployable domain expertise.

## Multi-topic vaults

Each top-level folder at the vault root is a **topic** — a self-contained subject with its own `raw/`, `wiki/`, `outputs/`, `bases/` subtrees. All topics share one Obsidian vault at the root, so cross-topic wikilinks work naturally (e.g., an `ai-harness` article on embeddings can link to a `rust-systems` article on implementation details). Topics stay self-contained in terms of content but contribute to a unified knowledge graph.

Each topic has its own `CLAUDE.md` capturing topic-specific scope, current articles, and research gaps. The vault-root `CLAUDE.md` captures the shared Karpathy pattern itself.
