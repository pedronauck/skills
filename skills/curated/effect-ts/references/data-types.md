# Effect-TS Data Types

Comprehensive reference for Effect's built-in data types. **Always prefer these over native JS equivalents** — they provide structural equality, immutability, type safety, and seamless integration with the Effect ecosystem.

## When to Use Which Type

| Need | Use | Not |
|---|---|---|
| Optional value | `Option<A>` | `null \| undefined` |
| Success or failure value | `Either<R, L>` | `{ ok: boolean, value?, error? }` |
| Result of running an Effect | `Exit<A, E>` | try-catch |
| Failure details (multiple, parallel) | `Cause<E>` | plain Error |
| Time span / delay / timeout | `Duration` | raw numbers (ms) |
| Date/time with zones | `DateTime` | `Date` |
| Precise decimal arithmetic | `BigDecimal` | `number` (floats) |
| Immutable array for streams/concat | `Chunk<A>` | `Array<A>` |
| Set with structural equality | `HashSet<A>` | `Set<A>` |
| Structural equality for plain data | `Data.struct`, `Data.Class` | plain objects |
| Wrap secrets (prevent logging) | `Redacted<A>` | raw strings |

---

## Data — Structural Equality & Tagged Types

The `Data` module provides structural equality (two values are equal if their contents match, regardless of reference identity).

```typescript
import { Data, Equal } from "effect";

// Plain data with structural equality
const a = Data.struct({ name: "Alice", age: 30 });
const b = Data.struct({ name: "Alice", age: 30 });
Equal.equals(a, b); // true (same structure)
Equal.equals(a, { name: "Alice", age: 30 }); // false (plain obj)

// Tuples and arrays
const t = Data.tuple("Alice", 30);      // readonly [string, number]
const arr = Data.array([1, 2, 3]);       // readonly number[]
```

### Case Constructors

```typescript
// Data.case — reusable constructor with structural equality
interface Person { readonly name: string; readonly age: number }
const makePerson = Data.case<Person>();
Equal.equals(makePerson({ name: "A", age: 1 }), makePerson({ name: "A", age: 1 })); // true

// Data.tagged — auto-injects _tag field
interface Created { readonly _tag: "Created"; readonly id: string }
const Created = Data.tagged<Created>("Created");
Created({ id: "1" }); // { _tag: "Created", id: "1" }
```

### Class-Based Constructors

```typescript
// Data.Class — class with structural equality + custom methods
class User extends Data.Class<{ name: string; role: string }> {
  get isAdmin() { return this.role === "admin"; }
}
Equal.equals(new User({ name: "A", role: "admin" }), new User({ name: "A", role: "admin" })); // true

// Data.TaggedClass — auto-injects _tag
class Created extends Data.TaggedClass("Created")<{ id: string }> {}
new Created({ id: "1" })._tag; // "Created"
```

### TaggedEnum — Discriminated Unions

```typescript
type Shape = Data.TaggedEnum<{
  Circle: { radius: number };
  Rectangle: { width: number; height: number };
}>;

const { Circle, Rectangle, $is, $match } = Data.taggedEnum<Shape>();

const shape = Circle({ radius: 5 });
$is("Circle")(shape);                              // true (type guard)
$match({ Circle: (s) => s.radius, Rectangle: (s) => s.width * s.height })(shape); // 5
```

### Error Types

```typescript
// Data.TaggedError — tagged error with _tag for Match/catchTag
class NotFoundError extends Data.TaggedError("NotFoundError")<{
  readonly id: string;
}> {}

// Data.Error — simple error with structural equality (no _tag)
class SimpleError extends Data.Error<{ readonly message: string }> {}
```

---

## Option — Optional Values

Use `Option<A>` instead of `null | undefined`. Provides explicit absence handling with composable operations.

