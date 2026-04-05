# Architecture and Rationale

The Karpathy Knowledge Base Pattern treats the LLM as a **compiler** that reads raw source documents and produces a structured, cross-linked markdown wiki. No vector database, no embedding pipeline, no retrieval ranking — the wiki itself is the knowledge base, and at personal scale (~100 articles, ~400K words) it fits entirely in a modern context window.

Described by Andrej Karpathy in April 2026 in [LLM Wiki: Knowledge Base Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), with conceptual roots in Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents. Bush's unsolved problem was *who does the maintenance*. LLMs solve that: they don't get bored, don't forget cross-references, and can touch 15 files in one pass.

## Core thesis

> You never write the wiki. The LLM writes everything. You just steer, and every answer compounds.

Three converging capabilities enable the pattern:

1. **1M+ token context windows** let the full wiki load into a single LLM call.
2. **LLM writing quality** is sufficient to produce technically rigorous reference articles.
3. **Markdown + Obsidian** gives inspectable, editable, scriptable, versionable, renderable files with no lock-in.

The human contributes judgment, taste, and direction. The LLM contributes exhaustive cross-referencing, consistent formatting, tireless compilation, and gap identification.

## Three-op core vs four-phase extension

Karpathy's original gist frames the pattern as three operations: **Ingest**, **Query**, **Lint**. In his flow, ingest is active — the LLM reads the source, discusses it, writes a summary page, and updates 10-15 related wiki pages in one pass. "Compile" is folded into ingest.

This skill **splits ingest into two distinct phases** — `ingest` (scrape + stage into `raw/` immutably) and `compile` (LLM reads `raw/`, writes `wiki/concepts/`) — for three reasons:

1. **Multi-topic vaults.** A source may arrive weeks before it has enough companions to compile a rigorous 3000-4000-word article. Staging decouples acquisition from synthesis.
2. **Batch scraping.** Tools like firecrawl and tweetsmash-api produce clusters of raw material. Staging them first lets the LLM pick the compile order.
3. **Reproducibility.** `raw/` is immutable — a compiled article can always be re-derived from its sourced files.

The four-phase loop:

```
    ┌──────────────┐
    │ 1. INGEST    │  Scrape / curate → raw/ (immutable)
    └──────┬───────┘
           │
           v
    ┌──────────────┐
    │ 2. COMPILE   │  LLM reads raw/, writes wiki/concepts/
    └──────┬───────┘
           │
           v
    ┌──────────────┐
    │ 3. QUERY     │  Q&A against wiki → outputs/queries/, promote strong answers to wiki/
    └──────┬───────┘
           │
           v
    ┌──────────────┐
    │ 4. LINT      │  Find gaps, fix errors, suggest articles
    └──────┬───────┘
           │
           └──────→ back to Phase 1
```

Every phase ends with an append to `<topic>/log.md`. Each phase enhances the next. The cycle runs continuously — the knowledge base is always growing, always improving.

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

**Every answer gets filed back** to `outputs/queries/<YYYY-MM-DD> <slug>.md`. On the next compile pass, insights from filed-back queries get absorbed into the wiki articles themselves. When an answer is strong enough to stand as a first-class reference (a comparison table, a concept synthesized from multiple articles, a novel trade-off analysis), **promote it to `wiki/concepts/`** following Procedure 3 standards. Karpathy's pattern treats strong query answers as equal citizens of the wiki, not secondary artifacts. This is the compounding mechanism — explorations become reusable knowledge.

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

Each top-level folder at the vault root is a **topic** — a self-contained subject with its own `raw/`, `wiki/`, `outputs/`, `bases/` subtrees plus `CLAUDE.md` and `log.md` at the topic root. All topics share one Obsidian vault at the root, so cross-topic wikilinks work naturally (e.g., an `ai-harness` article on embeddings can link to a `rust-systems` article on implementation details). Topics stay self-contained in terms of content but contribute to a unified knowledge graph.

Each topic has its own `CLAUDE.md` (symlinked to `AGENTS.md` for Codex parity) capturing topic-specific scope, current articles, and research gaps — **this IS the schema document** in Karpathy's terminology. The vault-root `CLAUDE.md` captures the shared Karpathy pattern itself.

## The log.md audit trail

Every topic carries a `log.md` at its root — an append-only, chronological record of every knowledge-base operation. Each entry is a single H2 heading with a consistent grep-able prefix:

```
## [YYYY-MM-DD] <op> | <short description>
```

Ops: `ingest`, `compile`, `query`, `promote`, `split`, `lint`. The consistent prefix means unix tools can query the log without special parsing:

```bash
grep "^## \[" log.md | tail -10        # recent activity
grep "compile" log.md | wc -l          # total compiles
```

The log is distinct from git history. Git records *what changed in the files*; `log.md` records *what the knowledge base did as a system* — decisions made, insights synthesized, gaps identified. Both coexist. The log is the operational memory; git is the version control.

## The wiki is a git repo

The wiki is just a directory of markdown files under git. No database, no server, no API — you get version history, branching, diffs, blame, and collaboration for free. Every compile and lint pass is a reviewable commit. If Obsidian disappears, the files are still markdown. If the LLM changes, the files are still text. This is the no-lock-in guarantee.
