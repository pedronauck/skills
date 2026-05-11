# Async Programming and Concurrency

## Async Execution Model

```
Future (lazy) -> poll() -> Ready(value) | Pending
                  ^            |
                Waker  <-  Runtime schedules
```

| Concept    | Purpose                                  |
|------------|------------------------------------------|
| `Future`   | Lazy computation that may complete later  |
| `async fn` | Function returning `impl Future`          |
| `await`    | Suspend until future completes            |
| `Task`     | Spawned future running concurrently       |
| `Runtime`  | Executor that polls futures               |

**Core rule:** Async for I/O-bound work, sync for CPU-bound work.

## Quick Start

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
futures = "0.3"
tokio-util = "0.7"
anyhow = "1.0"
tracing = "0.1"
tracing-subscriber = "0.3"
```

```rust
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    let result = fetch_data("https://api.example.com").await?;
    println!("Got: {}", result);
    Ok(())
}
```

## Concurrent Task Execution

### JoinSet for Multiple Tasks

```rust
use tokio::task::JoinSet;

async fn fetch_all(urls: Vec<String>) -> anyhow::Result<Vec<String>> {
    let mut set = JoinSet::new();
    for url in urls {
        set.spawn(async move { fetch_data(&url).await });
    }
    let mut results = Vec::new();
    while let Some(res) = set.join_next().await {
        match res {
            Ok(Ok(data)) => results.push(data),
            Ok(Err(e)) => tracing::error!("Task failed: {}", e),
            Err(e) => tracing::error!("Join error: {}", e),
        }
    }
    Ok(results)
}
```

### Concurrency-Limited Streams

```rust
use futures::stream::{self, StreamExt};

async fn fetch_with_limit(urls: Vec<String>, limit: usize) -> Vec<anyhow::Result<String>> {
    stream::iter(urls)
        .map(|url| async move { fetch_data(&url).await })
        .buffer_unordered(limit)
        .collect()
        .await
}
```

### join! and try_join!

```rust
// Concurrent execution
let (r1, r2) = tokio::join!(operation1(), operation2());

// Stops on first error
let (r1, r2) = tokio::try_join!(fallible_op1(), fallible_op2())?;
```

### select! for Racing

```rust
async fn race_requests(url1: &str, url2: &str) -> anyhow::Result<String> {
    tokio::select! {
        result = fetch_data(url1) => result,
        result = fetch_data(url2) => result,
    }
}
```

## Channels

| Channel | Use Case |
|---------|----------|
| `mpsc` | Multi-producer, single-consumer message passing |
| `broadcast` | Multi-producer, multi-consumer event fan-out |
| `oneshot` | Single value, single use (request-response) |
| `watch` | Latest-value-only, change notification |

### mpsc

```rust
let (tx, mut rx) = tokio::sync::mpsc::channel::<String>(100);
let tx2 = tx.clone();
tokio::spawn(async move { tx2.send("Hello".to_string()).await.unwrap(); });
while let Some(msg) = rx.recv().await {
    println!("Got: {}", msg);
}
```

### broadcast

```rust
let (tx, _) = tokio::sync::broadcast::channel::<String>(100);
let mut rx1 = tx.subscribe();
let mut rx2 = tx.subscribe();
tx.send("Event".to_string()).unwrap();
// Both receivers get the message
```

### oneshot

```rust
let (tx, rx) = tokio::sync::oneshot::channel::<String>();
tokio::spawn(async move { tx.send("Result".to_string()).unwrap(); });
let result = rx.await.unwrap();
```

### watch

```rust
let (tx, mut rx) = tokio::sync::watch::channel("initial".to_string());
tokio::spawn(async move {
    loop {
        rx.changed().await.unwrap();
        println!("New value: {}", *rx.borrow());
    }
});
tx.send("updated".to_string()).unwrap();
```

## Graceful Shutdown

### CancellationToken (Primary)

```rust
use tokio_util::sync::CancellationToken;

async fn run_server() -> anyhow::Result<()> {
    let token = CancellationToken::new();
    let token_clone = token.clone();

    tokio::spawn(async move {
        loop {
            tokio::select! {
                _ = token_clone.cancelled() => {
                    tracing::info!("Task shutting down");
                    break;
                }
                _ = do_work() => {}
            }
        }
    });

    tokio::signal::ctrl_c().await?;
    tracing::info!("Shutdown signal received");
    token.cancel();
    tokio::time::sleep(std::time::Duration::from_secs(5)).await;
    Ok(())
}
```

### Alternative: Broadcast Channel

```rust
let (shutdown_tx, _) = tokio::sync::broadcast::channel::<()>(1);
let mut rx = shutdown_tx.subscribe();
tokio::spawn(async move {
    tokio::select! {
        _ = rx.recv() => tracing::info!("Received shutdown"),
        _ = async { loop { do_work().await } } => {}
    }
});
tokio::signal::ctrl_c().await?;
let _ = shutdown_tx.send(());
```

### Alternative: Watch Channel

```rust
let (shutdown_tx, shutdown_rx) = tokio::sync::watch::channel(false);
tokio::spawn(background_task(shutdown_rx));
tokio::signal::ctrl_c().await?;
shutdown_tx.send(true).unwrap();
```

## Async Traits

Native `async fn` in traits is stable since Rust 1.75 but has limitations with `dyn` dispatch. Use `async-trait` crate when trait objects are needed:

```rust
use async_trait::async_trait;