```typescript
import { Option, pipe } from "effect";

// Creation
Option.some(42);                      // Some(42)
Option.none();                        // None
Option.fromNullable(null);            // None
Option.fromNullable("hello");         // Some("hello")
Option.liftPredicate((n: number) => n > 0)(5); // Some(5)
Option.liftPredicate((n: number) => n > 0)(-1); // None

// Guards
Option.isSome(opt);   // type narrows to Some<A>
Option.isNone(opt);   // type narrows to None

// Pattern matching
Option.match(opt, {
  onNone: () => "absent",
  onSome: (v) => `present: ${v}`,
});
```

### Transformations

```typescript
// map — transform value if Some
Option.map(Option.some(1), (n) => n * 2);          // Some(2)
Option.map(Option.none(), (n) => n * 2);            // None

// flatMap — chain Option-returning functions
Option.flatMap(Option.some(1), (n) =>
  n > 0 ? Option.some(n) : Option.none()
);

// filter — None if predicate fails
Option.filter(Option.some(3), (n) => n > 2);        // Some(3)
Option.filter(Option.some(1), (n) => n > 2);        // None
```

### Extracting Values

```typescript
Option.getOrElse(opt, () => 0);         // value or fallback
Option.getOrThrow(opt);                 // value or throws
Option.getOrNull(opt);                  // A | null
Option.getOrUndefined(opt);             // A | undefined
```

### Combining

```typescript
// all — all must be Some
Option.all([Option.some(1), Option.some(2)]);                  // Some([1, 2])
Option.all({ x: Option.some(1), y: Option.some(2) });         // Some({ x: 1, y: 2 })

// zipWith — combine two Options
Option.zipWith(Option.some(1), Option.some(2), (a, b) => a + b); // Some(3)

// firstSomeOf — first non-None
Option.firstSomeOf([Option.none(), Option.some(2), Option.some(3)]); // Some(2)

// orElse — fallback chain
Option.orElse(Option.none(), () => Option.some(42));            // Some(42)
```

### Generator Syntax

```typescript
const result = Option.gen(function* () {
  const a = yield* Option.some(10);
  const b = yield* Option.some(5);
  return a + b;
}); // Some(15) — short-circuits on None
```

### Interop with Effect

`Option<A>` is a subtype of `Effect<A, NoSuchElementException>`:
- `Some<A>` → succeeds with `A`
- `None` → fails with `NoSuchElementException`

```typescript
// Use Option directly in Effect.gen
const program = Effect.gen(function* () {
  const value = yield* Option.some(42); // None would fail the Effect
  return value;
});

// Wrap Effect result in Option (converts failure to None)
const wrapped = Effect.option(riskyEffect); // Effect<Option<A>>
```

---

## Either — Success or Failure Values

`Either<R, L>` represents a value that is either `Right<R>` (success) or `Left<L>` (failure). Use for synchronous validations and computations outside the Effect context.

```typescript
import { Either } from "effect";

// Creation
Either.right(42);                     // Right(42)
Either.left("error");                 // Left("error")
Either.fromNullable(null, () => "missing"); // Left("missing")

// Guards
Either.isRight(e);  // narrows to Right<R>
Either.isLeft(e);   // narrows to Left<L>

// Pattern matching
Either.match(e, {
  onLeft: (err) => `Error: ${err}`,
  onRight: (val) => `Value: ${val}`,
});
```

### Transformations

```typescript
Either.map(Either.right(1), (n) => n + 1);              // Right(2)
Either.mapLeft(Either.left("err"), (s) => s + "!");      // Left("err!")
Either.mapBoth(e, { onLeft: (s) => s + "!", onRight: (n) => n + 1 });
Either.flatMap(Either.right(1), (n) =>
  n > 0 ? Either.right(n) : Either.left("negative")
);
```

### Extracting & Combining

```typescript
Either.getOrElse(e, () => 0);       // value or fallback
Either.getOrThrow(e);               // value or throws
Either.merge(e);                    // collapses Left|Right to single type
Either.flip(e);                     // swaps Left ↔ Right

// all — combine tuple/struct (first Left short-circuits)
Either.all([Either.right(1), Either.right("a")]); // Right([1, "a"])
Either.all({ x: Either.right(1), y: Either.left("bad") }); // Left("bad")
```

