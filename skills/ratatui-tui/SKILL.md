---
name: ratatui-tui
description: |
  Build terminal UIs with ratatui following 2026 Rust best practices.
  Use when: (1) Creating new TUI apps, (2) Adding widgets/layouts,
  (3) Keyboard navigation/state management, (4) Image integration via
  ratatui-image, (5) Async event handling, (6) Release optimization.
  Covers v0.30.0+ API, Elm Architecture, StatefulWidget, color-eyre.
---

# Ratatui TUI Development

## Quick Start

1. **Copy template** to project:

   ```bash
   cp -r ~/.claude/skills/ratatui-tui/assets/templates/<template>/* .
   ```

2. **Run**:
   ```bash
   cargo run
   ```

## Template Selection

| Complexity | Template        | Use Case                    |
| ---------- | --------------- | --------------------------- |
| Minimal    | `hello-world`   | Learning, quick demos       |
| Simple     | `simple-app`    | Single-screen apps, tools   |
| Async      | `async-app`     | Background tasks, network   |
| Full       | `component-app` | Multi-view, config, logging |

**Decision tree:**

- Need async/network? → `async-app`
- Multiple screens/components? → `component-app`
- Just a simple tool? → `simple-app`
- Learning ratatui? → `hello-world`

## Project Setup

### Minimal Cargo.toml

```toml
[package]
name = "my-tui"
version = "0.1.0"
edition = "2024"

[dependencies]
ratatui = "0.30"
crossterm = "0.29"
color-eyre = "0.6"
```

### Full Dependencies (component-app)

```toml
[dependencies]
ratatui = "0.30"
crossterm = { version = "0.29", features = ["event-stream"] }
color-eyre = "0.6"
tokio = { version = "1", features = ["full"] }
futures = "0.3"
clap = { version = "4", features = ["derive"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
serde = { version = "1", features = ["derive"] }
config = "0.15"
dirs = "6"

# Optional: image support
ratatui-image = { version = "5", features = ["chafa-static"] }
```

### Release Profile

```toml
[profile.release]
lto = true
codegen-units = 1
panic = "abort"
strip = true
```

## Core Loop: TEA (The Elm Architecture)

```
Model → Message → Update → View
  ↑                         |
  └─────────────────────────┘
```

```rust
struct App {
    counter: i32,
    should_quit: bool,
}

enum Message {
    Increment,
    Decrement,
    Quit,
}

impl App {
    fn update(&mut self, msg: Message) {
        match msg {
            Message::Increment => self.counter += 1,
            Message::Decrement => self.counter -= 1,
            Message::Quit => self.should_quit = true,
        }
    }

    fn view(&self, frame: &mut Frame) {
        let text = format!("Counter: {}", self.counter);
        frame.render_widget(Paragraph::new(text), frame.area());
    }
}
```

## Styling Rules

**Use Stylize trait helpers:**

```rust
use ratatui::style::Stylize;

// Good
"text".bold()
"text".dim()
"text".cyan()
"text".on_dark_gray()
"text".bold().cyan()

// Avoid
Style::default().fg(Color::White)  // hardcoded white
Style::default().fg(Color::Black)  // hardcoded black
Style::new().add_modifier(Modifier::BOLD)  // verbose
```

**Color palette:**

- Primary: `.cyan()`, `.green()`
- Error: `.red()`
- Warning: `.yellow()` (sparingly)
- Muted: `.dim()`, `.dark_gray()`
- Accent: `.magenta()`

**Text wrapping:**

```rust
use textwrap::wrap;
use ratatui::text::Line;

let wrapped: Vec<Line> = wrap(&long_text, width as usize)
    .into_iter()
    .map(|cow| Line::from(cow.into_owned()))
    .collect();
```

See: [references/style-guide.md](references/style-guide.md)

## Widget Patterns

### StatefulWidget

```rust
struct MyList {
    items: Vec<String>,
}

struct MyListState {
    selected: usize,
}

impl StatefulWidget for MyList {
    type State = MyListState;

    fn render(self, area: Rect, buf: &mut Buffer, state: &mut Self::State) {
        // render with state.selected
    }
}

// Usage
frame.render_stateful_widget(my_list, area, &mut state);
```

### Layout

```rust
let [header, main, footer] = Layout::vertical([
    Constraint::Length(1),
    Constraint::Fill(1),
    Constraint::Length(1),
]).areas(frame.area());

let [left, right] = Layout::horizontal([
    Constraint::Percentage(30),
    Constraint::Fill(1),
]).areas(main);
```

### Built-in State Types

- `ListState` - for List widget
- `TableState` - for Table widget
- `ScrollbarState` - for Scrollbar

See: [references/architecture-patterns.md](references/architecture-patterns.md)

## Async Event Handling

