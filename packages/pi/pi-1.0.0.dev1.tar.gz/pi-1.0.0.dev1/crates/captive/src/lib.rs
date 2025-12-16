use clap::{Parser, Subcommand};
use std::ffi::{CString, c_char};
use std::fs::File;
use std::io::{Read, Seek, SeekFrom, Write, stdout};
use std::path::Path;
use std::process::Command;
use std::sync::atomic::{AtomicBool, AtomicI32, Ordering};
use std::sync::{Arc, Barrier, Mutex};
use std::thread;
use std::time::{Duration, Instant};
use tracing::{debug, error, info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use pishell_socket::{
    MessageServer,
    messages::{Message, MessagePeer},
};

mod dirs;
mod host;
mod key_parser;
mod messages;
mod process_manager;
mod string_parser;

use messages::{CaptiveCommandMessage, CaptiveMessage, CaptiveResponseMessage};
use process_manager::{Namespace, ProcessFilter, ProcessInfoLocal, get_process_list};

#[derive(Debug)]
enum ResumeAction {
    Text(String),
    Keys(Vec<String>),
    Ping,
}

// ProcessInfo is now imported from process_manager as ProcessInfoLocal

use key_parser::parse_keys;
use string_parser::parse_rust_string;

use crate::messages::CaptiveState;

#[derive(Parser)]
#[command(name = "pi-captive")]
#[command(about = "A process capture and management tool")]
struct Args {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Parser)]
pub struct RunCommand {
    #[arg(long)]
    kill: bool,

    #[arg(long)]
    tag: Option<String>,

    #[arg(long)]
    timeout: Option<u64>,

    #[arg(trailing_var_arg = true)]
    cmd_args: Vec<String>,
}

#[derive(Subcommand)]
enum Commands {
    /// Start a new process and run until it requires input.
    Run(RunCommand),
    /// List running processes in the namespace
    Ls,
    /// Resume a process with text input
    Resume {
        #[arg(long)]
        tag: Option<String>,
        #[arg(long)]
        pid: Option<u32>,
        #[arg(long)]
        text: Option<String>,
        #[arg(long)]
        key: Vec<String>,
    },
    /// Kill processes
    Kill {
        #[arg(long)]
        tag: Option<String>,
        #[arg(long)]
        pid: Option<u32>,
    },
    /// Remove defunct processes (logs and tags)
    Remove {
        #[arg(long)]
        tag: Option<String>,
        #[arg(long)]
        pid: Option<u32>,
        #[arg(long)]
        all: bool,
    },
    /// View process logs
    Log {
        #[arg(long)]
        tag: Option<String>,
        #[arg(long)]
        pid: Option<u32>,
        #[arg(long)]
        head: bool,
        #[arg(long)]
        tail: bool,
        #[arg(long)]
        all: bool,
    },
    /// Set timeout for a process
    Timeout {
        #[arg(long)]
        tag: Option<String>,
        #[arg(long)]
        pid: Option<u32>,
        timeout: u64,
    },
    DumpScreen {
        #[arg(long)]
        tag: Option<String>,
        #[arg(long)]
        pid: Option<u32>,
    },
    #[command(hide = true, name = "_boot")]
    Boot {
        #[arg(trailing_var_arg = true)]
        cmd_args: Vec<String>,
    },
    #[command(hide = true, name = "_boot2")]
    Boot2 {
        #[arg(trailing_var_arg = true)]
        cmd_args: Vec<String>,
    },
    /// Reset: kill all processes and clean up cache directory
    Reset {
        #[arg(long)]
        force: bool,
    },
}

fn init_log_stdout() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "warn".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .try_init()
        .expect("Failed to initialize tracing");
}

fn init_log() {
    let pid = std::process::id();
    let namespace = Namespace::get();
    let cache_dir = namespace.get_namespace_cache_dir();
    dirs::ensure_dir_exists(&cache_dir).expect("Failed to create cache directory");
    let log_file = std::fs::File::create(cache_dir.join(format!("pishell-captive.{}.log", pid)))
        .expect("Failed to create log file");
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "debug".into()),
        ))
        .with(tracing_subscriber::fmt::layer().with_writer(log_file))
        .try_init()
        .expect("Failed to initialize tracing");
}

