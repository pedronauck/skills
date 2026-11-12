---
name: hono
description: Use when building Hono web applications or when the user asks about Hono APIs, routing, middleware, JSX, validation, testing, or streaming. TRIGGER when code imports from 'hono' or 'hono/*', or user mentions Hono. Use Hono CLI to inspect and test the app.
---

# Hono Skill

Build Hono web applications. This skill provides inline API knowledge for AI. Use Hono CLI to inspect and test the app.

## Latest Documentation

For details beyond this inline reference, fetch the latest documentation from https://hono.dev. Get the index of doc pages from `https://hono.dev/llms.txt`, then fetch a page with the `Accept: text/markdown` header to receive it as Markdown:

```bash
curl -H "Accept: text/markdown" https://hono.dev/docs/helpers/cookie
```

## Hono CLI

Verify with [Hono CLI](https://github.com/honojs/cli), not with throwaway scripts or a dev server. It is a dev dependency (projects from `create-hono` already have it), loads the app in-process with `app.request()`, and prints JSON. Install it if missing, then read its help:

<!-- TODO at the 1.0 release: change @hono/cli@next to @hono/cli -->

```bash
npm install -D @hono/cli@next
npx hono --help
```

Follow the note at the top. It explains the JSON output contract and the workflow. `npx hono <command> --help` has examples and notes for each command (`routes`, `request`, `batch`, `snapshot`, `benchmark`, `ssg`, `init`).

<!-- TODO at the Hono v5 GA: change `npm create hono@next` to `npm create hono@latest` here and in hono-jsx -->

Notes:

- `npx hono routes` lists the routes; `npx hono request /path` sends one request — no server needed. If the app is not at the default path (`src/index.ts`), pass the file to every command: `npx hono request / src/app.ts`. Do not pass credentials directly in CLI arguments; use environment variables for sensitive values.
- Cloudflare bindings (KV, D1, R2, vars) reach `c.env` automatically — no server, no flag. In a project with `cloudflare.config.ts` (the `cf` CLI) and a Vite config, `request`, `batch`, and `snapshot` run through the Vite dev server by default, and `c.env` has the local bindings; `request` and `batch` default to Vite as well in a Vite project with no `src/index.*` (an app built by a Vite plugin; `snapshot` still needs the file), and `--runtime vite` selects it explicitly. In a project with a wrangler config, the app runs on Node.js with the real local bindings loaded; for the full Workers runtime there, add `--runtime workerd` (pass no file argument; the entry is `main` in the wrangler config). `--trace`, `--watch`, and a file argument run the app on Node.js, where `c.env` is empty in a `cf` project.
- `routes` and `snapshot` also load apps that import `cloudflare:workers` (Durable Objects); the import is stubbed while the routes are read.
- To add a Hono app to an existing directory, run `npx hono init --template cloudflare-workers` (or `nodejs`, `bun`, `deno`, ...; without `--template` it is detected from the files in the directory), then install the dependencies. It copies the `create-hono` template and never overwrites an existing file. For an empty directory, `npm create hono@next` does the same with prompts.
- For several requests, or a flow that keeps state (POST, then use the returned id), run them in one `hono batch -` call. One JSON object per line; `save` a value and use it as `{{id}}` in later steps. The steps share one app instance. Declare the expected status/body per step with `expect` (body is a deep partial match) and iterate until the summary shows `"failed": 0`:

  ```bash
  npx hono batch - <<'EOF'
  {"method":"POST","path":"/users","body":{"name":"Alice"},"save":{"id":".id"},"expect":{"status":201}}
  {"path":"/users/{{id}}","expect":{"status":200,"body":{"name":"Alice"}}}
  EOF
  ```

- Before changing existing routes, capture the current behavior: `npx hono snapshot` prints it as batch JSONL lines (real responses become the `expect`). Keep the lines, make the change, then rerun them with `npx hono batch -` until `"failed": 0`.
- On a large API, use `npx hono snapshot --status-only` and `npx hono batch - --compact` — same loop, much smaller output. A failed step carries `diff`: fix what it names.

---

## Hono API Reference

### App Constructor

```ts
import { Hono } from 'hono'

const app = new Hono()

// With TypeScript generics
type AppEnv = {
  Bindings: Env // generated from the bindings config — see "Environment (Cloudflare Workers)"
  Variables: { user: User }
}
const app = new Hono<AppEnv>()
```

### Routing Methods

```ts
app.get('/path', handler)
app.post('/path', handler)
app.put('/path', handler)
app.delete('/path', handler)
app.patch('/path', handler)
app.options('/path', handler)
app.all('/path', handler) // all HTTP methods
app.on('PURGE', '/path', handler) // custom method
app.on(['PUT', 'DELETE'], '/path', handler) // multiple methods
```

### Routing Patterns

```ts
// Path parameters
app.get('/user/:name', (c) => {
  const name = c.req.param('name')
  return c.json({ name })
})

// Multiple params
app.get('/posts/:id/comments/:commentId', (c) => {
  const { id, commentId } = c.req.param()
})

// Optional parameters
app.get('/api/animal/:type?', (c) => c.text('Animal!'))

// Wildcards
app.get('/wild/*/card', (c) => c.text('Wildcard'))

// Regexp constraints
app.get('/post/:date{[0-9]+}/:title{[a-z]+}', (c) => {
  const { date, title } = c.req.param()
})

// Chained routes
app
  .get('/endpoint', (c) => c.text('GET'))
  .post((c) => c.text('POST'))
  .delete((c) => c.text('DELETE'))
```

### Route Grouping

```ts
// Using route()
const api = new Hono()
api.get('/users', (c) => c.json([]))

const app = new Hono()
app.route('/api', api) // mounts at /api/users

// Using basePath()
const app = new Hono().basePath('/api')
app.get('/users', (c) => c.json([])) // GET /api/users
```

### Error Handling

```ts
app.notFound((c) => c.json({ message: 'Not Found' }, 404))

app.onError((err, c) => {
  console.error(err)
  return c.json({ message: 'Internal Server Error' }, 500)
})
```

---

## Context (c)

### Response Methods

```ts
c.text('Hello') // text/plain
c.json({ message: 'Hello' }) // application/json
c.html('<h1>Hello</h1>') // text/html
c.redirect('/new-path') // 302 redirect
c.redirect('/new-path', 301) // 301 redirect
c.body('raw body', 200, headers) // raw response
c.notFound() // 404 response
```

### Headers & Status

```ts
c.status(201)
c.header('X-Custom', 'value')
c.header('Cache-Control', 'no-store')
```

### Variables (request-scoped data)

```ts
// In middleware
c.set('user', { id: 1, name: 'Alice' })

// In handler
const user = c.get('user')
// or
const user = c.var.user
```

### Environment (Cloudflare Workers)

Never write the `Bindings` type by hand: generate it, and rerun after every change to the bindings. Which tool a project uses is visible from its files.

**`cf` CLI projects** (`cloudflare.config.ts`; this is what `create-hono` generates for `cloudflare-workers` now): bindings are declared in `cloudflare.config.ts` with the `bindings` helpers from `cf/config`. Local bindings need no IDs; do not create Cloudflare resources (KV, D1, R2) or set IDs unless the user asks. Then run `npm run typecheck` (= `cf workers types && tsc`; it writes `.cloudflare/types`) and use the generated `Env`:

```ts
// cloudflare.config.ts
import { bindings, defineConfig } from 'cf/config'
import * as entrypoint from './src/index.ts' with { type: 'cf-worker' }

export default defineConfig({
  worker: {
    name: 'my-app',
    compatibilityDate: '2026-10-06',
    entrypoint,
    env: {
      MY_KV: bindings.kv(),
      MY_VAR: bindings.text('my-variable'),
    },
  },
})
```

```ts
const app = new Hono<{ Bindings: Env }>()
```

Scripts are `cf dev`, `cf build`, and `cf deploy`. Such a project has no wrangler config; do not add one, and do not run `cf init` in a Hono project (its autoconfig stops on Hono).

**wrangler projects** (`wrangler.jsonc` or `wrangler.toml`): bindings are in the wrangler config. `npm run cf-typegen` (= `wrangler types --env-interface CloudflareBindings`) writes `worker-configuration.d.ts`, which declares `CloudflareBindings` together with the Workers runtime types. If there is no `cf-typegen` script, run `npx wrangler types` and use the interface it declares instead (`Env`, also available as `Cloudflare.Env`). `@cloudflare/workers-types` is superseded by either: do not install it.

```ts
const app = new Hono<{ Bindings: CloudflareBindings }>()

app.get('/', async (c) => {
  const value = await c.env.MY_KV.get('key')
  const db = c.env.MY_DB
  c.executionCtx.waitUntil(promise)
})
```

### Renderer

```ts
app.use(async (c, next) => {
  c.setRenderer((content) =>
    c.html(
      <html><body>{content}</body></html>
    )
  )
  await next()
})

app.get('/', (c) => c.render(<h1>Hello</h1>))
```

---

## HonoRequest (c.req)

```ts
c.req.param('id') // path parameter
c.req.param() // all path params as object
c.req.query('page') // query string parameter
c.req.query() // all query params; values are string | undefined
c.req.queries('tags') // multiple values: ?tags=A&tags=B → ['A', 'B']
c.req.header('Authorization') // request header
c.req.header() // all headers (keys are lowercase)

// Body parsing
await c.req.json<{ title: string }>() // parse JSON body (unknown without the type argument)
await c.req.text() // parse text body
await c.req.formData() // parse as FormData
await c.req.parseBody() // parse multipart/form-data or urlencoded
await c.req.arrayBuffer() // parse as ArrayBuffer
await c.req.blob() // parse as Blob

// Validated data (used with validator middleware)
c.req.valid('json')
c.req.valid('query')
c.req.valid('form')
c.req.valid('param')

// Properties
c.req.url // full URL string
c.req.path // pathname
c.req.method // HTTP method
c.req.raw // underlying Request object
```

---

## Middleware

### Using Built-in Middleware

```ts
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { basicAuth } from 'hono/basic-auth'
import { prettyJSON } from 'hono/pretty-json'
import { secureHeaders } from 'hono/secure-headers'
import { etag } from 'hono/etag'
import { compress } from 'hono/compress'
import { poweredBy } from 'hono/powered-by'
import { timing } from 'hono/timing'
import { cache } from 'hono/cache'
import { bearerAuth } from 'hono/bearer-auth'
import { jwt } from 'hono/jwt'
import { jwk } from 'hono/jwk'
import { csrf } from 'hono/csrf'
import { ipRestriction } from 'hono/ip-restriction'
import { bodyLimit } from 'hono/body-limit'
import { timeout } from 'hono/timeout'
import { requestId } from 'hono/request-id'
import { methodOverride } from 'hono/method-override'
import { methodNotAllowed } from 'hono/method-not-allowed'
import { languageDetector } from 'hono/language'
import { some, every, except } from 'hono/combine'
import { contextStorage, getContext } from 'hono/context-storage'
import { trailingSlash, trimTrailingSlash } from 'hono/trailing-slash'

// Registration
app.use(logger()) // all routes
app.use('/api/*', cors()) // specific path
app.post('/api/*', basicAuth({ username: 'admin', password: 'secret' }))
```

### Custom Middleware

```ts
// Inline
app.use(async (c, next) => {
  const start = Date.now()
  await next()
  const elapsed = Date.now() - start
  c.res.headers.set('X-Response-Time', `${elapsed}ms`)
})

// Reusable with createMiddleware
import { createMiddleware } from 'hono/factory'

const auth = createMiddleware(async (c, next) => {
  const token = c.req.header('Authorization')
  if (!token) return c.json({ error: 'Unauthorized' }, 401)
  await next()
})

app.use('/api/*', auth)
```

### Middleware Execution Order

Middleware executes in registration order. `await next()` calls the next middleware/handler, and code after `next()` runs on the way back:

```
Request → mw1 before → mw2 before → handler → mw2 after → mw1 after → Response
```

```ts
app.use(async (c, next) => {
  // before handler
  await next()
  // after handler
})
```

---

## Validation

Validation targets: `json`, `form`, `query`, `header`, `param`, `cookie`.

### Zod Validator

```ts
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

const schema = z.object({
  title: z.string().min(1),
  body: z.string()
})

app.post('/posts', zValidator('json', schema), (c) => {
  const data = c.req.valid('json') // fully typed
  return c.json(data, 201)
})
```

### Valibot / Standard Schema Validator

```ts
import { sValidator } from '@hono/standard-validator'
import * as v from 'valibot'

const schema = v.object({ name: v.string(), age: v.number() })

app.post('/users', sValidator('json', schema), (c) => {
  const data = c.req.valid('json')
  return c.json(data, 201)
})
```

---

## JSX

To build UI with it (layouts with `jsxRenderer`, Vite, client-side code), use the `hono-jsx` skill. This section covers the syntax only.

### Setup

In `tsconfig.json`:

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "hono/jsx"
  }
}
```

Or use pragma: `/** @jsxImportSource hono/jsx */`

**Important:** Files using JSX must have a `.tsx` extension. Rename `.ts` to `.tsx` or the compiler will fail.

### Components

```tsx
import type { PropsWithChildren } from 'hono/jsx'

