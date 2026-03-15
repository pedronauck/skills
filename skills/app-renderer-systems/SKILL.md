---
name: app-renderer-systems
description: Guides creation and modification of domain feature systems organized under a systems/ directory. Covers directory layout, API service layer patterns, TanStack Query and DB collection setup, React context and XState store conventions, hook organization, and public API barrel exports. Use when adding a new domain system, extending an existing one, or fixing bugs in a system-layer codebase. Don't use for generic React component work, backend API implementation, or codebases not organized around a systems/ domain pattern.
allowed-tools: Read, Grep, Glob
---

# Feature Systems Guide

A "system" is a self-contained, domain-driven module that owns everything related to one domain: its API calls, data layer, hooks, components, and public API. Systems live under a `systems/<domain>/` directory.

Read `references/directory-layout.md` for the full directory structure and naming conventions.
Read `references/patterns.md` for annotated implementation patterns per layer.

## Quick Reference

### Mandatory Companion Skills

Activate alongside this skill — systems span multiple technical domains:

| Situation | Activate |
|-----------|----------|
| Any hook or component | `react` + `tanstack` |
| TanStack DB collection | `tanstack` |
| XState store | `xstate` |
| Utility functions | `es-toolkit` |
| Writing/fixing tests | `test-antipatterns` + `vitest` |
| Bug fix | `systematic-debugging` + `no-workarounds` |

### System Directory at a Glance

```
systems/<domain>/
├── index.ts               # Public API barrel — required for every system
├── types.ts               # TypeScript types for this domain
├── adapters/              # API service layer (HTTP calls, error types)
│   └── <domain>-api.ts
├── lib/                   # Pure utilities, schemas, constants, query keys
│   ├── query-keys.ts      # TanStack Query key factory
│   ├── <domain>-schemas.ts
│   └── constants.ts
├── db/                    # TanStack DB collections (reactive/optimistic data)
│   └── <domain>-collection.ts
├── hooks/                 # React hooks
│   ├── __tests__/
│   └── use-<action>.ts
├── contexts/              # React contexts + providers
│   └── <domain>-context.tsx
├── stores/                # XState stores (complex async state machines)
│   └── <domain>-store.ts
├── components/            # React UI components
│   ├── stories/
│   └── index.ts
└── guards/                # Route guards / access checks
```

## Step-by-Step: Creating a New System

### Step 1 — Define types.ts

- Export clean domain types; never expose raw API response shapes.
- Derive from the project's API contract types when available.
- Document complex aggregated types with JSDoc explaining derivation rules and invariants.

### Step 2 — Build the API service layer

- Create `adapters/<domain>-api.ts`.
- Use the project's HTTP client for API calls.
- Export a single namespace object: `export const <domain>Api = { list, create, update, delete }`.
- Export a typed error class: `export class <Domain>ApiError extends Error { ... }`.
- Accept `signal?: AbortSignal` on every function to support query cancellation.
- Keep all internal helpers (error extraction, response normalization) private to the module.

### Step 3 — Add lib/query-keys.ts

```ts
export const <domain>Keys = {
  all: ["<domain>"] as const,
  list: (scopeId: string | null) => [...<domain>Keys.all, "list", scopeId] as const,
  detail: (id: string) => [...<domain>Keys.all, "detail", id] as const,
};
```

- Scope keys with any identifier (userId, orgId, etc.) that isolates the cache correctly.
- Use `as const` on every key tuple.

### Step 4 — (Optional) Create a DB collection

Create `db/<domain>-collection.ts` **only** when data needs optimistic updates or fine-grained reactivity. Read `references/patterns.md` for the full pattern.

Key rules:
- Export `create<Domain>Collection(scopeId)` factory function.
- Export `<domain>CollectionKey(scopeId)` for external registry/cache keying.
- Export `type <Domain>CollectionInstance = ReturnType<typeof create<Domain>Collection>`.
- Handlers (`onInsert`, `onUpdate`, `onDelete`) call the API service and sync the query cache.
- Always return `{ refetch: false }` from handlers to avoid double-fetches.

### Step 5 — Write hooks

- **Query hooks**: Wrap `useQuery` or `queryOptions`; accept a scope ID + optional `{ enabled? }`.
- **Mutation hooks**: Accept `collection: <Domain>CollectionInstance` as a parameter — never create a new collection internally.
- **View-model hooks**: Compose multiple hooks for a page/shell component; return a flat object.
- Place tests in `hooks/__tests__/` or co-locate as `use-xxx.test.tsx`.

### Step 6 — (Optional) Add context

Create `contexts/<domain>-context.tsx` when a collection instance or combined state must be shared across a component subtree.

```ts
// Always nullable context — consumer hook throws if used outside provider
export const <Domain>Context = createContext<<Domain>ContextValue | null>(null);
```

- Export the context, provider component, and re-export consumer hooks from the same file.
- For performance-sensitive trees, split into Core / UI / Operations sub-contexts.

### Step 7 — (Optional) Add an XState store

Create `stores/<domain>-store.ts` for complex async state machines (multi-step flows, polling, event emission).

```ts
export const <domain>Store = createStore({
  context: { ... } as <Domain>Context,
  emits: { ... },
  on: {
    someEvent: (context, event, enqueue) => {
      enqueue.effect(async () => { ... });
      return { ...context, isLoading: true };
    },
  },
});
```

### Step 8 — Wire up index.ts

Organize the barrel with labeled sections and explicit named exports:

```ts
// Types
export type { <Domain>Type } from "./types";

// Hooks
export { use<Domain>, use<Domain>Mutation } from "./hooks";

// Components
export { <Domain>Component } from "./components";

// Utilities
export { <domain>HelperFn } from "./lib/<domain>-utils";

// Query Keys
export { <domain>Keys } from "./lib/query-keys";

// API
export { <domain>Api, <Domain>ApiError } from "./adapters/<domain>-api";
```

## Critical Rules

1. **Never create collection instances in mutation hooks.** Mutation hooks receive `collection` as a parameter. Creating a new collection internally causes "key not found" errors at runtime.
2. **Unidirectional dependency flow.** `adapters → lib → db → hooks → components`. Adapters never import from hooks or components.
3. **Scope query keys.** Any query depending on an authenticated scope (user, org, tenant) must include that scope ID in its key to prevent stale cross-scope data.
4. **Typed errors in the API layer.** Never throw raw errors from adapters. Use a typed error class so consumers can distinguish error types without inspecting message strings.
5. **AbortSignal propagation.** Pass `signal` from the `queryFn` context through to every API call for proper query cancellation.
6. **Zod schemas in lib/.** Place all Zod schemas in `lib/<domain>-schemas.ts`. Collections reference them via the `schema` option for runtime validation.

## Error Handling

- **API layer throws typed error**: TanStack Query catches and exposes it via `query.error`.
- **Collection handler throws**: TanStack DB automatically rolls back the optimistic update.
- **"key not found" in collection**: A new collection instance was created inside a mutation hook instead of receiving the shared one — fix the hook signature.
- **Stale cross-scope data**: Add the scope ID to the query key and verify that `enabled` guards check `Boolean(scopeId)`.

## Detailed References

- `references/directory-layout.md` — Full directory structure, file naming, and barrel conventions
- `references/patterns.md` — Annotated code patterns for the API layer, collections, hooks, contexts, and stores
