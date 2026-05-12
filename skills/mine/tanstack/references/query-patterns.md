# TanStack Query Patterns (Vanilla)

Patterns for the standard `@tanstack/react-query` client: queries, mutations, caching, prefetching, SSR. For TanStack DB collections and live queries see `db-patterns.md`.

## Contents

- Core Principles
- Query Keys (factories, `queryOptions`)
- Caching (`staleTime`, `gcTime`, defaults, `placeholderData` vs `initialData`)
- Mutations (optimistic + rollback, targeted invalidation, `useMutationState`)
- Error Handling (`useQueryErrorResetBoundary`, retry policy)
- Prefetching (intent, `ensureQueryData`)
- Infinite Queries
- SSR (Dehydrate / Hydrate)
- Parallel Queries (`useQueries`)
- Query Cancellation (AbortSignal)
- Performance (`select`, dependent queries)
- Offline / Network Mode + cache persistence
- Testing
- Validation Checklist

## Core Principles

- **Query keys are the cache identity.** Treat them as canonical, not throwaway strings.
- **Stale data is good.** Returning stale data instantly while refetching in the background is the default Query optimization — tune `staleTime` instead of forcing fresh fetches.
- **Server state ≠ client state.** Do not mirror Query state into local state or Zustand; read from the cache.

## Query Keys

### Key factories

Centralize keys in factories. Prevents typo bugs, makes invalidation a discoverable API.

```typescript
// lib/query-keys.ts
export const todoKeys = {
  all: ['todos'] as const,
  lists: () => [...todoKeys.all, 'list'] as const,
  list: (filters: TodoFilters) => [...todoKeys.lists(), filters] as const,
  details: () => [...todoKeys.all, 'detail'] as const,
  detail: (id: number) => [...todoKeys.details(), id] as const,
  comments: (id: number) => [...todoKeys.detail(id), 'comments'] as const,
};

// Targeted invalidation
queryClient.invalidateQueries({ queryKey: todoKeys.all });          // everything
queryClient.invalidateQueries({ queryKey: todoKeys.detail(5) });    // one item + nested
```

### Pair with `queryOptions` for full type inference

```typescript
import { queryOptions } from '@tanstack/react-query';

export const todoQueries = {
  detail: (id: number) =>
    queryOptions({
      queryKey: todoKeys.detail(id),
      queryFn: () => fetchTodo(id),
      staleTime: 5 * 60 * 1000,
    }),
};

// Usage — single source of truth for key + fn + config
const { data } = useQuery(todoQueries.detail(5));
await queryClient.prefetchQuery(todoQueries.detail(5));
```

## Caching

### `staleTime` by data volatility

Default is `0` — every mount triggers a background refetch. Tune per data type:

| Data type | staleTime | Why |
|-----------|-----------|-----|
| Real-time (stocks, live) | `0` | Must always refresh |
| Notifications, feeds | `30s – 1min` | Changes frequently |
| User-generated content | `1 – 5min` | Changes on user action |
| Reference data (categories) | `10 – 30min` | Rarely changes |
| Static content | `Infinity` | Never changes |

### `gcTime` retention

`gcTime` (formerly `cacheTime`) controls how long inactive data stays in memory after all observers unmount. Default `5min`. Raise it for data you want available on navigation back; lower it for memory-heavy queries.

### QueryClient defaults

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,      // 1 min — sensible default
      gcTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

Override per-query when needed via `queryOptions` factory.

### `placeholderData` vs `initialData` — non-obvious gotcha

| | `initialData` | `placeholderData` |
|--|---------------|-------------------|
| Persists to cache | yes | no |
| Considered fresh | yes (subject to `staleTime`) | no — always refetches |
| Use case | seeded from SSR / known good | optimistic UI while loading |

