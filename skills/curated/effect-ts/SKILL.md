---
name: effect-ts
description: Expert guide for writing Effect-TS code, including project setup, core principles, data modeling with Schema, error handling, and the Context.Tag service pattern. Use when writing, refactoring, or analyzing TypeScript code using the Effect library.
allowed-tools: Read, Grep, Glob
---

# Effect-TS Developer Guide

Guidelines, patterns, and best practices for Effect-TS in this project.

## Reference Documents

Read the relevant reference before writing code. `references/core-patterns.md` is the master index.

| Reference | Topics |
|---|---|
| `references/foundations.md` | Setup, imports, TypeScript config |
| `references/construction-and-style.md` | `Effect.gen`, `pipe`, `Effect.fn`, `Effect.fnUntraced` |
| `references/schema-errors-config.md` | Schema modeling, errors, config, retry |
| `references/pattern-matching.md` | **`Match.type`, `Match.value`, `Match.tag`, `Match.exhaustive`** — mandatory for tagged unions |
| `references/control-flow-and-runtime.md` | `Effect.if`, `Effect.when`, loops, `runSync`, `runPromise`, `ManagedRuntime` |
| `references/data-types.md` | **All data types**: `Option`, `Either`, `Data`, `Exit`, `Cause`, `Duration`, `DateTime`, `BigDecimal`, `Chunk`, `HashSet`, `Redacted` |
| `references/data-and-testing.md` | Option/Either/Array quick ref, `@effect/vitest` setup |
| `references/concurrency-and-resources.md` | Concurrency, `Scope`, finalizers, resources |
| `references/streams-deep-dive.md` | Creating, operations, grouping, partitioning, broadcasting, buffering, throttling, error handling |
| `references/sink.md` | Sink constructors, collecting, folding, operations, concurrency, leftovers, `Stream.transduce` |
| `references/batching-and-caching.md` | Request batching (`RequestResolver`), `cachedWithTTL` |
| `references/schema-transforms-and-filters.md` | `Schema.transform`, `Schema.filter`, refinements |
| `references/api-platform-observability.md` | `HttpApi`, logging, tracing, spans |
| `references/class-patterns.md` | `Context.Tag` service pattern, layers, memoization, testing |
| `references/error-handling-patterns.md` | `Data.TaggedError`, `Schema.TaggedError`, error composition, recovery |
| `references/library-development-patterns.md` | Forbidden patterns, `Effect.fn` vs `Effect.fnUntraced`, resource management |
| `references/testing-patterns.md` | `@effect/vitest` with `assert`, `TestClock`, service mocking |
| `references/quality-tooling-and-resources.md` | Anti-patterns, validation checklist, packages |

## Core Principles

1. **Effect is not just for async** — Use `Effect` for any fallible operation
2. **Immutability** — Use Effect's immutable data structures (`Data`, `Chunk`, `HashSet`)
3. **Type Safety** — Track errors in types. No `any` or `unknown` in error channels
4. **Composition** — Build programs by composing small Effects
5. **Schema-First** — Define data models using `Schema` with branded types
6. **Pattern Matching** — Use `Match` for all branching over tagged unions (never `switch`/`if-else` on `_tag`)
7. **Effect Data Types** — Use `Option` (not null), `Either` (not ad-hoc), `Duration` (not raw ms), `DateTime` (not Date), `BigDecimal` (not floats), `Redacted` (for secrets). See `references/data-types.md`

## Quick Reference

### Import Convention

```typescript
import * as Context from "effect/Context";
import * as Effect from "effect/Effect";
import * as Layer from "effect/Layer";
import * as Schema from "effect/Schema";
import * as Match from "effect/Match";
import * as Option from "effect/Option";
import * as Either from "effect/Either";
import * as Data from "effect/Data";
import * as Duration from "effect/Duration";
import { pipe } from "effect/Function";
// Also: DateTime, BigDecimal, Chunk, HashSet, Exit, Cause, Redacted
```

### Effect.gen vs pipe vs Effect.fn

```typescript
// Effect.gen — complex logic with branching
Effect.gen(function* () {
  const user = yield* fetchUser(id);
  if (user.isAdmin) yield* logAdminAccess(user);
  return user;
});

// pipe — linear transformations
pipe(fetchData(), Effect.map(transform), Effect.flatMap(save));

// Effect.fn — traced reusable functions (public API)
const processUser = Effect.fn("processUser")(function* (userId: string) {
  const user = yield* getUser(userId);
  return yield* processData(user);
});
```

### Error Handling

`Data.TaggedError` for in-process discrimination, `Schema.TaggedError` for serializable errors. See `references/error-handling-patterns.md`.

```typescript
export class NotFoundError extends Data.TaggedError("NotFoundError")<{
  id: string;
}> {}

// Recovery
pipe(riskyOp, Effect.catchTag("NotFoundError", (e) => Effect.succeed(null)));
```

