use crate::events::OutputEvent;
use crate::process_handle::ProcessGroupHandle;
use crate::pty_pipes::input_jack::FdAcceptsInput;
use crate::pty_pipes::input_mode::InputMode;
use crate::virtual_pty::VirtualPty;
use crate::{
    ProcessHandle,
    osc133::Osc133Sequence,
    safe_libc::{self, FdSet},
    terminal_size,
};
use pishell_eventbus::EventSource;
use serde::{Deserialize, Serialize};
use std::io::{self, Write};
use std::os::fd::{AsRawFd, RawFd};
use std::process::ExitStatus;
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};
use sync_fd::channel::{MpscFdReceiver, MpscFdSender, TryRecvError, mpsc_fd_pair};
use tracing::{debug, error, info};
use vt_push_parser::VTPushParser;
use vt_push_parser::event::VTEvent;

const IDLE_TIMEOUT: Duration = Duration::from_millis(1000);
const IDLE_TIMEOUT_NEWLINE: Duration = Duration::from_millis(2000);
const IDLE_TIMEOUT_PROMPTISH: Duration = Duration::from_millis(500);
const TEXT_CIRCULAR_BUFFER_SIZE: usize = 4;

const PROMPTISH_CHARACTERS: &[u8] = b"?>#$%:=@!|)]}";

#[derive(Clone, Copy, PartialEq, Eq, Debug, Serialize, Deserialize)]
#[repr(u8)]
pub enum IdleType {
    Active = 0,
    IdleNewline = b'\n',
    IdlePromptish = b'?',
    IdleOther = b' ',
}

impl TryFrom<usize> for IdleType {
    type Error = ();

    fn try_from(value: usize) -> Result<Self, Self::Error> {
        Ok(match value as u8 {
            0 => IdleType::Active,
            b'\n' => IdleType::IdleNewline,
            b'?' => IdleType::IdlePromptish,
            b' ' => IdleType::IdleOther,
            _ => return Err(()),
        })
    }
}

/// Handles idle detection logic for pipe operations
struct IdleDetect {
    /// Current idle state
    idle: bool,
    /// Timestamp of last data received
    last_data: Instant,
    idle_event_source: EventSource<usize>,
    text_circular_buffer: [u8; TEXT_CIRCULAR_BUFFER_SIZE],
}

impl IdleDetect {
    fn new(idle_event_source: EventSource<usize>) -> Self {
        Self {
            idle: false,
            last_data: Instant::now(),
            idle_event_source,
            text_circular_buffer: [b'\n'; TEXT_CIRCULAR_BUFFER_SIZE],
        }
    }

    #[inline(always)]
    fn event(&mut self, idle_event: IdleEvent<'_>) {
        match idle_event {
            IdleEvent::SelectTimedOut => {
                self.do_check_idle_timeout();
            }
            IdleEvent::DataReceived => {
                self.do_data_received();
            }
            IdleEvent::TextReceived { buffer } => {
                self.do_text_received(buffer);
            }
        }
    }

    /// Check if we should transition to idle state and send events if needed
    #[inline(always)]
    fn do_check_idle_timeout(&mut self) {
        if !self.idle {
            let (timeout, idle_type) =
                if self.text_circular_buffer[TEXT_CIRCULAR_BUFFER_SIZE - 1] == b'\n' {
                    (IDLE_TIMEOUT_NEWLINE, IdleType::IdleNewline)
                } else if self
                    .text_circular_buffer
                    .iter()
                    .any(|c| PROMPTISH_CHARACTERS.contains(c))
                {
                    (IDLE_TIMEOUT_PROMPTISH, IdleType::IdlePromptish)
                } else {
                    (IDLE_TIMEOUT, IdleType::IdleOther)
                };

            if self.last_data.elapsed() > timeout {
                debug!("Setting idle");
                self.idle = true;
                self.idle_event_source.send(idle_type as usize);
            }
        }
    }

    #[inline(always)]
    fn do_data_received(&mut self) {}

    /// Reset idle state when new data is received
    #[inline(always)]
    fn do_text_received(&mut self, buffer: &[u8]) {
        // Rotate circular buffer
        if buffer.len() < TEXT_CIRCULAR_BUFFER_SIZE {
            let keep = TEXT_CIRCULAR_BUFFER_SIZE - buffer.len();
            for i in 0..keep {
                self.text_circular_buffer[i] = self.text_circular_buffer[i + buffer.len()];
            }
            self.text_circular_buffer[keep..].copy_from_slice(&buffer);
        } else {
            self.text_circular_buffer
                .copy_from_slice(&buffer[buffer.len() - TEXT_CIRCULAR_BUFFER_SIZE..]);
        }

        if self.idle {
            debug!("Resetting idle");
            self.idle = false;
            self.idle_event_source.send(IdleType::Active as usize);
        }
        self.idle = false;
        self.last_data = Instant::now();
    }

