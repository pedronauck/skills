use ratatui::{
    Frame,
    layout::{Constraint, Layout},
    style::Stylize,
    text::Line,
    widgets::{Block, Borders, List, ListItem, Paragraph},
};

use crate::app::App;

pub fn render(frame: &mut Frame, app: &App) {
    let [main_area, status_area, help_area] = Layout::vertical([
        Constraint::Fill(1),
        Constraint::Length(1),
        Constraint::Length(1),
    ])
    .areas(frame.area());

    render_list(frame, app, main_area);
    render_status(frame, status_area);
    render_help(frame, help_area);
}

fn render_list(frame: &mut Frame, app: &App, area: ratatui::layout::Rect) {
    let items: Vec<ListItem> = app
        .items()
        .iter()
        .enumerate()
        .map(|(i, item)| {
            let content = if i == app.selected() {
                format!("> {}", item).bold().cyan()
            } else {
                format!("  {}", item).dim()
            };
            ListItem::new(content)
        })
        .collect();

    let list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title("Items".bold().cyan()),
    );

    frame.render_widget(list, area);
}

fn render_status(frame: &mut Frame, area: ratatui::layout::Rect) {
    let status = Line::from(vec![" NORMAL ".bold().on_cyan(), " Ready ".dim()]);
    frame.render_widget(Paragraph::new(status), area);
}

fn render_help(frame: &mut Frame, area: ratatui::layout::Rect) {
    let help = Line::from(vec![
        " ↑/k ".bold().cyan(),
        "up ".dim(),
        " ↓/j ".bold().cyan(),
        "down ".dim(),
        " Enter ".bold().cyan(),
        "select ".dim(),
        " q ".bold().cyan(),
        "quit ".dim(),
    ]);
    frame.render_widget(Paragraph::new(help), area);
}
