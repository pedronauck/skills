# Quality, Tooling, and Further Reading

Anti-patterns, pitfalls, package recommendations, validation checklist, CLI tooling, and resources.

> **See also**: [`error-handling-patterns.md`](./error-handling-patterns.md) for comprehensive error type patterns (Data.TaggedError, Schema.TaggedError), [`library-development-patterns.md`](./library-development-patterns.md) for critical forbidden patterns (no try-catch in Effect.gen, no type assertions, mandatory `return yield*`), [`testing-patterns.md`](./testing-patterns.md) for testing with `assert` (not `expect`), [`pattern-matching.md`](./pattern-matching.md) for mandatory `Match` usage over `switch`/`if-else` on `_tag`, and [`data-types.md`](./data-types.md) for mandatory Effect data types (Option, Either, Duration, DateTime, BigDecimal, etc.).

## Anti-Patterns to Avoid

```typescript
// BAD: Don't use bare try/catch
try {
  await fetch(url);
} catch (e) {
  // Lost error tracking
}

// GOOD: Use Effect.tryPromise
Effect.tryPromise({
  try: () => fetch(url),
  catch: (error) => new NetworkError({ message: String(error), cause: error }),
});

// BAD: Don't use Effect.runSync inside Effects
Effect.gen(function* () {
  Effect.runSync(sideEffect); // Loses error tracking, breaks composition
});

// GOOD: Yield effects
Effect.gen(function* () {
  yield* sideEffect;
});

// BAD: Don't use unknown in error channel
Effect.Effect<User, unknown, Database>;

// GOOD: Explicit error types
Effect.Effect<User, UserNotFoundError | DatabaseError, Database>;

// BAD: Don't mix gen and pipe unnecessarily
Effect.gen(function* () {
  const result = yield* pipe(Effect.succeed(1), Effect.map((x) => x + 1));
});

// GOOD: Use gen OR pipe, not both
Effect.gen(function* () {
  const value = yield* Effect.succeed(1);
  return value + 1;
});
// OR
pipe(
  Effect.succeed(1),
  Effect.map((x) => x + 1)
);

// BAD: switch/if-else on _tag (no exhaustiveness — use Match instead)
switch (status._tag) {
  case "Pending": return "...";
  case "Approved": return "...";
  // Forgot "Rejected" — no compile error!
}

// GOOD: Use Match with exhaustive checking
import * as Match from "effect/Match";
const msg = Match.value(status).pipe(
  Match.tag("Pending", () => "..."),
  Match.tag("Approved", () => "..."),
  Match.tag("Rejected", () => "..."),
  Match.exhaustive
);

// BAD: Don't use .pipe() on non-pipeable values
const bad = someValue.pipe(transform);

// GOOD: Use pipe function
const good = pipe(someValue, transform);

// BAD: Don't run effects inside effects without yield/flatMap
const bad = Effect.gen(function* () {
  Effect.runPromise(sideEffect); // Loses error tracking
  return result;
});

// GOOD: Use yield* or flatMap
const good = Effect.gen(function* () {
  yield* sideEffect;
  return result;
});

// BAD: Don't mutate state
const bad = Effect.sync(() => {
  state.count++;
  return state;
});

// GOOD: Create new immutable values
const good = Effect.sync(() => ({
  ...state,
  count: state.count + 1,
}));

// BAD: Don't forget to provide layers
const bad = Effect.runPromise(program);

// GOOD: Always provide required layers
const good = Effect.runPromise(program.pipe(Effect.provide(AppLayer)));
```

## Avoiding Common Pitfalls

```typescript
// Use Clock service instead of Date.now() for testability
const program = Effect.gen(function* () {
  const now = yield* Clock.currentTimeMillis;
  return now;
});

// Use specific types, not Schema.Unknown
class Response extends Schema.Class<Response>("Response")({
  data: User, // Type-safe
}) {}
```

### Data Type Anti-Patterns (see [`data-types.md`](./data-types.md) for complete reference)