const Layout = (props: PropsWithChildren) => (
  <html>
    <head>
      <title>My App</title>
    </head>
    <body>{props.children}</body>
  </html>
)

const UserCard = ({ name }: { name: string }) => (
  <div class="card">
    <h2>{name}</h2>
  </div>
)

app.get('/', (c) => {
  return c.html(
    <Layout>
      <UserCard name="Alice" />
    </Layout>
  )
})
```

### jsxRenderer Middleware

Use `jsxRenderer` middleware for layouts. For details, see https://hono.dev/docs/middleware/builtin/jsx-renderer

### Async Components

```tsx
const UserList = async () => {
  const users = await fetchUsers()
  return (
    <ul>
      {users.map((u) => (
        <li>{u.name}</li>
      ))}
    </ul>
  )
}
```

### Fragments

```tsx
const Items = () => (
  <>
    <li>Item 1</li>
    <li>Item 2</li>
  </>
)
```

---

## Streaming

```ts
import { stream, streamText, streamSSE } from 'hono/streaming'

// Basic stream
app.get('/stream', (c) => {
  return stream(c, async (stream) => {
    stream.onAbort(() => console.log('Aborted'))
    await stream.write(new Uint8Array([0x48, 0x65]))
    await stream.pipe(readableStream)
  })
})

