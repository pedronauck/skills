# Ratatui Image Integration

## Overview

`ratatui-image` provides terminal image rendering using various protocols:

- **Sixel** - Wide support (xterm, foot, mlterm, etc.)
- **Kitty** - Kitty terminal native protocol
- **iTerm2** - iTerm2 and compatible terminals
- **Halfblocks** - Unicode fallback, works everywhere

## Setup

```toml
[dependencies]
ratatui-image = { version = "5", features = ["chafa-static"] }
image = "0.25"
```

### Feature Flags

| Feature        | Description                                    |
| -------------- | ---------------------------------------------- |
| `chafa-static` | Statically link libchafa for portable binaries |
| `chafa`        | Dynamic link to system libchafa                |
| `serde`        | Serialization support                          |

**Recommendation:** Use `chafa-static` for release binaries to ensure they work on any system.

## Protocol Detection

Query terminal capabilities once at startup:

```rust
use ratatui_image::picker::Picker;

fn main() -> Result<()> {
    // Query terminal for best supported protocol
    let picker = Picker::from_query_stdio()?;

    // Use picker throughout app lifetime
    run(picker)
}
```

### Manual Protocol Selection

```rust
use ratatui_image::picker::{Picker, ProtocolType};

// Force specific protocol
let picker = Picker::new(ProtocolType::Sixel);

// Or with custom font size (for accurate sizing)
let mut picker = Picker::new(ProtocolType::Kitty);
picker.set_font_size((8, 16)); // width, height in pixels
```

## Basic Usage

### StatefulImage (Recommended)

For images that need to persist across redraws:

```rust
use ratatui_image::{picker::Picker, protocol::StatefulProtocol, StatefulImage, Resize};

struct App {
    picker: Picker,
    image: Option<StatefulProtocol>,
}

impl App {
    fn load_image(&mut self, path: &Path, area: Rect) -> Result<()> {
        let dyn_img = image::open(path)?;

        // Create protocol with resize mode
        self.image = Some(self.picker.new_protocol(
            dyn_img,
            area.into(),
            Resize::Fit(None), // Fit within area, maintain aspect
        ));

        Ok(())
    }

    fn view(&mut self, frame: &mut Frame) {
        let area = frame.area();

        if let Some(ref mut img) = self.image {
            frame.render_stateful_widget(
                StatefulImage::default(),
                area,
                img,
            );
        }
    }
}
```

### Image (Simple, One-Shot)

For images rendered once:

```rust
use ratatui_image::{Image, Resize};

fn render_image(frame: &mut Frame, dyn_img: DynamicImage, area: Rect) {
    let image = Image::new(&dyn_img)
        .resize(Resize::Fit(None));

    frame.render_widget(image, area);
}
```

**Note:** `Image` re-encodes on every render. Use `StatefulImage` for persistent images.

## Resize Modes

```rust
use ratatui_image::Resize;

// Fit within area, maintain aspect ratio
Resize::Fit(None)

// Fit with specific background color for letterboxing
Resize::Fit(Some(Rgba([0, 0, 0, 255])))

// Crop to fill area (may cut edges)
Resize::Crop(None)

// Scale to exact size (distorts if aspect differs)
Resize::Scale(None)
```

## Background Thread Pattern

Image encoding is CPU-intensive. Offload to background thread:

```rust
use std::sync::mpsc;
use std::thread;

struct App {
    picker: Picker,
    image: Option<StatefulProtocol>,
    image_rx: Option<mpsc::Receiver<StatefulProtocol>>,
    loading: bool,
}

impl App {
    fn load_image_async(&mut self, path: PathBuf, area: Rect) {
        self.loading = true;

        let picker = self.picker.clone();
        let (tx, rx) = mpsc::channel();
        self.image_rx = Some(rx);

        thread::spawn(move || {
            if let Ok(dyn_img) = image::open(&path) {
                let protocol = picker.new_protocol(
                    dyn_img,
                    area.into(),
                    Resize::Fit(None),
                );
                tx.send(protocol).ok();
            }
        });
    }

    fn tick(&mut self) {
        // Check for completed image load
        if let Some(ref rx) = self.image_rx {
            if let Ok(protocol) = rx.try_recv() {
                self.image = Some(protocol);
                self.image_rx = None;
                self.loading = false;
            }
        }
    }

    fn view(&mut self, frame: &mut Frame) {
        let area = frame.area();

        if self.loading {
            frame.render_widget(
                Paragraph::new("Loading image...".dim()),
                area,
            );
        } else if let Some(ref mut img) = self.image {
            frame.render_stateful_widget(
                StatefulImage::default(),
                area,
                img,
            );
        }
    }
}
```

## Async Pattern (Tokio)