/// Get a client connection to a captive process with the given PID
fn get_client(
    pid: u32,
    namespace: &Namespace,
) -> Result<MessageServer, Box<dyn std::error::Error>> {
    let socket_path = namespace.get_socket_path(pid);
    debug!("Socket path: {:?}", socket_path);

    if !socket_path.exists() {
        return Err(format!("Socket not found for PID {}: {:?}", pid, socket_path).into());
    }

    // Connect using the standard MessageServer
    let client = MessageServer::with_socket_path(socket_path)?;
    info!("Created message server");
    client.register(None, None)?;
    info!("Registered message server");

    Ok(client)
}

fn derive_tag_from_cmd(cmd: &str) -> String {
    // Extract the command name from the full command path
    cmd.split('/').last().unwrap_or(cmd).to_string()
}

fn start_captive_process(
    cmd: String,
    args: Vec<String>,
    tag: Option<String>,
    timeout: Option<u64>,
    kill_existing: bool,
    namespace: &Namespace,
) -> Result<u32, Box<dyn std::error::Error>> {
    let tag_provided = tag.is_some();
    let tag = tag.unwrap_or_else(|| derive_tag_from_cmd(&cmd));
    let mut tag = tag.replace(|c: char| c != '-' && !c.is_alphanumeric(), "_");
    let timeout_duration = Duration::from_secs(timeout.unwrap_or(60));

    // Tag rules:
    // - If a tag was provided, it must be unique or --kill must be used.
    // - If a tag was not provided and --kill was used, the process will be
    //   killed.
    // - If a tag was not provided and --kill was not used, we'll find a unique
    //   tag.
    if tag_provided {
        if let Some(process_info) = get_process(ProcessFilter::Tag(tag.clone()), namespace)? {
            if kill_existing {
                println!("[pi] Killing existing process with tag: {}", tag);
                kill_process_by_pid(process_info.pid, namespace)?;
                namespace.remove_tag_symlink(&tag)?;
            } else {
                return Err(
                    format!("Tag '{}' is already in use. Use --kill to replace it.", tag).into(),
                );
            }
        }
    } else {
        let mut index = 0;
        let orig_tag = tag.clone();
        while let Some(process_info) = get_process(ProcessFilter::Tag(tag.clone()), namespace)? {
            tag = if index == 0 {
                orig_tag.clone()
            } else {
                format!("{}-{}", orig_tag, index)
            };
            if kill_existing {
                println!("[pi] Killing existing process with tag: {}", tag);
                kill_process_by_pid(process_info.pid, namespace)?;
                namespace.remove_tag_symlink(&tag)?;
                break;
            } else {
                index += 1;
            }
        }
    }

    // Get the current executable path
    let current_exe = std::env::current_exe()?;

    // Get the original command-line arguments
    let original_args: Vec<String> = std::env::args().collect();

    // Create new arguments with "run" replaced by "_boot"
    let mut new_args: Vec<String> = Vec::new();
    for arg in &original_args[1..] {
        if arg == "run" {
            new_args.push("_boot".to_string());
            break;
        } else {
            new_args.push(arg.clone());
        }
    }

    // Build the command to re-execute with modified arguments
    let mut boot_cmd = Command::new(current_exe);
    boot_cmd.args(&new_args);
    boot_cmd.arg("--");
    boot_cmd.arg(cmd);
    boot_cmd.args(&args);

    // Pass metadata as environment variables
    boot_cmd.env("PI_CAPTIVE_TAG", &tag);
    boot_cmd.env("PI_CAPTIVE_TIMEOUT", timeout_duration.as_secs().to_string());
    boot_cmd.env("PI_CAPTIVE_NAMESPACE", &namespace.to_string());

    let temp_file = tempfile::NamedTempFile::new()?;
    boot_cmd.env(
        "PI_CAPTIVE_PID_FILE",
        temp_file.path().to_string_lossy().to_string(),
    );

    // Start the process
    let _child = boot_cmd.spawn()?;

    let pid = loop {
        std::thread::sleep(std::time::Duration::from_millis(10));
        if !temp_file.path().exists() {
            continue;
        }
        let s = std::fs::read_to_string(temp_file.path()).unwrap_or_default();
        if s.is_empty() {
            continue;
        }
        break std::fs::read_to_string(temp_file.path())?.parse::<u32>()?;
    };

    // Wait for the process to start and create its socket client
    const MAX_CONNECT_TIMEOUT: Duration = Duration::from_millis(30_000);

    let start_time = Instant::now();
    let mut first = true;
    let _client = loop {
        match get_client(pid, namespace) {
            Ok(client) => break client,
            Err(e) => {
                if first {
                    first = false;
                    error!("Failed to connect to captive process, retrying: {}", e);
                }
                if start_time.elapsed() >= MAX_CONNECT_TIMEOUT {
                    eprintln!(
                        "Error: Failed to connect to captive process after {:?} ({e:?})",
                        MAX_CONNECT_TIMEOUT
                    );
                    return Err("Failed to connect to captive process".into());
                }
                thread::sleep(Duration::from_millis(100));
            }
        }
    };

    namespace.create_tag_symlink(&tag, pid)?;

    println!(
        "[pi] Started captive process with --pid {} and --tag {}",
        pid, tag
    );

    info!("Connected to captive process with PID: {}", pid);

    // Ping the process to ensure it's ready
    info!("Pinging captive process to ensure it's ready");
    match resume_process(Some(tag.clone()), Some(pid), ResumeAction::Ping, namespace) {
        Ok(_) => {
            info!("Captive process is ready and responding");
        }
        Err(e) => {
            warn!("Failed to ping captive process: {}, proceeding anyway", e);
        }
    }

    Ok(pid)
}

