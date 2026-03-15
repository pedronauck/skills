use color_eyre::eyre::Result;

use crate::action::{Action, Direction};
use crate::config::Config;
use crate::event::{AppEvent, EventHandler};
use crate::tui::Tui;
use crate::ui;

pub struct App {
    config: Config,
    items: Vec<String>,
    selected: usize,
    should_quit: bool,
}

impl App {
    pub fn new(config: Config) -> Self {
        Self {
            config,
            items: vec![
                "Item 1".into(),
                "Item 2".into(),
                "Item 3".into(),
                "Item 4".into(),
                "Item 5".into(),
            ],
            selected: 0,
            should_quit: false,
        }
    }

    pub async fn run(&mut self, tui: &mut Tui, mut events: EventHandler) -> Result<()> {
        loop {
            tui.draw(|frame| ui::render(frame, self))?;

            let action = match events.next().await? {
                AppEvent::Tick => Action::Tick,
                AppEvent::Key(key) => self.handle_key(key),
                AppEvent::Resize(_, _) => Action::Render,
            };

            self.update(action);

            if self.should_quit {
                break;
            }
        }

        Ok(())
    }

    fn handle_key(&self, key: crossterm::event::KeyEvent) -> Action {
        use crossterm::event::KeyCode;

        match key.code {
            KeyCode::Char('q') => Action::Quit,
            KeyCode::Up | KeyCode::Char('k') => Action::Navigate(Direction::Up),
            KeyCode::Down | KeyCode::Char('j') => Action::Navigate(Direction::Down),
            KeyCode::Enter => Action::Select,
            _ => Action::Tick,
        }
    }

    fn update(&mut self, action: Action) {
        match action {
            Action::Quit => self.should_quit = true,
            Action::Navigate(Direction::Up) => {
                self.selected = self.selected.saturating_sub(1);
            }
            Action::Navigate(Direction::Down) => {
                if self.selected < self.items.len().saturating_sub(1) {
                    self.selected += 1;
                }
            }
            Action::Select => {
                tracing::info!("Selected: {}", self.items[self.selected]);
            }
            Action::Error(msg) => {
                tracing::error!("Error: {}", msg);
            }
            Action::Tick | Action::Render => {}
        }
    }

    pub fn items(&self) -> &[String] {
        &self.items
    }

    pub fn selected(&self) -> usize {
        self.selected
    }

    #[allow(dead_code)]
    pub fn config(&self) -> &Config {
        &self.config
    }
}