// Text stream
app.get('/stream-text', (c) => {
  return streamText(c, async (stream) => {
    await stream.writeln('Hello')
    await stream.sleep(1000)
    await stream.write('World')
  })
})

// Server-Sent Events
app.get('/sse', (c) => {
  return streamSSE(c, async (stream) => {
    let id = 0
    while (true) {
      await stream.writeSSE({
        data: JSON.stringify({ time: new Date().toISOString() }),
        event: 'time-update',
        id: String(id++)
      })
      await stream.sleep(1000)
    }
  })
})
```

---

## Testing with app.request()

Test endpoints without starting an HTTP server:

```ts
// GET
const res = await app.request('/posts')
expect(res.status).toBe(200)
expect(await res.json()).toEqual({ posts: [] })

// POST with JSON
const res = await app.request('/posts', {
  method: 'POST',
  body: JSON.stringify({ title: 'Hello' }),
  headers: { 'Content-Type': 'application/json' }
})

// POST with FormData
const formData = new FormData()
formData.append('name', 'Alice')
const res = await app.request('/users', { method: 'POST', body: formData })

// With mock env (Cloudflare Workers bindings)
const res = await app.request('/api/data', {}, { KV: mockKV, DATABASE: mockDB })

// Using Request object
const req = new Request('http://localhost/api', { method: 'DELETE' })
const res = await app.request(req)
```

---

## Hono Client (RPC)

Type-safe API client using shared types between server and client.

**IMPORTANT: Routes MUST be chained for type inference to work. Without chaining, the client cannot infer route types.**

```ts
// Server: routes MUST be chained to preserve types
const route = app
  .post('/posts', zValidator('json', schema), (c) => {
    return c.json({ ok: true }, 201)
  })
  .get('/posts', (c) => {
    return c.json({ posts: [] })
  })
