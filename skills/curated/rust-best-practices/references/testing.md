# Testing

## Test Naming and Organization

Use descriptive names that read like sentences:

```rust
#[cfg(test)]
mod tests {
    mod process {
        #[test]
        fn should_return_error_when_input_empty() { /* ... */ }

        #[test]
        fn should_return_blob_when_larger_than_b() { /* ... */ }
    }
}
```

Naming scheme: `unit_of_work` + `expected_behavior` + `state_under_test`.

### One Assertion Per Test

Keeps tests clear and debugging straightforward:

```rust
// Good: one thing per test
#[test]
fn lowercase_letters_are_valid() {
    assert!(Thing::parse("abcd").is_ok(), "Parse error: {:?}", Thing::parse("abcd").unwrap_err());
}

#[test]
fn capital_letters_are_invalid() {
    assert!(Thing::parse("ABCD").is_err());
}
```

Include formatted failure messages in assertions:
```rust
assert_eq!(result, expected, "'result' differs: {}", result.diff(expected));
```

Use `matches!` for pattern matching without exact value:
```rust
assert!(matches!(error, MyError::BadInput(_)), "Expected BadInput, found {error}");
```

## Parameterized Tests with rstest

Avoid boilerplate for similar tests:
```rust
use rstest::rstest;

#[rstest]
#[case::single("a")]
#[case::first_letter("ab")]
#[case::last_letter("ba")]
#[case::in_the_middle("bab")]
fn accepts_all_strings_with_a(#[case] input: &str) {
    assert!(the_function(input).is_ok());
}
```

## Unit Tests

Tests in the same module as the tested unit. Access to private functions and `pub(crate)` items.

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unit_state_behavior() {
        let expected = /* ... */;
        let result = /* ... */;
        assert_eq!(result, expected, "Failed because {}", result - expected);
    }
}
```

- Keep tests simple — KISS
- Test errors and edge cases
- Use `#[ignore = "message"]` for incomplete tests
- Use `#[should_panic]` when panic is the expected behavior

## Integration Tests

External tests in `tests/` directory. Only test the public API:

```
tests/
  common/
    mod.rs          # shared utilities
  integration_test.rs
```

```rust
// tests/integration_test.rs
mod common;

#[test]
fn test_full_workflow() {
    let ctx = common::setup();
    let result = mylib::process(&ctx.config);
    assert!(result.is_ok());
}
```

Use `testcontainers` for external dependencies (databases, etc.).

## Doc Tests

Examples in `///` doc comments that run as tests:

```rust
/// Adds two numbers.
///
/// # Examples
///
/// ```rust
/// # use crate_name::add;
/// assert_eq!(add(2, 3), 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

- Run with `cargo test` but **NOT** `cargo nextest run` — use `cargo test --doc` separately
- Hide boilerplate with `#` prefix
- No issue if doc-tests duplicate unit tests

Doc test attributes:
- `should_panic` — block will panic
- `no_run` — compiles but doesn't execute
- `compile_fail` — demonstrates wrong usage
- `ignore` — skip execution

## Test Fixtures with Drop

```rust
struct TestContext {
    temp_dir: std::path::PathBuf,
    db: Database,
}

impl TestContext {
    fn setup() -> Self {
        let temp_dir = std::env::temp_dir().join("test");
        std::fs::create_dir_all(&temp_dir).unwrap();
        Self { temp_dir, db: Database::connect_test() }
    }
}

impl Drop for TestContext {
    fn drop(&mut self) {
        std::fs::remove_dir_all(&self.temp_dir).ok();
        self.db.disconnect();
    }
}
```

## Async Tests

```rust
#[tokio::test]
async fn test_async_function() {
    let result = async_operation().await;
    assert_eq!(result, 42);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn test_with_custom_runtime() {
    let result = concurrent_operation().await;
    assert!(result.is_ok());
}
```

## Snapshot Testing with insta

```toml
[dev-dependencies]
insta = { version = "1", features = ["yaml"] }
```

Use YAML snapshots for best version control diffs. Install CLI: `cargo install cargo-insta`.

```rust
#[test]
fn test_split_words() {
    let words = split_words("hello from the other side");
    insta::assert_yaml_snapshot!(words);
}
```

Workflow: `cargo insta test` then `cargo insta review`.

