use std::collections::HashSet;
use std::io::{self, IsTerminal};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use tracing::{error, info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use pishell_eventbus::DISPATCHER;
use pishell_metaterm::{IdleType, PipeMode, Process, ProcessSetupBuilder, RealTerminal, Terminal};
use pishell_rpc_types::ShellEvents;
use pishell_socket::{MessageServer, SocketServer};
use strum::IntoEnumIterator;

pub mod babelshell;
mod parent_shell;
mod project;
mod project_service;
pub mod semprompt;
mod service;

use pishell_ui::run_ui;
use uuid::Uuid;

use crate::babelshell::Shell;

fn init_log() {
    let log_file = std::fs::File::create("/tmp/pishell.log").expect("Failed to create log file");
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "debug".into()),
        ))
        .with(tracing_subscriber::fmt::layer().with_writer(log_file))
        .try_init()
        .expect("Failed to initialize tracing");
}

fn init_panic_handler() {
    // Set up panic handler to log to tracing
    std::panic::set_hook(Box::new(|panic_info| {
        let message = if let Some(s) = panic_info.payload().downcast_ref::<String>() {
            s.clone()
        } else if let Some(s) = panic_info.payload().downcast_ref::<&str>() {
            s.to_string()
        } else {
            "Unknown panic".to_string()
        };

        let location = if let Some(location) = panic_info.location() {
            format!(
                " at {}:{}:{}",
                location.file(),
                location.line(),
                location.column()
            )
        } else {
            " at unknown location".to_string()
        };

        tracing::error!("Panic occurred: {}{}", message, location);
    }));
}

fn is_debug_enabled() -> bool {
    matches!(
        std::env::var("_PI_UI_DEBUG").as_deref(),
        Ok("1") | Ok("true"),
    )
}

fn is_semprompt_disabled() -> bool {
    matches!(
        std::env::var("PI_SHELL_PROMPT_INTEGRATION").as_deref(),
        Ok("0") | Ok("false") | Ok("disable") | Ok("disabled"),
    )
}

pub fn main(python_exe: &str, args: &[&str]) -> Result<(), Box<dyn std::error::Error>> {
    if !io::stdin().is_terminal() || !io::stdout().is_terminal() {
        return Err("stdin and stdout must be terminals for pi shell".into());
    }

    let debug = is_debug_enabled();

    let sidebar_path = if let Ok(sidebar_path) = std::env::var("_PI_SIDEBAR") {
        shellish_parse::parse(&sidebar_path, shellish_parse::ParseOptions::new()).unwrap()
    } else if debug {
        // Enable `uv run textual console`
        vec![
            python_exe.to_string(),
            "-I".to_string(),
            "-m".to_string(),
            "textual_dev".to_string(),
            "run".to_string(),
            "--dev".to_string(),
            "pi._internal.app:PiApp".to_string(),
        ]
    } else {
        vec![
            python_exe.to_string(),
            "-m".to_string(),
            "pi._internal.app".to_string(),
        ]
    };
    let args = &args[1..];

    if debug {
        println!("-------------------------------");
        println!("---------- pishell ------------");
        println!("---- context saved for LLM ----");
        println!("-------------------------------");

        eprintln!("sidebar_path: {:?}", sidebar_path);
        eprintln!("args: {:?}", args);
    }
    let res = run(sidebar_path, args);

    if debug {
        println!("-------------------------------");
        println!("---------- pishell ------------");
        println!("--------- thank you! ----------");
        println!("-------------------------------");
    }

    info!("Shell process exited");

    res
}

fn broadcast_terminal_event(
    shell_events_client: &ShellEvents::Client<MessageServer>,
    shell: Arc<Process>,
    kind: ShellEvents::TerminalEventKind,
) {
    let request = ShellEvents::TerminalEventRequest {
        event: ShellEvents::TerminalEvent {
            active_pid: shell.foreground_pid().unwrap_or(0).into(),
            kind,
        },
    };

    if let Err(e) = shell_events_client.terminal_event_broadcast(request) {
        error!("Failed to send broadcast message: {}", e);
    }
}

