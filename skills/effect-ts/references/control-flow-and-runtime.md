# Control Flow and Runtime

Control flow operators, running effects, and runtime customization patterns.

## Table of Contents

- [Control Flow Operators](#control-flow-operators)
- [Running Effects](#running-effects)
- [ManagedRuntime](#managedruntime)
- [Locally Scoped Runtime Config](#locally-scoped-runtime-configuration)

## Control Flow Operators

### Effect.if

Executes one of two effects based on an effectful boolean predicate:

```typescript
import * as Effect from "effect/Effect";
import * as Random from "effect/Random";

const coinFlip = Effect.if(Random.nextBoolean, {
  onTrue: () => Effect.log("Heads"),
  onFalse: () => Effect.log("Tails"),
});
```

### Effect.when / Effect.unless

Conditionally execute an effect. Returns `Option<A>` — `Some(result)` if executed, `None` if skipped:

```typescript
import * as Effect from "effect/Effect";
import * as Option from "effect/Option";

// Execute only if condition is true
const validateWeight = (weight: number): Effect.Effect<Option.Option<number>> =>
  Effect.succeed(weight).pipe(Effect.when(() => weight >= 0));

// Execute only if condition is false (inverse of when)
const logUnlessAdmin = (isAdmin: boolean) =>
  Effect.log("Non-admin access").pipe(Effect.unless(() => isAdmin));
```

### Effect.whenEffect / Effect.unlessEffect

Same as `when`/`unless` but the condition itself is an effect:

```typescript
const randomInt = Random.nextInt.pipe(Effect.whenEffect(Random.nextBoolean));
// Only generates a random int if random boolean is true
```

### Effect.zip / Effect.zipWith

Combine two effects into a tuple or custom value:

```typescript
const combined = Effect.zip(task1, task2); // [A, B]
const summed = Effect.zipWith(task1, task2, (a, b) => a + b); // C

// Run concurrently with { concurrent: true }
const parallel = Effect.zip(task1, task2, { concurrent: true });
```

### Effect.all (with modes)

```typescript
// Fail fast (default) — stops at first error
const results = yield* Effect.all([task1, task2, task3]);

// Concurrent execution
const concurrent = yield* Effect.all(tasks, { concurrency: "unbounded" });

// Controlled concurrency
const controlled = yield* Effect.all(tasks, { concurrency: 5 });

// With discard — ignores results, returns void
yield* Effect.all(tasks, { discard: true });
```

### Effect.forEach

Apply effectful operation to each element:

```typescript
const results = yield* Effect.forEach([1, 2, 3], (n, index) =>
  Effect.succeed(n * 2)
);
// [2, 4, 6]

// Concurrent forEach
yield* Effect.forEach(items, processItem, { concurrency: "unbounded" });
```

### Effect.loop / Effect.iterate

Effectful loops with state:

```typescript
// loop — collects results into array
const collected = yield* Effect.loop(1, {
  while: (state) => state <= 5,
  step: (state) => state + 1,
  body: (state) => Effect.succeed(state * 2),
});
// [2, 4, 6, 8, 10]

// loop with discard — side effects only, returns void
yield* Effect.loop(0, {
  while: (i) => i < 3,
  step: (i) => i + 1,
  body: (i) => Effect.log(`Step ${i}`),
  discard: true,
});

// iterate — returns final state only (no collection)
const final = yield* Effect.iterate(1, {
  while: (result) => result <= 100,
  body: (result) => Effect.succeed(result * 2),
});
// 128
```

## Running Effects

### Core Run Functions

| Function | Returns | When to Use |
|---|---|---|
| `Effect.runSync` | `A` (throws on error/async) | Sync-only effects, no errors |
| `Effect.runSyncExit` | `Exit<A, E>` | Sync-only, inspect success/failure |
| `Effect.runPromise` | `Promise<A>` (rejects on error) | Most common, async-compatible |
| `Effect.runPromiseExit` | `Promise<Exit<A, E>>` | Async, inspect success/failure |
| `Effect.runFork` | `Fiber<A, E>` | Fire-and-forget, fiber control |

```typescript
// runSync — synchronous only, throws on failure or async
const value = Effect.runSync(Effect.succeed(42)); // 42

// runPromise — most common entry point
const result = await Effect.runPromise(myEffect);

// runPromiseExit — inspect without throwing
const exit = await Effect.runPromiseExit(myEffect);
if (exit._tag === "Success") console.log(exit.value);
else console.log(exit.cause);

// runFork — non-blocking, returns a Fiber
const fiber = Effect.runFork(longRunningEffect);
```

**Warning**: `Effect.runSync` throws if the effect is async or fails. Use `runPromise` for async effects.

### NodeRuntime.runMain

For Node.js entry points, use the platform runtime:

```typescript
import * as NodeRuntime from "@effect/platform-node/NodeRuntime";
import * as NodeContext from "@effect/platform-node/NodeContext";

const main = program.pipe(Effect.provide(NodeContext.layer));
NodeRuntime.runMain(main);
```

## ManagedRuntime

Use `ManagedRuntime` to share a pre-built runtime (with context, config, etc.) across multiple effect runs. Common in server frameworks:

```typescript
import * as ManagedRuntime from "effect/ManagedRuntime";
import * as Layer from "effect/Layer";

const AppRuntime = ManagedRuntime.make(AppLayer);

// Reuse across HTTP handlers
app.get("/users", async (req, res) => {
  const result = await AppRuntime.runPromise(UserController.list(req.query));
  res.json(result);
});

// Clean up on shutdown
process.on("SIGTERM", () => AppRuntime.dispose());
```

**When to use ManagedRuntime:**
- Web servers (share services across requests)
- React apps (share runtime across components)
- Long-running processes with shared state

## Locally Scoped Runtime Configuration

Override runtime config for a specific part of your code. Config reverts after that region completes:

```typescript
import * as Logger from "effect/Logger";
import * as LogLevel from "effect/LogLevel";

// Custom logger for a specific scope
const withSimpleLogger = Logger.replace(
  Logger.defaultLogger,
  Logger.make(({ message }) => console.log(message))
);

const program = Effect.gen(function* () {
  yield* Effect.log("This uses custom logger");
}).pipe(Effect.provide(withSimpleLogger));

// Override log level for a scope
const debugSection = myEffect.pipe(
  Logger.withMinimumLogLevel(LogLevel.Debug)
);
```
