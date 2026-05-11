# Pattern Matching with `effect/Match`

Type-safe, exhaustive pattern matching for discriminated unions, tagged types, and mixed-type dispatch. **Mandatory** for all branching over tagged unions and multi-type values — replaces `switch`, `if/else` chains, and manual `_tag` checks.

> Official docs: https://effect.website/docs/code-style/pattern-matching

## Why Pattern Matching Is Required

```typescript
// BAD: Manual switch on _tag — no exhaustiveness checking
switch (event._tag) {
  case "Success": return event.data;
  case "Error": return event.error;
  // Forgot "Pending" — no compile error!
}

// BAD: if/else chains on _tag — verbose, no exhaustiveness
if (event._tag === "Success") { return event.data; }
else if (event._tag === "Error") { return event.error; }
// Forgot "Pending" — no compile error!

// GOOD: Match.exhaustive — compiler error if any case is missing
const handle = Match.type<Event>().pipe(
  Match.tag("Success", (e) => e.data),
  Match.tag("Error", (e) => e.error),
  Match.tag("Pending", () => "loading..."),
  Match.exhaustive // TS error if any _tag variant is missing
);
```

## When to Use Match

| Scenario | Use Match? | Pattern |
|---|---|---|
| Branching over `_tag` discriminated unions | **Always** | `Match.tag` + `Match.exhaustive` |
| Branching over `Schema.Union` / `Schema.TaggedClass` types | **Always** | `Match.tag` or `Match.valueTags` |
| Dispatching over `string \| number \| boolean` etc. | **Always** | `Match.when` with predicates |
| Handling `Exit` / `Option` / `Either` variants | **Always** | `Match.tag` |
| Simple `if (x) return a; return b;` | No | Plain `if` is fine |
| Single boolean check | No | Plain `if` is fine |

## Creating Matchers

### `Match.type<T>()` — Matcher from a Type (returns a function)

```typescript
import { Match } from "effect";

// Creates a reusable matcher function
const handleInput = Match.type<string | number>().pipe(
  Match.when(Match.number, (n) => `number: ${n}`),
  Match.when(Match.string, (s) => `string: ${s}`),
  Match.exhaustive
);

handleInput(42);      // "number: 42"
handleInput("hello"); // "string: hello"
```

### `Match.value(v)` — Matcher from a Value (evaluates immediately)

```typescript
import { Match } from "effect";

const input = { name: "John", age: 30 };

const result = Match.value(input).pipe(
  Match.when({ name: "John" }, (user) => `${user.name} is ${user.age}`),
  Match.orElse(() => "Unknown user")
);
// result = "John is 30"
```

### `Match.withReturnType<T>()` — Enforce Return Type

Must be the **first** operator in the pipeline. Ensures all branches return the same type.

```typescript
import { Match } from "effect";

const match = Match.type<{ a: number } | { b: string }>().pipe(
  Match.withReturnType<string>(),
  Match.when({ a: Match.number }, (_) => String(_.a)), // Must return string
  Match.when({ b: Match.string }, (_) => _.b),
  Match.exhaustive
);
```

## Matching Patterns

### `Match.when(pattern, handler)` — Conditional Match

Supports literal values, predicates, and object shape patterns.

```typescript
import { Match } from "effect";

// Predicate matching
const classify = Match.type<number>().pipe(
  Match.when((n) => n > 100, () => "large"),
  Match.when((n) => n > 10, () => "medium"),
  Match.orElse(() => "small")
);

// Object shape matching
const handleUser = Match.type<{ role: string; active: boolean }>().pipe(
  Match.when({ role: "admin", active: true }, () => "active admin"),
  Match.when({ role: "admin" }, () => "inactive admin"),
  Match.orElse(() => "regular user")
);
```

### `Match.not(pattern, handler)` — Negated Match

Matches everything **except** the specified pattern.

```typescript
import { Match } from "effect";

const match = Match.type<string | number>().pipe(
  Match.not("skip", () => "processing"),
  Match.orElse(() => "skipped")
);

match("hello"); // "processing"
match("skip");  // "skipped"
```

### `Match.tag(...tags, handler)` — Tagged Union Match

Matches on the `_tag` discriminant field. Multiple tags can be combined in one call.

```typescript
import { Match } from "effect";

type Event =
  | { readonly _tag: "Fetch" }
  | { readonly _tag: "Success"; readonly data: string }
  | { readonly _tag: "Error"; readonly error: Error }
  | { readonly _tag: "Cancel" };

const handle = Match.type<Event>().pipe(
  Match.tag("Fetch", "Cancel", () => "no-op"),
  Match.tag("Success", (e) => `Data: ${e.data}`),
  Match.tag("Error", (e) => `Error: ${e.error.message}`),
  Match.exhaustive
);
```

### `Match.tags` and `Match.typeTags` — Shorthand Tag Matchers

```typescript
import { Match } from "effect";

type Result =
  | { readonly _tag: "Ok"; readonly value: number }
  | { readonly _tag: "Err"; readonly error: string };

// Match.tags — object shorthand for Match.type + Match.tag (returns function)
const handle = Match.typeTags<Result>()({
  Ok: (r) => `Value: ${r.value}`,
  Err: (r) => `Error: ${r.error}`,
});

// Match.valueTags — object shorthand for Match.value + Match.tag (evaluates immediately)
const result: Result = { _tag: "Ok", value: 42 };
const output = Match.valueTags(result, {
  Ok: (r) => `Value: ${r.value}`,
  Err: (r) => `Error: ${r.error}`,
});
```

### `Match.discriminator(field)` and `Match.discriminators(field)` — Custom Discriminant Fields

For types that use a discriminant field other than `_tag` (e.g., `type`, `kind`).

