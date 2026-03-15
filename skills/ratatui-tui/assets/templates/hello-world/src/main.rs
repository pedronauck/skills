use ratatui::{
    Frame,
    crossterm::event::{self, Event, KeyCode},
    style::Stylize,
    widgets::Paragraph,
};

fn main() {
    let mut terminal = ratatui::init();
    loop {
        terminal.draw(render).expect("failed to draw frame");
        if matches!(event::read().expect("failed to read event"), Event::Key(key) if key.code == KeyCode::Char('q'))
        {
            break;
        }
    }
    ratatui::restore();
}

fn render(frame: &mut Frame) {
    let text = "Hello, ratatui! Press 'q' to quit.".bold().cyan();
    frame.render_widget(Paragraph::new(text).centered(), frame.area());
}