### Generator Syntax & Effect Interop

```typescript
// Either.gen — short-circuits on Left
Either.gen(function* () {
  const a = yield* Either.right(1);
  const b = yield* Either.right(2);
  return a + b;
}); // Right(3)

// Either is a subtype of Effect: Left<L> → Effect<never, L>, Right<R> → Effect<R>
Effect.gen(function* () {
  const val = yield* Either.right(42); // Left would fail the Effect
  return val;
});
```

---

## Exit — Effect Execution Result

`Exit<A, E>` describes the result of running an Effect: either `Success` (value `A`) or `Failure` (a `Cause<E>`).

```typescript
import { Exit, Effect, Cause } from "effect";

// Constructors
Exit.succeed(42);                          // Success(42)
Exit.fail("error");                        // Failure(Cause.Fail("error"))
Exit.failCause(Cause.die("unexpected"));   // Failure(Cause.Die("unexpected"))

// Guards
Exit.isSuccess(exit);  // narrows, access exit.value
Exit.isFailure(exit);  // narrows, access exit.cause

// Pattern matching
Exit.match(exit, {
  onFailure: (cause) => `Failed: ${Cause.pretty(cause)}`,
  onSuccess: (value) => `OK: ${value}`,
});

// Getting Exit from an Effect (instead of try-catch)
const exit = yield* Effect.exit(riskyEffect);
// exit: Exit<A, E> — always succeeds, wraps failure in Exit
```

**Key relationship**: `Exit` is a subtype of `Effect` — an `Exit` value can be used wherever `Effect` is expected.

---

## Cause — Rich Failure Information

`Cause<E>` captures full failure context: expected errors, unexpected defects, interruptions, and combinations.

```typescript
import { Cause, FiberId } from "effect";

// Types: Empty | Fail<E> | Die | Interrupt | Sequential | Parallel
Cause.empty;                         // no error
Cause.fail("expected error");        // expected failure
Cause.die("unexpected defect");      // unexpected defect
Cause.interrupt(FiberId.none);       // fiber interruption

// Combining causes
Cause.sequential(Cause.fail("a"), Cause.fail("b")); // try-finally
Cause.parallel(Cause.fail("a"), Cause.die("b"));     // concurrent

// Guards
Cause.isFailType(c);     // Fail<E>
Cause.isDie(c);           // Die
Cause.isInterruptType(c); // Interrupt
Cause.isEmpty(c);         // Empty

// Accessing
Cause.failures(c);        // Array of expected errors (E[])
Cause.defects(c);         // Array of unexpected defects (unknown[])
Cause.failureOption(c);   // Option<E>
Cause.dieOption(c);       // Option<unknown>
```

### Pattern Matching & Rendering

```typescript
Cause.match(cause, {
  onEmpty: "(empty)",
  onFail: (error) => `fail: ${error}`,
  onDie: (defect) => `die: ${defect}`,
  onInterrupt: (fiberId) => `interrupt: ${fiberId}`,
  onSequential: (l, r) => `${l} then ${r}`,
  onParallel: (l, r) => `${l} and ${r}`,
});

// Human-readable with stack traces
Cause.pretty(cause); // "Error: something went wrong\n    at ..."
```

---

## Duration — Time Spans

Use `Duration` for all time-related values (timeouts, delays, scheduling). **Never use raw numbers for time.**

