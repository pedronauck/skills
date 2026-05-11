# Traits, Generics, and Type System

## Trait Basics

```rust
// Trait with default implementation
trait Describable {
    fn describe(&self) -> String {
        String::from("No description available")
    }
}

// Implementing traits
struct Circle { radius: f64 }

impl Describable for Circle {
    fn describe(&self) -> String {
        format!("A circle with radius {}", self.radius)
    }
}
```

## Associated Types vs Generic Parameters

Use associated types when there is one clear type per implementation:
```rust
trait Container {
    type Item;
    fn add(&mut self, item: Self::Item);
    fn get(&self, index: usize) -> Option<&Self::Item>;
}
```

Use generic parameters when multiple types might be used simultaneously.

## Generic Bounds and Where Clauses

```rust
fn print_info<T>(item: &T)
where
    T: std::fmt::Display + std::fmt::Debug,
{
    println!("Display: {}, Debug: {:?}", item, item);
}

// Blanket implementation
impl<T: std::fmt::Display> MyTrait for T {
    fn do_something(&self) { println!("Value: {}", self); }
}
```

## Static vs Dynamic Dispatch

> Static where you can, dynamic where you must.

### Static Dispatch: `impl Trait` or `<T: Trait>`

Zero runtime cost. The compiler monomorphizes per use:
```rust
fn specialized_sum<T: MyTrait>(iter: impl Iterator<Item = T>) -> T {
    iter.map(|x| x.random_mapping()).sum()
}
```

Best when: zero runtime cost needed, types known at compile time, tight loops.

### Dynamic Dispatch: `dyn Trait`

Runtime vtable. Use for heterogeneous collections and plugin architectures:
```rust
fn all_animals_greeting(animals: Vec<Box<dyn Animal>>) {
    for animal in animals {
        println!("{}", animal.greet());
    }
}
```

Best when: runtime polymorphism needed, different types in one collection, abstracting internals.

### Trade-off Summary

| | Static (`impl Trait`) | Dynamic (`dyn Trait`) |
|---|---|---|
| Performance | Faster, inlined | Slower: vtable indirection |
| Compile time | Slower: monomorphization | Faster: shared code |
| Binary size | Larger: per-type codegen | Smaller |
| Flexibility | One type at a time | Can mix types |
| Errors | Clearer | Erased types confuse errors |

### Trait Object Ergonomics

- Prefer `&dyn Trait` over `Box<dyn Trait>` when ownership is not needed
- Use `Arc<dyn Trait>` for shared access across threads
- Don't box prematurely inside structs — box at public API boundaries
- Object safety: no generic methods, no `Self: Sized`, methods use `&self`/`&mut self`/`self`

```rust
// Good: generics when possible
struct Renderer<B: Backend> { backend: B }

// Avoid: premature boxing
struct Renderer { backend: Box<dyn Backend> }
```

## Extension Traits

Add functionality to existing types:
```rust
trait StringExt {
    fn truncate_to(&self, max_len: usize) -> String;
}

impl StringExt for str {
    fn truncate_to(&self, max_len: usize) -> String {
        if self.len() <= max_len { self.to_string() }
        else { format!("{}...", &self[..max_len]) }
    }
}
```

## Sealed Traits

Prevent external implementors:
```rust
mod sealed {
    pub trait Sealed {}
}

pub trait MySealed: sealed::Sealed {
    fn method(&self);
}

struct MyType;
impl sealed::Sealed for MyType {}
impl MySealed for MyType {
    fn method(&self) { println!("Implemented"); }
}
```

## Supertraits

```rust
trait Printable {
    fn print(&self);
}

trait Loggable: Printable {
    fn log(&self) {
        self.print(); // Can call supertrait methods
    }
}
```

## Associated Constants

```rust
trait Config {
    const MAX_SIZE: usize;
    const DEFAULT_TIMEOUT: u64;
}

struct ServerConfig;
impl Config for ServerConfig {
    const MAX_SIZE: usize = 1024;
    const DEFAULT_TIMEOUT: u64 = 30;
}
```

## Generic Associated Types (GATs)

