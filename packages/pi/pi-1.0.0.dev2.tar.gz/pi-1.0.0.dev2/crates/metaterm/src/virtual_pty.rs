use crossterm::ExecutableCommand;
use std::sync::{
    Arc, Mutex,
    atomic::{AtomicUsize, Ordering},
};

use crate::terminal_size::TerminalSize;

const SCROLLBACK_CAPACITY: usize = 10000;
const HISTORY_SIZE: usize = 1000;

// Keep in sync with chat.py
const TRANSPARENT_CHAR: char = '\u{e000}';
const TRANSPARENT_CHAR_BYTES: &[u8] = {
    let mut bytes = [0; 3];
    let len = TRANSPARENT_CHAR.encode_utf8(&mut bytes).as_bytes().len();
    if len != 3 {
        panic!("TRANSPARENT_CHAR is not 3 bytes long");
    }
    &[bytes[0], bytes[1], bytes[2]]
};

/// A virtual PTY that maintains an internal VT100 parser state
/// and can render the screen as ANSI-formatted output
#[derive(Clone)]
pub struct VirtualPty {
    parser: Arc<Mutex<vt100::Parser>>,
    change_count: Arc<AtomicUsize>,
}

fn new_vt100_parser(rows: u16, cols: u16) -> vt100::Parser {
    vt100::Parser::builder()
        .size(rows, cols)
        .scrollback(SCROLLBACK_CAPACITY)
        .history(HISTORY_SIZE)
        .build()
}

impl VirtualPty {
    /// Create a new VirtualPty with the specified dimensions
    pub fn new(size: TerminalSize) -> Self {
        Self {
            parser: Arc::new(Mutex::new(new_vt100_parser(size.rows, size.cols))),
            change_count: Arc::new(AtomicUsize::new(0)),
        }
    }

    /// Feed data to the VT100 parser
    pub fn feed(&self, data: &[u8]) {
        let mut parser = self.parser.lock().unwrap();
        parser.process(data);
        self.change_count.fetch_add(1, Ordering::Relaxed);
    }

    /// Get the raw screen contents as a string
    pub fn dump(&self) -> String {
        let parser = self.parser.lock().unwrap();
        parser.screen().contents().to_string()
    }

    /// Get the current change count
    pub fn get_change_count(&self) -> usize {
        self.change_count.load(Ordering::Relaxed)
    }

    pub fn set_cursor_position(&self, row: u16, col: u16) {
        let mut parser = self.parser.lock().unwrap();
        _ = parser.execute(crossterm::cursor::MoveTo(col, row));
        self.change_count.fetch_add(1, Ordering::Relaxed);
    }

    pub fn clear(&self) {
        let mut parser = self.parser.lock().unwrap();
        let size = parser.screen().size();
        *parser = new_vt100_parser(size.0, size.1);
        self.change_count.fetch_add(1, Ordering::Relaxed);
    }

    /// Get the current terminal size
    pub fn size(&self) -> TerminalSize {
        let parser = self.parser.lock().unwrap();
        let screen = parser.screen();
        let (rows, cols) = screen.size();
        TerminalSize::new(rows, cols)
    }

    /// Resize the virtual terminal
    pub fn resize(&self, size: TerminalSize) {
        self.parser
            .lock()
            .unwrap()
            .screen_mut()
            .set_size(size.rows, size.cols);
        self.change_count.fetch_add(1, Ordering::Relaxed);
    }

    /// Get cursor position (row, col)
    pub fn cursor_position(&self) -> (u16, u16) {
        let parser = self.parser.lock().unwrap();
        let screen = parser.screen();
        screen.cursor_position()
    }

    /// Check if cursor is visible
    pub fn is_cursor_visible(&self) -> bool {
        let parser = self.parser.lock().unwrap();
        let screen = parser.screen();
        !screen.hide_cursor()
    }

    pub fn is_alternate_screen(&self) -> bool {
        let parser = self.parser.lock().unwrap();
        let screen = parser.screen();
        screen.alternate_screen()
    }

    pub fn get_input_mode_formatted(&self) -> Vec<u8> {
        let parser = self.parser.lock().unwrap();
        parser.screen().input_mode_formatted()
    }

