# Effect Construction and Style

Patterns for constructing effects and choosing between `Effect.gen`, `pipe`, and `Effect.fn`.

## Effect Construction Patterns

### Creating Effects

```typescript
// Success value
const success = Effect.succeed(42);

// Synchronous computation
const sync = Effect.sync(() => Math.random());

// Async computation
const async = Effect.promise(() => fetch("/api/data"));

// Fallible operation
const fallible = Effect.try({
  try: () => JSON.parse(data),
  catch: (error) => new JsonParseError({ error }),
});

// From Either/Option
const fromEither = Effect.fromEither(either);
const fromOption = Effect.fromOption(option);
```

### Never Use These Patterns

```typescript
// BAD: Don't use localStorage or browser storage APIs
localStorage.setItem("key", "value"); // Throws SecurityError in Effect sandbox

// BAD: Don't use bare try/catch for business logic
try {
  const result = riskyOperation();
} catch (error) {
  // Type information lost
}

// GOOD: Use Effect.try or Effect.tryPromise
const safe = Effect.try({
  try: () => riskyOperation(),
  catch: (error) => new RiskyOperationError({ cause: error }),
});
```

## Code Style: Effect.gen vs pipe

### Effect.gen Style (Recommended for Complex Logic)

Use `Effect.gen` for sequential, readable code similar to async/await:

```typescript
const program = Effect.gen(function* () {
  const user = yield* fetchUser(userId);
  const orders = yield* fetchOrders(user.id);
  const enriched = yield* enrichOrders(orders);
  return enriched;
});
```

### Effect.fn for Traced Functions (Recommended)

Use `Effect.fn` with generator functions for traced, named effects. This provides call-site tracing for debugging and observability:

```typescript
// Use Effect.fn for named, traceable functions
const processUser = Effect.fn("processUser")(function* (userId: string) {
  yield* Effect.logInfo(`Processing user ${userId}`);
  const user = yield* getUser(userId);
  return yield* processData(user);
});

// Use Effect.fn even for nullary methods (thunks)
const getAllUsers = Effect.fn("getAllUsers")(function* () {
  const response = yield* http.get("/api/users");
  return yield* parseUsers(response);
});
```

**Benefits of Effect.fn:**
- Call-site tracing for each invocation
- Stack traces with location details
- Automatic spans for telemetry integration
- Clean function signatures

### pipe Style (Recommended for Linear Transformations)

```typescript
const program = pipe(
  fetchUser(userId),
  Effect.flatMap((user) => fetchOrders(user.id)),
  Effect.flatMap(enrichOrders)
);
```

### Pipe for Instrumentation

Use `.pipe()` to add cross-cutting concerns:

```typescript
const program = fetchData.pipe(
  Effect.timeout("5 seconds"),
  Effect.retry(
    Schedule.exponential("100 millis").pipe(Schedule.compose(Schedule.recurs(3)))
  ),
  Effect.tap((data) => Effect.logInfo(`Fetched: ${data}`)),
  Effect.withSpan("fetchData")
);
```

**Common instrumentation:**
- `Effect.timeout` - fail if effect takes too long
- `Effect.retry` - retry on failure with a schedule
- `Effect.tap` - run side effect without changing the value
- `Effect.withSpan` - add tracing span

### Avoid Mixing Styles

```typescript
// BAD: Don't mix gen and pipe unnecessarily
const bad = Effect.gen(function* () {
  const result = yield* pipe(
    Effect.succeed(1),
    Effect.map((x) => x + 1)
  );
  return result;
});

// GOOD: Stay consistent
const good = pipe(
  Effect.succeed(1),
  Effect.map((x) => x + 1)
);
```

