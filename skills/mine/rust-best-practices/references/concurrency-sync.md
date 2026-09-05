# Synchronous Concurrency

## Send and Sync Traits

Rust tracks thread safety via `Send` and `Sync`:
- **`Send`**: data can move across threads
- **`Sync`**: data can be referenced from multiple threads (`&T` is `Send`)

A pointer is thread-safe only if the data behind it is.

## Atomics Over Mutex for Primitives

Atomics can fit independent primitive state. Use a mutex when a multi-field invariant needs one consistency boundary; replacing each field with an atomic does not preserve that invariant:

```rust
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};

static RUNNING: AtomicBool = AtomicBool::new(true);
static COUNTER: AtomicUsize = AtomicUsize::new(0);

// Read
let is_running = RUNNING.load(Ordering::Relaxed);
let count = COUNTER.load(Ordering::SeqCst);

// Write
RUNNING.store(false, Ordering::Relaxed);
COUNTER.fetch_add(1, Ordering::SeqCst);
```

## Memory Ordering

Choose ordering carefully based on the consistency guarantee needed:

| Ordering | Guarantee | Use When |
|----------|-----------|----------|
| `Relaxed` | No ordering guarantee | Counters, flags where ordering doesn't matter |
| `Acquire` | Reads after this see writes before the paired `Release` | Reading shared data after a flag check |
| `Release` | Writes before this are visible after the paired `Acquire` | Writing shared data before setting a flag |
| `AcqRel` | Both `Acquire` and `Release` | Read-modify-write operations |
| `SeqCst` | Total ordering across all threads | A single order for sequentially consistent operations |

When unsure, use `SeqCst`. Optimize to weaker orderings only with clear reasoning.

## Mutex and RwLock

### std::sync::Mutex

Exclusive access — one thread at a time:
```rust
use std::sync::{Arc, Mutex};

let data = Arc::new(Mutex::new(0));
let data_clone = Arc::clone(&data);

std::thread::spawn(move || {
    let mut lock = data_clone.lock().unwrap();
    *lock += 1;
});
```

### parking_lot::Mutex (Situational alternative)

`std::sync::Mutex` is the idiomatic default. `parking_lot::Mutex` is a drop-in opt-in when its trade-offs fit:
- No poisoning (simpler API, no `.unwrap()` on lock)
- Smaller memory footprint
- Better performance under contention

```rust
use parking_lot::Mutex;
use std::sync::Arc;

let data = Arc::new(Mutex::new(0));
let data_clone = Arc::clone(&data);

std::thread::spawn(move || {
    let mut lock = data.lock(); // No .unwrap() needed
    *lock += 1;
});
```

### std::sync::RwLock

Multiple readers OR single writer:
```rust
use std::sync::{Arc, RwLock};

let data = Arc::new(RwLock::new(vec![1, 2, 3]));

// Multiple concurrent readers
let read_handle = data.read().unwrap();
println!("{:?}", *read_handle);

drop(read_handle); // Release the read guard before requesting exclusive access.

// Exclusive writer
let mut write_handle = data.write().unwrap();
write_handle.push(4);
```

Prefer `RwLock` over `Mutex` for read-heavy workloads (`parking_lot::RwLock` under the same opt-in reasoning).

## Lock Ordering to Prevent Deadlocks

When acquiring multiple locks, always acquire them in a consistent order:

```rust
// Define a global ordering: lock_a before lock_b
let lock_a = Arc::new(Mutex::new(0));
let lock_b = Arc::new(Mutex::new(0));

// Always acquire in order: a then b
let _a = lock_a.lock().unwrap();
let _b = lock_b.lock().unwrap();

// NEVER: b then a (deadlock risk)
```

Rules:
- Document the lock ordering for the codebase
- Consider using a single lock for related data instead of multiple locks
- Use `try_lock()` to detect and recover from potential deadlocks

## Synchronous Channels

### crossbeam::channel (When you need select! or MPMC)

`std::sync::mpsc` (rewritten atop crossbeam internals in 1.67) covers the common case; crossbeam adds `select!` and multi-consumer:

```rust
use crossbeam::channel;

// Bounded channel
let (tx, rx) = channel::bounded(100);

// Unbounded channel
let (tx, rx) = channel::unbounded();

// Select across multiple channels
use crossbeam::select;
select! {
    recv(rx1) -> msg => println!("From rx1: {:?}", msg),
    recv(rx2) -> msg => println!("From rx2: {:?}", msg),
    default => println!("No message available"),
}
```

Use the existing channel implementation unless required selection, multi-consumer, or async semantics justify another dependency.

## Shared State Patterns

### Arc<Mutex<T>> for Shared Mutable State

```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    handles.push(std::thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    }));
}

for handle in handles {
    handle.join().unwrap();
}

println!("Result: {}", *counter.lock().unwrap());
```

### RwLock Cache Pattern

```rust
use std::sync::{Arc, RwLock};
use std::collections::HashMap;

struct Cache {
    data: RwLock<HashMap<String, String>>,
}

impl Cache {
    fn get(&self, key: &str) -> Option<String> {
        self.data.read().unwrap().get(key).cloned()
    }

    fn set(&self, key: String, value: String) {
        self.data.write().unwrap().insert(key, value);
    }
}
```

## Best Practices

- Choose synchronization around the invariant; independent primitive state may fit atomics
- Choose memory ordering carefully — `SeqCst` when unsure, weaker when justified
- Identify and document lock ordering to prevent deadlocks
- Keep standard synchronization by default; adopt `parking_lot` or `crossbeam` for required semantics or measured benefits
- Use `RwLock` instead of `Mutex` for read-heavy workloads
- Prefer channels over shared state when possible
- Use `Arc<Mutex<T>>` sparingly — consider architectural alternatives