    /// Get full screen as ANSI-formatted string with proper color and attribute handling
    pub fn get_ansi_screen(
        &self,
        dimmed: bool,
        end_row: Option<u16>,
        end_col: Option<u16>,
    ) -> Vec<String> {
        let parser = self.parser.lock().unwrap();
        self.get_ansi_screen_region(&parser, dimmed, 0, 0, end_row, end_col)
    }

    /// Copy a region of the screen to a target parser at a given position
    /// If overlay_source is provided and a cell contains the background
    /// character (`TRANSPARENT_CHAR`),
    /// the corresponding cell from overlay_source is rendered instead (dimmed)
    pub fn copy_screen(
        &self,
        dimmed: bool,
        start_row: u16,
        start_col: u16,
        end_row: Option<u16>,
        end_col: Option<u16>,
        target: &mut vt100::Parser,
        target_row: u16,
        target_col: u16,
        overlay_source: Option<&VirtualPty>,
    ) {
        let parser = self.parser.lock().unwrap();
        let screen = parser.screen();

        // Clamp coordinates to screen bounds
        let start_row = start_row.min(screen.size().0 - 1);
        let start_col = start_col.min(screen.size().1 - 1);
        let end_row = end_row
            .unwrap_or(screen.size().0 - 1)
            .min(screen.size().0 - 1);
        let end_col = end_col
            .unwrap_or(screen.size().1 - 1)
            .min(screen.size().1 - 1);

        for row in start_row..=end_row {
            let target_row = target_row + row - start_row;

            let mut row_dirty = false;
            for col in start_col..=end_col {
                let screen_cell = screen.cell(row, col).unwrap();
                let target_cell = target
                    .screen()
                    .cell(target_row, target_col + col - start_col)
                    .unwrap();

                if dimmed {
                    if map_color_dimmed(screen_cell.fgcolor()) != target_cell.fgcolor()
                        || map_color_dimmed(screen_cell.bgcolor()) != target_cell.bgcolor()
                        || screen_cell.contents() != target_cell.contents()
                        || screen_cell.bold() != target_cell.bold()
                        || screen_cell.italic() != target_cell.italic()
                        || screen_cell.underline() != target_cell.underline()
                        || screen_cell.inverse() != target_cell.inverse()
                    {
                        row_dirty = true;
                        break;
                    }
                } else {
                    if screen_cell != target_cell {
                        row_dirty = true;
                        break;
                    }
                }
            }

            if row_dirty {
                // If we have an overlay source, use a two-pass approach:
                // 1. First render underscreen (shell), skipping positions with overlay content
                // 2. Then render overscreen (sidebar) on top
                if let Some(overlay) = overlay_source {
                    let overlay_parser = overlay.parser.lock().unwrap();
                    let overlay_screen = overlay_parser.screen();

                    // First pass: render underscreen (shell), skipping overlay positions
                    let mut col = start_col;
                    while col <= end_col {
                        let screen_cell = screen.cell(row, col).unwrap();
                        let cell_content = screen_cell.contents();

                        // If this position will be overlaid by sidebar content (not background char)
                        if cell_content.as_bytes() != TRANSPARENT_CHAR_BYTES {
                            // Skip this position - we'll render sidebar content here in second pass
                            col += 1;
                            continue;
                        }

                        // This position has background character, so render shell content
                        if let Some(overlay_cell) = overlay_screen.cell(row, col) {
                            // Move to position
                            target.process(
                                &format!(
                                    "\x1b[{};{}H",
                                    target_row + 1,
                                    target_col + col - start_col + 1
                                )
                                .as_bytes(),
                            );
                            // Render shell cell (dimmed)
                            let (ansi, wide) = Self::render_single_cell(&overlay_cell, true);
                            target.process(ansi.as_bytes());
                            if wide {
                                col += 1;
                            }
                        }
                        col += 1;
                    }

                    // Second pass: render overscreen (sidebar content), skipping background chars
                    col = start_col;
                    while col <= end_col {
                        let screen_cell = screen.cell(row, col).unwrap();
                        let cell_content = screen_cell.contents();

                        // Only render actual sidebar content (not background character)
                        if cell_content.as_bytes() != TRANSPARENT_CHAR_BYTES {
                            // Move to position
                            target.process(
                                &format!(
                                    "\x1b[{};{}H",
                                    target_row + 1,
                                    target_col + col - start_col + 1
                                )
                                .as_bytes(),
                            );
                            // Render sidebar cell (not dimmed)
                            let (ansi, wide) = Self::render_single_cell(&screen_cell, false);
                            if wide {
                                col += 1;
                            }
                            target.process(ansi.as_bytes());
                        }
                        col += 1;
                    }
                } else {
                    // Original behavior when no overlay source
                    let ansi = self.get_ansi_screen_region(
                        &parser,
                        dimmed,
                        row,
                        start_col,
                        Some(row),
                        Some(end_col),
                    );
                    // Move to row/col
                    target.process(
                        &format!("\x1b[{};{}H", target_row + 1, target_col + 1).as_bytes(),
                    );
                    // Write the ANSI contents
                    target.process(&ansi[0].as_bytes());
                }
            }
        }
    }

