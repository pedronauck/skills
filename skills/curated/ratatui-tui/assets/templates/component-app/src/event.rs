use std::time::Duration;

use color_eyre::eyre::Result;
use crossterm::event::{Event, EventStream, KeyEvent};
use futures::StreamExt;
use tokio::{select, time::interval};

#[allow(dead_code)]
pub enum AppEvent {
    Tick,
    Key(KeyEvent),
    Resize(u16, u16),
}

pub struct EventHandler {
    events: EventStream,
    tick_rate: Duration,
}

impl EventHandler {
    pub fn new(tick_rate: Duration) -> Self {
        Self {
            events: EventStream::new(),
            tick_rate,
        }
    }

    pub async fn next(&mut self) -> Result<AppEvent> {
        let mut tick = interval(self.tick_rate);

        select! {
            Some(Ok(event)) = self.events.next() => {
                match event {
                    Event::Key(key) => Ok(AppEvent::Key(key)),
                    Event::Resize(w, h) => Ok(AppEvent::Resize(w, h)),
                    _ => Ok(AppEvent::Tick),
                }
            }
            _ = tick.tick() => {
                Ok(AppEvent::Tick)
            }
        }
    }
}
