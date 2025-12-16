use nix::sys::signal::{SaFlags, SigAction, SigHandler, SigSet, Signal, sigaction};
use std::{
    fs::File,
    sync::{
        Arc, Mutex,
        atomic::{AtomicBool, Ordering},
    },
    time::Duration,
};
use tracing::{error, info, warn};

use pishell_metaterm::{IdleType, ProcessSetupBuilder, Terminal, TerminalSize};
use pishell_socket::{
    MessageServer, SocketServer,
    messages::{Message, MessagePeer},
};

use crate::{
    messages::{CaptiveCommandMessage, CaptiveMessage, CaptiveResponseMessage, CaptiveState},
    process_manager::{Namespace, ProcessFilter, get_process_list},
};

#[derive(Clone)]
struct CurrentProcessState {
    inner: Arc<Mutex<CurrentProcessStateInner>>,
    message_server: MessageServer,
}

struct CurrentProcessStateInner {
    state: CaptiveState,
    exit_code: Option<i32>,
    ready: bool,
}

impl CurrentProcessState {
    pub fn new(message_server: MessageServer) -> Self {
        Self {
            inner: Arc::new(Mutex::new(CurrentProcessStateInner {
                state: CaptiveState::Ready,
                exit_code: None,
                ready: false,
            })),
            message_server,
        }
    }

    pub fn set_ready(&self) {
        info!("Sent initial ready message");
        let mut lock = self.inner.lock().unwrap();
        if !lock.ready {
            lock.ready = true;
            let state = lock.state;
            let exit_code = lock.exit_code;
            drop(lock);

            self.message_server
                .send_message(
                    "broadcast",
                    CaptiveMessage {
                        state: CaptiveState::Ready,
                        exit_code: None,
                    },
                )
                .ok();

            if state != CaptiveState::Ready {
                self.message_server
                    .send_message("broadcast", CaptiveMessage { state, exit_code })
                    .ok();
            }
        } else {
            panic!("Can't be ready again");
        }
    }

    pub fn set_idle(&self, idle: IdleType) {
        let mut lock = self.inner.lock().unwrap();
        let state = match idle {
            IdleType::Active => CaptiveState::Active,
            IdleType::IdleNewline => CaptiveState::IdleNewline,
            IdleType::IdlePromptish => CaptiveState::IdlePromptish,
            IdleType::IdleOther => CaptiveState::IdleOther,
        };
        if lock.state != state {
            lock.state = state;
            let exit_code = lock.exit_code;
            let ready = lock.ready;
            drop(lock);
            if ready {
                self.message_server
                    .send_message("broadcast", CaptiveMessage { state, exit_code })
                    .ok();
            }
        }
    }

    pub fn set_exit(&self, code: i32) {
        let mut lock = self.inner.lock().unwrap();
        lock.state = CaptiveState::Exit;
        lock.exit_code = Some(code);
        drop(lock);

        self.message_server
            .send_message(
                "broadcast",
                CaptiveMessage {
                    state: CaptiveState::Exit,
                    exit_code: Some(code),
                },
            )
            .ok();
    }

    pub fn resend(&self) {
        let lock = self.inner.lock().unwrap();
        if lock.ready {
            if let Some(exit_code) = lock.exit_code {
                self.message_server
                    .send_message(
                        "broadcast",
                        CaptiveMessage {
                            state: CaptiveState::Exit,
                            exit_code: Some(exit_code),
                        },
                    )
                    .ok();
            } else {
                match lock.state {
                    CaptiveState::Ready => self
                        .message_server
                        .send_message(
                            "broadcast",
                            CaptiveMessage {
                                state: CaptiveState::Ready,
                                exit_code: None,
                            },
                        )
                        .ok(),
                    CaptiveState::Active => self
                        .message_server
                        .send_message(
                            "broadcast",
                            CaptiveMessage {
                                state: CaptiveState::Active,
                                exit_code: None,
                            },
                        )
                        .ok(),
                    CaptiveState::IdleNewline => self
                        .message_server
                        .send_message(
                            "broadcast",
                            CaptiveMessage {
                                state: CaptiveState::IdleNewline,
                                exit_code: None,
                            },
                        )
                        .ok(),
                    CaptiveState::IdlePromptish => self
                        .message_server
                        .send_message(
                            "broadcast",
                            CaptiveMessage {
                                state: CaptiveState::IdlePromptish,
                                exit_code: None,
                            },
                        )
                        .ok(),
                    CaptiveState::IdleOther => self
                        .message_server
                        .send_message(
                            "broadcast",
                            CaptiveMessage {
                                state: CaptiveState::IdleOther,
                                exit_code: None,
                            },
                        )
                        .ok(),
                    CaptiveState::Exit => self
                        .message_server
                        .send_message(
                            "broadcast",
                            CaptiveMessage {
                                state: CaptiveState::Exit,
                                exit_code: Some(0),
                            },
                        )
                        .ok(),
                };
            }
        }
    }
}

