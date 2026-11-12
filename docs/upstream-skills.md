# Maintaining third-party skills

Published third-party skills stay in `skills/{curated,marketing}`. Consumers can continue installing a bucket with `npx skills add pedronauck/skills/skills/curated`. The maintainer workflow uses the native `skills` CLI in temporary projects, then copies the installed packages into their mapped catalogue directories.

## Commands

Requires Make, Python 3.10+, Node.js/npm, Git, and network access for remote checks or updates. Run from this repository (`make` alone lists the shortcuts):

```bash
# Offline inventory and local edit detection
make status

# Fetch upstream copies and compare without changing published skills or locks
make check

# Update all verified sources
make update

# Limit an operation to a bucket or a skill
make check BUCKET=curated
make update SKILL=context7
```

`SKILL` and `BUCKET` work with `status`, `check`, and `update`, and can be combined. Override `PYTHON` if needed. The underlying `python3 scripts/upstream-skills.py` commands remain available without Make, including repeated `--skill`/`--bucket` flags and initial `--bootstrap` adoption. Make propagates a nonzero command result as a failed target; it does not suppress reported differences or errors.

`check` returns 0 for a current, managed selection or intentionally excluded local/retired entries, 1 for differences, unmanaged verified entries, or unresolved origins, and 2 for an error. The full inventory intentionally continues to report sources that need investigation. `status` is an offline report. An update skips `local`, `retired`, and `unresolved` entries and prints their state.

Do not use bare `npx skills update` or `npx skills check` to maintain this catalogue. In the pinned CLI version **1.5.26**, `check` is an alias for the updating command, and project installs target `.agents/skills`. The wrapper's `check` runs installation only inside ignored staging directories. These behaviours were verified against the [CLI dispatcher](https://github.com/vercel-labs/skills/blob/d6b37f62ae23c3825b0ed16c73e123eee0a41fdc/src/cli.ts) and [installer](https://github.com/vercel-labs/skills/blob/d6b37f62ae23c3825b0ed16c73e123eee0a41fdc/src/installer.ts), including a real installation and overwrite experiment.

## Files and update behaviour

- [`upstream/sources.json`](../upstream/sources.json) maps every third-party bucket directory to its origin, upstream path/name, local name, evidence, and maintenance status. It also pins the native CLI version.
- [`upstream/skills-lock.json`](../upstream/skills-lock.json) contains the native project lock records produced by actual `npx skills add` installations. Its keys use upstream names.
- [`upstream/catalog-lock.json`](../upstream/catalog-lock.json) records the installed catalogue directory hashes, including local name aliases. It detects subsequent local changes before replacement.
- The root `skills-lock.json` belongs to the repository's development environment. The catalogue updater leaves it and the active `.agents/skills` and `.claude/skills` surfaces alone. Existing symlinks continue pointing at the published directories; deprecated skills remain outside those active links.

The wrapper installs each selected skill in a separate temporary project using this command shape:

```bash
DISABLE_TELEMETRY=1 npx --yes skills@1.5.26 add owner/repo/path/to/skill \
  --skill upstream-name --agent codex --copy --yes
```

It checks the resulting native lock and skill identity before publishing anything. All selected downloads must succeed first. A mismatch, missing source, or local edit stops the update. Initial migration replaces the copied external package with the current upstream package; only the published frontmatter `name` is preserved when it is an alias. Once managed, the updater refuses to overwrite local modifications, even with `--bootstrap`.

Backups of replaced directories and previous locks remain under `.tmp/upstream-skills/<run>/backup`, alongside installation logs. Publication errors trigger rollback from those backups. Review the Git diff after an update; the tool does not commit or publish changes. Backups are ignored local recovery files, not part of the distributed catalogue. An update process lock prevents overlapping update runs; after an interrupted process, inspect the recorded PID before removing a stale lock.

For a new external skill, verify its origin and add a manifest entry with the intended bucket destination. Then install or adopt only that entry:

```bash
python3 scripts/upstream-skills.py update --bootstrap --skill skills/curated/example
```

`--bootstrap` explicitly installs a new destination or adopts an unmanaged directory and saves its previous contents. It does not permit overwriting edits or resurrecting a deleted managed directory. Do not assign a same-name source without verifying matching content. Skills in `skills/mine` are outside this updater; owner-authored skills explicitly placed in `curated` use status `local` and are also excluded from upstream updates. Changing an existing native lock name to a different source/path fails explicitly; review the provenance change and migrate that lock entry deliberately rather than silently switching owners.