```typescript
import { Duration } from "effect";

// Creation
Duration.millis(100);     Duration.seconds(2);
Duration.minutes(5);      Duration.hours(7);
Duration.days(3);         Duration.weeks(2);
Duration.nanos(100n);     Duration.zero;
Duration.infinity;

// Decode from various inputs
Duration.decode(100);            // 100 millis
Duration.decode("5 minutes");    // 5 minutes
Duration.decode(10n);            // 10 nanos

// Arithmetic
Duration.sum(Duration.seconds(30), Duration.minutes(1));  // 1m30s
Duration.times(Duration.seconds(30), 2);                  // 1m
Duration.subtract(Duration.minutes(2), Duration.seconds(30)); // 1m30s

// Comparison
Duration.lessThan(Duration.seconds(30), Duration.minutes(1));   // true
Duration.greaterThan(a, b);
Duration.between(d, { minimum: Duration.seconds(10), maximum: Duration.minutes(1) });

// Conversion
Duration.toMillis(Duration.minutes(1));  // 60000
Duration.toSeconds(Duration.minutes(1)); // 60
Duration.format(Duration.millis(1001));  // "1s 1ms"

// Guards
Duration.isDuration(x);   Duration.isFinite(d);   Duration.isZero(d);
```

### Usage with Effect APIs

```typescript
Effect.sleep(Duration.seconds(2));          // or Effect.sleep("2 seconds")
Effect.timeout(myEffect, Duration.millis(500));
Schedule.spaced(Duration.minutes(1));
Schedule.exponential(Duration.millis(100));
```

---

## DateTime — Dates with Time Zones

Use `DateTime` instead of `Date` — provides immutable, timezone-aware date/time with Effect integration.

```typescript
import { DateTime, Duration, Option, Effect } from "effect";

// Two variants: DateTime.Utc and DateTime.Zoned
// Utc — just epoch millis, no timezone
// Zoned — epoch millis + TimeZone (named IANA or fixed offset)
```

### Creation

```typescript
// UTC constructors
DateTime.unsafeMake("2025-01-01");                  // Utc from string
DateTime.unsafeMake(new Date("2025-01-01"));        // Utc from Date
DateTime.unsafeMake({ year: 2025, month: 1 });      // Utc from parts

// Safe version returns Option
const dt: Option.Option<DateTime.Utc> = DateTime.make("2025-01-01");

// Zoned constructors
DateTime.unsafeMakeZoned(new Date(), { timeZone: "America/New_York" });
DateTime.unsafeMakeZoned(new Date(), { timeZone: "Europe/Rome", adjustForTimeZone: true });

// Current time (uses Clock service — testable)
const now: Effect.Effect<DateTime.Utc> = DateTime.now;
const nowUnsafe: DateTime.Utc = DateTime.unsafeNow(); // uses Date.now() directly
```

### Time Zone Management

```typescript
DateTime.setZoneNamed(dt, "America/New_York");     // Option<Zoned>
DateTime.unsafeSetZoneNamed(dt, "Europe/Rome");     // Zoned (throws if invalid)
DateTime.setZoneOffset(dt, 3600000);                // Zoned with +1h offset

// Time zone layers for dependency injection
DateTime.layerCurrentZoneNamed("America/New_York");
DateTime.layerCurrentZoneLocal;
```

### Manipulation & Comparison

```typescript
DateTime.add(dt, Duration.hours(1));
DateTime.subtract(dt, Duration.days(7));
DateTime.startOf(dt, "day");              // midnight
DateTime.endOf(dt, "month");             // last moment of month

DateTime.lessThan(dt1, dt2);
DateTime.greaterThan(dt1, dt2);
DateTime.between(dt, { minimum: start, maximum: end });
```

### Formatting & Conversion

```typescript
DateTime.formatIso(dt);                   // "2025-01-01T00:00:00.000Z"
DateTime.formatIsoZoned(zoned);           // "2025-01-01T04:00:00.000+01:00[Europe/Rome]"
DateTime.format(dt, { dateStyle: "full" });
DateTime.toDateUtc(dt);                   // JS Date in UTC
DateTime.toEpochMillis(dt);              // number
DateTime.getParts(dt);                    // { year, month, day, hours, minutes, seconds, millis }
```

### Guards

```typescript
DateTime.isDateTime(x);   DateTime.isUtc(dt);   DateTime.isZoned(dt);
```

---

## BigDecimal — Precise Decimal Arithmetic

Use `BigDecimal` for financial calculations and anywhere floating-point precision matters.

