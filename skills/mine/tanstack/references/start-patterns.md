# TanStack Start Patterns

Patterns for TanStack Start (full-stack React framework): server functions, middleware, auth, SSR, deployment. Assumes familiarity with `query-patterns.md` and `router-patterns.md`.

## Contents

- Core Principles
- Server Functions (`createServerFn`)
  - Input validation with Zod
  - Method choice (GET vs POST)
  - Composing server functions
  - Calling from loaders / components
  - Error handling (`notFound`, `redirect`)
- Middleware
  - Request vs function middleware
  - Composing middleware
  - Attaching to a server function
  - Execution order
- Authentication
  - Secure session cookie (HTTP-only, SameSite)
  - Login / logout pattern
  - Route protection (`_authenticated` layout)
  - Cookie settings reference table
- SSR
  - Streaming non-critical content with Suspense
  - Hydration safety (common mismatch causes)
  - Prerender / ISR
  - Selective SSR
- API Routes (external consumers)
- Environment Functions (typed server/client split)
- File Organization (`*.server.ts`, `*.functions.ts`, `*.shared.ts`)
- Deployment Adapters (Vercel, Netlify, Node, Cloudflare, Bun)
- Validation Checklist

## Core Principles

- **Server functions over fetch + handlers.** Use `createServerFn` so input/output types flow end-to-end and the build keeps server code out of the client bundle.
- **Cookies, not localStorage, for auth.** HTTP-only cookies survive XSS; localStorage doesn't.
- **Stream what you can, await what you must.** SSR is fast when only the critical path blocks.

## Server Functions

### `createServerFn` with input validation

```typescript
// lib/posts.functions.ts
import { createServerFn } from '@tanstack/react-start'
import { z } from 'zod'
import { db } from './db.server'

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  published: z.boolean().default(false),
})

export const createPost = createServerFn({ method: 'POST' })
  .validator(createPostSchema)
  .handler(async ({ data }) => {
    // server-only — never reaches the client bundle
    return db.posts.create({ data })
  })
```

Three reasons this beats raw `fetch`:

1. **Type safety end-to-end** — return type is inferred at the call site.
2. **Build-time code splitting** — handler body is replaced with an RPC stub on the client.
3. **Validator-first** — Zod runs before the handler; invalid input is a typed error.

### Method choice

- `GET` (default) for idempotent reads — can be cached and prefetched.
- `POST` for any state mutation. Never use `GET` for actions with side effects.

### Composing server functions

Call one server function from another. The build still tree-shakes correctly:

```typescript
export const getPostWithComments = createServerFn()
  .validator(z.object({ postId: z.string() }))
  .handler(async ({ data }) => {
    const [post, comments] = await Promise.all([
      getPost({ data: { id: data.postId } }),
      getComments({ data: { postId: data.postId } }),
    ])
    return { post, comments }
  })
```

### Calling from loaders and components

```typescript
// from a route loader
loader: ({ params }) => getPost({ data: { id: params.postId } })

// from a component (mutations)
const createPostMutation = useServerFn(createPost)
await createPostMutation({ data: { title, content, published: false } })
```

### Error handling

Throw inside the handler; errors are serialized to the client. Use `redirect()` and `notFound()` for control flow, not generic `Error`:

```typescript
import { notFound, redirect } from '@tanstack/react-router'

export const getPost = createServerFn()
  .validator(z.object({ id: z.string() }))
  .handler(async ({ data }) => {
    const post = await db.posts.findUnique({ where: { id: data.id } })
    if (!post) throw notFound()
    if (post.deleted) throw redirect({ to: '/posts' })
    return post
  })
```

## Middleware

Two flavors:

- **Request middleware** — wraps every server request (routes, SSR, server functions). Use for global concerns.
- **Function middleware** — applied to specific server functions. Use for per-handler concerns like auth on mutations.

### Request middleware

```typescript
// lib/middleware/auth.ts
import { createMiddleware } from '@tanstack/react-start'

export const authMiddleware = createMiddleware().server(async ({ next }) => {
  const session = await getSession()
  return next({
    context: { session, user: session?.user ?? null },
  })
})

// app/start.ts
import { createStart } from '@tanstack/react-start/server'

export default createStart({
  requestMiddleware: [loggingMiddleware, authMiddleware],
})
```

