# TanStack Router Patterns and Best Practices

This document contains comprehensive patterns and best practices for using TanStack Router in this project.

## Contents

- Core Principles
- Router Setup
  - Register the router type (CRITICAL `declare module`)
  - Configure router defaults (`defaultPreload`, `scrollRestoration`, etc.)
  - Use `from` for type narrowing
- File-Based Routing Structure
  - File naming conventions
  - Pathless layouts
- Common Tasks
  - Basic route, dynamic params, search params with Zod
  - Data loading with loaders
  - Parallel loading (avoid waterfalls)
  - Deferred (streaming) data
  - Authentication layout
  - Type-safe navigation
  - Error handling, code splitting, pending component
- Advanced Patterns
  - Route context, search updates
  - Route masks (modal-on-route, pretty URLs)
  - Custom search-param serializer
  - Global not-found (`notFound()`)
  - Prefetching
- Integration with TanStack Query
- Validation Checklist
- Common Mistakes to Avoid

## Core Principles

- **Type-Safe Routing**: Embrace type-safe routing as the primary benefit.
- **File-Based Routes**: Use file-based routing for scalability.
- **Generated Route Tree**: Leverage the generated route tree for type safety.
- **Layouts and Nesting**: Think in terms of layouts and nested routes.

## Router Setup

### Register the router type (CRITICAL)

Without this `declare module`, `useNavigate`, `Link`, `useParams`, and `useSearch` lose route inference and accept any string. This is the single most impactful step for type safety:

```typescript
// src/router.tsx
import { createRouter } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
```

### Configure router defaults

`createRouter` accepts global options that prevent boilerplate at the route level:

```typescript
const router = createRouter({
  routeTree,
  context: { queryClient, user: null },

  // Preloading
  defaultPreload: 'intent',           // preload on hover/focus
  defaultPreloadStaleTime: 0,         // delegate freshness to TanStack Query

  // Global error / 404 handling
  defaultErrorComponent: DefaultCatchBoundary,
  defaultNotFoundComponent: DefaultNotFound,

  // UX
  scrollRestoration: true,            // restore scroll on back/forward
  defaultPendingComponent: PendingBar,
  defaultPendingMs: 1000,             // delay before showing pending UI
  defaultPendingMinMs: 200,           // min time pending UI is shown

  // Performance
  defaultStructuralSharing: true,     // re-render less from loader data
})
```

Key options:

| Option | When to use |
|--------|-------------|
| `defaultPreload: 'intent'` | Always — almost free win on hover/focus |
| `defaultPreloadStaleTime: 0` | When using TanStack Query; let Query own caching |
| `scrollRestoration` | Almost always — improves back/forward UX |
| `defaultErrorComponent` | Replace the built-in white-screen fallback |
| `defaultNotFoundComponent` | Required for global 404 |

Routes can override any default (`errorComponent: AdminErrorBoundary`, `preload: false`, etc.).

### Use `from` for type narrowing

Hooks accept a `from` parameter that narrows types to that specific route:

```typescript
const { postId } = useParams({ from: '/posts/$postId' })   // postId: string
const search    = useSearch({ from: '/posts' })            // typed search shape
const data      = useLoaderData({ from: '/posts/$postId' })// typed loader return
```

Without `from`, types collapse to `unknown` or the union of all possibilities. Always use `from` outside of `Route.useX()` (which is already scoped).

## File-Based Routing Structure

```
src/routes/
├── __root.tsx          # Root layout with providers
├── _authenticated.tsx  # Auth layout wrapper
├── index.tsx          # Home page (/)
├── about.tsx          # /about
├── posts/
│   ├── index.tsx      # /posts
│   └── $postId.tsx    # /posts/:postId (typed params)
└── settings/
    ├── _layout.tsx    # Settings layout
    ├── index.tsx      # /settings
    └── profile.tsx    # /settings/profile
```

### File Naming Conventions

- `index.tsx` - Index route for a directory
- `$paramName.tsx` - Dynamic route parameter
- `_layoutName.tsx` - Pathless layout route (underscore prefix — does NOT add a path segment)
- `_authenticated.tsx` - Protected route layout
- `__root.tsx` - Root layout (double underscore)
- `route.lazy.tsx` - Lazy-loaded route component
- `(group)/` - Route group folder for organization without a path segment