### Pattern Matching (Mandatory for Tagged Unions)

**Always use `Match`** — `Match.exhaustive` catches missing cases at compile time. See `references/pattern-matching.md`.

```typescript
// Match.type — reusable matcher function
const handle = Match.type<Status>().pipe(
  Match.tag("Pending", (s) => `Pending since ${s.requestedAt}`),
  Match.tag("Approved", (s) => `Approved by ${s.approvedBy}`),
  Match.exhaustive // Compile error if any variant is missing
);

// Match.valueTags — shorthand for immediate matching
Match.valueTags(status, {
  Pending: (s) => `Pending since ${s.requestedAt}`,
  Approved: (s) => `Approved by ${s.approvedBy}`,
});
```

### Service Pattern (Context.Tag)

See `references/class-patterns.md` for full pattern with factory methods and layers.

```typescript
export class MyService extends Context.Tag("@myapp/MyService")<
  MyService,
  { readonly find: (id: string) => Effect.Effect<Result, NotFoundError> }
>() {
  static readonly layer = Layer.effect(MyService, Effect.gen(function* () {
    const db = yield* Database;
    return MyService.of({ find: MyService.createFind(db) });
  }));
}
```

### Testing

**CRITICAL**: Use `assert` from `@effect/vitest` for `it.effect`. Never `expect` with `it.effect`. See `references/testing-patterns.md`.

```typescript
import { assert, describe, it } from "@effect/vitest";

it.effect("processes data", () =>
  Effect.gen(function* () {
    const result = yield* processData("input");
    assert.strictEqual(result, "expected");
  }).pipe(Effect.provide(MyService.testLayer))
);
```

## Forbidden Patterns

```typescript
// NEVER: try-catch in Effect.gen — use Effect.exit instead
Effect.gen(function* () {
  try { yield* someEffect } catch (e) { } // WRONG — will never catch
});

// NEVER: Type assertions
const value = something as any;   // FORBIDDEN
const value = something as never; // FORBIDDEN

// NEVER: Missing return on terminal yield
Effect.gen(function* () {
  if (bad) { yield* Effect.fail("err") } // Missing return!
});

// NEVER: switch/if-else on _tag — use Match instead
switch (status._tag) { /* no exhaustiveness checking! */ }

// NEVER: Effect.runSync inside Effects
Effect.gen(function* () { Effect.runSync(sideEffect) }); // Loses error tracking

// NEVER: Native JS where Effect data types exist
const x: string | null = null;              // Use Option<string>
const delay = 5000;                         // Use Duration.seconds(5)
const now = new Date();                     // Use DateTime.now or DateTime.unsafeNow()
const price = 0.1 + 0.2;                   // Use BigDecimal for precision
const secret = "sk-1234";                   // Use Redacted.make("sk-1234")

// NEVER: expect with it.effect
it.effect("test", () => Effect.gen(function* () {
  expect(result).toBe(value) // WRONG — use assert.strictEqual
}));

// NEVER: Inline layers (breaks memoization)
Layer.provide(Postgres.layer({ url })) // Store in constant instead
```

## Validation Checklist

- [ ] Imports use `import * as Module from "effect/Module"`
- [ ] `Effect.gen` for complex logic, `pipe` for linear, `Effect.fn` for public API
- [ ] `Match` for all `_tag` branching with `Match.exhaustive`
- [ ] Branded types for domain primitives (IDs, Emails)
- [ ] Errors: `Data.TaggedError` (discrimination) or `Schema.TaggedError` (serializable)
- [ ] No `any`/`unknown` in error channels, no type assertions
- [ ] No try-catch in `Effect.gen` — use `Effect.exit`
- [ ] `return yield*` for terminal effects (`Effect.fail`, `Effect.interrupt`)
- [ ] Services: `Context.Tag` with static factory methods and `Effect.fn` tracing
- [ ] Layers: `Layer.merge`/`Layer.provide`, parameterized layers in constants
- [ ] Resources: `Effect.acquireRelease` or `Effect.scoped`
- [ ] `Option` for nullable values, `Either` for sync success/failure
- [ ] `Duration` for time values, `DateTime` for dates (not `Date`)
- [ ] `BigDecimal` for financial/precise math, `Redacted` for secrets
- [ ] `Data.struct`/`Data.Class` for structural equality, `HashSet` for sets
- [ ] `Clock.currentTimeMillis` instead of `Date.now()`
- [ ] Tests: `assert` from `@effect/vitest` (not `expect`) with `it.effect`
- [ ] Run `pnpm run typecheck` and `pnpm run test`

## Reference Implementation

See `/packages/looper/src/data/api-client/api-client.ts` for Context.Tag service pattern.

## Effect Solutions CLI

```bash
pnpm exec effect-solutions list              # List all topics
pnpm exec effect-solutions show <slug...>    # Read topics
pnpm exec effect-solutions search <term>     # Search by keyword
```