### Composing middleware

`requireAuthMiddleware` depends on `authMiddleware`, so the user is guaranteed by the time it runs:

```typescript
export const requireAuthMiddleware = createMiddleware()
  .middleware([authMiddleware])
  .server(async ({ next, context }) => {
    if (!context.user) throw redirect({ to: '/login' })
    return next({ context: { user: context.user } })
  })
```

### Attaching middleware to a server function

```typescript
export const updateProfile = createServerFn({ method: 'POST' })
  .middleware([requireAuthMiddleware])
  .validator(profileSchema)
  .handler(async ({ data, context }) => {
    // context.user is typed and guaranteed
    return db.users.update({ where: { id: context.user.id }, data })
  })
```

### Execution order

Middleware wraps the chain — first declared, last unwrapped:

```
Request → Logging → Auth → Handler → Auth (after) → Logging (after) → Response
```

## Authentication

### Secure session cookie

Always HTTP-only. localStorage is XSS-bait:

```typescript
// lib/session.server.ts
import { useSession } from '@tanstack/react-start/server'

export function getSession() {
  return useSession({
    password: process.env.SESSION_SECRET!,         // 32+ random chars
    cookie: {
      name: '__session',
      httpOnly: true,                              // not readable by JS
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',                             // CSRF mitigation
      maxAge: 60 * 60 * 24 * 7,                    // 7 days
    },
  })
}
```

Generate the secret with `openssl rand -base64 32`. Rotate on breach.

### Login / logout pattern

```typescript
export const login = createServerFn({ method: 'POST' })
  .validator(z.object({ email: z.string().email(), password: z.string().min(1) }))
  .handler(async ({ data }) => {
    const user = await db.users.findUnique({ where: { email: data.email } })
    if (!user || !(await verifyPassword(data.password, user.passwordHash))) {
      throw new Error('Invalid email or password')
    }
    const session = await getSession()
    await session.update({ userId: user.id, email: user.email })
    throw redirect({ to: '/dashboard' })
  })

export const logout = createServerFn({ method: 'POST' }).handler(async () => {
  const session = await getSession()
  await session.clear()
  throw redirect({ to: '/' })
})
```

Keep the session payload minimal — `userId` plus what you need for every request. Fetch the full user on demand.

### Route protection

`beforeLoad` runs server-side during SSR and client-side on navigation. Pair with a pathless `_authenticated` layout:

```typescript
// routes/_authenticated.tsx
export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ context, location }) => {
    if (!context.user) {
      throw redirect({ to: '/login', search: { redirect: location.href } })
    }
  },
  component: () => <Outlet />,
})
```

| Cookie setting | Value | Why |
|----------------|-------|-----|
| `httpOnly` | `true` | XSS can't read the cookie |
| `secure` | `true` in prod | HTTPS-only |
| `sameSite` | `'lax'` or `'strict'` | CSRF mitigation |
| `maxAge` | App-specific | Bound session lifetime |

## SSR

### Streaming non-critical content

Block only on data needed for the first paint; stream the rest with `Suspense`:

```typescript
export const Route = createFileRoute('/dashboard')({
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(userQueries.profile())     // critical
    queryClient.prefetchQuery(dashboardQueries.stats())          // streamed
    queryClient.prefetchQuery(activityQueries.recent())          // streamed
  },
  component: DashboardPage,
})

function DashboardPage() {
  const { data: user } = useSuspenseQuery(userQueries.profile())
  return (
    <>
      <Header user={user} />
      <Suspense fallback={<StatsSkeleton />}><DashboardStats /></Suspense>
      <Suspense fallback={<ActivitySkeleton />}><RecentActivity /></Suspense>
    </>
  )
}
```

Wrap each `Suspense` in an `ErrorBoundary` so one slow/failed section doesn't crash the page.

### Hydration safety

Hydration mismatches happen when server-rendered HTML disagrees with the first client render. Common causes:

- `new Date()`, `Math.random()`, or `window` checks at render time.
- Timezone-dependent rendering (`toLocaleString` without explicit `Intl` options).
- Stored UI state (`localStorage`, `matchMedia`) read during render.

