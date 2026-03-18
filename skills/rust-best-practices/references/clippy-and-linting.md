# Clippy and Linting Discipline

## Why Clippy

`cargo clippy` catches issues the compiler misses:
- Performance pitfalls
- Style issues and non-idiomatic Rust
- Redundant code
- Potential bugs

## Always Run Clippy

Add to daily workflow and CI:

```bash
cargo clippy --all-targets --all-features --locked -- -D warnings
```

- `--all-targets`: checks library, tests, benches, examples
- `--all-features`: checks code for all features
- `--locked`: requires up-to-date `Cargo.lock`
- `-D warnings`: treats warnings as errors

Optional additions:
- `-- -W clippy::pedantic`: stricter lints (occasional false positives)
- `-- -W clippy::nursery`: new lints under development

## Important Lints

| Lint | Why | Category |
|------|-----|----------|
| `redundant_clone` | Unnecessary `.clone()`, performance impact | nursery + perf |
| `needless_borrow` | Redundant `&` borrowing | style |
| `map_unwrap_or` | Simplifies nested `Option/Result` handling | pedantic |
| `manual_ok_or` | Suggests `.ok_or_else` instead of `match` | style |
| `large_enum_variant` | Oversized variant — suggests `Box`ing | perf |
| `unnecessary_wraps` | Function always returns `Some`/`Ok` | pedantic |
| `clone_on_copy` | `.clone()` on `Copy` types | complexity |
| `needless_collect` | Collecting iterator when allocation not needed | nursery |

## Fix Warnings, Don't Silence Them

**Never** use `#[allow(clippy::lint)]` unless:
1. The warning is understood and justified
2. The justification is documented

Use `#[expect(...)]` instead of `#[allow(...)]` — `expect` warns when the lint no longer applies:

```rust
// Faster matching is preferred over size efficiency
#[expect(clippy::large_enum_variant)]
enum Message {
    Code(u8),
    Content([u8; 1024]),
}
```

### Handling False Positives

1. Try to refactor the code to satisfy the lint
2. If refactoring is not feasible, **locally** override with `#[expect(clippy::lint_name)]` and a reason comment
3. Avoid global overrides unless it is a core crate concern

## Workspace and Package Lint Configuration

Configure in `Cargo.toml` with priority levels. Higher priority wins on conflicts:

### Package-level:
```toml
[lints.rust]
future-incompatible = "warn"
nonstandard_style = "deny"

[lints.clippy]
all = { level = "deny", priority = 10 }
redundant_clone = { level = "deny", priority = 9 }
pedantic = { level = "warn", priority = 3 }
```

### Workspace-level:
```toml
[workspace.lints.rust]
future-incompatible = "warn"
nonstandard_style = "deny"

[workspace.lints.clippy]
all = { level = "warn", priority = -1 }
pedantic = { level = "warn", priority = -1 }
```

Minimum baseline: `#![warn(clippy::all)]` in every crate.
