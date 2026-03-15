---
name: elysia
description: Expert guide for building APIs with the Elysia framework, including routing, validation, plugins, error handling, and type-safe handlers. Use when building APIs with Elysia framework, defining routes, plugins, or type-safe handlers.
allowed-tools: Read, Grep, Glob
---

# Elysia Developer Guide

This skill provides guidelines, patterns, and best practices for working with the Elysia framework in this project.

## Quick Start

For detailed development guidelines, imports, and patterns, please refer to `references/patterns.md` in this skill directory.

## Core Philosophy

- **Pattern-agnostic but feature-based** structure recommended
- **"1 Elysia instance = 1 controller"** principle
- **Strong typing** with TypeBox for runtime validation
- **Centralized error handling** and consistent responses
- **Production-ready** deployment strategies

## Structure, Routing & Controllers

### Essential Organization Patterns

- **App as controller**: Treat each `new Elysia({ prefix })` instance as the controller for that feature. Do **not** pass entire class methods directly as handlers. Instead, inline a small handler that calls service functions.
- **Feature folders**: Use a feature-based structure:
  - `src/modules/<feature>/index.ts` - Elysia controller (routes, guards, cookies)
  - `src/modules/<feature>/service.ts` - business logic (no HTTP context)
  - `src/modules/<feature>/model.ts` - schemas & types via `t` (TypeBox)
  - Keep shared utilities in `src/utils/*`.
- **Method chaining**: Prefer fluent chaining on the Elysia instance for routes, guards, plugins.
- **Plugins**: Encapsulate cross-cutting concerns in plugins via `.use()` (e.g., OpenAPI, JWT, CORS).
- **Context hygiene**: If a service needs request data, keep it in the controller and pass only the relevant fields into the service function.

### Feature Scaffolding Pattern

When scaffolding a feature, generate:

1. `model.ts` with `t.Object(...)` schemas and exported `type` aliases via `typeof schema.static`.
2. `service.ts` with pure functions (or an `abstract class` of statics when no instance state is needed).
3. `index.ts` that mounts the Elysia routes, applies `guard()` with shared validation, and returns typed responses.

## Validation, Schemas & Types

### Runtime Validation + Static Types

- Use `import { t } from 'elysia'` to define **Body**, **Query**, **Params**, **Headers**, **Cookie**, and **Response** schemas.
- Derive TS types from `typeof schema.static` and export them (e.g., `export type SignInBody = typeof signInBody.static`).
- Apply shared validation with `.guard({ ... })`. If combining guards, consider `schema: 'standalone'` to keep them independent.
- Validate **files** by content: use `fileType` (magic number) when using standard schema systems.
- Ensure **response** schemas are present for 2xx and error variants for strong end-to-end typing.

### Handler Schema Guidelines

When generating handlers:

- Include the 3rd argument schema object with `body/query/params/headers/cookie/response`.
- Don't parse body for GET/HEAD (Elysia follows HTTP spec).
- Provide examples with `t.Object`, `t.Array`, `t.Union`, `t.Literal`, file schemas, and show `guard()` for shared query/headers.

## Error Handling & Response Shape

### Centralized Error Management

- Use `.onError(({ code, error, path, request }) => { ... })` on the app to map framework and custom errors to a **uniform JSON** shape (e.g., `{ ok: false, error: { code, message, details } }`).
- Prefer `throw status(code, messageOrPayload)` for error control flow that `onError` can catch. Note: `return status(...)` won't be caught by `onError`.
- Validation errors: normalize them to a predictable JSON (array of issues) while hiding sensitive internals in production.
- Include correlation ids (e.g., `x-request-id`) and log within `onError`. Avoid leaking stack traces in production.
- For success responses, optionally wrap in `{ ok: true, data }` for uniformity.

### Error Plugin Structure

When generating code, create:

- `src/plugins/error.ts` that installs `.onError(...)`.
- Optionally `src/plugins/logging.ts` to log in `onResponse` & `onError`.

## OpenAPI, Auth & Cross-cutting

### OpenAPI

- Add `@elysiajs/openapi` plugin and expose docs route (Scalar UI).
- Keep **response** schemas accurate - OpenAPI derives from them.
- If building SDKs, ensure routes are fully typed and examples provided.

### Auth

- Use `@elysiajs/jwt` for JWT signing/verification, or integrate with your auth of choice.
- Keep auth in a plugin that decorates context with `user` after verification.
- Protect routes via `.guard({ headers: t.Object({ authorization: t.String() }) })` and verify bearer tokens before handlers.

### Cross-cutting Plugins

- Install `@elysiajs/cors` where needed.
- Consider `@elysiajs/server-timing` and `@elysiajs/opentelemetry` for observability.

When scaffolding, generate `src/plugins/openapi.ts`, `src/plugins/auth.ts`, and wire them in `src/app.ts`.

## Deploy, Performance & Docker

### Production Deployment

- **Cluster mode** for multi-core: use a small launcher (`index.ts`) that forks workers and imports `server.ts` per worker.
- Prefer building with bundlers like Vite or esbuild for production deployments.
- If compiling interferes with tracing (OpenTelemetry), avoid `--minify` or mark instrumented modules as `--external`.
- Accept `process.env.PORT` (with fallback) and bind `0.0.0.0` for PaaS.

### Docker

- Build stage: use Node.js base image with pnpm.
- Runtime: **distroless** base, copy binary, `CMD ["./server"]`.

### Deployment Scaffolding

When generating a deploy scaffold, include:

- `src/index.ts` (cluster launcher), `src/server.ts` (app), `Dockerfile` (multi-stage), and build scripts.

## Testing

### Unit Tests

- Use `vitest`.
- Import the app and use `app.handle(new Request(url, options))` to assert status/body/headers.
- For service tests, call pure functions directly.

### Test Examples to Include

- Simple GET test returning text.
- POST with `body` validation (both valid and invalid paths).
- Authenticated route example using a mocked `Authorization` header.
- Prefer small, focused tests per route and per service.

## Quick Utilities

### Common Patterns

- App context: use `.state()` and `.decorate()` to add version info, helpers, etc., then read from `{ store, getDate }`.
- WebSocket endpoints via `.ws()` for simple real-time APIs.
- Custom body parser with `.onParse()` for special content types.

## Validation Checklist

Before finishing a task involving Elysia:

- [ ] Feature structure follows `model.ts`, `service.ts`, `index.ts` pattern.
- [ ] All handlers have proper schema definitions (body/query/params/response).
- [ ] Error handling uses centralized `.onError()` plugin.
- [ ] Response schemas are defined for OpenAPI generation.
- [ ] Tests use `app.handle(new Request(...))` pattern.
- [ ] Run type checks (`pnpm run typecheck`) and tests (`pnpm run test`).

For detailed patterns and code examples, see `references/patterns.md`.
