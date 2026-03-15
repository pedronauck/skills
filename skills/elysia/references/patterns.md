# Elysia Framework Patterns & Best Practices

This document provides comprehensive patterns, guidelines, and best practices for developing with the Elysia framework in this project.

## Core Philosophy

- **Pattern-agnostic but feature-based** structure recommended
- **"1 Elysia instance = 1 controller"** principle
- **Strong typing** with TypeBox for runtime validation
- **Centralized error handling** and consistent responses
- **Production-ready** deployment strategies

## Project Structure

### Feature-Based Organization

Use a feature-based structure for organizing Elysia modules:

```
src/
  modules/
    <feature>/
      index.ts      # Elysia controller (routes, guards, cookies)
      service.ts    # Business logic (no HTTP context)
      model.ts      # Schemas & types via `t` (TypeBox)
  plugins/
    error.ts        # Centralized error handling
    logging.ts      # Request/response logging
    openapi.ts      # OpenAPI/Swagger configuration
    auth.ts         # Authentication plugin
  utils/
    ...             # Shared utilities
  app.ts            # Main application setup
  server.ts         # Server entry point
```

### Feature Scaffolding Pattern

When creating a new feature, generate the following files:

1. **`model.ts`** - Schemas and types:
```typescript
import { t } from 'elysia'

export const createUserBody = t.Object({
  email: t.String({ format: 'email' }),
  name: t.String({ minLength: 1 }),
  password: t.String({ minLength: 8 })
})

export type CreateUserBody = typeof createUserBody.static

export const userResponse = t.Object({
  id: t.String(),
  email: t.String(),
  name: t.String(),
  createdAt: t.String()
})

export type UserResponse = typeof userResponse.static
```

2. **`service.ts`** - Business logic:
```typescript
import type { CreateUserBody, UserResponse } from './model'

export async function createUser(data: CreateUserBody): Promise<UserResponse> {
  // Business logic here - no HTTP context
  return {
    id: crypto.randomUUID(),
    email: data.email,
    name: data.name,
    createdAt: new Date().toISOString()
  }
}
```

3. **`index.ts`** - Elysia controller:
```typescript
import { Elysia } from 'elysia'
import { createUserBody, userResponse } from './model'
import { createUser } from './service'

export const usersModule = new Elysia({ prefix: '/users' })
  .post('/', async ({ body }) => createUser(body), {
    body: createUserBody,
    response: { 200: userResponse }
  })
```

## Routing & Controllers

### Essential Patterns

- **App as controller**: Treat each `new Elysia({ prefix })` instance as the controller for that feature
- **Method chaining**: Prefer fluent chaining for routes, guards, and plugins
- **Context hygiene**: Pass only relevant fields from request context to service functions

### Route Definition Examples

```typescript
import { Elysia, t } from 'elysia'

const app = new Elysia({ prefix: '/api' })
  // GET with query parameters
  .get('/items', ({ query }) => getItems(query), {
    query: t.Object({
      page: t.Optional(t.Number({ default: 1 })),
      limit: t.Optional(t.Number({ default: 10 }))
    }),
    response: { 200: itemsListResponse }
  })

  // POST with body validation
  .post('/items', ({ body }) => createItem(body), {
    body: createItemBody,
    response: { 201: itemResponse }
  })

  // PUT with path parameters
  .put('/items/:id', ({ params, body }) => updateItem(params.id, body), {
    params: t.Object({ id: t.String() }),
    body: updateItemBody,
    response: { 200: itemResponse }
  })

  // DELETE with path parameters
  .delete('/items/:id', ({ params }) => deleteItem(params.id), {
    params: t.Object({ id: t.String() }),
    response: { 204: t.Void() }
  })
```

### Guards for Shared Validation

```typescript
const protectedRoutes = new Elysia()
  .guard({
    headers: t.Object({
      authorization: t.String()
    })
  })
  .get('/profile', ({ headers }) => getProfile(headers.authorization))
  .get('/settings', ({ headers }) => getSettings(headers.authorization))
```

## Validation & Schemas

### Schema Definition Best Practices