    /// Render a single cell with its attributes as an ANSI string
    fn render_single_cell(cell: &vt100::Cell, dimmed: bool) -> (String, bool) {
        let mut result = String::new();

        // Reset attributes
        result.push_str("\x1b[0m");

        // Apply cell attributes
        if cell.bold() {
            result.push_str("\x1b[1m");
        }
        if cell.italic() {
            result.push_str("\x1b[3m");
        }
        if cell.underline() {
            result.push_str("\x1b[4m");
        }
        if cell.inverse() {
            result.push_str("\x1b[7m");
        }

        // Apply foreground color
        let fg = if dimmed {
            map_color_dimmed(cell.fgcolor())
        } else {
            cell.fgcolor()
        };

        match fg {
            vt100::Color::Default => {
                // Don't set anything, use terminal default
            }
            vt100::Color::Idx(n) if n < 8 => {
                result.push_str(&format!("\x1b[3{}m", n));
            }
            vt100::Color::Idx(n) if n < 16 => {
                result.push_str(&format!("\x1b[9{}m", n - 8));
            }
            vt100::Color::Idx(n) => {
                result.push_str(&format!("\x1b[38;5;{}m", n));
            }
            vt100::Color::Rgb(r, g, b) => {
                result.push_str(&format!("\x1b[38;2;{};{};{}m", r, g, b));
            }
        }

        // Apply background color
        let bg = if dimmed {
            map_color_dimmed(cell.bgcolor())
        } else {
            cell.bgcolor()
        };

        match bg {
            vt100::Color::Default => {
                // Don't set anything, use terminal default
            }
            vt100::Color::Idx(n) if n < 8 => {
                result.push_str(&format!("\x1b[4{}m", n));
            }
            vt100::Color::Idx(n) if n < 16 => {
                result.push_str(&format!("\x1b[10{}m", n - 8));
            }
            vt100::Color::Idx(n) => {
                result.push_str(&format!("\x1b[48;5;{}m", n));
            }
            vt100::Color::Rgb(r, g, b) => {
                result.push_str(&format!("\x1b[48;2;{};{};{}m", r, g, b));
            }
        }

        // Add the character content
        let content = cell.contents();
        if content.is_empty() || content == "\0" {
            result.push(' ');
        } else {
            result.push_str(&content);
        }

        (result, cell.is_wide())
    }

    /// Get the last `n` commands from the shell attached to this PTY,
    /// most recent command first.
    pub fn command_history(&self, n: usize) -> Vec<vt100::CommandHistory> {
        let parser = self.parser.lock().unwrap();
        parser
            .screen()
            .command_history()
            .rev()
            .take(n)
            .cloned()
            .collect()
    }

    /// Attempt to obtain output of command given command sequence number.
    /// If the output scrolled past scrollback buffer limit, or if the
    /// command is too old (beyond history limit), `None` is returned.
    pub fn command_output_by_number(&self, command_number: usize) -> Option<String> {
        let parser = self.parser.lock().unwrap();
        let screen = parser.screen();
        screen
            .command_by_number(command_number)
            .and_then(|cmd| cmd.output(screen))
    }

