# Ratatui Style Guide

## Stylize Trait

Always use the `Stylize` trait for inline styling. Import it:

```rust
use ratatui::style::Stylize;
```

### Cheatsheet

```rust
// Modifiers
"text".bold()
"text".dim()
"text".italic()
"text".underlined()
"text".reversed()

// Foreground colors
"text".cyan()
"text".green()
"text".red()
"text".magenta()
"text".yellow()
"text".white()
"text".gray()
"text".dark_gray()

// Background colors
"text".on_black()
"text".on_dark_gray()
"text".on_cyan()
"text".on_red()

// Chaining
"text".bold().cyan()
"text".dim().on_dark_gray()
"header".bold().cyan().on_dark_gray()
```

### Color Semantic Mapping

| Purpose         | Style            | Example                   |
| --------------- | ---------------- | ------------------------- |
| Primary action  | `.cyan()`        | Selected item, active tab |
| Success         | `.green()`       | Completion, valid input   |
| Error           | `.red()`         | Errors, invalid input     |
| Warning         | `.yellow()`      | Caution (use sparingly)   |
| Muted/secondary | `.dim()`         | Help text, metadata       |
| Accent          | `.magenta()`     | Highlights, special items |
| Key bindings    | `.bold().cyan()` | Keyboard shortcuts        |

## What to Avoid

### Hardcoded Colors

```rust
// Bad - hardcoded white/black don't adapt to terminal themes
Style::default().fg(Color::White)
Style::default().fg(Color::Black)
Style::default().bg(Color::Blue)  // blue often unreadable

// Good - use semantic colors or let terminal theme handle it
"text".cyan()
"text".dim()
Style::default()  // inherits terminal default
```

### Verbose Style Construction

```rust
// Bad - verbose
Style::new().add_modifier(Modifier::BOLD)
Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)

// Good - concise
"text".bold()
"text".bold().cyan()
```

### Manual Style Objects for Spans

```rust
// Bad
Span::styled("text", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))

// Good
"text".bold().cyan()
```

## Text Wrapping

Use `textwrap` crate for wrapping long text:

```rust
use textwrap::wrap;
use ratatui::text::Line;

fn wrap_text(text: &str, width: u16) -> Vec<Line<'static>> {
    wrap(text, width as usize)
        .into_iter()
        .map(|cow| Line::from(cow.into_owned()))
        .collect()
}
```

### Wrapping with Style

```rust
fn wrap_styled(text: &str, width: u16) -> Vec<Line<'static>> {
    wrap(text, width as usize)
        .into_iter()
        .map(|cow| Line::from(cow.into_owned().dim()))
        .collect()
}
```

## Building Lines and Spans

### Simple Line

```rust
let line = Line::from("Simple text");
```

### Mixed Styles

```rust
let line = Line::from(vec![
    "Key: ".dim(),
    "value".cyan(),
]);
```

### Status Bar Pattern

```rust
let status = Line::from(vec![
    " MODE ".bold().on_cyan(),
    " ".into(),
    format!("{} items", count).dim(),
]);
```

### Key Binding Help

```rust
let help = Line::from(vec![
    " q ".bold().cyan(),
    "quit ".dim(),
    " ↑↓ ".bold().cyan(),
    "navigate ".dim(),
    " Enter ".bold().cyan(),
    "select".dim(),
]);
```

## Block Styling

```rust
use ratatui::widgets::{Block, Borders};

// Simple border
Block::default()
    .borders(Borders::ALL)
    .title("Title")

// Styled border
Block::default()
    .borders(Borders::ALL)
    .border_style(Style::default().dim())
    .title("Title".bold().cyan())

// Rounded corners
Block::default()
    .borders(Borders::ALL)
    .border_type(BorderType::Rounded)
```

## Table Styling

```rust
use ratatui::widgets::{Table, Row, Cell};

let rows = items.iter().enumerate().map(|(i, item)| {
    let style = if i == selected {
        Style::default().bg(Color::DarkGray)
    } else {
        Style::default()
    };
    Row::new(vec![
        Cell::from(item.name.clone()),
        Cell::from(item.value.to_string().dim()),
    ]).style(style)
});

Table::new(rows, [Constraint::Fill(1), Constraint::Length(10)])
    .header(Row::new(vec!["Name".bold(), "Value".bold()]))
    .highlight_style(Style::default().on_dark_gray())
```

## List Styling

```rust
use ratatui::widgets::{List, ListItem};

let items: Vec<ListItem> = data.iter()
    .map(|s| ListItem::new(s.as_str()))
    .collect();

List::new(items)
    .block(Block::default().borders(Borders::ALL).title("Items"))
    .highlight_style(Style::default().bold().on_dark_gray())
    .highlight_symbol("> ")
```

## Scrollbar

```rust
use ratatui::widgets::{Scrollbar, ScrollbarOrientation, ScrollbarState};

let scrollbar = Scrollbar::default()
    .orientation(ScrollbarOrientation::VerticalRight)
    .symbols(scrollbar::VERTICAL);

let mut scrollbar_state = ScrollbarState::new(total_items)
    .position(current_position);

frame.render_stateful_widget(scrollbar, area, &mut scrollbar_state);
```

## Terminal Theme Compatibility

Design for both light and dark terminals:

1. **Avoid pure white/black** - use `.dim()` for low-contrast text
2. **Test both themes** - colors render differently
3. **Use relative brightness** - `.dim()`, `.bold()` adapt better
4. **Prefer cyan/green/magenta** - readable on most themes
5. **Avoid blue** - often too dark on dark terminals

## Accessibility

- High contrast for important elements (`.bold()`)
- Low contrast for secondary info (`.dim()`)
- Don't rely solely on color - use symbols too
- Provide key binding hints