```rust
use crossterm::event::{EventStream, Event, KeyCode};
use futures::StreamExt;
use tokio::select;

async fn run(mut app: App) -> Result<()> {
    let mut events = EventStream::new();

    loop {
        // Render
        terminal.draw(|f| app.view(f))?;

        // Handle events
        select! {
            Some(Ok(event)) = events.next() => {
                if let Event::Key(key) = event {
                    match key.code {
                        KeyCode::Char('q') => break,
                        KeyCode::Up => app.update(Message::Up),
                        KeyCode::Down => app.update(Message::Down),
                        _ => {}
                    }
                }
            }
            // Add other channels here (background tasks, timers)
        }

        if app.should_quit {
            break;
        }
    }
    Ok(())
}
```

See: [references/async-patterns.md](references/async-patterns.md)

## Image Integration

```rust
use ratatui_image::{picker::Picker, StatefulImage, Resize};
use std::thread;

// Query terminal protocol support once at startup
let mut picker = Picker::from_query_stdio()?;

// Load and resize in background thread
let (tx, rx) = std::sync::mpsc::channel();
thread::spawn(move || {
    let dyn_img = image::open("photo.png").unwrap();
    let protocol = picker.new_protocol(dyn_img, area.into(), Resize::Fit(None));
    tx.send(protocol).unwrap();
});

// In render, use StatefulImage for efficient redraw
if let Ok(protocol) = rx.try_recv() {
    image_state = Some(protocol);
}
if let Some(ref mut img) = image_state {
    frame.render_stateful_widget(StatefulImage::default(), area, img);
}
```

**Key points:**

- Use `chafa-static` feature for portable binaries
- Query protocol once, not per-frame
- Offload resize/encode to background thread
- Use `StatefulImage` to avoid re-encoding on redraws

See: [references/image-integration.md](references/image-integration.md)

## Error Handling

```rust
use color_eyre::eyre::Result;

fn main() -> Result<()> {
    // Install hooks before anything else
    color_eyre::install()?;

    // Set panic hook to restore terminal
    let original_hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |panic_info| {
        let _ = crossterm::terminal::disable_raw_mode();
        let _ = crossterm::execute!(
            std::io::stdout(),
            crossterm::terminal::LeaveAlternateScreen
        );
        original_hook(panic_info);
    }));

    run()
}
```

**Error propagation:**

```rust
// Use ? for recoverable errors
let file = std::fs::read_to_string(path)?;

// Use color_eyre context
let config = load_config()
    .wrap_err("Failed to load configuration")?;
```

## Release Build

```bash
cargo build --release
```

Binary at `target/release/<name>`.

**Size optimization:**

```toml
[profile.release]
lto = true
codegen-units = 1
panic = "abort"
strip = true
opt-level = "z"  # size over speed
```

## Templates Overview

### hello-world (~25 lines)

Minimal ratatui demo using `ratatui::run()`.

### simple-app (~80 lines)

Synchronous event loop, App struct, basic render.

### async-app (~120 lines)

Tokio runtime, EventStream, `select!` pattern.

### component-app (~300 lines)

Full modular structure:

- `main.rs` - entry point
- `app.rs` - App state, update logic
- `event.rs` - event handling
- `ui.rs` - rendering
- `action.rs` - Action enum
- `tui.rs` - terminal setup
- `config.rs` - configuration with dirs
- `logging.rs` - tracing setup

## Common Patterns

### Centered Popup

```rust
fn centered_rect(percent_x: u16, percent_y: u16, area: Rect) -> Rect {
    let [_, center, _] = Layout::vertical([
        Constraint::Percentage((100 - percent_y) / 2),
        Constraint::Percentage(percent_y),
        Constraint::Percentage((100 - percent_y) / 2),
    ]).areas(area);

    let [_, center, _] = Layout::horizontal([
        Constraint::Percentage((100 - percent_x) / 2),
        Constraint::Percentage(percent_x),
        Constraint::Percentage((100 - percent_x) / 2),
    ]).areas(center);

    center
}
```

### Key Bindings Display

```rust
let help = Line::from(vec![
    " q ".bold().cyan(),
    "quit ".dim(),
    " ↑↓ ".bold().cyan(),
    "navigate ".dim(),
    " Enter ".bold().cyan(),
    "select ".dim(),
]);
```

### Status Bar

```rust
let status = Line::from(vec![
    " MODE ".bold().on_cyan(),
    format!(" {} items ", count).dim().into(),
]);
```

## Checklist

Before shipping:

- [ ] `cargo fmt`
- [ ] `cargo clippy --all-features` clean
- [ ] No `unwrap()` outside tests
- [ ] Panic hook restores terminal
- [ ] `cargo build --release` succeeds
- [ ] Test on target terminal(s)