```typescript
import { t } from 'elysia'

// Basic types
const stringField = t.String({ minLength: 1, maxLength: 255 })
const emailField = t.String({ format: 'email' })
const numberField = t.Number({ minimum: 0 })
const booleanField = t.Boolean({ default: false })

// Complex types
const addressSchema = t.Object({
  street: t.String(),
  city: t.String(),
  country: t.String(),
  zipCode: t.Optional(t.String())
})

// Arrays
const tagsSchema = t.Array(t.String(), { minItems: 1, maxItems: 10 })

// Unions and Literals
const statusSchema = t.Union([
  t.Literal('pending'),
  t.Literal('active'),
  t.Literal('completed')
])

// Nullable fields
const nullableField = t.Union([t.String(), t.Null()])
```

### File Validation

```typescript
import { t } from 'elysia'

const fileUploadBody = t.Object({
  file: t.File({
    type: ['image/png', 'image/jpeg'],
    maxSize: 5 * 1024 * 1024 // 5MB
  }),
  description: t.Optional(t.String())
})
```

### Response Schema Guidelines

Always define response schemas for proper typing and OpenAPI generation:

```typescript
const successResponse = t.Object({
  ok: t.Literal(true),
  data: userResponse
})

const errorResponse = t.Object({
  ok: t.Literal(false),
  error: t.Object({
    code: t.String(),
    message: t.String(),
    details: t.Optional(t.Any())
  })
})

// Use in route
.post('/users', handler, {
  body: createUserBody,
  response: {
    200: successResponse,
    400: errorResponse,
    500: errorResponse
  }
})
```

## Error Handling

### Centralized Error Plugin

Create `src/plugins/error.ts`:

```typescript
import { Elysia, status } from 'elysia'

interface ErrorShape {
  ok: false
  error: {
    code: string
    message: string
    details?: unknown
  }
}

export const errorPlugin = new Elysia({ name: 'error-handler' })
  .onError(({ code, error, path, request }) => {
    const requestId = request.headers.get('x-request-id') || crypto.randomUUID()

    // Log error (don't expose in production)
    console.error(`[${requestId}] Error at ${path}:`, error)

    const response: ErrorShape = {
      ok: false,
      error: {
        code: code,
        message: error.message,
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
      }
    }

    switch (code) {
      case 'VALIDATION':
        return status(400, response)
      case 'NOT_FOUND':
        return status(404, response)
      case 'INTERNAL_SERVER_ERROR':
        return status(500, response)
      default:
        return status(500, response)
    }
  })
```

### Throwing Errors

```typescript
import { status } from 'elysia'

// Use `throw status()` for errors (caught by onError)
.get('/items/:id', async ({ params }) => {
  const item = await findItem(params.id)
  if (!item) {
    throw status(404, { message: 'Item not found' })
  }
  return item
})
```

**Important**: Use `throw status(...)` not `return status(...)` for errors to be caught by `onError`.

## Authentication

### JWT Auth Plugin

Create `src/plugins/auth.ts`:

```typescript
import { Elysia, t } from 'elysia'
import { jwt } from '@elysiajs/jwt'

export const authPlugin = new Elysia({ name: 'auth' })
  .use(jwt({
    name: 'jwt',
    secret: process.env.JWT_SECRET!
  }))
  .derive(async ({ jwt, headers }) => {
    const token = headers.authorization?.replace('Bearer ', '')
    if (!token) return { user: null }

    const payload = await jwt.verify(token)
    return { user: payload }
  })
  .macro({
    requireAuth: (enabled: boolean) => ({
      beforeHandle: ({ user }) => {
        if (enabled && !user) {
          throw new Error('Unauthorized')
        }
      }
    })
  })
```

### Protected Routes

```typescript
import { authPlugin } from '../plugins/auth'

const protectedModule = new Elysia()
  .use(authPlugin)
  .guard({ requireAuth: true })
  .get('/profile', ({ user }) => ({ user }))
```

## OpenAPI Integration

### Setup