/// Derive a tag from a command string
pub fn derive_tag_from_cmd(cmd: &str) -> String {
    // Extract the command name from the full command path
    cmd.split('/').last().unwrap_or(cmd).to_string()
}

/// Handle dump_screen command
pub fn handle_dump_screen(
    process: &pishell_metaterm::Process,
) -> Result<Option<String>, Box<dyn std::error::Error>> {
    let text = process.virtual_pty().dump();
    info!("Screen dump: {}", text);
    Ok(Some(text))
}

/// Handle inject_text command
pub fn handle_inject_text(
    process: &pishell_metaterm::Process,
    text: &str,
) -> Result<Option<String>, Box<dyn std::error::Error>> {
    if !process.write_stdin(text.as_bytes()) {
        return Err("Failed to inject text".into());
    }
    info!("Successfully injected text: {}", text);
    Ok(None)
}

/// Handle inject_keys command
pub fn handle_inject_keys(
    process: &pishell_metaterm::Process,
    keys_str: &str,
) -> Result<Option<String>, Box<dyn std::error::Error>> {
    let keys: Vec<&str> = keys_str.split(',').collect();
    info!("Handling inject_keys request: {:?}", keys);

    for key in keys {
        if !process.write_stdin(key.as_bytes()) {
            return Err("Failed to inject key".into());
        }
        info!("Successfully injected key: {}", key);
    }

    Ok(None)
}

pub fn handle_kill(
    process: &pishell_metaterm::Process,
) -> Result<Option<String>, Box<dyn std::error::Error>> {
    info!("Handling kill request");
    process.kill();
    Ok(None)
}

/// Handle ping command
pub fn handle_ping() -> Result<Option<String>, Box<dyn std::error::Error>> {
    info!("Handling ping request");
    Ok(Some("pong".to_string()))
}

