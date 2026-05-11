---
name: rust-best-practices
description: >
  Comprehensive Rust coding guidelines covering ownership, error handling, async patterns,
  traits, testing, performance, clippy, and documentation. Use when writing new Rust code,
  reviewing or refactoring existing Rust, implementing async systems with Tokio, designing
  error hierarchies, choosing between borrowing and cloning, setting up tests or benchmarks,
  configuring linting, or optimizing performance. Do not use for non-Rust languages or
  general software architecture unrelated to Rust idioms.
license: MIT
compatibility: Rust 1.70+, Cargo
metadata:
  version: "2.0.0"
  domain: language
  triggers: Rust, Cargo, ownership, borrowing, lifetimes, async Rust, tokio, zero-cost abstractions, memory safety, systems programming, traits, generics, error handling, thiserror, anyhow, clippy, rustfmt, testing, benchmarks
allowed-tools: Bash(cargo:*) Bash(rustc:*) Bash(rustfmt:*) Bash(clippy:*) Read Write Edit Glob Grep
---

# Rust Best Practices

Unified Rust guidelines covering coding style, ownership, error handling, async patterns, traits, testing, performance, linting, and documentation. Apply when writing or reviewing Rust code.

## When to Apply

- Writing new Rust code or designing APIs
- Reviewing or refactoring existing Rust code
- Implementing async systems with Tokio
- Designing error hierarchies with thiserror/anyhow
- Choosing between borrowing, cloning, or ownership transfer
- Setting up tests, benchmarks, or snapshot testing
- Configuring clippy lints and workspace settings
- Optimizing Rust code for performance

## Reference Guide

Load detailed guidance based on context. Read the relevant file when the topic arises:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Coding Style | `references/coding-style.md` | Naming, imports, iterators, comments, string handling, macros |
| Error Handling | `references/error-handling.md` | Result, Option, ?, thiserror, anyhow, custom errors, async errors |
| Ownership & Pointers | `references/ownership-and-pointers.md` | Lifetimes, borrowing, smart pointers, Pin, Cow, interior mutability |
| Traits & Generics | `references/traits-and-generics.md` | Trait design, dispatch, GATs, sealed traits, type state pattern |
| Async & Concurrency | `references/async-and-concurrency.md` | Tokio, channels, streams, shutdown, runtime config, async traits |
| Sync Concurrency | `references/concurrency-sync.md` | Atomics, Mutex, RwLock, lock ordering, Send/Sync, memory ordering |
| Testing | `references/testing.md` | Unit/integration/doc tests, snapshot, proptest, mockall, benchmarks, fuzz |
| Performance | `references/performance.md` | Profiling, flamegraph, cloning, stack vs heap, iterators, allocation |
| Clippy & Linting | `references/clippy-and-linting.md` | Clippy config, key lints, workspace setup, #[expect] vs #[allow] |
| Documentation | `references/documentation.md` | Doc comments, rustdoc, doc lints, coverage checklist |

## Quick Reference: Coding Style

- Prefer `&T` over `.clone()` unless ownership transfer is required
- Use `&str` over `String`, `&[T]` over `Vec<T>` in function parameters
- No `get_` prefix on getters: `fn name()` not `fn get_name()`
- Conversion naming: `as_` (cheap borrow), `to_` (expensive/cloning), `into_` (ownership transfer)
- Iterator methods: `iter()` / `iter_mut()` / `into_iter()`
- Import ordering: `std` -> external crates -> workspace crates -> `super::` -> `crate::`
- Comments explain *why* (safety, workarounds), not *what*
- Use `format!` over string concatenation with `+`
- Prefer `s.bytes()` over `s.chars()` for ASCII-only operations
- Avoid macros unless necessary; prefer functions or generics

## Quick Reference: Error Handling

- Return `Result<T, E>` for fallible operations; reserve `panic!` for unrecoverable bugs
- **No `unwrap()` in production.** Use `expect()` with descriptive message only when the value is logically guaranteed. Prefer `?`, `if let`, `let...else` for all other cases
- Use `thiserror` for library/crate errors, `anyhow` for binaries only
- Prefer `?` operator over `match` chains for error propagation
- Use `_else` variants (`ok_or_else`, `unwrap_or_else`) to prevent eager allocation
- Use `inspect_err` and `map_err` for logging and transforming errors
- `assert!` at function entry for invariant checking (debug builds)

## Quick Reference: Ownership & Pointers

