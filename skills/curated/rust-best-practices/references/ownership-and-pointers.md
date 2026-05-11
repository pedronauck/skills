# Ownership, Borrowing, and Pointers

## Move Semantics and Borrowing

```rust
// Move semantics (ownership transfer)
fn take_ownership(s: String) {
    println!("{}", s);
} // s dropped here

// Immutable borrowing
fn borrow(s: &str) {
    println!("{}", s);
} // caller still owns

// Mutable borrowing
fn borrow_mut(s: &mut String) {
    s.push_str(" world");
}
```

## Lifetime Annotations

Use meaningful lifetime names: `'src`, `'ctx`, `'conn` — not just `'a`.

```rust
fn longest<'src>(x: &'src str, y: &'src str) -> &'src str {
    if x.len() > y.len() { x } else { y }
}

// Lifetime in structs
struct Excerpt<'src> {
    part: &'src str,
}

// Static lifetime (lives for entire program)
const GREETING: &'static str = "Hello, world!";
```

## Pointer Type Reference

| Pointer | Send+Sync? | Primary Use |
|---------|-----------|-------------|
| `&T` | Yes | Shared immutable access |
| `&mut T` | Not Send | Exclusive mutable access |
| `Box<T>` | Yes (if T: Send+Sync) | Heap allocation, single owner, recursive types |
| `Rc<T>` | Neither | Shared ownership, single-threaded |
| `Arc<T>` | Yes | Shared ownership, multi-threaded |
| `Cell<T>` | Not Sync | Interior mutability, Copy types only |
| `RefCell<T>` | Not Sync | Interior mutability, runtime borrow checking |
| `Mutex<T>` | Yes | Thread-safe exclusive access |
| `RwLock<T>` | Yes | Thread-safe shared read OR exclusive write |
| `OnceCell<T>` | Not Sync | Single-thread one-time initialization |
| `LazyCell<T>` | Not Sync | Lazy version of OnceCell with closure init |
| `OnceLock<T>` | Yes | Thread-safe one-time initialization |
| `LazyLock<T>` | Yes | Thread-safe lazy initialization with closure |
| `*const T / *mut T` | No | Raw pointers, FFI (inherently unsafe) |

## Smart Pointers

### Box<T> — Heap Allocated, Single Owner

Great for recursive types and large structs:
```rust
enum Tree<T> {
    Leaf(T),
    Branch(Box<Tree<T>>, Box<Tree<T>>),
}
```

### Rc<T> and Arc<T> — Reference Counting

```rust
use std::rc::Rc;
use std::sync::Arc;

// Rc: single-threaded shared ownership
let rc1 = Rc::new(vec![1, 2, 3]);
let rc2 = Rc::clone(&rc1);
println!("Count: {}", Rc::strong_count(&rc1)); // 2

// Arc: thread-safe shared ownership
let arc1 = Arc::new(vec![1, 2, 3]);
let arc2 = Arc::clone(&arc1);
std::thread::spawn(move || println!("{:?}", arc2));
```

### Arc<Mutex<T>> Pattern

For shared mutable state across threads:
```rust
let counter = Arc::new(Mutex::new(0));
let counter_clone = Arc::clone(&counter);
std::thread::spawn(move || {
    let mut num = counter_clone.lock().unwrap();
    *num += 1;
});
```

## Interior Mutability

### Cell<T> — Copy Types Only

Fast, no runtime overhead for borrow checking:
```rust
use std::cell::Cell;

struct SomeStruct {
    regular_field: u8,
    special_field: Cell<u8>,
}

let s = SomeStruct { regular_field: 0, special_field: Cell::new(1) };
s.special_field.set(100); // OK even though s is immutable
```

### RefCell<T> — Runtime Borrow Checking

Use `try_borrow()` to avoid panics:
```rust
use std::cell::RefCell;

let data = RefCell::new(vec![1, 2, 3]);
data.borrow_mut().push(4);

// Prefer try_borrow to avoid panics
if let Ok(mut val) = data.try_borrow_mut() {
    val.push(5);
}
```

### Mock Objects with Interior Mutability

