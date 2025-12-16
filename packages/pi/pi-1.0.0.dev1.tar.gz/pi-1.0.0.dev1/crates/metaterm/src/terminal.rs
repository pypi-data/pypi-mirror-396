use crate::error::MetatermError;
use crate::process::{Process, ProcessSetup};
use crate::pty_pipes::input_jack::TriggeredInputJack;
use crate::pty_pipes::{InputPipe, PipeMode};
use crate::terminal_size::TerminalSize;
use pishell_eventbus::ListenerHandle;
use std::collections::HashMap;
use std::io::{self, Write};
use std::os::fd::AsRawFd;
use std::sync::{Arc, Mutex};
use tracing::{error, info};

/// A terminal that manages multiple subprocesses
#[derive(Clone)]
pub struct Terminal {
    processes: Arc<Mutex<HashMap<String, Process>>>,
    trigger_event: Arc<TriggeredInputJack>,
    environment_variables: Arc<Mutex<HashMap<String, String>>>,
    active_process_id: Arc<Mutex<Option<String>>>,
    input_pipe: InputPipe,
}

impl Terminal {
    /// Create a new Terminal instance
    pub fn new() -> Self {
        let input_pipe = InputPipe::new();
        let trigger_event = Arc::new(TriggeredInputJack::new());

        let terminal = Self {
            processes: Arc::new(Mutex::new(HashMap::new())),
            trigger_event,
            environment_variables: Arc::new(Mutex::new(HashMap::new())),
            active_process_id: Arc::new(Mutex::new(None)),
            input_pipe,
        };

        // Start the stdin forwarding thread
        terminal.input_pipe.start_stdin_thread();

        terminal
    }

    pub fn set_active_process(&self, process: &Process) {
        info!("Setting active process to: {}", process.id());
        self.attach_input(process);

        let mut active_id = self.active_process_id.lock().unwrap();
        *active_id = Some(process.id().to_string());

        process.change_mode(PipeMode::Direct);

        info!("Active process set to: {}", process.id());
    }

    /// Create a new process that will be the active one (using real terminal size)
    pub fn create_active_process(
        &self,
        setup: ProcessSetup,
        size: TerminalSize,
    ) -> io::Result<Process> {
        let mut active_lock = self.active_process_id.lock().unwrap();

        if active_lock.is_some() {
            return Err(io::Error::new(
                io::ErrorKind::AlreadyExists,
                "Only one active process is allowed",
            ));
        }

        let process =
            self.create_process_inner(setup, size, PipeMode::Direct, std::io::stdout())?;
        *active_lock = Some(process.id().to_owned());

        // Update active stdin fd
        self.trigger_event.attach(process.input_jack().clone());
        self.input_pipe
            .input_jack
            .attach(self.trigger_event.clone());
        info!("Updated active stdin fd to: {:?}", process.input_jack());

        Ok(process)
    }

    /// Create a new process with virtual size (not active)
    pub fn create_process(
        &self,
        setup: ProcessSetup,
        virtual_size: TerminalSize,
    ) -> io::Result<Process> {
        Ok(self.create_process_inner(setup, virtual_size, PipeMode::Virtual, std::io::stdout())?)
    }

    pub fn create_logged_process<W>(
        &self,
        setup: ProcessSetup,
        log_file: W,
        virtual_size: TerminalSize,
    ) -> io::Result<Process>
    where
        W: Write + Send + AsRawFd + 'static,
    {
        Ok(self.create_process_inner(setup, virtual_size, PipeMode::Logged, log_file)?)
    }

    /// Create a new process with virtual size (not active)
    fn create_process_inner<W>(
        &self,
        mut setup: ProcessSetup,
        virtual_size: TerminalSize,
        mode: PipeMode,
        target_stdout: W,
    ) -> io::Result<Process>
    where
        W: Write + Send + AsRawFd + 'static,
    {
        // Merge terminal environment variables with provided ones
        for (key, value) in self.get_env() {
            setup.env.push((key.to_string(), value.to_string()));
        }

        let process = Process::new(setup.clone(), virtual_size, mode, target_stdout)
            .map_err(|e| MetatermError::io(format!("Could not create {:?}", setup.id), e))?;

        let id = setup.id.clone();

        // Add the new process
        {
            let mut processes = self.processes.lock().unwrap();
            processes.insert(id, process.clone());
        }

        Ok(process)
    }

