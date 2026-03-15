# Ratatui Async Patterns

## Why Async?

Sync event loops block on input, making background tasks impossible:

- Network requests
- File I/O
- Timers/animations
- External process output

## EventStream Setup

Enable the `event-stream` feature in crossterm:

```toml
[dependencies]
crossterm = { version = "0.29", features = ["event-stream"] }
tokio = { version = "1", features = ["full"] }
futures = "0.3"
```

## Basic Async Pattern

```rust
use crossterm::event::{Event, EventStream, KeyCode};
use futures::StreamExt;
use tokio::select;

#[tokio::main]
async fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;

    let mut terminal = ratatui::init();
    let result = run(&mut terminal).await;
    ratatui::restore();

    result
}

async fn run(terminal: &mut Terminal<impl Backend>) -> Result<()> {
    let mut app = App::default();
    let mut events = EventStream::new();

    loop {
        // Render current state
        terminal.draw(|frame| app.view(frame))?;

        // Wait for events
        select! {
            Some(Ok(event)) = events.next() => {
                if let Event::Key(key) = event {
                    match key.code {
                        KeyCode::Char('q') => break,
                        KeyCode::Up => app.select_prev(),
                        KeyCode::Down => app.select_next(),
                        _ => {}
                    }
                }
            }
        }

        if app.should_quit {
            break;
        }
    }

    Ok(())
}
```

## Multiple Event Sources

```rust
use tokio::sync::mpsc;
use tokio::time::{interval, Duration};

async fn run(terminal: &mut Terminal<impl Backend>) -> Result<()> {
    let mut app = App::default();
    let mut events = EventStream::new();

    // Tick timer for animations/updates
    let mut tick = interval(Duration::from_millis(250));

    // Channel for background task results
    let (tx, mut rx) = mpsc::unbounded_channel::<BackgroundResult>();

    loop {
        terminal.draw(|frame| app.view(frame))?;

        select! {
            // Terminal events (keyboard, mouse, resize)
            Some(Ok(event)) = events.next() => {
                app.handle_event(event);
            }

            // Periodic tick
            _ = tick.tick() => {
                app.tick();
            }

            // Background task results
            Some(result) = rx.recv() => {
                app.handle_background_result(result);
            }
        }

        if app.should_quit {
            break;
        }
    }

    Ok(())
}
```

## Background Tasks

### Fire-and-Forget

```rust
impl App {
    fn start_load(&mut self, tx: mpsc::UnboundedSender<BackgroundResult>) {
        self.loading = true;

        tokio::spawn(async move {
            let result = load_data().await;
            tx.send(BackgroundResult::DataLoaded(result)).ok();
        });
    }

    fn handle_background_result(&mut self, result: BackgroundResult) {
        match result {
            BackgroundResult::DataLoaded(data) => {
                self.loading = false;
                self.data = data;
            }
        }
    }
}
```

### With Progress Updates

```rust
enum BackgroundResult {
    Progress(usize, usize),  // current, total
    Complete(Data),
    Error(String),
}

async fn load_with_progress(
    tx: mpsc::UnboundedSender<BackgroundResult>,
) {
    let items = get_items().await;
    let total = items.len();

    for (i, item) in items.into_iter().enumerate() {
        process_item(item).await;
        tx.send(BackgroundResult::Progress(i + 1, total)).ok();
    }

    let data = finalize().await;
    tx.send(BackgroundResult::Complete(data)).ok();
}
```

### Cancellable Tasks

```rust
use tokio_util::sync::CancellationToken;

struct App {
    cancel_token: Option<CancellationToken>,
    // ...
}

impl App {
    fn start_task(&mut self, tx: mpsc::UnboundedSender<BackgroundResult>) {
        // Cancel any existing task
        if let Some(token) = self.cancel_token.take() {
            token.cancel();
        }

        let token = CancellationToken::new();
        self.cancel_token = Some(token.clone());

        tokio::spawn(async move {
            select! {
                result = do_work() => {
                    tx.send(BackgroundResult::Complete(result)).ok();
                }
                _ = token.cancelled() => {
                    tx.send(BackgroundResult::Cancelled).ok();
                }
            }
        });
    }

    fn cancel_task(&mut self) {
        if let Some(token) = self.cancel_token.take() {
            token.cancel();
        }
    }
}
```

## Debouncing Input

Useful for search-as-you-type:

```rust
use tokio::time::{sleep, Duration, Instant};

struct App {
    search_query: String,
    last_input: Instant,
    pending_search: bool,
}

impl App {
    fn handle_search_input(&mut self, c: char) {
        self.search_query.push(c);
        self.last_input = Instant::now();
        self.pending_search = true;
    }

    fn tick(&mut self, tx: &mpsc::UnboundedSender<BackgroundResult>) {
        // Debounce: only search after 300ms of no input
        if self.pending_search
            && self.last_input.elapsed() > Duration::from_millis(300)
        {
            self.pending_search = false;
            self.start_search(tx.clone());
        }
    }
}
```

