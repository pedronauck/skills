# Coding Style and Idioms

## Borrowing Over Cloning

Prefer `&T` over `.clone()`. Use `&str` over `String`, `&[T]` over `Vec<T>` in function parameters.

```rust
// Good: borrows
fn process(name: &str) {
    println!("Hello {name}");
}

// Bad: unnecessary ownership
fn process_string(name: String) {
    println!("Hello {name}");
}
```

### Clone Traps to Avoid

- Auto-cloning in loops: prefer `.cloned()` or `.copied()` at the end of the iterator chain
- Cloning large data structures like `Vec<T>` or `HashMap<K, V>`
- Cloning because of bad API design instead of adjusting lifetimes
- Cloning a reference argument — if ownership is needed, make it explicit in the function signature

### When to Clone

- Immutable snapshots (need to change AND preserve the original)
- Reference-counted pointers (`Arc`, `Rc`)
- Sharing data across threads (usually `Arc`)
- When the underlying API requires owned data
- Caching results

## Copy Trait

Small types (<=24 bytes) with all `Copy` fields and no heap allocations should derive `Copy`:

```rust
// Good: small, all fields Copy
#[derive(Debug, Copy, Clone)]
struct Point { x: f32, y: f32, z: f32 }

// Bad: String is not Copy
#[derive(Debug, Clone)]
struct BadIdea { age: i32, name: String }
```

Enums can derive `Copy` when they act as tags and all payloads are `Copy`. Enum size equals the largest variant.

Primitive type sizes: `i8/u8`: 1B, `i16/u16`: 2B, `i32/u32`: 4B, `i64/u64`: 8B, `i128/u128`: 16B, `f32`: 4B, `f64`: 8B, `bool`: 1B, `char`: 4B, `isize/usize`: arch-dependent.

## Naming Conventions

| Convention | Rule |
|-----------|------|
| General | `snake_case` (fn/var), `CamelCase` (type), `SCREAMING_CASE` (const) |
| No `get_` prefix | `fn name()` not `fn get_name()` |
| Iterator methods | `iter()` / `iter_mut()` / `into_iter()` |
| Conversions | `as_` (cheap borrow &), `to_` (expensive/cloning), `into_` (ownership transfer) |
| Static variables | `G_CONFIG` prefix for `static`, no prefix for `const` |

## Option and Result Pattern Matching

Use `match` when pattern matching against inner types:
```rust
match self {
    Ok(Direction::South) => { /* ... */ },
    Ok(Direction::North) => { /* ... */ },
    Err(E::One) => { /* ... */ },
}
```

Use `let...else` for early returns when the missing case is expected:
```rust
let Some(value) = optional else { return Err(MyError::Missing); };
```

Use `if let...else` when recovery requires extra computation:
```rust
if let Some(x) = self.next() {
    // computation
} else {
    // computation when None
}
```

Bad patterns to avoid:
- Converting between Result and Option manually — use `.ok()`, `.ok_or()`, `.ok_or_else()`
- Using `unwrap`/`expect` outside tests

## Iterators vs For Loops

Both are idiomatic. Each excels in different contexts.

### Prefer `for` loops when:
- Early exits needed (`break`, `continue`, `return`)
- Simple iteration with side effects
- Readability matters more than chaining

### Prefer iterators when:
- Transforming collections or Option/Results
- Composing multiple steps elegantly
- Using `.enumerate()`, `.windows()`, `.chunks()`
- Combining data from multiple sources without intermediate allocation

```rust
// Iterator style
let sum: i32 = (0..=10).filter(|x| x % 2 == 0).map(|x| x + 1).sum();
```

### Anti-patterns:
- Needless `.collect()` just to iterate again — pass the iterator directly
- Using `into_iter` when `iter` suffices (don't take ownership unnecessarily)
- For summing, prefer `.sum()` over `.fold()` — `.sum()` is specialized for optimization

Iterators are **lazy**: `.iter`, `.map`, `.filter` don't execute until consumed (`.collect`, `.sum`, `.for_each`).

## String Handling

- Prefer `s.bytes()` over `s.chars()` for ASCII-only operations
- Use `Cow<str>` when data might need modification of borrowed data
- Use `format!` over string concatenation with `+`
- `contains()` on strings is O(n*m) — avoid nested string iteration

## Import Ordering

Standard order, enforceable via `rustfmt.toml`:

1. `std` (`core`, `alloc`)
2. External crates (from `Cargo.toml [dependencies]`)
3. Workspace crates
4. `super::`
5. `crate::`

```rust
use std::sync::Arc;

use chrono::Utc;
use uuid::Uuid;

use broker::database::PooledConnection;

use super::schema::{Context, Payload};
use crate::models::Event;
```

`rustfmt.toml` config:
```toml
reorder_imports = true
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

As of Rust 1.88, execute `cargo +nightly fmt` for correct reordering.

## Comments: Context, Not Clutter

Comments explain **why**, not what or how. Well-written code with expressive types speaks for itself.

### Good comments:
```rust
// SAFETY: pointer is guaranteed non-null and aligned by caller
unsafe { std::ptr::copy_nonoverlapping(src, dst, len); }

// PERF: Root store per subgraph caused high TLS startup latency on MacOS
// See: [ADR-123](link/to/adr-123)
```

### Bad comments:
- Wall-of-text explanations
- Restating obvious code (`// increment i by 1`)
- Comments that could be replaced by better naming or extracted functions

### Replace comments with code:
```rust
// Instead of commenting each step:
fn process_request(request: T) -> Result<(), Error> {
    validate_request_headers(&request)?;
    let payload = decode_payload(&request);
    authorize(&payload)?;
    dispatch_to_handler(payload)
}
```

### TODOs:
Turn `TODO`s into tracked issues. Reference in code:
```rust
// TODO(#42): Remove workaround after bugfix
```

## Macros

- Avoid macros unless necessary; prefer functions or generics
- Macro input should look like valid Rust syntax
- Use macros only when compile-time code generation or syntax extension is genuinely needed

## Newtypes and Data Patterns

- Use newtypes for domain semantics: `struct Email(String)`
- Prefer slice patterns: `if let [first, .., last] = slice`
- Use arrays for fixed sizes; avoid `Vec` when length is known at compile time
- Use shadowing for transformations: `let x = x.parse()?`
- Pre-allocate collections: `Vec::with_capacity()`, `String::with_capacity()`