- Small `Copy` types (<=24 bytes, all fields `Copy`, no heap) pass by value
- Use `Cow<'_, T>` when data may or may not need ownership
- Meaningful lifetime names: `'src`, `'ctx`, `'conn` — not just `'a`
- Use `try_borrow()` on `RefCell` to avoid panics; prefer over direct `.borrow_mut()`
- Shadowing for transformations: `let x = x.parse()?`

| Pointer | When to Use |
|---------|-------------|
| `Box<T>` | Single ownership, heap allocation, recursive types |
| `Rc<T>` | Shared ownership, single-threaded |
| `Arc<T>` | Shared ownership, multi-threaded |
| `Cell<T>` / `RefCell<T>` | Interior mutability, single-threaded |
| `Mutex<T>` / `RwLock<T>` | Interior mutability, multi-threaded |

## Quick Reference: Traits & Generics

- Prefer generics (static dispatch) by default for zero-cost abstractions
- Use `dyn Trait` only when heterogeneous collections or plugin architectures are needed
- Box at API boundaries, not internally
- Object safety: no generic methods, no `Self: Sized`, methods use `&self`/`&mut self`/`self`
- Use sealed traits to prevent external implementors
- Type state pattern encodes valid states in the type system:

```rust
struct Connection<S> { _state: PhantomData<S> }
struct Disconnected;
struct Connected;
impl Connection<Connected> { fn send(&self, data: &[u8]) { /* ... */ } }
```

## Quick Reference: Async & Concurrency

- Async for I/O-bound work, sync for CPU-bound work
- Never hold locks across `.await` points — use scoped guards
- Never use `std::thread::sleep` in async — use `tokio::time::sleep`
- Never spawn unboundedly — use semaphores for limits
- Ensure `Send` bounds on spawned futures
- Use `JoinSet` for managing multiple concurrent tasks
- Use `CancellationToken` (from `tokio_util`) for graceful shutdown
- Instrument with `tracing` + `#[instrument]` for async debugging

| Channel | Use Case |
|---------|----------|
| `mpsc` | Multi-producer, single-consumer message passing |
| `broadcast` | Multi-producer, multi-consumer event fan-out |
| `oneshot` | Single value, single use (request-response) |
| `watch` | Latest-value-only, change notification |

- Sync channels: `crossbeam::channel` over `std::sync::mpsc`
- Async channels: `tokio::sync::{mpsc, broadcast, oneshot, watch}`
- Atomics (`AtomicBool`, `AtomicUsize`) over `Mutex` for primitive types
- Choose memory ordering carefully: `Relaxed` / `Acquire` / `Release` / `SeqCst`

## Quick Reference: Testing

- Name tests descriptively: `process_should_return_error_when_input_empty()`
- One assertion per test when possible; include formatted failure messages
- Group tests in `mod` blocks by unit of work
- Use doc tests (`///`) for public API examples; run separately with `cargo test --doc`
- Snapshot testing: `cargo insta test` then `cargo insta review`; redact unstable fields
- `rstest` for parameterized tests with `#[case::name]` labels
- `proptest` for property-based testing with custom strategies
- `mockall` with `#[automock]` for mocking traits
- `criterion` for benchmarks with `iter_batched` and `BenchmarkId`
- `cargo-fuzz` with `libfuzzer_sys` for fuzz testing
- `cargo-tarpaulin` or `cargo-llvm-cov` for code coverage
- `sqlx::test` for database integration tests with automatic pool injection
- Use `#[should_panic]` and `#[ignore]` attributes where appropriate

## Quick Reference: Performance

- Golden rule: don't guess, measure. Always benchmark with `--release`
- Run `cargo clippy -- -D clippy::perf` for performance-related hints
- Use `cargo flamegraph` or `samply` (macOS) for profiling
- Avoid cloning in loops; clone at the last moment only
- Pre-allocate: `Vec::with_capacity()`, `String::with_capacity()`
- Prefer iterators over manual `for` loops; avoid intermediate `.collect()`
- Stack for small types, heap for large/recursive; use `smallvec` for large const arrays
- Use `Cow<'_, T>` to avoid unnecessary allocation
- Prefer `s.bytes()` over `s.chars()` for ASCII-only string operations

## Quick Reference: Clippy & Linting

Run regularly:
```
cargo clippy --all-targets --all-features --locked -- -D warnings
```

