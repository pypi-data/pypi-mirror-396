#[derive(Clone, Copy, PartialEq, Eq)]
pub struct TerminalSize {
    pub rows: u16,
    pub cols: u16,
    pub pixel_size: Option<(u16, u16)>,
}

impl std::fmt::Debug for TerminalSize {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}x{}", self.rows, self.cols)?;
        if let Some((pixel_width, pixel_height)) = self.pixel_size {
            write!(f, " (char {}px x {}px)", pixel_width, pixel_height)?;
        }
        Ok(())
    }
}

impl Default for TerminalSize {
    fn default() -> Self {
        Self {
            rows: 25,
            cols: 80,
            pixel_size: None,
        }
    }
}

impl TerminalSize {
    pub fn new(rows: u16, cols: u16) -> Self {
        Self {
            rows,
            cols,
            pixel_size: None,
        }
    }

    pub fn from_winsize(ws: libc::winsize) -> Self {
        Self {
            rows: ws.ws_row,
            cols: ws.ws_col,
            pixel_size: if ws.ws_xpixel > 0 && ws.ws_ypixel > 0 {
                Some((ws.ws_xpixel / ws.ws_col, ws.ws_ypixel / ws.ws_row))
            } else {
                None
            },
        }
    }

    pub fn subtract_cols(self, cols: u16) -> Self {
        Self {
            cols: self.cols.saturating_sub(cols),
            ..self
        }
    }

    pub fn subtract_rows(self, rows: u16) -> Self {
        Self {
            rows: self.rows.saturating_sub(rows),
            ..self
        }
    }

    pub fn with_cols(self, cols: u16) -> Self {
        Self { cols, ..self }
    }

    pub fn with_rows(self, rows: u16) -> Self {
        Self { rows, ..self }
    }

    pub fn winsize(&self) -> libc::winsize {
        libc::winsize {
            ws_row: self.rows,
            ws_col: self.cols,
            ws_xpixel: self.pixel_size.unwrap_or((10, 10)).0 * self.cols,
            ws_ypixel: self.pixel_size.unwrap_or((10, 10)).1 * self.rows,
        }
    }
}

pub fn term_size() -> Option<TerminalSize> {
    term_size_ioctl()
        .or_else(term_size_stty)
        .or_else(term_size_env)
        .map(|(rows, cols)| TerminalSize::new(rows, cols))
}

/// Use ioctl to get the terminal size
fn term_size_ioctl() -> Option<(u16, u16)> {
    if let Some((width, height)) = terminal_size::terminal_size() {
        Some((height.0, width.0))
    } else {
        None
    }
}

/// Use environment variables to get the terminal size
fn term_size_env() -> Option<(u16, u16)> {
    if let Ok(lines) = std::env::var("LINES") {
        if let Ok(columns) = std::env::var("COLUMNS") {
            return Some((lines.parse().unwrap(), columns.parse().unwrap()));
        }
    }

    None
}

/// Use stty to get the terminal size
fn term_size_stty() -> Option<(u16, u16)> {
    // Use sh -c to run stty in a subshell with its own stdin
    let output = std::process::Command::new("sh")
        .arg("-c")
        .arg("stty size < /dev/tty 2>/dev/null")
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::null())
        .output()
        .ok()?;

    if !output.status.success() {
        return None;
    }

    let size_str = String::from_utf8_lossy(&output.stdout);
    let parts: Vec<&str> = size_str.trim().split_whitespace().collect();

    if parts.len() != 2 {
        return None;
    }

    let lines = parts[0].parse::<u16>().ok()?;
    let cols = parts[1].parse::<u16>().ok()?;

    Some((lines, cols))
}
