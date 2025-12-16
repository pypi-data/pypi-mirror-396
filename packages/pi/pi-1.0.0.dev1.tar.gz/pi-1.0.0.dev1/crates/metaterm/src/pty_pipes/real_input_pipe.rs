use std::io;
use std::os::fd::AsRawFd;
use std::sync::{Arc, Barrier, Mutex};
use std::thread::{self, JoinHandle};

use tracing::{debug, error, info};

use crate::pty_pipes::input_jack::{AtomicAcceptHandle, Input};
use crate::safe_libc;

/// Heuristic: If we idle for too long, reset the parser to avoid parsing
/// failures. This technically could trigger a partial decode, but it avoids
/// us getting wedged.
const IDLE_COUNT_RESET_THRESHOLD: usize = 10;

/// Processes raw bytes from stdin (or some other byte stream) and forwards them to the input jack.
pub struct ByteInputSource {
    input_jack: Arc<AtomicAcceptHandle>,
    input_parser: vtinput::TerminalInputParser,
    idle_count: usize,
}

impl ByteInputSource {
    pub fn new(input_jack: Arc<AtomicAcceptHandle>) -> Self {
        Self {
            input_jack,
            input_parser: vtinput::TerminalInputParser::new(),
            idle_count: 0,
        }
    }

    #[allow(dead_code)]
    pub fn reset(&mut self) {
        self.input_parser = vtinput::TerminalInputParser::new();
    }

    /// Reset the parser state but keep the bracketed paste state
    fn reset_parser(&mut self) {
        self.input_parser = vtinput::TerminalInputParser::new();
    }

    pub fn idle(&mut self) {
        if self.idle_count == 0 {
            debug!("Idle");
        }
        let _events_sent = self.input_parser.idle(&mut |event| {
            self.input_jack.accept_input(Input::TerminalEvent(event));
        });

        self.idle_count += 1;

        // Only reset after IDLE_COUNT_RESET_THRESHOLD consecutive idles
        if self.idle_count >= IDLE_COUNT_RESET_THRESHOLD {
            self.reset_parser();
            self.idle_count = 0;
        }
    }

    pub fn process(&mut self, data: &[u8]) {
        self.input_parser.feed_with(data, &mut |event| {
            self.idle_count = 0;
            self.input_jack.accept_input(Input::TerminalEvent(event));
        });
    }
}

#[derive(Clone)]
pub struct InputPipe {
    pub input_jack: Arc<AtomicAcceptHandle>,
    pub stdin_thread: Arc<Mutex<Option<JoinHandle<()>>>>,
}

impl Default for InputPipe {
    fn default() -> Self {
        Self::new()
    }
}

impl InputPipe {
    pub fn new() -> Self {
        Self {
            input_jack: Arc::new(AtomicAcceptHandle::new()),
            stdin_thread: Arc::new(Mutex::new(None)),
        }
    }

    /// Start the stdin forwarding thread
    pub fn start_stdin_thread(&self) {
        let input_jack = self.input_jack.clone();

        let running = self.stdin_thread.clone();
        let barrier = Arc::new(Barrier::new(2));
        let barrier_clone = barrier.clone();
        let mut byte_input_source = ByteInputSource::new(input_jack);

        let handle = thread::spawn(move || {
            let stdin_fd = io::stdin().as_raw_fd();
            let mut buffer = [0u8; 1024];

            // Ensure the started thread is stored and we're ready to process
            barrier_clone.wait();

            loop {
                if running.lock().unwrap().is_none() {
                    info!("Stdin thread is not running, exiting");
                    break;
                }

                let timeout = std::time::Duration::from_millis(100);

                // Use high-level select API
                match safe_libc::wait_for_read(stdin_fd, Some(timeout)) {
                    Ok(true) => {} // File descriptor is ready
                    Ok(false) => {
                        byte_input_source.idle();
                        continue; // Timeout occurred
                    }
                    Err(err) => {
                        error!("Select error: {}", err);
                        break;
                    }
                }

                // Use high-level safe libc read from stdin
                let n = match safe_libc::read_slice(stdin_fd, &mut buffer) {
                    Ok(0) => {
                        // EOF
                        info!("Stdin EOF, exiting stdin thread");
                        break;
                    }
                    Ok(n) => n,
                    Err(err) => {
                        error!("Error reading from stdin: {}", err);
                        break;
                    }
                };
                let data = &buffer[..n];
                info!("Read {} bytes from stdin: {:?}", n, data);

                byte_input_source.process(data);
            }
        });

        // Store the thread handle
        if let Ok(mut thread_guard) = self.stdin_thread.lock() {
            *thread_guard = Some(handle);
            barrier.wait();
        }
    }
}