## Rate Limiting Renders

Avoid rendering too frequently:

```rust
use std::time::{Duration, Instant};

const MIN_FRAME_DURATION: Duration = Duration::from_millis(16); // ~60fps

async fn run(terminal: &mut Terminal<impl Backend>) -> Result<()> {
    let mut last_render = Instant::now();
    let mut needs_render = true;

    loop {
        // Only render if needed and enough time has passed
        if needs_render && last_render.elapsed() >= MIN_FRAME_DURATION {
            terminal.draw(|frame| app.view(frame))?;
            last_render = Instant::now();
            needs_render = false;
        }

        select! {
            Some(Ok(event)) = events.next() => {
                if app.handle_event(event) {
                    needs_render = true;
                }
            }
            _ = tick.tick() => {
                if app.tick() {
                    needs_render = true;
                }
            }
            // ...
        }
    }
}
```

## Async File Operations

```rust
use tokio::fs;

async fn load_file(path: &Path, tx: mpsc::UnboundedSender<Action>) {
    match fs::read_to_string(path).await {
        Ok(content) => {
            tx.send(Action::FileLoaded(content)).ok();
        }
        Err(e) => {
            tx.send(Action::Error(format!("Failed to load: {}", e))).ok();
        }
    }
}

async fn save_file(path: &Path, content: String, tx: mpsc::UnboundedSender<Action>) {
    match fs::write(path, &content).await {
        Ok(()) => {
            tx.send(Action::FileSaved).ok();
        }
        Err(e) => {
            tx.send(Action::Error(format!("Failed to save: {}", e))).ok();
        }
    }
}
```

## Network Requests

```rust
use reqwest::Client;

struct App {
    client: Client,
    // ...
}

impl App {
    fn fetch_data(&self, tx: mpsc::UnboundedSender<Action>) {
        let client = self.client.clone();
        let url = self.api_url.clone();

        tokio::spawn(async move {
            match client.get(&url).send().await {
                Ok(response) => {
                    match response.json::<ApiResponse>().await {
                        Ok(data) => tx.send(Action::DataReceived(data)).ok(),
                        Err(e) => tx.send(Action::Error(e.to_string())).ok(),
                    };
                }
                Err(e) => {
                    tx.send(Action::Error(e.to_string())).ok();
                }
            }
        });
    }
}
```

## Event Handler Module

For larger apps, separate event handling:

```rust
// event.rs
use crossterm::event::{Event, KeyCode, KeyEvent, KeyModifiers};

pub enum AppEvent {
    Key(KeyEvent),
    Resize(u16, u16),
    Tick,
    Background(BackgroundResult),
}

pub struct EventHandler {
    events: EventStream,
    tick_rate: Duration,
    rx: mpsc::UnboundedReceiver<BackgroundResult>,
}

impl EventHandler {
    pub fn new(
        tick_rate: Duration,
        rx: mpsc::UnboundedReceiver<BackgroundResult>,
    ) -> Self {
        Self {
            events: EventStream::new(),
            tick_rate,
            rx,
        }
    }

    pub async fn next(&mut self) -> Result<AppEvent> {
        let tick_delay = tokio::time::sleep(self.tick_rate);

        select! {
            Some(Ok(event)) = self.events.next() => {
                match event {
                    Event::Key(key) => Ok(AppEvent::Key(key)),
                    Event::Resize(w, h) => Ok(AppEvent::Resize(w, h)),
                    _ => Ok(AppEvent::Tick),
                }
            }
            Some(result) = self.rx.recv() => {
                Ok(AppEvent::Background(result))
            }
            _ = tick_delay => {
                Ok(AppEvent::Tick)
            }
        }
    }
}
```

## Error Handling in Async

```rust
use color_eyre::eyre::{Result, WrapErr};

async fn run() -> Result<()> {
    // Wrap errors with context
    let data = load_config()
        .await
        .wrap_err("Failed to load configuration")?;

    // Handle recoverable errors gracefully
    match fetch_data().await {
        Ok(data) => app.data = data,
        Err(e) => {
            app.error = Some(format!("Network error: {}", e));
            // Continue running, show error to user
        }
    }

    Ok(())
}
```

## Best Practices

1. **Keep main loop simple** - delegate to handlers
2. **Use channels for communication** - avoid shared mutable state
3. **Handle all channel errors** - `.ok()` for send, match recv
4. **Cancel long tasks** - use CancellationToken
5. **Rate limit renders** - 60fps is enough
6. **Debounce user input** - for search/filter operations
7. **Show loading states** - feedback during async operations
8. **Log background errors** - don't silently fail