    /// Get a process by ID
    pub fn get_process(&self, id: &str) -> Option<Process> {
        let processes = self.processes.lock().unwrap();
        processes.get(id).cloned()
    }

    /// Get the currently active process
    pub fn get_active_process(&self) -> Option<Process> {
        let active_id = self.active_process_id.lock().unwrap();
        if let Some(ref id) = *active_id {
            self.get_process(id)
        } else {
            None
        }
    }

    /// Get all process IDs
    pub fn get_process_ids(&self) -> Vec<String> {
        let processes = self.processes.lock().unwrap();
        processes.keys().cloned().collect()
    }

    /// Remove a process
    pub fn remove_process(&self, id: &str) -> Result<(), Box<dyn std::error::Error>> {
        info!("Removing process: {}", id);

        // If this is the active process, deactivate it first
        {
            let active_id = self.active_process_id.lock().unwrap();
            if active_id.as_ref() == Some(&id.to_string()) {
                return Err("Cannot remove active process".into());
            }
        }

        // Remove from processes map
        {
            let mut processes = self.processes.lock().unwrap();
            processes.remove(id);
        }

        Ok(())
    }

    /// Write to the active process's stdin
    pub fn write_to_active_stdin(&self, data: &[u8]) -> bool {
        if let Some(process) = self.get_active_process() {
            process.write_stdin(data)
        } else {
            false
        }
    }

    pub fn on_control_trigger(
        &self,
        letter: char,
        mut callback: impl FnMut(()) + Send + 'static,
    ) -> ListenerHandle {
        self.trigger_event.ctrl(letter);
        self.trigger_event.trigger_event().subscribe(move |_| {
            callback(());
        })
    }

    pub fn attach_input(&self, process: &Process) {
        self.trigger_event.attach(process.input_jack().clone());
        self.input_pipe
            .input_jack
            .attach(self.trigger_event.clone());
    }

    pub fn detach_input(&self) {
        self.input_pipe.input_jack.attach(Arc::new(()));
    }

    /// Add an environment variable that will be passed to all new processes
    pub fn add_env(&self, key: &str, value: &str) {
        if let Ok(mut env_vars) = self.environment_variables.lock() {
            env_vars.insert(key.to_string(), value.to_string());
            info!("Added environment variable: {}={}", key, value);
        }
    }

    /// Get all environment variables
    pub fn get_env(&self) -> Vec<(String, String)> {
        if let Ok(env_vars) = self.environment_variables.lock() {
            env_vars
                .iter()
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect()
        } else {
            Vec::new()
        }
    }

    pub fn shutdown(&self) {
        info!("Shutting down terminal");
        // Event source will be dropped automatically when terminal is dropped
        self.stop_stdin_thread();
        info!("Terminal shutdown completed");
    }

    pub fn input_pipe(&self) -> &InputPipe {
        &self.input_pipe
    }
}

impl Default for Terminal {
    fn default() -> Self {
        Self::new()
    }
}

impl Terminal {
    /// Stop the stdin forwarding thread
    fn stop_stdin_thread(&self) {
        info!("Stopping stdin forwarding thread");
        let handle = {
            if let Ok(mut thread_guard) = self.input_pipe.stdin_thread.lock() {
                if let Some(handle) = thread_guard.take() {
                    info!("Stdin thread: Got handle");
                    handle
                } else {
                    error!("Stdin thread is not running, cannot stop");
                    return;
                }
            } else {
                error!("Failed to lock stdin thread, cannot stop");
                return;
            }
        };
        handle.join().unwrap();
        info!("Stdin forwarding thread stopped");
    }
}
