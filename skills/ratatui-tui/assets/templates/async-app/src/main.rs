use std::time::Duration;

use color_eyre::eyre::Result;
use crossterm::event::{Event, EventStream, KeyCode};
use futures::StreamExt;
use ratatui::{
    DefaultTerminal, Frame,
    layout::{Constraint, Layout},
    style::Stylize,
    text::Line,
    widgets::{Block, Borders, Paragraph},
};
use tokio::{select, time::interval};

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;
    install_panic_hook();

    let mut terminal = ratatui::init();
    let result = run(&mut terminal).await;
    ratatui::restore();

    result
}

fn install_panic_hook() {
    let original_hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |panic_info| {
        ratatui::restore();
        original_hook(panic_info);
    }));
}

#[derive(Default)]
struct App {
    counter: i32,
    tick_count: u64,
    should_quit: bool,
}

enum Message {
    Increment,
    Decrement,
    Tick,
    Quit,
}

impl App {
    fn update(&mut self, msg: Message) {
        match msg {
            Message::Increment => self.counter += 1,
            Message::Decrement => self.counter -= 1,
            Message::Tick => self.tick_count += 1,
            Message::Quit => self.should_quit = true,
        }
    }

    fn view(&self, frame: &mut Frame) {
        let [main_area, status_area, help_area] = Layout::vertical([
            Constraint::Fill(1),
            Constraint::Length(1),
            Constraint::Length(1),
        ])
        .areas(frame.area());

        let counter_text = format!("Counter: {}", self.counter);
        let paragraph = Paragraph::new(counter_text.bold().cyan())
            .centered()
            .block(Block::default().borders(Borders::ALL).title("Async App"));
        frame.render_widget(paragraph, main_area);

        let status = Line::from(vec![
            " ASYNC ".bold().on_cyan(),
            format!(" tick #{} ", self.tick_count).dim(),
        ]);
        frame.render_widget(Paragraph::new(status), status_area);

        let help = Line::from(vec![
            " ↑/k ".bold().cyan(),
            "increment ".dim(),
            " ↓/j ".bold().cyan(),
            "decrement ".dim(),
            " q ".bold().cyan(),
            "quit ".dim(),
        ]);
        frame.render_widget(Paragraph::new(help), help_area);
    }
}

async fn run(terminal: &mut DefaultTerminal) -> Result<()> {
    let mut app = App::default();
    let mut events = EventStream::new();
    let mut tick = interval(Duration::from_secs(1));

    loop {
        terminal.draw(|frame| app.view(frame))?;

        select! {
            Some(Ok(event)) = events.next() => {
                if let Event::Key(key) = event {
                    let msg = match key.code {
                        KeyCode::Char('q') => Message::Quit,
                        KeyCode::Up | KeyCode::Char('k') => Message::Increment,
                        KeyCode::Down | KeyCode::Char('j') => Message::Decrement,
                        _ => continue,
                    };
                    app.update(msg);
                }
            }
            _ = tick.tick() => {
                app.update(Message::Tick);
            }
        }

        if app.should_quit {
            break;
        }
    }

    Ok(())
}
