# Query Caching

## Set Appropriate staleTime

`staleTime` is how long data stays fresh before refetching on a new mount. Default is `0` (immediately stale → refetch every mount). Match it to how often the data actually changes: set a sensible `QueryClient` default and override per query.

```tsx
const { data: profile } = useQuery({
  queryKey: ['user-profile', userId],
  queryFn: () => fetchUserProfile(userId),
  staleTime: 5 * 60 * 1000, // profile rarely changes
})

// Sensible default, override per query
const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60 * 1000 } },
})
```

| Data type | staleTime |
| --- | --- |
| Real-time (stocks, live feeds) | `0` |
| Frequently changing (notifications) | 30s–1min |
| User-generated content | 1–5min |
| Reference data (categories, config) | 10–30min |
| Static content | `Infinity` |

Stale data is still returned instantly — the refetch runs in the background. For SSR, raise `staleTime` to avoid an immediate client refetch.

## Configure gcTime for Inactive Query Retention

`gcTime` (formerly `cacheTime`) is how long an *inactive* query stays cached before garbage collection; the countdown starts when the last observer unmounts. Default is 5min. Longer gcTime = instant return on revisit; shorter = less memory. Avoid `Infinity` (memory leak) and `0` (loses the cache on unmount).

```tsx
const { data } = useQuery({
  queryKey: ['dashboard-stats'],
  queryFn: fetchDashboardStats,
  gcTime: 30 * 60 * 1000, // user returns to the dashboard often
})
```

Lifecycle: `mount → fresh (staleTime) → stale → unmount → gcTime countdown → garbage collected`. Remounting before `gcTime` expires returns cached data instantly.

| Scenario | gcTime |
| --- | --- |
| Frequently revisited routes | 15–30min |
| Detail pages (viewed once) | 2–5min |
| Large payloads | 1–2min |
| SSR hydration | ≥ 2s (never `0`) |

`gcTime < staleTime` is rarely useful.

## Use Targeted Invalidation

Invalidation marks matching queries stale, triggering a background refetch when they're next used. Match precisely: reread affected entries (list, detail, dependent counts) only when authoritative response/cache writers cannot reconcile them. Bare `invalidateQueries()` nukes the whole cache.

```tsx
const mutation = useMutation({
  mutationFn: addComment,
  onSuccess: (data, { postId }) => {
    queryClient.invalidateQueries({ queryKey: ['posts', postId, 'comments'] })
    queryClient.invalidateQueries({ queryKey: ['posts', postId, 'comment-count'] })
  },
})
```

Matching modes:

```tsx
queryClient.invalidateQueries({ queryKey: ['todos'] })              // prefix: ['todos'], ['todos', 1], …
queryClient.invalidateQueries({ queryKey: ['todos'], exact: true }) // only ['todos']
queryClient.invalidateQueries({ predicate: (q) => q.queryKey.includes('user-generated') })
```

`refetchType` controls what actually refetches: `'active'` (default) refetches only queries with observers; use `'all'`, `'inactive'`, or `'none'` (mark stale without refetching) for the rest. For a value you already hold, prefer `setQueryData` over invalidation.

## Placeholder Data vs Initial Data

Both show data before the fetch resolves, but `initialData` is written to the cache as real data (respects `staleTime`, shared with other observers) while `placeholderData` is temporary — not cached, always refetches, flagged by `isPlaceholderData`.

```tsx
// initialData: known-good data (e.g. SSR) — persists to cache
useQuery({
  queryKey: ['posts', serverData.id],
  queryFn: () => fetchPost(serverData.id),
  initialData: serverData,
  initialDataUpdatedAt: serverData.fetchedAt, // for correct stale calc
})

// placeholderData: temporary preview from a list — does not persist
const { data, isPlaceholderData } = useQuery({
  queryKey: ['posts', postId],
  queryFn: () => fetchPost(postId),
  placeholderData: () =>
    queryClient.getQueryData<Post[]>(['posts'])?.find((p) => p.id === postId),
})
```

| Behavior | `initialData` | `placeholderData` |
| --- | --- | --- |
| Persisted to cache | Yes | No |
| `staleTime` applies | Yes | No (always fetches) |
| `isPlaceholderData` | `false` | `true` |
| Shown to other components | Yes | No |
| Use case | SSR, complete known data | Preview, previous page |

For pagination, `placeholderData: keepPreviousData` keeps the last page visible while the next loads — check `isPlaceholderData` to dim the UI.

## Coalesce Live and Focus Invalidation

When the server pushes change signals (WebSocket, Pusher, SSE) or the app refreshes on window focus, uncoordinated invalidation becomes the dominant load: every hook instance with its own listener, every signal invalidating a whole key family with `cancelRefetch: true`, and a cron publishing every minute re-read everything on screen. Route all of it through one coalescer per QueryClient:

- **One window per client** (e.g. 200 ms, fixed — continuous traffic must not postpone it forever). Collect targets, drop a key already covered by a pending prefix, then flush once.
- **Refetch only what is mounted, never cancel what is in flight**: `invalidateQueries({ queryKey, refetchType: 'active', predicate }, { cancelRefetch: false })`. A read that was mid-fetch when its signal arrived may have read old data: invalidate it again when that fetch settles.
- **One shared focus/visibility listener** for every consumer, not one per hook. After a long hidden period (frozen tab, sleeping laptop) refresh what the channel would have refreshed.
- **Map each signal to the narrowest keys**: a key prefix, or a prefix narrowed by a `predicate` (one team's reads, one record's detail). Invalidating the module root (`['tasks']`) on every signal refetches other teams' boards and every open list.
- **Skip the author's own echo.** The tab that made the change already patched its cache (optimistic update or authoritative response). Send its socket id with the mutation (a server-function middleware header) and exclude that socket when publishing; then make sure the author's *other* reads the patch cannot settle (counts, other lists, comments) are refreshed explicitly, or they go stale for the author only.
- **After a mutation, refresh only what the patch cannot settle**, through the same coalescer. When the caller awaits fresh data (a form that closes on success), flush the window and resolve once the targeted mounted reads have refetched.

Size `staleTime` per factory to how fast the data actually changes (analytics recomputed every few hours: minutes; live collaborative data: the global default). A short global `staleTime` on slow-moving data refetches on every page change.