#[async_trait]
pub trait Repository {
    async fn get(&self, id: &str) -> anyhow::Result<Entity>;
    async fn save(&self, entity: &Entity) -> anyhow::Result<()>;
}

#[async_trait]
impl Repository for PostgresRepository {
    async fn get(&self, id: &str) -> anyhow::Result<Entity> {
        sqlx::query_as!(Entity, "SELECT * FROM entities WHERE id = $1", id)
            .fetch_one(&self.pool)
            .await
            .map_err(Into::into)
    }
    // ...
}

// Trait object usage
async fn process(repo: &dyn Repository, id: &str) -> anyhow::Result<()> {
    let entity = repo.get(id).await?;
    repo.save(&entity).await
}
```

## Streams and Async Iteration

### Creating Streams with async_stream

```rust
use async_stream::stream;
use futures::stream::Stream;

fn numbers_stream() -> impl Stream<Item = i32> {
    stream! {
        for i in 0..10 {
            tokio::time::sleep(std::time::Duration::from_millis(100)).await;
            yield i;
        }
    }
}
```

### Processing Streams

```rust
use futures::stream::StreamExt;

// Filter, map, collect
let processed: Vec<_> = numbers_stream()
    .filter(|n| futures::future::ready(*n % 2 == 0))
    .map(|n| n * 2)
    .collect()
    .await;

// Chunked processing
let mut chunks = numbers_stream().chunks(3);
while let Some(chunk) = chunks.next().await {
    println!("Processing chunk: {:?}", chunk);
}

// Merge multiple streams
use futures::stream;
let merged = stream::select(numbers_stream(), numbers_stream());
merged.for_each(|n| async move { println!("Got: {}", n); }).await;
```

## Resource Management

### Shared State with RwLock (Read-Heavy)

```rust
use std::sync::Arc;
use tokio::sync::RwLock;

struct Cache {
    data: RwLock<std::collections::HashMap<String, String>>,
}

impl Cache {
    async fn get(&self, key: &str) -> Option<String> {
        self.data.read().await.get(key).cloned()
    }
    async fn set(&self, key: String, value: String) {
        self.data.write().await.insert(key, value);
    }
}
```

### Connection Pool with Semaphore

```rust
use tokio::sync::{Mutex, Semaphore, SemaphorePermit};

struct Pool {
    semaphore: Semaphore,
    connections: Mutex<Vec<Connection>>,
}

impl Pool {
    fn new(size: usize) -> Self {
        Self {
            semaphore: Semaphore::new(size),
            connections: Mutex::new((0..size).map(|_| Connection::new()).collect()),
        }
    }

    async fn acquire(&self) -> PooledConnection<'_> {
        let permit = self.semaphore.acquire().await.unwrap();
        let conn = self.connections.lock().await.pop().unwrap();
        PooledConnection { pool: self, conn: Some(conn), _permit: permit }
    }
}

struct PooledConnection<'a> {
    pool: &'a Pool,
    conn: Option<Connection>,
    _permit: SemaphorePermit<'a>,
}

impl Drop for PooledConnection<'_> {
    fn drop(&mut self) {
        if let Some(conn) = self.conn.take() {
            let pool = self.pool;
            tokio::spawn(async move {
                pool.connections.lock().await.push(conn);
            });
        }
    }
}
```

## Manual Future Implementation

```rust
use std::pin::Pin;
use std::future::Future;
use std::task::{Context, Poll};

struct DelayedValue {
    value: i32,
    delay: tokio::time::Sleep,
}

impl Future for DelayedValue {
    type Output = i32;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        match Pin::new(&mut self.delay).poll(cx) {
            Poll::Ready(_) => Poll::Ready(self.value),
            Poll::Pending => Poll::Pending,
        }
    }
}
```

## Runtime Configuration

```rust
// Custom multi-thread runtime
let runtime = tokio::runtime::Builder::new_multi_thread()
    .worker_threads(4)
    .thread_name("my-worker")
    .thread_stack_size(3 * 1024 * 1024)
    .enable_all()
    .build()
    .unwrap();

// Single-threaded runtime
let runtime = tokio::runtime::Builder::new_current_thread()
    .enable_all()
    .build()
    .unwrap();
```

## Debugging

### tokio-console

```bash
# Cargo.toml: tokio = { features = ["tracing"] }
RUSTFLAGS="--cfg tokio_unstable" cargo run
# Then: tokio-console
```

### Tracing Instrumentation

```rust
use tracing::instrument;

#[instrument(skip(pool))]
async fn fetch_user(pool: &PgPool, id: &str) -> anyhow::Result<User> {
    tracing::debug!("Fetching user");
    // ...
}

// Track task spawning
let span = tracing::info_span!("worker", id = %worker_id);
tokio::spawn(async move {
    // Enters span when polled
}.instrument(span));
```

## Best Practices

### Do
- Use `tokio::select!` for racing futures
- Prefer channels over shared state when possible
- Use `JoinSet` for managing multiple tasks
- Instrument with `tracing` for debugging async code
- Handle cancellation via `CancellationToken`
- Use `spawn_blocking` for blocking operations
- Use timeout for all external I/O operations
- Prefer `try_join!` over manual error handling

### Don't
- Never use `std::thread::sleep` in async context
- Never hold locks across `.await` points
- Never spawn unboundedly — use semaphores for limits
- Never ignore errors — propagate with `?` or log
- Never forget `Send` bounds on spawned futures
