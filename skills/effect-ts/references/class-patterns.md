# Effect-TS Service Pattern (Context.Tag)

This document contains the canonical pattern for creating Effect-TS services using `Context.Tag`. Use this when refactoring OOP classes or creating new services that need dependency injection.

## When to Apply

- Refactoring existing OOP classes to Effect-TS
- Creating new services that need dependency injection
- Building testable, composable infrastructure code

## Import Convention

Always use the `import * as` pattern for Effect modules:

```typescript
import * as Context from "effect/Context";
import * as Effect from "effect/Effect";
import * as Layer from "effect/Layer";
import * as Schema from "effect/Schema";
import { pipe } from "effect/Function";
```

## Service Architecture Overview

### Key Concepts

1. **Context.Tag** - Declares a service interface with a unique identifier
2. **Layer** - Provides a service implementation that can be composed
3. **Effect.fn** - Creates traced, named functions for observability
4. **Static methods** - Organize service factories and helpers within the service class

### Service Principles

- **Service methods should have no dependencies (`R = never`)**. Dependencies are handled via Layer composition.
- **Use readonly properties**. Services should not expose mutable state.
- **Layer naming:** camelCase with `Layer` suffix: `layer`, `testLayer`, `postgresLayer`.

## Complete Service Pattern

### 1. Define Error Types with Schema.TaggedError

```typescript
/**
 * Custom error for HTTP failures
 * Schema.TaggedError provides: serialization, _tag for pattern matching, yieldable errors
 */
export class HttpError extends Schema.TaggedError<HttpError>()("HttpError", {
  statusCode: Schema.Number,
  url: Schema.String,
  message: Schema.String,
}) {}

/**
 * Use Schema.Defect for wrapping unknown errors from external libraries
 */
export class NetworkError extends Schema.TaggedError<NetworkError>()(
  "NetworkError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Defect),
  }
) {}

export class ValidationError extends Schema.TaggedError<ValidationError>()(
  "ValidationError",
  {
    message: Schema.String,
    details: Schema.optional(Schema.Unknown), // Acceptable for dynamic error details
  }
) {}
```

### 2. Define Configuration Service

```typescript
/**
 * Configuration type - all properties readonly
 */
type MyServiceConfigType = {
  readonly baseUrl: string;
  readonly maxRetries: number;
  readonly timeout: number;
};

/**
 * Configuration service tag
 * Use @path/ServiceName pattern for unique identifiers
 */
export class MyServiceConfig extends Context.Tag("@myapp/MyServiceConfig")<
  MyServiceConfig,
  MyServiceConfigType
>() {
  /**
   * Layer factory with defaults
   * Use Layer.succeed for simple config layers
   */
  static readonly layer = (config: {
    baseUrl: string;
    maxRetries?: number;
    timeout?: number;
  }) =>
    Layer.succeed(MyServiceConfig, {
      baseUrl: config.baseUrl,
      maxRetries: config.maxRetries ?? 3,
      timeout: config.timeout ?? 30000,
    });
}
```

### 3. Extract Helper Functions as Static Methods

Use static methods in a helper class instead of module-scoped functions. This improves organization and makes utilities easier to test.

**When to use a separate helper class:**
- Pure utility functions that don't depend on service-specific context
- Functions that might be reused across multiple services
- Constants and configuration values
- HTTP request builders, validators, parsers

**When to put methods directly on the service class:**
- Service method factories (always go on the service class)
- Methods that are tightly coupled to the service interface

