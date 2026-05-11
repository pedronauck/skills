# Concurrency and Resource Management

Structured concurrency, pattern matching, and safe resource lifecycle patterns.

## Concurrency & Streaming

### Concurrent Operations

```typescript
// Parallel execution
const parallel = Effect.all([task1, task2, task3], {
  concurrency: "unbounded",
});

// Controlled concurrency
const controlled = Effect.all(tasks, { concurrency: 5 });

// Race operations
const fastest = Effect.race(fetchFromCache, fetchFromDatabase);

// Collect all with different behaviors
const allOrFail = Effect.all(effects); // Fail if any fails
const allSettled = Effect.allSuccesses(effects); // Continue on failures
```

### FiberSet (Structured Concurrency)

Use `FiberSet` for managing dynamic collections of background tasks. This ensures proper scope management and cleanup, preventing "fire-and-forget" leaks.

```typescript
import { FiberSet } from "effect";

const program = Effect.gen(function* () {
  // Create a FiberSet tied to the current scope
  const set = yield* FiberSet.make();

  // Run background tasks managed by the set
  yield* FiberSet.run(set, Effect.log("Background task 1"));
  yield* FiberSet.run(set, Effect.log("Background task 2"));

  // All fibers in the set are automatically interrupted when the scope closes
});
```

### Sequential Execution

```typescript
// Run effects sequentially
const results = yield* Effect.all([effect1, effect2, effect3], {
  concurrency: 1,
});

// forEach with sequential execution
yield* Effect.forEach(items, (item) => processItem(item), { concurrency: 1 });
```

### Working with Streams

```typescript
import * as Stream from "effect/Stream";

const numbers = Stream.range(1, 100);

const processed = pipe(
  numbers,
  Stream.map((n) => n * 2),
  Stream.filter((n) => n > 50),
  Stream.take(10)
);

const collected = Stream.runCollect(processed);
```

## Pattern Matching

```typescript
import * as Match from "effect/Match";

// Match on tagged types
const handleResult = Match.type<Result>().pipe(
  Match.tag("Success", (success) => Effect.succeed(success.data)),
  Match.tag("Error", (error) => Effect.fail(error)),
  Match.exhaustive
);

// Match on values with Match.valueTags
const result = Match.valueTags(value, {
  Success: ({ data }) => `Got: ${data}`,
  Failure: ({ error }) => `Error: ${error}`,
});
```

## Resource Management

### Using acquireRelease

```typescript
// Automatic cleanup with acquireRelease
const managedConnection = Effect.acquireRelease(
  Effect.sync(() => createConnection()),
  (connection) => Effect.sync(() => connection.close())
);

// Use with scoped
Effect.scoped(
  Effect.gen(function* () {
    const connection = yield* managedConnection;
    return yield* connection.query("SELECT * FROM users");
  })
);
```

### acquireUseRelease Pattern

```typescript
const withConnection = <A, E, R>(
  use: (conn: Connection) => Effect.Effect<A, E, R>
): Effect.Effect<A, E | ConnectionError, R> =>
  Effect.acquireUseRelease(
    Effect.tryPromise({
      try: () => createConnection(),
      catch: (error) => new ConnectionError({ cause: error }),
    }),
    use,
    (conn) => Effect.sync(() => conn.close())
  );

// Use with Effect.scoped
const program = Effect.scoped(
  Effect.gen(function* () {
    const conn = yield* withConnection(identity);
    const result = yield* conn.query("SELECT * FROM users");
    return result;
  })
);
```

### Scope and Finalizers

A `Scope` represents the lifetime of resources. When closed, all finalizers run in reverse order:

```typescript
import * as Scope from "effect/Scope";

// Manual scope management (rarely needed)
const manual = Scope.make().pipe(
  Effect.tap((scope) =>
    Scope.addFinalizer(scope, Effect.log("cleanup 1"))
  ),
  Effect.tap((scope) =>
    Scope.addFinalizer(scope, Effect.log("cleanup 2"))
  ),
  Effect.andThen((scope) =>
    Scope.close(scope, Exit.succeed("done"))
  )
);
// Output: cleanup 2, cleanup 1 (reverse order)
```

### Effect.addFinalizer

High-level API — automatically ties to the current scope. The finalizer receives the `Exit` value:

```typescript
const program = Effect.gen(function* () {
  yield* Effect.addFinalizer((exit) =>
    Effect.log(`Cleanup. Exit: ${exit._tag}`)
  );
  return "result";
});

// Effect.scoped closes the scope and runs finalizers
const runnable = Effect.scoped(program);
```

### Exit-Dependent Cleanup

Finalizers can vary behavior based on success or failure:

```typescript
yield* Effect.addFinalizer((exit) =>
  exit._tag === "Success"
    ? Effect.log("Committed transaction")
    : Effect.log("Rolling back transaction")
);
```

### Scoped Resources in Layers

Resources that live as long as their Layer:

```typescript
const DbPoolLayer = Layer.scoped(
  DbPool,
  Effect.gen(function* () {
    const pool = yield* Effect.acquireRelease(
      Effect.sync(() => createPool({ size: 10 })),
      (pool) => Effect.sync(() => pool.close())
    );
    return DbPool.of(pool);
  })
);
// Pool is created when Layer is built, closed when Layer is disposed
```