export type AppType = typeof route

// Client: use hc() with the exported type
import { hc } from 'hono/client'
import type { AppType } from './server'

const client = hc<AppType>('http://localhost:8787/')
const res = await client.posts.$post({ json: { title: 'Hello' } })
const data = await res.json() // fully typed
```

Type utilities:

```ts
import type { InferRequestType, InferResponseType } from 'hono/client'

type ReqType = InferRequestType<typeof client.posts.$post>
type ResType = InferResponseType<typeof client.posts.$post, 200>
```

---

## Helpers

Helpers are utility functions imported from `hono/<helper-name>`:

```ts
import { getConnInfo } from 'hono/conninfo'
import { getCookie, setCookie, deleteCookie } from 'hono/cookie'
import { css, Style } from 'hono/css'
import { createFactory } from 'hono/factory'
import { html, raw } from 'hono/html'
import { stream, streamText, streamSSE } from 'hono/streaming'
import { testClient } from 'hono/testing'
import { upgradeWebSocket } from '@hono/cloudflare-workers' // or another @hono/<runtime> adapter package
```

Available helpers: Accepts, Adapter, ConnInfo, Cookie, css, Dev, Factory, html, JWT, Proxy, Route, SSG, Streaming, Testing, WebSocket.

For details, see `https://hono.dev/docs/helpers/<helper-name>` (fetch with `Accept: text/markdown`).