```typescript
import { Match } from "effect";

type Shape =
  | { readonly kind: "circle"; readonly radius: number }
  | { readonly kind: "rect"; readonly width: number; readonly height: number };

// Single discriminator value match
const area = Match.type<Shape>().pipe(
  Match.discriminator("kind")("circle", (s) => Math.PI * s.radius ** 2),
  Match.discriminator("kind")("rect", (s) => s.width * s.height),
  Match.exhaustive
);

// Object shorthand — Match.discriminatorsExhaustive
const describe = Match.type<Shape>().pipe(
  Match.discriminatorsExhaustive("kind")({
    circle: (s) => `Circle r=${s.radius}`,
    rect: (s) => `Rect ${s.width}x${s.height}`,
  })
);
```

## Built-in Predicates

Use inside `Match.when` for type-safe narrowing:

| Predicate | Matches |
|---|---|
| `Match.number` | `number` values |
| `Match.string` | `string` values |
| `Match.boolean` | `boolean` values |
| `Match.bigint` | `bigint` values |
| `Match.date` | `Date` instances |
| `Match.null` | `null` |
| `Match.undefined` | `undefined` |
| `Match.defined` | Any non-null, non-undefined value |
| `Match.nonEmptyString` | Non-empty strings |
| `Match.record` | Plain objects (`Record<string, unknown>`) |
| `Match.any` | Matches anything (wildcard) |
| `Match.instanceOf(Class)` | Instances of a given class |
| `Match.is(...values)` | Exact value match (one of the provided values) |

```typescript
import { Match } from "effect";

type Input = string | number | null | Date;

const describe = Match.type<Input>().pipe(
  Match.when(Match.null, () => "nothing"),
  Match.when(Match.date, (d) => `date: ${d.toISOString()}`),
  Match.when(Match.nonEmptyString, (s) => `text: ${s}`),
  Match.when(Match.string, () => "empty string"),
  Match.when(Match.number, (n) => `num: ${n}`),
  Match.exhaustive
);
```

## Completing the Match

| Completion | Behavior |
|---|---|
| `Match.exhaustive` | **Required** — compile error if any case is unhandled |
| `Match.orElse(fn)` | Fallback for unmatched cases (like `default`) |
| `Match.option` | Returns `Option<Result>` — `Some` if matched, `None` if not |
| `Match.either` | Returns `Either<Result, Unmatched>` — `Right` if matched, `Left` if not |

**Prefer `Match.exhaustive`** — it catches missing cases at compile time. Use `Match.orElse` only when a genuine default is needed.

## Pattern Matching in Effect Pipelines

### Matching Schema.TaggedClass Unions

```typescript
import * as Match from "effect/Match";
import * as Schema from "effect/Schema";

class Pending extends Schema.TaggedClass<Pending>()("Pending", {
  requestedAt: Schema.DateFromSelf,
}) {}

class Approved extends Schema.TaggedClass<Approved>()("Approved", {
  approvedBy: Schema.String,
}) {}

class Rejected extends Schema.TaggedClass<Rejected>()("Rejected", {
  reason: Schema.String,
}) {}

const Status = Schema.Union(Pending, Approved, Rejected);
type Status = typeof Status.Type;

// Exhaustive match over all variants
const describeStatus = Match.type<Status>().pipe(
  Match.tag("Pending", (s) => `Pending since ${s.requestedAt}`),
  Match.tag("Approved", (s) => `Approved by ${s.approvedBy}`),
  Match.tag("Rejected", (s) => `Rejected: ${s.reason}`),
  Match.exhaustive
);
```

### Matching Error Types

```typescript
import * as Effect from "effect/Effect";
import * as Match from "effect/Match";
import { Data } from "effect";

class NotFoundError extends Data.TaggedError("NotFoundError")<{ id: string }> {}
class ValidationError extends Data.TaggedError("ValidationError")<{ field: string }> {}
class NetworkError extends Data.TaggedError("NetworkError")<{ url: string }> {}

type AppError = NotFoundError | ValidationError | NetworkError;

const handleError = Match.type<AppError>().pipe(
  Match.tag("NotFoundError", (e) => `Not found: ${e.id}`),
  Match.tag("ValidationError", (e) => `Invalid: ${e.field}`),
  Match.tag("NetworkError", (e) => `Network failure: ${e.url}`),
  Match.exhaustive
);

// Use in Effect error recovery
const program = pipe(
  riskyOperation,
  Effect.catchAll((error) => Effect.succeed(handleError(error)))
);
```

### Matching Exit Results

```typescript
import * as Effect from "effect/Effect";
import * as Match from "effect/Match";
import * as Exit from "effect/Exit";

const program = Effect.gen(function* () {
  const exit = yield* Effect.exit(riskyOperation);
  return Match.value(exit).pipe(
    Match.tag("Success", (e) => e.value),
    Match.tag("Failure", (e) => `Failed: ${e.cause}`),
    Match.exhaustive
  );
});
```

## Forbidden Patterns

```typescript
// BAD: switch on _tag — no exhaustiveness checking
switch (status._tag) {
  case "Pending": return "...";
  case "Approved": return "...";
  // Forgot Rejected — no compile error!
}

// BAD: if/else chain on _tag — verbose, error-prone
if (status._tag === "Pending") { /* ... */ }
else if (status._tag === "Approved") { /* ... */ }
// Forgot Rejected — no compile error!

// BAD: Manual ternary chain for multi-branch
const msg = status._tag === "Pending" ? "..."
  : status._tag === "Approved" ? "..."
  : "..."; // No type narrowing, no exhaustiveness

// GOOD: Match with exhaustive checking
const msg = Match.value(status).pipe(
  Match.tag("Pending", () => "..."),
  Match.tag("Approved", () => "..."),
  Match.tag("Rejected", () => "..."),
  Match.exhaustive
);
```
