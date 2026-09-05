use std::time::Duration;

use color_eyre::eyre::Result;
use crossterm::event::{self, Event, KeyCode};
use ratatui::{
    DefaultTerminal, Frame,
    layout::{Constraint, Layout},
    style::Stylize,
    text::Line,
    widgets::{Block, Borders, Paragraph},
};

fn main() -> Result<()> {
    color_eyre::install()?;
    install_panic_hook();

    let mut terminal = ratatui::init();
    let result = run(&mut terminal);
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
        let [main_area, help_area] =
            Layout::vertical([Constraint::Fill(1), Constraint::Length(1)]).areas(frame.area());

        let counter_text = format!("Counter: {}", self.counter);
        let paragraph = Paragraph::new(counter_text.bold().cyan())
            .centered()
            .block(Block::default().borders(Borders::ALL).title("Simple App"));

        frame.render_widget(paragraph, main_area);

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

fn run(terminal: &mut DefaultTerminal) -> Result<()> {
    let mut app = App::default();

    loop {
        terminal.draw(|frame| app.view(frame))?;

        if event::poll(Duration::from_millis(100))?
            && let Event::Key(key) = event::read()?
        {
            let msg = match key.code {
                KeyCode::Char('q') => Message::Quit,
                KeyCode::Up | KeyCode::Char('k') => Message::Increment,
                KeyCode::Down | KeyCode::Char('j') => Message::Decrement,
                _ => continue,
            };
            app.update(msg);
        }

        if app.should_quit {
            break;
        }
    }

    Ok(())
}