Fix by deferring to `useEffect` or rendering a stable placeholder until mount:

```typescript
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
return mounted ? <ClientOnlyThing /> : <Skeleton />
```

For values that must come from the server (current time, feature flags), pass them through the loader.

### Prerender / ISR

Static-ish pages should prerender at build time. Configure on a route:

```typescript
export const Route = createFileRoute('/blog/$slug')({
  ssr: 'prerender',  // build-time static
  loader: ({ params }) => getPost({ data: { slug: params.slug } }),
})
```

For incremental revalidation, combine prerender with a `revalidate` interval at the adapter level (Vercel, Netlify).

### Selective SSR

Per-route SSR mode:

- `'data-only'` — render shell on server, hydrate data; cheaper SSR.
- `false` — pure CSR for this route (admin tooling, dashboards with heavy client state).

## API Routes

Use `createAPIFileRoute` for endpoints meant for external consumers (webhooks, OAuth callbacks, mobile clients). Server functions are RPC-shaped; API routes are RESTful:

```typescript
// routes/api/webhook.ts
import { createAPIFileRoute } from '@tanstack/react-start/api'

export const APIRoute = createAPIFileRoute('/api/webhook')({
  POST: async ({ request }) => {
    const signature = request.headers.get('x-signature')
    if (!verifySignature(signature, await request.text())) {
      return new Response('Unauthorized', { status: 401 })
    }
    return Response.json({ ok: true })
  },
})
```

Rule of thumb: prefer server functions for your own UI; reach for API routes only when an external system dictates the HTTP shape.

## Environment Functions

`createEnv` (or equivalent) guards env vars at boot and exposes typed `env` everywhere:

```typescript
// lib/env.ts
import { createEnv } from '@t3-oss/env-core'
import { z } from 'zod'

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    SESSION_SECRET: z.string().min(32),
  },
  clientPrefix: 'PUBLIC_',
  client: {
    PUBLIC_APP_URL: z.string().url(),
  },
  runtimeEnv: process.env,
})
```

Server keys must never appear in the client bundle — the typed split makes that a compile-time guarantee instead of a code-review chore.

## File Organization

- `*.server.ts` / `*.server.tsx` — server-only; importing from a client file is a build error.
- `*.functions.ts` — server functions (`createServerFn`). Safe to import anywhere; client gets RPC stubs.
- `*.shared.ts` — pure logic and Zod schemas shared by both. No I/O, no env access.

Validation schemas typically live in `*.shared.ts` so the form and the server function validate against the same source.

## Deployment Adapters

`@tanstack/react-start` ships adapters that compile the app for the target platform. Pick at build time:

| Adapter | Target | Notes |
|---------|--------|-------|
| `vercel` | Vercel | First-class streaming + ISR |
| `netlify` | Netlify Functions | Edge-compatible builds available |
| `node` | Custom Node server | Long-running, self-hosted |
| `cloudflare-workers` | CF Workers | Edge runtime — no Node APIs |
| `bun` | Bun runtime | Fast cold start |

Avoid platform-specific APIs (`fs`, native modules) in code that the edge adapter must run. Gate them behind `.server.ts` files plus runtime checks if needed.

## Validation Checklist

Before finishing a task involving TanStack Start:

- [ ] Server logic lives in `createServerFn` with a Zod validator, not raw `fetch` + API routes
- [ ] `method: 'POST'` is used for any mutation; `GET` only for idempotent reads
- [ ] Auth uses HTTP-only cookies with `secure` in prod and `sameSite: 'lax'`/`'strict'`
- [ ] Session payload holds only IDs; full user is fetched per request
- [ ] Protected routes use `_authenticated` pathless layout + `beforeLoad` redirect
- [ ] Cross-cutting concerns (logging, auth) are middleware, not duplicated in handlers
- [ ] Loaders await only critical data; non-critical is `prefetchQuery` + `Suspense`
- [ ] `Suspense` boundaries are paired with `ErrorBoundary`
- [ ] Env vars validated at boot with typed `server`/`client` split
- [ ] Server-only modules end in `.server.ts` to prevent client leakage
- [ ] Schemas live in `*.shared.ts` and are reused by form + server fn
- [ ] Deployment adapter matches the target platform
