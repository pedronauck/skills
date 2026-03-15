# System Directory Layout

## Canonical Structure

```
systems/<domain>/
├── index.ts                         # REQUIRED — public API barrel
├── types.ts                         # Domain types
│
├── adapters/
│   ├── <domain>-api.ts              # API service functions + error class
│   └── <domain>-api.test.ts
│
├── lib/
│   ├── query-keys.ts                # TanStack Query key factory
│   ├── <domain>-schemas.ts          # Zod schemas (collections + forms)
│   ├── <domain>-utils.ts            # Pure domain-specific utilities
│   ├── collection-utils.ts          # Helpers for collection data transforms
│   └── constants.ts                 # Domain constants (timeouts, limits, etc.)
│
├── db/
│   ├── <domain>-collection.ts       # TanStack DB collection factory
│   └── __tests__/
│       └── <domain>-collection.test.ts
│
├── hooks/
│   ├── __tests__/                   # Subdirectory for complex/integration tests
│   │   └── use-<action>.test.tsx
│   ├── use-<domain>-collection.ts   # Hook that manages the shared collection instance
│   ├── use-<action>.ts              # Query hooks
│   ├── use-create-<entity>.ts       # Mutation hooks
│   ├── use-update-<entity>.ts
│   ├── use-delete-<entity>.ts
│   └── use-<domain>-view-model.ts   # Composed view-model hook for a page/shell
│
├── contexts/
│   ├── <domain>-context.tsx         # Context + provider + re-exported consumer hooks
│   └── <domain>-context.test.tsx
│
├── stores/
│   ├── <domain>-store.ts            # XState store
│   └── <domain>-store.test.ts
│
├── components/
│   ├── <component-name>.tsx
│   ├── <component-name>.test.tsx
│   ├── stories/
│   │   └── <component-name>.stories.tsx
│   └── index.ts                     # Component barrel
│
└── guards/
    ├── <guard-name>.ts
    └── <guard-name>.test.ts
```

## File Naming Rules

| Layer | Pattern | Example |
|-------|---------|---------|
| API service | `<domain>-api.ts` | `issues-api.ts` |
| Types | `types.ts` | `types.ts` |
| Query keys | `query-keys.ts` | `query-keys.ts` |
| Zod schema | `<domain>-schemas.ts` | `issue-schemas.ts` |
| Collection | `<domain>-collection.ts` | `issues-collection.ts` |
| Hook | `use-kebab-case.ts` | `use-create-issue.ts` |
| Context | `<domain>-context.tsx` | `issue-details-context.tsx` |
| Store | `<domain>-store.ts` | `api-key-store.ts` |
| Component | `kebab-case.tsx` | `issue-list-item.tsx` |
| Story | `<component>.stories.tsx` | `issue-list.stories.tsx` |
| Test | `<file>.test.ts(x)` | `use-delete-issue.test.tsx` |

## Folders That Are Optional

Only create these when the system actually needs them:

- `db/` — only when data requires optimistic updates or fine-grained reactivity
- `contexts/` — only when a collection instance or state tree must be shared across a subtree
- `stores/` — only for complex async state machines (multi-step flows, polling, event emission)
- `guards/` — only for route-level or access-control logic

## Index Barrel Convention

Use explicit named exports organized by labeled sections. No `export * from`:

```ts
// Types
export type { FooType, FooStatus } from "./types";

// Hooks
export { useFooList } from "./hooks/use-foo-list";
export { useCreateFoo } from "./hooks/use-create-foo";

// Components
export { FooList, FooDetail } from "./components";

// Utilities
export { fooHelperFn } from "./lib/foo-utils";

// Query Keys
export { fooKeys } from "./lib/query-keys";

// API
export { fooApi, FooApiError } from "./adapters/foo-api";
```

## Component Barrel Convention

`components/index.ts` exports all public components by name:

```ts
export { FooCard } from "./foo-card";
export { FooList } from "./foo-list";
export { FooGuard } from "./foo-guard";
```

## Cross-System Imports

- Import from another system using its public barrel: `import { issuesApi } from "@/systems/issues"`.
- Never reach into another system's internals: `import { xxx } from "@/systems/issues/adapters/issues-api"` is forbidden.
- Shared utilities that multiple systems need belong in the project's shared `lib/` directory, not inside any system folder.
