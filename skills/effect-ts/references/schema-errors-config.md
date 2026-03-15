# Schema, Errors, and Configuration

Schema-first modeling, typed error design, and configuration patterns.

## Schema-First Development

### Data Modeling Fundamentals

All representable data is composed of:
- **Records (AND types)**: A `User` has a name AND an email AND a createdAt
- **Variants (OR types)**: A `Result` is a Success OR a Failure

### Branded Types (Critical)

**In a well-designed domain model, nearly all primitives should be branded**. Not just IDs, but emails, URLs, timestamps, slugs, counts, percentages, and any value with semantic meaning:

```typescript
import * as Schema from "effect/Schema";

// IDs - prevent mixing different entity IDs
export const UserId = Schema.String.pipe(Schema.brand("UserId"));
export type UserId = typeof UserId.Type;

export const PostId = Schema.String.pipe(Schema.brand("PostId"));
export type PostId = typeof PostId.Type;

// Domain primitives with validation
export const Email = Schema.String.pipe(
  Schema.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
  Schema.brand("Email")
);
export type Email = typeof Email.Type;

export const Port = Schema.Int.pipe(
  Schema.between(1, 65535),
  Schema.brand("Port")
);
export type Port = typeof Port.Type;

export const PositiveInt = Schema.Number.pipe(
  Schema.int(),
  Schema.positive(),
  Schema.brand("PositiveInt")
);
export type PositiveInt = typeof PositiveInt.Type;

// Usage - impossible to mix types
function getUser(id: UserId) {
  return id;
}
function sendEmail(to: Email) {
  return to;
}

const userId = UserId.make("user-123");
const postId = PostId.make("post-456");

getUser(userId); // Works
// getUser(postId) // Type error: Can't pass PostId where UserId expected
```

### Records with Schema.Class

```typescript
import * as Schema from "effect/Schema";

const UserId = Schema.String.pipe(Schema.brand("UserId"));
type UserId = typeof UserId.Type;

export class User extends Schema.Class<User>("User")({
  id: UserId,
  name: Schema.NonEmptyString,
  email: Schema.String,
  createdAt: Schema.Date,
}) {
  // Add custom getters and methods
  get displayName() {
    return `${this.name} (${this.email})`;
  }
}
```

### Variants with Schema.TaggedClass

For structured variants with fields, combine `Schema.TaggedClass` with `Schema.Union`:

```typescript
import * as Schema from "effect/Schema";
import * as Match from "effect/Match";

// Define variants with a tag field
export class Pending extends Schema.TaggedClass<Pending>()("Pending", {
  requestedAt: Schema.DateFromSelf,
}) {}

export class Approved extends Schema.TaggedClass<Approved>()("Approved", {
  approvedBy: UserId,
  approvedAt: Schema.DateFromSelf,
}) {}

export class Rejected extends Schema.TaggedClass<Rejected>()("Rejected", {
  reason: Schema.String,
  rejectedAt: Schema.DateFromSelf,
}) {}

// Create the union
export const Status = Schema.Union(Pending, Approved, Rejected);
export type Status = typeof Status.Type;

// Pattern match with Match.valueTags
const success = Pending.make({ requestedAt: new Date() });

Match.valueTags(success, {
  Pending: ({ requestedAt }) => `Pending since: ${requestedAt}`,
  Approved: ({ approvedBy }) => `Approved by: ${approvedBy}`,
  Rejected: ({ reason }) => `Rejected: ${reason}`,
});
```

### JSON Encoding & Decoding

Use `Schema.parseJson` to parse JSON strings and validate in one step:

```typescript
import * as Schema from "effect/Schema";
import * as Effect from "effect/Effect";

class Move extends Schema.Class<Move>("Move")({
  from: Position,
  to: Position,
}) {}

// parseJson combines JSON.parse + schema decoding
const MoveFromJson = Schema.parseJson(Move);

const program = Effect.gen(function* () {
  const jsonString =
    '{"from":{"row":"A","column":"1"},"to":{"row":"B","column":"2"}}';

  // Parse and validate JSON string in one step
  const move = yield* Schema.decodeUnknown(MoveFromJson)(jsonString);

  // Encode back to JSON string
  const json = yield* Schema.encode(MoveFromJson)(move);
  return json;
});
```

### Schema Usage Patterns

```typescript
// Decoding (parsing external data)
const parseUser = Schema.decode(User);

const program = pipe(
  Effect.succeed(rawApiData),
  Effect.flatMap(parseUser),
  Effect.map((user) => user)
);

// Encoding (serializing for external use)
const encodeUser = Schema.encode(User);
```