### Factory

Use `createFactory` to define the app's `Env` type (`AppEnv` above) once and share it across app, middleware, and handlers:

```ts
import { createFactory } from 'hono/factory'

const factory = createFactory<AppEnv>()

// Create app (AppEnv is inherited)
const app = factory.createApp()

// Create middleware (AppEnv is inherited, no need to pass generics)
const mw = factory.createMiddleware(async (c, next) => {
  await next()
})

// Create handlers separately (preserves type inference)
const handlers = factory.createHandlers(logger(), (c) => c.json({ message: 'Hello' }))
app.get('/api', ...handlers)
```

---

## Best Practices

- Write handlers inline in route definitions for proper type inference of path params.
- Use `app.route()` to organize large apps by feature, not Rails-style controllers.
- Use `createFactory()` to share Env type across app, middleware, and handlers.
- Use `c.set()`/`c.get()` to pass data between middleware and handlers.
- Chain validators for multiple request parts (param + query + json).
- Export app type for RPC: `export type AppType = typeof routes`
- Use `app.request()` for testing — no server startup needed.

## Adapters

Hono runs on multiple runtimes. The default export works for Cloudflare Workers, Deno, and Bun. For Node.js, use the Node adapter:

```ts
// Cloudflare Workers / Deno / Bun
export default app

// Node.js
import { serve } from '@hono/node-server'
serve(app)
```

Runtime-specific helpers (`serveStatic`, `upgradeWebSocket`, `getConnInfo`, Lambda handlers) live in separate packages since Hono v5: `@hono/cloudflare-workers`, `@hono/bun`, `@hono/deno`, `@hono/aws-lambda`, `@hono/lambda-edge`, `@hono/netlify`, `@hono/vercel`, `@hono/service-worker`. Install the one for the runtime and import from it; `hono/<runtime>` only exists on v4. `hono/adapter` (`env()`, `getRuntimeKey()`) stays in `hono`. Hono v5 is ESM only and needs Node.js 22.12 or later.
