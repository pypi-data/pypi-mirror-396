use std::sync::{
    Arc,
    atomic::{AtomicBool, Ordering},
};

use crossterm::{
    cursor::{Hide, MoveTo, Show},
    event::{
        DisableMouseCapture, EnableMouseCapture, KeyboardEnhancementFlags,
        PopKeyboardEnhancementFlags, PushKeyboardEnhancementFlags,
    },
    execute,
    style::ResetColor,
    terminal::{
        BeginSynchronizedUpdate, Clear, ClearType, DisableLineWrap, EnableLineWrap,
        EndSynchronizedUpdate, EnterAlternateScreen, LeaveAlternateScreen,
    },
};
use pishell_eventbus::EventListeners;
use pishell_metaterm::{OffsetMouseInputJack, TerminalSize};
use pishell_metaterm::{Process, Terminal, TriggeredInputJack};
use std::io::{self, Write};
use tracing::info;

// Sidebar is now full screen with background character overlay
const SIDEBAR_OUT_FRAME_COUNT: usize = 5;

pub fn run_ui(
    terminal: Terminal,
    shell: Arc<Process>,
    sidebar: Arc<Process>,
    close_event: EventListeners<()>,
) {
    info!("run_ui: Starting UI...");

    // Set up the terminal for raw crossterm
    let mut stdout = io::stdout();
    info!("run_ui: Entering alternate screen...");
    if !shell.virtual_pty().is_alternate_screen() {
        execute!(stdout, EnterAlternateScreen).expect("Failed to enter alternate screen");
        execute!(stdout, Clear(ClearType::All)).expect("Failed to clear screen");
    }
    execute!(stdout, Hide).expect("Failed to hide cursor");

    execute!(io::stdout(), EnableMouseCapture).expect("Failed to enable mouse capture");
    execute!(
        io::stdout(),
        PushKeyboardEnhancementFlags(
            KeyboardEnhancementFlags::DISAMBIGUATE_ESCAPE_CODES
                | KeyboardEnhancementFlags::REPORT_EVENT_TYPES
                | KeyboardEnhancementFlags::REPORT_ALTERNATE_KEYS
        )
    )
    .expect("Failed to push keyboard enhancement flags");

    let finished = Arc::new(AtomicBool::new(false));

    let trigger = Arc::new(TriggeredInputJack::new());
    trigger.attach(sidebar.input_jack().clone());
    let offset_mouse_jack = Arc::new(OffsetMouseInputJack::new(0, 0));
    offset_mouse_jack.attach(trigger.clone());

    let finished_clone = finished.clone();
    let _close_event = close_event.subscribe(move |_| {
        info!("run_ui: Close event received");
        finished_clone.store(true, Ordering::Relaxed);
    });
    terminal
        .input_pipe()
        .input_jack
        .attach(offset_mouse_jack.clone());

    info!("run_ui: Terminal setup complete");

    // Get virtual PTY references
    let shell_vpty = shell.virtual_pty().clone();
    let sidebar_vpty = sidebar.virtual_pty().clone();

    // Main event loop
    info!("run_ui: Starting main event loop...");

    let (mut term_width, mut term_height) =
        crossterm::terminal::size().expect("Failed to get terminal size");
    let mut ui = vt100::Parser::new(term_height, term_width, 0);
    // Hide cursor
    ui.process("\x1b[?25l".as_bytes());
    let mut old_screen = ui.screen().clone();

    let mut last_size = (0, 0);

    let mut finished_count = SIDEBAR_OUT_FRAME_COUNT;

    // Track change counts for both processes to avoid unnecessary rendering
    let mut last_shell_change_count = shell_vpty.get_change_count();
    let mut last_sidebar_change_count = sidebar_vpty.get_change_count();

    while finished_count > 0 {
        if finished.load(Ordering::Relaxed) {
            finished_count = finished_count.saturating_sub(1);
            if finished_count == 0 {
                break;
            }
        }

        // Get terminal size each time we loop
        let size = crossterm::terminal::size().expect("Failed to get terminal size");
        let resized = size != last_size;

        if resized {
            (term_width, term_height) = size;
            ui.screen_mut().set_size(term_height, term_width);
            // Reset screen
            ui.process(b"\x1b[2J");
            last_size = size;
        }

        // Mouse events should go to sidebar (which overlays the shell)
        offset_mouse_jack.set_offset(0, 0);

        // Check if either process has new data before rendering
        let current_shell_change_count = shell_vpty.get_change_count();
        let current_sidebar_change_count = sidebar_vpty.get_change_count();
        let shell_changed = current_shell_change_count != last_shell_change_count;
        let sidebar_changed = current_sidebar_change_count != last_sidebar_change_count;
        let has_changes = shell_changed || sidebar_changed || resized || !sidebar.is_running();

        // Note that we might be able to avoid rendering either left or right
        // side if only one has changed but we'll have to take into account
        // sidebar sizing for that to be proper. For now, re-render both sides.
        if has_changes {
            // Update change counts
            last_shell_change_count = current_shell_change_count;
            last_sidebar_change_count = current_sidebar_change_count;

            if !sidebar.is_running() {
                // Render a message that the sidebar crashed at (0, 0)
                sidebar_vpty.feed(b"\x1b[0;0H\x1b[31mSIDEBAR CRASHED\x1b[0m\n");
            }

            // Render sidebar with shell overlay - sidebar is now full screen
            // When sidebar cells contain `TRANSPARENT_CHAR`, the shell content shows through
            sidebar_vpty.copy_screen(
                false,
                0,
                0,
                Some(term_height - 1),
                Some(term_width - 1),
                &mut ui,
                0,
                0,
                Some(&shell_vpty),
            );

            // Move cursor to top left and reset attributes
            ui.process(b"\x1b[H\x1b[0m");
        }

        if resized {
            // Both shell and sidebar get full screen size
            let _ = shell.set_window_size(TerminalSize::new(term_height, term_width));
            let _ = sidebar.set_window_size(TerminalSize::new(term_height, term_width));
        }

        // Only render if there are changes
        if has_changes {
            // Begin synchronized update
            execute!(stdout, BeginSynchronizedUpdate).expect("Failed to begin synchronized update");

            if resized {
                // If resized, clear the screen, reset the color and render the screen
                execute!(stdout, Clear(ClearType::All)).expect("Failed to clear screen");

                // Render shell fullscreen
                execute!(stdout, DisableLineWrap).expect("Failed to disable line wrap");
                for (row, line) in ui.screen().rows_formatted(0, term_width).enumerate() {
                    execute!(stdout, MoveTo(0, row as u16))
                        .expect("Failed to print final shell line");
                    execute!(stdout, ResetColor).expect("Failed to move cursor");
                    stdout.write_all(&line).expect("Failed to write line");
                }
            } else {
                // Otherwise, render the diff only
                let diff = ui.screen().contents_diff(&old_screen);
                stdout.write_all(&diff).expect("Failed to write diff");
                stdout.flush().expect("Failed to flush stdout");
            }
            execute!(stdout, ResetColor).expect("Failed to reset");
            execute!(stdout, MoveTo(0, 0)).expect("Failed to print final shell line");
            execute!(stdout, EnableLineWrap).expect("Failed to enable line wrap");
            old_screen = ui.screen().clone();

            // End synchronized update
            execute!(stdout, EndSynchronizedUpdate).expect("Failed to end synchronized update");
        }

        std::thread::sleep(std::time::Duration::from_millis(10));
    }

    // Restore input mode via crossterm, then ask the virtual pty to restore its input mode
    execute!(io::stdout(), DisableMouseCapture).expect("Failed to disable mouse capture");
    io::stdout()
        .write_all(shell.virtual_pty().get_input_mode_formatted().as_slice())
        .expect("Failed to write input mode formatted");
    execute!(io::stdout(), PopKeyboardEnhancementFlags)
        .expect("Failed to push keyboard enhancement flags");

    // Clean up the terminal
    info!("run_ui: Cleaning up terminal...");
    if !shell.virtual_pty().is_alternate_screen() {
        execute!(stdout, LeaveAlternateScreen).expect("Failed to leave alternate screen");
    } else {
        // Begin synchronized update for final render
        execute!(stdout, BeginSynchronizedUpdate).expect("Failed to begin synchronized update");

        // Clear screen and move cursor to top-left
        execute!(
            stdout,
            crossterm::terminal::Clear(crossterm::terminal::ClearType::All)
        )
        .expect("Failed to clear screen");

        // Render shell fullscreen
        let shell_ansi = shell.virtual_pty().get_ansi_screen(false, None, None);
        execute!(stdout, DisableLineWrap).expect("Failed to disable line wrap");
        for (row, line) in shell_ansi.iter().enumerate() {
            execute!(stdout, MoveTo(0, row as u16)).expect("Failed to print final shell line");
            execute!(stdout, ResetColor).expect("Failed to move cursor");
            stdout
                .write_all(line.as_bytes())
                .expect("Failed to write line");
        }
        execute!(stdout, EnableLineWrap).expect("Failed to enable line wrap");
        execute!(stdout, ResetColor).expect("Failed to reset color");
        let cursor_position = shell.virtual_pty().cursor_position();
        execute!(stdout, MoveTo(cursor_position.1, cursor_position.0))
            .expect("Failed to print final shell line");

        // End synchronized update
        execute!(stdout, EndSynchronizedUpdate).expect("Failed to end synchronized update");
    }

    terminal.input_pipe().input_jack.attach(Arc::new(()));

    // Show cursor before exiting
    execute!(stdout, Show).expect("Failed to show cursor");

    let terminal_size = crossterm::terminal::size().expect("Failed to get terminal size");
    let _ = shell.set_window_size(TerminalSize::new(terminal_size.1, terminal_size.0));

    info!("run_ui: UI finished");
}
