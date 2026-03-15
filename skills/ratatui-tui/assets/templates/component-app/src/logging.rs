use color_eyre::eyre::Result;
use tracing_subscriber::{EnvFilter, fmt, prelude::*};

use crate::config::Config;

pub fn init_logging(_config: &Config, debug: bool) -> Result<()> {
    let filter = if debug {
        EnvFilter::new("debug")
    } else {
        EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"))
    };

    // Log to file in config directory
    let log_dir = dirs::data_local_dir()
        .unwrap_or_else(|| std::path::PathBuf::from("."))
        .join("component-app")
        .join("logs");

    std::fs::create_dir_all(&log_dir)?;

    let log_file = std::fs::File::create(log_dir.join("app.log"))?;

    tracing_subscriber::registry()
        .with(filter)
        .with(
            fmt::layer()
                .with_writer(log_file)
                .with_ansi(false)
                .with_target(true),
        )
        .init();

    Ok(())
}
