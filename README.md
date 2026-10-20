# Pedro Nauck's Skills

A curated collection of **88 agent skills** for Claude Code and compatible AI coding assistants — **41 original** (⭐️), **34 hand-picked** (💎), and **13 marketing & business** (📣). Each skill provides domain-specific knowledge, best practices, and guided workflows that enhance an agent's ability to perform specialized tasks.

## Installation

### Quick install (recommended)

Install this repository into your agent skills directory with the [`skills`](https://www.npmjs.com/package/skills) CLI:

```bash
npx skills add https://github.com/pedronauck/skills
```

### Install a single bucket

Use the `owner/repo/<subpath>` shorthand to install only one bucket:

```bash
# Only the original skills
npx skills add pedronauck/skills/skills/mine

# Only the curated skills
npx skills add pedronauck/skills/skills/curated
```

You can also pin a specific skill with `--skill`:

```bash
npx skills add pedronauck/skills/skills/mine --skill react
```

### Manual install

Copy or symlink the skills you need into your Claude Code configuration:

```bash
# Copy a single skill
cp -r skills/mine/react ~/.claude/skills/react

# Or symlink an entire bucket
ln -s $(pwd)/skills/mine ~/.claude/skills/mine
```

Skills are organized into three top-level buckets:

- `skills/mine/` — 41 original skills authored in this repository (⭐️)
- `skills/curated/` — 34 hand-picked skills, including locally authored skills (💎)
- `skills/marketing/` — 13 marketing, business, and writing skills (📣)

## Usage

Skills are automatically picked up by Claude Code when placed in the `~/.claude/skills/` directory. The agent matches tasks to relevant skills based on the `description` field in each `SKILL.md` frontmatter.

## What are Skills?

Skills are structured instruction sets that give AI agents deep expertise in specific domains. Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file with metadata, procedures, and reference material. Skills follow the [agentskills.io](https://agentskills.io) specification.

## Skill Catalog

> ⭐️ = original skill authored in this repository &nbsp;·&nbsp; 💎 = hand-picked community skill &nbsp;·&nbsp; 📣 = marketing & business skill

### Mine ⭐️

Original skills authored in this repository.

- **[agent-exploration](./skills/mine/agent-exploration)** — Dispatch scoped-write explorer subagents in parallel through the current harness's native subagent facility for multi-area research — each slice writes one seven-section analysis file, and the parent synthesizes a summary
- **[app-renderer-systems](./skills/mine/app-renderer-systems)** — Domain feature systems organized under a `systems/` directory
- **[architectural-analysis](./skills/mine/architectural-analysis)** — Deep architectural audit for dead code, duplication, anti-patterns, and code smells
- **[bubbletea](./skills/mine/bubbletea)** — Build terminal UIs with Go and Bubbletea -- Elm architecture, Lipgloss styling, dual-pane layouts, and reusable components
- **[ddd-master](./skills/mine/ddd-master)** — Assess DDD fit and model language, bounded contexts, and aggregates using scoped references and existing domain evidence
- **[deep-review](./skills/mine/deep-review)** — Review branch diffs, working trees, and PRs with automated preparation, staged rule discovery, compact per-job assessments, targeted repairs, complete defect/polish coverage, and optional PR publication
- **[deslop](./skills/mine/deslop)** — Remove AI-generated code slop from the branch diff — unnecessary comments, abnormal defensive checks, `any` casts, deep nesting — before claiming a task complete or opening a PR
- **[drizzle-safe-migrations](./skills/mine/drizzle-safe-migrations)** — Production-safe Drizzle migration workflows for schema changes
- **[git-rebase](./skills/mine/git-rebase)** — Git rebase operations and merge conflict resolution with clean history
- **[glassmorphism](./skills/mine/glassmorphism)** — Glass and Apple Liquid Glass interfaces on the web at reference quality: a material anatomy (thin light fill, one locked light direction expressed as rim + inset highlight + sheen + tinted shadow, optional grain), three ink modes chosen by backdrop luminance (white on light tint, white on smoked tint, dark ink on white frost) with measured contrast, a solid-first `glass.css` token system with reduced-transparency / forced-colors / print fallbacks, geometry-derived SVG displacement refraction for small controls (Chromium-only, with the filter-region and chromatic-pass traps), a runnable material lab with seven backdrops and a live contrast estimate, a 22-item reference board, rendering-cost budgets and triage, and conditional SwiftUI / visionOS / Fluent / Expo routes
- **[golang-master](./skills/mine/golang-master)** — Go 1.21–1.26 engineering doctrine for any Go codebase — a ten-rule floor (error wrapping, goroutine ownership, context-first APIs, race-clean tests) plus branch-routed references: errors (sentinel vs typed, `%w` chains, single-handling rule, panic policy), concurrency (channel/mutex/atomic and WaitGroup/errgroup decision tables, `errgroup.SetLimit` pools, spawn checklist), context (cancellation discipline, `WithoutCancel` detachment, value hygiene), safety (nil interface trap, append aliasing, numeric truncation, defer-in-loop), interfaces & generics (consumer-side contracts, `cmp.Ordered` constraints), naming & style (anti-stutter, functional options, no `init()`), assertion-framework-free testing (table-driven, `synctest`, goleak, `b.Loop()`), pprof-first performance methodology, version-by-version modernization tables, and module layout. Supersedes the curated `golang-pro`
- **[herdr-orchestration](./skills/mine/herdr-orchestration)** — Orchestrate Claude and Codex worker TUIs from a controller agent — one worker per named herdr tab, driven over the herdr socket CLI; supports plan-first delegation (Claude Code plan mode, Codex Plan mode) and native agent-status waits; controller owns assignment, state, conflict control, integration, and retirement (verified workers' tabs are closed, never left piled up); workers launch as interactive TUIs via `herdr agent start`
- **[insta-master](./skills/mine/insta-master)** — Plan, create, distribute, and monetize Instagram content by combining two complementary methodologies (pt-BR): **Hyeser** (tactical creator, 421k — Reels, virality, engagement, faceless monetization) and **Rafael Kiso** (mLabs founder — algorithm-as-graph, per-surface retention, internal search/SEO/AEO, consumer journey, social-media-as-a-business), distilled from 8 deep-research slices over 344 transcripts — the retention + social-signals distribution engine with per-surface thresholds (Feed 10s / Explore 11s / Reels 15s) and a diagnosis funnel, the COCA×journey content matrix (Growth / Objection / Connection / Authority), Reels craft ("it's the start, not the 3 seconds", 33% retention rule, hook→development→loop structure, lo-fi CapCut editing, A/B test reels), modern discovery (caption-as-semantic-field with the Question→Answer template, hashtag-as-SEO timeline, AEO to appear in ChatGPT/IA), profile foundations (bio-promise, subniche, @name, 0→1000 plan, converting bio link), Stories & cadence (3-5 story blocks, the frequency band over a magic number, best-time myth), creator monetization & selling (sell-without-looking-like-an-ad 80/20, 4-step DM social selling, affiliate / clips / faceless-IA / IG Shop / infoproduct), social-media-as-a-business (value/ROI pricing, 4-pillar method, media kit, UGC × influencer × brandlover), a publication checklist, plus read-only `retencao-check.py` + `post-check.py` helpers
- **[jev-engineering](./skills/mine/jev-engineering)** — Design and build use cases, POCs and production systems with TypeSafe's Jev decision model (System One): design modes and use-case archetypes, decision state, typed questions, Jev combined with generative models, workflows, retrieval and perception, aggregation and gates in code, evaluation and rollout; covers the jev-1.14 danger-zone features (images, Box, long context); ships dependency-free Python/TypeScript clients (TypeSafe API, OpenRouter Decisions, Vercel AI Gateway) and a POC skeleton
- **[kb-yt-channel](./skills/mine/kb-yt-channel)** — Turn a YouTube channel into a Karpathy KB topic — resolves recent or full uploads, scaffolds `yt-channels` topics, ingests transcripts via `kb ingest youtube` (captions / auto / STT), and validates plus indexes the result
- **[no-workarounds](./skills/mine/no-workarounds)** — Enforce root-cause fixes over workarounds, hacks, and symptom patches
- **[qa-execution](./skills/mine/qa-execution)** — Run scoped dogfooding through public product interfaces, record findings in living QA docs, and repair within authorization; assess PR or release readiness when included in the request
- **[qa-report](./skills/mine/qa-report)** — Plan real-user QA as living repo docs: owns the canonical `docs/qa/` tree, merge-safe by construction — content-addressed ids and one file per scenario/bug/charter, so parallel branches never contend (enum-disciplined scenario tracker materialized into a gitignored `state.csv` view, global bug registry with the five-tier user-impact rubric, project personas, journey flowcharts, session charters, coverage taxonomy, automation backlog). Maps every user-visible change as a Mermaid journey flow *before* deriving scenarios (flows-before-matrix), plans persona×journey×tour session charters by cadence tier (smoke/targeted/full/sanity), and enforces "every journey walked by a persona this cycle" completeness — sessions, not test-case accumulation.
- **[react](./skills/mine/react)** — React 19 under the React Compiler — the Rules of React as a build-time contract (purity, immutability, refs, globals, static components) with each rule mapped to its `eslint-plugin-react-hooks` v7 lint rule, a memoization decision table for when `useMemo`/`useCallback`/`memo` still earn their place, the full bail-out catalogue (three hard syntax errors plus the silent `Todo` skips) with `"use no memo"` bisection and DevTools/healthcheck detection, compiler setup per bundler and incremental adoption, effects (anti-pattern catalogue, `useEffectEvent`, `useSyncExternalStore`), component and composition patterns, React 19 TypeScript migration (`ref` as prop, `React.JSX`, `useRef` arity) with codemods, state placement plus interior-mutability libraries, React 19/19.2 APIs (`use()`, Actions, `useOptimistic`, `<Activity>`, metadata, `cacheSignal`), and Vitest/RTL v16 testing
- **[refactoring-analysis](./skills/mine/refactoring-analysis)** — Identify refactoring opportunities using Martin Fowler's code smells catalog with prioritized reports
- **[rust-best-practices](./skills/mine/rust-best-practices)** — Unified Rust guidelines covering ownership, error handling, async/Tokio, traits, testing, performance, clippy, and documentation
- **[ship-pr](./skills/mine/ship-pr)** — End-of-feature ritual: explore impact across docs/site/README, generate release notes (via `pr-release` when present, else inline from `git log`), assemble a complete PR description (with QA artifacts when detected), commit per the repo's commitlint, open the PR via `gh`, and optionally launch a CodeRabbit review-watch loop. Optional integrations (`pr-release`, `skeeper`, `compozy`, QA artifacts) auto-detect and skip cleanly when absent.
- **[spec-peer-review](./skills/mine/spec-peer-review)** — Optional cross-LLM peer review of a spec (TechSpec/design doc/RFC/PRD) via Compozy — an independent model writes one scoped findings file (blockers/nits + READY/BLOCKED/NEEDS_REWORK) for user-directed incorporation. Project-agnostic with configurable `--ide`/`--model`/`--reasoning` runtime, six tech-agnostic quality markers, and auto-discovered project rules
- **[storybook-stories](./skills/mine/storybook-stories)** — Create, update, or refactor Storybook stories following project patterns
- **[tailwindcss](./skills/mine/tailwindcss)** — Tailwind CSS v4 patterns, design tokens, and tailwind-variants
- **[tanstack](./skills/mine/tanstack)** — TanStack Query, Router, and Form patterns for React — query keys, caching, mutations, prefetching, SSR/offline, file-based routes, search params, loaders, and Form validation
- **[tech-logos](./skills/mine/tech-logos)** — Install official tech brand logos from the Elements registry via shadcn
- **[testing-boss](./skills/mine/testing-boss)** — Choose owning test suites and independent behavioral oracles, use mocks at unit I/O boundaries, validate the relevant real integration, and diagnose flaky tests or agent evals without mandatory companion-test quotas
- **[to-prompt](./skills/mine/to-prompt)** — Create a handoff brief in `docs/prompts/` with relevant evidence, accepted user decisions, and unresolved implementation choices
- **[tweetsmash-api](./skills/mine/tweetsmash-api)** — TweetSmash REST API for fetching bookmarks, managing labels, filtering, and pagination
- **[typescript-advanced](./skills/mine/typescript-advanced)** — Advanced type system -- generics, conditional types, mapped types, template literals
- **[ui-craft](./skills/mine/ui-craft)** — Design and review UI using project authorities, observable usability and accessibility evidence, conditional design/performance references, and optional audit templates
- **[vc-outreach](./skills/mine/vc-outreach)** — Runs the investor-facing raise motion (list → meeting → pipeline → close): partner-level tiered target lists with disqualification and referrer mapping, warm-intro blurbs and cold emails that convert to first calls, meeting prep and objection handling, the parallel-process pipeline (batching, momentum, follow-ups, health benchmarks), and diligence through close (data room, references, term-sheet-to-wire). Distilled from a 625-source fundraising corpus (NFX, Paul Graham, First Round, YC, Hustle Fund, real founder funnels with numbers). Pairs with [vc-strategy](./skills/mine/vc-strategy) and [vc-pitch-deck](./skills/mine/vc-pitch-deck)
- **[vc-pitch-deck](./skills/mine/vc-pitch-deck)** — Builds and tears down investor decks: maps the fundraising narrative onto a slide sequence, enforces per-slide requirements (problem, solution, traction, market, team, ask), covers proof slides, and reviews decks against funded-deck patterns and DocSend attention telemetry — with send-ahead, presented, and demo-day variants and a per-slide teardown rubric. Benchmarks carry source and year because deck norms drift. Pairs with [vc-strategy](./skills/mine/vc-strategy) and [vc-outreach](./skills/mine/vc-outreach)
- **[vc-strategy](./skills/mine/vc-strategy)** — Designs the fundraise before any artifact exists: fundability assessment against what VCs actually evaluate, the fundraising narrative and value proposition (positioning, why-now), round design (when to raise, how much, valuation, SAFE vs priced, dilution, milestones), stage benchmarks, term-sheet economics and negotiation, and devtools/AI-infra positioning (open source, platform risk, developer traction). Numbers carry source and vintage. Pairs with [vc-pitch-deck](./skills/mine/vc-pitch-deck) and [vc-outreach](./skills/mine/vc-outreach)
- **[writing-agents-md](./skills/mine/writing-agents-md)** — Write and audit AGENTS.md/CLAUDE.md instructions: scope project rules, preserve canonical ownership, and make workflow authorization and stopping conditions explicit
- **[writing-skills](./skills/mine/writing-skills)** — Create, refactor, and debug agent skills: concise discovery descriptions, conditional reference loading, package authoring, static metadata checks, and diagnosis of missed references
- **[writing-tech-post](./skills/mine/writing-tech-post)** — Draft and edit engineering posts with supported claims, conditional structure/voice references, and publication checks scoped to the requested artifact
- **[xstate-store](./skills/mine/xstate-store)** — `@xstate/store` v4 event-driven state for TypeScript — a primitive-selection table (store / store logic / atom / XState machine), store core (transitions, `trigger`/`can`, Immer), `enqueue` effects with the synchronous-determinism rule, Standard Schema contracts plus opt-in `validateSchemas()`, selectors and atoms (derived, reducer, config, async), `createStoreLogic` with input and named selectors, the `persist` / `undoRedo` / `reset` extensions, `@xstate/store-react` v2 hooks with scope guidance, pure-`transition()` testing and `fromStore` XState interop, and a v3 → v4 migration path (plus a Zustand concept map). Every sample typechecked against 4.2.2
- **[yc-apply](./skills/mine/yc-apply)** — Drive a Y Combinator batch application end-to-end through a 10-phase workspace — captures the live YC form, profiles founders and stress-tests the idea via an embedded grill loop, runs a mandatory 5-agent parallel external-research pass on the startup, drafts every field with a buzzword scanner and a provenance-labeled accepted-answer rubric, generates founder-video bullet notes (no script), enforces a script-checked 10-check pre-submit gate, then unlocks a post-invite interview-prep simulator and reapplicant delta tracking. Built from 84 YC essays + 28 interview transcripts
- **[yt-master](./skills/mine/yt-master)** — Plan, package (title + thumbnail), script, and optimize YouTube videos by combining two complementary methodologies (pt-BR): **Escola Para Youtubers** (Caique — 50 transcripts; packaging-first / algorithm) and **Camilo Coutinho** (20-yr veteran — 100 transcripts; search SEO, sustainable production system, channel decisions), validated by real cross-channel metrics — the embrulho-primeiro production pyramid, 3 psychological thumbnail triggers (FOMO / pain+solution / objection-break) plus a data-driven post-publish thumbnail-swap, 8 metric-backed title formulas plus the 3 verbs (findable/clickable/shareable), a ≤30s hook with a named-technique library, block-based script template, the Problem-vs-Ambition payoff axis and an unblock gate (brain dump / camera fear), the 5-stage algorithm funnel (Impression → CTR → Retention → Satisfaction → Session) with myth-vs-reality and two discovery channels (internal funnel + Google search: 5-block description, rankable chapters, playlists), monetization & growth (YPP, YouTube Shopping, operational Brand Connect, sustainable production system "Fortaleza de Vídeos", community 15-min/day, dark/AI demonetization gate, copyright), channel decisions (naming, audience collision, restart/migrate), a publication checklist, and read-only `ctr-baseline.py` + `title-check.py` helpers

### Curated 💎

Hand-picked skills maintained in this repository, including locally authored skills placed here by the owner.

- **[agent-browser](./skills/curated/agent-browser)** — Automate browser interactions for testing, form filling, and data extraction
- **[ai-sdk](./skills/curated/ai-sdk)** — Vercel AI SDK for building AI-powered features
- **[autoresearch](./skills/curated/autoresearch)** — Autonomously optimize any skill by running evals, mutating prompts, and keeping improvements
- **[centrifugo](./skills/curated/centrifugo)** — Centrifugo real-time messaging -- WebSocket PUB/SUB, channels, JWT auth, scaling
- **[context7](./skills/curated/context7)** — Retrieve up-to-date technical documentation, API references, and code examples for any library via Context7 CLI
- **[documentation-writer](./skills/curated/documentation-writer)** — Diátaxis-guided technical writing across tutorials, how-to guides, reference, and explanation quadrants
- **[effect-ts](./skills/curated/effect-ts)** — Effect-TS code including setup, data modeling, error handling, and `Context.Tag`
- **[electron-builder](./skills/curated/electron-builder)** — Electron packaging, code signing, auto-updates, and release workflows
- **[electron-dev](./skills/curated/electron-dev)** — Electron development with Electron Vite and Builder -- main/renderer processes, IPC
- **[electron-release](./skills/curated/electron-release)** — Electron production builds, notarization, auto-updates, and releases
- **[es-toolkit](./skills/curated/es-toolkit)** — Modern utility library as a lodash replacement -- array, object, string operations
- **[extreme-software-optimization](./skills/curated/extreme-software-optimization)** — Profile-driven performance optimization with behavior proofs, opportunity scoring, and isomorphism guarantees
- **[hono](./skills/curated/hono)** — Hono framework development with documentation search and API reference
- **[inngest](./skills/curated/inngest)** — Serverless background jobs, event-driven workflows, and durable execution
- **[lesson-learned](./skills/curated/lesson-learned)** — Extract software engineering lessons from git history and recent code changes
- **[mermaid-diagrams](./skills/curated/mermaid-diagrams)** — Software diagrams using Mermaid syntax -- class, sequence, flowcharts, ERD, C4
- **[next-best-practices](./skills/curated/next-best-practices)** — Next.js best practices -- file conventions, RSC boundaries, data patterns, async APIs, metadata, error handling, and optimization
- **[obsidian-bases](./skills/curated/obsidian-bases)** — Create and edit Obsidian Bases (`.base` files) with views, filters, formulas, and summaries
- **[obsidian-cli](./skills/curated/obsidian-cli)** — Interact with Obsidian vaults via CLI -- read, create, search, manage notes, and develop plugins
- **[obsidian-markdown](./skills/curated/obsidian-markdown)** — Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and tags
- **[qmd](./skills/curated/qmd)** — Search markdown knowledge bases, notes, and documentation using QMD
- **[requirements-clarity](./skills/curated/requirements-clarity)** — Clarify ambiguous requirements through focused dialogue before implementation
- **[sentry-cli](./skills/curated/sentry-cli)** — Sentry CLI for interacting with Sentry from the command line
- **[shadcn](./skills/curated/shadcn)** — Building UI components with shadcn/ui, Radix UI primitives, and design tokens
- **[systematic-debugging](./skills/curated/systematic-debugging)** — Root-cause investigation before proposing fixes for bugs or test failures
- **[tauri-v2](./skills/curated/tauri-v2)** — Tauri v2 cross-platform apps with Rust backend, IPC, permissions, and builds
- **[tui-design](./skills/curated/tui-design)** — Universal TUI design patterns -- layouts, color schemes, keyboard navigation, dashboards, and accessibility
- **[vercel-composition-patterns](./skills/curated/vercel-composition-patterns)** — React composition patterns for refactoring boolean prop proliferation
- **[vercel-react-best-practices](./skills/curated/vercel-react-best-practices)** — React/Next.js performance optimization from Vercel Engineering
- **[verification-before-completion](./skills/curated/verification-before-completion)** — Run verification commands and confirm output before claiming success
- **[vitest](./skills/curated/vitest)** — Fast unit testing with Vite -- Jest-compatible API, mocking, coverage, and fixtures
- **[xstate](./skills/curated/xstate)** — XState v5 state machines, actors, and TanStack Query integration (for `@xstate/store` v4, use [xstate-store](./skills/mine/xstate-store))
- **[zod](./skills/curated/zod)** — Zod schema validation for type safety, parsing, and error handling
- **[zustand](./skills/curated/zustand)** — Zustand state management patterns, store organization, and best practices

### Marketing 📣

Marketing, sales, business, and writing skills.

- **[alex-hormozi-pitch](./skills/marketing/alex-hormozi-pitch)** — Create irresistible offers using Hormozi's $100M Offers methodology
- **[brand-storytelling](./skills/marketing/brand-storytelling)** — Craft compelling brand narratives and positioning
- **[content-research-writer](./skills/marketing/content-research-writer)** — Writing partner for research, outlining, drafting, and refining content
- **[copywriting](./skills/marketing/copywriting)** — Conversion copywriting for marketing pages, CTAs, and headlines
- **[fundraising](./skills/marketing/fundraising)** — Plan and run early-stage fundraising with pitch narrative, investor pipeline, and outreach
- **[google-ads](./skills/marketing/google-ads)** — Query, audit, and optimize Google Ads campaigns
- **[hormozi-ad-factory](./skills/marketing/hormozi-ad-factory)** — Generate 150-750+ ad variations using Hormozi's combinatorial Hook x Meat x CTA framework
- **[humanizer](./skills/marketing/humanizer)** — Remove signs of AI-generated writing from text
- **[professional-communication](./skills/marketing/professional-communication)** — Technical communication for emails, team messaging, and meeting agendas
- **[promo-video](./skills/marketing/promo-video)** — Create promotional videos using Remotion with AI voiceover and background music
- **[sales-methodology-implementer](./skills/marketing/sales-methodology-implementer)** — Implement proven sales methodologies (MEDDIC, BANT, Sandler, Challenger, SPIN)
- **[startup-validator](./skills/marketing/startup-validator)** — Comprehensive startup idea validation and market analysis
- **[writing-clearly-and-concisely](./skills/marketing/writing-clearly-and-concisely)** — Strunk's timeless rules for clearer, stronger, more professional prose

## Structure

Each skill follows a consistent directory layout:

```
skills/
  mine/<skill-name>/       # Original skills authored here (⭐️)
  curated/<skill-name>/    # Hand-picked community skills (💎)
  marketing/<skill-name>/  # Marketing, business, and writing skills (📣)

skills/<bucket>/<skill-name>/
  SKILL.md              # Main skill definition (required)
  references/           # Deep-dive reference material
  examples/             # Usage examples and patterns
  templates/            # Code templates and scaffolds
  scripts/              # Automation scripts and validators
  checklists/           # Step-by-step verification checklists
```

## Contributing

### Updating imported skills

Third-party skills are tracked in [`upstream/sources.json`](./upstream/sources.json), including original repositories, renamed skills, and sources that are retired or still unverified. Keep their published files in `skills/` and use the maintainer command:

```bash
make check
make update
# Or update one skill:
make update SKILL=context7
```

Use `make status` for the offline inventory, `make check BUCKET=curated` to select a bucket, and `make` to see all shortcuts.

This runs the native `npx skills add` in isolated staging projects, preserves bucket paths and published names, and protects subsequent local edits. It uses separate catalogue locks under `upstream/`; the root development-environment lock is untouched. See [the maintenance guide](./docs/upstream-skills.md) for setup, backups, source exceptions, and adding a new tracked skill. Bare `npx skills check` is not a read-only catalogue check in the pinned CLI version.

### Adding skills

To add a new skill:

1. Create a directory under the appropriate bucket with a lowercase, hyphenated name:
   - `skills/mine/` — original work authored here
   - `skills/curated/` — hand-picked, high-quality community skills you maintain
   - `skills/marketing/` — marketing, sales, business, or writing skills
2. Add a `SKILL.md` with proper frontmatter (`name` and `description` fields)
3. Include reference material, examples, and templates as needed
4. Follow the conventions documented in `skills/mine/writing-skills/SKILL.md`

## License

See repository root for license information.
