# Router Data Loading

## Start a Page's Reads in the Route Loader

The route `loader` starts the data a page needs, not the component. The loader runs on hover preload (`defaultPreload: 'intent'`), on the server during SSR and on navigation. A component that starts its own fetch in `useEffect` (or only through `useQuery`) cannot preload, ships a skeleton in the SSR HTML and creates a waterfall after mount.

```tsx
export const Route = createFileRoute('/posts')({
  loader: async () => {
    const posts = await fetchPosts()
    return { posts }
  },
  component: PostsPage,
})

function PostsPage() {
  const { posts } = Route.useLoaderData()
  return <PostList posts={posts} />
}
```

Access route params in the loader for parameterized fetches; fetch independent data in parallel (see below).

## Search Params Reach the Loader Only Through `loaderDeps`

Declare in `loaderDeps` only the search keys the loader's reads depend on. The loader re-runs whenever a declared dep changes, so page-local params (sort, chart metric, open drawer, display options) must stay out of it, or every UI toggle re-runs every read.

```tsx
export const Route = createFileRoute('/sales')({
  validateSearch: salesSearchSchema,
  // Only the filters the reads key on; `sort`, `drawer`, `metric` stay page-local
  loaderDeps: ({ search }) => ({ period: search.period, product: search.product }),
  loader: ({ context: { queryClient }, deps }) =>
    queryClient.query(salesQueries.summary(deps)),
})
```

Deriving deps by omitting page-local keys from the shared filter schema (`schema.omit({...}).parse(search)`) keeps them in sync as filters grow.

## Pair With TanStack Query Through `queryClient.query`

When Query owns the cache, the loader and the component use **the same `queryOptions` factory**: one cache entry, one request, and the component reads what the loader started.

From `@tanstack/query-core` 5.104, `ensureQueryData`, `fetchQuery` and `prefetchQuery` are deprecated in favor of `queryClient.query(options)` (check the installed version; on older 5.x use `ensureQueryData` for awaited reads and `prefetchQuery` for fire-and-forget):

| Deprecated | Replacement |
| --- | --- |
| `ensureQueryData(opts)` | `query({ ...opts, staleTime: 'static' })` |
| `fetchQuery(opts)` | `query(opts)` |
| `prefetchQuery(opts)` | `void query(opts).catch(noop)` |

`query` resolves to the data (after `select`) and rejects with the fetch error. It ignores `enabled`, so a loader skips a disabled read itself (`cond && read(...)`), mirroring the component's `enabled`.

```tsx
import { queryOptions, useQuery } from '@tanstack/react-query'

export const postQueries = {
  detail: (postId: string) =>
    queryOptions({
      queryKey: ['posts', postId],
      queryFn: () => fetchPost(postId),
      staleTime: 5 * 60 * 1000,
    }),
}

export const Route = createFileRoute('/posts/$postId')({
  loader: ({ params, context: { queryClient } }) =>
    queryClient.query(postQueries.detail(params.postId)),
  component: PostPage,
})

function PostPage() {
  const { postId } = Route.useParams()
  const { data: post } = useQuery(postQueries.detail(postId)) // same factory, same entry
  return <PostContent post={post} />
}
```

Wire the `queryClient` into router context, set `defaultPreloadStaleTime: 0` so Query owns freshness, and with TanStack Start install `setupRouterSsrQueryIntegration({ router, queryClient })` so the server's cache is dehydrated into the HTML and hydrated on the client (see `start.md`). Build a fresh `QueryClient` per SSR request, never a module singleton.

## How a Loader Waits: Server vs Client

Whether to await depends on where the loader runs. Without a route `pendingComponent`, an awaiting client loader freezes the previous page (dead clicks, a filter bar that ignores input) until the slowest read lands.

- **Server (document request)**: await the first-paint reads, so the HTML ships with data and the cache hydrates without a refetch.
- **Client (navigation, preload, filter change)**: start the reads and return at once. Components pick up the in-flight queries, render their own skeletons and keep previous data while a filter changes.
- **Below-the-fold reads start only in the browser, unawaited.** Started on the server, they stay pending past dehydration and stream in; one that lands before hydration fills a section whose server HTML is a skeleton — a hydration mismatch. Pass them as a function so the server never starts them.
- **A loader read never rejects; the component that renders the data owns the error state.** On the server, drop a failed query from the cache and don't retry: every cached query is dehydrated into the HTML, an error crosses as a redacted plain `Error` the page renders as a generic failure, and a server retry only holds the document.

```ts
import { environmentManager, noop, type QueryClient } from '@tanstack/react-query'

export function readQuery(queryClient: QueryClient, options: QueryExecuteOptions /* … */) {
  const server = environmentManager.isServer()
  return queryClient.query(server ? { ...options, retry: false } : options).catch(() => {
    if (server) queryClient.removeQueries({ queryKey: options.queryKey, exact: true })
    return undefined
  })
}

export function settleRouteReads(
  firstPaint: ReadonlyArray<Promise<unknown> | false>,
  belowFold?: () => ReadonlyArray<Promise<unknown> | false>,
) {
  const settled = Promise.all(firstPaint.map((read) => read && read.catch(noop)))
  if (environmentManager.isServer()) return settled.then(noop)
  for (const read of belowFold?.() ?? []) if (read) read.catch(noop)
  return undefined
}

// Route
loader: ({ context: { queryClient }, deps }) =>
  settleRouteReads(
    [readQuery(queryClient, salesQueries.summary(deps)), deps.uf && readQuery(queryClient, salesQueries.byUf(deps))],
    () => [readQuery(queryClient, salesQueries.history(deps))],
  ),
```

When the app does render a `pendingComponent` and wants blocking navigation, awaiting on the client is a valid choice; decide per route, not by default.

`useQuery` never runs on the server: only loader-started data (or `useSuspenseQuery`) reaches the SSR HTML. Everything else arrives after hydration.

## Leverage Parallel Route Loading

TanStack Router loads nested route data in parallel, not sequentially. Fetch independent data with `Promise.all` inside a loader rather than awaiting each call in turn — chained `await`s create an artificial waterfall (three 200ms calls become 600ms instead of 200ms). Await sequentially only when one read needs another's result.

```tsx
export const Route = createFileRoute('/dashboard')({
  loader: ({ context: { queryClient } }) =>
    Promise.all([
      queryClient.query(statsQueries.overview()),
      queryClient.query(activityQueries.recent()),
      queryClient.query(notificationQueries.unread()),
    ]),
})
```

Parent and child route loaders also run in parallel automatically — navigating to `/posts/123` costs `max(parentLoader, childLoader)`, not their sum. A layout route's loader reads what gates its children (the user's teams, the companies list) alongside the children's first-paint reads, not before them.

- `beforeLoad` runs before `loader` and blocks every child; keep it to auth, redirects and context setup, and never make an uncached network call there (see `router-split-errors-context.md`).

## Loader Arguments: `cause`, `preload`, `deps`

Loaders receive `params`, `context`, `abortController`, `cause` (`'enter' | 'preload' | 'stay'`), `deps` and `preload` — use these instead of globals. Pass `abortController.signal` to `fetch` so stale requests cancel, and branch on `preload` to keep preloads cheap.

- **`cause === 'stay'`** (a search change on the page already on screen): start only what the cache misses (`staleTime: Infinity` for that call). The mounted views keep their own reads fresh; refetching them all on every filter tweak is wasted work.
- **Import heavy loader-only dependencies lazily** (`const { pageReads } = await import('./page-reads')`) so they stay out of the route tree's chunk. Loaders stay in the route file: `.lazy.tsx` never holds them and `autoCodeSplitting` does not split them by default.