### Pathless layouts

A file prefixed with `_` (e.g. `_authenticated.tsx`) creates a layout without contributing to the URL. Use it to share `beforeLoad`, context, or UI across siblings:

```
routes/
├── _authenticated.tsx        # auth check, no URL segment
├── _authenticated/
│   ├── dashboard.tsx         # URL: /dashboard
│   └── settings.tsx          # URL: /settings
```

This is different from a regular layout like `settings.tsx` + `settings/profile.tsx`, which contributes `/settings` to the URL.

## Common Tasks

### Creating a Basic Route

Use `createFileRoute` with the route path matching the file location.

```typescript
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/posts/')({
  component: PostsList,
})

function PostsList() {
  return <div>Posts List</div>
}
```

### Route with Typed Parameters

Use `$paramName` in the file path for dynamic segments and access them via `Route.useParams()`.

```typescript
// routes/posts/$postId.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/posts/$postId')({
  component: PostDetail,
})

function PostDetail() {
  const { postId } = Route.useParams()
  return <div>Post: {postId}</div>
}
```

### Search Params with Zod Validation

Use `validateSearch` with a Zod schema for type-safe URL search parameters.

```typescript
import { createFileRoute } from '@tanstack/react-router'
import { z } from 'zod'

const searchSchema = z.object({
  page: z.number().min(1).catch(1),
  search: z.string().optional(),
  sort: z.enum(['asc', 'desc']).catch('asc'),
})

export const Route = createFileRoute('/posts/')({
  validateSearch: searchSchema,
  component: PostsList,
})

function PostsList() {
  const { page, search, sort } = Route.useSearch()
  // Use search params...
}
```

### Data Loading with Loaders

Use the `loader` option for server-side data fetching and `loaderDeps` to control re-fetching.

```typescript
export const Route = createFileRoute('/posts/')({
  validateSearch: z.object({
    page: z.number().min(1).catch(1),
  }),
  loaderDeps: ({ search }) => ({ page: search.page }),
  loader: async ({ deps }) => {
    return await fetchPosts(deps.page)
  },
  component: PostsList,
})

function PostsList() {
  const posts = Route.useLoaderData()
  // Render posts...
}
```

### Parallel loading — avoid waterfalls

Nested route loaders run **in parallel** by default. Inside a single loader, fan out with `Promise.all`:

```typescript
// GOOD — fans out
beforeLoad: async () => {
  const [user, config] = await Promise.all([fetchUser(), fetchAppConfig()])
  return { user, config }
}

loader: async ({ context }) => {
  const [stats, activity] = await Promise.all([
    queryClient.ensureQueryData(statsQueries.for(context.user.id)),
    queryClient.ensureQueryData(activityQueries.for(context.user.id)),
  ])
  return { stats, activity }
}

// BAD — serial waterfall
beforeLoad: async () => {
  const user = await fetchUser()          // 200ms
  const perms = await fetchPermissions()  // +200ms
  return { user, perms }                  // 400ms total
}
```

### Deferred (streaming) data

Stream non-critical data without blocking the route render. Critical data is awaited; secondary data starts but is consumed via `useQuery` in the component:

```typescript
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, context: { queryClient } }) => {
    // critical — awaited
    const post = await queryClient.ensureQueryData(postQueries.detail(params.postId))
    // non-critical — kicked off, not awaited
    queryClient.prefetchQuery(commentQueries.forPost(params.postId))
    return { post }
  },
})

function PostPage() {
  const { postId } = Route.useParams()
  const { data: comments, isLoading } = useQuery(commentQueries.forPost(postId))
  return isLoading ? <CommentsSkeleton /> : <Comments data={comments} />
}
```

### Authentication Layout Route

Use layout routes with `beforeLoad` for authentication checks.

```typescript
// routes/_authenticated.tsx
import { createFileRoute, redirect, Outlet } from '@tanstack/react-router'

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ location }) => {
    const isAuthenticated = checkAuth()
    if (!isAuthenticated) {
      throw redirect({
        to: '/login',
        search: { redirect: location.href },
      })
    }
  },
  component: () => <Outlet />,
})
```