#[cfg(test)]
mod tests {
    use vtinput::TerminalInputEventOwned;

    use crate::pty_pipes::input_jack::InputOwned;

    use super::*;

    fn create_byte_input_source_with_data(
        data: &[u8],
    ) -> (ByteInputSource, Arc<Mutex<Vec<InputOwned>>>) {
        let received_inputs = Arc::new(Mutex::new(Vec::<InputOwned>::new()));
        let mut byte_input_source =
            ByteInputSource::new(AtomicAcceptHandle::from(received_inputs.clone()).into());
        for (i, chunk) in data.split(|c| *c == 0).enumerate() {
            if i > 0 {
                byte_input_source.idle();
            }
            byte_input_source.process(chunk);
        }
        byte_input_source.idle();
        byte_input_source.reset();
        (byte_input_source, received_inputs)
    }

    #[test]
    fn test_byte_input_source_sequences_broken() {
        use vtinput::VTOwnedEvent;

        // xterm.js sends busted OSC. We require a long idle sequence to
        // trigger a reset. Test case 1: Single idle (1 null byte) - OSC
        // should remain open and subsequent input becomes OSC data.
        let (_, received_inputs) = create_byte_input_source_with_data(
            b"\x1b[3;1R\x1b[>1;10;0c\x1b]10;rgb:ffff/ffff/ffff\x1b]11;rgb:2828/2c2c/3434\0\x1b[3;1R",
        );
        let received = std::mem::take(&mut *received_inputs.lock().unwrap());
        assert_eq!(received.len(), 5);

        assert!(matches!(
            &received[0],
            InputOwned::TerminalEvent(TerminalInputEventOwned::CursorPosition(0, 2))
        ));

        assert!(matches!(
            &received[1],
            InputOwned::TerminalEvent(TerminalInputEventOwned::LowLevel(
                vt_event
            )) if matches!(**vt_event, VTOwnedEvent::Csi(ref csi) if csi.private == Some(b'>') && csi.final_byte == b'c')
        ));

        assert!(matches!(
            &received[2],
            InputOwned::TerminalEvent(TerminalInputEventOwned::LowLevel(
                vt_event
            )) if matches!(**vt_event, VTOwnedEvent::OscStart)
        ));

        assert!(matches!(
            &received[3],
            InputOwned::TerminalEvent(TerminalInputEventOwned::LowLevel(
                vt_event
            )) if matches!(**vt_event, VTOwnedEvent::OscData(ref data) if data == b"10;rgb:ffff/ffff/ffff\x1b]11;rgb:2828/2c2c/3434")
        ));

        assert!(matches!(
            &received[4],
            InputOwned::TerminalEvent(TerminalInputEventOwned::LowLevel(
                vt_event
            )) if matches!(**vt_event, VTOwnedEvent::OscData(ref data) if data == b"\x1b[3;1R")
        ));

        // Test case 2: Many idles (11 null bytes) - OSC should be terminated
        // after exceeding threshold, and subsequent input is parsed normally.
        let (_, received_inputs) = create_byte_input_source_with_data(
            b"\x1b[3;1R\x1b[>1;10;0c\x1b]10;rgb:ffff/ffff/ffff\x1b]11;rgb:2828/2c2c/3434\0\0\0\0\0\0\0\0\0\0\0\x1b[3;1R",
        );
        let received = std::mem::take(&mut *received_inputs.lock().unwrap());
        assert_eq!(received.len(), 5);

        assert!(matches!(
            &received[0],
            InputOwned::TerminalEvent(TerminalInputEventOwned::CursorPosition(0, 2))
        ));

        assert!(matches!(
            &received[1],
            InputOwned::TerminalEvent(TerminalInputEventOwned::LowLevel(
                vt_event
            )) if matches!(**vt_event, VTOwnedEvent::Csi(ref csi) if csi.private == Some(b'>') && csi.final_byte == b'c')
        ));

        assert!(matches!(
            &received[2],
            InputOwned::TerminalEvent(TerminalInputEventOwned::LowLevel(
                vt_event
            )) if matches!(**vt_event, VTOwnedEvent::OscStart)
        ));

        assert!(matches!(
            &received[3],
            InputOwned::TerminalEvent(TerminalInputEventOwned::LowLevel(
                vt_event
            )) if matches!(**vt_event, VTOwnedEvent::OscData(ref data) if data == b"10;rgb:ffff/ffff/ffff\x1b]11;rgb:2828/2c2c/3434")
        ));

        assert!(matches!(
            &received[4],
            InputOwned::TerminalEvent(TerminalInputEventOwned::CursorPosition(0, 2))
        ));
    }
}