fn get_process(
    filter: ProcessFilter,
    namespace: &Namespace,
) -> Result<Option<ProcessInfoLocal>, Box<dyn std::error::Error>> {
    let processes = get_process_list(filter, namespace)?;
    Ok(processes.into_iter().next())
}

fn list_processes(namespace: &Namespace) -> Result<(), Box<dyn std::error::Error>> {
    let processes = get_process_list(ProcessFilter::All, namespace)?;

    // Generate process list from ProcessInfo collection
    if processes.is_empty() {
        println!("[pi] No processes running in namespace '{}'", namespace);
    } else {
        for process in &processes {
            println!("[pi] {} ({})", process.id(), process.status());
        }
    }

    Ok(())
}

fn run_client_command(
    tag: Option<String>,
    pid: Option<u32>,
    command: CaptiveCommandMessage,
    wait_for_idle: bool,
    namespace: &Namespace,
) -> Result<(String, Option<i32>), Box<dyn std::error::Error>> {
    let target_pid = if let Some(p) = pid {
        p
    } else if let Some(t) = tag {
        // Look up PID by tag using symlink
        match namespace.get_pid_from_tag(&t)? {
            Some(pid) => pid,
            None => return Err(format!("No process found with tag '{}'", t).into()),
        }
    } else {
        return Err("Either --pid or --tag must be specified".into());
    };

    let client = get_client(target_pid, namespace)?;

    // Set up response handler
    let response_received =
        std::sync::Arc::new(std::sync::Mutex::new(None::<CaptiveResponseMessage>));
    let got_idle = Arc::new(AtomicBool::new(!wait_for_idle));
    let exit_code = Arc::new(AtomicI32::new(i32::MIN));

    let response_received_clone = response_received.clone();
    client.on_message(move |message: Message<CaptiveResponseMessage>| {
        debug!("Received response: {:?}", message.payload);
        *response_received_clone.lock().unwrap() = Some(message.payload.clone());
        None // No response needed
    });

    let got_idle_clone = got_idle.clone();
    let exit_code_clone = exit_code.clone();
    client.on_message(move |message: Message<CaptiveMessage>| {
        debug!("Received message: {:?}", message.payload);
        if matches!(
            message.payload.state,
            CaptiveState::IdleNewline
                | CaptiveState::IdlePromptish
                | CaptiveState::IdleOther
                | CaptiveState::Exit
        ) {
            got_idle_clone.store(true, Ordering::Relaxed);
        }
        if matches!(message.payload.state, CaptiveState::Exit) {
            exit_code_clone.store(message.payload.exit_code.unwrap_or(0), Ordering::Relaxed);
        }
        None // No response needed
    });

    // Start listening for responses
    client.listen()?;

    // Send command based on action
    client.send_message("captive", command)?;

    // Wait for response
    let start_time = std::time::Instant::now();
    let timeout = std::time::Duration::from_secs(5);

    while start_time.elapsed() < timeout {
        if got_idle.load(Ordering::Relaxed) {
            if let Some(response) = response_received.lock().unwrap().take() {
                if !response.success {
                    return Err(format!("Command failed: {}", response.message).into());
                }
                let exit_code = exit_code.load(Ordering::Relaxed);
                if exit_code != i32::MIN {
                    return Ok((response.data.unwrap_or_default(), Some(exit_code)));
                }
                return Ok((response.data.unwrap_or_default(), None));
            }
        }
        std::thread::sleep(std::time::Duration::from_millis(10));
    }

    Err("Timeout waiting for response".into())
}