fn run(mut sidebar_path: Vec<String>, args: &[&str]) -> Result<(), Box<dyn std::error::Error>> {
    init_log();
    init_panic_handler();

    // Start socket server (manages its own thread)
    let mut socket_server = SocketServer::new()?;
    socket_server.start()?;
    info!("Socket server started successfully");

    // Create and register message server with the socket server's path
    let message_server = MessageServer::with_socket_path(socket_server.socket_path())?;
    message_server.register(Some("shell".to_string()), None)?;
    info!("Message server registered successfully");

    // Start listening for messages (manages its own thread)
    message_server.listen()?;
    info!("Message server started listening");

    let real_terminal = RealTerminal::new();

    // Create a new Terminal instance
    let terminal = Terminal::new();
    terminal.add_env("PI_SOCKET", &socket_server.socket_path());

    let size = real_terminal.size();
    info!("Created terminal with size: {:?}", size);

    let ready_uuid = Uuid::new_v4();
    let _ready_message = format!("ready:{}", ready_uuid);

    let shell_builder = ProcessSetupBuilder::new().with_id("shell");

    let shell_builder = if let Some(cursor_position) = real_terminal.terminal_info().cursor_position
    {
        shell_builder.with_initial_cursor_position(Some(cursor_position))
    } else {
        shell_builder.with_initial_cursor_position(None)
    };

    let shell = if args.is_empty() {
        let mut shell_path = if let Ok(shell_path) = std::env::var("_PI_SHELL") {
            shell_path.into()
        } else if let Some(shell) = parent_shell::detect_parent_shell() {
            shell
        } else if let Ok(shell_env) = std::env::var("SHELL") {
            warn!("could not detect parent shell, falling back to login shell");
            shell_env.into()
        } else {
            warn!(
                "could not detect parent shell, and could not detect login shell, \
                falling back to default (`/bin/bash`)"
            );
            "/bin/bash".into()
        };

        let shell_type = if let Ok(shell_type) = std::env::var("_PI_SHELL_TYPE") {
            shell_type
                .try_into()
                .map_err(|_| "Unsupported shell type")?
        } else {
            match Shell::try_from(&shell_path) {
                Ok(st) => st,
                Err(_) => {
                    warn!(
                        "parent shell `{shell_path:?}` is not supported, falling back to `/bin/bash`"
                    );
                    shell_path = "/bin/bash".into();
                    Shell::try_from(&shell_path).map_err(|_| "Unsupported shell type")?
                }
            }
        };

        let need_semprompt_enablement = if is_semprompt_disabled() {
            info!(
                "Semantic shell prompt integration disabled via PI_SHELL_PROMPT_INTEGRATION environment variable"
            );
            vec![]
        } else {
            info!("Probing for existing semantic shell prompt integration...");

            match semprompt::probe_shell(shell_type, &shell_path) {
                Ok(result) => {
                    let all_seqs: HashSet<_> = pishell_metaterm::Osc133Type::iter().collect();
                    let unsupported: Vec<_> =
                        all_seqs.difference(&result.detected_sequences).collect();
                    if unsupported.is_empty() {
                        info!("Semantic shell integration is already enabled in target shell");
                    } else {
                        info!(
                            "Semantic shell integration has not been detected in target shell, \
                            will attempt to enable"
                        );
                    }
                    unsupported.iter().map(|seq| seq.to_string()).collect()
                }
                Err(e) => {
                    return Err(e.into());
                }
            }
        };

        let mut env = vec![(
            "_PI_SHELL_EXECUTABLE".to_string(),
            shell_path.to_string_lossy().to_string(),
        )];

        if !need_semprompt_enablement.is_empty() {
            env.push((
                "_PI_SETUP_SEMANTIC_PROMPT".to_string(),
                need_semprompt_enablement.join(","),
            ));
        }

        let (i_args, i_env) = shell_type.interactive_mode();
        env.extend(i_env.iter().map(|(k, v)| (k.to_string(), v.to_string())));

        info!("launching shell {shell_path:?}");

        let shell_cmd = std::env::current_exe()
            .unwrap()
            .to_str()
            .unwrap()
            .to_string();

        let mut args = vec![
            "shell-launch".to_string(),
            shell_type.shell_name().to_string(),
            shell_path.to_string_lossy().to_string(),
        ];
        args.extend(i_args.iter().map(|a| a.to_string()));

        terminal.create_process(
            shell_builder
                .with_command(shell_cmd)
                .with_args(args)
                .with_env(env)
                .build(),
            real_terminal.size(),
        )?
    } else {
        terminal.create_active_process(
            shell_builder
                .with_command(args[0])
                .with_args(args[1..].iter().map(|s| s.to_string()).collect::<Vec<_>>())
                .build(),
            real_terminal.size(),
        )?
    };

    // Fill the shell with pseudo-random characters before the cursor position
    // to suggest that it's unavailable in the history.
    shell.virtual_pty().clear();
    if let Some(cursor_position) = real_terminal.terminal_info().cursor_position {
        shell.virtual_pty().set_cursor_position(
            cursor_position.0.saturating_sub(1),
            cursor_position.1.saturating_sub(1),
        );
    }

    let real_terminal = Arc::new(real_terminal);
    let shell = Arc::new(shell);
    let shell_service = service::setup(
        shell.clone(),
        real_terminal.terminal_info().clone(),
        &message_server,
    )?;
    let _project_service = project_service::setup(&message_server)?;
    let shell_events_client = ShellEvents::Client::new(message_server.clone());
    let shell_clone = shell.clone();
    let _idle_handle = {
        let mut shell_events_client = shell_events_client.clone();
        shell.on_idle(move |is_idle| {
            info!("Shell is idle");
            broadcast_terminal_event(
                &mut shell_events_client,
                shell_clone.clone(),
                if is_idle == IdleType::Active {
                    ShellEvents::TerminalEventKind::Idle
                } else {
                    ShellEvents::TerminalEventKind::Active
                },
            );
        })
    };

    // Create a virtual process (sidebar) at full screen size
    let sidebar = terminal.create_process(
        ProcessSetupBuilder::new()
            .with_id("sidebar".to_string())
            .with_command(sidebar_path.remove(0))
            .with_args(sidebar_path)
            .build(),
        size, // Full screen size - overlay handled via background character
    )?;
    let sidebar = Arc::new(sidebar);

    // if args.is_empty() {
    //     loop {
    //         if shell.virtual_pty().dump().contains(&ready_message) {
    //             break;
    //         }
    //         std::thread::sleep(std::time::Duration::from_millis(10));
    //     }
    // };

    info!("Shell is ready");
    terminal.set_active_process(&shell);

    let in_ui = Arc::new(AtomicBool::new(false));

    let _size_handle = {
        let sidebar = sidebar.clone();
        let shell = shell.clone();
        let in_ui = in_ui.clone();
        let real_terminal_clone = real_terminal.clone();
        real_terminal_clone.on_size_change(move |size| {
            if in_ui.load(Ordering::Relaxed) {
                return;
            }
            let _ = shell.set_window_size(size);
            let _ = sidebar.set_window_size(size); // Full screen size
        })
    };

    // When the terminal gets the trigger key (Ctrl+K), open the UI
    let terminal_clone = terminal.clone();
    let sidebar_clone = sidebar.clone();

    let shell_clone = shell.clone();
    let sidebar_cleanup = sidebar.clone();

    let trigger = std::env::var("PI_TRIGGER")
        .unwrap_or_else(|_| "g".to_string())
        .chars()
        .next()
        .unwrap_or('g');

    let shell_service_clone = shell_service.clone();
    let _trigger_handle = terminal.on_control_trigger(trigger, move |_| {
        info!("Trigger handler called!");
        let shell_events_client = shell_events_client.clone();
        let shell_clone = shell_clone.clone();
        let terminal_clone = terminal_clone.clone();
        let in_ui = in_ui.clone();
        let sidebar_clone = sidebar_clone.clone();
        let shell_service_clone = shell_service_clone.clone();

        std::thread::spawn(move || {
            broadcast_terminal_event(
                &shell_events_client,
                shell_clone.clone(),
                ShellEvents::TerminalEventKind::SidebarActivated,
            );

            terminal_clone.detach_input();
            shell_clone.change_mode(PipeMode::Virtual);

            // Run the provided function
            in_ui.store(true, Ordering::Relaxed);
            let (close_event_source, close_event_listeners) = DISPATCHER.tear_off::<()>();
            shell_service_clone.set_sidebar_close_event(close_event_source);
            run_ui(
                terminal_clone.clone(),
                shell_clone.clone(),
                sidebar_clone.clone(),
                close_event_listeners,
            );
            in_ui.store(false, Ordering::Relaxed);

            shell_clone.change_mode(PipeMode::Direct);
            terminal_clone.attach_input(&shell_clone);

            broadcast_terminal_event(
                &shell_events_client,
                shell_clone.clone(),
                ShellEvents::TerminalEventKind::SidebarDeactivated,
            );
        });
    });

    // Wait for the shell process to exit before existing the program
    let _ = shell.wait();
    let _ = sidebar_cleanup.kill();

    terminal.shutdown();

    drop(real_terminal);

    Ok(())
}

