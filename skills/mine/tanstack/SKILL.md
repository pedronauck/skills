---
name: tanstack
description: Comprehensive guide for the TanStack ecosystem in React — Query (caching, mutations, prefetching, SSR), DB (collections, live queries, optimistic updates), Form (state, validation, fields), Router (file-based, type-safe navigation, search params, loaders), and Start (server functions, middleware, auth, SSR). Use when working with any TanStack library in a React/full-stack project. Don't use for non-TanStack data libraries (SWR, Apollo, RTK Query), non-React TanStack ports (Solid, Svelte), or backend-only work.
allowed-tools: Read, Grep, Glob
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# TanStack Developer Guide

This SKILL.md is a **dispatcher**, not an encyclopedia. The load-bearing detail (code patterns, anti-patterns, edge cases, full checklists) lives in `references/*.md`. The tripwires below exist so you can detect violations during scanning — they are not the contract.

## Required Reading Router

Match the task to the row. **Read the listed file(s) in full before producing output.** They are not appendices — they are the contract. Inline content in this SKILL.md is a pointer, not a substitute.

| Task | MUST read |
|------|-----------|
| `useQuery` / `useMutation` / prefetch / infinite list / SSR hydration / cache config | `references/query-patterns.md` |
| Typed collections, live queries, optimistic collection mutations | `references/db-patterns.md` |
| Forms, field components, validation, async checks | `references/form-patterns.md` |
| Routes, search params, loaders, navigation, auth-protected layouts, router setup | `references/router-patterns.md` |
| Server functions, middleware, sessions, SSR streaming, env, deploy adapters | `references/start-patterns.md` |
| Anything that touches **two or more** layers (e.g. route loader + server fn + form) | Each file from the relevant rows — read all before designing |

## Reference Index

| File | What you get |
|------|--------------|
| `references/query-patterns.md` | Vanilla Query: key factories + `queryOptions`, `staleTime`/`gcTime`, `placeholderData` vs `initialData`, optimistic mutations with rollback, error boundaries, intent prefetch, infinite queries, SSR dehydrate/hydrate, `useQueries`, cancellation, `select`, network mode, persistence, testing |
| `references/db-patterns.md` | DB collections: 5 critical rules, collection setup, live queries with joins, optimistic updates, shared collection instances, persistence handlers, common anti-patterns, advanced patterns (computed, aggregations, pagination) |
| `references/form-patterns.md` | Form: `createFormHook` + `useAppForm`, Zod schema validation, field/form/async validators with debounce, reusable field components (TextField, SelectField, SubmitButton), array fields, error handling with a11y, performance, anti-patterns |
| `references/router-patterns.md` | Router: `declare module` registration, router defaults, `from` narrowing, pathless layouts, search-param Zod validation, parallel + deferred loaders, lazy + auto code splitting, custom serializers, `notFound()`, route masks, integration with TanStack Query |
| `references/start-patterns.md` | Start: `createServerFn` with Zod validator, request + function middleware, secure cookie sessions, route protection, SSR streaming + hydration safety, prerender/ISR, API routes, env split, file separation, deploy adapters |

---

## Tripwires (not the contract)

These bullets exist so you can spot likely violations during a scan. **They are deliberately incomplete.** The full rules, examples, and edge cases live in the reference files. If a tripwire triggers, you must consult the referenced file before fixing.

### Query / DB

- Vanilla Query and DB collections are different paradigms — never mix them on the same entity.
- `staleTime: 0` (default) refetches on every mount. Tune by data volatility.
- Optimistic mutations without `cancelQueries` + rollback context will get overwritten by in-flight refetches.

**STOP. Read `references/query-patterns.md` in full before writing a `useQuery`, `useMutation`, prefetch, or SSR hydration boundary.** **STOP. Read `references/db-patterns.md` in full before creating a collection, live query, or persistence handler.** The three bullets above only flag the most common slip-ups.

### Form

- `defaultValues` drives type inference — manual generics fight it.
- Async validators without `asyncDebounceMs` hammer the network.
- Reuse Zod schemas across form + server function (in `*.shared.ts`).

**STOP. Read `references/form-patterns.md` in full before building or modifying a form, field component, or validator.** Field-level a11y attributes, `createFormHook` setup, and array-field patterns are not in this body.

### Router

- Without `declare module '@tanstack/react-router' { interface Register { router: typeof router } }`, `Link`/`useNavigate`/`useParams` silently degrade to `unknown`.
- Sequential `await`s in a loader create waterfalls — fan out with `Promise.all`.
- Throw `notFound()` / `redirect()` from loaders, not generic `Error`.

**STOP. Read `references/router-patterns.md` in full before adding a route, changing router setup, writing a loader, or modifying search-param validation.** Defaults (`defaultPreload`, `scrollRestoration`, global error/404), pathless layouts, masks, and deferred loaders all live in the reference.

### Start

- Server logic belongs in `createServerFn` with a Zod `validator()` — not raw `fetch` + API routes.
- Auth uses HTTP-only cookies. localStorage is XSS-bait.
- SSR loaders should `await` only critical data; stream the rest via `prefetchQuery` + `Suspense`.

**STOP. Read `references/start-patterns.md` in full before writing a server function, middleware, session helper, or SSR loader.** Cookie settings, middleware composition order, hydration-safety pitfalls, and adapter trade-offs are not in this body.

---

## End-of-task checklist

Each reference file has a scoped checklist with the real validation criteria. This umbrella confirms you actually consulted them:

- [ ] For each layer you touched, the corresponding reference file was read **in full**, not skimmed
- [ ] The scoped checklist in that reference file passes
- [ ] No mixed Query/DB paradigms on the same entity
- [ ] `pnpm run typecheck` and `pnpm run test` pass

If you cannot point to which reference file you read for a given change, the change is not done.