    /// Get full screen as ANSI-formatted string with proper color and attribute handling
    fn get_ansi_screen_region(
        &self,
        parser: &vt100::Parser,
        dimmed: bool,
        start_row: u16,
        start_col: u16,
        end_row: Option<u16>,
        end_col: Option<u16>,
    ) -> Vec<String> {
        let screen = parser.screen();

        // Clamp coordinates to screen bounds
        let start_row = start_row.min(screen.size().0);
        let start_col = start_col.min(screen.size().1);
        let end_row = end_row.unwrap_or(screen.size().0 - 1);
        let end_col = end_col.unwrap_or(screen.size().1 - 1);

        let mut output = Vec::new();
        let mut last_attrs = (
            vt100::Color::Default,
            vt100::Color::Default,
            false,
            false,
            false,
            false,
        );

        // Get cursor info
        let (cursor_row, cursor_col) = screen.cursor_position();
        let cursor_visible = !screen.hide_cursor();

        for row in start_row..=end_row {
            let mut line = String::new();

            for col in start_col..=end_col {
                let cell = screen.cell(row, col).unwrap();

                // Check if this is the cursor position
                let is_cursor = cursor_visible && row == cursor_row && col == cursor_col;

                let attrs = (
                    if dimmed {
                        map_color_dimmed(cell.fgcolor())
                    } else {
                        cell.fgcolor()
                    },
                    if dimmed {
                        map_color_dimmed(cell.bgcolor())
                    } else {
                        cell.bgcolor()
                    },
                    cell.bold(),
                    cell.italic(),
                    cell.underline(),
                    is_cursor || cell.inverse(), // Add inverse for cursor or cell inverse
                );

                // Only emit escape codes when attributes change or we're on the first cell
                if attrs != last_attrs || (row == start_row && col == start_col) {
                    // Reset first
                    line.push_str("\x1b[0m");

                    // Apply new attributes
                    if cell.bold() {
                        line.push_str("\x1b[1m");
                    }
                    if cell.italic() {
                        line.push_str("\x1b[3m");
                    }
                    if cell.underline() {
                        line.push_str("\x1b[4m");
                    }
                    if is_cursor || cell.inverse() {
                        line.push_str("\x1b[7m"); // Inverse video
                    }

                    // Foreground color
                    match attrs.0 {
                        vt100::Color::Default => {
                            // Don't set anything, use terminal default
                        }
                        vt100::Color::Idx(n) if n < 8 => {
                            line.push_str(&format!("\x1b[3{}m", n));
                        }
                        vt100::Color::Idx(n) if n < 16 => {
                            line.push_str(&format!("\x1b[9{}m", n - 8));
                        }
                        vt100::Color::Idx(n) => {
                            line.push_str(&format!("\x1b[38;5;{}m", n));
                        }
                        vt100::Color::Rgb(r, g, b) => {
                            line.push_str(&format!("\x1b[38;2;{};{};{}m", r, g, b));
                        }
                    }

                    // Background color
                    match attrs.1 {
                        vt100::Color::Default => {
                            // Don't set anything, use terminal default
                        }
                        vt100::Color::Idx(n) if n < 8 => {
                            line.push_str(&format!("\x1b[4{}m", n));
                        }
                        vt100::Color::Idx(n) if n < 16 => {
                            line.push_str(&format!("\x1b[10{}m", n - 8));
                        }
                        vt100::Color::Idx(n) => {
                            line.push_str(&format!("\x1b[48;5;{}m", n));
                        }
                        vt100::Color::Rgb(r, g, b) => {
                            line.push_str(&format!("\x1b[48;2;{};{};{}m", r, g, b));
                        }
                    }

                    last_attrs = attrs;
                }

                // Get the character content
                let content = cell.contents();
                if content.is_empty() || content == "\0" {
                    line.push(' '); // Use space for empty cells
                } else {
                    line.push_str(&content);
                }
            }

            output.push(line);
        }

        output
    }
}

impl Default for VirtualPty {
    fn default() -> Self {
        Self::new(TerminalSize::new(24, 80))
    }
}

fn map_color_dimmed(color: vt100::Color) -> vt100::Color {
    match color {
        vt100::Color::Default => vt100::Color::Default,
        vt100::Color::Idx(n) if n < 8 => {
            match n {
                0 => vt100::Color::Idx(0), // Black stays black
                _ => vt100::Color::Idx(8), // Other dark colors become dark grey
            }
        }
        vt100::Color::Idx(_) => vt100::Color::Idx(8), // Dark grey
        vt100::Color::Rgb(r, g, b) => {
            // If very dark (sum of RGB < 100), use black, otherwise grey
            let grey = ((r as u32 + g as u32 + b as u32) / 3) as u8;
            vt100::Color::Rgb(grey, grey, grey)
        }
    }
}