pub fn shell_main(args: &[&str]) -> Result<(), Box<dyn std::error::Error>> {
    // Since this is an internal command, we don't need to print help
    if args.len() < 2 {
        return Err("Invalid arguments".into());
    }

    let Ok(shell) = Shell::try_from(args[1]) else {
        return Err("Invalid shell".into());
    };
    let shell_path = args[2].to_string();
    let rc_args = args[3..].to_vec();

    let rc_script = shell.rc_script();
    let Some(rc_script) = rc_script else {
        return Err(format!("No rc script or args for shell {shell:?}").into());
    };

    let rc_file = tempfile::NamedTempFile::with_prefix(".pitmprc.")?;
    let rc_path = rc_file.path();
    std::fs::write(rc_path, rc_script)?;
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(rc_path, std::fs::Permissions::from_mode(0o755))?;

    let shell_exe = std::ffi::CString::new(shell_path).unwrap();

    let args = shell.insert_rc_args(&rc_args, rc_file.path());
    let mut args_cstring = vec![shell_exe.clone()];
    for arg in args {
        args_cstring.push(std::ffi::CString::new(arg).unwrap());
    }
    let mut args_ptr: Vec<*const libc::c_char> = args_cstring.iter().map(|s| s.as_ptr()).collect();
    args_ptr.push(std::ptr::null());

    unsafe {
        libc::execv(shell_exe.as_ptr(), args_ptr.as_ptr());
    }

    // If we reach here, exec failed
    std::process::exit(1);
}