```rust
struct MockLogger {
    messages: RefCell<Vec<String>>,
}

impl MockLogger {
    fn new() -> Self {
        Self { messages: RefCell::new(Vec::new()) }
    }
    fn log(&self, msg: &str) {
        self.messages.borrow_mut().push(msg.to_string());
    }
    fn get_messages(&self) -> Vec<String> {
        self.messages.borrow().clone()
    }
}
```

## Pin and Self-Referential Types

Self-referential structs require `Pin` to prevent moves:
```rust
use std::pin::Pin;
use std::marker::PhantomPinned;

struct SelfReferential {
    data: String,
    pointer: *const String,
    _pin: PhantomPinned,
}

impl SelfReferential {
    fn new(data: String) -> Pin<Box<Self>> {
        let mut boxed = Box::pin(Self {
            data,
            pointer: std::ptr::null(),
            _pin: PhantomPinned,
        });
        let ptr = &boxed.data as *const String;
        // SAFETY: not moving the data after this point
        unsafe {
            let mut_ref = Pin::as_mut(&mut boxed);
            Pin::get_unchecked_mut(mut_ref).pointer = ptr;
        }
        boxed
    }
}
```

Futures are often self-referential, which is why `Pin` appears in async contexts.

## Cow (Clone on Write)

Avoid allocation when data might not need modification:
```rust
use std::borrow::Cow;

fn process_text(input: &str) -> Cow<str> {
    if input.contains("bad") {
        Cow::Owned(input.replace("bad", "good")) // Allocates
    } else {
        Cow::Borrowed(input) // No allocation
    }
}

fn hello_greet(name: Cow<'_, str>) {
    println!("Hello {name}");
}

hello_greet(Cow::Borrowed("Julia"));
hello_greet(Cow::Owned("Naomi".to_string()));
```

## Drop Trait and RAII

Implement `Drop` for automatic cleanup:
```rust
struct FileGuard { name: String }

impl FileGuard {
    fn new(name: String) -> Self {
        println!("Opening {}", name);
        Self { name }
    }
}

impl Drop for FileGuard {
    fn drop(&mut self) {
        println!("Closing {}", self.name);
    }
}

// Usage: automatic cleanup when scope ends
{
    let _file = FileGuard::new("data.txt".to_string());
} // Drop called automatically
```

## Builder Pattern with Ownership

Consuming builder that transfers ownership at each step:
```rust
struct ConfigBuilder {
    host: Option<String>,
    port: Option<u16>,
}

impl ConfigBuilder {
    fn host(mut self, host: impl Into<String>) -> Self {
        self.host = Some(host.into());
        self
    }
    fn port(mut self, port: u16) -> Self {
        self.port = Some(port);
        self
    }
    fn build(self) -> Result<Config, &'static str> {
        Ok(Config {
            host: self.host.ok_or("host required")?,
            port: self.port.unwrap_or(8080),
        })
    }
}
```

## OnceLock and LazyLock

For static initialization, replacing `lazy_static!` and `once_cell`:

```rust
use std::sync::OnceLock;

static CELL: OnceLock<u32> = OnceLock::new();

std::thread::spawn(|| {
    let value = CELL.get_or_init(|| 12345);
    assert_eq!(value, &12345);
}).join().unwrap();
```

```rust
use std::sync::LazyLock;

static CONFIG: LazyLock<HashMap<&str, T>> = LazyLock::new(|| {
    let data = read_config();
    let mut config: HashMap<&str, T> = data.into();
    config.insert("special_case", T::default());
    config
});
```

## Shadowing for Transformations

Use shadowing to transform values without new variable names:
```rust
let x = "42";
let x = x.parse::<i32>()?;
let x = x * 2;
```

## Best Practices

- Prefer borrowing (`&T`) over ownership transfer when possible
- Use `&str` over `String`, `&[T]` over `Vec<T>` for function parameters
- Clone only when necessary (profile first)
- Use `Cow<'a, T>` for conditional cloning
- Document lifetime relationships in complex cases
- Use `Arc<Mutex<T>>` for shared mutable state across threads
- Use `Rc<RefCell<T>>` for shared mutable state in single thread
- Implement `Drop` for RAII patterns
- Use `try_borrow()` on `RefCell` to avoid panics
- Use meaningful lifetime names (`'src`, `'ctx`, not just `'a`)