| Lint | Catches |
|------|---------|
| `redundant_clone` | Unnecessary `.clone()` calls |
| `needless_borrow` | Unnecessary `&` borrows |
| `large_enum_variant` | Oversized variants (consider `Box`) |
| `needless_collect` | Premature `.collect()` before iteration |
| `map_unwrap_or` | `.map().unwrap_or()` chains |
| `unnecessary_wraps` | Functions always returning `Ok`/`Some` |
| `clone_on_copy` | `.clone()` on `Copy` types |

- Use `#[expect(clippy::lint)]` over `#[allow(...)]` — `expect` warns when lint no longer applies
- Add justification comment on every suppression
- Set `#![warn(clippy::all)]` as workspace minimum
- Configure workspace lints in `Cargo.toml` with priority levels

## Quick Reference: Documentation

- `//` comments explain *why*: safety invariants, workarounds, design rationale
- `///` doc comments explain *what* and *how* for all public items
- `//!` for module-level and crate-level documentation at top of `lib.rs`/`mod.rs`
- Every `TODO` needs a linked issue: `// TODO(#42): description`
- Enable `#![deny(missing_docs)]` for libraries
- Include `# Examples`, `# Errors`, `# Panics`, `# Safety` sections in doc comments

| Doc Lint | Purpose |
|----------|---------|
| `missing_docs` | Ensure all public items documented |
| `broken_intra_doc_links` | Catch dead cross-references |
| `missing_panics_doc` | Document panic conditions |
| `missing_errors_doc` | Document error conditions |
| `missing_safety_doc` | Document unsafe safety requirements |

## Quick Reference: Data Types & Patterns

- Use newtypes for domain semantics: `struct Email(String)`
- Prefer slice patterns: `if let [first, .., last] = slice`
- Use arrays for fixed sizes; avoid `Vec` when length is known at compile time
- Shadowing for transformation: `let x = x.parse()?`
- `Cow<str>` when data might need modification of borrowed data
- `contains()` on strings is O(n*m) — avoid nested string iteration

## Deprecated to Modern Migration

| Deprecated | Better | Since |
|------------|--------|-------|
| `lazy_static!` | `std::sync::OnceLock` | Rust 1.70 |
| `once_cell::Lazy` | `std::sync::LazyLock` | Rust 1.80 |
| `std::sync::mpsc` | `crossbeam::channel` (sync) | — |
| `std::sync::Mutex` | `parking_lot::Mutex` (recommended) | — |
| `failure` / `error-chain` | `thiserror` / `anyhow` | — |
| `try!()` | `?` operator | Rust 2018 |
| `async-trait` crate | Native `async fn` in traits (1.75+, limited) | Rust 1.75 |

## Cargo.toml Essentials

Recommended dependencies:
```toml
[dependencies]
thiserror = "2"
anyhow = "1"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
tracing = "0.1"
tracing-subscriber = "0.3"

[dev-dependencies]
rstest = "0.25"
proptest = "1"
mockall = "0.13"
criterion = { version = "0.5", features = ["html_reports"] }
insta = { version = "1", features = ["yaml"] }
```

Workspace lints (`Cargo.toml`):
```toml
[workspace.lints.clippy]
all = { level = "warn", priority = -1 }
pedantic = { level = "warn", priority = -1 }
```

`rustfmt.toml`:
```toml
reorder_imports = true
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

## Constraints

### MUST DO
1. Use ownership and borrowing for memory safety
2. Handle all errors explicitly via `Result`/`Option` — no silent failures
3. Use `thiserror` for library errors, `anyhow` for binaries
4. Minimize `unsafe` code; document all `unsafe` blocks with safety invariants
5. Use the type system for compile-time guarantees
6. Run `cargo clippy` and fix all warnings
7. Use `cargo fmt` for consistent formatting
8. Write tests including doc tests for public APIs
9. Add `///` documentation with examples for all public items
10. Use `tracing` for observability in async code
11. When reviewing or writing code, suggest a testing approach using the recommended tools (`rstest`, `proptest`, `insta`, `mockall`, `criterion`) — even if the user did not ask for tests

### MUST NOT DO
1. Use `unwrap()` in production code
2. Create memory leaks or dangling pointers
3. Use `unsafe` without documented safety invariants
4. Ignore clippy warnings without `#[expect(...)]` and justification
5. Hold locks across `.await` points
6. Use `std::thread::sleep` in async context
7. Skip error handling or use `panic!` for recoverable errors
8. Use `String` where `&str` suffices; clone unnecessarily
9. Spawn tasks unboundedly without semaphore limits
10. Mix blocking and async code without `spawn_blocking`