```typescript
// initialData — treated as canonical, won't refetch unless stale
useQuery({
  queryKey: ['user', id],
  queryFn: fetchUser,
  initialData: ssrUser,
  initialDataUpdatedAt: ssrTimestamp, // so staleTime works correctly
});

// placeholderData — instant UI, always refetches in background
useQuery({
  queryKey: ['users', filters],
  queryFn: () => fetchUsers(filters),
  placeholderData: (prev) => prev, // keep previous page during pagination
});
```

## Mutations

### Optimistic updates with rollback

The full pattern: `onMutate` snapshots and writes optimistically, `onError` rolls back, `onSettled` reconciles.

```typescript
const updateTodo = useMutation({
  mutationFn: (next: Todo) => api.update(next),

  onMutate: async (next) => {
    await queryClient.cancelQueries({ queryKey: todoKeys.detail(next.id) });
    const previous = queryClient.getQueryData(todoKeys.detail(next.id));
    queryClient.setQueryData(todoKeys.detail(next.id), next);
    return { previous }; // rollback context
  },

  onError: (_err, next, ctx) => {
    if (ctx?.previous) {
      queryClient.setQueryData(todoKeys.detail(next.id), ctx.previous);
    }
  },

  onSettled: (_data, _err, next) => {
    queryClient.invalidateQueries({ queryKey: todoKeys.detail(next.id) });
  },
});
```

Always `cancelQueries` first — otherwise an in-flight refetch can overwrite your optimistic write.

### Targeted invalidation

Prefer the narrowest key that covers the affected data. Broad keys waste bandwidth and re-render unrelated components.

```typescript
// BAD — invalidates every cached query
queryClient.invalidateQueries();

// GOOD — invalidates only the affected entity tree
queryClient.invalidateQueries({ queryKey: todoKeys.detail(id) });
```

### `useMutationState` for cross-component tracking

When several components must react to the same mutation (e.g., a toolbar and a list both want to show "saving…"), avoid prop-drilling the mutation. Use `useMutationState`:

```typescript
const pending = useMutationState({
  filters: { mutationKey: ['updateTodo'], status: 'pending' },
});
```

## Error Handling

### Error boundaries with `useQueryErrorResetBoundary`

```typescript
import { useQueryErrorResetBoundary } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';

function TodosPage() {
  const { reset } = useQueryErrorResetBoundary();
  return (
    <ErrorBoundary onReset={reset} fallbackRender={({ resetErrorBoundary }) => (
      <button onClick={resetErrorBoundary}>Retry</button>
    )}>
      <TodoList />
    </ErrorBoundary>
  );
}

useQuery({ queryKey, queryFn, throwOnError: true }); // forwards errors to boundary
```

### Retry policy

```typescript
useQuery({
  queryKey,
  queryFn,
  retry: (failureCount, error) => {
    if (error instanceof HTTPError && error.status < 500) return false; // never retry 4xx
    return failureCount < 3;
  },
  retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30_000),
});
```

## Prefetching

### Intent-based prefetch (hover / focus)

```typescript
function TodoLink({ id }: { id: number }) {
  const queryClient = useQueryClient();
  const prefetch = () =>
    queryClient.prefetchQuery({
      ...todoQueries.detail(id),
      staleTime: 30_000, // skip prefetch if recently fetched
    });

  return (
    <Link
      to={`/todos/${id}`}
      onMouseEnter={prefetch}
      onFocus={prefetch}
    >
      Todo #{id}
    </Link>
  );
}
```

### `ensureQueryData` — read-or-fetch

Returns cached data if present, otherwise fetches and caches. Ideal in route loaders.

```typescript
loader: ({ context, params }) =>
  context.queryClient.ensureQueryData(todoQueries.detail(params.id)),
```

## Infinite Queries

```typescript
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
  queryKey: ['todos', 'infinite'],
  queryFn: ({ pageParam }) => fetchPage(pageParam),
  initialPageParam: 0,
  getNextPageParam: (last, _all, lastPageParam) =>
    last.hasMore ? lastPageParam + 1 : undefined,
  maxPages: 10, // cap memory in long lists
});

// Guard before fetching to avoid double-fires
const onScrollEnd = () => {
  if (hasNextPage && !isFetchingNextPage) fetchNextPage();
};
```

