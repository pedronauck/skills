---
name: karpathy-kb
description: Creates and maintains Karpathy-style knowledge bases — Obsidian markdown vaults where an LLM compiles raw sources into cross-linked wiki articles, files Q&A answers back into the corpus, and lints for gaps. Use when scaffolding a new topic folder, scraping sources into raw/, writing or updating wiki/concepts/ articles, maintaining Dashboard/Concept Index/Source Index files, running the ingest-compile-query-lint cycle, or adding frontmatter to notes. Do not use for general markdown editing, non-knowledge-base Obsidian notes, code documentation, or personal daily notes.
---

# Karpathy Knowledge Base Pattern

Build and maintain a self-compiling Obsidian markdown knowledge base. The LLM reads raw sources, writes cross-linked wiki articles, files Q&A results back into the corpus, and runs lint-and-heal passes.

Each **topic** lives in its own top-level folder (e.g. `ai-harness/`) with `raw/`, `wiki/`, `outputs/`, `bases/` subtrees. All topics share a single Obsidian vault at the repo root. Read `references/architecture.md` for the full rationale and the four-phase pipeline (ingest → compile → query → lint).

## Related skills

This skill orchestrates several companion skills — use them for the sub-tasks of the pipeline:

- **[firecrawl](https://github.com/pedronauck/skills/tree/main/skills/firecrawl)** — scrape URLs and crawl sites to populate `<topic>/raw/` during the **ingest** phase.
- **[tweetsmash-api](https://github.com/pedronauck/skills/tree/main/skills/tweetsmash-api)** — fetch TweetSmash bookmark clusters into `<topic>/raw/bookmarks/`.
- **[qmd](https://github.com/pedronauck/skills/tree/main/skills/qmd)** — build and query per-topic semantic collections over the vault; drives the **query** phase and source discovery during **compile**.
- **[obsidian-markdown](https://github.com/pedronauck/skills/tree/main/skills/obsidian-markdown)** — author wiki articles with valid Obsidian Flavored Markdown (wikilinks, callouts, embeds, properties).
- **[obsidian-bases](https://github.com/pedronauck/skills/tree/main/skills/obsidian-bases)** — create `.base` files under `<topic>/bases/` for dashboard views, filters, and formulas.
- **[obsidian-cli](https://github.com/pedronauck/skills/tree/main/skills/obsidian-cli)** — interact with the running Obsidian vault from the command line (open notes, search, refresh indexes).

## When to apply

- Scaffolding a new topic folder under the knowledge vault
- Scraping a web article or GitHub README into `<topic>/raw/articles/` or `<topic>/raw/github/`
- Pulling bookmark clusters from TweetSmash into `<topic>/raw/bookmarks/`
- Writing a new wiki article in `<topic>/wiki/concepts/` (target 3000-4000 words, dense wikilinks)
- Updating a topic's Dashboard / Concept Index / Source Index after structural changes
- Filing a Q&A result back to `<topic>/outputs/queries/`
- Running lint checks for dead wikilinks, orphan articles, missing source files

## Procedures

### Procedure 1: Scaffold a new topic

Run from the vault root:

```bash
bash .claude/skills/karpathy-kb/scripts/new-topic.sh <topic-slug> "<Topic Title>" <domain>
```

Example: `bash .claude/skills/karpathy-kb/scripts/new-topic.sh rust-systems "Rust Systems Programming" rust`

The script creates the standard directory tree (`raw/{articles,bookmarks,github}`, `wiki/{concepts,index}`, `outputs/{briefings,queries,diagrams}`, `bases/`), installs Dashboard / Concept Index / Source Index from `assets/`, and writes a topic `CLAUDE.md` stub. After the script finishes:

1. Add the topic as a new row in the vault-root `README.md` topic table.
2. Create a qmd collection via the [qmd skill](https://github.com/pedronauck/skills/tree/main/skills/qmd): `qmd collection add <topic-slug>/ --name <topic-slug> && qmd embed`.
3. Start ingesting sources (Procedure 2).

### Procedure 2: Ingest a raw source

1. Scrape the URL with the [firecrawl skill](https://github.com/pedronauck/skills/tree/main/skills/firecrawl): `firecrawl scrape <url>` (single page) or `firecrawl crawl <url>` (multi-page).
2. Save the output to `<topic>/raw/articles/<descriptive-slug>.md` (or `raw/github/` for READMEs). Format the body as Obsidian Flavored Markdown — see the [obsidian-markdown skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-markdown) for wikilinks, callouts, and properties.
3. Prepend frontmatter — copy the matching schema from `references/frontmatter-schemas.md`. Fill `title`, `source_url`, `scraped` (today's ISO date), and topic-specific `tags`.
4. For TweetSmash bookmarks, pull clusters via the [tweetsmash-api skill](https://github.com/pedronauck/skills/tree/main/skills/tweetsmash-api) and save to `<topic>/raw/bookmarks/<Topic> Bookmarks <Subtopic>.md` using the bookmark-cluster frontmatter schema.
5. Re-index the topic's [qmd](https://github.com/pedronauck/skills/tree/main/skills/qmd) collection: `qmd collection remove <collection> && qmd collection add <topic>/ --name <collection> && qmd embed`.

### Procedure 3: Compile a wiki article

1. Read `references/compilation-guide.md` to anchor on length, style, wikilink density, and sourcing rules.
2. Identify candidate sources via the [qmd skill](https://github.com/pedronauck/skills/tree/main/skills/qmd) — `qmd query "<topic phrase>"` scoped to the topic's collection — or read `<topic>/wiki/index/Source Index.md`.
3. Load the candidate raw sources fully into context.
4. Load `<topic>/wiki/index/Concept Index.md` for orientation on existing articles and wikilink targets (including in other topics).
5. Write the article to `<topic>/wiki/concepts/<Article Title>.md` using `assets/wiki-article-template.md`, following the [obsidian-markdown skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-markdown) for wikilink, callout, and frontmatter syntax. Target 3000-4000 words with a Sources section, wikilinks to related articles, and code or diagram blocks where applicable.
6. Update the topic's indexes (Procedure 4).
7. Update `<topic>/CLAUDE.md` current-articles list.
8. Re-index the [qmd](https://github.com/pedronauck/skills/tree/main/skills/qmd) collection.

### Procedure 4: Maintain topic indexes

After adding, renaming, or removing any wiki article:

1. `<topic>/wiki/index/Dashboard.md` — update article count, total word count, featured sections, and any Obsidian Base embeds (use the [obsidian-bases skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-bases) to author `.base` files and embed them).
2. `<topic>/wiki/index/Concept Index.md` — insert/update the article row alphabetically with its one-line summary.
3. `<topic>/wiki/index/Source Index.md` — for each new article, append rows for every source it cites, with a wikilink back to the article.
4. Optionally refresh the live view in Obsidian with the [obsidian-cli skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-cli) (`obsidian open <path>`, `obsidian search <query>`).

### Procedure 5: File back a Q&A answer

After answering a cross-article query against the wiki:

1. Save the answer to `<topic>/outputs/queries/<YYYY-MM-DD> <Question Slug>.md`.
2. Use the research-output frontmatter from `references/frontmatter-schemas.md` with `stage: query`.
3. In the body, list which wiki articles informed the answer (as wikilinks) and call out new insights that should be absorbed back into those articles on the next compile pass.
4. When the insight is strong enough to warrant article updates, recompile the affected articles (Procedure 3).

### Procedure 6: Lint and heal

Run from the vault root:

```bash
python3 .claude/skills/karpathy-kb/scripts/lint-wiki.py <topic>/
```

The script prints dead wikilinks, orphan articles, and missing source references. For each issue:

- **Dead wikilink** — either create the missing article (Procedure 3) or rewrite the wikilink to point at an existing article.
- **Orphan article** — add incoming wikilinks from at least one related article, or remove the article if it is outside the topic's scope.
- **Missing source file** — an article's `sources:` frontmatter references a file absent from `raw/`. Either re-scrape (Procedure 2) or correct the reference.

For deeper self-healing checks (stale content, inconsistencies, missing-coverage suggestions), read `references/lint-procedure.md`.

## Error Handling

- **qmd collection not found** — create it via the [qmd skill](https://github.com/pedronauck/skills/tree/main/skills/qmd): `qmd collection add <topic>/ --name <collection> && qmd embed`.
- **Article exceeds 4000 words** — extract a sub-topic into its own article and wikilink to it, rather than padding.
- **Cross-topic wikilink ambiguity** — if two topics contain articles with the same title, disambiguate with the full path: `[[ai-harness/wiki/concepts/RAG Architecture Patterns|RAG]]`. See the [obsidian-markdown skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-markdown) for wikilink edge cases.
- **firecrawl returns truncated or missing content** — retry per the [firecrawl skill](https://github.com/pedronauck/skills/tree/main/skills/firecrawl): `firecrawl scrape <url> --format markdown --only-main-content`.
- **`lint-wiki.py` missing** — the script is at `.claude/skills/karpathy-kb/scripts/lint-wiki.py`; run from the vault root.
- **new-topic.sh refuses to run** — the target folder already exists. Remove it first or choose a new slug.