```typescript
// ============================================================================
// Helper Types
// ============================================================================

type ServiceDeps = {
  config: MyServiceConfigType;
  requests: ReturnType<typeof MyServiceHelpers.createRequestHelpers>;
  retry: ReturnType<typeof MyServiceHelpers.createRetryExecutor>;
  logger: Logger;
};

type HttpResponse = { status: number; body: unknown };
type AnySchema = Schema.Schema.AnyNoContext;
type RetryServiceType = Context.Tag.Service<typeof RetryService>;
type TimeServiceType = Context.Tag.Service<typeof TimeService>;

// ============================================================================
// MyServiceHelpers - Static Utility Methods
// ============================================================================

/**
 * Static helper methods for service utilities
 * Use static methods instead of module-scoped functions for better organization
 */
class MyServiceHelpers {
  /**
   * Constants as static readonly properties
   */
  static readonly RETRIABLE_STATUS_CODES = [429, 502, 503, 504] as const;

  /**
   * Pure helper function - no Effect context required
   */
  static validateResponse(
    status: number,
    url: string,
    expectedStatuses: number[]
  ): Effect.Effect<void, HttpError> {
    if (!expectedStatuses.includes(status)) {
      return Effect.fail(
        new HttpError({ message: `HTTP ${status}`, statusCode: status, url })
      );
    }
    return Effect.void;
  }

  /**
   * Create HTTP request with error handling
   */
  static createHttpRequest(
    fetchFn: () => Promise<{ status: number; body: unknown }>,
    url: string
  ): Effect.Effect<HttpResponse, HttpError | NetworkError> {
    return pipe(
      Effect.tryPromise({
        try: fetchFn,
        catch: (error): NetworkError =>
          new NetworkError({ message: "Network request failed", cause: error }),
      }),
      Effect.flatMap((res) => {
        if (this.isServerError(res.status)) {
          return Effect.fail(
            new HttpError({
              message: `HTTP ${res.status}: Request failed`,
              statusCode: res.status,
              url,
            })
          );
        }
        return Effect.succeed({ status: res.status, body: res.body });
      })
    );
  }

  /**
   * Check if HTTP status code is a server error (5xx)
   */
  static isServerError(status: number): boolean {
    return status >= 500 && status < 600;
  }

  /**
   * Parse response data with schema validation
   */
  static parseWithSchema<TSchema extends AnySchema>(
    schema: TSchema,
    data: unknown,
    message: string
  ): Effect.Effect<
    Schema.Schema.Type<TSchema>,
    ValidationError,
    Schema.Schema.Context<TSchema>
  > {
    return Effect.gen(function* () {
      const parsedInput = yield* Effect.try({
        try: () => (typeof data === "string" ? JSON.parse(data) : data),
        catch: (error) =>
          new ValidationError({
            message: "Failed to parse JSON response",
            details: {
              originalError:
                error instanceof Error ? error.message : String(error),
            },
          }),
      });

      return yield* Schema.decodeUnknown(schema, { onExcessProperty: "error" })(
        parsedInput
      ).pipe(
        Effect.mapError(
          (error) => new ValidationError({ message, details: error })
        )
      );
    });
  }

  /**
   * Create retry executor factory
   */
  static createRetryExecutor(
    config: MyServiceConfigType,
    retryService: RetryServiceType,
    timeService: TimeServiceType
  ) {
    return <A>(
      request: Effect.Effect<A, HttpError | NetworkError>
    ): Effect.Effect<A, HttpError | NetworkError> => {
      const schedule = timeService.exponentialBackoff(
        config.baseDelayMs,
        2,
        config.maxDelayMs
      );
      return retryService.retryWithPredicate(request, {
        schedule,
        maxAttempts: config.maxRetries + 1,
        shouldRetry: this.shouldRetryError.bind(this),
      });
    };
  }

  /**
   * Check if error should be retried
   */
  static shouldRetryError(error: HttpError | NetworkError): boolean {
    if (error instanceof NetworkError) return true;
    if (error instanceof HttpError) {
      return (
        this.isServerError(error.statusCode) ||
        this.RETRIABLE_STATUS_CODES.includes(
          error.statusCode as (typeof this.RETRIABLE_STATUS_CODES)[number]
        )
      );
    }
    return false;
  }

  /**
   * Create request helper bound to a client instance
   */
  static createRequestHelpers(client: HttpClient) {
    return {
      get: (url: string) => this.createHttpRequest(() => client.get(url), url),
      post: (url: string, body: unknown) =>
        this.createHttpRequest(() => client.post(url, body), url),
    };
  }
}
```

### 4. Service Method Factories as Static Methods

Use `Effect.fn` for traced, named functions. Define service method factories as static methods on the service class:

```typescript
// ============================================================================
// Main Service
// ============================================================================

/**
 * Service interface - all methods readonly, return Effect with R = never
 * Service methods should have no dependencies in R channel
 */
export class MyService extends Context.Tag("@myapp/MyService")<
  MyService,
  {
    readonly fetchItems: (
      categoryId: string
    ) => Effect.Effect<Item[], HttpError | NetworkError | ValidationError>;
    readonly updateItem: (
      itemId: string,
      data: ItemUpdate
    ) => Effect.Effect<void, HttpError | NetworkError | ValidationError>;
  }
>() {
  /**
   * Factory for fetchItems method
   * Effect.fn provides: call-site tracing, stack traces, telemetry spans
   * Static methods keep factories organized within the service class
   */
  static createFetchItems(deps: ServiceDeps) {
    return Effect.fn("MyService.fetchItems")(function* (categoryId: string) {
      const { config, requests, logger } = deps;

      yield* Effect.sync(() => logger.info("Fetching items", { categoryId }));

      const url = `${config.baseUrl}/api/items?category=${encodeURIComponent(categoryId)}`;
      const response = yield* requests.get(url);

      yield* MyServiceHelpers.validateResponse(response.status, url, [200]);

      const wrappedResponse = yield* MyServiceHelpers.parseWithSchema(
        ItemsResponseSchema,
        response.body,
        "Failed to parse items response"
      );
      return wrappedResponse.data.items;
    });
  }

  /**
   * Factory for updateItem method
   */
  static createUpdateItem(deps: ServiceDeps) {
    return Effect.fn("MyService.updateItem")(function* (
      itemId: string,
      data: ItemUpdate
    ) {
      const { config, requests, logger } = deps;

      yield* Effect.sync(() => logger.debug("Updating item", { itemId, data }));

      const url = `${config.baseUrl}/api/items/${encodeURIComponent(itemId)}`;
      const response = yield* requests.patch(url, data);

      yield* MyServiceHelpers.validateResponse(response.status, url, [
        200, 204,
      ]);
      return yield* Effect.void;
    });
  }
```

### 5. Service Layer Implementation

Complete the service class with layer implementation using static methods:

```typescript
  /**
   * Live implementation layer
   * Use Layer.effect when construction requires Effects
   */
  static readonly layer = Layer.effect(
    MyService,
    Effect.gen(function* () {
      // Yield dependencies from context
      const config = yield* MyServiceConfig;
      const retryService = yield* RetryService;
      const timeService = yield* TimeService;

      // Create internal dependencies
      const client = new HttpClient(config.baseUrl);
      const logger = getLogger(["myapp", "my-service"]);

      // Build deps object for factories
      const deps: ServiceDeps = {
        config,
        requests: MyServiceHelpers.createRequestHelpers(client),
        retry: MyServiceHelpers.createRetryExecutor(
          config,
          retryService,
          timeService
        ),
        logger,
      };

      // Return service implementation using static factory methods
      return MyService.of({
        fetchItems: MyService.createFetchItems(deps),
        updateItem: MyService.createUpdateItem(deps),
      });
    })
  );

  /**
   * Test layer - use Layer.succeed for synchronous test implementations
   */
  static readonly testLayer = Layer.succeed(MyService, {
    fetchItems: () => Effect.succeed([]),
    updateItem: () => Effect.void,
  });
}
```

## Service-Driven Development

Start by sketching leaf service tags without implementations. This lets you write real TypeScript for higher-level services that type-checks even before leaf services are runnable:

```typescript
// Leaf services: contracts only
class Users extends Context.Tag("@app/Users")<
  Users,
  { readonly findById: (id: UserId) => Effect.Effect<User> }
>() {}

class Tickets extends Context.Tag("@app/Tickets")<
  Tickets,
  {
    readonly issue: (
      eventId: EventId,
      userId: UserId
    ) => Effect.Effect<Ticket>;
  }
>() {}

// Higher-level service: orchestrates leaf services
class Events extends Context.Tag("@app/Events")<
  Events,
  {
    readonly register: (
      eventId: EventId,
      userId: UserId
    ) => Effect.Effect<Registration>;
  }
>() {
  static readonly layer = Layer.effect(
    Events,
    Effect.gen(function* () {
      const users = yield* Users;
      const tickets = yield* Tickets;

      const register = Effect.fn("Events.register")(function* (
        eventId: EventId,
        userId: UserId
      ) {
        const user = yield* users.findById(userId);
        const ticket = yield* tickets.issue(eventId, userId);
        // ... orchestration logic
      });

      return Events.of({ register });
    })
  );
}
```