`maxPages` evicts the oldest page when the cap is hit — critical for infinite feeds that would otherwise grow unbounded.

## SSR (Dehydrate / Hydrate)

```typescript
// server
const queryClient = new QueryClient();           // one per request
await queryClient.prefetchQuery(todoQueries.detail(id));
const dehydratedState = dehydrate(queryClient);

// client
<QueryClientProvider client={browserClient}>
  <HydrationBoundary state={dehydratedState}>
    <App />
  </HydrationBoundary>
</QueryClientProvider>
```

Use higher `staleTime` on the server to prevent an immediate client refetch right after hydration:

```typescript
new QueryClient({ defaultOptions: { queries: { staleTime: 60 * 1000 } } });
```

## Parallel Queries

### Dynamic parallelism with `useQueries`

```typescript
const results = useQueries({
  queries: userIds.map((id) => ({
    queryKey: ['user', id],
    queryFn: () => fetchUser(id),
  })),
});

const users = results.map((r) => r.data).filter(Boolean);
const isLoading = results.some((r) => r.isLoading);
```

Use this whenever the number of queries is dynamic — never call `useQuery` in a loop.

## Query Cancellation

`queryFn` receives an `AbortSignal`. Forward it to `fetch` so navigating away cancels in-flight requests:

```typescript
useQuery({
  queryKey: ['search', term],
  queryFn: ({ signal }) => fetch(`/api/search?q=${term}`, { signal }).then((r) => r.json()),
});
```

## Performance

### `select` for transform / subscription narrowing

`select` runs after data is returned and the component only re-renders when the selected value changes (structural sharing).

```typescript
const count = useQuery({
  queryKey: todoKeys.lists(),
  queryFn: fetchTodos,
  select: (todos) => todos.length, // re-renders only when count changes
});
```

### Dependent queries via `enabled`

```typescript
const { data: user } = useQuery({ queryKey: ['user', userId], queryFn: () => getUser(userId) });

const { data: projects } = useQuery({
  queryKey: ['projects', user?.id],
  queryFn: () => getProjects(user!.id),
  enabled: !!user?.id,
});
```

## Offline / Network Mode

### `networkMode`

- `'online'` (default): pauses queries when offline, refetches on reconnect.
- `'always'`: runs regardless of network (useful for local-first / mocked offline).
- `'offlineFirst'`: tries network once, falls back to cache.

```typescript
new QueryClient({ defaultOptions: { queries: { networkMode: 'offlineFirst' } } });
```

### Persisting the cache

```typescript
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

persistQueryClient({
  queryClient,
  persister: createSyncStoragePersister({ storage: window.localStorage }),
  maxAge: 1000 * 60 * 60 * 24, // 1 day
});
```

Use cache buster (version key) so deployments invalidate old data.

## Testing

```typescript
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }, // never retry in tests
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

test('fetches todos', async () => {
  const { result } = renderHook(() => useTodos(), { wrapper: createWrapper() });
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
});
```

## Validation Checklist

- [ ] Query keys flow through a factory, not literal arrays scattered in components
- [ ] `staleTime` is set per data volatility (not just defaulted to 0)
- [ ] Optimistic mutations have `cancelQueries` + rollback context
- [ ] Invalidations target the narrowest key that covers the change
- [ ] Loaders prefer `ensureQueryData` over `fetchQuery`
- [ ] Infinite queries declare `getNextPageParam` and a `maxPages` cap when feasible
- [ ] SSR uses `dehydrate` + `HydrationBoundary` with a per-request `QueryClient`
- [ ] Long-running searches forward `signal` from `queryFn`
- [ ] Component-level `select` is used when only a derived slice is consumed
- [ ] `retry` is `false` in tests
