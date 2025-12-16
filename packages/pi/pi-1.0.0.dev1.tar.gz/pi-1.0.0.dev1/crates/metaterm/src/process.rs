use crate::ProcessHandle;
use crate::error::MetatermError;
use crate::events::OutputEvent;
use crate::pty_pipes::input_jack::{AcceptsInput, FdAcceptsInput, Input};
use crate::pty_pipes::output_pipe::IdleType;
use crate::pty_pipes::{OutputPipe, OutputPipeHandle, PipeMode};
use crate::safe_libc;
use crate::terminal_size::TerminalSize;
use crate::virtual_pty::VirtualPty;
use pishell_eventbus::{DISPATCHER, EventListeners, ListenerHandle};
use std::io::{self, Write};
use std::os::fd::{AsRawFd, RawFd};
use std::process::{Command, ExitStatus};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use tracing::{debug, info};
use typesafe_builder::*;

#[derive(Builder, Debug, Clone)]
pub struct ProcessSetup {
    #[builder(required, into)]
    pub id: String,
    #[builder(required, into)]
    pub command: String,
    #[builder(default)]
    pub args: Vec<String>,
    #[builder(default)]
    pub env: Vec<(String, String)>,
    #[builder(into, default)]
    pub stdin: String,
    #[builder(default = "true")]
    pub echo: bool,
    #[builder(default)]
    pub initial_cursor_position: Option<(u16, u16)>,
}

/// A process running in a PTY
#[derive(Clone)]
pub struct Process {
    setup: ProcessSetup,
    piper_handle: Arc<Option<OutputPipeHandle>>,
    mode: Arc<Mutex<PipeMode>>,
    virtual_pty: Arc<VirtualPty>,
    idle_event: EventListeners<usize>,
    trigger_event: EventListeners<OutputEvent>,
    is_idle: Arc<AtomicUsize>,
    input_jack: Arc<FdAcceptsInput>,
}

impl Process {
    /// Create a new Process
    pub(crate) fn new<W>(
        setup: ProcessSetup,
        size: TerminalSize,
        mode: PipeMode,
        target_stdout: W,
    ) -> io::Result<Self>
    where
        W: Write + Send + AsRawFd + 'static,
    {
        info!(
            "Creating process: {} with command: {} (mode: {:?})",
            setup.id, setup.command, mode
        );

        let mut cmd = Command::new(&setup.command);
        cmd.args(&setup.args);
        for (key, value) in &setup.env {
            cmd.env(key, value);
        }

        // Spawn the process in a PTY
        let (pid, master_fd) = crate::pty::spawn_in_pty(size, cmd, setup.echo)?;
        let pid = ProcessHandle::new(pid);

        if !setup.stdin.is_empty() {
            if let Err(err) = safe_libc::write_all(master_fd, setup.stdin.as_bytes()) {
                return Err(MetatermError::io(format!("Failed to write to stdin"), err));
            }
        }

        // Create the piper
        let piper = OutputPipe::new(pid, master_fd);

        let is_idle = Arc::new(AtomicUsize::new(0));
        let (idle_event_source, idle_event) = DISPATCHER.tear_off();
        let (trigger_event_source, trigger_event) = DISPATCHER.tear_off();

        {
            let is_idle = is_idle.clone();
            idle_event
                .subscribe(move |s: usize| {
                    is_idle.store(s, Ordering::Relaxed);
                })
                .forget();
        }

        let input_jack = Arc::new(FdAcceptsInput::new(master_fd));
        let virtual_pty = Arc::new(VirtualPty::new(size));
        if let Some(cursor_position) = setup.initial_cursor_position {
            virtual_pty.set_cursor_position(
                cursor_position.0.saturating_sub(1),
                cursor_position.1.saturating_sub(1),
            );
        }
        let piper_handle = piper.start_piping(
            mode,
            virtual_pty.clone(),
            target_stdout,
            idle_event_source,
            trigger_event_source,
            input_jack.clone(),
        );

        info!(
            "Created process: {} with command: {} (mode: {:?})",
            setup.id, setup.command, mode
        );

        Ok(Self {
            setup,
            piper_handle: Arc::new(Some(piper_handle)),
            virtual_pty,
            mode: Arc::new(Mutex::new(mode)),
            idle_event,
            trigger_event,
            is_idle,
            input_jack,
        })
    }

