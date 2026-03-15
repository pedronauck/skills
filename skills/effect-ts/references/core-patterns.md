# Effect-TS Core Patterns

This guide was split into smaller, focused references for easier navigation and maintenance.

## Reading Order

1. [Foundations](./foundations.md)
2. [Effect Construction and Style](./construction-and-style.md)
3. [Control Flow and Runtime](./control-flow-and-runtime.md)
4. [Schema, Errors, and Configuration](./schema-errors-config.md)
5. [Schema Transforms and Filters](./schema-transforms-and-filters.md)
6. [Data Types (comprehensive)](./data-types.md) — Option, Either, Data, Exit, Cause, Duration, DateTime, BigDecimal, Chunk, HashSet, Redacted
7. [Data Types and Testing (quick ref)](./data-and-testing.md) — Option/Either/Array quick ref + testing setup
8. [Concurrency and Resource Management](./concurrency-and-resources.md)
9. [Class Patterns](./class-patterns.md) — Context.Tag service pattern, layers, memoization, testing
10. [Streams Deep Dive](./streams-deep-dive.md) — Creating, operations, grouping, partitioning, broadcasting, buffering, throttling, error handling
11. [Sink](./sink.md) — Creating sinks, collecting, folding, operations, concurrency, leftovers, transduce
12. [Batching and Caching](./batching-and-caching.md)
13. [HttpApi, Platform, and Observability](./api-platform-observability.md)
14. [Pattern Matching](./pattern-matching.md)
15. [Quality, Tooling, and Further Reading](./quality-tooling-and-resources.md)

### Official Effect-TS Patterns (from effect-smol)

16. [Error Handling Patterns](./error-handling-patterns.md) — Data.TaggedError, Data.Error, Schema.TaggedError (serializable), forbidden patterns (no try-catch in Effect.gen), `return yield*` mandate, error composition with union types
17. [Library Development Patterns](./library-development-patterns.md) — Forbidden patterns (no type assertions), Effect.gen vs Effect.fn vs Effect.fnUntraced selection guide, resource management, layer composition, progressive implementation
18. [Testing Patterns](./testing-patterns.md) — @effect/vitest with `assert` (not `expect`), TestClock, forbidden test patterns, assertion API reference, service mocking, test organization

## Topic Map

- Project setup and imports: [Foundations](./foundations.md)
- Building and composing effects: [Effect Construction and Style](./construction-and-style.md)
- Control flow, loops, running effects, ManagedRuntime: [Control Flow and Runtime](./control-flow-and-runtime.md)
- Schema modeling, errors, config, error accumulation, retry: [Schema, Errors, and Configuration](./schema-errors-config.md)
- Schema.transform, Schema.filter, built-in refinements: [Schema Transforms and Filters](./schema-transforms-and-filters.md)
- All data types (Option, Either, Data, Exit, Cause, Duration, DateTime, BigDecimal, Chunk, HashSet, Redacted): [Data Types](./data-types.md)
- Option/Either quick ref, arrays, and tests: [Data Types and Testing](./data-and-testing.md)
- Concurrency, Scope, finalizers, resources: [Concurrency and Resource Management](./concurrency-and-resources.md)
- Context.Tag service pattern, layers, memoization, dependency injection: [Class Patterns](./class-patterns.md)
- Creating, transforming, consuming streams, grouping, partitioning, broadcasting, buffering, throttling: [Streams Deep Dive](./streams-deep-dive.md)
- Sink constructors, collecting, folding, operations, concurrency, leftovers, transduce: [Sink](./sink.md)
- Request batching, N+1, effect caching: [Batching and Caching](./batching-and-caching.md)
- HttpApi, platform services, logging, tracing, OpenTelemetry: [HttpApi, Platform, and Observability](./api-platform-observability.md)
- Pattern matching, Match.type, Match.value, Match.tag, exhaustive checks: [Pattern Matching](./pattern-matching.md)
- Anti-patterns and checklist: [Quality, Tooling, and Further Reading](./quality-tooling-and-resources.md)
- Error types (Data.TaggedError, Schema.TaggedError), error composition, recovery: [Error Handling Patterns](./error-handling-patterns.md)
- Forbidden patterns, Effect.fn vs Effect.fnUntraced, development workflow: [Library Development Patterns](./library-development-patterns.md)
- Testing with assert, TestClock, service mocking, test organization: [Testing Patterns](./testing-patterns.md)
