# Pedro Nauck's Skills

A curated collection of **129 agent skills** for Claude Code and compatible AI coding assistants — **35 original** (⭐️), **30 hand-picked** (💎), **18 marketing & business** (📣), plus **46 community** skills. Each skill provides domain-specific knowledge, best practices, and guided workflows that enhance an agent's ability to perform specialized tasks.

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

Skills are organized into four top-level buckets:

- `skills/mine/` — 35 original skills authored in this repository (⭐️)
- `skills/curated/` — 30 hand-picked community skills (💎)
- `skills/marketing/` — 18 marketing, business, and writing skills (📣)
- `skills/community/` — 46 broader community skills

## Usage

Skills are automatically picked up by Claude Code when placed in the `~/.claude/skills/` directory. The agent matches tasks to relevant skills based on the `description` field in each `SKILL.md` frontmatter.

## What are Skills?

Skills are structured instruction sets that give AI agents deep expertise in specific domains. Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file with metadata, procedures, and reference material. Skills follow the [agentskills.io](https://agentskills.io) specification.

## Skill Catalog

> ⭐️ = original skill authored in this repository &nbsp;·&nbsp; 💎 = hand-picked community skill &nbsp;·&nbsp; 📣 = marketing & business skill

### Mine ⭐️

Original skills authored in this repository.

- **[agent-exploration](./skills/mine/agent-exploration)** — Dispatch scoped-write explorer subagents in parallel for codebase/topic research — each writes one analysis file to a seven-section schema, and the parent synthesizes a summary
- **[agent-output-audit](./skills/mine/agent-output-audit)** — Independent audit of AI-implemented work / Compozy task slugs / AI-authored PRs. Runs the independent-evaluator protocol on implementer transcripts, scans test diffs for RF-1..RF-6 red flags (skipped tests, weakened assertions, mocks hiding integration, snapshot drift), reconciles `task_NN.md` frontmatter `status:` against evidence, runs the canonical CI gate with flaky-test triage, and emits a Quality Gates verdict. Integrates with `cy-codex-loop` slugs at `.compozy/tasks/<slug>/`.
- **[app-renderer-systems](./skills/mine/app-renderer-systems)** — Domain feature systems organized under a `systems/` directory
- **[architectural-analysis](./skills/mine/architectural-analysis)** — Deep architectural audit for dead code, duplication, anti-patterns, and code smells
- **[bubbletea](./skills/mine/bubbletea)** — Build terminal UIs with Go and Bubbletea -- Elm architecture, Lipgloss styling, dual-pane layouts, and reusable components
- **[deep-review](./skills/mine/deep-review)** — CodeRabbit-grade deep review of a branch diff, working tree, or GitHub PR at any size (no file cap) — funnels changed files into cohorts, fans out parallel hunk-level reviewers with checkout-verified evidence discipline, merges findings mechanically, and emits a walkthrough, severity-tagged findings with committable suggestions plus AI-agent fix prompts, and a SHIP/FIX_BEFORE_SHIP/REWORK verdict — with incremental re-reviews, optional PR publishing, cross-LLM `--subagent` runtimes, and `--spec` conformance gating
- **[deslop](./skills/mine/deslop)** — Remove AI-generated code slop from the branch diff — unnecessary comments, abnormal defensive checks, `any` casts, deep nesting — before claiming a task complete or opening a PR
- **[drizzle-safe-migrations](./skills/mine/drizzle-safe-migrations)** — Production-safe Drizzle migration workflows for schema changes
- **[git-rebase](./skills/mine/git-rebase)** — Git rebase operations and merge conflict resolution with clean history
- **[herdr-orchestration](./skills/mine/herdr-orchestration)** — Orchestrate Claude and Codex worker TUIs from a controller agent through herdr panes and the herdr socket CLI — supports plan-first delegation (Claude Code plan mode, Codex Plan mode) and native agent-status waits; controller owns assignment, state, conflict control, integration, and retirement (verified workers' panes are closed, never left piled up); workers launch as interactive TUIs via `herdr agent start`
- **[impl-peer-review](./skills/mine/impl-peer-review)** — Optional cross-LLM peer review of an implementation diff via Compozy — an independent model writes one scoped findings file (blockers/risks/nits + SHIP/FIX/REWORK verdict) for user-directed remediation. Project-agnostic with configurable `--ide`/`--model`/`--reasoning` runtime, auto-detected `--verify` gate, and auto-discovered project rules
- **[insta-master](./skills/mine/insta-master)** — Plan, create, distribute, and monetize Instagram content by combining two complementary methodologies (pt-BR): **Hyeser** (tactical creator, 421k — Reels, virality, engagement, faceless monetization) and **Rafael Kiso** (mLabs founder — algorithm-as-graph, per-surface retention, internal search/SEO/AEO, consumer journey, social-media-as-a-business), distilled from 8 deep-research slices over 344 transcripts — the retention + social-signals distribution engine with per-surface thresholds (Feed 10s / Explore 11s / Reels 15s) and a diagnosis funnel, the COCA×journey content matrix (Growth / Objection / Connection / Authority), Reels craft ("it's the start, not the 3 seconds", 33% retention rule, hook→development→loop structure, lo-fi CapCut editing, A/B test reels), modern discovery (caption-as-semantic-field with the Question→Answer template, hashtag-as-SEO timeline, AEO to appear in ChatGPT/IA), profile foundations (bio-promise, subniche, @name, 0→1000 plan, converting bio link), Stories & cadence (3-5 story blocks, the frequency band over a magic number, best-time myth), creator monetization & selling (sell-without-looking-like-an-ad 80/20, 4-step DM social selling, affiliate / clips / faceless-IA / IG Shop / infoproduct), social-media-as-a-business (value/ROI pricing, 4-pillar method, media kit, UGC × influencer × brandlover), a publication checklist, plus read-only `retencao-check.py` + `post-check.py` helpers
- **[kb-yt-channel](./skills/mine/kb-yt-channel)** — Turn a YouTube channel into a Karpathy KB topic — resolves recent or full uploads, scaffolds `yt-channels` topics, ingests transcripts via `kb ingest youtube` (captions / auto / STT), and validates plus indexes the result
- **[no-workarounds](./skills/mine/no-workarounds)** — Enforce root-cause fixes over workarounds, hacks, and symptom patches
- **[qa-execution](./skills/mine/qa-execution)** — Run real-user dogfooding sessions through public interfaces: persona-driven journey walks via browser under strict persona-fidelity guardrails (no dev shortcuts, stall-is-a-finding, evaluator framing forbidden), thematic tours, user edge probes, experiential lenses, and paper-cut hunting. Reads plans from the living `docs/qa/` tree, dedups against the global bug registry before filing, applies the fix-loop governor (auto-fix only small and contained, with a red-before/green-after regression test; escalate the rest to "Decisions for a Human"), updates scenario-file verdicts, and writes an incremental per-run report — session debriefs included — created the moment the session matrix exists, with a full-suite exit gate before Final Status.
- **[qa-report](./skills/mine/qa-report)** — Plan real-user QA as living repo docs: owns the canonical `docs/qa/` tree, merge-safe by construction — content-addressed ids and one file per scenario/bug/charter, so parallel branches never contend (enum-disciplined scenario tracker materialized into a gitignored `state.csv` view, global bug registry with the five-tier user-impact rubric, project personas, journey flowcharts, session charters, coverage taxonomy, automation backlog). Maps every user-visible change as a Mermaid journey flow *before* deriving scenarios (flows-before-matrix), plans persona×journey×tour session charters by cadence tier (smoke/targeted/full/sanity), and enforces "every journey walked by a persona this cycle" completeness — sessions, not test-case accumulation.
- **[react](./skills/mine/react)** — Component architecture, hooks, state management, TypeScript integration, and testing
- **[refactoring-analysis](./skills/mine/refactoring-analysis)** — Identify refactoring opportunities using Martin Fowler's code smells catalog with prioritized reports
- **[rust-best-practices](./skills/mine/rust-best-practices)** — Unified Rust guidelines covering ownership, error handling, async/Tokio, traits, testing, performance, clippy, and documentation
- **[ship-pr](./skills/mine/ship-pr)** — End-of-feature ritual: explore impact across docs/site/README, generate release notes (via `pr-release` when present, else inline from `git log`), assemble a complete PR description (with QA artifacts when detected), commit per the repo's commitlint, open the PR via `gh`, and optionally launch a CodeRabbit review-watch loop. Optional integrations (`pr-release`, `skeeper`, `compozy`, QA artifacts) auto-detect and skip cleanly when absent.
- **[spec-peer-review](./skills/mine/spec-peer-review)** — Optional cross-LLM peer review of a spec (TechSpec/design doc/RFC/PRD) via Compozy — an independent model writes one scoped findings file (blockers/nits + READY/BLOCKED/NEEDS_REWORK) for user-directed incorporation. Project-agnostic with configurable `--ide`/`--model`/`--reasoning` runtime, six tech-agnostic quality markers, and auto-discovered project rules
- **[storybook-stories](./skills/mine/storybook-stories)** — Create, update, or refactor Storybook stories following project patterns
- **[tailwindcss](./skills/mine/tailwindcss)** — Tailwind CSS v4 patterns, design tokens, and tailwind-variants
- **[tanstack](./skills/mine/tanstack)** — TanStack Query, Router, and Form patterns for React — query keys, caching, mutations, prefetching, SSR/offline, file-based routes, search params, loaders, and Form validation
- **[tech-logos](./skills/mine/tech-logos)** — Install official tech brand logos from the Elements registry via shadcn
- **[testing-boss](./skills/mine/testing-boss)** — Comprehensive testing doctrine — Iron Laws, 12 positive patterns, 25 anti-patterns across five families, 7 mandatory gates for agents writing tests, flaky-test taxonomy with quarantine workflow, contract / property / mutation testing, and an LLM/agent eval primer (oracle ladder, LLM-as-judge calibration, agent trajectory vs outcome)
- **[to-prompt](./skills/mine/to-prompt)** — Turn code, issues, or context into a handoff brief for another LLM — full context, zero prescribed solution — written from a bundled template to `docs/prompts/<timestamp>_<slug>.md`
- **[tweetsmash-api](./skills/mine/tweetsmash-api)** — TweetSmash REST API for fetching bookmarks, managing labels, filtering, and pagination
- **[typescript-advanced](./skills/mine/typescript-advanced)** — Advanced type system -- generics, conditional types, mapped types, template literals
- **[ui-craft](./skills/mine/ui-craft)** — Anti-AI-slop guardrails for UI/UX work — usability heuristics, accessibility floors, design-system discipline, 14 named slop patterns with severity tags, tunable design dials (`VISUAL_VARIANCE`/`MOTION_INTENSITY`/`INFORMATION_DENSITY`), scene-driven decisions, Product vs Brand registers, anti-defaults blocklist, 7 named UI archetypes, plus performance / motion / dark-mode reference packs and executable contrast + token-drift scripts
- **[writing-agents-md](./skills/mine/writing-agents-md)** — Author lean AGENTS.md/CLAUDE.md files as resident system-prompt context — the three-part rent test (delta / frequency / economy) per line, a scope ladder from global CLAUDE.md down to linked docs, form rules for rules that bind (no examples, no emphasis inflation), and Write / Trim / Gate branches
- **[writing-skills](./skills/mine/writing-skills)** — Author, refactor, and debug agent skills: agentskills.io authoring procedure with metadata validator, the predictability doctrine (information hierarchy, pruning, leading words, descriptions, failure modes) with full glossary, and a loading-diagnosis pass for references the agent ignores (pointer-strength ladder). Merges the former skill-best-practices, writing-great-skills, and skill-load-tips
- **[writing-tech-post](./skills/mine/writing-tech-post)** — SOTA authoring loop for engineering blog posts — 8 archetype contracts (launch / postmortem / migration / performance / tutorial / research-translation / AI-agent / security), 5-rung abstraction ladder with rung-whiplash diagnostic, 12-form evidence taxonomy with `claim → artifact → reading` cadence, 7-publisher voice matrix, four disclosure contracts (blameless / coordinated-disclosure / paper-link-first / what-we'd-do-differently), narrative arcs + closer taxonomy, and a read-only `lint-post.py` pre-publish gate
- **[yc-apply](./skills/mine/yc-apply)** — Drive a Y Combinator batch application end-to-end through a 10-phase workspace — captures the live YC form, profiles founders and stress-tests the idea via an embedded grill loop, runs a mandatory 5-agent parallel external-research pass on the startup, drafts every field with a buzzword scanner and a provenance-labeled accepted-answer rubric, generates founder-video bullet notes (no script), enforces a script-checked 10-check pre-submit gate, then unlocks a post-invite interview-prep simulator and reapplicant delta tracking. Built from 84 YC essays + 28 interview transcripts
- **[yt-master](./skills/mine/yt-master)** — Plan, package (title + thumbnail), script, and optimize YouTube videos by combining two complementary methodologies (pt-BR): **Escola Para Youtubers** (Caique — 50 transcripts; packaging-first / algorithm) and **Camilo Coutinho** (20-yr veteran — 100 transcripts; search SEO, sustainable production system, channel decisions), validated by real cross-channel metrics — the embrulho-primeiro production pyramid, 3 psychological thumbnail triggers (FOMO / pain+solution / objection-break) plus a data-driven post-publish thumbnail-swap, 8 metric-backed title formulas plus the 3 verbs (findable/clickable/shareable), a ≤30s hook with a named-technique library, block-based script template, the Problem-vs-Ambition payoff axis and an unblock gate (brain dump / camera fear), the 5-stage algorithm funnel (Impression → CTR → Retention → Satisfaction → Session) with myth-vs-reality and two discovery channels (internal funnel + Google search: 5-block description, rankable chapters, playlists), monetization & growth (YPP, YouTube Shopping, operational Brand Connect, sustainable production system "Fortaleza de Vídeos", community 15-min/day, dark/AI demonetization gate, copyright), channel decisions (naming, audience collision, restart/migrate), a publication checklist, and read-only `ctr-baseline.py` + `title-check.py` helpers

### Curated 💎

Hand-picked community skills maintained in this repository.

- **[agent-browser](./skills/curated/agent-browser)** — Automate browser interactions for testing, form filling, and data extraction
- **[architecture-diagram](./skills/curated/architecture-diagram)** — Professional dark-themed system architecture diagrams as standalone HTML/SVG files
- **[autoresearch](./skills/curated/autoresearch)** — Autonomously optimize any skill by running evals, mutating prompts, and keeping improvements
- **[brainstorming](./skills/curated/brainstorming)** — Explore intent, requirements, and design through collaborative dialogue
- **[context7](./skills/curated/context7)** — Retrieve up-to-date technical documentation, API references, and code examples for any library via Context7 CLI
- **[documentation-writer](./skills/curated/documentation-writer)** — Diátaxis-guided technical writing across tutorials, how-to guides, reference, and explanation quadrants
- **[effect-ts](./skills/curated/effect-ts)** — Effect-TS code including setup, data modeling, error handling, and `Context.Tag`
- **[exa-web-search-free](./skills/curated/exa-web-search-free)** — Free AI-powered web, code, and company search via Exa MCP
- **[extreme-software-optimization](./skills/curated/extreme-software-optimization)** — Profile-driven performance optimization with behavior proofs, opportunity scoring, and isomorphism guarantees
- **[firecrawl](./skills/curated/firecrawl)** — Web scraping, search, crawling, and browser automation via the Firecrawl CLI
- **[game-changing-features](./skills/curated/game-changing-features)** — Find 10x product opportunities and high-leverage improvements
- **[golang-pro](./skills/curated/golang-pro)** — Concurrent Go patterns, microservices with gRPC/REST, pprof optimization, generics, and idiomatic error handling
- **[hono](./skills/curated/hono)** — Hono framework development with documentation search and API reference
- **[impeccable](./skills/curated/impeccable)** — Production-grade frontend design and iteration — bold or quiet redesigns, live UI iteration, visual hierarchy, accessibility, motion, and design-token discipline backed by real working code
- **[lesson-learned](./skills/curated/lesson-learned)** — Extract software engineering lessons from git history and recent code changes
- **[mastra](./skills/curated/mastra)** — Mastra framework for building AI agents and workflows
- **[next-best-practices](./skills/curated/next-best-practices)** — Next.js best practices -- file conventions, RSC boundaries, data patterns, async APIs, metadata, error handling, and optimization
- **[qmd](./skills/curated/qmd)** — Search markdown knowledge bases, notes, and documentation using QMD
- **[ratatui-tui](./skills/curated/ratatui-tui)** — Terminal UIs with ratatui v0.30.0+ -- Elm Architecture, StatefulWidget, async events
- **[sentry-cli](./skills/curated/sentry-cli)** — Sentry CLI for interacting with Sentry from the command line
- **[shadcn](./skills/curated/shadcn)** — Building UI components with shadcn/ui, Radix UI primitives, and design tokens
- **[systematic-debugging](./skills/curated/systematic-debugging)** — Root-cause investigation before proposing fixes for bugs or test failures
- **[tui-design](./skills/curated/tui-design)** — Universal TUI design patterns -- layouts, color schemes, keyboard navigation, dashboards, and accessibility
- **[vercel-composition-patterns](./skills/curated/vercel-composition-patterns)** — React composition patterns for refactoring boolean prop proliferation
- **[vercel-react-best-practices](./skills/curated/vercel-react-best-practices)** — React/Next.js performance optimization from Vercel Engineering
- **[verification-before-completion](./skills/curated/verification-before-completion)** — Run verification commands and confirm output before claiming success
- **[vitest](./skills/curated/vitest)** — Fast unit testing with Vite -- Jest-compatible API, mocking, coverage, and fixtures
- **[xstate](./skills/curated/xstate)** — XState v5 state machines, actors, `@xstate/store`, and TanStack Query integration
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
- **[pitch-deck](./skills/marketing/pitch-deck)** — Generate professional PowerPoint pitch decks for startups
- **[pitch-deck-visuals](./skills/marketing/pitch-deck-visuals)** — Investor pitch deck visuals with slide-by-slide framework and design rules
- **[pitch-gen](./skills/marketing/pitch-gen)** — Generate startup pitch deck content with AI
- **[pptx-creator](./skills/marketing/pptx-creator)** — Create professional PowerPoint presentations from outlines or data
- **[professional-communication](./skills/marketing/professional-communication)** — Technical communication for emails, team messaging, and meeting agendas
- **[promo-video](./skills/marketing/promo-video)** — Create promotional videos using Remotion with AI voiceover and background music
- **[sales-methodology-implementer](./skills/marketing/sales-methodology-implementer)** — Implement proven sales methodologies (MEDDIC, BANT, Sandler, Challenger, SPIN)
- **[startup-validator](./skills/marketing/startup-validator)** — Comprehensive startup idea validation and market analysis
- **[viz](./skills/marketing/viz)** — Four visualization modes in one skill -- Excalidraw diagrams, Swiss Pulse PNG infographics, inline Visualizer widgets, and published HeyGenverse apps
- **[writing-clearly-and-concisely](./skills/marketing/writing-clearly-and-concisely)** — Strunk's timeless rules for clearer, stronger, more professional prose

### Community

Broader community skills.

- **[a11y-testing](./skills/community/a11y-testing)** — Automated accessibility testing with axe-core, Playwright, and jest-axe
- **[adversarial-review](./skills/community/adversarial-review)** — Spawn opposing AI model reviewers to adversarially challenge work
- **[ai-sdk](./skills/community/ai-sdk)** — Vercel AI SDK for building AI-powered features
- **[argocd-expert](./skills/community/argocd-expert)** — ArgoCD GitOps deployment, sync strategies, and production operations
- **[better-auth-best-practices](./skills/community/better-auth-best-practices)** — Better Auth TypeScript authentication framework integration
- **[better-auth-organization-best-practices](./skills/community/better-auth-organization-best-practices)** — Multi-tenant organizations, RBAC, teams, members, and invitations with Better Auth's organization plugin
- **[building-components](./skills/community/building-components)** — Accessible, composable UI components with design tokens and documentation
- **[centrifugo](./skills/community/centrifugo)** — Centrifugo real-time messaging -- WebSocket PUB/SUB, channels, JWT auth, scaling
- **[cloudflare](./skills/community/cloudflare)** — Cloudflare platform -- Workers, Pages, storage, AI, networking, and security
- **[crafting-effective-readmes](./skills/community/crafting-effective-readmes)** — Templates and guidance for writing README files matched to audience and project
- **[creating-spec](./skills/community/creating-spec)** — Comprehensive technical specs for SDK gaps, features, or system centralization
- **[design-spec-extraction](./skills/community/design-spec-extraction)** — Extract production-ready JSON design specs from visual inputs using a 7-pass architecture
- **[devops-engineer](./skills/community/devops-engineer)** — Dockerfiles, CI/CD pipelines, Kubernetes manifests, and Terraform/Pulumi templates
- **[drizzle-orm](./skills/community/drizzle-orm)** — Drizzle ORM best practices -- schemas, queries, mutations, transactions, migrations
- **[drizzle-postgres](./skills/community/drizzle-postgres)** — PostgreSQL and Drizzle ORM best practices for type-safe database apps
- **[electron-builder](./skills/community/electron-builder)** — Electron packaging, code signing, auto-updates, and release workflows
- **[electron-dev](./skills/community/electron-dev)** — Electron development with Electron Vite and Builder -- main/renderer processes, IPC
- **[electron-release](./skills/community/electron-release)** — Electron production builds, notarization, auto-updates, and releases
- **[elysia](./skills/community/elysia)** — Type-safe APIs with Elysia including routing, validation, plugins, and error handling
- **[es-toolkit](./skills/community/es-toolkit)** — Modern utility library as a lodash replacement -- array, object, string operations
- **[evolution-api](./skills/community/evolution-api)** — Evolution API for WhatsApp messaging, instance management, and chatbot orchestration
- **[executing-plans](./skills/community/executing-plans)** — Execute implementation plans in batches with review checkpoints
- **[find-rules](./skills/community/find-rules)** — Discover project rules, coding standards, and architectural guidelines
- **[find-skills](./skills/community/find-skills)** — Discover and install agent skills from the open agent skills ecosystem
- **[fixing-motion-performance](./skills/community/fixing-motion-performance)** — Diagnose and fix animation performance issues in UI code
- **[helm-chart-scaffolding](./skills/community/helm-chart-scaffolding)** — Design, organize, and manage Helm charts for Kubernetes applications
- **[hetzner-server](./skills/community/hetzner-server)** — Create and manage Hetzner Cloud servers via the `hcloud` CLI
- **[inngest](./skills/community/inngest)** — Serverless background jobs, event-driven workflows, and durable execution
- **[k8s-security-policies](./skills/community/k8s-security-policies)** — Kubernetes security policies -- NetworkPolicy, PodSecurityPolicy, and RBAC
- **[kubernetes-specialist](./skills/community/kubernetes-specialist)** — Deploy and manage Kubernetes workloads -- manifests, Helm, RBAC, networking, GitOps
- **[mermaid-diagrams](./skills/community/mermaid-diagrams)** — Software diagrams using Mermaid syntax -- class, sequence, flowcharts, ERD, C4
- **[motion](./skills/community/motion)** — React animations with Motion (formerly Framer Motion) -- gestures, scroll effects, spring physics
- **[motion-react](./skills/community/motion-react)** — Full Motion for React guide including SVG, exit animations, and layout transitions
- **[obsidian-bases](./skills/community/obsidian-bases)** — Create and edit Obsidian Bases (`.base` files) with views, filters, formulas, and summaries
- **[obsidian-cli](./skills/community/obsidian-cli)** — Interact with Obsidian vaults via CLI -- read, create, search, manage notes, and develop plugins
- **[obsidian-markdown](./skills/community/obsidian-markdown)** — Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and tags
- **[pal](./skills/community/pal)** — Pal MCP toolkit for code analysis, debugging, planning, refactoring, and tracing
- **[perplexity](./skills/community/perplexity)** — Web search and research using Perplexity AI
- **[remotion-best-practices](./skills/community/remotion-best-practices)** — Best practices for Remotion video creation in React
- **[requirements-clarity](./skills/community/requirements-clarity)** — Clarify ambiguous requirements through focused dialogue before implementation
- **[ship-learn-next](./skills/community/ship-learn-next)** — Transform learning content into actionable implementation plans
- **[sourcebot](./skills/community/sourcebot)** — Search external libraries and frameworks using Sourcebot MCP
- **[tauri-v2](./skills/community/tauri-v2)** — Tauri v2 cross-platform apps with Rust backend, IPC, permissions, and builds
- **[terraform-style-guide](./skills/community/terraform-style-guide)** — Terraform HCL following HashiCorp's official style conventions
- **[workflow](./skills/community/workflow)** — Durable, resumable workflows using Vercel's Workflow DevKit
- **[wrangler](./skills/community/wrangler)** — Cloudflare Workers CLI for deploying and managing Workers, KV, R2, D1, and more

## Structure

Each skill follows a consistent directory layout:

```
skills/
  mine/<skill-name>/       # Original skills authored here (⭐️)
  curated/<skill-name>/    # Hand-picked community skills (💎)
  marketing/<skill-name>/  # Marketing, business, and writing skills (📣)
  community/<skill-name>/  # Broader community skills

skills/<bucket>/<skill-name>/
  SKILL.md              # Main skill definition (required)
  references/           # Deep-dive reference material
  examples/             # Usage examples and patterns
  templates/            # Code templates and scaffolds
  scripts/              # Automation scripts and validators
  checklists/           # Step-by-step verification checklists
```

## Contributing

To add a new skill:

1. Create a directory under the appropriate bucket with a lowercase, hyphenated name:
   - `skills/mine/` — original work authored here
   - `skills/curated/` — hand-picked, high-quality community skills you maintain
   - `skills/marketing/` — marketing, sales, business, or writing skills
   - `skills/community/` — broader community skills
2. Add a `SKILL.md` with proper frontmatter (`name` and `description` fields)
3. Include reference material, examples, and templates as needed
4. Follow the conventions documented in `skills/mine/writing-skills/SKILL.md`

## License

See repository root for license information.