```rust
use tokio::task::spawn_blocking;
use tokio::sync::mpsc;

async fn load_image_async(
    picker: Picker,
    path: PathBuf,
    area: Rect,
    tx: mpsc::UnboundedSender<AppEvent>,
) {
    let result = spawn_blocking(move || {
        let dyn_img = image::open(&path)?;
        let protocol = picker.new_protocol(
            dyn_img,
            area.into(),
            Resize::Fit(None),
        );
        Ok::<_, image::ImageError>(protocol)
    }).await;

    match result {
        Ok(Ok(protocol)) => {
            tx.send(AppEvent::ImageLoaded(protocol)).ok();
        }
        Ok(Err(e)) => {
            tx.send(AppEvent::Error(e.to_string())).ok();
        }
        Err(e) => {
            tx.send(AppEvent::Error(e.to_string())).ok();
        }
    }
}
```

## Handling Resize

Re-encode image when terminal resizes:

```rust
impl App {
    fn handle_resize(&mut self, width: u16, height: u16) {
        self.terminal_size = (width, height);

        // Re-encode image for new size
        if self.original_image.is_some() {
            let area = self.image_area();
            self.encode_image(area);
        }
    }

    fn image_area(&self) -> Rect {
        // Calculate area based on layout
        Rect::new(0, 0, self.terminal_size.0, self.terminal_size.1 - 2)
    }
}
```

## Image Gallery Example

```rust
struct Gallery {
    picker: Picker,
    images: Vec<PathBuf>,
    current: usize,
    cached: Option<StatefulProtocol>,
    loading: bool,
}

impl Gallery {
    fn next(&mut self) {
        if self.current < self.images.len() - 1 {
            self.current += 1;
            self.cached = None; // Invalidate cache
        }
    }

    fn prev(&mut self) {
        if self.current > 0 {
            self.current -= 1;
            self.cached = None;
        }
    }

    fn ensure_loaded(&mut self, area: Rect) {
        if self.cached.is_none() && !self.loading {
            self.load_current(area);
        }
    }

    fn load_current(&mut self, area: Rect) {
        let path = &self.images[self.current];
        if let Ok(dyn_img) = image::open(path) {
            self.cached = Some(self.picker.new_protocol(
                dyn_img,
                area.into(),
                Resize::Fit(None),
            ));
        }
    }

    fn view(&mut self, frame: &mut Frame) {
        let [image_area, status_area] = Layout::vertical([
            Constraint::Fill(1),
            Constraint::Length(1),
        ]).areas(frame.area());

        // Ensure image is loaded for current area
        self.ensure_loaded(image_area);

        // Render image
        if let Some(ref mut img) = self.cached {
            frame.render_stateful_widget(
                StatefulImage::default(),
                image_area,
                img,
            );
        }

        // Status line
        let status = format!(
            " {}/{} | ←→ navigate | q quit ",
            self.current + 1,
            self.images.len()
        );
        frame.render_widget(
            Paragraph::new(status.dim()),
            status_area,
        );
    }
}
```

## Terminal Compatibility

| Terminal       | Protocol             | Notes                   |
| -------------- | -------------------- | ----------------------- |
| Kitty          | Kitty                | Native, best quality    |
| iTerm2         | iTerm2               | Native support          |
| WezTerm        | Kitty, Sixel, iTerm2 | Multiple protocols      |
| foot           | Sixel                | Good quality            |
| xterm          | Sixel                | Enable with `-ti vt340` |
| Alacritty      | Halfblocks           | No native image support |
| macOS Terminal | Halfblocks           | No native support       |

### Fallback Strategy

```rust
fn get_picker() -> Picker {
    // Try to query for best protocol
    match Picker::from_query_stdio() {
        Ok(picker) => picker,
        Err(_) => {
            // Fall back to halfblocks (always works)
            Picker::new(ProtocolType::Halfblocks)
        }
    }
}
```

## Performance Tips

1. **Query protocol once** - at startup, not per-render
2. **Use StatefulImage** - avoids re-encoding on redraws
3. **Offload encoding** - use background thread for large images
4. **Cache encoded images** - store StatefulProtocol, not DynamicImage
5. **Resize smartly** - only re-encode on terminal resize
6. **Use chafa-static** - portable and well-optimized

## Troubleshooting

### Image Not Showing

1. Check terminal supports the protocol
2. Verify image path is correct
3. Ensure area has non-zero size

### Poor Quality

1. Try different protocol (Kitty > Sixel > Halfblocks)
2. Check font size detection: `picker.set_font_size((w, h))`
3. Use `Resize::Fit` instead of `Scale`

### Slow Rendering

1. Use `StatefulImage` instead of `Image`
2. Offload encoding to background thread
3. Reduce image resolution before encoding

### Artifacts on Resize

1. Clear the image area before re-rendering
2. Re-encode with new dimensions
3. Use `terminal.clear()` if needed