fn kill_process(
    tag: Option<String>,
    pid: Option<u32>,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    let response = run_client_command(
        tag.clone(),
        pid,
        CaptiveCommandMessage {
            command: "kill".to_string(),
            data: None,
        },
        false,
        namespace,
    );

    let response = match response {
        Ok(response) => response,
        Err(e) => {
            println!("[pi] Failed to kill process: {:?}", e);
            kill_process_signal(tag, pid, namespace)?;
            return Ok(());
        }
    };

    if let Some(exit_code) = response.1 {
        if exit_code == 0 {
            println!("[pi] Process exited successfully");
        } else {
            println!("[pi] Process exited with status: {}", exit_code);
        }
    }

    println!("{}", response.0);

    Ok(())
}

fn kill_process_signal(
    tag: Option<String>,
    pid: Option<u32>,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    let process = get_process(
        if let Some(pid) = pid {
            ProcessFilter::Pid(pid)
        } else if let Some(tag) = tag.clone() {
            ProcessFilter::Tag(tag)
        } else {
            return Err("Either --pid or --tag must be specified".into());
        },
        namespace,
    )?;

    let Some(process) = process else {
        return Err("Process not found".into());
    };

    info!("Sending signal to process with --pid {}", process.pid);
    kill_process_by_pid(process.pid, namespace)?;

    Ok(())
}

fn dump_screen(
    tag: Option<String>,
    pid: Option<u32>,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    let response = run_client_command(
        tag,
        pid,
        CaptiveCommandMessage {
            command: "dump_screen".to_string(),
            data: None,
        },
        false,
        namespace,
    )?;

    if let Some(exit_code) = response.1 {
        if exit_code == 0 {
            println!("[pi] Process exited successfully");
        } else {
            println!("[pi] Process exited with status: {}", exit_code);
        }
    }

    println!("{}", response.0);

    Ok(())
}

