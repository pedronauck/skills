mod action;
mod app;
mod config;
mod event;
mod logging;
mod tui;
mod ui;

use clap::Parser;
use color_eyre::eyre::Result;

use crate::app::App;
use crate::config::Config;
use crate::event::EventHandler;
use crate::logging::init_logging;
use crate::tui::Tui;

#[derive(Parser)]
#[command(name = "component-app")]
#[command(about = "A ratatui TUI application")]
struct Cli {
    /// Config file path
    #[arg(short, long)]
    config: Option<std::path::PathBuf>,

    /// Enable debug logging
    #[arg(short, long)]
    debug: bool,
}

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;

    let cli = Cli::parse();

    let config = Config::load(cli.config.as_deref())?;
    init_logging(&config, cli.debug)?;

    tracing::info!("Starting application");

    let mut tui = Tui::new()?;
    let events = EventHandler::new(config.tick_rate);
    let mut app = App::new(config);

    tui.enter()?;
    let result = app.run(&mut tui, events).await;
    tui.exit()?;

    result
}