    /// Get current idle state
    fn is_idle(&self) -> bool {
        self.idle
    }
}

enum IdleEvent<'a> {
    SelectTimedOut,
    DataReceived,
    TextReceived { buffer: &'a [u8] },
}

#[derive(Clone, Copy, PartialEq, Eq, Debug, Serialize, Deserialize)]
pub enum PipeMode {
    Direct,
    Logged,
    Virtual,
}

/// Request payloads
#[derive(Debug, Serialize, Deserialize)]
pub enum RpcRequest {
    /// Request to change the pipe mode
    ChangeMode(PipeMode),
    /// Request to send line events
    SendLineEvents(bool),
}

/// A transparent pipe that forwards data between a process and real stdin/stdout
/// while parsing VT100 sequences from the process output
pub struct OutputPipe {
    master_fd: RawFd,
    pid: ProcessHandle,
}

/// Handle for managing the piping threads
pub struct OutputPipeHandle {
    virtual_pty: Arc<VirtualPty>,
    mode_sender: Arc<Mutex<MpscFdSender<RpcRequest>>>,
    join_handles: Arc<Mutex<Vec<JoinHandle<io::Result<()>>>>>,
    master_fd: RawFd,
    pid: ProcessHandle,
    pgid: ProcessGroupHandle,
}

impl OutputPipeHandle {
    /// Get the master file descriptor for this PTY
    pub fn master_fd(&self) -> RawFd {
        self.master_fd
    }

    pub fn pid(&self) -> &ProcessHandle {
        &self.pid
    }

    pub fn set_window_size(&self, size: terminal_size::TerminalSize) {
        self.virtual_pty.resize(size);
        let winsize = size.winsize();
        unsafe {
            libc::ioctl(self.master_fd, libc::TIOCSWINSZ, &winsize);
        }
    }

    /// Change mode asynchronously (safe to call from callbacks)
    pub fn change_mode_async(&self, new_mode: PipeMode) {
        // Send the request asynchronously without waiting for response
        let message = RpcRequest::ChangeMode(new_mode);

        if let Ok(mut sender) = self.mode_sender.lock() {
            if let Err(e) = sender.blocking_send(message) {
                error!("Failed to send async mode change: {:?}", e);
            }
        }
    }

    /// Wait for all piping threads to complete
    pub fn wait(&self) -> Result<ExitStatus, Box<dyn std::error::Error>> {
        info!("Waiting for PtyPiperHandle threads to complete");

        if let Ok(mut join_handles) = self.join_handles.lock() {
            for handle in join_handles.drain(..) {
                match handle.join() {
                    Ok(result) => {
                        if let Err(e) = result {
                            error!("Thread completed with error: {}", e);
                        }
                    }
                    Err(e) => {
                        if let Some(e) = e.downcast_ref::<String>() {
                            error!("Failed to join thread: {}", e);
                        } else {
                            error!("Failed to join thread: {:?}", e);
                        }
                    }
                }
            }
        }

        info!("All PtyPiperHandle threads completed");

        Ok(self.pid.wait()?)
    }

    /// Check if the piping threads are still running
    pub fn is_running(&self) -> bool {
        // First check if the process itself is still running
        if !self.pid.is_running() {
            return false;
        }

        // Then check if any threads are still active
        if let Ok(join_handles) = self.join_handles.lock() {
            for handle in join_handles.iter() {
                if !handle.is_finished() {
                    return true;
                }
            }
            // All threads have finished
            false
        } else {
            // If we can't lock, assume it's still running
            true
        }
    }

    pub fn kill(&self) {
        _ = self.pgid.force_kill();
    }
}

struct PipeState {
    buffer: [u8; 4096],
    idle_detect: IdleDetect,
    mode: PipeMode,
    send_line_events: bool,
    vt_parser_output: VTPushParser,
    input_mode: InputMode,
    first_byte: bool,
}

struct PipeEvents {
    idle: EventSource<usize>,
    trigger: EventSource<OutputEvent>,
}

