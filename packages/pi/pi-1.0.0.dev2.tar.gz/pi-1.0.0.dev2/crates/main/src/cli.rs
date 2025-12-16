use std::collections::VecDeque;
use std::process::Command;

/// Execute command directly with the given arguments and env
fn exec_direct(
    exe: &str,
    args: &[&str],
    env: &[(&str, &str)],
) -> Result<(), Box<dyn std::error::Error>> {
    let mut cmd = Command::new(exe);
    cmd.args(args);
    cmd.envs(env.iter().map(|(k, v)| (k, v)));

    #[cfg(unix)]
    {
        use std::os::unix::process::CommandExt;
        let err = cmd.exec();
        // exec only returns if there's an error
        return Err(Box::new(err));
    }

    #[cfg(not(unix))]
    {
        let status = cmd.status()?;
        if !status.success() {
            std::process::exit(status.code().unwrap_or(1));
        }
        Ok(())
    }
}

fn is_debug_enabled() -> bool {
    match std::env::var("_PI_REPL_DEBUG").as_deref() {
        Ok("1") | Ok("true") => true,
        _ => false,
    }
}

pub fn get_python_exe() -> String {
    // Try to find a sibling python executable next to the current binary
    if let Ok(exe_path) = std::env::current_exe()
        && let Some(exe_dir) = exe_path.parent()
    {
        let root = pi_lang_python::find_possible_project_root(
            exe_dir,
            &pi_lang::DetectionConfig::default(),
        );
        if let Some(root) = &root {
            let venvs = pi_lang_python::detect_virtual_environments(
                root,
                pi_lang_python::EnvironmentLookupConfig {
                    include_global: false,
                },
            );
            if !venvs.is_empty()
                && let Some(exe) = &venvs[0].executable
            {
                return exe.to_string_lossy().to_string();
            } else {
                // Check for python3 first, then python
                let python_names = ["python3", "python"];

                for python_name in &python_names {
                    let python_path = exe_dir.join(python_name);
                    if python_path.exists() {
                        // Return the absolute path as a string
                        return python_path.to_string_lossy().to_string();
                    }
                }
            }
        }
    }

    // Fallback to "python" if no sibling executable found
    "python3".to_string()
}

pub fn main(mut args: VecDeque<&str>) {
    // Remove argv[0] which is the script/module path
    args.pop_front().expect("Missing argv[0]");

    let python_exe = get_python_exe();
    // Leak the python_exe string to get a &'static str since
    // we need it for the program lifetime
    let python_exe_static = Box::leak(python_exe.clone().into_boxed_str());
    if is_debug_enabled() {
        eprintln!("Using `{python_exe}` to run PI")
    }

    // Check for "--" separator to pass commands to shell
    // This handles both "pi shell -- cmd" and "pi -- cmd" formats
    let mut shell_command_args = Vec::new();

    // First, check if the first argument is "--" (implicit shell command)
    if !args.is_empty() && args[0] == "--" {
        // Remove the "--" separator
        args.pop_front();

        // Everything after "--" becomes shell command args
        while let Some(arg) = args.pop_front() {
            shell_command_args.push(arg);
        }

        // Set shell as the subcommand
        args.push_back("shell");
    }
    // Otherwise, check if the first argument is "shell" with a "--" separator
    else if !args.is_empty() && args[0] == "shell" {
        // Look for "--" separator
        let mut found_separator = false;
        let mut new_args = VecDeque::new();
        new_args.push_back("shell");

        // Skip the "shell" argument and process the rest
        args.pop_front();

        for arg in args.iter() {
            if found_separator {
                shell_command_args.push(*arg);
            } else if *arg == "--" {
                found_separator = true;
            } else {
                new_args.push_back(*arg);
            }
        }

        args = new_args;
    }

    if args.is_empty() {
        args.push_front("shell");
    }

    let mut subcommand = *args.front().unwrap();

    // Check if the subcommand looks like it's the pi executable itself
    // This can happen when 'pi pi' is invoked or similar patterns
    // We check if the subcommand ends with "/pi" or is just "pi"
    if subcommand == "pi" || subcommand.ends_with("/pi") {
        if is_debug_enabled() {
            eprintln!(
                "Subcommand '{}' appears to be the pi executable, treating as default",
                subcommand
            );
        }
        args.pop_front(); // Remove the executable name from args
        if args.is_empty() {
            args.push_front("shell");
        }
        subcommand = *args.front().unwrap();
    }

    if subcommand == "--help" || subcommand == "-h" {
        println!("pi: a transcendental shell experience");
        println!("Usage: pi <command>");
        println!();
        println!("Commands (use pi <command> --help for more info):");
        println!("  captive    Run a captive process");
        println!("  shell      Run an LLM-enabled shell");
        println!("  python     Run python with pi enhancements");
        std::process::exit(0);
    } else if subcommand == "--version" {
        println!("{}", env!("CARGO_PKG_VERSION"));
        std::process::exit(0);
    }

    let already_in_pi = std::env::var("PI_EXE").is_ok_and(|v| !v.is_empty());
    if !already_in_pi {
        unsafe {
            std::env::set_var("PI_EXE", std::env::current_exe().unwrap());
        }
    }

    let res = match subcommand {
        "captive" => pishell_captive::main(args.make_contiguous()),
        "shell" => {
            if already_in_pi {
                eprintln!("pi is already running in this shell session, exiting");
                std::process::exit(1);
            }

            // Add shell command args if present
            if !shell_command_args.is_empty() {
                for arg in shell_command_args {
                    args.push_back(arg);
                }
            }
            pishell_shell::main(python_exe_static, args.make_contiguous())
        }
        "shell-launch" => pishell_shell::shell_main(args.make_contiguous()),
        _ if subcommand.starts_with("python") || subcommand == "py" => {
            // Handle python, python3, python3.11, etc.
            let invocation = pi_lang_python::process_python_invocation(args.make_contiguous());

            match &invocation.mode {
                pi_lang_python::ExecutionMode::Repl(shell_args) => {
                    // Interactive mode: use the shell with Pi REPL
                    let mut shell_args_str: Vec<&str> = vec![];
                    if !already_in_pi {
                        shell_args_str.push("shell");
                        shell_args_str.push(python_exe_static);
                    }
                    shell_args_str.extend(shell_args.iter().map(|s| s.as_str()));
                    if already_in_pi {
                        exec_direct(python_exe_static, &shell_args_str, &[])
                    } else {
                        pishell_shell::main(&python_exe_static, &shell_args_str)
                    }
                }
                pi_lang_python::ExecutionMode::Direct(python_args, python_env) => {
                    // Non-interactive mode: execute Python directly
                    let args_str: Vec<&str> = python_args.iter().map(|s| s.as_str()).collect();
                    let env_str: Vec<(&str, &str)> = python_env
                        .iter()
                        .map(|(k, v)| (k.as_str(), v.as_str()))
                        .collect();
                    exec_direct(
                        invocation.python_executable.to_str().unwrap(),
                        &args_str,
                        &env_str,
                    )
                }
            }
        }
        _ => Err(format!("Unknown command: {subcommand}").into()),
    };

    if let Err(error) = res {
        let mut e = &*error;
        loop {
            eprintln!("{e}");
            e = if let Some(cause) = e.source() {
                cause.into()
            } else {
                break;
            };
        }
        std::process::exit(1);
    }
}