```typescript
import { BigDecimal, Option } from "effect";

// Creation
BigDecimal.make(1n, 2);                    // 0.01 (value × 10^-scale)
BigDecimal.fromBigInt(10n);                // 10
BigDecimal.fromString("0.02");             // Option<BigDecimal>
BigDecimal.unsafeFromString("123.456");    // BigDecimal (throws on invalid)
BigDecimal.unsafeFromNumber(123.456);      // BigDecimal (throws on NaN/Infinity)
```

### Why BigDecimal?

```typescript
// Native JS floating-point bug:
1.05 + 2.1;  // 3.1500000000000004

// BigDecimal:
BigDecimal.format(BigDecimal.sum(
  BigDecimal.unsafeFromString("1.05"),
  BigDecimal.unsafeFromString("2.10"),
)); // "3.15" — exact
```

### Arithmetic

```typescript
BigDecimal.sum(a, b);           BigDecimal.subtract(a, b);
BigDecimal.multiply(a, b);      BigDecimal.divide(a, b);       // Option<BigDecimal>
BigDecimal.unsafeDivide(a, b);  BigDecimal.negate(a);
BigDecimal.abs(a);              BigDecimal.sign(a);            // -1, 0, or 1
BigDecimal.remainder(a, b);     // Option<BigDecimal>
```

### Comparison & Formatting

```typescript
BigDecimal.lessThan(a, b);      BigDecimal.greaterThan(a, b);
BigDecimal.equals(a, b);        BigDecimal.between(a, { minimum, maximum });
BigDecimal.min(a, b);           BigDecimal.max(a, b);
BigDecimal.isZero(a);           BigDecimal.isPositive(a);      BigDecimal.isNegative(a);

BigDecimal.format(d);           // "123.456"
BigDecimal.toExponential(d);    // "1.23456e+5"
BigDecimal.normalize(d);        // removes trailing zeros (1.00 → 1)
```

---

## Chunk — Immutable Array for Streams

`Chunk<A>` is an immutable, ordered collection optimized for repeated concatenation. **Use `Chunk` when working with streams or when you need efficient append/concat. For general array work, prefer `Array` module.**

```typescript
import { Chunk, Equal } from "effect";

// Creation
Chunk.empty<number>();                    // empty chunk
Chunk.make(1, 2, 3);                     // NonEmptyChunk
Chunk.fromIterable([1, 2, 3]);           // from array (copies)
Chunk.unsafeFromArray([1, 2, 3]);        // from array (no copy, unsafe)

// Operations
Chunk.append(chunk, 4);                  // add to end
Chunk.prepend(chunk, 0);                 // add to start
Chunk.appendAll(chunkA, chunkB);         // concatenate
Chunk.drop(chunk, 2);                    // remove first N
Chunk.take(chunk, 2);                    // keep first N
Chunk.map(chunk, (n) => n * 2);
Chunk.filter(chunk, (n) => n > 2);
Chunk.flatMap(chunk, (n) => Chunk.make(n, -n));
Chunk.reduce(chunk, 0, (acc, n) => acc + n);
Chunk.head(chunk);                       // Option<A>
Chunk.findFirst(chunk, (n) => n > 2);    // Option<A>

// Conversion
Chunk.toReadonlyArray(chunk);            // readonly A[]

// Equality (structural)
Equal.equals(Chunk.make(1, 2), Chunk.make(1, 2)); // true
```

---

## HashSet — Set with Structural Equality

`HashSet<A>` provides O(1) lookup/insert/remove with structural equality instead of reference equality.