## Layer Composition

### Basic Composition

```typescript
// ============================================================================
// Composed Layer Exports
// ============================================================================

/**
 * Store parameterized layers in constants for memoization
 * Effect automatically memoizes layers by reference identity
 */
const RetryLayerWithTime = RetryLayer.pipe(Layer.provide(TimeLayer));

/**
 * Combined dependencies layer
 */
const DependenciesLayer = Layer.merge(RetryLayerWithTime, TimeLayer);

/**
 * Service layer with internal dependencies satisfied
 * Requires: MyServiceConfig
 */
export const MyServiceLayer = MyService.layer.pipe(
  Layer.provide(DependenciesLayer)
);

/**
 * Fully configured layer factory
 * All dependencies satisfied - ready to use
 */
export const makeMyServiceLayer = (config: {
  baseUrl: string;
  maxRetries?: number;
  timeout?: number;
}) =>
  Layer.merge(
    MyServiceLayer.pipe(Layer.provide(MyServiceConfig.layer(config))),
    TimeLayer // Include if service methods need TimeService at runtime
  );
```

### Layer Memoization (Critical)

Effect automatically memoizes layers by reference identity. When the same layer instance appears multiple times in your dependency graph, it's constructed only once.

```typescript
// BAD: calling the constructor twice creates two instances
const badAppLayer = Layer.merge(
  UserRepo.layer.pipe(
    Layer.provide(
      Postgres.layer({ url: "postgres://localhost/mydb", poolSize: 10 })
    )
  ),
  OrderRepo.layer.pipe(
    Layer.provide(
      Postgres.layer({ url: "postgres://localhost/mydb", poolSize: 10 })
    ) // Different reference!
  )
);
// Creates TWO connection pools (20 connections total)

// GOOD: store the layer in a constant first
const postgresLayer = Postgres.layer({
  url: "postgres://localhost/mydb",
  poolSize: 10,
});

const goodAppLayer = Layer.merge(
  UserRepo.layer.pipe(Layer.provide(postgresLayer)),
  OrderRepo.layer.pipe(Layer.provide(postgresLayer)) // Same reference!
);
// Single connection pool shared by both repos
```

**The rule:** When using parameterized layer constructors, always store the result in a module-level constant before using it in multiple places.

### App-Level Layer Composition

```typescript
// Layers compose naturally
export const AppLayer = Layer.mergeAll(
  ConfigServiceLive,
  LoggerServiceLive
).pipe(
  Layer.provideMerge(DatabaseServiceLive),
  Layer.provideMerge(CacheServiceLive)
);

// Provide once at the entry point
const main = program.pipe(Effect.provide(AppLayer));

Effect.runPromise(main);
```

**Why provide once at the top?**
- Clear dependency graph: all wiring in one place
- Easier testing: swap `AppLayer` for `testLayer`
- No hidden dependencies: effects declare what they need via types

### Using Services in Programs

```typescript
// Access service in Effect.gen
const program = Effect.gen(function* () {
  const db = yield* DatabaseService;
  const results = yield* db.query("SELECT * FROM users");
  return results;
});

// Type: Effect.Effect<unknown[], DatabaseError, DatabaseService>
```

## ManagedRuntime Pattern (Advanced)

Use `ManagedRuntime` when sharing services across multiple Effect runs:

```typescript
import * as Runtime from "effect/Runtime";

const AppRuntime = Runtime.ManagedRuntime.make(AppLayer);

// Reuse runtime across requests
app.get("/api/users", async (req, res) => {
  const result = await AppRuntime.runPromise(
    UserController.getUsers(req.query)
  );
  res.json(result);
});

await AppRuntime.dispose();
```

## Type Aliases

```typescript
// ============================================================================
// Type Aliases
// ============================================================================

/**
 * Type alias for service interface
 * Use when typing mock objects or partial implementations
 */
export type MyServiceType = Context.Tag.Service<typeof MyService>;
```