## Provenance and exceptions

The September 14, 2026 research covered all **102 original directories** in the four external/deprecated buckets using Exa searches, upstream file comparisons, and historical GitHub revisions where names or content changed: **71 verified installable sources, 4 retired sources, 9 local skills/adaptations, and 18 unresolved origins**. Of the 71 verified packages, 59 changed and 12 were already current at initial adoption. Consumer validation then identified 11 required Firecrawl sibling guides, bringing the manifest to **113 entries and 82 managed sources**. `verified` establishes provenance and an installable target; it does not certify the quality or continued maintenance of an upstream project.

The owner subsequently confirmed authorship of `centrifugo`, `effect-ts`, `shadcn`, `xstate`, `zustand`, `elysia`, `es-toolkit`, `evolution-api`, `electron-builder`, `electron-dev`, and `electron-release`. All 11 live in `curated` as explicitly requested, with no external source. Seven moved from community; four were already in curated. The current classification is **82 verified, 20 local, 6 unresolved, and 4 retired**. These local skills are never downloaded or replaced by the updater.

The autoresearch package has an upstream link to `references/eval-guide.md` although the file is at its root. A narrow manifest replacement repairs that link after each native install; the native lock retains the upstream hash while the catalogue lock reflects the correction. If the source changes so neither the old nor corrected text exists, installation fails for review. The `.gitignore` exception ensures this real skill package is included in the published repository.

The known alias retained for existing consumers is `context7` ← `find-docs`.

Retired entries are `next-best-practices` (retired by its author), `brand-storytelling` (removed during reorganization), and `fundraising` (deleted upstream by `oldwinter/skills` commit `4de594e780`, 2026-10-12). They retain their current content and historical references. `hormozi-ad-factory` is treated as local based on the dedicated Pedro commit and available provenance, with that inference explicitly noted.

For unresolved entries, the manifest records searches and rejected candidates. Absence of an external match is not proof of local authorship. These entries remain usable and untouched, without fabricated lock records.

### Catalogue cleanup (November 12, 2026)

The owner had deleted the `community` and `deprecated` buckets, the Firecrawl family, `mastra`, `exa-web-search-free`, the `pitch-*` skills, `pptx-creator`, `viz`, `elysia` and `evolution-api` from disk while their manifest entries remained, so the updater reported them as local edits and refused to run. Their 66 entries were removed from `sources.json`, both locks and the source table. Eight skills that had moved from `community` to `curated` (`ai-sdk`, `inngest`, `mermaid-diagrams`, `obsidian-bases`, `obsidian-cli`, `obsidian-markdown`, `requirements-clarity`, `tauri-v2`) now use their `curated` paths. The Obsidian skills moved upstream to `plugins/obsidian/skills/`; their manifest and native lock paths were migrated deliberately. Current inventory: **46 entries: 33 verified, 10 local, 3 retired**. A full `make update` and `make check` passed.

## Validation

The tooling suite owns destination/alias correctness, native lock validation, local edit protection, and rollback:

```bash
make test
```

Use a real remote update/check and a fresh native CLI consumer installation when changing the installer integration. Unit tests alone do not establish that upstream installation and bucket discovery work.

The initial migration passed 15 tooling tests and actual native installation of all 82 managed packages. Subsequent read-only checks passed for the alias/normalized-name sample and the corrected Firecrawl/autoresearch group. Local working-tree consumer installations validated all five buckets: curated 35, community 46, marketing 18, deprecated 14, and mine 40 — 153 names and 1,438 copied files, compared byte-for-byte. The four published aliases and all explicit local references in the active buckets resolved. Two existing sibling references in deprecated `cmux-orchestration` remain outside this migration's scope. The 31 excluded original entries, `skills/mine`, root lock, and existing active skill surfaces were preserved. This verifies the local working tree; the changes have not been committed or published to GitHub.

After the owner-confirmed reclassification, fresh native consumer installs passed for curated (42) and community (39). The moved directories retained identical contents, and the 14 existing active symlinks were updated to their new paths. Upstream package locks were unchanged.
