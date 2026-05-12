# TanStack Skills Consolidation Plan

**Date:** 2026-05-12
**Owner:** Pedro Nauck
**Goal:** Consolidate `community/tanstack-query-best-practices`, `community/tanstack-router-best-practices`, and `community/tanstack-start-best-practices` into the single owned skill `mine/tanstack`, then remove the community duplicates.

---

## Context

`mine/tanstack` currently covers:
- TanStack DB collections (deep)
- TanStack Form (deep)
- TanStack Router (basic patterns only)
- Vanilla TanStack Query: minimal (covers a few patterns inside the DB-focused file)
- TanStack Start: not covered

The three community skills together hold ~107 rule files of well-categorized patterns. Compozy's adjacent projects (`agh`, `looper`) use TanStack Start, so Start coverage is in-scope.

## Decisions

1. **Single consolidated skill** at `skills/mine/tanstack/`. No new skills.
2. **Split `query-patterns.md`** into two files because vanilla Query and DB collections are distinct paradigms that should not be mixed:
   - `references/query-patterns.md` — vanilla Query (new content)
   - `references/db-patterns.md` — DB collections (current content, trimmed)
3. **Expand `router-patterns.md`** in-place with the high-value gaps.
4. **Create `references/start-patterns.md`** covering server functions, middleware, auth, SSR, deploy.
5. **Keep `form-patterns.md`** as-is — already strong.
6. **Filter signal-vs-noise**: skip rules that are obvious or pure restatement (`qk-array-structure`, `qk-serializable`, `nav-active-states`, etc.). Keep the ones that prevent real bugs.
7. **Remove** the three community skills after the merge lands.

## Final file layout (mine/tanstack)

```
skills/mine/tanstack/
├── SKILL.md                       # entry point + checklist
└── references/
    ├── query-patterns.md          # vanilla TanStack Query
    ├── db-patterns.md             # TanStack DB collections (renamed)
    ├── router-patterns.md         # expanded
    ├── form-patterns.md           # unchanged
    └── start-patterns.md          # NEW (TanStack Start)
```

## Content to bring in

### Query (new `query-patterns.md`)

- staleTime/gcTime with volatility table
- placeholderData vs initialData (non-obvious gotcha)
- Query key factory pattern with `queryOptions`
- Targeted invalidation
- Mutations: optimistic updates + rollback context, `onMutate` pattern, `useMutationState`
- Error handling: `useQueryErrorResetBoundary`, retry config
- Prefetching: intent (hover/focus), `ensureQueryData`
- Infinite queries: `getNextPageParam`, loading guards
- SSR: `dehydrate`/`HydrationBoundary`, `QueryClient` per request
- Parallel: `useQueries`
- Query cancellation with `signal`
- `select` for transform/filter
- `networkMode`, persistence with `persistQueryClient`

### Router (expand `router-patterns.md`)

- `ts-register-router` (declare module — CRITICAL, missing)
- `ts-use-from-param` (type narrowing)
- `router-default-options` (scrollRestoration, defaultErrorComponent, defaultPreload)
- `split-lazy-routes` (deeper — auto code splitting)
- `preload-intent` + `preload-stale-time`
- `search-custom-serializer` / `search-middleware`
- `err-not-found` (global)
- `org-pathless-layouts` / `org-virtual-routes`
- `load-parallel` / `load-deferred-data`
- `nav-route-masks` rationale + use cases

### Start (new `start-patterns.md`)

- `createServerFn` patterns + input validation with Zod
- Method selection (GET vs POST)
- Server function error handling
- Request middleware vs function middleware, context flow
- Auth: session management, route protection via `beforeLoad`, cookie security
- SSR: hydration safety, streaming, selective SSR, prerender/ISR
- API routes for external consumers
- Env functions (`createEnv`)
- File separation server/client
- Deploy adapters (Vercel, Netlify, Node)

### Things explicitly NOT bringing

- `qk-array-structure`, `qk-serializable` — obvious for anyone reading the docs once
- `nav-active-states`, `nav-relative-paths` — covered by Link types
- `sec-csrf-protection`, `sec-sensitive-data` — generic security advice, not Start-specific
- `mut-loading-states` — trivial isPending check
- `org-index-routes`, `org-file-based-routing` — already in router-patterns

## Execution order

1. Write plan (this file)
2. Create `references/db-patterns.md` from current `query-patterns.md` content
3. Replace `references/query-patterns.md` with vanilla Query content
4. Expand `references/router-patterns.md`
5. Create `references/start-patterns.md`
6. Update `SKILL.md`: description, file list, checklist
7. Remove `skills/community/tanstack-query-best-practices/`
8. Remove `skills/community/tanstack-router-best-practices/`
9. Remove `skills/community/tanstack-start-best-practices/`
10. Update `skills-lock.json` and `README.md` to drop the three community entries

## Success criteria

- `mine/tanstack` has 5 reference files covering Query, DB, Router, Form, Start
- SKILL.md description mentions all five areas
- No `community/tanstack-*` directories remain
- `skills-lock.json` no longer lists the three community tanstack skills
- README reflects the change

## Rollback

`git checkout HEAD -- skills/community/tanstack-*` restores the deleted community folders if needed.
