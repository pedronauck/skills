# Frontmatter Schemas

All notes in the vault use YAML frontmatter for metadata. The subfolder path identifies the topic; the `domain` field is a shortcut for Bases and qmd queries.

Conventions:

- `domain: <short-slug>` identifies the topic (e.g., `ai` for `ai-harness/`).
- `created` and `updated` use ISO date format `YYYY-MM-DD`.
- `tags` always include the domain plus the note type plus topic-specific tags.
- `sources` entries are wikilinks pointing at files in `raw/`.

---

## Wiki article — `<topic>/wiki/concepts/<Article Title>.md`

```yaml
---
title: Article Title
type: wiki
stage: compiled
domain: <topic-domain>
tags:
  - <topic-domain>
  - wiki
  - topic-specific-tag
  - another-topic-tag
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[Source File Name]]"
  - "[[Another Source]]"
---
```

## Raw article — `<topic>/raw/articles/<slug>.md`

```yaml
---
title: Descriptive Title
type: source
stage: raw
domain: <topic-domain>
source_kind: article
source_url: https://example.com/article
scraped: YYYY-MM-DD
tags:
  - <topic-domain>
  - raw
  - topic-specific-tag
---
```

`source_kind` values: `article`, `github-readme`, `documentation`, `paper`, `blog-post`, `whitepaper`.

## GitHub README — `<topic>/raw/github/<slug>.md`

```yaml
---
title: Repository or Doc Title
type: source
stage: raw
domain: <topic-domain>
source_kind: github-readme
source_url: https://github.com/owner/repo
scraped: YYYY-MM-DD
tags:
  - <topic-domain>
  - raw
  - github
  - topic-specific-tag
---
```

## Bookmark cluster — `<topic>/raw/bookmarks/<Topic> Bookmarks <Subtopic>.md`

```yaml
---
title: <Topic> Bookmarks <Subtopic>
type: source
stage: raw
domain: <topic-domain>
source_kind: bookmark-cluster
status: seeded
created: YYYY-MM-DD
updated: YYYY-MM-DD
source_urls:
  - https://twitter.com/user/status/123
  - https://twitter.com/user/status/456
tags:
  - <topic-domain>
  - bookmarks
  - raw
  - topic-specific-tag
---
```

`status` values: `seeded`, `enriched`, `archived`.

## Research output — `<topic>/outputs/queries/<YYYY-MM-DD> <slug>.md`

```yaml
---
title: Output Title
type: output
stage: query
domain: <topic-domain>
tags:
  - <topic-domain>
  - output
  - query
  - topic-specific-tag
created: YYYY-MM-DD
updated: YYYY-MM-DD
informed_by:
  - "[[Wiki Article 1]]"
  - "[[Wiki Article 2]]"
---
```

`stage` values for outputs: `briefing`, `query`, `diagram`, `lint-report`.

## Lint report — `<topic>/outputs/reports/<YYYY-MM-DD>-lint.md`

```yaml
---
title: Lint Report YYYY-MM-DD
type: output
stage: lint-report
domain: <topic-domain>
tags:
  - <topic-domain>
  - output
  - lint-report
created: YYYY-MM-DD
issues_found: N
issues_fixed: M
---
```

## Topic index — Dashboard / Concept Index / Source Index

These files are human-browsed hubs, not research notes. Keep frontmatter minimal:

```yaml
---
title: Dashboard
type: index
domain: <topic-domain>
updated: YYYY-MM-DD
---
```

## Quick reference

| File type | Path | type | stage |
|-----------|------|------|-------|
| Wiki article | `wiki/concepts/` | `wiki` | `compiled` |
| Raw article | `raw/articles/` | `source` | `raw` |
| Raw GitHub | `raw/github/` | `source` | `raw` |
| Raw bookmarks | `raw/bookmarks/` | `source` | `raw` |
| Briefing | `outputs/briefings/` | `output` | `briefing` |
| Query result | `outputs/queries/` | `output` | `query` |
| Diagram | `outputs/diagrams/` | `output` | `diagram` |
| Lint report | `outputs/reports/` | `output` | `lint-report` |
| Index | `wiki/index/` | `index` | — |
