# Performance

## Golden Rule

> Don't guess, measure.

Rust code is often already fast. Optimize only after finding bottlenecks with evidence.

### First Steps

- Use `--release` flag on builds (debug mode has no optimizations)
- Run `cargo clippy -- -D clippy::perf` for performance hints
- Use `cargo bench` for micro-benchmarks
- Use `cargo flamegraph` or `samply` (macOS) for profiling

## Flamegraph

Visualize how much time the CPU spends on each task:

```bash
cargo install flamegraph

# Profile release build (default)
cargo flamegraph

# Profile specific binary
cargo flamegraph --bin=stress2

# Profile unit tests
cargo flamegraph --unit-test -- test::in::package

# Profile integration tests
cargo flamegraph --test test_name

# Profile criterion benchmark
cargo flamegraph --bench some_benchmark -- --bench
```

Always profile with `--release`. The `--dev` flag is not realistic.

### Reading Flamegraphs

- **Y-axis**: stack depth — `main` is at the bottom, called functions stack upward
- **Box width**: total CPU time for that function (wider = more CPU or called more often)
- **Color**: random, not significant
- **Thick stacks**: heavy CPU usage
- **Thin stacks**: low intensity (cheap)

## Avoid Redundant Cloning

Clone only when truly needed, and at the last moment:

- Only `.clone()` if a new owned copy is required
- Prefer API designs that take references: `fn process(values: &[T])` not `fn process(values: Vec<T>)`
- If only read access is needed, use `.iter()` or slices
- Auto-cloning in loops is expensive — prefer `.cloned()` or `.copied()` at the iterator chain end

### When to Pass Ownership

- Crate API requires owned data
- Overloaded `std::ops` but still need the original
- Reference-counted pointers (`Arc`, `Rc`)
- HTTP clients (e.g., `hyper_util::Client`) where cloning shares the connection pool
- Modeling business logic/state transitions

### Use Cow for Maybe-Owned Data

```rust
use std::borrow::Cow;

fn process(name: Cow<'_, str>) {
    println!("Hello {name}");
}

process(Cow::Borrowed("Julia"));        // No allocation
process(Cow::Owned("Naomi".to_string())); // Allocation
```

## Pre-Allocate Collections

Avoid repeated reallocation:
```rust
let mut v = Vec::with_capacity(expected_size);
let mut s = String::with_capacity(expected_len);
```

Use arrays for fixed sizes; avoid `Vec` when length is known at compile time.

## Stack vs Heap

### Good Practices

- Keep small types (`impl Copy`, `usize`, `bool`) on the stack
- Avoid passing huge types (>512 bytes) by value — use `&T` or `&mut T`
- Heap-allocate recursive data structures:
```rust
enum OctreeNode<T> {
    Node(T),
    Children(Box<[Node<T>; 8]>),
}
```
- Return small `Copy` types by value

### Be Mindful

- Only use `#[inline]` when benchmarks prove benefit — Rust is good at auto-inlining
- Avoid massive stack allocations: `Box::new([0u8; 65536])` first allocates on stack then boxes. Instead use `vec![0; 65536].into_boxed_slice()`
- For large const arrays, use `smallvec` — it heap-allocates when the array is too large

## Iterators and Zero-Cost Abstractions

Rust iterators are lazy and compiled into tight loops. Chaining `.filter()`, `.map()`, `.rev()`, `.collect()` has no extra cost.

- Prefer iterators over manual `for` loops for collection transforms
- `.iter()` creates a reference — hold multiple iterators of the same collection
- For summing, prefer `.sum()` over `.fold()` — `.sum()` is specialized for optimization

### Avoid Intermediate Collections

```rust
// Bad: useless allocation
let doubled: Vec<_> = items.iter().map(|x| x * 2).collect();
process(doubled);

// Good: pass the iterator
let doubled_iter = items.iter().map(|x| x * 2);
process(doubled_iter);
```

## String Performance

- Prefer `s.bytes()` over `s.chars()` for ASCII-only operations
- `contains()` on strings is O(n*m) — avoid nested string iteration
- Use `format!` over `+` concatenation (avoids intermediate allocations)
