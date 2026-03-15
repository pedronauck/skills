# System Implementation Patterns

> **Note on project-specific imports**: The patterns below use placeholder imports (`your-http-client`, `your-query-client`, etc.). Replace these with the actual paths used in the target project. Before writing code, read the existing systems in the codebase to confirm the exact import paths for the HTTP client, query client, error base class, and collection registry.

---

## API Service Layer (`adapters/<domain>-api.ts`)

The adapter owns all HTTP communication for the domain. It exports a single namespace object and a typed error class. All internal helpers stay private.

```ts
import type { FooResponse, CreateFooBody, UpdateFooBody } from "../types";

// --- Typed error class ---
// Extend the project's base error class if one exists (e.g. AppError, ApiError).
// Otherwise extend Error directly.
export class FooApiError extends Error {
  constructor(
    message: string,
    public readonly statusCode?: number,
    public readonly code?: string
  ) {
    super(message);
    this.name = "FooApiError";
  }
}

// --- Private helpers ---
function extractErrorMessage(error: unknown, fallback: string): string {
  if (!error || typeof error !== "object") return fallback;
  const e = error as Record<string, unknown>;
  // Handle both flat { message } and nested { error: { message } } shapes
  const nested = (e.error as Record<string, unknown> | undefined)?.message;
  const flat = e.message;
  return (typeof nested === "string" ? nested : typeof flat === "string" ? flat : null) ?? fallback;
}

async function handleResponse<T>(response: Response, fallback: string): Promise<T> {
  if (!response.ok) {
    let body: unknown;
    try { body = await response.json(); } catch { /* ignore */ }
    throw new FooApiError(
      extractErrorMessage(body, fallback),
      response.status
    );
  }
  if (response.status === 204) return null as T;
  return response.json() as Promise<T>;
}

// --- API namespace ---
// Use the project's typed HTTP client (e.g. openapi-fetch, ky, axios, or raw fetch).
// The important contract: accept signal, throw FooApiError on failure.

export const fooApi = {
  list: async (scopeId: string, signal?: AbortSignal): Promise<FooResponse[]> => {
    const response = await fetch(`/api/foos?scopeId=${scopeId}`, { signal });
    return handleResponse<FooResponse[]>(response, "Failed to fetch foos");
  },

  get: async (fooId: string, signal?: AbortSignal): Promise<FooResponse> => {
    const response = await fetch(`/api/foos/${fooId}`, { signal });
    return handleResponse<FooResponse>(response, "Failed to fetch foo");
  },

  create: async (body: CreateFooBody): Promise<FooResponse> => {
    const response = await fetch("/api/foos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return handleResponse<FooResponse>(response, "Failed to create foo");
  },

  update: async (fooId: string, body: UpdateFooBody): Promise<FooResponse> => {
    const response = await fetch(`/api/foos/${fooId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return handleResponse<FooResponse>(response, "Failed to update foo");
  },

  delete: async (fooId: string, signal?: AbortSignal): Promise<void> => {
    const response = await fetch(`/api/foos/${fooId}`, { method: "DELETE", signal });
    await handleResponse<null>(response, "Failed to delete foo");
  },
};
```

---

## Query Keys (`lib/query-keys.ts`)

```ts
export const fooKeys = {
  all: ["foo"] as const,
  // Scope by any ID that isolates the cache (userId, orgId, tenantId, etc.)
  list: (scopeId: string | null) =>
    [...fooKeys.all, "list", scopeId] as const,
  detail: (fooId: string) =>
    [...fooKeys.all, "detail", fooId] as const,
};
```

---

## Zod Schema (`lib/<domain>-schemas.ts`)

```ts
import { z } from "zod";

const fooStatusSchema = z.enum(["pending", "active", "completed"]);

