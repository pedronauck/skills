---
name: karpathy-kb
description: Creates and maintains Karpathy-style knowledge bases — Obsidian markdown vaults where an LLM compiles raw sources into cross-linked wiki articles, files Q&A answers back into the corpus, appends a chronological log.md, and lints for gaps. Use when scaffolding a new topic folder, scraping sources into raw/, writing or updating wiki/concepts/ articles, maintaining Dashboard/Concept Index/Source Index/log.md files, running the ingest-compile-query-lint cycle, or adding frontmatter to notes. Do not use for general markdown editing, non-knowledge-base Obsidian notes, code documentation, or personal daily notes.
---

# Karpathy Knowledge Base Pattern

Build and maintain a self-compiling Obsidian markdown knowledge base. The LLM reads raw sources, writes cross-linked wiki articles, files Q&A results back into the corpus, appends every operation to a chronological `log.md`, and runs lint-and-heal passes.

Each **topic** lives in its own top-level folder (e.g. `ai-harness/`) with `raw/`, `wiki/`, `outputs/`, `bases/` subtrees plus a topic-level `log.md` and `CLAUDE.md`. All topics share a single Obsidian vault at the repo root. Read `references/architecture.md` for the full rationale and the four-phase pipeline (ingest → compile → query → lint) adapted from Karpathy's three-op core (ingest → query → lint).

The topic's **`CLAUDE.md`** (symlinked to `AGENTS.md`) is the **schema document** — it tells the LLM the scope, conventions, current articles, and research gaps for that topic. Co-evolve it as the topic matures.

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
- Answering a cross-article question against the wiki (Concept Index first, then drill into articles), filing the answer to `<topic>/outputs/queries/`, and optionally promoting it to `wiki/concepts/`
- Appending ingest / compile / query / lint events to `<topic>/log.md`
- Running lint checks for dead wikilinks, orphan articles, missing source files

## Procedures

### Procedure 1: Scaffold a new topic

Run from the vault root:

```bash
bash .claude/skills/karpathy-kb/scripts/new-topic.sh <topic-slug> "<Topic Title>" <domain>
```

Example: `bash .claude/skills/karpathy-kb/scripts/new-topic.sh rust-systems "Rust Systems Programming" rust`

The script creates the standard directory tree (`raw/{articles,bookmarks,github}`, `wiki/{concepts,index}`, `outputs/{briefings,queries,diagrams}`, `bases/`), installs Dashboard / Concept Index / Source Index from `assets/`, and writes a topic `CLAUDE.md` stub plus an empty `log.md`. After the script finishes:

1. Add the topic as a new row in the vault-root `README.md` topic table.
2. (Optional, recommended at ~20+ sources) Create a qmd collection via the [qmd skill](https://github.com/pedronauck/skills/tree/main/skills/qmd): `qmd collection add <topic-slug>/ --name <topic-slug> && qmd embed`. At smaller scale, the topic's Concept Index + Source Index are sufficient navigation — see `references/tooling-tips.md`.
3. Start ingesting sources (Procedure 2).

### Procedure 2: Ingest a raw source

1. Scrape the URL with the [firecrawl skill](https://github.com/pedronauck/skills/tree/main/skills/firecrawl): `firecrawl scrape <url>` (single page) or `firecrawl crawl <url>` (multi-page).
2. Save the output to `<topic>/raw/articles/<descriptive-slug>.md` (or `raw/github/` for READMEs). Format the body as Obsidian Flavored Markdown — see the [obsidian-markdown skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-markdown) for wikilinks, callouts, and properties.
3. Prepend frontmatter — copy the matching schema from `references/frontmatter-schemas.md`. Fill `title`, `source_url`, `scraped` (today's ISO date), and topic-specific `tags`.
4. For TweetSmash bookmarks, pull clusters via the [tweetsmash-api skill](https://github.com/pedronauck/skills/tree/main/skills/tweetsmash-api) and save to `<topic>/raw/bookmarks/<Topic> Bookmarks <Subtopic>.md` using the bookmark-cluster frontmatter schema.
5. Re-index the topic's [qmd](https://github.com/pedronauck/skills/tree/main/skills/qmd) collection if one exists: `qmd collection remove <collection> && qmd collection add <topic>/ --name <collection> && qmd embed`.
6. Append an entry to `<topic>/log.md` (Procedure 7) — e.g., `## [YYYY-MM-DD] ingest | <slug>.md (<source_kind>)`.

### Procedure 3: Compile a wiki article

1. Read `references/compilation-guide.md` to anchor on length, style, wikilink density, and sourcing rules.
2. Identify candidate sources via the [qmd skill](https://github.com/pedronauck/skills/tree/main/skills/qmd) — `qmd query "<topic phrase>"` scoped to the topic's collection — or read `<topic>/wiki/index/Source Index.md`.
3. Load the candidate raw sources fully into context.
4. Load `<topic>/wiki/index/Concept Index.md` for orientation on existing articles and wikilink targets (including in other topics).
5. **Surface takeaways BEFORE drafting.** Present to the user: 3-5 key takeaways from the sources, the entities/concepts this article will introduce or update, and anything that contradicts existing wiki articles. Ask: *"Anything specific to emphasize or de-emphasize?"* Wait for the response. Skip this step only if the user has explicitly asked for autonomous compilation.
6. Write the article to `<topic>/wiki/concepts/<Article Title>.md` using `assets/wiki-article-template.md`, following the [obsidian-markdown skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-markdown) for wikilink, callout, and frontmatter syntax. Target 3000-4000 words with a Sources section, wikilinks to related articles, and code or diagram blocks where applicable.
7. **Backlink audit — do not skip.** Grep every existing article in `<topic>/wiki/concepts/` for mentions of the new article's title, aliases, or core entities. For each match, add a `[[New Article]]` wikilink at the first mention (and one later occurrence). This is the step most commonly skipped — a compounding wiki depends on bidirectional links.
   ```bash
   grep -rln "<new article title or key term>" <topic>/wiki/concepts/
   ```
8. Update the topic's indexes (Procedure 4).
9. Update `<topic>/CLAUDE.md` current-articles list.
10. Re-index the [qmd](https://github.com/pedronauck/skills/tree/main/skills/qmd) collection (if present).
11. Append an entry to `<topic>/log.md` (Procedure 7) — e.g., `## [YYYY-MM-DD] compile | <Article Title> (<word_count> words, <N> sources)`.

When **updating an existing article** (rather than writing new), use the `Current / Proposed / Reason / Source` diff format and contradiction-sweep workflow described in `references/compilation-guide.md`.

### Procedure 4: Maintain topic indexes

After adding, renaming, or removing any wiki article:

1. `<topic>/wiki/index/Dashboard.md` — update article count, total word count, featured sections, and any Obsidian Base embeds (use the [obsidian-bases skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-bases) to author `.base` files and embed them).
2. `<topic>/wiki/index/Concept Index.md` — insert/update the article row alphabetically with its one-line summary.
3. `<topic>/wiki/index/Source Index.md` — for each new article, append rows for every source it cites, with a wikilink back to the article.
4. Optionally refresh the live view in Obsidian with the [obsidian-cli skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-cli) (`obsidian open <path>`, `obsidian search <query>`).

### Procedure 5: Query the wiki and file back the answer

A query has two phases: **Phase A** produces the answer by reading the wiki (never from general knowledge); **Phase B** files the answer back so the exploration compounds.

**Precondition:** Identify which topic(s) the question belongs to. If the question spans topics, load each topic's Concept Index.

#### Phase A — Answer from the wiki

1. **Read the topic's Concept Index first** (`<topic>/wiki/index/Concept Index.md`). Scan the full index to identify candidate articles. Do NOT answer from general knowledge — the wiki is the source of truth, even when the answer seems obvious. A contradiction between the wiki and general knowledge is itself valuable signal.
2. **Locate relevant articles.** At small scale (<30 articles), the index is enough. At larger scale, supplement with `qmd query "<phrase>"` scoped to the topic's collection. Also grep the topic for keywords: `grep -rl "<keyword>" <topic>/wiki/concepts/`.
3. **Read the identified articles in full.** Follow one level of `[[wikilinks]]` when targets look relevant to the question. Stop at one hop — deeper traversal wastes context.
4. **(Optional) Pull in raw sources** if an article's claim is ambiguous and its `sources:` frontmatter points at a specific raw file worth verifying.
5. **Synthesize the answer** with these properties:
   - Grounded in the wiki articles you just read — every factual claim traces back to a `[[Wiki Article]]` citation.
   - Notes **agreements and disagreements** between articles when they exist.
   - Flags **gaps explicitly**: "The wiki has no article on X" or "[[Article Y]] does not yet cover Z".
   - Suggests follow-up **ingest targets** or open questions.
6. **Match format to question type:**
   - Factual → prose with inline `[[wikilink]]` citations.
   - Comparison → table with rows per alternative, citations in cells.
   - How-it-works → numbered steps with citations.
   - What-do-we-know-about-X → structured summary with "Known", "Open questions", "Gaps".
   - Visual → ASCII/Mermaid diagram, Marp deck (see `references/tooling-tips.md`), or matplotlib chart.

#### Phase B — File back the answer

7. **Save the answer** to `<topic>/outputs/queries/<YYYY-MM-DD> <Question Slug>.md` using the research-output frontmatter from `references/frontmatter-schemas.md` with `stage: query`.
8. In the body, list which wiki articles informed the answer under `informed_by:` (as wikilinks) and call out new insights that should be absorbed back into those articles on the next compile pass.
9. When a filed-back insight contradicts or extends an article's claims, **recompile the affected articles** (Procedure 3).
10. **Promote to wiki when the synthesis is durable.** If the answer is a first-class reference (a comparison table, a trade-off analysis, a new concept synthesized from multiple articles), copy it to `<topic>/wiki/concepts/<Title>.md` following Procedure 3 standards and update the indexes (Procedure 4). Karpathy's pattern treats strong query answers as wiki citizens, not just output artifacts.
11. **Append to `<topic>/log.md`** (Procedure 7) — e.g., `## [YYYY-MM-DD] query | <Question Slug>` plus a second line `## [YYYY-MM-DD] promote | <Title>` if promoted.

**Anti-patterns to avoid:**

- **Answering from memory** — always read the wiki pages. The wiki may contradict what you think you know.
- **No citations** — every factual claim must trace back to a `[[wikilink]]`.
- **Skipping the save** — good query answers compound the wiki's value. Always file to `outputs/queries/`; promote when durable.
- **Silent gaps** — surface missing coverage explicitly so the next ingest pass can fill it.

### Procedure 6: Lint and heal

Run from the vault root and tee the report to a dated artifact:

```bash
python3 .claude/skills/karpathy-kb/scripts/lint-wiki.py <topic>/ | tee <topic>/outputs/reports/$(date +%Y-%m-%d)-lint.md
```

Saving the report as a wiki artifact makes it referenceable (you can wikilink it from the heal-pass log entry) and gives a historical audit trail of the topic's health over time.

The script prints dead wikilinks, orphan articles, and missing source references. For each issue, **propose the fix with a diff before applying** — do not batch-apply changes:

- **Dead wikilink** — either create the missing article (Procedure 3) or rewrite the wikilink to point at an existing article.
- **Orphan article** — add incoming wikilinks from at least one related article, or remove the article if it is outside the topic's scope.
- **Missing source file** — an article's `sources:` frontmatter references a file absent from `raw/`. Either re-scrape (Procedure 2) or correct the reference.

For deeper self-healing checks (stale content, inconsistencies, missing-coverage suggestions), read `references/lint-procedure.md`. After the heal pass, append `## [YYYY-MM-DD] lint | <N> issues found, <M> fixed → [[YYYY-MM-DD-lint]]` to `<topic>/log.md`.

### Procedure 7: Append to log.md

Every ingest, compile, query, and lint operation ends by appending one line to `<topic>/log.md`. The log is an append-only, chronological audit trail — never rewrite history.

**Format** — each entry is a single H2 heading with a consistent prefix so the log stays grep-able:

```markdown
## [YYYY-MM-DD] <op> | <short description>
```

Where `<op>` is one of `ingest`, `compile`, `query`, `lint`, `promote`, or `split`.

**Examples:**

```markdown
## [2026-04-04] ingest | attention-is-all-you-need.md (paper)
## [2026-04-04] compile | Transformer Architecture (3847 words, 6 sources)
## [2026-04-04] query | 2026-04-04 flash-attention-vs-paged-attention.md
## [2026-04-04] promote | FlashAttention vs PagedAttention (from query)
## [2026-04-04] lint | 3 dead links, 1 orphan, all fixed
## [2026-04-05] split | "Inference Optimization" → KV Cache, Speculative Decoding
```

Optionally add a body paragraph under each entry with more context (key findings, source urls, decisions made). Keep entries terse — the log is for skimming, not prose.

**Quick recent-activity check** — the consistent prefix lets unix tools query the log:

```bash
grep "^## \[" <topic>/log.md | tail -10                  # last 10 events
grep "^## \[.*compile" <topic>/log.md | wc -l            # total compiles
grep "^## \[2026-04" <topic>/log.md                      # April 2026 events
```

Keep `log.md` at the topic root (not inside `wiki/` or `outputs/`) so it sits alongside `CLAUDE.md` as a first-class topic artifact.

## Error Handling

- **qmd collection not found** — create it via the [qmd skill](https://github.com/pedronauck/skills/tree/main/skills/qmd): `qmd collection add <topic>/ --name <collection> && qmd embed`.
- **Article exceeds 4000 words** — extract a sub-topic into its own article and wikilink to it, rather than padding.
- **Cross-topic wikilink ambiguity** — if two topics contain articles with the same title, disambiguate with the full path: `[[ai-harness/wiki/concepts/RAG Architecture Patterns|RAG]]`. See the [obsidian-markdown skill](https://github.com/pedronauck/skills/tree/main/skills/obsidian-markdown) for wikilink edge cases.
- **firecrawl returns truncated or missing content** — retry per the [firecrawl skill](https://github.com/pedronauck/skills/tree/main/skills/firecrawl): `firecrawl scrape <url> --format markdown --only-main-content`.
- **`lint-wiki.py` missing** — the script is at `.claude/skills/karpathy-kb/scripts/lint-wiki.py`; run from the vault root.
- **new-topic.sh refuses to run** — the target folder already exists. Remove it first or choose a new slug.
- **`log.md` missing in an existing topic** — create it from `assets/log-template.md` and backfill entries from git history: `git log --format='## [%ad] <op> | %s' --date=short <topic>/` gives a reasonable starting point.
- **Log entry conflicts with git** — the log is a human/LLM-readable audit trail, not a replacement for git. Let them coexist: git records *what changed*, `log.md` records *what the knowledge base did*.