## Usage in Tests

```typescript
import { Effect } from "effect";
import { describe, expect, it } from "vitest";
import { MyService, makeMyServiceLayer } from "./my-service";

const createTestLayer = () =>
  makeMyServiceLayer({
    baseUrl: "http://localhost:3000",
    maxRetries: 0, // Fast tests
  });

describe("MyService", () => {
  it("should fetch items", async () => {
    const result = await Effect.runPromise(
      Effect.gen(function* () {
        const service = yield* MyService;
        return yield* service.fetchItems("category-1");
      }).pipe(Effect.provide(createTestLayer()))
    );

    expect(result).toEqual([
      /* expected items */
    ]);
  });

  it("should handle errors", async () => {
    const result = await Effect.runPromise(
      Effect.gen(function* () {
        const service = yield* MyService;
        return yield* service.fetchItems("invalid");
      }).pipe(Effect.provide(createTestLayer()), Effect.either)
    );

    expect(result._tag).toBe("Left");
    if (result._tag === "Left") {
      expect(result.left).toBeInstanceOf(HttpError);
    }
  });
});
```

## Usage with Test Layer

```typescript
// For unit tests that don't need real HTTP
it("should use test layer", async () => {
  await Effect.runPromise(
    Effect.gen(function* () {
      const service = yield* MyService;
      const items = yield* service.fetchItems("any");
      expect(items).toEqual([]); // testLayer returns empty array
    }).pipe(Effect.provide(MyService.testLayer))
  );
});
```

## Validation Checklist

When refactoring a class to this pattern, verify:

- [ ] Imports use `import * as Module from "effect/Module"` pattern
- [ ] Error types use `Schema.TaggedError` with descriptive fields
- [ ] Unknown errors wrapped with `Schema.Defect`
- [ ] Config service uses `Context.Tag` with `@path/ServiceName` identifier
- [ ] Config layer uses `Layer.succeed` with sensible defaults
- [ ] Helper functions organized as static methods in a helper class (not module-scoped)
- [ ] Service method factories defined as static methods on the service class
- [ ] Service methods use `Effect.fn("ServiceName.methodName")` for tracing
- [ ] Service interface has `readonly` properties
- [ ] Service methods return `Effect.Effect<T, E>` with `R = never`
- [ ] Live layer uses `Layer.effect` with `Effect.gen`
- [ ] Layer implementation calls static factory methods (e.g., `MyService.createFetchItems(deps)`)
- [ ] Test layer uses `Layer.succeed` with mock implementations
- [ ] Parameterized layers stored in constants (memoization)
- [ ] Layer composition uses `Layer.merge` and `Layer.provide`
- [ ] Type alias exported for external typing needs

## Anti-Patterns to Avoid

```typescript
// BAD: Don't use OOP inheritance
class MyService extends BaseService {}

// BAD: Don't use module-scoped functions (use static methods instead)
const validateResponse = (status: number) => {
  /* ... */
};
const createFetchItems = (deps: ServiceDeps) => {
  /* ... */
};

// GOOD: Use static methods in helper class and service class
class MyServiceHelpers {
  static validateResponse(status: number) {
    /* ... */
  }
}
class MyService {
  static createFetchItems(deps: ServiceDeps) {
    /* ... */
  }
}

// BAD: Don't use bare try/catch
try {
  await fetch(url);
} catch (e) {}

// BAD: Don't use Effect.runSync inside Effects
Effect.gen(function* () {
  Effect.runSync(sideEffect); // Loses error tracking
});

// BAD: Don't create layers inline (breaks memoization)
Layer.merge(
  Service1.layer.pipe(Layer.provide(Postgres.layer({ url }))),
  Service2.layer.pipe(Layer.provide(Postgres.layer({ url }))) // Different instance!
);

// BAD: Don't use unknown in error channel
Effect.Effect<User, unknown, Database>;

// BAD: Don't mix gen and pipe unnecessarily
Effect.gen(function* () {
  const result = yield* pipe(
    Effect.succeed(1),
    Effect.map((x) => x + 1)
  );
});
```

## Reference Implementation

See `/packages/looper/src/data/api-client/api-client.ts` for a complete reference implementation of this pattern.