    /// Get the process ID
    pub fn id(&self) -> &str {
        &self.setup.id
    }

    /// Get the command
    pub fn command(&self) -> &str {
        &self.setup.command
    }

    /// Check if the process is currently active
    pub fn is_active(&self) -> bool {
        *self.mode.lock().unwrap() == PipeMode::Direct
    }

    /// Get the virtual PTY
    pub fn virtual_pty(&self) -> &Arc<VirtualPty> {
        &self.virtual_pty
    }

    /// Write data to the process's stdin
    pub fn write_stdin(&self, data: &[u8]) -> bool {
        self.input_jack.accept_input(Input::Raw(data))
    }

    /// Get the master file descriptor for this process
    pub fn master_fd(&self) -> Option<RawFd> {
        if let Some(piper_handle) = &*self.piper_handle {
            Some(piper_handle.master_fd())
        } else {
            None
        }
    }

    /// Set the window size for this process
    pub fn set_window_size(&self, size: TerminalSize) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(piper_handle) = &*self.piper_handle {
            piper_handle.set_window_size(size);
        } else {
            return Err("No piper handle available".into());
        }
        Ok(())
    }

    /// Get the current window size
    pub fn get_window_size(&self) -> TerminalSize {
        self.virtual_pty.size()
    }

    /// Check if the process is still running
    pub fn is_running(&self) -> bool {
        if let Some(piper_handle) = &*self.piper_handle {
            piper_handle.is_running()
        } else {
            false
        }
    }

    /// Wait for the process to exit (blocking)
    pub fn wait(&self) -> Result<ExitStatus, Box<dyn std::error::Error>> {
        info!("Waiting for process {} to exit", self.setup.id);

        // Wait for the piper thread to complete
        if let Some(piper_handle) = &*self.piper_handle {
            let res = piper_handle.wait()?;
            info!("Process {} has exited", self.setup.id);
            Ok(res)
        } else {
            // Shouldn't happen
            Err("No piper handle available".into())
        }
    }

    /// Change the pipe mode (Direct or Virtual)
    pub fn change_mode(&self, mode: PipeMode) {
        if let Some(piper_handle) = &*self.piper_handle {
            piper_handle.change_mode_async(mode);
        }
    }

    pub fn on_idle(&self, mut callback: impl FnMut(IdleType) + Send + 'static) -> ListenerHandle {
        callback(self.is_idle.load(Ordering::Relaxed).try_into().unwrap());
        self.idle_event.subscribe(move |s: usize| {
            debug!("Idle event: {}", s);
            callback(s.try_into().unwrap());
        })
    }

    pub fn on_event(
        &self,
        mut callback: impl FnMut(&OutputEvent) + Send + 'static,
    ) -> ListenerHandle {
        self.trigger_event
            .subscribe(move |e: &OutputEvent| callback(e))
    }

    pub fn kill(&self) {
        if let Some(piper_handle) = &*self.piper_handle {
            piper_handle.kill();
        }
    }

    pub fn foreground_pid(&self) -> Option<u32> {
        // Get the master file descriptor for this process
        let master_fd = self.master_fd()?;

        // Use tcgetpgrp to get the foreground process group ID from the terminal
        // This tells us which process group is currently in the foreground
        unsafe {
            let fg_pgrp = libc::tcgetpgrp(master_fd);
            if fg_pgrp > 0 {
                Some(fg_pgrp as u32)
            } else {
                // If tcgetpgrp fails, fall back to the process's own PID
                if let Some(piper_handle) = &*self.piper_handle {
                    Some(piper_handle.pid().pid() as u32)
                } else {
                    None
                }
            }
        }
    }

    pub fn input_jack(&self) -> &Arc<FdAcceptsInput> {
        &self.input_jack
    }
}

impl std::fmt::Debug for Process {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Process")
            .field("id", &self.setup.id)
            .field("command", &self.setup.command)
            .field("is_active", &self.is_active())
            .field("is_running", &self.is_running())
            .finish()
    }
}
