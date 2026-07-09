---
name: tanstack
description: TanStack ecosystem patterns for React — Query (caching, mutations, prefetching, SSR hydration), DB (collections, live queries, optimistic updates), Form (state, Zod validation, field components), Router (file-based routing, type-safe navigation, search params, loaders), and Start (server functions, middleware, auth, SSR). Use when writing or reviewing code with any of these TanStack libraries. Don't use for non-TanStack data libraries (SWR, Apollo, RTK Query), non-React TanStack ports (Solid, Svelte), or backend-only work.
allowed-tools: Read, Grep, Glob
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# TanStack Developer Guide

Before writing or reviewing code in a TanStack area, read the matching reference file(s) below **in full** — they hold the patterns, anti-patterns, and validation checklists this page only points to. The reference is the contract; this page is the index.

## Which reference to read

| When you are working on… | Read in full first |
|--------------------------|--------------------|
| `useQuery`/`useMutation`, prefetch, infinite lists, SSR hydration, or `staleTime`/cache config | `references/query-patterns.md` |
| Typed collections, live queries, optimistic collection mutations, or persistence handlers | `references/db-patterns.md` |
| Forms, field components, Zod validation, or async/debounced field checks | `references/form-patterns.md` |
| Routes, loaders, search-param validation, navigation, auth layouts, or router setup | `references/router-patterns.md` |
| Server functions, middleware, sessions, SSR streaming, env split, or deploy adapters | `references/start-patterns.md` |

Working across two or more areas (e.g. a route loader that calls a server function and feeds a form)? Read every matching file before you design.

Choose one data paradigm per entity — vanilla Query **or** DB collections, never both on the same entity.

## Done

For each area you touched, that reference file's **Validation Checklist** passes and `pnpm run typecheck` + `pnpm run test` are green. If you cannot name the reference file behind a change, the change is not finished.