fn resume_process(
    tag: Option<String>,
    pid: Option<u32>,
    action: ResumeAction,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    let process = get_process(
        if let Some(pid) = pid {
            ProcessFilter::Pid(pid)
        } else if let Some(tag) = tag.clone() {
            ProcessFilter::Tag(tag)
        } else {
            return Err("Either --pid or --tag must be specified".into());
        },
        namespace,
    )?;

    let Some(process) = process else {
        return Err("Process not found".into());
    };

    let mut log_file = File::open(process.log_file)?;

    let barrier = Arc::new(Barrier::new(2));

    let is_ping = matches!(action, ResumeAction::Ping);
    let stdout_last_read = Arc::new(Mutex::new(Instant::now()));

    let barrier_clone = barrier.clone();
    let stdout_last_read_clone = stdout_last_read.clone();
    let _log_reader = thread::spawn(move || {
        if !is_ping {
            fn seek_log_file(log_file: &mut File) -> Result<(), Box<dyn std::error::Error>> {
                const MAX_LOG_SCAN: i64 = 1024;
                const FALLBACK_LOG_SCAN: i64 = 80;

                let mut buf = [0u8; MAX_LOG_SCAN as _];
                let size = log_file.seek(SeekFrom::End(0))?;
                let read_start = size.saturating_sub(MAX_LOG_SCAN as _);
                log_file.seek(SeekFrom::Start(read_start))?;
                log_file.read(&mut buf[..(size - read_start) as _])?;
                let newline_pos = buf.iter().rposition(|&b| b == b'\n');
                if let Some(newline_pos) = newline_pos {
                    log_file.seek(SeekFrom::Start(read_start + newline_pos as u64 + 1))?;
                } else {
                    log_file.seek(SeekFrom::Start(size.saturating_sub(FALLBACK_LOG_SCAN as _)))?;
                }
                Ok(())
            }

            if let Err(e) = seek_log_file(&mut log_file) {
                warn!("Error seeking log file: {}", e);
            };
        }
        barrier_clone.wait();
        let mut buf = [0u8; 16];
        loop {
            let Ok(bytes_read) = log_file.read(&mut buf) else {
                break;
            };
            if bytes_read == 0 {
                std::thread::sleep(std::time::Duration::from_millis(10));
                continue;
            }
            *stdout_last_read_clone.lock().unwrap() = Instant::now();
            _ = stdout().write_all(&buf[..bytes_read]);
            _ = stdout().flush();
        }
    });

    let _ = barrier.wait();

    // Send command based on action
    let command = match action {
        ResumeAction::Text(text_input) => {
            // Parse any escapes out of the string, using Rust string syntax:
            let unescaped_string = match parse_rust_string(&text_input) {
                Ok(parsed) => parsed,
                Err(e) => {
                    eprintln!("Failed to parse string '{}': {}", text_input, e);
                    return Err(format!("String parsing error: {}", e).into());
                }
            };
            // Send inject_text command
            CaptiveCommandMessage {
                command: "inject_text".to_string(),
                data: Some(unescaped_string),
            }
        }
        ResumeAction::Keys(keys) => {
            let keys = parse_keys(&keys)?;
            let keys_str = String::from_utf8(keys)?;
            CaptiveCommandMessage {
                command: "inject_keys".to_string(),
                data: Some(keys_str),
            }
        }
        ResumeAction::Ping => CaptiveCommandMessage {
            command: "ping".to_string(),
            data: None,
        },
    };

    let response = run_client_command(tag, pid, command, true, namespace)?;
    while stdout_last_read.lock().unwrap().elapsed() < Duration::from_millis(250) {
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
    println!();
    if let Some(exit_code) = response.1 {
        if exit_code == 0 {
            println!("[pi] Process exited successfully");
        } else {
            println!("[pi] Process exited with status: {}", exit_code);
        }
    }

    Ok(())
}

fn kill_process_by_pid(pid: u32, namespace: &Namespace) -> Result<(), Box<dyn std::error::Error>> {
    for pid in [-(pid as i32), pid as i32] {
        unsafe { libc::kill(pid, libc::SIGTERM) };
    }

    // Only remove the socket file to put the process into defunct state
    // Keep the log file and tag symlinks for the remove command to handle
    let socket_path = namespace.get_socket_path(pid);
    if socket_path.exists() {
        let _ = std::fs::remove_file(socket_path);
        info!("Removed socket file for PID {} (process now defunct)", pid);
    }

    Ok(())
}

fn remove_process(
    tag: Option<String>,
    pid: Option<u32>,
    all: bool,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    // Determine the appropriate filter
    let filter = if all {
        ProcessFilter::All
    } else if let Some(p) = pid {
        ProcessFilter::Pid(p)
    } else if let Some(t) = tag {
        ProcessFilter::Tag(t)
    } else {
        return Err("Either --pid, --tag, or --all must be specified".into());
    };

    // Get processes using the filter
    let processes = get_process_list(filter, namespace)?;
    if processes.is_empty() {
        println!(
            "[pi] No processes found to remove in namespace '{}'",
            namespace
        );
        return Ok(());
    }

    // Filter for defunct processes (those without sockets)
    let defunct_processes: Vec<_> = processes
        .into_iter()
        .filter(|p| p.socket_path.is_none())
        .collect();

    if defunct_processes.is_empty() {
        if all {
            println!(
                "[pi] No defunct processes to remove in namespace '{}'",
                namespace
            );
        } else {
            println!(
                "[pi] Process is still running (has active socket). Use 'kill' command to stop it first."
            );
        }
        return Ok(());
    }

    // Remove defunct processes
    let mut removed_count = 0;
    for process in defunct_processes {
        match remove_defunct_process(&process, namespace) {
            Ok(_) => {
                println!("[pi] Removed defunct process: {}", process.id());
                removed_count += 1;
            }
            Err(e) => {
                println!(
                    "[pi] Failed to remove defunct process with PID {}: {}",
                    process.pid, e
                );
            }
        }
    }

    // Summary output
    if all && removed_count > 0 {
        println!(
            "[pi] Removed {} defunct processes in namespace '{}'",
            removed_count, namespace
        );
    }

    Ok(())
}

fn remove_defunct_process(
    process: &ProcessInfoLocal,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    // Remove log file
    if process.log_file.exists() {
        std::fs::remove_file(&process.log_file)?;
        info!("Removed log file: {:?}", process.log_file);
    }

    // Remove tag symlink if applicable
    if let Some(tag) = process.tag.as_ref() {
        let tag_path = namespace.get_tag_path(tag);
        if tag_path.exists() {
            std::fs::remove_file(&tag_path)?;
            info!("Removed tag symlink: {:?}", tag_path);
        }
    }

    Ok(())
}

fn view_logs(
    tag: Option<String>,
    pid: Option<u32>,
    head: bool,
    tail: bool,
    all: bool,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    let target_pid = if let Some(p) = pid {
        p
    } else if let Some(t) = tag {
        // Look up PID by tag using symlink
        match namespace.get_pid_from_tag(&t)? {
            Some(pid) => pid,
            None => return Err(format!("No process found with tag '{}'", t).into()),
        }
    } else {
        return Err("Either --pid or --tag must be specified".into());
    };

    let log_path = namespace.get_log_path(target_pid);

    if !log_path.exists() {
        println!("[pi] No log file found for PID {}", target_pid);
        return Ok(());
    }

    let log_content = std::fs::read_to_string(&log_path)?;

    if log_content.is_empty() {
        println!("[pi] Log file is empty for PID {}", target_pid);
        return Ok(());
    }

    // Handle different log viewing options
    let lines: Vec<&str> = log_content.lines().collect();

    let output = if all {
        log_content
    } else if head {
        // Show first 25 lines
        lines
            .iter()
            .take(25)
            .cloned()
            .collect::<Vec<_>>()
            .join("\n")
    } else if tail {
        // Show last 25 lines (default)
        lines
            .iter()
            .rev()
            .take(25)
            .cloned()
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .collect::<Vec<_>>()
            .join("\n")
    } else {
        // Default to tail 25 lines
        lines
            .iter()
            .rev()
            .take(25)
            .cloned()
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .collect::<Vec<_>>()
            .join("\n")
    };

    println!("[pi] Log output for PID {}:\n{}", target_pid, output);
    Ok(())
}

fn set_timeout(
    tag: Option<String>,
    pid: Option<u32>,
    timeout: u64,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    let target_pid = if let Some(p) = pid {
        p
    } else if let Some(t) = tag {
        // Look up PID by tag using symlink
        match namespace.get_pid_from_tag(&t)? {
            Some(pid) => pid,
            None => return Err(format!("No process found with tag '{}'", t).into()),
        }
    } else {
        return Err("Either --pid or --tag must be specified".into());
    };

    // TODO: Implement actual timeout setting by communicating with the process
    // For now, just acknowledge the command
    println!(
        "[pi] Set timeout to {} seconds for PID {} (not yet fully implemented)",
        timeout, target_pid
    );
    Ok(())
}

fn reset_captive_environment(
    force: bool,
    namespace: &Namespace,
) -> Result<(), Box<dyn std::error::Error>> {
    println!(
        "[pi] Resetting captive environment for namespace '{}'",
        namespace
    );

    if !force {
        println!(
            "[pi] Are you sure you want to reset the captive environment? This will kill all running processes and clean up the cache directory. Use --force to proceed or type 'y' to confirm."
        );
        let mut input = String::new();
        std::io::stdin().read_line(&mut input)?;
        if input.trim().to_lowercase() != "y" {
            println!("[pi] Reset cancelled.");
            return Ok(());
        }
    }

    // First, kill all running processes
    println!("[pi] Killing all running processes...");
    let processes = get_process_list(ProcessFilter::All, namespace)?;

    if processes.is_empty() {
        println!("[pi] No processes to kill");
    } else {
        let mut killed_count = 0;
        for process in &processes {
            let pid = process.pid;
            match kill_process_by_pid(pid, namespace) {
                Ok(_) => {
                    println!("[pi] Killed process with PID {}", pid);
                    killed_count += 1;
                }
                Err(e) => {
                    println!("[pi] Failed to kill process with PID {}: {}", pid, e);
                }
            }
        }
        println!("[pi] Killed {} processes", killed_count);
    }

    // Clean up all sockets, logs, and tag symlinks in the run directory
    println!("[pi] Cleaning up run directory...");
    let run_dir = dirs::get_run_dir();
    if run_dir.exists() {
        match std::fs::remove_dir_all(&run_dir) {
            Ok(_) => {
                println!("[pi] Removed run directory: {:?}", run_dir);
            }
            Err(e) => {
                println!("[pi] Failed to remove run directory: {:?}: {}", run_dir, e);
            }
        }
    }

    // Clean up all logs in the cache directory
    println!("[pi] Cleaning up cache directory...");
    let cache_dir = dirs::get_cache_dir();
    if cache_dir.exists() {
        match std::fs::remove_dir_all(&cache_dir) {
            Ok(_) => {
                println!("[pi] Removed cache directory: {:?}", cache_dir);
            }
            Err(e) => {
                println!(
                    "[pi] Failed to remove cache directory: {:?}: {}",
                    cache_dir, e
                );
            }
        }
    }

    println!("[pi] Reset complete");
    Ok(())
}

/// `setsid` and then fork again. Never returns.
fn daemonize(cmd: &Path, cmd_args: &[&str]) -> ! {
    fn leak_string(s: &str) -> *const c_char {
        let cstr = CString::new(s).unwrap();
        let ptr = cstr.as_ptr() as *const c_char;
        std::mem::forget(cstr);
        ptr
    }
    let mut args = vec![];
    for arg in cmd_args {
        args.push(leak_string(arg));
    }
    args.push(std::ptr::null());
    let args = args.as_slice() as *const _ as *const *const c_char;
    let cmd = leak_string(cmd.to_str().unwrap());

    // Close stdio handles by dup2'ing /dev/null over them all
    let null_fd = unsafe { libc::open(c"/dev/null".as_ptr(), libc::O_RDWR) };
    if null_fd == -1 {
        panic!("Failed to open /dev/null");
    }

    unsafe {
        if libc::dup2(null_fd, libc::STDIN_FILENO) == -1 {
            panic!("Failed to redirect stdin to /dev/null");
        }
        if libc::dup2(null_fd, libc::STDOUT_FILENO) == -1 {
            panic!("Failed to redirect stdout to /dev/null");
        }
        if libc::dup2(null_fd, libc::STDERR_FILENO) == -1 {
            panic!("Failed to redirect stderr to /dev/null");
        }

        if null_fd > libc::STDERR_FILENO {
            libc::close(null_fd);
        }
    }

    unsafe {
        if libc::setsid() == -1 {
            panic!("Failed to set session id");
        }
    }
    let pid = unsafe { libc::fork() };
    if pid == -1 {
        panic!("Failed to fork");
    }

    let res = unsafe { libc::setpgid(pid, 0) };
    if res == -1 {
        panic!("Failed to set process group id");
    }

    // Exit if parent process
    if pid != 0 {
        let pid_file = std::env::var("PI_CAPTIVE_PID_FILE").unwrap();
        let temp_pid_file = format!("{pid_file}.tmp");
        std::fs::write(&temp_pid_file, pid.to_string()).unwrap();
        std::fs::rename(temp_pid_file, pid_file).unwrap();
        std::process::exit(0);
    }

    unsafe {
        if libc::execv(cmd, args) == -1 {
            panic!("Failed to execute command");
        }
    }

    unreachable!();
}

pub fn main(args: &[&str]) -> Result<(), Box<dyn std::error::Error>> {
    let namespace = Namespace::get();

    // Use clap for other commands
    let args = Args::parse_from(args);

    if !matches!(args.command, Commands::Boot { .. } | Commands::Boot2 { .. }) {
        init_log();
    }

    match args.command {
        Commands::Run(run_cmd) => {
            let kill = run_cmd.kill;
            let tag = run_cmd.tag;
            let timeout = run_cmd.timeout;
            let cmd_args = &run_cmd.cmd_args;

            if cmd_args.is_empty() {
                return Err("Command is required".into());
            }

            let cmd = &cmd_args[0];
            let args = &cmd_args[1..];

            info!("Running command: {} with args: {:?}", cmd, args);
            let pid = start_captive_process(
                cmd.to_string(),
                args.iter().map(|s| s.to_string()).collect(),
                tag,
                timeout,
                kill,
                &namespace,
            )?;
            Ok(())
        }
        Commands::Ls => {
            info!("Listing processes");
            list_processes(&namespace)
        }
        Commands::Resume {
            tag,
            pid,
            text,
            key,
        } => {
            info!("Resuming process");
            let action = if let Some(text_input) = text {
                ResumeAction::Text(text_input)
            } else if !key.is_empty() {
                ResumeAction::Keys(key)
            } else {
                return Err("Either --text or --key must be specified".into());
            };
            resume_process(tag, pid, action, &namespace)
        }
        Commands::DumpScreen { tag, pid } => {
            info!("Dumping screen");
            dump_screen(tag, pid, &namespace)
        }
        Commands::Kill { tag, pid } => {
            info!("Killing process");
            kill_process(tag, pid, &namespace)
        }
        Commands::Remove { tag, pid, all } => {
            info!("Removing defunct process");
            remove_process(tag, pid, all, &namespace)
        }
        Commands::Log {
            tag,
            pid,
            head,
            tail,
            all,
        } => {
            info!("Viewing logs");
            view_logs(tag, pid, head, tail, all, &namespace)
        }
        Commands::Timeout { tag, pid, timeout } => {
            info!("Setting timeout");
            set_timeout(tag, pid, timeout, &namespace)
        }
        Commands::Boot { cmd_args } => {
            if cmd_args.is_empty() {
                return Err("Command is required".into());
            }

            let cmd = std::env::current_exe()?;
            let mut args = vec![];
            for arg in std::env::args() {
                if arg == "_boot" {
                    args.push("_boot2");
                } else {
                    args.push(arg.leak());
                }
            }

            daemonize(&cmd, args.as_slice());
        }
        Commands::Boot2 { cmd_args } => {
            init_log();

            let cmd = &cmd_args[0];
            let args = &cmd_args[1..];

            info!("Booting command: {} with args: {:?}", cmd, args);
            if let Err(e) = host::run_captive_process(
                cmd.to_string(),
                args.iter().map(|s| s.to_string()).collect(),
                &namespace,
            ) {
                error!("Failed to run captive process: {}", e);
                Err(e)
            } else {
                info!("Captive process completed");
                Ok(())
            }
        }
        Commands::Reset { force } => {
            info!("Resetting captive environment");
            reset_captive_environment(force, &namespace)
        }
    }
}
