# TanStack Start: Server Functions, Selective SSR and Request Scope

Router and Query rules still apply (`router-data-loading.md` for loaders, `query-caching.md` for invalidation). This file covers what only exists under Start. Method names follow the installed `@tanstack/react-start` types; check them before copying (the validator step, for example, has been named differently across releases).

## Every Server Function Authorizes Itself

A route guard (`beforeLoad`) is navigation UX; it does not protect data. A server function is a public HTTP endpoint: anything can call it, with any input, without passing through the route. Each data server function authorizes at the top of its handler and fails closed, and validates its input on the server.

```ts
import { createServerFn, createServerOnlyFn } from '@tanstack/react-start'

export const requirePermission = createServerOnlyFn(async (permission: Permission) => {
  const user = await readSessionUser() // memoized per request, below
  if (!user) throw new Error('Unauthorized')
  if (!user.permissions.includes(permission)) throw new Error('Forbidden')
  return user
})

export const fetchSalesSummary = createServerFn({ method: 'GET' })
  .validator((input: unknown) => salesSearchSchema.parse(input))
  .handler(async ({ data }) => {
    await requirePermission('analytics:view')
    return queries.salesSummary(data)
  })
```

- Wrap server-only helpers in `createServerOnlyFn` so an accidental client import fails instead of shipping server code.
- Return only the fields the view uses; a server function's return value is visible in the network tab and, when a loader starts it, serialized into the SSR HTML.
- A read the caller is refused (no session, removed member) can return `null` or a typed `{ refused: reason }` for guards that redirect, instead of throwing an error that crosses into dehydrated state.

## Memoize Authorization Reads per Request

An SSR render runs the route guard and every loader's server functions inside one HTTP request. Without a request scope each call repeats the session, membership and permission queries (dozens of identical statements for one page). Memoize them on the `Request` object: never across requests or users, collected with the request.

```ts
import { createServerOnlyFn } from '@tanstack/react-start'
import { getRequest } from '@tanstack/react-start/server'

const scopes = new WeakMap<Request, Map<string, Promise<unknown>>>()

export const memoizeForRequest = createServerOnlyFn(
  <T>(key: string, load: () => Promise<T>): Promise<T> => {
    let request: Request | undefined
    try { request = getRequest() } catch { return load() } // scripts, cron, tests: no scope
    let entries = scopes.get(request)
    if (!entries) scopes.set(request, (entries = new Map()))
    const cached = entries.get(key)
    if (cached) return cached as Promise<T>
    const pending = load()
    entries.set(key, pending)
    pending.catch(() => { if (entries.get(key) === pending) entries.delete(key) }) // a failure can retry
    return pending
  },
)
```

A signed session cookie cache (e.g. better-auth `session.cookieCache`) removes the session lookup itself; keep membership and roles out of it, so a role change or deactivation applies on the next request. Accept and document the cookie's revocation lag.

## Choose SSR per Route

`ssr` on a route takes `true` (default), `'data-only'`, `false`, or a function of `{ params, search }` returning one of them.

| Mode | `beforeLoad` + `loader` on the server | Component rendered on the server |
| --- | --- | --- |
| `true` | yes | yes |
| `'data-only'` | yes | no (client renders, data already hydrated) |
| `false` | no | no |

- Prefer `'data-only'` over `false` for a route that only needs browser state to *render* (localStorage, window size): its data still starts on the server. Pair it with a `pendingComponent` (`pendingMinMs: 0`) for the client render.
- **Hydration does not re-run `beforeLoad`.** If `beforeLoad` decides something from browser-only state (a saved view in localStorage), that route must be `ssr: false` for the URLs that need it; a function lets URLs that carry the state themselves keep SSR:
  ```ts
  ssr: ({ search }) => (search.status === 'success' && search.value.view ? undefined : false),
  ```
- `useQuery` never runs on the server. What the SSR HTML shows is what loaders (or `useSuspenseQuery`) produced.

## SSR Query Integration

- Create the `QueryClient` inside `getRouter()` so each SSR request gets its own; a module-level client leaks one user's cache into another's HTML.
- Install `setupRouterSsrQueryIntegration({ router, queryClient })`: loader-started queries are dehydrated into the HTML and hydrated on the client, and `defaultPreloadStaleTime: 0` leaves freshness to Query.
- Everything in the server cache is serialized into the page. Remove failed reads before render, never cache secrets in queries a loader starts, and keep below-the-fold reads off the server (`router-data-loading.md`).

## Function Middleware for Cross-Cutting Headers

Attach per-call client context (the live socket id, a trace id) with a global function middleware instead of threading it through every call site. Register global middleware in `src/start.ts`:

```ts
// lib/live/socket-middleware.ts
export const liveSocketMiddleware = createMiddleware({ type: 'function' }).client(({ next }) => {
  const socket = liveSocketId()
  return socket ? next({ headers: { 'x-live-socket': socket } }) : next()
})

// src/start.ts
export const startInstance = createStart(() => ({
  functionMiddleware: [errorReportingMiddleware, liveSocketMiddleware], // error reporting first
  requestMiddleware: [errorReportingRequestMiddleware],
}))
```

Server-side, read and validate the header before trusting it (it is client input).