pub fn run_captive_process(
    cmd: String,
    args: Vec<String>,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    let pid = std::process::id();
    let socket_path = namespace.get_socket_path(pid);

    // Get metadata from environment variables
    let tag = std::env::var("PI_CAPTIVE_TAG").unwrap_or_else(|_| derive_tag_from_cmd(&cmd));
    let timeout_secs = std::env::var("PI_CAPTIVE_TIMEOUT")
        .unwrap_or_else(|_| "60".to_string())
        .parse::<u64>()
        .unwrap_or(60);
    let timeout = Duration::from_secs(timeout_secs);
    let namespace_env =
        std::env::var("PI_CAPTIVE_NAMESPACE").unwrap_or_else(|_| "default".to_string());

    info!(
        "Starting captive process with PID: {}, tag: {}, timeout: {:?}, namespace: {}",
        pid, tag, timeout, namespace_env
    );

    println!("[pi] Created process with --tag {} and --pid {}", tag, pid);

    // Show other running processes
    let all_processes = get_process_list(ProcessFilter::All, &namespace)?;
    let other_processes: Vec<_> = all_processes.into_iter().filter(|p| p.pid != pid).collect();

    if !other_processes.is_empty() {
        println!("[pi] Other processes are running (use kill, resume or log to interact):");
        for process_info in other_processes {
            let status: String = process_info.status();
            println!("[pi] {} ({})", process_info.id(), status);
        }
    }

    // Create socket server with custom path
    let mut temp_socket_path = socket_path.clone();
    temp_socket_path.set_extension("sock.temp");
    let mut socket_server = SocketServer::with_path(temp_socket_path.clone())?;
    socket_server.start()?;

    info!(
        "Renaming socket file from {:?} to {:?}",
        temp_socket_path, socket_path
    );
    std::fs::rename(temp_socket_path, &socket_path)?;

    // Create message server that connects to the socket server
    let message_server = MessageServer::with_socket_path(socket_path.clone())?;
    info!("Created message server");

    message_server.register(Some("captive".to_string()), None)?;
    info!("Registered message server");

    // Set up message handlers for captive-specific messages
    let terminal = Terminal::new();
    let virtual_size = TerminalSize::new(30, 120);

    // Create log file path
    let log_path = namespace.get_log_path(pid);
    let log_file = File::create(&log_path)?;
    info!("Log file path: {:?}", log_path);

    let process = terminal.create_logged_process(
        ProcessSetupBuilder::new()
            .with_id("process")
            .with_command(cmd)
            .with_args(args)
            .build(),
        log_file,
        virtual_size,
    )?;

    // Safety exit: if the log file is removed, exit the process
    let log_path_clone = log_path.clone();
    let process_clone = process.clone();

    static SIGINT_RECEIVED: AtomicBool = AtomicBool::new(false);

    extern "C" fn sigint_handler(_: i32) {
        SIGINT_RECEIVED.store(true, Ordering::Relaxed);
    }

    // SIGINT handler (async-signal-safe)
    info!("Setting up SIGINT handler");
    unsafe {
        let sa = SigAction::new(
            SigHandler::Handler(sigint_handler),
            SaFlags::SA_RESTART,
            SigSet::empty(),
        );
        sigaction(Signal::SIGINT, &sa)?;
    }
    info!("SIGINT handler installed");

    std::thread::spawn(move || {
        loop {
            if SIGINT_RECEIVED.load(Ordering::Relaxed) {
                info!("SIGINT received, killing process");
                process_clone.kill();
                break;
            }
            if !log_path_clone.exists() {
                error!("Log file was removed, exiting: {:?}", log_path_clone);
                process_clone.kill();
                break;
            }
            std::thread::sleep(std::time::Duration::from_millis(250));
        }
    });

    let current_state = CurrentProcessState::new(message_server.clone());

    {
        let current_state = current_state.clone();
        process
            .on_idle(move |idle| {
                current_state.set_idle(idle);
            })
            .forget();
    }

    let process_final = process.clone();

    info!("Setting up message handlers...");

    // Handle captive command messages
    let current_state_clone = current_state.clone();
    message_server.on_message(move |message: Message<CaptiveCommandMessage>| {
        info!("Received captive command: {}", message.payload.command);
        info!("Message details: {:?}", message);

        let command = &message.payload.command;
        let result = match command.as_str() {
            "dump_screen" => {
                info!("Handling dump_screen request");
                handle_dump_screen(&process)
            }
            "inject_text" => {
                if let Some(text) = &message.payload.data {
                    info!("Handling inject_text request: {}", text);
                    handle_inject_text(&process, text)
                } else {
                    info!("No text data provided for inject_text");
                    Err("No text data provided".into())
                }
            }
            "inject_keys" => {
                if let Some(keys_str) = &message.payload.data {
                    info!("Handling inject_keys request: {}", keys_str);
                    handle_inject_keys(&process, keys_str)
                } else {
                    info!("No keys data provided for inject_keys");
                    Err("No keys data provided".into())
                }
            }
            "ping" => {
                info!("Handling ping request");
                handle_ping()
            }
            "kill" => {
                info!("Handling kill request");
                handle_kill(&process)
            }
            _ => {
                info!("Unknown command: {}", command);
                Err(format!("Unknown command: {}", command).into())
            }
        };

        current_state_clone.resend();

        match result {
            Ok(data) => Some(message.response(CaptiveResponseMessage {
                success: true,
                message: "Command executed successfully".to_string(),
                data,
            })),
            Err(e) => {
                error!("Command failed: {}", e);
                Some(message.response(CaptiveResponseMessage {
                    success: false,
                    message: format!("Command failed: {}", e),
                    data: None,
                }))
            }
        }
    });

    current_state.set_ready();

    // Start listening for messages
    info!("Starting message server listener");
    message_server.listen()?;
    info!("Message server listener started");

    // For now, skip terminal creation and just keep the socket server running
    info!("Captive process socket server started successfully");
    info!("Socket path: {:?}", socket_path);

    let exit_code = process_final.wait()?;
    info!("Process exited with status: {:?}", exit_code);

    if let Some(code) = exit_code.code() {
        current_state.set_exit(code);
    } else {
        // Signal
        current_state.set_exit(-1);
    }

    // Stay alive for 60 seconds to allow time to view logs
    std::thread::sleep(std::time::Duration::from_secs(60));

    // Remove socket file and log file
    if socket_path.exists() {
        if let Err(e) = std::fs::remove_file(&socket_path) {
            warn!("Failed to remove socket file {:?}: {}", socket_path, e);
        } else {
            info!("Removed socket file: {:?}", socket_path);
        }
    }

    if log_path.exists() {
        if let Err(e) = std::fs::remove_file(&log_path) {
            warn!("Failed to remove log file {:?}: {}", log_path, e);
        } else {
            info!("Removed log file: {:?}", log_path);
        }
    }

    // Remove tag symlink
    if let Err(e) = namespace.remove_tag_symlink(&tag) {
        warn!("Failed to remove tag symlink {:?}: {}", tag, e);
    }

    Ok(())
}