```typescript
import { Elysia } from 'elysia'
import { swagger } from '@elysiajs/swagger'

export const openapiPlugin = new Elysia({ name: 'openapi' })
  .use(swagger({
    documentation: {
      info: {
        title: 'API Documentation',
        version: '1.0.0'
      },
      tags: [
        { name: 'users', description: 'User management' },
        { name: 'items', description: 'Item operations' }
      ]
    },
    path: '/docs'
  }))
```

### Route Documentation

```typescript
.post('/users', handler, {
  body: createUserBody,
  response: { 200: userResponse },
  detail: {
    tags: ['users'],
    summary: 'Create a new user',
    description: 'Creates a new user account with the provided information'
  }
})
```

## Testing

### Test Setup with Vitest

```typescript
import { describe, it, expect } from 'vitest'
import { app } from '../src/app'

describe('Users API', () => {
  it('should create a user', async () => {
    const response = await app.handle(
      new Request('http://localhost/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          name: 'Test User',
          password: 'password123'
        })
      })
    )

    expect(response.status).toBe(200)
    const body = await response.json()
    expect(body.email).toBe('test@example.com')
  })

  it('should return 400 for invalid body', async () => {
    const response = await app.handle(
      new Request('http://localhost/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'invalid' })
      })
    )

    expect(response.status).toBe(400)
  })

  it('should require authentication', async () => {
    const response = await app.handle(
      new Request('http://localhost/api/profile')
    )

    expect(response.status).toBe(401)
  })

  it('should access protected route with token', async () => {
    const response = await app.handle(
      new Request('http://localhost/api/profile', {
        headers: { Authorization: 'Bearer valid-token' }
      })
    )

    expect(response.status).toBe(200)
  })
})
```

### Service Unit Tests

```typescript
import { describe, it, expect } from 'vitest'
import { createUser } from '../src/modules/users/service'

describe('User Service', () => {
  it('should create user with valid data', async () => {
    const result = await createUser({
      email: 'test@example.com',
      name: 'Test',
      password: 'password123'
    })

    expect(result.email).toBe('test@example.com')
    expect(result.id).toBeDefined()
  })
})
```

## Deployment

### Production Server Setup

```typescript
// src/server.ts
import { app } from './app'

const port = process.env.PORT || 3000

app.listen(port, () => {
  console.log(`Server running on port ${port}`)
})
```

### Cluster Mode for Multi-Core

```typescript
// src/index.ts
import cluster from 'node:cluster'
import os from 'node:os'

const numCPUs = os.cpus().length

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} is running`)

  for (let i = 0; i < numCPUs; i++) {
    cluster.fork()
  }

  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died, spawning replacement`)
    cluster.fork()
  })
} else {
  import('./server')
}
```

### Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable pnpm
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Runtime stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## Common Patterns

### State and Decorators

```typescript
const app = new Elysia()
  .state('version', '1.0.0')
  .decorate('getDate', () => new Date().toISOString())
  .get('/info', ({ store, getDate }) => ({
    version: store.version,
    timestamp: getDate()
  }))
```

### WebSocket Endpoints

```typescript
const app = new Elysia()
  .ws('/chat', {
    message(ws, message) {
      ws.send(`Echo: ${message}`)
    },
    open(ws) {
      console.log('Client connected')
    },
    close(ws) {
      console.log('Client disconnected')
    }
  })
```

### Custom Body Parser

```typescript
const app = new Elysia()
  .onParse(async ({ request, contentType }) => {
    if (contentType === 'application/custom') {
      return parseCustomFormat(await request.text())
    }
  })
```

## Validation Checklist

Before completing any Elysia-related task, verify:

- [ ] Feature structure follows `model.ts`, `service.ts`, `index.ts` pattern
- [ ] All handlers have proper schema definitions (body/query/params/response)
- [ ] Error handling uses centralized `.onError()` plugin
- [ ] Response schemas are defined for OpenAPI generation
- [ ] Tests use `app.handle(new Request(...))` pattern
- [ ] Type checks pass (`pnpm run typecheck`)
- [ ] Tests pass (`pnpm run test`)
- [ ] Linting passes (`pnpm run lint`)