```typescript
import { HashSet, Data } from "effect";

// Creation
HashSet.make(1, 2, 3);
HashSet.empty<number>();
HashSet.fromIterable([1, 2, 2, 3]);      // deduplicates → {1, 2, 3}

// Operations
HashSet.add(set, 4);                     // returns new set
HashSet.remove(set, 2);                  // returns new set
HashSet.has(set, 1);                     // true
HashSet.size(set);                       // 3
HashSet.toggle(set, 2);                  // add if absent, remove if present

// Set algebra
HashSet.union(a, b);
HashSet.intersection(a, b);
HashSet.difference(a, b);
HashSet.isSubset(a, b);

// Iteration
HashSet.toValues(set);                   // Array
HashSet.map(set, (n) => n * 2);
HashSet.filter(set, (n) => n > 2);
HashSet.reduce(set, 0, (acc, n) => acc + n);
HashSet.every(set, (n) => n > 0);
HashSet.some(set, (n) => n > 2);
HashSet.forEach(set, (n) => console.log(n));
```

### Structural Equality with Data

```typescript
// Native Set uses reference equality — duplicates objects
const jsSet = new Set([{ id: 1 }, { id: 1 }]); // size: 2

// HashSet with Data.struct uses structural equality
const p1 = Data.struct({ id: 1 });
const p2 = Data.struct({ id: 1 });
HashSet.size(HashSet.make(p1, p2)); // 1 — deduplicated
```

### Batched Mutations

```typescript
const modified = HashSet.mutate(original, (draft) => {
  HashSet.add(draft, 4);
  HashSet.remove(draft, 1);
}); // original unchanged, modified has changes
```

---

## Redacted — Secret Value Wrapper

`Redacted<A>` wraps sensitive values (API keys, passwords, tokens) to prevent accidental logging.

```typescript
import { Redacted, Effect } from "effect";

// Creation
const apiKey = Redacted.make("sk-1234567890");

// Logging is safe — value is hidden
console.log(apiKey);           // {}
console.log(String(apiKey));   // <redacted>
Effect.runSync(Effect.log(apiKey)); // message="<redacted>"

// Access the actual value (only when needed)
const raw = Redacted.value(apiKey); // "sk-1234567890"

// Use in HTTP headers
const headers = { Authorization: `Bearer ${Redacted.value(apiKey)}` };

// Wipe from memory when done
Redacted.unsafeWipe(apiKey);
// Redacted.value(apiKey) now throws

// Safe comparison without exposing values
const eq = Redacted.getEquivalence(Equivalence.string);
eq(key1, key2); // true/false

// Guard
Redacted.isRedacted(x);
```

### Best Practices

1. Wrap secrets **immediately at the boundary** (env vars, config loading)
2. Only call `Redacted.value()` at the **last moment** (HTTP call, DB connection)
3. **Never** store `Redacted.value()` result in a variable longer than needed
4. Call `Redacted.unsafeWipe()` when the secret is no longer needed

---

## Import Convention

```typescript
import * as BigDecimal from "effect/BigDecimal";
import * as Cause from "effect/Cause";
import * as Chunk from "effect/Chunk";
import * as Data from "effect/Data";
import * as DateTime from "effect/DateTime";
import * as Duration from "effect/Duration";
import * as Either from "effect/Either";
import * as Exit from "effect/Exit";
import * as HashSet from "effect/HashSet";
import * as Option from "effect/Option";
import * as Redacted from "effect/Redacted";
```

## Validation Checklist

- [ ] `Option` for optional values (not `null | undefined`)
- [ ] `Either` for sync success/failure (not ad-hoc `{ ok, error }` objects)
- [ ] `Exit` + `Effect.exit` for inspecting Effect results (not try-catch)
- [ ] `Duration` for all time values (not raw numbers)
- [ ] `DateTime` for date/time operations (not `Date`)
- [ ] `BigDecimal` for financial/precise arithmetic (not `number`)
- [ ] `Chunk` for stream data and repeated concatenation
- [ ] `HashSet` when structural set equality is needed (not `Set`)
- [ ] `Data.struct`/`Data.Class` for structural equality
- [ ] `Data.TaggedError` for typed errors with `_tag`
- [ ] `Data.TaggedEnum` for discriminated unions with factory + `$match`
- [ ] `Redacted` for all secrets (API keys, passwords, tokens)
- [ ] `Cause` for rich failure inspection (never discard failure info)
