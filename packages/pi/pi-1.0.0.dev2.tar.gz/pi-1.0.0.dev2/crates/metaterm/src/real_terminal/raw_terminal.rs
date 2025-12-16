use crossterm::terminal::{disable_raw_mode, enable_raw_mode};
use std::io;
use tracing::debug;

/// Configure terminal for raw mode
pub fn configure_terminal_raw() -> io::Result<()> {
    debug!("Configuring terminal for raw mode");
    enable_raw_mode()?;
    Ok(())
}

/// Restore terminal to normal mode
pub fn restore_terminal() -> io::Result<()> {
    debug!("Restoring terminal to normal mode");
    disable_raw_mode()?;
    Ok(())
}

/// RAII guard to automatically restore terminal settings when dropped
pub struct TerminalGuard;

impl TerminalGuard {
    /// Create a new terminal guard
    pub fn new() -> io::Result<Self> {
        configure_terminal_raw()?;
        Ok(TerminalGuard)
    }
}

impl Drop for TerminalGuard {
    fn drop(&mut self) {
        if let Err(e) = restore_terminal() {
            debug!("Failed to restore terminal: {}", e);
        }
    }
}

impl Default for TerminalGuard {
    fn default() -> Self {
        Self::new().unwrap_or_else(|_| TerminalGuard)
    }
}