Allow generics in associated types:
```rust
trait LendingIterator {
    type Item<'a> where Self: 'a;
    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

struct WindowsMut<'data, T> {
    data: &'data mut [T],
    index: usize,
}

impl<'data, T> LendingIterator for WindowsMut<'data, T> {
    type Item<'a> = &'a mut [T] where Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
        if self.index >= self.data.len() { return None; }
        let start = self.index;
        self.index += 2;
        Some(&mut self.data[start..start.min(self.data.len())])
    }
}
```

## Marker Traits and PhantomData

```rust
use std::marker::PhantomData;

trait Trusted {}

struct TrustedData<T> {
    data: T,
    _marker: PhantomData<T>,
}

impl<T: Trusted> TrustedData<T> {
    fn new(data: T) -> Self {
        Self { data, _marker: PhantomData }
    }
}
```

## Operator Overloading

```rust
use std::ops::{Add, Mul};

#[derive(Debug, Clone, Copy)]
struct Vector2D { x: f64, y: f64 }

impl Add for Vector2D {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        Self { x: self.x + other.x, y: self.y + other.y }
    }
}

impl Mul<f64> for Vector2D {
    type Output = Self;
    fn mul(self, scalar: f64) -> Self {
        Self { x: self.x * scalar, y: self.y * scalar }
    }
}
```

## From/Into and TryFrom/TryInto

```rust
struct UserId(u64);

impl From<u64> for UserId {
    fn from(id: u64) -> Self { UserId(id) }
}

// Into is automatically implemented
fn accept_user_id(id: impl Into<UserId>) {
    let user_id = id.into();
}

// TryFrom for fallible conversions
impl TryFrom<i64> for UserId {
    type Error = &'static str;
    fn try_from(value: i64) -> Result<Self, Self::Error> {
        if value < 0 { Err("User ID cannot be negative") }
        else { Ok(UserId(value as u64)) }
    }
}
```

## Derive Macros

```rust
// Standard derives
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct User { id: u64, name: String }

// With serde
#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct Config { host: String, port: u16 }
```

## Type State Pattern

Encode states as types using generics + `PhantomData`. Invalid states become compile errors:

```rust
use std::marker::PhantomData;

struct FileNotOpened;
struct FileOpened;

struct File<State> {
    path: std::path::PathBuf,
    handle: Option<std::fs::File>,
    _state: PhantomData<State>,
}

impl File<FileNotOpened> {
    fn open(path: &std::path::Path) -> std::io::Result<File<FileOpened>> {
        let file = std::fs::File::open(path)?;
        Ok(File {
            path: path.to_path_buf(),
            handle: Some(file),
            _state: PhantomData::<FileOpened>,
        })
    }
}

impl File<FileOpened> {
    fn read(&mut self) -> std::io::Result<String> {
        use std::io::Read;
        let mut content = String::new();
        self.handle.as_mut().unwrap().read_to_string(&mut content)?;
        Ok(content)
    }
}
```

### Multi-State Builder

```rust
struct MissingName;
struct NameSet;
struct MissingAge;
struct AgeSet;

struct Builder<NameState, AgeState> {
    name: Option<String>,
    age: u8,
    _name: PhantomData<NameState>,
    _age: PhantomData<AgeState>,
}

impl Builder<NameSet, AgeSet> {
    fn build(self) -> Person {
        Person { name: self.name.unwrap(), age: self.age }
    }
}
```

### When to Use Type State:
- Compile-time state safety
- Enforcing API constraints
- Library/crate design dependent on state variants
- Replacing runtime booleans with type-safe code paths

### When to Avoid:
- Trivial states (simple enums suffice)
- Runtime flexibility is required
- Leads to overcomplicated generics

PhantomData is zero-sized and removed after compilation — no runtime overhead.

## Const Traits (Nightly)

```rust
#![feature(const_trait_impl)]

#[const_trait]
trait ConstAdd {
    fn add(self, other: Self) -> Self;
}

impl const ConstAdd for i32 {
    fn add(self, other: Self) -> Self { self + other }
}

const fn compute() -> i32 { 5.add(10) }
```

## Best Practices

- Prefer associated types when one type per implementation
- Use generic parameters when multiple types used simultaneously
- Keep traits small and focused (single responsibility)
- Prefer static dispatch; use `dyn Trait` when flexibility outweighs speed
- Use `#[derive]` when possible instead of manual implementations
- Implement standard traits (`Debug`, `Clone`, etc.) for ecosystem integration
- Use sealed traits to prevent external implementations when needed
- Document trait requirements and invariants
