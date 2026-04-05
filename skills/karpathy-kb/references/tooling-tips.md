# Tooling Tips

Companion tooling and Obsidian plugins that accelerate the Karpathy KB workflow. All are optional — the core pattern only requires markdown files. Add them as scale demands.

## Obsidian Web Clipper (browser extension)

Converts web articles to clean markdown with a single click, writing directly into the vault. The fastest path for getting articles from browser → `<topic>/raw/articles/`.

- Install from the Obsidian Web Clipper page (official extension for Chrome/Firefox/Safari).
- Configure the default save location to `<topic>/raw/articles/` per topic.
- Configure a default template that includes `source_url`, `scraped`, and topic tags in frontmatter (match the raw-article schema in `frontmatter-schemas.md`).

After clipping, still run Procedure 2 steps 3-6 (frontmatter fix-up, re-index, log entry).

## Image download and asset handling

LLMs cannot reliably read markdown with inline images in a single pass. The workaround: download images locally so the LLM can view them separately when needed.

**Obsidian config:**

- Settings → Files and links → **Attachment folder path**: set to `raw/assets/` (or a per-topic attachments dir).
- Settings → Hotkeys → search "Download" → bind **"Download attachments for current file"** to a hotkey (e.g., Ctrl+Shift+D).

**Workflow:** after clipping an article with image URLs, press the hotkey — all referenced images download to the attachment folder and the markdown is rewritten to reference local files. The LLM then reads the text first, then views specific images separately for additional context.

## Dataview plugin

Runs SQL-like queries over page frontmatter. Useful when the LLM adds structured frontmatter (tags, dates, `source_count`) to wiki pages — Dataview turns that into dynamic tables without maintaining a separate index.

**Example:** list all wiki articles updated in the last 30 days, sorted by source count:

```dataview
TABLE updated, length(sources) AS "Sources"
FROM "ai-harness/wiki/concepts"
WHERE date(updated) > date(today) - dur(30 days)
SORT length(sources) DESC
```

Dataview complements the static `Concept Index.md` — keep the static index for LLM navigation and add Dataview blocks inside `Dashboard.md` for live views.

## Marp plugin

Converts markdown files to slide decks (PDF/HTML/PPTX). A query answer, a wiki article, or a comparison can be exported to a slide deck with zero extra authoring.

**Usage:**

- Add `marp: true` to the frontmatter of the file being presented.
- Use `---` separators between slides.
- Export via Marp's CLI or the Obsidian Marp plugin.

Useful for briefings in `<topic>/outputs/briefings/` that need to be shared as decks.

## qmd vs naked index tradeoffs

Karpathy's original pattern notes that at small scale, the static `index.md` (our `Concept Index.md` + `Source Index.md`) is sufficient — the LLM reads it to find relevant pages, then drills in. [qmd](https://github.com/tobi/qmd) (hybrid BM25 + vector search with LLM re-ranking, all local) becomes worth adding as the corpus grows.

**Heuristic:**

| Scale | Navigation |
|-------|-----------|
| 1-20 sources, <30 wiki articles | Concept Index + Source Index only |
| 20-50 sources, 30-80 articles | Add qmd collection, still read indexes first |
| 50+ sources, 80+ articles | qmd primary, indexes become secondary browsing aids |

The indexes never go away — they serve as the LLM's *mental model* of the topic. qmd serves as its *search tool*.

## Graph view

Obsidian's graph view is the fastest way to see the shape of a topic — what's central, what's orphan, what's overconnected. Run it after each lint pass to eyeball the structure. Orphan nodes in the graph corroborate orphan detection from `lint-wiki.py`.

## The wiki is just a git repo

No database, no server. Every commit is a reviewable checkpoint. Branch to experiment with a restructure without risking the main wiki. `git log --follow <article>.md` shows the full evolution of any concept. `git blame` shows which compile pass introduced which claim.
