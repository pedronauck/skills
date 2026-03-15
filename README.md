# Pedro Nauck's Skills

A curated collection of **95+ agent skills** for Claude Code and compatible AI coding assistants. Each skill provides domain-specific knowledge, best practices, and guided workflows that enhance an agent's ability to perform specialized tasks.

## What are Skills?

Skills are structured instruction sets that give AI agents deep expertise in specific domains. Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file with metadata, procedures, and reference material. Skills follow the [agentskills.io](https://agentskills.io) specification.

## Skill Catalog

### Frontend & UI

- **[react](./skills/react)** — Component architecture, hooks, state management, TypeScript integration, and testing
- **[tailwindcss](./skills/tailwindcss)** — Tailwind CSS v4 patterns, design tokens, and tailwind-variants
- **[shadcn](./skills/shadcn)** — Building UI components with shadcn/ui, Radix UI primitives, and design tokens
- **[shadcn-ui](./skills/shadcn-ui)** — Complete shadcn/ui component library patterns, forms with Zod/React Hook Form, and theming
- **[motion](./skills/motion)** — React animations with Motion (formerly Framer Motion) -- gestures, scroll effects, spring physics
- **[motion-react](./skills/motion-react)** — Full Motion for React guide including SVG, exit animations, and layout transitions
- **[fixing-motion-performance](./skills/fixing-motion-performance)** — Diagnose and fix animation performance issues in UI code
- **[zustand](./skills/zustand)** — Zustand state management patterns, store organization, and best practices
- **[xstate](./skills/xstate)** — XState v5 state machines, actors, @xstate/store, and TanStack Query integration
- **[storybook](./skills/storybook)** — Storybook story authoring and CSF 3.0 best practices
- **[storybook-stories](./skills/storybook-stories)** — Create, update, or refactor Storybook stories following project patterns
- **[building-components](./skills/building-components)** — Accessible, composable UI components with design tokens and documentation
- **[tech-logos](./skills/tech-logos)** — Install official tech brand logos from the Elements registry via shadcn
- **[tanstack](./skills/tanstack)** — Comprehensive TanStack ecosystem guide -- Query/DB, Form, and Router
- **[tanstack-query-best-practices](./skills/tanstack-query-best-practices)** — Data fetching, caching, mutations, and server state management
- **[tanstack-router-best-practices](./skills/tanstack-router-best-practices)** — Type-safe routing, data loading, search params, and navigation
- **[tanstack-start-best-practices](./skills/tanstack-start-best-practices)** — Full-stack React with server functions, middleware, SSR, and deployment
- **[vercel-composition-patterns](./skills/vercel-composition-patterns)** — React composition patterns for refactoring boolean prop proliferation
- **[vercel-react-best-practices](./skills/vercel-react-best-practices)** — React/Next.js performance optimization from Vercel Engineering

### UI/UX Design

- **[frontend-design](./skills/frontend-design)** — Distinctive, production-grade frontend interfaces with high design quality
- **[interface-design](./skills/interface-design)** — Interface design for dashboards, admin panels, apps, and tools
- **[landing-page-design](./skills/landing-page-design)** — High-converting landing pages with AI-generated visuals and conversion optimization
- **[bencium-innovative-ux-designer](./skills/bencium-innovative-ux-designer)** — Innovative UX design with design system templates, motion specs, and accessibility
- **[ui-ux-pro-max](./skills/ui-ux-pro-max)** — 50 design styles, 21 palettes, 50 font pairings, and 9 tech stacks for web/mobile
- **[web-design-guidelines](./skills/web-design-guidelines)** — Review UI code for Web Interface Guidelines compliance
- **[design-spec-extraction](./skills/design-spec-extraction)** — Extract production-ready JSON design specs from visual inputs using a 7-pass architecture

### Backend & APIs

- **[hono](./skills/hono)** — Hono framework development with documentation search and API reference
- **[elysia](./skills/elysia)** — Type-safe APIs with Elysia including routing, validation, plugins, and error handling
- **[drizzle-orm](./skills/drizzle-orm)** — Drizzle ORM best practices -- schemas, queries, mutations, transactions, migrations
- **[drizzle-safe-migrations](./skills/drizzle-safe-migrations)** — Production-safe Drizzle migration workflows for schema changes
- **[postgres-drizzle](./skills/postgres-drizzle)** — PostgreSQL and Drizzle ORM best practices for type-safe database apps
- **[better-auth-best-practices](./skills/better-auth-best-practices)** — Better Auth TypeScript authentication framework integration
- **[inngest](./skills/inngest)** — Serverless background jobs, event-driven workflows, and durable execution
- **[workflow](./skills/workflow)** — Durable, resumable workflows using Vercel's Workflow DevKit

### Stripe & Payments

- **[stripe-best-practices](./skills/stripe-best-practices)** — Best practices for Stripe integrations across all use cases
- **[stripe-integration](./skills/stripe-integration)** — PCI-compliant payment flows including checkout, subscriptions, and webhooks
- **[stripe-subscriptions](./skills/stripe-subscriptions)** — Subscription billing with feature flags, webhook handling, and billing portal
- **[stripe-webhooks](./skills/stripe-webhooks)** — Receive and verify Stripe webhooks with signature debugging

### TypeScript & JavaScript

- **[typescript-advanced](./skills/typescript-advanced)** — Advanced type system -- generics, conditional types, mapped types, template literals
- **[zod](./skills/zod)** — Zod schema validation for type safety, parsing, and error handling
- **[es-toolkit](./skills/es-toolkit)** — Modern utility library as a lodash replacement -- array, object, string operations
- **[effect-ts](./skills/effect-ts)** — Effect-TS code including setup, data modeling, error handling, and Context.Tag

### Rust

- **[rust-engineer](./skills/rust-engineer)** — Senior Rust engineer persona for memory-safe systems-level applications
- **[rust-best-practices](./skills/rust-best-practices)** — Idiomatic Rust based on Apollo GraphQL's best practices handbook
- **[rust-coding-guidelines](./skills/rust-coding-guidelines)** — 50 core rules for Rust code style, naming, formatting, and best practices
- **[rust-async-patterns](./skills/rust-async-patterns)** — Async programming with Tokio, async traits, error handling, and concurrency
- **[ratatui-tui](./skills/ratatui-tui)** — Terminal UIs with ratatui v0.30.0+ -- Elm Architecture, StatefulWidget, async events

### Desktop Applications

- **[electron-dev](./skills/electron-dev)** — Electron development with Electron Vite and Builder -- main/renderer processes, IPC
- **[electron-builder](./skills/electron-builder)** — Electron packaging, code signing, auto-updates, and release workflows
- **[electron-release](./skills/electron-release)** — Electron production builds, notarization, auto-updates, and releases
- **[tauri-v2](./skills/tauri-v2)** — Tauri v2 cross-platform apps with Rust backend, IPC, permissions, and builds

### DevOps & Infrastructure

- **[devops-engineer](./skills/devops-engineer)** — Dockerfiles, CI/CD pipelines, Kubernetes manifests, and Terraform/Pulumi templates
- **[kubernetes-specialist](./skills/kubernetes-specialist)** — Deploy and manage Kubernetes workloads -- manifests, Helm, RBAC, networking, GitOps
- **[argocd-expert](./skills/argocd-expert)** — ArgoCD GitOps deployment, sync strategies, and production operations
- **[helm-chart-scaffolding](./skills/helm-chart-scaffolding)** — Design, organize, and manage Helm charts for Kubernetes applications
- **[k8s-security-policies](./skills/k8s-security-policies)** — Kubernetes security policies -- NetworkPolicy, PodSecurityPolicy, and RBAC
- **[terraform-style-guide](./skills/terraform-style-guide)** — Terraform HCL following HashiCorp's official style conventions
- **[cloudflare](./skills/cloudflare)** — Cloudflare platform -- Workers, Pages, storage, AI, networking, and security
- **[wrangler](./skills/wrangler)** — Cloudflare Workers CLI for deploying and managing Workers, KV, R2, D1, and more
- **[hetzner-server](./skills/hetzner-server)** — Create and manage Hetzner Cloud servers via the hcloud CLI
- **[sentry-cli](./skills/sentry-cli)** — Sentry CLI for interacting with Sentry from the command line

### Real-Time & Messaging

- **[centrifugo](./skills/centrifugo)** — Centrifugo real-time messaging -- WebSocket PUB/SUB, channels, JWT auth, scaling
- **[evolution-api](./skills/evolution-api)** — Evolution API for WhatsApp messaging, instance management, and chatbot orchestration
- **[rivetkit](./skills/rivetkit)** — RivetKit backend and Rivet Actor runtime for long-lived, in-memory processes
- **[rivetkit-client-javascript](./skills/rivetkit-client-javascript)** — RivetKit JavaScript client for browser, Node.js, or Bun
- **[rivetkit-client-react](./skills/rivetkit-client-react)** — RivetKit React client with `@rivetkit/react`
- **[sync-provider](./skills/sync-provider)** — Sync upstream changes from cloned repos while preserving local customizations

### AI & Agent Development

- **[ai-sdk](./skills/ai-sdk)** — Vercel AI SDK for building AI-powered features
- **[agent-identifier](./skills/agent-identifier)** — Agent structure, system prompts, triggering conditions, and development best practices
- **[mastra](./skills/mastra)** — Mastra framework for building AI agents and workflows
- **[develop-ai-functions-example](./skills/develop-ai-functions-example)** — Develop examples for AI SDK functions to validate provider support
- **[skills-best-practices](./skills/skills-best-practices)** — Author professional-grade agent skills following the agentskills.io spec
- **[find-skills](./skills/find-skills)** — Discover and install agent skills from the open agent skills ecosystem
- **[pal](./skills/pal)** — Pal MCP toolkit for code analysis, debugging, planning, refactoring, and tracing
- **[sourcebot](./skills/sourcebot)** — Search external libraries and frameworks using Sourcebot MCP

### Testing & Quality

- **[vitest](./skills/vitest)** — Fast unit testing with Vite -- Jest-compatible API, mocking, coverage, and fixtures
- **[a11y-testing](./skills/a11y-testing)** — Automated accessibility testing with axe-core, Playwright, and jest-axe
- **[test-antipatterns](./skills/test-antipatterns)** — Prevent common testing anti-patterns like testing mock behavior
- **[verification-before-completion](./skills/verification-before-completion)** — Run verification commands and confirm output before claiming success
- **[adversarial-review](./skills/adversarial-review)** — Spawn opposing AI model reviewers to adversarially challenge work

### Code Quality & Workflows

- **[architectural-analysis](./skills/architectural-analysis)** — Deep architectural audit for dead code, duplication, anti-patterns, and code smells
- **[systematic-debugging](./skills/systematic-debugging)** — Root-cause investigation before proposing fixes for bugs or test failures
- **[no-workarounds](./skills/no-workarounds)** — Enforce root-cause fixes over workarounds, hacks, and symptom patches
- **[receiving-code-review](./skills/receiving-code-review)** — Handle code review feedback with technical rigor and verification
- **[fix-coderabbit-review](./skills/fix-coderabbit-review)** — End-to-end remediation workflow for PR review feedback
- **[git-rebase](./skills/git-rebase)** — Git rebase operations and merge conflict resolution with clean history
- **[find-rules](./skills/find-rules)** — Discover project rules, coding standards, and architectural guidelines

### Planning & Research

- **[brainstorming](./skills/brainstorming)** — Explore intent, requirements, and design through collaborative dialogue
- **[creating-spec](./skills/creating-spec)** — Comprehensive technical specs for SDK gaps, features, or system centralization
- **[deep-research](./skills/deep-research)** — Comprehensive research and analysis using multiple discovery tools
- **[executing-plans](./skills/executing-plans)** — Execute implementation plans in batches with review checkpoints
- **[dispatching-parallel-agents](./skills/dispatching-parallel-agents)** — Dispatch independent tasks to parallel agents to avoid bottlenecks
- **[crafting-effective-readmes](./skills/crafting-effective-readmes)** — Templates and guidance for writing README files matched to audience and project

### Web Scraping & Search

- **[firecrawl](./skills/firecrawl)** — Web scraping, search, crawling, and browser automation via the Firecrawl CLI
- **[exa-web-search-free](./skills/exa-web-search-free)** — Free AI-powered web, code, and company search via Exa MCP
- **[agent-browser](./skills/agent-browser)** — Automate browser interactions for testing, form filling, and data extraction

### Architecture & Patterns

- **[app-renderer-systems](./skills/app-renderer-systems)** — Domain feature systems organized under a `systems/` directory
- **[organization-best-practices](./skills/organization-best-practices)** — Multi-tenant organizations, RBAC, teams, and permissions with Better Auth
- **[trading-strategies](./skills/trading-strategies)** — Framework for developing, testing, and deploying prediction market trading strategies

### Utilities

- **[to-prompt](./skills/to-prompt)** — Transform code, issues, or context into a detailed prompt for another LLM
- **[outside-to-issue](./skills/outside-to-issue)** — Transform outside-of-diff review files into formatted issue files for a PR

## Structure

Each skill follows a consistent directory layout:

```
skills/<skill-name>/
  SKILL.md              # Main skill definition (required)
  references/           # Deep-dive reference material
  examples/             # Usage examples and patterns
  templates/            # Code templates and scaffolds
  scripts/              # Automation scripts and validators
  checklists/           # Step-by-step verification checklists
```

## Usage

Copy or symlink the skills you need into your Claude Code configuration:

```bash
# Copy a single skill
cp -r skills/react ~/.claude/skills/react

# Or symlink the entire collection
ln -s $(pwd)/skills ~/.claude/skills
```

Skills are automatically picked up by Claude Code when placed in the `~/.claude/skills/` directory. The agent matches tasks to relevant skills based on the `description` field in each `SKILL.md` frontmatter.

## Contributing

To add a new skill:

1. Create a directory under `skills/` with a lowercase, hyphenated name
2. Add a `SKILL.md` with proper frontmatter (`name` and `description` fields)
3. Include reference material, examples, and templates as needed
4. Follow the conventions documented in `skills/skills-best-practices/SKILL.md`

## License

See repository root for license information.
