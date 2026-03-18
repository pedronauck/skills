# Error Handling

## Prefer Result, Avoid Panic

Return `Result<T, E>` for fallible operations. Reserve `panic!` for unrecoverable bugs:

```rust
fn divide(x: f64, y: f64) -> Result<f64, DivisionError> {
    if y == 0.0 {
        Err(DivisionError::DividedByZero)
    } else {
        Ok(x / y)
    }
}
```

Alternatives to `panic!`:
- `todo!()` — alerts the compiler that code is missing
- `unreachable!()` — asserts a condition is impossible
- `unimplemented!()` — alerts a block is not yet implemented

## Unwrap and Expect Policy

**No `unwrap()` in production code.** Use `expect()` with descriptive message only when the value is logically guaranteed. Prefer `?`, `if let`, `let...else` for all other cases.

### Alternatives to unwrap/expect:

Use `let...else` for early returns without needing the error value:
```rust
let Ok(json) = serde_json::from_str(&input) else {
    return Err(MyError::InvalidJson);
};
```

Use `if let...else` when recovery requires computation:
```rust
if let Ok(json) = serde_json::from_str(&input) {
    // computation
} else {
    Err(do_something_with_input(&input))
}
```

Use `unwrap_or`, `unwrap_or_else`, or `unwrap_or_default` for fallback values.

Use `assert!` at function entry for invariant checking (panics in debug, can be optimized away in release).

## The `?` Operator

Prefer `?` over verbose `match` chains for error propagation:

```rust
fn handle_request(req: &Request) -> Result<ValidatedRequest, MyError> {
    validate_headers(req)?;
    validate_body_format(req)?;
    validate_credentials(req)?;
    let body = Body::try_from(req)?;
    Ok(ValidatedRequest::try_from((req, body))?)
}
```

For error recovery, use `or_else`, `map_err`, or `if let Ok(..) else`. To inspect or log errors, use `inspect_err`.

## Prevent Early Allocation

Use `_else` variants to avoid eager allocation:

```rust
// Good: closure only runs on None
x.ok_or_else(|| ParseError::ValueAbsent(format!("value {x}")))

// Bad: format! always runs, even on Some
x.ok_or(ParseError::ValueAbsent(format!("value {x}")))
```

Same applies to `map_or` vs `map_or_else`, `unwrap_or` vs `unwrap_or_else`.

### Mapping Errors

Use `inspect_err` for logging and `map_err` for transforming:
```rust
result
    .inspect_err(|err| tracing::error!("function_name: {err}"))
    .map_err(|err| GeneralError::from(("function_name", err)))?;
```

## thiserror for Library/Crate Errors

Use `thiserror` for structured, typed errors with automatic `Display` and `From` implementations:

```rust
#[derive(Debug, thiserror::Error)]
pub enum MyError {
    #[error("Network Timeout")]
    Timeout,
    #[error("Invalid data: {0}")]
    InvalidData(String),
    #[error(transparent)]
    Serialization(#[from] serde_json::Error),
    #[error("Invalid request. Header: {headers}, Metadata: {metadata}")]
    InvalidRequest { headers: Headers, metadata: Metadata },
}
```

### Error Hierarchies

For layered systems, use nested errors with `#[from]`:
```rust
#[derive(Debug, thiserror::Error)]
pub enum ServiceError {
    #[error("Database error: {0}")]
    Db(#[from] DbError),
    #[error("Network error: {0}")]
    Network(#[from] reqwest::Error),
    #[error("Not found: {0}")]
    NotFound(String),
    #[error("Timeout after {0:?}")]
    Timeout(std::time::Duration),
}
```

### Custom Error Structs

When there is only one error type, use a struct instead of an enum:
```rust
#[derive(Debug, thiserror::Error, PartialEq)]
#[error("Request failed with code `{code}`: {message}")]
struct HttpError {
    code: u16,
    message: String,
}
```

## anyhow for Binaries Only

`anyhow` erases type info, making it unsuitable for libraries. Use only in binaries:

```rust
use anyhow::{Context, Result, bail, ensure};

fn main() -> Result<()> {
    let content = std::fs::read_to_string("config.json")
        .context("Failed to read config file")?;

    ensure!(!content.is_empty(), "File is empty");

    if content.len() > MAX_SIZE {
        bail!("File too large");
    }

    Config::from_str(&content)
        .map_err(|err| anyhow::anyhow!("Config parsing error: {err}"))
}
```