/// Perform one iteration of data flow using file descriptors
fn pipe_directional_once(
    master_fd: RawFd,
    stdout_fd: RawFd,
    mode_receiver: &mut MpscFdReceiver<RpcRequest>,
    virtual_pty: &VirtualPty,
    pipe_state: &mut PipeState,
    pipe_events: &PipeEvents,
) -> Result<(), ()> {
    // Set up file descriptor sets for select
    let mut read_fds = FdSet::new();
    let mode_read_fd = mode_receiver.as_raw_fd();
    read_fds.set(master_fd);
    read_fds.set(mode_read_fd);

    // Wait for data on process stdout. If we aren't idle, we want a shorter
    // timeout so we can detect idle faster.
    let timeout_duration = if pipe_state.idle_detect.is_idle() {
        1000
    } else {
        100
    };
    let result = match safe_libc::select(
        Some(&mut read_fds),
        None,
        None,
        Some(Duration::from_millis(timeout_duration)),
    ) {
        Ok(count) => count,
        Err(err) => {
            error!("Select error: {}", err);
            return Err(());
        }
    };

    if result == 0 {
        pipe_state.idle_detect.event(IdleEvent::SelectTimedOut);
        return Ok(());
    }

    pipe_state.idle_detect.event(IdleEvent::DataReceived);

    if read_fds.is_set(mode_read_fd) {
        // Use the MpscFdReceiver to receive the message
        match mode_receiver.try_recv() {
            Ok(RpcRequest::ChangeMode(new_mode)) => {
                pipe_state.mode = new_mode;
            }
            Ok(RpcRequest::SendLineEvents(send_line_events)) => {
                pipe_state.send_line_events = send_line_events;
            }
            Err(TryRecvError::Empty) => {
                // No message available, continue
            }
            Err(TryRecvError::Disconnected) => {
                debug!("Mode receiver disconnected");
                return Err(());
            }
        }
    }

    // Check if process stdout has data (process -> target stdout)
    if read_fds.is_set(master_fd) {
        let n = match safe_libc::read_slice(master_fd, &mut pipe_state.buffer) {
            Ok(0) => {
                debug!("Process stdout EOF");
                return Err(());
            }
            Ok(n) => n,
            Err(err) => {
                error!("Error reading from process stdout: {}", err);
                return Err(());
            }
        };

        if pipe_state.first_byte {
            pipe_events.trigger.send(OutputEvent::FirstByte);
            pipe_state.first_byte = false;
        }

        debug!("Received {} bytes from process stdout", n);
        debug!(
            "Buffer: {:?}",
            String::from_utf8_lossy(&pipe_state.buffer[..n])
        );

        let buffer = &pipe_state.buffer[..n];

        if pipe_state.send_line_events && buffer.contains(&b'\n') {
            pipe_events.trigger.send(OutputEvent::Line);
        }

        // Process through VT100 parser
        pipe_state
            .vt_parser_output
            .feed_with(&pipe_state.buffer[..n], &mut |event: VTEvent| {
                if let VTEvent::Raw(data) = event {
                    pipe_state
                        .idle_detect
                        .event(IdleEvent::TextReceived { buffer: data });
                    if pipe_state.mode == PipeMode::Logged {
                        // Write to log
                        match safe_libc::write_all(stdout_fd, data) {
                            Ok(_client) => {}
                            Err(err) => {
                                error!("Failed to write to real stdout: {}", err);
                            }
                        }
                    }
                }

                // Check for OSC 133 sequences
                if let Some(osc133_sequence) = Osc133Sequence::from_vt_event(&event) {
                    debug!("Detected OSC 133 sequence: {}", osc133_sequence);
                    pipe_events
                        .trigger
                        .send(OutputEvent::Prompt(osc133_sequence));
                }

                if matches!(event, VTEvent::Csi { .. }) {
                    debug!("CSI event: {:?}", event);
                }

                if pipe_state.input_mode.is_mode_event(&event) {
                    pipe_state.input_mode.process_vt_event(&event);
                }

                // Also check for other potential interesting characters
                if matches!(event, VTEvent::C0(0x07)) {
                    // Bell character
                    info!("Bell triggered from output");
                    pipe_events.trigger.send(OutputEvent::Bell);
                }

                // Handle various cursor position queries and other queries
                if matches!(
                    event,
                    VTEvent::Csi {
                        private: None,
                        final_byte: b'R',
                        ..
                    }
                ) {
                    // Cursor Position Report (CPR) response
                    debug!("Cursor Position Report received");
                }

                if matches!(
                    event,
                    VTEvent::Csi {
                        private: Some(b'?'),
                        final_byte: b'c',
                        ..
                    }
                ) {
                    // Device Attributes query response
                    debug!("Device Attributes response received");
                }

                if matches!(
                    event,
                    VTEvent::Csi {
                        private: Some(b'?'),
                        final_byte: b'n',
                        ..
                    }
                ) {
                    // Device Status Report query response
                    debug!("Device Status Report response received");
                }

                if matches!(
                    event,
                    VTEvent::Csi {
                        private: Some(b'>'),
                        final_byte: b'c',
                        ..
                    }
                ) {
                    // Secondary Device Attributes query response
                    debug!("Secondary Device Attributes response received");
                }
            });

        virtual_pty.feed(&pipe_state.buffer[..n]);

        if pipe_state.mode == PipeMode::Direct {
            // Write to real stdout
            match safe_libc::write_slice(stdout_fd, &pipe_state.buffer[..n]) {
                Ok(bytes_written) => {
                    if bytes_written != n {
                        error!(
                            "Incomplete write to real stdout: {} of {} bytes",
                            bytes_written, n
                        );
                        return Err(());
                    }
                }
                Err(err) => {
                    error!("Failed to write to real stdout: {}", err);
                    return Err(());
                }
            }
        }
    }

    Ok(())
}