### Type-Safe Navigation

Use `Link` component for declarative navigation and `useNavigate` for programmatic navigation.

```typescript
import { Link, useNavigate } from '@tanstack/react-router'

function Navigation() {
  const navigate = useNavigate()

  return (
    <>
      <Link
        to="/posts/$postId"
        params={{ postId: '123' }}
        search={{ tab: 'comments' }}
      >
        View Post
      </Link>

      <button onClick={() => navigate({ to: '/posts', search: { page: 1 } })}>
        Go to Posts
      </button>
    </>
  )
}
```

### Error Handling

Use `errorComponent` and `notFoundComponent` for route-level error boundaries.

```typescript
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.postId)
    if (!post) throw new Error('Post not found')
    return post
  },
  errorComponent: ({ error, retry }) => (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={retry}>Retry</button>
    </div>
  ),
  notFoundComponent: () => <div>Post not found</div>,
})
```

### Code Splitting with Lazy Routes

Two complementary mechanisms:

**1. `.lazy.tsx` files** — split the non-critical part (component, errorComponent) while keeping critical config (path, loader, validateSearch) in the main file:

```typescript
// routes/admin.tsx — critical, eagerly loaded
export const Route = createFileRoute('/admin')({
  validateSearch: z.object({ tab: z.string().optional() }),
  loader: ({ context }) => context.queryClient.ensureQueryData(adminQueries.summary()),
})

// routes/admin.lazy.tsx — lazy, only the component
import { createLazyFileRoute } from '@tanstack/react-router'

export const Route = createLazyFileRoute('/admin')({
  component: AdminDashboard,
})
```

**2. `autoCodeSplitting: true`** in the Vite plugin — splits component/pendingComponent/errorComponent automatically without manual `.lazy.tsx` files:

```typescript
// vite.config.ts
import { tanstackRouter } from '@tanstack/router-plugin/vite'

export default defineConfig({
  plugins: [tanstackRouter({ autoCodeSplitting: true })],
})
```

Prefer auto-splitting in new projects. Use `.lazy.tsx` only when you need fine control over which parts are split.

### Pending Component

Show loading state while data is being fetched.

```typescript
export const Route = createFileRoute('/posts/')({
  loader: async () => {
    return await fetchPosts()
  },
  pendingComponent: () => <div>Loading...</div>,
  component: PostsList,
})
```

## Advanced Patterns

### Context and Route Context

Pass context data through the route tree.

```typescript
// __root.tsx
import { createRootRouteWithContext } from '@tanstack/react-router'
import type { QueryClient } from '@tanstack/react-query'

interface RouterContext {
  queryClient: QueryClient
  auth: AuthState
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
})
```

### Using Route Context in Child Routes

```typescript
export const Route = createFileRoute('/posts/')({
  beforeLoad: ({ context }) => {
    // Access context.queryClient, context.auth, etc.
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: '/login' })
    }
  },
  loader: ({ context }) => {
    return context.queryClient.ensureQueryData({
      queryKey: ['posts'],
      queryFn: fetchPosts,
    })
  },
})
```

### Updating Search Params

Use `navigate` or `Link` to update search params while preserving current state.

```typescript
function PostsFilter() {
  const navigate = useNavigate()
  const { page, sort } = Route.useSearch()

  const handleSortChange = (newSort: 'asc' | 'desc') => {
    navigate({
      search: (prev) => ({ ...prev, sort: newSort }),
    })
  }

  return (
    <Link
      to="."
      search={(prev) => ({ ...prev, page: page + 1 })}
    >
      Next Page
    </Link>
  )
}
```

### Route Masks — when and why

Masks let the rendered route differ from the URL the user sees. Two main use cases:

1. **Modal-on-route**: open a detail view as a modal overlay on a list page. The list URL stays in history so back-button closes the modal.
2. **Pretty URLs over implementation details**: hide query params from the user-facing URL.

