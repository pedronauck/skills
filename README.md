# Pedro Nauck's Skills

A curated collection of **122 agent skills** for Claude Code and compatible AI coding assistants — **27 original** (⭐️), **21 hand-picked** (💎), **17 marketing & business** (📣), plus **57 community** skills. Each skill provides domain-specific knowledge, best practices, and guided workflows that enhance an agent's ability to perform specialized tasks.

## Installation

### Quick install (recommended)

Install this repository into your agent skills directory with the [`skills`](https://www.npmjs.com/package/skills) CLI:

```bash
npx skills add https://github.com/pedronauck/skills
```

### Manual install

Copy or symlink the skills you need into your Claude Code configuration:

```bash
# Copy a single skill
cp -r skills/curated/react ~/.claude/skills/react

# Or symlink an entire bucket
ln -s $(pwd)/skills/mine ~/.claude/skills/mine
```

Skills are organized into four top-level buckets:

- `skills/mine/` — 27 original skills authored in this repository (⭐️)
- `skills/curated/` — 21 hand-picked community skills (💎)
- `skills/marketing/` — 17 marketing, business, and writing skills (📣)
- `skills/community/` — 57 broader community skills

## Usage

Skills are automatically picked up by Claude Code when placed in the `~/.claude/skills/` directory. The agent matches tasks to relevant skills based on the `description` field in each `SKILL.md` frontmatter.

## What are Skills?

Skills are structured instruction sets that give AI agents deep expertise in specific domains. Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file with metadata, procedures, and reference material. Skills follow the [agentskills.io](https://agentskills.io) specification.

## Skill Catalog

> ⭐️ = original skill authored in this repository &nbsp;·&nbsp; 💎 = hand-picked community skill &nbsp;·&nbsp; 📣 = marketing & business skill

### Frontend & UI

- **[react](./skills/curated/react)** 💎 — Component architecture, hooks, state management, TypeScript integration, and testing
- **[tailwindcss](./skills/curated/tailwindcss)** 💎 — Tailwind CSS v4 patterns, design tokens, and tailwind-variants
- **[shadcn](./skills/community/shadcn)** — Building UI components with shadcn/ui, Radix UI primitives, and design tokens
- **[motion](./skills/community/motion)** — React animations with Motion (formerly Framer Motion) -- gestures, scroll effects, spring physics
- **[motion-react](./skills/community/motion-react)** — Full Motion for React guide including SVG, exit animations, and layout transitions
- **[fixing-motion-performance](./skills/community/fixing-motion-performance)** — Diagnose and fix animation performance issues in UI code
- **[zustand](./skills/curated/zustand)** 💎 — Zustand state management patterns, store organization, and best practices
- **[xstate](./skills/community/xstate)** — XState v5 state machines, actors, `@xstate/store`, and TanStack Query integration
- **[storybook](./skills/community/storybook)** — Storybook story authoring and CSF 3.0 best practices
- **[storybook-stories](./skills/mine/storybook-stories)** ⭐️ — Create, update, or refactor Storybook stories following project patterns
- **[building-components](./skills/community/building-components)** — Accessible, composable UI components with design tokens and documentation
- **[tech-logos](./skills/mine/tech-logos)** ⭐️ — Install official tech brand logos from the Elements registry via shadcn
- **[tanstack](./skills/curated/tanstack)** 💎 — Comprehensive TanStack ecosystem guide -- Query/DB, Form, and Router
- **[tanstack-query-best-practices](./skills/community/tanstack-query-best-practices)** — Data fetching, caching, mutations, and server state management
- **[tanstack-router-best-practices](./skills/community/tanstack-router-best-practices)** — Type-safe routing, data loading, search params, and navigation
- **[tanstack-start-best-practices](./skills/community/tanstack-start-best-practices)** — Full-stack React with server functions, middleware, SSR, and deployment
- **[vercel-composition-patterns](./skills/curated/vercel-composition-patterns)** 💎 — React composition patterns for refactoring boolean prop proliferation
- **[next-best-practices](./skills/curated/next-best-practices)** 💎 — Next.js best practices -- file conventions, RSC boundaries, data patterns, async APIs, metadata, error handling, and optimization
- **[vercel-react-best-practices](./skills/curated/vercel-react-best-practices)** 💎 — React/Next.js performance optimization from Vercel Engineering

### UI/UX Design

- **[ui-craft](./skills/mine/ui-craft)** ⭐️ — Anti-AI-slop guardrails for UI/UX work — usability heuristics, accessibility floors, design-system discipline, 14 named slop patterns with severity tags, tunable design dials (`VISUAL_VARIANCE`/`MOTION_INTENSITY`/`INFORMATION_DENSITY`), scene-driven decisions, Product vs Brand registers, anti-defaults blocklist, 7 named UI archetypes, plus performance / motion / dark-mode reference packs and executable contrast + token-drift scripts
- **[design-spec-extraction](./skills/community/design-spec-extraction)** — Extract production-ready JSON design specs from visual inputs using a 7-pass architecture

### Backend & APIs

- **[hono](./skills/curated/hono)** 💎 — Hono framework development with documentation search and API reference
- **[elysia](./skills/community/elysia)** — Type-safe APIs with Elysia including routing, validation, plugins, and error handling
- **[drizzle-orm](./skills/community/drizzle-orm)** — Drizzle ORM best practices -- schemas, queries, mutations, transactions, migrations
- **[drizzle-safe-migrations](./skills/curated/drizzle-safe-migrations)** 💎 — Production-safe Drizzle migration workflows for schema changes
- **[drizzle-postgres](./skills/community/drizzle-postgres)** — PostgreSQL and Drizzle ORM best practices for type-safe database apps
- **[better-auth-best-practices](./skills/community/better-auth-best-practices)** — Better Auth TypeScript authentication framework integration
- **[better-auth-organization-best-practices](./skills/community/better-auth-organization-best-practices)** — Multi-tenant organizations, RBAC, teams, members, and invitations with Better Auth's organization plugin
- **[inngest](./skills/community/inngest)** — Serverless background jobs, event-driven workflows, and durable execution
- **[workflow](./skills/community/workflow)** — Durable, resumable workflows using Vercel's Workflow DevKit
- **[mastra](./skills/curated/mastra)** 💎 — Mastra framework for building AI agents and workflows

### TypeScript & JavaScript

- **[typescript-advanced](./skills/mine/typescript-advanced)** ⭐️ — Advanced type system -- generics, conditional types, mapped types, template literals
- **[zod](./skills/curated/zod)** 💎 — Zod schema validation for type safety, parsing, and error handling
- **[es-toolkit](./skills/community/es-toolkit)** — Modern utility library as a lodash replacement -- array, object, string operations
- **[effect-ts](./skills/curated/effect-ts)** 💎 — Effect-TS code including setup, data modeling, error handling, and `Context.Tag`

### Rust

- **[rust-best-practices](./skills/mine/rust-best-practices)** ⭐️ — Unified Rust guidelines covering ownership, error handling, async/Tokio, traits, testing, performance, clippy, and documentation
- **[ratatui-tui](./skills/curated/ratatui-tui)** 💎 — Terminal UIs with ratatui v0.30.0+ -- Elm Architecture, StatefulWidget, async events
- **[tui-design](./skills/curated/tui-design)** 💎 — Universal TUI design patterns -- layouts, color schemes, keyboard navigation, dashboards, and accessibility

### Go

- **[golang-pro](./skills/community/golang-pro)** — Concurrent Go patterns, microservices with gRPC/REST, pprof optimization, generics, and idiomatic error handling
- **[bubbletea](./skills/mine/bubbletea)** ⭐️ — Build terminal UIs with Go and Bubbletea -- Elm architecture, Lipgloss styling, dual-pane layouts, and reusable components

### Desktop Applications

- **[electron-dev](./skills/community/electron-dev)** — Electron development with Electron Vite and Builder -- main/renderer processes, IPC
- **[electron-builder](./skills/community/electron-builder)** — Electron packaging, code signing, auto-updates, and release workflows
- **[electron-release](./skills/community/electron-release)** — Electron production builds, notarization, auto-updates, and releases
- **[tauri-v2](./skills/community/tauri-v2)** — Tauri v2 cross-platform apps with Rust backend, IPC, permissions, and builds

### DevOps & Infrastructure

- **[devops-engineer](./skills/community/devops-engineer)** — Dockerfiles, CI/CD pipelines, Kubernetes manifests, and Terraform/Pulumi templates
- **[kubernetes-specialist](./skills/community/kubernetes-specialist)** — Deploy and manage Kubernetes workloads -- manifests, Helm, RBAC, networking, GitOps
- **[argocd-expert](./skills/community/argocd-expert)** — ArgoCD GitOps deployment, sync strategies, and production operations
- **[helm-chart-scaffolding](./skills/community/helm-chart-scaffolding)** — Design, organize, and manage Helm charts for Kubernetes applications
- **[k8s-security-policies](./skills/community/k8s-security-policies)** — Kubernetes security policies -- NetworkPolicy, PodSecurityPolicy, and RBAC
- **[terraform-style-guide](./skills/community/terraform-style-guide)** — Terraform HCL following HashiCorp's official style conventions
- **[cloudflare](./skills/community/cloudflare)** — Cloudflare platform -- Workers, Pages, storage, AI, networking, and security
- **[wrangler](./skills/community/wrangler)** — Cloudflare Workers CLI for deploying and managing Workers, KV, R2, D1, and more
- **[hetzner-server](./skills/community/hetzner-server)** — Create and manage Hetzner Cloud servers via the `hcloud` CLI
- **[sentry-cli](./skills/curated/sentry-cli)** 💎 — Sentry CLI for interacting with Sentry from the command line

### Real-Time & Messaging

- **[centrifugo](./skills/community/centrifugo)** — Centrifugo real-time messaging -- WebSocket PUB/SUB, channels, JWT auth, scaling
- **[evolution-api](./skills/community/evolution-api)** — Evolution API for WhatsApp messaging, instance management, and chatbot orchestration
- **[sync-provider](./skills/community/sync-provider)** — Sync upstream changes from cloned repos while preserving local customizations

### AI & Agent Development

- **[ai-sdk](./skills/community/ai-sdk)** — Vercel AI SDK for building AI-powered features
- **[skill-best-practices](./skills/mine/skill-best-practices)** ⭐️ — Author professional-grade agent skills following the agentskills.io spec
- **[autoresearch](./skills/mine/autoresearch)** ⭐️ — Autonomously optimize any skill by running evals, mutating prompts, and keeping improvements
- **[agent-md-refactor](./skills/curated/agent-md-refactor)** 💎 — Refactor bloated AGENTS.md/CLAUDE.md files into organized, linked documentation
- **[find-skills](./skills/community/find-skills)** — Discover and install agent skills from the open agent skills ecosystem
- **[pal](./skills/community/pal)** — Pal MCP toolkit for code analysis, debugging, planning, refactoring, and tracing
- **[sourcebot](./skills/community/sourcebot)** — Search external libraries and frameworks using Sourcebot MCP
- **[council](./skills/mine/council)** ⭐️ — Run decisions through 5 independent advisors, anonymous peer review, and a chairman synthesis (Karpathy-style LLM Council)

### Testing & Quality

- **[vitest](./skills/community/vitest)** — Fast unit testing with Vite -- Jest-compatible API, mocking, coverage, and fixtures
- **[a11y-testing](./skills/community/a11y-testing)** — Automated accessibility testing with axe-core, Playwright, and jest-axe
- **[test-antipatterns](./skills/mine/test-antipatterns)** ⭐️ — Prevent common testing anti-patterns like testing mock behavior
- **[qa-report](./skills/mine/qa-report)** ⭐️ — Generate test plans, manual test cases, regression suites, and bug reports
- **[qa-execution](./skills/mine/qa-execution)** ⭐️ — Audit task/spec completion against real implementation evidence, discover the repo verification contract, run build/lint/test/start gates, exercise end-to-end CLI/HTTP/browser workflows, reopen incomplete tasks via frontmatter, and re-verify. Integrates with `cy-codex-loop` slugs at `.compozy/tasks/<slug>/`.
- **[verification-before-completion](./skills/community/verification-before-completion)** — Run verification commands and confirm output before claiming success
- **[adversarial-review](./skills/community/adversarial-review)** — Spawn opposing AI model reviewers to adversarially challenge work

### Code Quality & Workflows

- **[architectural-analysis](./skills/mine/architectural-analysis)** ⭐️ — Deep architectural audit for dead code, duplication, anti-patterns, and code smells
- **[systematic-debugging](./skills/curated/systematic-debugging)** 💎 — Root-cause investigation before proposing fixes for bugs or test failures
- **[extreme-software-optimization](./skills/mine/extreme-software-optimization)** ⭐️ — Profile-driven performance optimization with behavior proofs, opportunity scoring, and isomorphism guarantees
- **[no-workarounds](./skills/mine/no-workarounds)** ⭐️ — Enforce root-cause fixes over workarounds, hacks, and symptom patches
- **[find-rules](./skills/community/find-rules)** — Discover project rules, coding standards, and architectural guidelines
- **[fix-coderabbit-review](./skills/mine/fix-coderabbit-review)** ⭐️ — End-to-end remediation workflow for PR review feedback
- **[git-rebase](./skills/curated/git-rebase)** 💎 — Git rebase operations and merge conflict resolution with clean history
- **[refactoring-analysis](./skills/mine/refactoring-analysis)** ⭐️ — Identify refactoring opportunities using Martin Fowler's code smells catalog with prioritized reports

### Planning & Research

- **[brainstorming](./skills/mine/brainstorming)** ⭐️ — Explore intent, requirements, and design through collaborative dialogue
- **[creating-spec](./skills/community/creating-spec)** — Comprehensive technical specs for SDK gaps, features, or system centralization
- **[executing-plans](./skills/community/executing-plans)** — Execute implementation plans in batches with review checkpoints
- **[crafting-effective-readmes](./skills/community/crafting-effective-readmes)** — Templates and guidance for writing README files matched to audience and project
- **[requirements-clarity](./skills/community/requirements-clarity)** — Clarify ambiguous requirements through focused dialogue before implementation
- **[lesson-learned](./skills/mine/lesson-learned)** ⭐️ — Extract software engineering lessons from git history and recent code changes
- **[ship-learn-next](./skills/community/ship-learn-next)** — Transform learning content into actionable implementation plans

### Web Scraping & Search

- **[firecrawl](./skills/curated/firecrawl)** 💎 — Web scraping, search, crawling, and browser automation via the Firecrawl CLI
- **[exa-web-search-free](./skills/mine/exa-web-search-free)** ⭐️ — Free AI-powered web, code, and company search via Exa MCP
- **[perplexity](./skills/community/perplexity)** — Web search and research using Perplexity AI
- **[context7](./skills/mine/context7)** ⭐️ — Retrieve up-to-date technical documentation, API references, and code examples for any library via Context7 CLI
- **[agent-browser](./skills/curated/agent-browser)** 💎 — Automate browser interactions for testing, form filling, and data extraction

### Knowledge Management & Notes

- **[obsidian-cli](./skills/community/obsidian-cli)** — Interact with Obsidian vaults via CLI -- read, create, search, manage notes, and develop plugins
- **[obsidian-markdown](./skills/community/obsidian-markdown)** — Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and tags
- **[obsidian-bases](./skills/community/obsidian-bases)** — Create and edit Obsidian Bases (`.base` files) with views, filters, formulas, and summaries
- **[qmd](./skills/community/qmd)** — Search markdown knowledge bases, notes, and documentation using QMD

### Content & Writing

- **[content-research-writer](./skills/marketing/content-research-writer)** 📣 — Writing partner for research, outlining, drafting, and refining content
- **[copywriting](./skills/marketing/copywriting)** 📣 — Conversion copywriting for marketing pages, CTAs, and headlines
- **[humanizer](./skills/marketing/humanizer)** 📣 — Remove signs of AI-generated writing from text
- **[writing-clearly-and-concisely](./skills/marketing/writing-clearly-and-concisely)** 📣 — Strunk's timeless rules for clearer, stronger, more professional prose
- **[professional-communication](./skills/marketing/professional-communication)** 📣 — Technical communication for emails, team messaging, and meeting agendas

### Business & Strategy

- **[alex-hormozi-pitch](./skills/marketing/alex-hormozi-pitch)** 📣 — Create irresistible offers using Hormozi's $100M Offers methodology
- **[brand-storytelling](./skills/marketing/brand-storytelling)** 📣 — Craft compelling brand narratives and positioning
- **[fundraising](./skills/marketing/fundraising)** 📣 — Plan and run early-stage fundraising with pitch narrative, investor pipeline, and outreach
- **[game-changing-features](./skills/curated/game-changing-features)** 💎 — Find 10x product opportunities and high-leverage improvements
- **[startup-validator](./skills/marketing/startup-validator)** 📣 — Comprehensive startup idea validation and market analysis
- **[sales-methodology-implementer](./skills/marketing/sales-methodology-implementer)** 📣 — Implement proven sales methodologies (MEDDIC, BANT, Sandler, Challenger, SPIN)

### Presentations & Documents

- **[pitch-deck](./skills/marketing/pitch-deck)** 📣 — Generate professional PowerPoint pitch decks for startups
- **[pitch-deck-visuals](./skills/marketing/pitch-deck-visuals)** 📣 — Investor pitch deck visuals with slide-by-slide framework and design rules
- **[pitch-gen](./skills/marketing/pitch-gen)** 📣 — Generate startup pitch deck content with AI
- **[pptx-creator](./skills/marketing/pptx-creator)** 📣 — Create professional PowerPoint presentations from outlines or data
- **[architecture-diagram](./skills/mine/architecture-diagram)** ⭐️ — Professional dark-themed system architecture diagrams as standalone HTML/SVG files
- **[mermaid-diagrams](./skills/community/mermaid-diagrams)** — Software diagrams using Mermaid syntax -- class, sequence, flowcharts, ERD, C4
- **[viz](./skills/marketing/viz)** 📣 — Four visualization modes in one skill -- Excalidraw diagrams, Swiss Pulse PNG infographics, inline Visualizer widgets, and published HeyGenverse apps

### Video & Media

- **[promo-video](./skills/marketing/promo-video)** 📣 — Create promotional videos using Remotion with AI voiceover and background music
- **[remotion-best-practices](./skills/community/remotion-best-practices)** — Best practices for Remotion video creation in React

### Twitter & Social Media

- **[tweetsmash-api](./skills/mine/tweetsmash-api)** ⭐️ — TweetSmash REST API for fetching bookmarks, managing labels, filtering, and pagination

### Marketing & Advertising

- **[google-ads](./skills/marketing/google-ads)** 📣 — Query, audit, and optimize Google Ads campaigns
- **[hormozi-ad-factory](./skills/mine/hormozi-ad-factory)** ⭐️ — Generate 150-750+ ad variations using Hormozi's combinatorial Hook x Meat x CTA framework

### Architecture & Patterns

- **[app-renderer-systems](./skills/mine/app-renderer-systems)** ⭐️ — Domain feature systems organized under a `systems/` directory

### Utilities

- **[to-prompt](./skills/mine/to-prompt)** ⭐️ — Transform code, issues, or context into a detailed prompt for another LLM
- **[outside-to-issue](./skills/mine/outside-to-issue)** ⭐️ — Transform outside-of-diff review files into formatted issue files for a PR

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
4. Follow the conventions documented in `skills/mine/skill-best-practices/SKILL.md`

## License

See repository root for license information.