## Error Handling

### Error Type Patterns with Schema.TaggedError

```typescript
import * as Schema from "effect/Schema";

// Tagged error classes - serializable and type-safe
export class ValidationError extends Schema.TaggedError<ValidationError>()(
  "ValidationError",
  {
    field: Schema.String,
    message: Schema.String,
    details: Schema.optional(Schema.Unknown), // Acceptable for dynamic error details
  }
) {}

export class NotFoundError extends Schema.TaggedError<NotFoundError>()(
  "NotFoundError",
  {
    entity: Schema.String,
    id: Schema.String,
  }
) {}

export class UserNotFoundError extends Schema.TaggedError<UserNotFoundError>()(
  "UserNotFoundError",
  {
    id: Schema.String,
    message: Schema.optional(Schema.String),
  }
) {}

// Union for error types
const AppError = Schema.Union(ValidationError, NotFoundError);
type AppError = typeof AppError.Type;
```

**Benefits:**
- Serializable (can send over network/save to DB)
- Built-in `_tag` for pattern matching
- Custom methods via class
- Sensible default `message` when you don't declare one

### Yieldable Errors

`Schema.TaggedError` creates yieldable errors that can be used directly without `Effect.fail()`:

```typescript
// GOOD: Yieldable errors can be used directly
return error.response.status === 404
  ? UserNotFoundError.make({ id })
  : Effect.die(error);

// REDUNDANT: no need to wrap with Effect.fail
return error.response.status === 404
  ? Effect.fail(UserNotFoundError.make({ id }))
  : Effect.die(error);
```

### Schema.Defect for Unknown Errors

Use `Schema.Defect` to wrap unknown errors from external libraries:

```typescript
class ApiError extends Schema.TaggedError<ApiError>()("ApiError", {
  endpoint: Schema.String,
  statusCode: Schema.Number,
  // Wrap the underlying error from fetch/axios/etc
  error: Schema.Defect,
}) {}

class NetworkError extends Schema.TaggedError<NetworkError>()("NetworkError", {
  message: Schema.String,
  cause: Schema.optional(Schema.Defect),
}) {}

const fetchUser = (id: string) =>
  Effect.tryPromise({
    try: () => fetch(`/api/users/${id}`).then((r) => r.json()),
    catch: (error) =>
      ApiError.make({
        endpoint: `/api/users/${id}`,
        statusCode: 500,
        error, // Wrapped with Schema.Defect
      }),
  });
```

**Schema.Defect handles:**
- JavaScript `Error` instances -> `{ name, message }` objects
- Any unknown value -> string representation
- Serializable for network/storage

### Error Recovery

```typescript
// Catch specific error types
const recovered = pipe(
  riskyOperation,
  Effect.catchTag("NotFoundError", (error) => Effect.succeed(defaultValue))
);

// Catch multiple error types
const recovered2 = pipe(
  riskyOperation,
  Effect.catchTags({
    NotFoundError: (error) => Effect.succeed(defaultValue),
    ValidationError: (error) =>
      Effect.fail(new BadRequestError({ cause: error })),
  })
);

// Catch all errors
const recovered3 = pipe(
  riskyOperation,
  Effect.catchAll((error) => Effect.succeed(fallbackValue))
);

// Transform errors
const transformed = pipe(
  riskyOperation,
  Effect.mapError((error) => new WrappedError({ cause: error }))
);

// Retry with policy
const retried = pipe(
  riskyOperation,
  Effect.retry({
    schedule: Schedule.exponential("100 millis").pipe(
      Schedule.compose(Schedule.recurs(3))
    ),
  })
);
```

### Expected Errors vs Defects

Effect tracks errors in the type system so callers know what can go wrong. But tracking only matters if recovery is possible.

**Use typed errors** for domain failures the caller can handle: validation errors, "not found", permission denied, rate limits.

**Use defects** for unrecoverable situations: bugs and invariant violations.

```typescript
// At app entry: if config fails, nothing can proceed
const main = Effect.gen(function* () {
  const config = yield* loadConfig.pipe(Effect.orDie);
  yield* Effect.log(`Starting on port ${config.port}`);
});
```

### Working with Cause

```typescript
import * as Cause from "effect/Cause";

const handled = pipe(
  Effect.sandbox(riskyEffect),
  Effect.catchAll((cause) =>
    pipe(
      Cause.failureOrCause(cause),
      Either.match({
        onLeft: (expectedError) => handleExpected(expectedError),
        onRight: (unexpectedCause) => handleUnexpected(unexpectedCause),
      })
    )
  )
);
```

