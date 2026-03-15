# Ratatui Architecture Patterns

## The Elm Architecture (TEA)

The recommended pattern for ratatui apps:

```
     ┌──────────────────────────────────────┐
     │                                      │
     ▼                                      │
  Model ──────► View ──────► Terminal       │
     │                          │           │
     │                          │           │
     │                          ▼           │
     │                       Events         │
     │                          │           │
     │                          ▼           │
     └────────── Update ◄───── Message ─────┘
```

### Core Components

```rust
/// Application state (Model)
struct App {
    items: Vec<String>,
    selected: usize,
    mode: Mode,
    should_quit: bool,
}

/// All possible state changes (Message)
enum Message {
    SelectNext,
    SelectPrev,
    Enter,
    ChangeMode(Mode),
    Quit,
}

impl App {
    /// Pure state transition (Update)
    fn update(&mut self, msg: Message) {
        match msg {
            Message::SelectNext => {
                if self.selected < self.items.len().saturating_sub(1) {
                    self.selected += 1;
                }
            }
            Message::SelectPrev => {
                self.selected = self.selected.saturating_sub(1);
            }
            Message::Enter => {
                // Handle selection
            }
            Message::ChangeMode(mode) => {
                self.mode = mode;
            }
            Message::Quit => {
                self.should_quit = true;
            }
        }
    }

    /// Render current state (View)
    fn view(&self, frame: &mut Frame) {
        // Render widgets based on self
    }
}
```

### Main Loop

```rust
fn run(mut app: App, mut terminal: Terminal<impl Backend>) -> Result<()> {
    loop {
        // Render
        terminal.draw(|frame| app.view(frame))?;

        // Handle input
        if event::poll(Duration::from_millis(16))? {
            if let Event::Key(key) = event::read()? {
                let msg = match key.code {
                    KeyCode::Char('q') => Message::Quit,
                    KeyCode::Up | KeyCode::Char('k') => Message::SelectPrev,
                    KeyCode::Down | KeyCode::Char('j') => Message::SelectNext,
                    KeyCode::Enter => Message::Enter,
                    _ => continue,
                };
                app.update(msg);
            }
        }

        if app.should_quit {
            break;
        }
    }
    Ok(())
}
```

## Component Trait Pattern

For larger apps with multiple reusable views:

```rust
use ratatui::Frame;
use crossterm::event::KeyEvent;

/// Result of handling an event
pub enum EventResult {
    Consumed,       // Event was handled
    Ignored,        // Pass to parent
    Action(Action), // Trigger app-level action
}

/// Component trait for reusable UI elements
pub trait Component {
    /// Handle keyboard input
    fn handle_key(&mut self, key: KeyEvent) -> EventResult;

    /// Render the component
    fn render(&self, frame: &mut Frame, area: Rect);

    /// Optional: handle tick for animations
    fn tick(&mut self) {}

    /// Optional: focus management
    fn focus(&mut self) {}
    fn blur(&mut self) {}
}
```

### Example Component

```rust
pub struct ItemList {
    items: Vec<String>,
    state: ListState,
    focused: bool,
}

impl ItemList {
    pub fn new(items: Vec<String>) -> Self {
        let mut state = ListState::default();
        if !items.is_empty() {
            state.select(Some(0));
        }
        Self { items, state, focused: false }
    }

    pub fn selected(&self) -> Option<&String> {
        self.state.selected().map(|i| &self.items[i])
    }
}

impl Component for ItemList {
    fn handle_key(&mut self, key: KeyEvent) -> EventResult {
        match key.code {
            KeyCode::Up | KeyCode::Char('k') => {
                self.state.select_previous();
                EventResult::Consumed
            }
            KeyCode::Down | KeyCode::Char('j') => {
                self.state.select_next();
                EventResult::Consumed
            }
            KeyCode::Enter => {
                if let Some(item) = self.selected() {
                    EventResult::Action(Action::Select(item.clone()))
                } else {
                    EventResult::Ignored
                }
            }
            _ => EventResult::Ignored,
        }
    }

    fn render(&self, frame: &mut Frame, area: Rect) {
        let items: Vec<ListItem> = self.items.iter()
            .map(|s| ListItem::new(s.as_str()))
            .collect();

        let border_style = if self.focused {
            Style::default().cyan()
        } else {
            Style::default().dim()
        };

        let list = List::new(items)
            .block(Block::default()
                .borders(Borders::ALL)
                .border_style(border_style)
                .title("Items"))
            .highlight_style(Style::default().bold().on_dark_gray())
            .highlight_symbol("> ");

        frame.render_stateful_widget(list, area, &mut self.state.clone());
    }

    fn focus(&mut self) { self.focused = true; }
    fn blur(&mut self) { self.focused = false; }
}
```

## Action Pattern

For decoupling input handling from state changes:

```rust
/// App-level actions
#[derive(Debug, Clone)]
pub enum Action {
    Tick,
    Render,
    Quit,
    Navigate(Direction),
    Select,
    ChangeMode(Mode),
    Error(String),
    // Domain-specific actions
    LoadData,
    SaveData,
    Refresh,
}

#[derive(Debug, Clone)]
pub enum Direction {
    Up,
    Down,
    Left,
    Right,
}
```

### Action Channel Pattern

```rust
use tokio::sync::mpsc;

struct App {
    action_tx: mpsc::UnboundedSender<Action>,
    action_rx: mpsc::UnboundedReceiver<Action>,
}

impl App {
    fn new() -> Self {
        let (action_tx, action_rx) = mpsc::unbounded_channel();
        Self { action_tx, action_rx }
    }

    async fn run(&mut self) -> Result<()> {
        loop {
            // Receive actions from anywhere
            if let Some(action) = self.action_rx.recv().await {
                match action {
                    Action::Quit => break,
                    Action::Render => self.render()?,
                    action => self.handle_action(action)?,
                }
            }
        }
        Ok(())
    }

    fn handle_action(&mut self, action: Action) -> Result<()> {
        match action {
            Action::Navigate(dir) => { /* ... */ }
            Action::LoadData => {
                // Spawn background task
                let tx = self.action_tx.clone();
                tokio::spawn(async move {
                    // Load data...
                    tx.send(Action::Render).ok();
                });
            }
            _ => {}
        }
        Ok(())
    }
}
```

## State Management Strategies

### Single State Struct (Simple Apps)

```rust
struct App {
    // All state in one place
    items: Vec<Item>,
    selected: usize,
    filter: String,
    mode: Mode,
    error: Option<String>,
}
```

### Nested State (Medium Apps)

```rust
struct App {
    state: AppState,
    config: Config,
}

struct AppState {
    list: ListState,
    input: InputState,
    mode: Mode,
}

struct ListState {
    items: Vec<Item>,
    selected: usize,
    scroll: usize,
}

struct InputState {
    value: String,
    cursor: usize,
}
```

### Component-Based State (Large Apps)

```rust
struct App {
    components: Components,
    focus: FocusTarget,
    mode: Mode,
}

struct Components {
    sidebar: Sidebar,
    main_view: MainView,
    status_bar: StatusBar,
    command_palette: Option<CommandPalette>,
}

enum FocusTarget {
    Sidebar,
    MainView,
    CommandPalette,
}
```

## Modal/Dialog Pattern

```rust
enum Modal {
    None,
    Confirm { message: String, on_confirm: Action },
    Input { prompt: String, value: String },
    Error { message: String },
}

struct App {
    state: AppState,
    modal: Modal,
}

impl App {
    fn handle_key(&mut self, key: KeyEvent) {
        // Modal gets first priority
        match &mut self.modal {
            Modal::Confirm { on_confirm, .. } => {
                match key.code {
                    KeyCode::Char('y') => {
                        let action = on_confirm.clone();
                        self.modal = Modal::None;
                        self.handle_action(action);
                    }
                    KeyCode::Char('n') | KeyCode::Esc => {
                        self.modal = Modal::None;
                    }
                    _ => {}
                }
            }
            Modal::None => {
                // Normal key handling
            }
            // ...
        }
    }

    fn view(&self, frame: &mut Frame) {
        // Render main UI
        self.render_main(frame);

        // Render modal on top
        if let Some(modal_area) = self.modal_area(frame.area()) {
            self.render_modal(frame, modal_area);
        }
    }
}
```

## Mode-Based State Machine

```rust
#[derive(Default, Clone, Copy, PartialEq)]
enum Mode {
    #[default]
    Normal,
    Insert,
    Visual,
    Command,
}

impl App {
    fn handle_key(&mut self, key: KeyEvent) {
        match self.mode {
            Mode::Normal => self.handle_normal_key(key),
            Mode::Insert => self.handle_insert_key(key),
            Mode::Visual => self.handle_visual_key(key),
            Mode::Command => self.handle_command_key(key),
        }
    }

    fn handle_normal_key(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Char('i') => self.mode = Mode::Insert,
            KeyCode::Char('v') => self.mode = Mode::Visual,
            KeyCode::Char(':') => self.mode = Mode::Command,
            // Normal mode bindings...
            _ => {}
        }
    }

    fn handle_insert_key(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Esc => self.mode = Mode::Normal,
            // Insert mode bindings...
            _ => {}
        }
    }
}
```

## Best Practices

1. **Keep state normalized** - avoid duplicated data
2. **Make updates pure** - `update()` should only modify state, no I/O
3. **Batch related state** - group logically related fields
4. **Use enums for modes** - exhaustive matching catches bugs
5. **Separate concerns** - input handling, state, rendering
6. **Prefer composition** - build complex UIs from simple components
