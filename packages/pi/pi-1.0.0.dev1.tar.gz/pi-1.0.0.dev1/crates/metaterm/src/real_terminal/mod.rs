use std::sync::{Arc, Mutex};
use tracing::info;

use crate::TerminalSize;
use pishell_eventbus::{DISPATCHER, EventListeners, ListenerHandle};

pub mod raw_terminal;
mod size_watcher;
mod terminal_info;
mod vt;

pub use terminal_info::{CursorShape, TerminalInfo, terminal_info};

pub struct RealTerminal {
    terminal_info: terminal_info::TerminalInfo,
    size_event: EventListeners<()>,
    size: Arc<Mutex<TerminalSize>>,
    #[allow(unused)]
    raw_terminal_guard: Arc<Mutex<raw_terminal::TerminalGuard>>,
    #[allow(unused)]
    size_watcher: ListenerHandle,
}

impl RealTerminal {
    pub fn new() -> Self {
        let raw_terminal_guard = raw_terminal::TerminalGuard::new().unwrap();
        let terminal_info = terminal_info::terminal_info().unwrap();
        let size = Arc::new(Mutex::new(TerminalSize::default()));
        let (size_event_source, size_event) = DISPATCHER.tear_off();

        let size_watcher = {
            let size_holder = size.clone();
            let size_watcher = size_watcher::subscribe(move |_| {
                if let Ok(ws) = size_watcher::query_winsize() {
                    info!("Real terminal size changed to: {:?}", ws);
                    *size_holder.lock().unwrap() = ws;
                    size_event_source.send(());
                }
            });
            size_watcher
        };

        Self {
            raw_terminal_guard: Arc::new(Mutex::new(raw_terminal_guard)),
            terminal_info,
            size_watcher,
            size,
            size_event,
        }
    }

    pub fn size(&self) -> TerminalSize {
        *self.size.lock().unwrap()
    }

    pub fn on_size_change(
        &self,
        mut callback: impl FnMut(TerminalSize) + Send + 'static,
    ) -> ListenerHandle {
        let size_holder = self.size.clone();
        self.size_event.subscribe(move |_| {
            let size = size_holder.lock().unwrap();
            callback(*size);
        })
    }

    pub fn terminal_info(&self) -> &terminal_info::TerminalInfo {
        &self.terminal_info
    }
}
