use std::io::{self, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

use crossterm::event::{
    DisableMouseCapture, EnableMouseCapture, KeyCode, KeyboardEnhancementFlags,
    PopKeyboardEnhancementFlags, PushKeyboardEnhancementFlags,
};
use crossterm::execute;
use pishell_metaterm::{Input, InputPipe, TerminalGuard, XTERM_NORMALIZE};

pub fn main() {
    let input_pipe = InputPipe::new();
    eprintln!("Key test: hit Ctrl+G twice to exit");
    eprintln!("Press 1 to set kitty key mode");
    eprintln!("Press 2 to set normal key mode");
    eprintln!("Press 3 to enable mouse");
    eprintln!("Press 4 to disable mouse");

    let _raw_terminal = TerminalGuard::new();
    std::io::stdout().write_all(XTERM_NORMALIZE).unwrap();
    std::io::stdout().flush().unwrap();

    let quit = Arc::new(AtomicUsize::new(0));
    let pending_key = Arc::new(Mutex::new(None));

    let quit_clone = quit.clone();
    let pending_key_clone = pending_key.clone();
    input_pipe
        .input_jack
        .attach(Arc::new(move |input: Input<'_>| {
            match input {
                Input::BracketedPaste(paste) => {
                    eprintln!("BracketedPaste: {:?}\r", paste);
                }
                Input::Raw(data) => {
                    eprintln!("Raw: {:?}\r", data);
                }
                Input::TerminalEvent(vtinput::TerminalInputEvent::Key(key)) => {
                    if key.code == vtinput::KeyCode::Char('g')
                        && key.modifiers.contains(vtinput::KeyModifiers::CONTROL)
                    {
                        quit_clone.fetch_add(1, Ordering::Relaxed);
                    } else if matches!(key.code, vtinput::KeyCode::Char('1' | '2' | '3' | '4')) {
                        let code = match key.code {
                            vtinput::KeyCode::Char(c) => KeyCode::Char(c),
                            _ => unreachable!(),
                        };
                        pending_key_clone.lock().unwrap().replace(code);
                    }
                    eprintln!("Key: {:?}\r", key);
                }
                Input::TerminalEvent(vtinput::TerminalInputEvent::Focus(gained)) => {
                    if gained {
                        eprintln!("FocusGained\r");
                    } else {
                        eprintln!("FocusLost\r");
                    }
                }
                Input::TerminalEvent(vtinput::TerminalInputEvent::Mouse(mouse)) => {
                    eprintln!("Mouse: {:?}\r", mouse);
                }
                Input::TerminalEvent(vtinput::TerminalInputEvent::Paste(paste)) => {
                    eprintln!("Paste: {:?}\r", paste);
                }
                Input::TerminalEvent(vtinput::TerminalInputEvent::Resize(cols, rows)) => {
                    eprintln!("Resize: {:?}\r", (cols, rows));
                }
                Input::TerminalEvent(event) => {
                    eprintln!("TerminalEvent: {:?}\r", event);
                }
                Input::Size(size) => {
                    eprintln!("Size: {:?}\r", size);
                }
            }
            true
        }));

    input_pipe.start_stdin_thread();

    while quit.load(Ordering::Relaxed) < 2 {
        std::thread::sleep(std::time::Duration::from_millis(100));
        if let Some(key) = pending_key.lock().unwrap().take() {
            match key {
                KeyCode::Char('1') => {
                    eprintln!("Setting kitty key mode\r");
                    execute!(
                        io::stdout(),
                        PushKeyboardEnhancementFlags(
                            KeyboardEnhancementFlags::DISAMBIGUATE_ESCAPE_CODES
                                | KeyboardEnhancementFlags::REPORT_ALTERNATE_KEYS
                        )
                    )
                    .unwrap();
                }
                KeyCode::Char('2') => {
                    eprintln!("Setting normal key mode\r");
                    execute!(io::stdout(), PopKeyboardEnhancementFlags).unwrap();
                }
                KeyCode::Char('3') => {
                    eprintln!("Enable mouse\r");
                    execute!(io::stdout(), EnableMouseCapture).unwrap();
                }
                KeyCode::Char('4') => {
                    eprintln!("Disable mouse\r");
                    execute!(io::stdout(), DisableMouseCapture).unwrap();
                }
                _ => {}
            }
        }
    }
}