### Best Practices:
- Use named snapshots: `assert_snapshot!("config/http", config.http)`
- Keep snapshots small — don't snapshot huge objects
- Don't snapshot primitives — use `assert_eq!` instead
- Redact unstable fields (timestamps, UUIDs):
```rust
insta::assert_json_snapshot!(data, {
    ".created_at" => "[timestamp]",
    ".id" => "[uuid]"
});
```
- Commit snapshots to git
- Review changes carefully before accepting

## Property-Based Testing with proptest

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn reversing_twice_is_identity(ref s in ".*") {
        let reversed: String = s.chars().rev().collect();
        let double_reversed: String = reversed.chars().rev().collect();
        assert_eq!(s, &double_reversed);
    }

    #[test]
    fn addition_is_commutative(a in 0..1000i32, b in 0..1000i32) {
        assert_eq!(a + b, b + a);
    }
}
```

### Custom Strategies

```rust
fn user_strategy() -> impl Strategy<Value = User> {
    (1..1000u64, "[a-z]{3,10}", "[a-z0-9.]+@[a-z]+\\.[a-z]+")
        .prop_map(|(id, name, email)| User { id, name, email })
}

proptest! {
    #[test]
    fn user_serialization_roundtrip(user in user_strategy()) {
        let json = serde_json::to_string(&user).unwrap();
        let deserialized: User = serde_json::from_str(&json).unwrap();
        assert_eq!(user, deserialized);
    }
}
```

## Mocking with mockall

```rust
use mockall::*;
use mockall::predicate::*;

#[automock]
trait Database {
    fn get_user(&self, id: u64) -> Option<User>;
    fn save_user(&mut self, user: User) -> Result<(), Error>;
}

#[test]
fn test_with_mock() {
    let mut mock = MockDatabase::new();

    mock.expect_get_user()
        .with(eq(1))
        .times(1)
        .returning(|_| Some(User { id: 1, name: "Alice".to_string() }));

    let user = mock.get_user(1);
    assert!(user.is_some());
}
```

## Benchmarks with criterion

```rust
// benches/my_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};

fn criterion_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

// Multiple sizes
fn bench_sizes(c: &mut Criterion) {
    let mut group = c.benchmark_group("sorting");
    for size in [10, 100, 1000, 10000] {
        group.bench_with_input(BenchmarkId::from_parameter(size), &size, |b, &size| {
            b.iter_batched(
                || generate_random_vec(size),
                |mut v| v.sort(),
                criterion::BatchSize::SmallInput,
            );
        });
    }
    group.finish();
}

criterion_group!(benches, criterion_benchmark, bench_sizes);
criterion_main!(benches);
```

```toml
# Cargo.toml
[[bench]]
name = "my_benchmark"
harness = false
```

## Database Tests with sqlx

```rust
#[sqlx::test]
async fn test_database_operations(pool: sqlx::PgPool) -> sqlx::Result<()> {
    sqlx::query("INSERT INTO users (name) VALUES ($1)")
        .bind("Alice")
        .execute(&pool)
        .await?;

    let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM users")
        .fetch_one(&pool)
        .await?;

    assert_eq!(count.0, 1);
    Ok(())
}
```

## Fuzzing

```rust
// fuzz/fuzz_targets/fuzz_target_1.rs
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    if let Ok(s) = std::str::from_utf8(data) {
        let _ = mylib::parse_input(s);
    }
});
```

Setup and run:
```bash
cargo install cargo-fuzz
cargo fuzz init
cargo fuzz run fuzz_target_1
```

## Code Coverage

```bash
# Using tarpaulin
cargo install cargo-tarpaulin
cargo tarpaulin --out Html --output-dir coverage

# Using llvm-cov
cargo install cargo-llvm-cov
cargo llvm-cov --html
```

## Best Practices

- Write tests alongside production code in `#[cfg(test)]` modules
- Use integration tests in `tests/` for end-to-end testing
- Include doctests for public API examples
- Use descriptive test names explaining what is being tested
- Test edge cases (empty inputs, max values, boundaries)
- Use property-based testing for algorithmic code
- Benchmark performance-critical code with criterion
- Run tests in CI with `cargo test --all-features`
- Run clippy on test code too
- Measure coverage and aim for high coverage on critical paths
- Use fuzzing for security-critical parsers