export const fooSchema = z.object({
  id: z.string(),
  title: z.string(),
  status: fooStatusSchema,
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

// The schema passed to the DB collection's `schema` option
export const fooListItemSchema = fooSchema;

export type FooStatus = z.infer<typeof fooStatusSchema>;
```

---

## DB Collection (`db/<domain>-collection.ts`)

Only create this layer when optimistic updates or fine-grained reactivity are needed.
The collection must be treated as a singleton per scope — share it via context.

```ts
import { queryCollectionOptions } from "@tanstack/query-db-collection";
import { createCollection } from "@tanstack/react-db";

// Import the project's queryClient instance
import { queryClient } from "your-query-client";

import { fooApi } from "../adapters/foo-api";
import { fooListItemSchema } from "../lib/foo-schemas";
import { fooKeys } from "../lib/query-keys";
import type { FooResponse } from "../types";

const FOO_COLLECTION_PREFIX = "foo:";
const STALE_TIME = 1000 * 60 * 5;  // 5 min
const GC_TIME    = 1000 * 60 * 30; // 30 min

export function fooQueryOptions(scopeId: string) {
  return {
    queryKey: fooKeys.list(scopeId),
    queryFn: () => fooApi.list(scopeId),
    staleTime: STALE_TIME,
    gcTime: GC_TIME,
    retry: false,
  } as const;
}

export function fooCollectionKey(scopeId: string): string {
  return `${FOO_COLLECTION_PREFIX}${JSON.stringify(fooQueryOptions(scopeId).queryKey)}`;
}

export function createFooCollection(scopeId: string) {
  const { queryKey, queryFn } = fooQueryOptions(scopeId);

  return createCollection(
    queryCollectionOptions({
      id: queryKey.join("-"),
      queryKey,
      queryClient,
      queryFn,
      select: (data) => (Array.isArray(data) ? data : []),
      schema: fooListItemSchema,
      getKey: (item: FooResponse) => item.id,
      staleTime: STALE_TIME,
      gcTime: GC_TIME,
      retry: false,

      onInsert: async ({ transaction }) => {
        await Promise.all(
          transaction.mutations.map((m) => fooApi.create(m.modified as FooResponse))
        );
        return { refetch: false }; // Always false — avoids double-fetch after mutation
      },

      onUpdate: async ({ transaction }) => {
        const m = transaction.mutations[0];
        const original = m.original as FooResponse;
        await fooApi.update(original.id, m.changes as Partial<FooResponse>);
        return { refetch: false };
      },

      onDelete: async ({ transaction }) => {
        await Promise.all(
          transaction.mutations.map((m) => fooApi.delete((m.original as FooResponse).id))
        );
        return { refetch: false };
      },
    })
  );
}

export type FooCollectionInstance = ReturnType<typeof createFooCollection>;
```

---

## Collection Hook (`hooks/use-<domain>-collection.ts`)

If the project has a shared collection registry, use it to share the instance:

```ts
import { useCallback, useMemo } from "react";
// If the project has a shared collection registry:
import { useSharedCollection } from "your-collection-registry";
import { createFooCollection, fooCollectionKey } from "../db/foo-collection";
import type { FooCollectionInstance } from "../db/foo-collection";

export function useFooCollection(scopeId: string): FooCollectionInstance {
  const key = useMemo(() => fooCollectionKey(scopeId), [scopeId]);
  const factory = useCallback(() => createFooCollection(scopeId), [scopeId]);
  return useSharedCollection(key, factory);
}
```

If the project has no shared registry, manage the instance in the provider:

```ts
import { useMemo } from "react";
import { createFooCollection } from "../db/foo-collection";

export function useFooCollection(scopeId: string) {
  // useMemo is safe here because scopeId changes cause a new collection
  return useMemo(() => createFooCollection(scopeId), [scopeId]);
}
```

---

## Query Hook (`hooks/use-<action>.ts`)

```ts
import { queryOptions, useQuery } from "@tanstack/react-query";
import { fooApi } from "../adapters/foo-api";
import { fooKeys } from "../lib/query-keys";
import type { FooResponse } from "../types";

// Export queryOptions separately for route loaders and prefetching
export function fooListQueryOptions(scopeId: string | null) {
  return queryOptions({
    queryKey: fooKeys.list(scopeId),
    queryFn: ({ signal }) => fooApi.list(scopeId!, signal),
    staleTime: 60_000,
    enabled: Boolean(scopeId),
  });
}

export function useFooList(scopeId: string | null, options?: { enabled?: boolean }) {
  const enabled = Boolean(scopeId) && (options?.enabled ?? true);
  return useQuery({ ...fooListQueryOptions(scopeId), enabled });
}

export function useFooDetail(fooId: string) {
  return useQuery<FooResponse>({
    queryKey: fooKeys.detail(fooId),
    queryFn: ({ signal }) => fooApi.get(fooId, signal),
    enabled: Boolean(fooId),
  });
}
```

---

## Mutation Hook (`hooks/use-create-<entity>.ts`)

**CRITICAL**: Always receive `collection` as a parameter. Never create a new collection inside.

```ts
import { useCallback, useState } from "react";
import type { FooCollectionInstance } from "../db/foo-collection";
import type { FooResponse } from "../types";

type CreateFooInput = Pick<FooResponse, "title" | "status">;

export function useCreateFoo(collection: FooCollectionInstance) {
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutateAsync = useCallback(async (input: CreateFooInput): Promise<FooResponse> => {
    setIsPending(true);
    setError(null);
    try {
      const optimistic: FooResponse = {
        id: crypto.randomUUID(),
        ...input,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      const tx = collection.insert(optimistic);
      await tx.isPersisted.promise;
      return optimistic;
    } catch (err) {
      const resolved = err instanceof Error ? err : new Error("Failed to create foo");
      setError(resolved);
      throw resolved;
    } finally {
      setIsPending(false);
    }
  }, [collection]);

  const mutate = useCallback((input: CreateFooInput) => { void mutateAsync(input); }, [mutateAsync]);
  const reset = useCallback(() => setError(null), []);

  return { mutateAsync, mutate, isPending, error, reset };
}
```

---

## Context (`contexts/<domain>-context.tsx`)

```ts
import { createContext, use, useMemo } from "react";
import type { FooCollectionInstance } from "../db/foo-collection";

interface FooContextValue {
  collection: FooCollectionInstance;
}

export const FooContext = createContext<FooContextValue | null>(null);

export function FooProvider({
  collection,
  children,
}: {
  collection: FooCollectionInstance;
  children: React.ReactNode;
}) {
  const value = useMemo(() => ({ collection }), [collection]);
  return <FooContext value={value}>{children}</FooContext>;
}

// Consumer hook — throws descriptively if used outside the provider
export function useFooContext(): FooContextValue {
  const ctx = use(FooContext);
  if (!ctx) throw new Error("useFooContext must be used within <FooProvider>");
  return ctx;
}
```

For performance-sensitive trees with many consumers, split into focused sub-contexts:

```ts
export const FooCoreContext    = createContext<FooCoreValue | null>(null);
export const FooUiContext      = createContext<FooUiValue | null>(null);
export const FooActionsContext = createContext<FooActionsValue | null>(null);

export function FooProvider({ children, ...props }: FooProviderProps) {
  const state = useFooProviderState(props);
  return (
    <FooCoreContext value={state.coreValue}>
      <FooUiContext value={state.uiValue}>
        <FooActionsContext value={state.actionsValue}>
          {children}
        </FooActionsContext>
      </FooUiContext>
    </FooCoreContext>
  );
}
```

---

## XState Store (`stores/<domain>-store.ts`)

Use for complex async state machines — multi-step flows, polling, event emission.

```ts
import { createStore } from "@xstate/store";
import { fooApi } from "../adapters/foo-api";
import type { FooResponse } from "../types";

interface FooStoreContext {
  data: FooResponse | null;
  isLoading: boolean;
  error: string | null;
}

export const fooStore = createStore({
  context: {
    data: null,
    isLoading: false,
    error: null,
  } as FooStoreContext,

  emits: {
    dataLoaded: (_payload: { data: FooResponse }) => {},
    loadFailed: (_payload: { error: string }) => {},
  },

  on: {
    load: (context, event: { id: string }, enqueue) => {
      enqueue.effect(async () => {
        try {
          const data = await fooApi.get(event.id);
          enqueue.emit.dataLoaded({ data });
          fooStore.trigger.setData({ data });
        } catch (err) {
          const error = err instanceof Error ? err.message : "Failed to load";
          enqueue.emit.loadFailed({ error });
          fooStore.trigger.setError({ error });
        }
      });
      return { ...context, isLoading: true, error: null };
    },

    setData: (context, event: { data: FooResponse }) => ({
      ...context,
      data: event.data,
      isLoading: false,
      error: null,
    }),

    setError: (context, event: { error: string }) => ({
      ...context,
      error: event.error,
      isLoading: false,
    }),

    reset: (_context) => ({ data: null, isLoading: false, error: null }),
  },
});
```

---

## View-Model Hook

Compose multiple hooks for a single page/shell component. Return a flat object.

```ts
import { useFooDetail } from "./use-foo-detail";
import { useCreateFoo } from "./use-create-foo";
import { useDeleteFoo } from "./use-delete-foo";
import type { FooCollectionInstance } from "../db/foo-collection";

export function useFooDetailViewModel(fooId: string, collection: FooCollectionInstance) {
  const { data: detail, isLoading, error } = useFooDetail(fooId);
  const create = useCreateFoo(collection);
  const remove = useDeleteFoo(collection);

  return { detail, isLoading, error, create, remove };
}
```

---

## Types (`types.ts`)

Export clean domain types. Derive from the project's API contract when available.

```ts
// If the project has a generated API contract, derive from it:
// import type { OperationResponse } from "your-api-contract";
// type FooContract = OperationResponse<"getFoo">;
// export type FooResponse = FooContract;

// Otherwise define types directly:
export interface FooResponse {
  id: string;
  title: string;
  status: FooStatus;
  createdAt: string;
  updatedAt: string;
}

export type FooStatus = "pending" | "active" | "completed";

export interface CreateFooBody {
  title: string;
  status?: FooStatus;
}

export interface UpdateFooBody {
  title?: string;
  status?: FooStatus;
}

/**
 * Aggregated UI state for the foo detail view.
 *
 * Derivation rules:
 * - isActive: status === "active"
 * - canEdit: isActive && !isDeleting
 */
export interface FooDetailState {
  foo: FooResponse;
  isActive: boolean;
  canEdit: boolean;
}
```