```typescript
// Open product detail as a modal overlaid on /products
navigate({
  to: '/products/$productId',
  params: { productId: '123' },
  mask: { to: '/products', search: { modal: '123' } },
})
// User sees /products?modal=123 but renders /products/$productId
```

Masks are bookmark-safe: visiting the masked URL directly loads the real route too, if you reverse-mask via `routeMasks` on the router.

### Custom search-param serializer

The default JSON serializer produces ugly URLs (`?filters=%7B...%7D`). Override globally on the router when URLs need to be shareable or human-readable:

```typescript
import qs from 'qs'

const router = createRouter({
  routeTree,
  search: {
    serialize: (search) => qs.stringify(search, { encodeValuesOnly: true, arrayFormat: 'brackets' }),
    parse: (str) => qs.parse(str, { ignoreQueryPrefix: true }),
  },
})
// /products?filters[category]=electronics&filters[price][min]=100
```

`validateSearch` (Zod) still runs after parsing. Watch out for URL length limits (~2000 chars) and SEO — base64-encoded params are opaque to crawlers.

### Global not-found

`notFoundComponent` on a route handles 404s for that subtree. Set a router-wide fallback in `createRouter`:

```typescript
const router = createRouter({
  routeTree,
  defaultNotFoundComponent: () => (
    <div>
      <h1>404</h1>
      <Link to="/">Go home</Link>
    </div>
  ),
})
```

Throw `notFound()` from a loader to trigger it without throwing a generic error:

```typescript
import { notFound } from '@tanstack/react-router'

loader: async ({ params }) => {
  const post = await fetchPost(params.postId)
  if (!post) throw notFound()
  return post
}
```

### Prefetching Routes

Preload route data for faster navigation.

```typescript
import { usePrefetch } from '@tanstack/react-router'

function PostLink({ postId }: { postId: string }) {
  const prefetch = usePrefetch()

  return (
    <Link
      to="/posts/$postId"
      params={{ postId }}
      onMouseEnter={() => prefetch({ to: '/posts/$postId', params: { postId } })}
    >
      View Post
    </Link>
  )
}
```

## Integration with TanStack Query

For optimal data fetching, integrate TanStack Router with TanStack Query:

```typescript
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params, context }) => {
    // Use queryClient from context
    await context.queryClient.ensureQueryData({
      queryKey: ['post', params.postId],
      queryFn: () => fetchPost(params.postId),
    })
  },
  component: PostDetail,
})

function PostDetail() {
  const { postId } = Route.useParams()
  const { data: post } = useQuery({
    queryKey: ['post', postId],
    queryFn: () => fetchPost(postId),
  })
  // Render post...
}
```

## Validation Checklist

Before finishing a task involving TanStack Router:

- [ ] Router type registered via `declare module '@tanstack/react-router'`
- [ ] Router defaults configured: `defaultPreload: 'intent'`, `scrollRestoration`, global error + 404 components
- [ ] `defaultPreloadStaleTime: 0` when TanStack Query owns caching
- [ ] Route path in `createFileRoute` matches file location
- [ ] Search params use Zod validation with `.catch()` defaults
- [ ] Loader dependencies declared in `loaderDeps`
- [ ] Loaders fan out with `Promise.all`; non-critical data is streamed via `prefetchQuery`
- [ ] Auth routes use `beforeLoad` with proper redirects and pathless `_authenticated` layouts
- [ ] `notFound()` thrown from loaders instead of generic errors
- [ ] Hooks outside `Route.useX()` pass `from` for type narrowing
- [ ] Code splitting via `autoCodeSplitting` or `.lazy.tsx`
- [ ] Route context is typed at the root with `createRootRouteWithContext`
- [ ] Run type checks (`pnpm run typecheck`) and tests (`pnpm run test`)

## Common Mistakes to Avoid

1. **Incorrect route path**: The path in `createFileRoute` must match the file location exactly.
2. **Missing `.catch()` on search params**: Always provide defaults with `.catch()` for optional params.
3. **Not using `loaderDeps`**: If your loader depends on search params, specify them in `loaderDeps`.
4. **Throwing redirects incorrectly**: Use `throw redirect({...})` not `return redirect({...})`.
5. **Forgetting to type route context**: Always type your root route context for type safety.
