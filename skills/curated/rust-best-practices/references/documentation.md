# Comments and Documentation

## Comments vs Documentation

| Purpose | `// comment` | `/// doc` or `//! crate doc` |
|---------|-------------|------------------------------|
| Describe Why | Yes — tricky reasoning | Not for this |
| Describe API | Not useful | Yes — public interfaces |
| Maintainability | Often becomes obsolete | Tied to code, testable |
| Visibility | Local only | Exported to users and `cargo doc` |

## When to Use `//` Comments

Use when something can't be expressed clearly in code:

- **Safety guarantees**: `// SAFETY: pointer is guaranteed non-null by caller`
- **Workarounds or optimizations**: `// PERF: caching to avoid repeated OS calls`
- **Legacy or platform-specific** behaviors
- **Links to Design Docs or ADRs**: `// CONTEXT: See [ADR-12](link)`
- **Assumptions or gotchas** that aren't obvious

Name your comments: `// SAFETY: ...`, `// PERF: ...`, `// CONTEXT: ...`

## When Comments Hurt

Avoid comments that:
- Restate obvious code (`// increment i by 1`)
- Could be replaced by better naming or smaller functions
- Are long and likely to become stale
- Are `TODO`s without tracked issues

### Replace Comments with Code

```rust
// Instead of commenting each step:
fn process_request(request: T) -> Result<(), Error> {
    validate_request_headers(&request)?;
    let payload = decode_payload(&request);
    authorize(&payload)?;
    dispatch_to_handler(payload)
}
```

### Comments as "Living Documentation" Is Dangerous

- Comments **rot** — nobody compiles them
- Comments **mislead** — readers assume they are true
- Comments **go stale** — unless maintained with the code

If something deserves to persist, put it in:
- An **ADR** (Architectural Decision Record)
- A Design Document
- **Doc comments** (`///`) where they can be tested
- Tests that cover and explain the behavior

## TODO Policy

Don't leave `// TODO:` without a tracked issue:

```rust
// TODO(#42): Remove workaround after bugfix
```

## Doc Comments: `///` and `//!`

### `///` — Item-Level Documentation

For functions, structs, traits, enums, constants:

```rust
/// Loads a [`User`] profile from disk.
///
/// # Errors
/// - Returns [`MyError::FileNotFound`] if the file is missing.
/// - Returns [`MyError::InvalidJson`] if content is invalid JSON.
///
/// # Examples
///
/// ```rust
/// # use my_crate::load_user;
/// let user = load_user(std::path::Path::new("user.json")).unwrap();
/// ```
pub fn load_user(path: &std::path::Path) -> Result<User, MyError> { /* ... */ }
```

Guidelines:
- Write clear **what it does** and **how to use it**
- Include `# Examples` that can run as tests via `cargo test`
- Use `# Panics`, `# Errors`, `# Safety` sections when relevant
- Hide boilerplate in examples with `#` prefix

### `//!` — Module/Crate-Level Documentation

Place at the top of `lib.rs` or `mod.rs`:

```rust
//! This module implements a custom chess engine.
//!
//! It handles board state, move generation and check detection.
//!
//! # Example
//! ```
//! let board = chess::engine::Board::default();
//! assert!(board.is_valid());
//! ```
```

## Documentation Lints

| Lint | Description |
|------|-------------|
| `missing_docs` | Public items missing documentation |
| `broken_intra_doc_links` | Broken internal `[`links`]` in docs |
| `empty_docs` | Prevents bypassing `missing_docs` with empty comments |
| `missing_panics_doc` | Functions that can panic need `# Panics` section |
| `missing_errors_doc` | Functions returning `Result` need `# Errors` section |
| `missing_safety_doc` | Unsafe functions need `# Safety` section |

Enable in libraries: `#![deny(missing_docs)]`

## Documentation Coverage Checklist

### Crate-Level (`lib.rs`)
- `//!` doc explains what the crate does and what problems it solves
- Includes `# Examples` or pointers to modules

### Modules (`mod.rs`)
- `//!` doc explains what the module is for, its exports, and invariants
- Avoid repeating docs on re-exported items

### Structs, Enums, Traits
- `///` doc explains the role, invariants, and example usage
- Consider `#[non_exhaustive]` for enums external users may match on

### Functions and Methods
- `///` covers: what it does, parameters, return value, edge cases
- Include `# Examples`, `# Panics`, `# Errors` where applicable

### Traits
- Explain the purpose (marker? dynamic dispatch?)
- Document each method — when/why to implement it
- Document default implementations and when to override

### Public Constants
- Document what they configure and when to use them

## Best Practices

- Use examples generously — they double as test cases
- Prefer clarity over formality
- Use `cargo doc --open` to check output often
- Add relevant doc lints to enforce coverage
