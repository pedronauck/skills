# Sink Reference

Sinks consume elements from a Stream and produce a result. Comprehensive reference for creating, transforming, and composing sinks.

> **See also**: [`streams-deep-dive.md`](./streams-deep-dive.md) for creating and operating on streams, [`data-types.md`](./data-types.md) for Chunk/Option used in sink results.

## Table of Contents

- [Type Signature](#type-signature)
- [Running a Sink](#running-a-sink)
- [Common Constructors](#common-constructors)
- [Collecting](#collecting)
- [Folding](#folding)
- [Operations](#operations)
- [Concurrency](#concurrency)
- [Leftovers](#leftovers)
- [Using Sinks with Stream.transduce](#using-sinks-with-streamtransduce)
- [Quick Reference Table](#quick-reference-table)
- [Import Convention](#import-convention)

## Type Signature

```
     ┌─── Type of the result produced by the Sink
     |  ┌─── Type of elements consumed by the Sink
     |  |   ┌─── Type of any leftover elements
     │  |   |  ┌─── Type of possible errors
     │  │   |  |  ┌─── Type of required dependencies
     ▼  ▼   ▼  ▼  ▼
Sink<A, In, L, E, R>
```

- `A` — final result after consuming elements
- `In` — element type consumed from the stream
- `L` — leftover elements not consumed (often same as `In`)
- `E` — error type (`never` if infallible)
- `R` — required dependencies (`never` if none)

## Running a Sink

Pass a sink to `Stream.run` to consume a stream:

```typescript
import * as Stream from "effect/Stream";
import * as Sink from "effect/Sink";
import * as Effect from "effect/Effect";

const result = yield* Stream.run(Stream.make(1, 2, 3), Sink.sum);
// 6
```

## Common Constructors

### Terminal Sinks

```typescript
// First element — Option<A>
Sink.head<number>()           // Some(1) or None

// Last element — Option<A>
Sink.last<number>()           // Some(3) or None

// Count all elements — number
Sink.count                    // 4

// Sum numeric elements — number
Sink.sum                      // 10

// First N elements — Chunk<A>
Sink.take<number>(3)          // Chunk(1, 2, 3)

// Discard all — void (for side effects upstream)
Sink.drain

// Measure execution time — Duration
Sink.timed
```

### Effectful Consumption

```typescript
// Run effect for each element
Sink.forEach<number>((n) => Console.log(`Got: ${n}`))
```

### Success / Failure

```typescript
// Immediately succeed without consuming
Sink.succeed(0)               // always returns 0

// Immediately fail without consuming
Sink.fail("oops")             // fails with "oops"
```

## Collecting

```typescript
// All elements into Chunk
Sink.collectAll<number>()

// First N elements into Chunk
Sink.collectAllN<number>(3)

// While predicate holds
Sink.collectAllWhile<number>((n) => n !== 0)

// Into HashSet (unique elements)
Sink.collectAllToSet<number>()

// Into HashSet with max size
Sink.collectAllToSetN<number>(3)

// Into HashMap with key + merge functions
Sink.collectAllToMap<number, number>(
  (n) => n % 3,          // key function
  (a, b) => a + b        // merge values with same key
)

// Into HashMap with max keys
Sink.collectAllToMapN<number, number>(
  3,                      // max keys
  (n) => n,               // key function
  (a, b) => a + b         // merge function
)
```

## Folding

```typescript
// Standard left fold — processes entire stream
Sink.foldLeft(0, (acc, n) => acc + n)

// Fold with early termination
Sink.fold(
  0,                       // initial
  (sum) => sum <= 10,      // continue while true
  (acc, n) => acc + n      // fold operation
)
// Stops when sum > 10

// Fold up to N elements
Sink.foldUntil(0, 3, (acc, n) => acc + n)
// Folds first 3 elements only

// Fold by weight — resets when maxCost exceeded
Sink.foldWeighted({
  initial: Chunk.empty<number>(),
  maxCost: 3,
  cost: () => 1,                          // weight per element
  body: (acc, el) => Chunk.append(acc, el)
})
```

## Operations

### Transforming Input

`Sink.mapInput` adapts what a sink accepts. `Sink.map` transforms the output.

```typescript
// Convert string input to numbers for Sink.sum
const stringSum = Sink.sum.pipe(
  Sink.mapInput((s: string) => Number.parseFloat(s))
);
// Stream.run(Stream.make("1", "2", "3"), stringSum) → 6
```

### Transforming Both Input and Output

```typescript
const sumAsString = Sink.dimap(Sink.sum, {
  onInput: (s: string) => Number.parseFloat(s),
  onDone: (n) => String(n)
});
// Stream.run(Stream.make("1", "2", "3"), sumAsString) → "6"
```

### Filtering Input

```typescript
// Only collect positive numbers in chunks of 3
Sink.collectAllN<number>(3).pipe(
  Sink.filterInput((n) => n > 0)
)
```

### Mapping Output

```typescript
// Transform the result
Sink.count.pipe(Sink.map((n) => `Total: ${n}`))

// Replace the result with a constant
Sink.forEach(Console.log).pipe(Sink.as(42))
```

## Concurrency

### Zip — Combine Two Sinks

Run two sinks concurrently and combine results into a tuple:

```typescript
const sink1 = Sink.forEach((s: string) =>
  Console.log(`sink 1: ${s}`)
).pipe(Sink.as(1));

const sink2 = Sink.forEach((s: string) =>
  Console.log(`sink 2: ${s}`)
).pipe(Sink.as(2));

const combined = Sink.zip(sink1, sink2, { concurrent: true });
// Stream.run(stream, combined) → [1, 2]
```

### Race — First Completion Wins

```typescript
const winner = Sink.race(sink1, sink2);
// Result from whichever sink finishes first
```

## Leftovers

When a sink doesn't consume all elements, the rest are "leftovers."

```typescript
// Collect leftovers as a tuple: [result, Chunk<leftover>]
const withLeftovers = Sink.take<number>(3).pipe(Sink.collectLeftover);
// Stream.run(Stream.make(1,2,3,4,5), withLeftovers)
// → [Chunk(1,2,3), Chunk(4,5)]

// Discard leftovers
const noLeftovers = Sink.take<number>(3).pipe(Sink.ignoreLeftover);
```

## Using Sinks with Stream.transduce

`Stream.transduce` repeatedly applies a sink to a stream, producing a stream of sink results:

```typescript
const chunked = Stream.make(1, 2, 3, 4, 5, 6, 7).pipe(
  Stream.transduce(Sink.collectAllN<number>(3))
);
// Produces: Chunk(1,2,3), Chunk(4,5,6), Chunk(7)

// Batch with weighted elements
const batched = stream.pipe(
  Stream.transduce(
    Sink.foldWeighted({
      initial: Chunk.empty<number>(),
      maxCost: 100,
      cost: (_, el) => el,
      body: (acc, el) => Chunk.append(acc, el)
    })
  )
);
```

## Quick Reference Table

| Sink | Result | Consumes |
|---|---|---|
| `Sink.head()` | `Option<A>` | First element |
| `Sink.last()` | `Option<A>` | All elements |
| `Sink.count` | `number` | All elements |
| `Sink.sum` | `number` | All numeric |
| `Sink.take(n)` | `Chunk<A>` | First N |
| `Sink.drain` | `void` | All (discards) |
| `Sink.timed` | `Duration` | All (measures) |
| `Sink.forEach(f)` | `void` | All (side effects) |
| `Sink.collectAll()` | `Chunk<A>` | All elements |
| `Sink.collectAllN(n)` | `Chunk<A>` | First N |
| `Sink.collectAllWhile(p)` | `Chunk<A>` | While predicate |
| `Sink.collectAllToSet()` | `HashSet<A>` | All (unique) |
| `Sink.collectAllToMap(k, m)` | `HashMap<K, A>` | All (grouped) |
| `Sink.foldLeft(s, f)` | `S` | All elements |
| `Sink.fold(s, cont, f)` | `S` | Until condition |
| `Sink.foldUntil(s, n, f)` | `S` | First N |
| `Sink.foldWeighted(opts)` | `S` | Until max cost |

## Import Convention

```typescript
import * as Sink from "effect/Sink";
import * as Stream from "effect/Stream";
import * as Chunk from "effect/Chunk";
import * as Console from "effect/Console";
```
