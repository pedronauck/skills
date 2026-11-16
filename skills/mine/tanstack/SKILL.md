---
name: tanstack
description: "Implement React data, routes, server functions, or forms with TanStack. Covers Query, Router, Start (server functions, selective SSR), and Form; excludes TanStack DB and unrelated state or routing libraries."
---

# TanStack

Read the reference matched by the API or behavior being changed. Load adjacent references only for concerns the change crosses; reuse relevant context already read.

## Branches

| When you are… | Reference |
| --- | --- |
| Defining or changing query keys / factories | `references/query-keys.md` |
| Setting staleTime, gcTime, invalidation, live/focus refresh, placeholder/initial data | `references/query-caching.md` |
| Writing mutations, optimistic updates, or mutation state | `references/query-mutations.md` |
| Prefetching, parallel queries, infinite queries, or cancellation | `references/query-fetch-patterns.md` |
| SSR dehydrate/hydrate, offline networkMode, or query persistence | `references/query-ssr-offline.md` |
| Query error boundaries or select/performance | `references/query-errors-performance.md` |
| Registering the router, `from` typing, virtual routes, or router defaults | `references/router-type-and-org.md` |
| Route loaders, `queryClient.query` in loaders, loaderDeps, or SSR vs client loader waiting | `references/router-data-loading.md` |
| Search params, Link/navigate, route masks, or preload | `references/router-search-nav.md` |
| Lazy routes, not-found, route context, or auth beforeLoad (session caching) | `references/router-split-errors-context.md` |
| Start server functions, authorization, per-request memo, `ssr` modes, SSR Query integration, function middleware | `references/start.md` |
| TanStack Form hooks, Zod validators, or field components | `references/form.md` |

Apply the technical rules relevant to the changed behavior.

## Tripwires

**Query** — array keys that include every dependency; route live/focus invalidation through one coalescer with the narrowest keys, `refetchType: 'active'` and `cancelRefetch: false`; reconcile mutations through canonical keys: update from authoritative responses or invalidate when the owning read model requires a server reread; optimistic cache writes need rollback; never put non-serializable values in keys.

**Router** — register the router type; validate search with defaults (`.catch()`) and strip them from URLs; the loader starts a page's reads with the same `queryOptions` the component uses (`queryClient.query`, Query ≥ 5.104; `ensureQueryData` before); `loaderDeps` holds only the keys reads depend on; await first-paint reads on the server only, never reject a loader read; `beforeLoad` runs on every navigation and preload, so cache what it reads; `throw redirect(...)` not `return`.

**Start** — every server function authorizes and validates itself (the route guard is UX); memoize auth reads per request; one `QueryClient` per SSR request; everything a loader caches is serialized into the HTML; `'data-only'` before `ssr: false`; hydration does not re-run `beforeLoad`.

**Form** — complete `defaultValues` for inference; Zod at form/field level; debounce async validators to fit endpoint cost and interaction needs; `role="alert"` on field errors; `preventDefault` on submit.
