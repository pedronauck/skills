# Batching and Caching

Automatic request batching with `Effect.request` and `RequestResolver`, plus caching patterns.

## Table of Contents

- [The N+1 Problem](#the-n1-problem)
- [Request and RequestResolver](#request-and-requestresolver)
- [Declaring Requests](#declaring-requests)
- [Declaring Resolvers](#declaring-resolvers)
- [Defining Queries](#defining-queries)
- [Caching Effects](#caching-effects)

## The N+1 Problem

When iterating over items and fetching related data, naive implementations make one API call per item:

```typescript
// BAD: N+1 problem — if 100 todos, makes 100+ getUserById calls
const program = Effect.gen(function* () {
  const todos = yield* getTodos;
  yield* Effect.forEach(todos, (todo) => notifyOwner(todo), {
    concurrency: "unbounded",
  });
});
```

Effect's batching system solves this by automatically collecting concurrent requests and resolving them in batches.

## Request and RequestResolver

The batching system has three parts:

1. **Requests** — typed data structures describing what to fetch
2. **Resolvers** — handlers that process batches of requests
3. **Queries** — `Effect.request` calls that use resolvers

The caller code stays unchanged — Effect automatically batches requests that happen concurrently.

## Declaring Requests

Define request types using `Request.Request<Value, Error>`:

```typescript
import * as Request from "effect/Request";
import * as Data from "effect/Data";

// Request to get a user by ID
interface GetUserById extends Request.Request<User, GetUserError> {
  readonly _tag: "GetUserById";
  readonly id: number;
}
const GetUserById = Request.tagged<GetUserById>("GetUserById");

// Request to send an email
interface SendEmail extends Request.Request<void, SendEmailError> {
  readonly _tag: "SendEmail";
  readonly address: string;
  readonly text: string;
}
const SendEmail = Request.tagged<SendEmail>("SendEmail");

// Request that returns a list (non-batchable)
interface GetTodos extends Request.Request<Array<Todo>, GetTodosError> {
  readonly _tag: "GetTodos";
}
const GetTodos = Request.tagged<GetTodos>("GetTodos");
```

## Declaring Resolvers

### Standard Resolver (non-batchable)

For requests that cannot be batched:

```typescript
import * as RequestResolver from "effect/RequestResolver";

const GetTodosResolver = RequestResolver.fromEffect(
  (_: GetTodos): Effect.Effect<Todo[], GetTodosError> =>
    Effect.tryPromise({
      try: () => fetch("/api/todos").then((r) => r.json() as Promise<Todo[]>),
      catch: () => new GetTodosError(),
    })
);
```

### Batched Resolver

For requests that can be combined into a single API call:

```typescript
const GetUserByIdResolver = RequestResolver.makeBatched(
  (requests: ReadonlyArray<GetUserById>) =>
    Effect.tryPromise({
      try: () =>
        fetch("/api/users/batch", {
          method: "POST",
          body: JSON.stringify({ ids: requests.map((r) => r.id) }),
        }).then((r) => r.json() as Promise<User[]>),
      catch: () => new GetUserError(),
    }).pipe(
      // Complete each request with its corresponding result
      Effect.andThen((users) =>
        Effect.forEach(requests, (request, index) =>
          Request.completeEffect(request, Effect.succeed(users[index]!))
        )
      ),
      // On batch failure, fail all requests
      Effect.catchAll((error) =>
        Effect.forEach(requests, (request) =>
          Request.completeEffect(request, Effect.fail(error))
        )
      )
    )
);
```

**Key patterns for batched resolvers:**
- Use `Request.completeEffect` to resolve each request individually
- Always handle errors — fail all pending requests on batch failure
- The runtime groups concurrent `Effect.request` calls into batches automatically

## Defining Queries

Wrap requests into reusable query functions using `Effect.request`:

```typescript
const getTodos: Effect.Effect<Todo[], GetTodosError> = Effect.request(
  GetTodos({}),
  GetTodosResolver
);

const getUserById = (id: number): Effect.Effect<User, GetUserError> =>
  Effect.request(GetUserById({ id }), GetUserByIdResolver);

const sendEmail = (
  address: string,
  text: string
): Effect.Effect<void, SendEmailError> =>
  Effect.request(SendEmail({ address, text }), SendEmailResolver);
```

**Usage is identical to non-batched code:**

```typescript
const program = Effect.gen(function* () {
  const todos = yield* getTodos;
  yield* Effect.forEach(todos, (todo) => notifyOwner(todo), {
    concurrency: "unbounded",
  });
});
// If 5 todos share 2 owners, only 1 batch call for getUserById instead of 5
```

### Resolvers with Context

When resolvers need dependencies (e.g., HttpClient), use `RequestResolver.fromEffect` or construct within a Layer:

```typescript
const GetUserByIdResolver = RequestResolver.makeBatched(
  (requests: ReadonlyArray<GetUserById>) =>
    Effect.gen(function* () {
      const client = yield* HttpClient.HttpClient;
      // ... use client for batch request
    })
);

// Provide context when using the query
const getUserById = (id: number) =>
  Effect.request(GetUserById({ id }), GetUserByIdResolver);
```

## Caching Effects

### Effect.cachedWithTTL

Cache the result of an expensive effect for a duration:

```typescript
const cachedConfig = Effect.cachedWithTTL(loadRemoteConfig, "5 minutes");

const program = Effect.gen(function* () {
  const getConfig = yield* cachedConfig;
  const config1 = yield* getConfig; // Fetches
  const config2 = yield* getConfig; // Returns cached (within 5 min)
});
```

### Effect.cached

Cache an effect result forever (within scope):

```typescript
const cachedResult = Effect.cached(expensiveComputation);

const program = Effect.gen(function* () {
  const get = yield* cachedResult;
  const a = yield* get; // Computes once
  const b = yield* get; // Returns cached
});
```

### Effect.once

Ensure an effect runs at most once, even with concurrent calls:

```typescript
const program = Effect.gen(function* () {
  const logOnce = yield* Effect.once(Effect.log("Initialized"));
  yield* logOnce; // Logs "Initialized"
  yield* logOnce; // Does nothing
  yield* logOnce; // Does nothing
});
```