```typescript
// BAD: null/undefined for optional values
const email: string | null = user.email ?? null;
// GOOD: Option
const email: Option.Option<string> = Option.fromNullable(user.email);

// BAD: raw numbers for time
const timeout = 5000; // what unit? millis? seconds?
// GOOD: Duration — self-documenting and type-safe
const timeout = Duration.seconds(5);

// BAD: Date for date/time operations
const now = new Date();
// GOOD: DateTime — immutable, timezone-aware, Effect-integrated
const now = yield* DateTime.now; // uses Clock service (testable)

// BAD: floating-point for money
const total = 0.1 + 0.2; // 0.30000000000000004
// GOOD: BigDecimal — exact decimal arithmetic
const total = BigDecimal.sum(
  BigDecimal.unsafeFromString("0.1"),
  BigDecimal.unsafeFromString("0.2")
); // exactly 0.3

// BAD: raw strings for secrets
const apiKey = process.env.API_KEY!;
console.log(apiKey); // accidentally logs secret
// GOOD: Redacted — safe from accidental logging
const apiKey = Redacted.make(process.env.API_KEY!);
console.log(apiKey); // logs "<redacted>"
```

## Package Recommendations

Essential Effect ecosystem packages:

```json
{
  "dependencies": {
    "effect": "latest"
  },
  "devDependencies": {
    "@effect/language-service": "latest",
    "@effect/vitest": "latest"
  },
  "optionalDependencies": {
    "@effect/platform": "latest",
    "@effect/platform-node": "latest",
    "@effect/sql": "for database",
    "@effect/rpc": "for RPC",
    "@effect/cli": "for CLIs",
    "@effect/opentelemetry": "for tracing"
  }
}
```

## Validation Checklist

Before finishing a task involving Effect-TS:

- [ ] Effect Language Service installed and configured
- [ ] TypeScript `strict` and `exactOptionalPropertyTypes` enabled
- [ ] Module system configured correctly for project type (bundler vs NodeNext)
- [ ] Imports use `import * as Module from "effect/Module"` pattern
- [ ] `Effect.gen` used for complex logic, `pipe` for linear transformations
- [ ] `Effect.fn` for public API, `Effect.fnUntraced` for performance-critical internals
- [ ] `Match` used for all branching over tagged unions (`_tag`) — no `switch`/`if-else` on `_tag`
- [ ] `Match.exhaustive` used to ensure all cases are handled at compile time
- [ ] Branded types used for all domain primitives (IDs, Emails, etc.)
- [ ] Schemas defined for all external data
- [ ] Errors use appropriate pattern: `Data.TaggedError` (discrimination), `Data.Error` (simple), or `Schema.TaggedError` (serializable)
- [ ] Unknown errors wrapped with `Schema.Defect`
- [ ] No `any` or `unknown` in error channels
- [ ] No `as any`, `as never`, or `as unknown` type assertions
- [ ] No try-catch inside `Effect.gen` — use `Effect.exit` instead
- [ ] `return yield*` used for terminal effects (`Effect.fail`, `Effect.interrupt`)
- [ ] Services organized as Context.Tag with static layer property
- [ ] Layer memoization considered (store parameterized layers in constants)
- [ ] `Option` used for optional values (not `null | undefined`)
- [ ] `Either` used for sync success/failure (not ad-hoc `{ ok, error }`)
- [ ] `Duration` used for time values (not raw numbers in ms)
- [ ] `DateTime` used for date/time operations (not `Date`)
- [ ] `BigDecimal` used for financial/precise arithmetic (not floating-point `number`)
- [ ] `Redacted` used for all secrets (API keys, passwords, tokens)
- [ ] `Data.struct`/`Data.Class` for structural equality where needed
- [ ] `HashSet` used when set structural equality is needed (not native `Set`)
- [ ] `Chunk` used for stream data and repeated concatenation
- [ ] Clock.currentTimeMillis used instead of Date.now() for testability
- [ ] Resources properly managed with `Effect.acquireRelease` or `Effect.scoped`
- [ ] Tests use @effect/vitest with `assert` (not `expect`) for `it.effect`
- [ ] Tests use `it.effect`, `it.scoped`, `it.live` appropriately
- [ ] Immutable data structures used throughout
- [ ] Proper Layer composition and provision to programs
- [ ] Run `pnpm run typecheck` and `pnpm run test`

## Effect Solutions CLI

The Effect Solutions CLI provides curated best practices. Use it before working on Effect code:

```bash
pnpm exec effect-solutions list              # List all topics
pnpm exec effect-solutions show <slug...>    # Read topics
pnpm exec effect-solutions search <term>     # Search by keyword
```

## Additional Resources

- Official Documentation: https://effect.website/docs
- API Reference: https://effect-ts.github.io/effect/
- Discord Community: https://discord.gg/effect-ts
- Example Repository: https://github.com/Effect-TS/examples