Gotchas:
- Keeping `context()` strings up-to-date across a codebase is harder than `thiserror` messages
- `anyhow::Result` erases context a caller might need — avoid in libraries
- Test helpers can use `anyhow` freely

## Error Conversion with From Trait

Implement `From` manually when not using `thiserror`:
```rust
#[derive(Debug)]
enum MyError {
    Io(io::Error),
    Parse(ParseIntError),
}

impl From<io::Error> for MyError {
    fn from(err: io::Error) -> Self { MyError::Io(err) }
}

impl From<ParseIntError> for MyError {
    fn from(err: ParseIntError) -> Self { MyError::Parse(err) }
}

// Now ? works with automatic conversion
fn read_and_parse(path: &str) -> Result<i32, MyError> {
    let content = std::fs::read_to_string(path)?;
    let number = content.trim().parse()?;
    Ok(number)
}
```

## Option and Result Combinators

```rust
// Option combinators
let doubled = Some(5).map(|n| n * 2);           // Some(10)
let chained = Some(5).and_then(|n| if n > 0 { Some(n * 2) } else { None });
let fallback = None.unwrap_or_else(|| expensive_computation());
let filtered = Some(5).filter(|&n| n > 10);     // None

// Result combinators
let mapped = Ok(5).map(|n| n * 2);              // Ok(10)
let err_mapped = Err("err").map_err(|e| e.to_uppercase());
let recovered = Err("err").or_else(|_| Ok(42));  // Ok(42)

// Converting between Option and Result
let opt: Option<i32> = Ok(5).ok();               // Some(5)
let res: Result<i32, &str> = Some(5).ok_or("missing");
```

## Async Error Handling

Ensure errors implement `Send + Sync + 'static` at `.await` boundaries:

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    Ok(())
}
```

### Timeout Wrapping Pattern

```rust
async fn with_timeout<T, F>(duration: Duration, future: F) -> Result<T, ServiceError>
where
    F: std::future::Future<Output = Result<T, ServiceError>>,
{
    tokio::time::timeout(duration, future)
        .await
        .map_err(|_| ServiceError::Timeout(duration))?
}
```

### Context Chaining with anyhow

```rust
async fn process_request(id: &str) -> anyhow::Result<Response> {
    let data = fetch_data(id).await.context("Failed to fetch data")?;
    let parsed = parse_response(&data).context("Failed to parse response")?;
    Ok(parsed)
}
```

## Advanced Patterns

### ContextError Extension Trait

Build custom context support without `anyhow`:
```rust
#[derive(thiserror::Error, Debug)]
#[error("{message}")]
struct ContextError {
    message: String,
    #[source]
    source: Option<Box<dyn Error + Send + Sync>>,
}

trait Context<T> {
    fn context(self, message: impl Into<String>) -> Result<T, ContextError>;
}

impl<T, E: Error + Send + Sync + 'static> Context<T> for Result<T, E> {
    fn context(self, message: impl Into<String>) -> Result<T, ContextError> {
        self.map_err(|e| ContextError {
            message: message.into(),
            source: Some(Box::new(e)),
        })
    }
}
```

### Try Blocks (Nightly)

```rust
#![feature(try_blocks)]

let result: Result<i32, Box<dyn Error>> = try {
    let file = std::fs::read_to_string("config.txt")?;
    let num: i32 = file.trim().parse()?;
    num * 2
};
```

### Box<dyn Error> for Multiple Sources

Use when prototyping or when precise error types are not needed:
```rust
fn complex_operation() -> Result<String, Box<dyn Error>> {
    let file = std::fs::read_to_string("data.txt")?;
    let number: i32 = file.trim().parse()?;
    Ok(format!("Number: {}", number))
}
```

Avoid `Box<dyn std::error::Error>` in libraries unless truly necessary.

## Testing Errors

Errors often don't implement `PartialEq`. Test messages with `to_string()`:
```rust
#[test]
fn error_message_is_correct() {
    let err = divide(10., 0.0).unwrap_err();
    assert_eq!(err.to_string(), "division by zero");
}

#[test]
fn error_variant_matches() {
    let err = process(my_value).unwrap_err();
    assert!(matches!(err, MyError::BadInput(_)));
}
```
