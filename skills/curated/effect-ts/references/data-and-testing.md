# Data Types and Testing (Quick Reference)

> **Comprehensive data types reference**: See [`data-types.md`](./data-types.md) for full coverage of all 11 Effect data types (Option, Either, Data, Exit, Cause, Duration, DateTime, BigDecimal, Chunk, HashSet, Redacted).

Quick reference for Option/Either basics and Array utilities. For testing, see [`testing-patterns.md`](./testing-patterns.md).

## Option (quick)

```typescript
import * as Option from "effect/Option";

Option.some(42);                        // Some(42)
Option.none();                          // None
Option.fromNullable(null);              // None
Option.match(opt, { onNone: () => "absent", onSome: (v) => `${v}` });
Option.map(opt, (v) => v + 1);         // transform if Some
Option.flatMap(opt, (v) => Option.some(v)); // chain
Option.getOrElse(opt, () => 0);        // extract with fallback
Option.all([opt1, opt2]);              // all must be Some
```

## Either (quick)

```typescript
import * as Either from "effect/Either";

Either.right(42);                       // Right(42)
Either.left("error");                   // Left("error")
Either.match(e, { onLeft: (l) => l, onRight: (r) => r });
Either.map(e, (v) => v + 1);           // transform Right
Either.flatMap(e, (v) => Either.right(v)); // chain
Either.getOrElse(e, () => 0);          // extract with fallback
Either.all([e1, e2]);                   // first Left short-circuits
```

## Array Operations

```typescript
import * as Array from "effect/Array";

Array.map(numbers, (n) => n * 2);
Array.filter(numbers, (n) => n % 2 === 0);
Array.reduce(numbers, 0, (acc, n) => acc + n);
Array.head(items);                      // Option<T>
Array.findFirst(items, (item) => item.id === id); // Option<T>
Array.groupBy(items, (item) => item.category);
```

## Testing with @effect/vitest

> **IMPORTANT**: For comprehensive testing patterns including forbidden patterns, assertion APIs, and advanced strategies, see [`testing-patterns.md`](./testing-patterns.md).

### Setup

```bash
pnpm add -D vitest @effect/vitest
```

Update `package.json`:

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

### Assertion Rules

**CRITICAL**: Use `assert` from `@effect/vitest` for `it.effect` tests. Use `expect` from `vitest` only for pure (non-Effect) tests.

```typescript
// WRONG - Never use expect with it.effect
it.effect("wrong", () =>
  Effect.gen(function* () {
    const result = yield* someEffect;
    expect(result).toBe(value); // WRONG
  })
);

// CORRECT - Use assert with it.effect
it.effect("correct", () =>
  Effect.gen(function* () {
    const result = yield* someEffect;
    assert.strictEqual(result, value); // CORRECT
  })
);
```

### Basic Testing

```typescript
import { Effect } from "effect";
import { assert, describe, it } from "@effect/vitest";

describe("Calculator", () => {
  // Effect test - use assert
  it.effect("adds numbers", () =>
    Effect.gen(function* () {
      const result = yield* Effect.succeed(1 + 1);
      assert.strictEqual(result, 2);
    })
  );
});
```

For pure (non-Effect) tests, use standard vitest:

```typescript
import { describe, expect, it } from "vitest";

it("creates instances", () => {
  const result = 1 + 1;
  expect(result).toBe(2);
});
```

### Test Function Variants

```typescript
// it.effect() - Most common, for tests returning Effect
it.effect("processes data", () =>
  Effect.gen(function* () {
    const result = yield* processData("input");
    assert.strictEqual(result, "expected");
  })
);

// it.scoped() - For scoped resources with automatic cleanup
it.scoped("temp directory is cleaned up", () =>
  Effect.gen(function* () {
    const fs = yield* FileSystem.FileSystem;
    const tempDir = yield* fs.makeTempDirectoryScoped();
    // tempDir is deleted when test ends
  }).pipe(Effect.provide(NodeFileSystem.layer))
);

// it.live() - Uses real time (no TestClock)
it.live("real clock", () =>
  Effect.gen(function* () {
    const now = yield* Clock.currentTimeMillis;
    assert.isTrue(now > 0); // Actual system time
  })
);
```

### Using TestClock

`it.effect` automatically provides TestContext with TestClock:

```typescript
import { Effect, Fiber, TestClock } from "effect";
import { assert, it } from "@effect/vitest";

it.effect("time-based test", () =>
  Effect.gen(function* () {
    const fiber = yield* Effect.delay(
      Effect.succeed("done"),
      "10 seconds"
    ).pipe(Effect.fork);
    yield* TestClock.adjust("10 seconds");
    const result = yield* Fiber.join(fiber);
    assert.strictEqual(result, "done");
  })
);
```

### Test Layers

**Preferred: Per-Test Layering**
Provide a fresh layer for each test to ensure isolation and prevent state leaks.

```typescript
// Create test layer with inline values
it.effect("queries database", () =>
  Effect.gen(function* () {
    const db = yield* Database;
    const results = yield* db.query("SELECT * FROM users");
    assert.strictEqual(results.length, 2);
  }).pipe(Effect.provide(Database.testLayer))
);
```

**Advanced: Shared Suite Layers (`it.layer`)**
Use `it.layer` only when you need to share an expensive resource (like a DB connection) across an entire suite. **Warning:** State will leak between tests.

```typescript
// Shared layer initialized once for the suite
it.layer(Database.testLayer)("Database Suite", (it) => {
  it.effect("test 1", () => ...);
  it.effect("test 2", () => ...);
});
```

### Test Modifiers

```typescript
it.effect.skip("temporarily disabled", () => ...);
it.effect.only("focus on this test", () => ...);
it.effect.fails("known bug - expected to fail", () => ...);
```