fn pipe_directional<W>(
    pipe_state: &mut PipeState,
    master_fd: RawFd,
    target_stdout: W,
    mut mode_receiver: MpscFdReceiver<RpcRequest>,
    virtual_pty: &VirtualPty,
    pipe_events: &PipeEvents,
) -> io::Result<()>
where
    W: Write + Send + AsRawFd + 'static,
{
    let stdout_fd = target_stdout.as_raw_fd();

    while pipe_directional_once(
        master_fd,
        stdout_fd,
        &mut mode_receiver,
        virtual_pty,
        pipe_state,
        pipe_events,
    )
    .is_ok()
    {}

    info!("Bidirectional piping completed");
    Ok(())
}

impl OutputPipe {
    /// Create a new PtyPiper instance
    pub fn new(pid: ProcessHandle, master_fd: RawFd) -> Self {
        unsafe {
            let flags = libc::fcntl(master_fd, libc::F_GETFL);
            if flags == -1 {
                panic!("Failed to get file flags");
            }
            if libc::fcntl(master_fd, libc::F_SETFL, flags | libc::O_NONBLOCK) == -1 {
                panic!("Failed to set nonblocking");
            }
        }

        Self { master_fd, pid }
    }

    /// Start the transparent piping between the given process and stdout
    ///
    /// # Arguments
    /// * `target_stdout` - Write interface to the target stdout
    pub fn start_piping<W>(
        self,
        initial_mode: PipeMode,
        virtual_pty: Arc<VirtualPty>,
        target_stdout: W,
        idle_event_source: EventSource<usize>,
        trigger_event_source: EventSource<OutputEvent>,
        input_jack: Arc<FdAcceptsInput>,
    ) -> OutputPipeHandle
    where
        W: Write + Send + AsRawFd + 'static,
    {
        info!("Starting transparent piping");

        let master_fd = self.master_fd;
        let mut join_handles = Vec::new();

        // Create MpscFd pair for control messages
        let (mode_sender, mode_receiver) = mpsc_fd_pair::<RpcRequest>().unwrap();

        // Spawn single thread for bidirectional piping
        let piping_thread = {
            let master_fd = master_fd;
            let virtual_pty = virtual_pty.clone();
            thread::spawn(move || {
                let mut pipe_state = PipeState {
                    buffer: [0; 4096],
                    idle_detect: IdleDetect::new(idle_event_source.clone()),
                    mode: initial_mode,
                    send_line_events: false,
                    vt_parser_output: VTPushParser::new(),
                    input_mode: input_jack.input_mode().clone(),
                    first_byte: true,
                };

                let pipe_events = PipeEvents {
                    idle: idle_event_source,
                    trigger: trigger_event_source,
                };

                pipe_directional(
                    &mut pipe_state,
                    master_fd,
                    target_stdout,
                    mode_receiver,
                    &virtual_pty,
                    &pipe_events,
                )
            })
        };

        join_handles.push(piping_thread);
        let pgid = ProcessGroupHandle::new(self.pid.pid());

        OutputPipeHandle {
            virtual_pty,
            join_handles: Arc::new(Mutex::new(join_handles)),
            mode_sender: Arc::new(Mutex::new(mode_sender)),
            master_fd,
            pid: self.pid,
            pgid,
        }
    }
}

impl Drop for OutputPipeHandle {
    fn drop(&mut self) {
        info!("Dropping PtyPiperHandle, waiting for threads to complete");

        // Wait for all threads to complete
        // if let Ok(mut join_handles) = self.join_handles.lock() {
        //     for handle in join_handles.drain(..) {
        //         match handle.join() {
        //             Ok(result) => {
        //                 if let Err(e) = result {
        //                     error!("Thread completed with error: {}", e);
        //                 }
        //             }
        //             Err(e) => {
        //                 error!("Failed to join thread: {:?}", e);
        //             }
        //         }
        //     }
        // }

        info!("All threads completed");
    }
}