## Configuration

### Config with Schema.Config (Recommended)

Use `Schema.Config` for validation instead of `Config.mapOrFail`:

```typescript
import * as Schema from "effect/Schema";
import * as Effect from "effect/Effect";

const Port = Schema.Int.pipe(Schema.between(1, 65535), Schema.brand("Port"));
type Port = typeof Port.Type;

const Environment = Schema.Literal("development", "staging", "production");

const program = Effect.gen(function* () {
  const port = yield* Schema.Config("PORT", Port);
  const env = yield* Schema.Config("ENV", Environment);
  return { port, env };
});
```

**Schema.Config benefits:**
- Automatic type inference from schema
- Rich validation errors
- Reusable schemas across config and runtime validation
- Full Schema transformation power (brands, transforms, refinements)

### Config Service Pattern (Recommended)

Create a config service with a `layer` export:

```typescript
import * as Config from "effect/Config";
import * as Context from "effect/Context";
import * as Effect from "effect/Effect";
import * as Layer from "effect/Layer";
import * as Redacted from "effect/Redacted";

class ApiConfig extends Context.Tag("@app/ApiConfig")<
  ApiConfig,
  {
    readonly apiKey: Redacted.Redacted;
    readonly baseUrl: string;
    readonly timeout: number;
  }
>() {
  static readonly layer = Layer.effect(
    ApiConfig,
    Effect.gen(function* () {
      const apiKey = yield* Config.redacted("API_KEY");
      const baseUrl = yield* Config.string("API_BASE_URL").pipe(
        Config.orElse(() => Config.succeed("https://api.example.com"))
      );
      const timeout = yield* Config.integer("API_TIMEOUT").pipe(
        Config.orElse(() => Config.succeed(30000))
      );

      return ApiConfig.of({ apiKey, baseUrl, timeout });
    })
  );

  // For tests - hardcoded values
  static readonly testLayer = Layer.succeed(
    ApiConfig,
    ApiConfig.of({
      apiKey: Redacted.make("test-key"),
      baseUrl: "https://test.example.com",
      timeout: 5000,
    })
  );
}
```

### Using Redacted for Secrets

Always use `Config.redacted()` for sensitive values:

```typescript
const program = Effect.gen(function* () {
  const apiKey = yield* Config.redacted("API_KEY");

  // Use Redacted.value() to extract
  const headers = {
    Authorization: `Bearer ${Redacted.value(apiKey)}`,
  };

  console.log(apiKey); // Output: <redacted>

  return headers;
});
```

## Error Accumulation

By default, `Effect.zip`, `Effect.all`, and `Effect.forEach` use a **fail-fast** policy — they stop at the first error. When you need to collect all errors (e.g., form validation), use accumulation functions.

### Effect.validate

Like `Effect.zip` but continues even after encountering errors:

```typescript
const result = task1.pipe(
  Effect.validate(task2),
  Effect.validate(task3),
  Effect.validate(task4)
);
// If task2 and task4 fail, BOTH errors are accumulated in a Sequential cause
```

### Effect.validateAll

Like `Effect.forEach` but collects all errors into an array:

```typescript
// Type: Effect<number[], string[], never>
const validated = Effect.validateAll([1, 2, 3, 4, 5], (n) => {
  if (n < 4) return Effect.succeed(n);
  return Effect.fail(`${n} is not less than 4`);
});
// Failure: ["4 is not less than 4", "5 is not less than 4"]
```

### Effect.partition

Split effects into successes and failures without stopping:

```typescript
const [failures, successes] = yield* Effect.partition(
  [1, 2, 3, 4, 5],
  (n) => (n > 3 ? Effect.fail(`Too big: ${n}`) : Effect.succeed(n))
);
// failures: ["Too big: 4", "Too big: 5"]
// successes: [1, 2, 3]
```

## Retry with Conditions

### Retry n Times

```typescript
yield* Effect.retry(task, { times: 5 }); // Retry up to 5 times immediately
```

### Retry Until / While

```typescript
// Stop retrying when condition is met
yield* Effect.retry(task, { until: (error) => error.statusCode === 404 });

// Keep retrying while condition holds
yield* Effect.retry(task, { while: (error) => error.statusCode >= 500 });
```

### retryOrElse — Retry with Fallback

```typescript
const result = yield* Effect.retryOrElse(
  task,
  Schedule.exponential("100 millis").pipe(Schedule.compose(Schedule.recurs(3))),
  (error, _fiberId) => Effect.succeed(fallbackValue)
);
```

