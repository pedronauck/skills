---
name: rust-best-practices
description: "Write, review, refactor, or optimize Rust, including ownership, errors, Tokio, traits, tests, benchmarks, Clippy, and documentation. Excludes other languages and architecture unrelated to Rust idioms."
license: MIT
compatibility: Cargo; honor the repository edition, pinned toolchain, and minimum supported Rust version
metadata:
  version: "2.1.0"
  domain: language
  triggers: Rust, Cargo, ownership, borrowing, lifetimes, async Rust, tokio, zero-cost abstractions, memory safety, systems programming, traits, generics, error handling, thiserror, anyhow, clippy, rustfmt, testing, benchmarks
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
allowed-tools: Bash(cargo:*) Bash(rustc:*) Bash(rustfmt:*) Bash(clippy:*) Read Write Edit Glob Grep
---
# Rust Best Practices

Use the existing crate design, edition, `rust-toolchain.toml`, and `Cargo.toml` `rust-version` (MSRV). Reference examples may use newer features: confirm support before adopting them; do not upgrade the toolchain or add a crate just to follow an example.

Read the reference for the Rust concern being changed. A local edit does not require every category, a new test framework, or a workspace-wide audit.

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

## Engineering floor

- Borrow or transfer ownership deliberately; clone when independent ownership is needed. Prefer clear ownership over numeric size rules or avoiding every allocation.
- Handle fallible operations with `Result` and preserve useful error context. Reserve panic/assertions for violated programmer invariants; validate external input with recoverable errors.
- Match error types, dispatch, and dependencies to the existing public contract. `thiserror`, `anyhow`, Tokio, and third-party synchronization crates are options, not mandatory additions.
- Keep lock lifetimes short, maintain lock order, and reason about cancellation, shutdown, and spawned-task ownership. Do not hold a synchronous lock across `.await`.
- Treat `Send`/`Sync` bounds and atomic orderings as correctness properties. Choose weaker ordering only with a valid synchronization argument; benchmark before performance-driven rewrites.
- Put behavior tests in the suite that owns the invariant. Add type-level, property, fuzz, snapshot, or benchmark tests when that contract or risk warrants them.
- Run the repository's required scoped format, lint, and test commands; reuse valid evidence. Full workspace/all-feature runs and documentation coverage rules follow project policy. Check feature combinations actually supported by the crate.
