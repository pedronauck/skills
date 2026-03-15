# HttpApi, Platform, and Observability

Schema-driven HTTP APIs, platform services, and tracing/logging practices.

## HttpApi Architecture (Schema-Driven APIs)

Use `HttpApi` to define type-safe, schema-driven API contracts. This replaces manual `HttpClient` usage for defining service boundaries.

### Defining an API

```typescript
import { HttpApi, HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

// Define the API
class UsersApi extends HttpApiGroup.make("users")
  .add(
    HttpApiEndpoint.get("getUser", "/users/:id")
      .addSuccess(Schema.Struct({ id: Schema.Number, name: Schema.String }))
      .addError(Schema.NotFound)
  )
  .add(
    HttpApiEndpoint.post("createUser", "/users")
      .setPayload(Schema.Struct({ name: Schema.String }))
      .addSuccess(Schema.Struct({ id: Schema.Number, name: Schema.String }))
  ) {}

// Export the API definition
export class MyApi extends HttpApi.make("my-api").add(UsersApi) {}
```

### Consuming an API

```typescript
import { HttpApiClient } from "@effect/platform";

const program = Effect.gen(function* () {
  const client = yield* HttpApiClient.make(MyApi, {
    baseUrl: "https://api.example.com",
  });

  // Type-safe method calls
  const user = yield* client.users.getUser({ path: { id: 1 } });
});
```

## Platform Integration

### HTTP Client

```typescript
import * as HttpClient from "@effect/platform/HttpClient";

const fetchUser = (id: string) =>
  pipe(
    HttpClient.get(`https://api.example.com/users/${id}`),
    Effect.flatMap((response) => response.json),
    Effect.flatMap(Schema.decode(User)),
    Effect.scoped
  );
```

### Platform Services

```typescript
import * as NodeContext from "@effect/platform-node/NodeContext";
import * as NodeRuntime from "@effect/platform-node/NodeRuntime";

// Run with Node runtime
NodeRuntime.runMain(program.pipe(Effect.provide(NodeContext.layer)));
```

## Logging & Observability

### Log Functions

```typescript
import * as Effect from "effect/Effect";

yield* Effect.log("Info message");           // INFO level (default)
yield* Effect.logDebug("Debug message");     // DEBUG (hidden by default)
yield* Effect.logInfo("Info message");       // INFO
yield* Effect.logWarning("Warning message"); // WARNING
yield* Effect.logError("Error message");     // ERROR
yield* Effect.logFatal("Fatal message");     // FATAL

// Log multiple messages
yield* Effect.log("msg1", "msg2", "msg3");

// Log with Cause context
yield* Effect.log("Operation failed", Cause.die("Oh no!"));
```

Default logger output format:
```
timestamp=... level=INFO fiber=#0 message="Application started"
```

### Log Levels

By default, DEBUG messages are hidden. Adjust with `Logger.withMinimumLogLevel`:

```typescript
import * as Logger from "effect/Logger";
import * as LogLevel from "effect/LogLevel";

// Enable DEBUG logs for a specific scope
const debugTask = myEffect.pipe(
  Logger.withMinimumLogLevel(LogLevel.Debug)
);

// Available levels (in order): All, Trace, Debug, Info, Warning, Error, Fatal, None
```

### Custom Loggers

Replace the default logger:

```typescript
// Simple console logger
const simpleLogger = Logger.replace(
  Logger.defaultLogger,
  Logger.make(({ message }) => console.log(message))
);

const program = myEffect.pipe(Effect.provide(simpleLogger));

// Pretty logger (built-in)
const pretty = myEffect.pipe(Effect.provide(Logger.pretty));

// JSON logger (built-in)
const json = myEffect.pipe(Effect.provide(Logger.json));
```

### Log Annotations

Add structured metadata to log entries:

```typescript
// Annotate specific scope
const annotated = myEffect.pipe(
  Effect.annotateLogs("userId", userId),
  Effect.annotateLogs("requestId", requestId)
);
// Output: timestamp=... level=INFO ... userId=abc123 requestId=xyz message="..."

// Annotate with record
const annotated2 = myEffect.pipe(
  Effect.annotateLogs({ module: "auth", action: "login" })
);
```

### Log Spans (Timing)

Measure how long a section takes:

```typescript
const timed = myEffect.pipe(Effect.withLogSpan("fetchUser"));
// Output: timestamp=... level=INFO ... message="Done" span=fetchUser=150ms
```

### Tracing & Spans

```typescript
// Add OpenTelemetry-compatible spans
const traced = pipe(
  fetchUser(userId),
  Effect.withSpan("fetch-user", {
    attributes: { userId }
  }),
  Effect.tap((user) => Effect.logInfo("User fetched", { user: user.email }))
);

// Annotate the current span
yield* Effect.annotateCurrentSpan("result.count", results.length);

// Nested spans
const program = Effect.gen(function* () {
  const user = yield* fetchUser(id).pipe(Effect.withSpan("fetch-user"));
  const orders = yield* fetchOrders(user.id).pipe(Effect.withSpan("fetch-orders"));
  return { user, orders };
}).pipe(Effect.withSpan("get-user-with-orders"));
```

### OpenTelemetry Integration

```typescript
import { NodeSdk } from "@effect/opentelemetry";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";

const TracingLayer = NodeSdk.layer(() => ({
  resource: { serviceName: "my-service" },
  spanProcessor: new BatchSpanProcessor(new OTLPTraceExporter()),
}));

const main = program.pipe(Effect.provide(TracingLayer));
```

