# Streams Deep Dive

Creating, transforming, consuming, and error handling with Effect streams.

> **See also**: [`sink.md`](./sink.md) for comprehensive Sink reference (creating, operations, concurrency, leftovers).

## Table of Contents

- [Creating Streams](#creating-streams)
- [Stream Operations](#stream-operations)
- [Concatenation and Merging](#concatenation-and-merging)
- [Grouping, Partitioning, and Broadcasting](#grouping-partitioning-and-broadcasting)
- [Buffering, Debouncing, and Throttling](#buffering-debouncing-and-throttling)
- [Consuming Streams](#consuming-streams)
- [Error Handling in Streams](#error-handling-in-streams)
- [Resourceful Streams](#resourceful-streams)

## Creating Streams

### From Values

```typescript
import * as Stream from "effect/Stream";
import * as Effect from "effect/Effect";

// From explicit values
const s1 = Stream.make(1, 2, 3);

// Empty stream
const s2 = Stream.empty;

// Single void value (signal)
const s3 = Stream.void;

// Range of integers (inclusive)
const s4 = Stream.range(1, 100); // 1..100

// Infinite stream via iteration
const naturals = Stream.iterate(1, (n) => n + 1); // 1, 2, 3, ...
```

### From Effects

```typescript
// Single-element stream from an Effect
const randomStream = Stream.fromEffect(Random.nextInt);

// Repeat an effect as a stream
const repeated = Stream.repeatEffect(Random.nextInt);

// Repeat with schedule
const polled = Stream.repeatEffectWithSchedule(
  fetchLatestData,
  Schedule.fixed("5 seconds")
);
```

### From Chunks

```typescript
import * as Chunk from "effect/Chunk";

const fromChunk = Stream.fromChunk(Chunk.make(1, 2, 3));
const fromChunks = Stream.fromChunks(
  Chunk.make(1, 2, 3),
  Chunk.make(4, 5, 6)
);
```

### From Iterables and Async Sources

```typescript
// From iterable
const fromArray = Stream.fromIterable([1, 2, 3]);

// From async callback (push-based)
const fromCallback = Stream.async<number, Error>((emit) => {
  someEventEmitter.on("data", (data) => {
    emit(Effect.succeed(Chunk.of(data)));
  });
  someEventEmitter.on("end", () => {
    emit(Effect.fail(Option.none())); // Signal end
  });
  someEventEmitter.on("error", (err) => {
    emit(Effect.fail(Option.some(new MyError({ cause: err }))));
  });
});

// Unfold — generate from a seed
const fibonacci = Stream.unfold([0, 1] as const, ([a, b]) =>
  Option.some([a, [b, a + b] as const] as const)
);

// Paginated API
const pages = Stream.paginate(1, (page) => [
  fetchPage(page),
  page < totalPages ? Option.some(page + 1) : Option.none(),
]);
```

### From Scoped Resources

```typescript
const fromResource = Stream.scoped(
  Effect.acquireUseRelease(
    openConnection(),
    (conn) => conn.read(),
    (conn) => Effect.sync(() => conn.close())
  )
);
```

## Stream Operations

### Mapping and Filtering

```typescript
pipe(
  Stream.range(1, 100),
  Stream.map((n) => n * 2),            // Transform each element
  Stream.filter((n) => n > 50),        // Keep elements matching predicate
  Stream.take(10),                      // Take first N elements
  Stream.drop(5),                       // Skip first N elements
);

// mapEffect — apply an effectful function to each element
pipe(userIds, Stream.mapEffect((id) => fetchUser(id)));

// mapEffect with concurrency
pipe(userIds, Stream.mapEffect((id) => fetchUser(id), { concurrency: 5 }));

// takeUntil — take until condition met (like break in a loop)
pipe(stream, Stream.takeUntil((n) => n > 100));

// takeWhile — take while condition holds
pipe(stream, Stream.takeWhile((n) => n < 100));
```

### Stateful Mapping

```typescript
// mapAccum — accumulate state and transform simultaneously
pipe(
  Stream.make("a", "b", "c"),
  Stream.mapAccum(0, (index, char) => [index + 1, `${index}:${char}`]),
);
// "0:a", "1:b", "2:c"

// scan — running accumulation (emits each intermediate state)
pipe(
  Stream.range(1, 5),
  Stream.scan(0, (acc, n) => acc + n),
);
// 0, 1, 3, 6, 10, 15
```

### Flattening

```typescript
// flatMap — map to streams and flatten
pipe(
  departmentStream,
  Stream.flatMap((dept) => Stream.fromIterable(dept.employees)),
);

// flatMap with concurrency — run inner streams concurrently
pipe(
  userIds,
  Stream.flatMap((id) => fetchUserStream(id), { concurrency: 5 }),
);

// flatMap with switch — cancel previous when new element arrives
// Useful for search/autocomplete: only latest result matters
pipe(
  searchTerms,
  Stream.flatMap((term) => searchApi(term), { switch: true }),
);
```

### Deduplication

```typescript
// Remove consecutive duplicates
pipe(stream, Stream.changes);

// Custom equality for deduplication
pipe(stream, Stream.changesWith((a, b) => a.id === b.id));
```

### Zipping

```typescript
// Pair elements from two streams
const zipped = Stream.zip(names, ages);
// ["Alice", 30], ["Bob", 25], ...

const zippedWith = Stream.zipWith(names, ages, (name, age) =>
  `${name} is ${age}`
);

// Zip with index
pipe(stream, Stream.zipWithIndex);
// [element, 0], [element, 1], ...

// Cartesian product — all combinations
const product = Stream.cross(s1, s2);
// s1=[1,2], s2=["a","b"] → [1,"a"], [1,"b"], [2,"a"], [2,"b"]
```

### Interspersing

```typescript
// Insert separator between elements
pipe(Stream.make("a", "b", "c"), Stream.intersperse(","));
// "a", ",", "b", ",", "c"
```

## Concatenation and Merging

### Concatenation (Sequential)

```typescript
// Two streams in sequence
const sequential = Stream.concat(Stream.make(1, 2), Stream.make(3, 4));
// 1, 2, 3, 4

// Multiple streams
const all = Stream.concatAll(Chunk.make(s1, s2, s3));
```

### Merging (Concurrent)

```typescript
// Interleave two streams as elements become available
const merged = Stream.merge(stream1, stream2);

// Merge with termination strategy
// "first" — stop when first stream ends
// "last" — stop when last stream ends (default)
// "either" — stop when either ends
// "both" — stop when both end
const merged2 = Stream.merge(stream1, stream2, {
  haltStrategy: "first"
});

// Merge multiple streams with concurrency
const all = Stream.mergeAll([s1, s2, s3], { concurrency: 3 });

// Merge with custom combiner
Stream.mergeWith(s1, s2, {
  onSelf: (n) => n * 2,
  onOther: (s) => Number.parseInt(s)
});
```

### Interleaving

```typescript
// Strict alternation between two streams
const interleaved = Stream.interleave(s1, s2);
// s1=[1,2,3], s2=["a","b","c"] → 1, "a", 2, "b", 3, "c"
```

## Grouping, Partitioning, and Broadcasting

### Grouping

```typescript
// Fixed-size chunks
pipe(Stream.range(0, 8), Stream.grouped(3));
// Chunk[0,1,2], Chunk[3,4,5], Chunk[6,7,8]

// Group by time OR size (whichever first)
pipe(stream, Stream.groupedWithin(100, "5 seconds"));
// Batch up to 100 elements or 5 seconds

// Group adjacent equal elements
pipe(
  Stream.make(1, 1, 2, 2, 2, 3),
  Stream.groupAdjacentBy((n) => n),
);
// [1, Chunk[1,1]], [2, Chunk[2,2,2]], [3, Chunk[3]]

// GroupBy with evaluate — group by key and process each group
import * as GroupBy from "effect/GroupBy";

const grouped = Stream.fromIterable(exams).pipe(
  Stream.groupByKey((exam) => Math.floor(exam.score / 10) * 10)
);
const counts = GroupBy.evaluate(grouped, (key, stream) =>
  Stream.fromEffect(
    Stream.runCollect(stream).pipe(
      Effect.andThen((chunk) => [key, Chunk.size(chunk)] as const)
    )
  )
);
```

### Partitioning

Both return scoped resources — must be used within `Effect.scoped`:

```typescript
// Partition by predicate → [falsy stream, truthy stream]
const program = Stream.range(1, 9).pipe(
  Stream.partition((n) => n % 2 === 0, { bufferSize: 5 })
);
yield* Effect.scoped(
  Effect.gen(function* () {
    const [odds, evens] = yield* program;
    console.log(yield* Stream.runCollect(odds));  // 1,3,5,7,9
    console.log(yield* Stream.runCollect(evens)); // 2,4,6,8
  })
);

// Effectful partition with Either
Stream.partitionEither(
  (n) => Effect.succeed(n % 2 === 0 ? Either.right(n) : Either.left(n)),
  { bufferSize: 5 }
);
```

### Broadcasting

Send each element to multiple downstream consumers:

```typescript
// Broadcast to N consumers with maximum lag
const program = Effect.scoped(
  Stream.range(1, 20).pipe(
    Stream.broadcast(2, 5), // 2 consumers, max lag 5
    Stream.flatMap(([first, second]) =>
      Effect.gen(function* () {
        const f1 = yield* Stream.runFold(first, 0, Math.max).pipe(Effect.fork);
        const f2 = yield* Stream.runForEach(second, Console.log).pipe(Effect.fork);
        yield* Fiber.join(f1).pipe(Effect.zip(Fiber.join(f2), { concurrent: true }));
      })
    ),
    Stream.runCollect
  )
);
```

## Buffering, Debouncing, and Throttling

### Buffering

Decouple producer/consumer speeds:

```typescript
// Bounded buffer — blocks producer when full
pipe(stream, Stream.buffer({ capacity: 100 }));

// Unbounded — never blocks (use cautiously)
pipe(stream, Stream.buffer({ capacity: "unbounded" }));

// Sliding — drops oldest when full
pipe(stream, Stream.buffer({ capacity: 100, strategy: "sliding" }));

// Dropping — drops newest when full
pipe(stream, Stream.buffer({ capacity: 100, strategy: "dropping" }));
```

### Debouncing

Emit only the last value after a quiet period:

```typescript
// Only emit after 300ms pause in rapid values
pipe(eventStream, Stream.debounce("300 millis"));
```

### Throttling

Regulate emission rate using token bucket algorithm:

```typescript
// Shape strategy (default) — delays chunks to match rate
pipe(
  fastStream,
  Stream.throttle({
    cost: () => 1,           // 1 token per chunk
    duration: "100 millis",  // refill interval
    units: 1                 // tokens per refill
  })
);

// Enforce strategy — drops chunks that exceed rate
pipe(
  fastStream,
  Stream.throttle({
    cost: () => 1,
    duration: "100 millis",
    units: 1,
    strategy: "enforce"
  })
);
```

### Scheduling

Pace element emission:

```typescript
// Emit each element with 1 second spacing
pipe(stream, Stream.schedule(Schedule.spaced("1 second")));
```

### Rechunking

Control chunk boundaries:

```typescript
// Rechunk into chunks of size 2
pipe(Stream.fromIterable([1,2,3,4,5]), Stream.rechunk(2));
```

### Transducing with Sinks

Apply a Sink repeatedly to process stream in batches. See [`sink.md`](./sink.md) for Sink details.

```typescript
// Collect in chunks of 3
pipe(
  stream,
  Stream.transduce(Sink.collectAllN<number>(3))
);
// Produces stream of: Chunk(1,2,3), Chunk(4,5,6), Chunk(7)

// Weighted batching
pipe(
  stream,
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

### Pull-Based Consumption

Alternative to async iterables — manually pull chunks:

```typescript
const program = Effect.gen(function* () {
  const getChunk = yield* Stream.toPull(stream);
  while (true) {
    const chunk = yield* getChunk; // fails with None when stream ends
    console.log(chunk);
  }
});
yield* Effect.scoped(program);
```

## Consuming Streams

### Collect All Elements

```typescript
const chunk = yield* Stream.runCollect(stream);
// Chunk<A> — all elements in memory
```

### Run for Side Effects

```typescript
// Process each element, discard results
yield* Stream.runForEach(stream, (element) =>
  Effect.log(`Processing: ${element}`)
);

// Drain — run stream, discard all output
yield* Stream.runDrain(stream);
```

### Fold / Reduce

```typescript
// Fold to a single value
const sum = yield* Stream.runFold(stream, 0, (acc, n) => acc + n);

// Fold with early termination
const partial = yield* Stream.runFoldWhile(
  stream, 0, (sum) => sum <= 10, (acc, n) => acc + n
);
```

### Run to Sink

```typescript
import * as Sink from "effect/Sink";

const count = yield* Stream.run(stream, Sink.count);
const first = yield* Stream.run(stream, Sink.head());
```

## Error Handling in Streams

### Catching Errors

```typescript
// Catch all errors, switch to fallback stream
pipe(riskyStream, Stream.catchAll((error) => Stream.make(fallbackValue)));

// Catch specific tagged errors
pipe(riskyStream, Stream.catchTag("NetworkError", (e) => Stream.make(cached)));

// Catch some errors (return Option.some to handle, Option.none to pass)
pipe(riskyStream, Stream.catchSome((error) => {
  if (error === "recoverable") return Option.some(Stream.make(fallback));
  return Option.none();
}));

// Catch all causes (including defects)
pipe(riskyStream, Stream.catchAllCause(() => fallbackStream));

// Catch some causes
pipe(riskyStream, Stream.catchSomeCause((cause) => {
  if (Cause.isDie(cause)) return Option.some(fallbackStream);
  return Option.none();
}));
```

### Fallback and Recovery

```typescript
// orElse — switch to fallback on any error
pipe(primaryStream, Stream.orElse(() => fallbackStream));

// orElseEither — tag elements with Left/Right to identify source
pipe(primaryStream, Stream.orElseEither(() => fallbackStream));

// onError — run cleanup effect on failure
pipe(stream, Stream.onError(() => Console.log("Cleaning up").pipe(Effect.orDie)));
```

### Retry on Error

```typescript
pipe(
  riskyStream,
  Stream.retry(Schedule.exponential("100 millis").pipe(
    Schedule.compose(Schedule.recurs(3))
  )),
);
```

### Timeouts

```typescript
// Timeout — end stream after duration
pipe(stream, Stream.timeout("5 seconds"));

// Timeout with custom error
pipe(stream, Stream.timeoutFail(new TimeoutError(), "5 seconds"));

// Timeout and switch to another stream
pipe(stream, Stream.timeoutTo("5 seconds", fallbackStream));
```

## Resourceful Streams

Streams with guaranteed resource cleanup:

### acquireRelease

```typescript
const fileLines = pipe(
  Stream.acquireRelease(
    openFile("data.txt"),
    (handle) => Effect.sync(() => handle.close())
  ),
  Stream.flatMap((handle) => Stream.fromIterable(handle.readLines())),
);
// File is automatically closed when stream completes or errors
```

### Scoped Streams

```typescript
const dbStream = Stream.unwrapScoped(
  Effect.gen(function* () {
    const conn = yield* Effect.acquireRelease(
      connectToDb(),
      (c) => Effect.sync(() => c.close())
    );
    return Stream.fromEffect(conn.query("SELECT * FROM users"));
  })
);
```

### Finalizer

Run an effect when the stream's scope closes:

```typescript
const program = application.pipe(
  Stream.concat(
    Stream.finalizer(deleteDir("tmp").pipe(
      Effect.andThen(Console.log("Cleanup complete"))
    ))
  )
);
```

### Ensuring

Run an effect after the stream's finalization:

```typescript
pipe(
  myStream,
  Stream.concat(Stream.finalizer(Console.log("Finalizing"))),
  Stream.ensuring(Console.log("After finalization")),
);
```

## Import Convention

```typescript
import * as Stream from "effect/Stream";
import * as Sink from "effect/Sink";
import * as Chunk from "effect/Chunk";
import * as GroupBy from "effect/GroupBy";
import * as Effect from "effect/Effect";
import * as Schedule from "effect/Schedule";
import { pipe } from "effect/Function";
```
