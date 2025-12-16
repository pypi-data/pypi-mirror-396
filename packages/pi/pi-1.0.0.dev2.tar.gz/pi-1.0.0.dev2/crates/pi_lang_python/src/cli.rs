//! Python command-line argument processing for Pi shim
//!
//! This module provides functionality to determine if a Python invocation
//! should be interactive (Pi REPL) or non-interactive (direct execution).

use std::path::PathBuf;

/// Execution mode for Python invocation
#[derive(Debug, Clone)]
pub enum ExecutionMode {
    /// Direct execution with Python arguments
    Direct(Vec<String>, Vec<(String, String)>),
    /// Interactive REPL execution with shell arguments
    Repl(Vec<String>),
}

/// Result of processing Python command-line arguments
#[derive(Debug, Clone)]
pub struct PythonInvocation {
    /// Execution mode with appropriate arguments
    pub mode: ExecutionMode,
    /// The Python executable to use
    pub python_executable: PathBuf,
    /// The Python prefix (venv) to use (if detected)
    pub python_prefix: Option<PathBuf>,
}

/// Parsed Python command-line arguments
#[derive(Debug, Default)]
struct ParsedArgs {
    /// Inspect interactively after running script
    interactive: bool,
    /// Program passed in as string
    command: Option<String>,
    /// Run library module as a script
    module: Option<String>,
    /// Any help or version flag (all non-interactive)
    informational: bool,
    /// Whether a script file was found
    has_script: bool,
}

/// Extract Python version from executable name (e.g. "python3.12" -> Some("3.12"))
fn extract_python_version(executable: &str) -> Option<String> {
    if let Some(version_part) = executable.strip_prefix("python") {
        if version_part.is_empty() {
            None // Just "python"
        } else if version_part.starts_with('3') {
            Some(version_part.to_string()) // "3" or "3.12" etc.
        } else {
            None
        }
    } else {
        None
    }
}

/// Filter virtual environments based on Python version
fn filter_venvs_by_version(
    venvs: Vec<pi_lang::ToolchainEnvironment>,
    target_version: Option<&str>,
) -> Vec<pi_lang::ToolchainEnvironment> {
    if let Some(target_version) = target_version {
        // Try to find venvs that match the target version
        let matching_venvs: Vec<_> = venvs
            .into_iter()
            .filter(|venv| {
                if let Some(venv_version) = &venv.version {
                    // Match exact version (e.g. "3.12") or major version prefix (e.g. "3")
                    return venv_version == target_version
                        || venv_version.starts_with(&format!("{target_version}."));
                }
                false
            })
            .collect();

        if matching_venvs.is_empty() {
            // If no matching venvs found, return empty to use fallback
            Vec::new()
        } else {
            matching_venvs
        }
    } else {
        venvs
    }
}

/// Process Python command-line arguments and determine execution mode
#[must_use]
pub fn process_python_invocation(args: &[&str]) -> PythonInvocation {
    // Extract Python executable name and version from first argument
    let (python_executable_name, python_args) = if args.is_empty() {
        ("python", Vec::new())
    } else {
        let exe_name = args[0];
        let remaining_args: Vec<String> = args[1..].iter().map(|s| (*s).to_string()).collect();
        (exe_name, remaining_args)
    };

    let python_version = extract_python_version(python_executable_name);

    // Parse arguments manually
    let parsed = parse_python_args(&python_args);

    // Determine if invocation should be interactive
    let is_interactive = determine_interactive_mode(&parsed);

    // Detect virtual environments and filter by version if specified
    let (detected_executable, detected_prefix) = if let Ok(cwd) = std::env::current_dir() {
        let venvs = crate::detect_virtual_environments(
            &cwd,
            crate::EnvironmentLookupConfig {
                include_global: true,
            },
        );

        // Filter venvs by Python version if we have one
        let filtered_venvs = filter_venvs_by_version(venvs, python_version.as_deref());

        if filtered_venvs.is_empty() {
            // No matching venv found, use the original executable name
            (PathBuf::from(python_executable_name), None)
        } else {
            let venv = &filtered_venvs[0];
            // Use the detected venv executable or fall back to the requested executable
            (
                venv.executable
                    .clone()
                    .unwrap_or_else(|| PathBuf::from(python_executable_name)),
                venv.prefix.clone(),
            )
        }
    } else {
        // Could not get current directory, use the requested executable name
        (PathBuf::from(python_executable_name), None)
    };

    let mut result = PythonInvocation {
        mode: if is_interactive {
            ExecutionMode::Repl(Vec::new()) // Will be populated below
        } else {
            let mut env: Vec<(String, String)> = vec![];
            if let Some(prefix) = &detected_prefix {
                env.push((
                    "VIRTUAL_ENV".to_string(),
                    prefix.to_string_lossy().to_string(),
                ));

                // Add the venv's bin directory to PATH
                let bin_dir = (if cfg!(windows) {
                    prefix.join("Scripts")
                } else {
                    prefix.join("bin")
                })
                .to_string_lossy()
                .to_string();

                let path = if let Ok(current_path) = std::env::var("PATH") {
                    format!("{bin_dir}{}{current_path}", std::path::MAIN_SEPARATOR)
                } else {
                    bin_dir
                };

                env.push(("PATH".to_string(), path));
            }

            ExecutionMode::Direct(python_args.clone(), env)
        },
        python_executable: detected_executable,
        python_prefix: detected_prefix,
    };

    // Prepare shell args for interactive mode
    if let ExecutionMode::Repl(_) = result.mode {
        let shell_args = prepare_repl_args(&result, &python_args);
        result.mode = ExecutionMode::Repl(shell_args);
    }

    result
}

/// Parse Python command-line arguments manually
fn parse_python_args(args: &[String]) -> ParsedArgs {
    let mut parsed = ParsedArgs::default();
    let mut i = 0;

    while i < args.len() {
        let arg = &args[i];

        match arg.as_str() {
            "-i" => {
                parsed.interactive = true;
                i += 1;
            }
            "-c" => {
                if i + 1 < args.len() {
                    parsed.command = Some(args[i + 1].clone());
                    return parsed; // Stop processing after -c
                }
                // Missing command argument, invalid but continue
                i += 1;
            }
            "-m" => {
                if i + 1 < args.len() {
                    parsed.module = Some(args[i + 1].clone());
                    return parsed; // Stop processing after -m
                }
                // Missing module argument, invalid but continue
                i += 1;
            }
            "-h" | "--help" | "-V" | "--version" | "--help-env" | "--help-xoptions"
            | "--help-all" => {
                parsed.informational = true;
                i += 1;
            }
            arg if arg.starts_with('-') => {
                // Handle flags that take arguments
                if matches!(arg, "-W" | "-X") && i + 1 < args.len() {
                    i += 2; // Skip flag and its value
                } else {
                    i += 1; // Skip just the flag
                }
            }
            "-" => {
                // Stdin input - this is interactive
                return parsed;
            }
            _ => {
                // Non-flag argument: script file found
                parsed.has_script = true;
                return parsed; // Stop processing after finding script
            }
        }
    }

    parsed
}

/// Determine if invocation should be interactive based on parsed args
fn determine_interactive_mode(parsed: &ParsedArgs) -> bool {
    // Non-interactive conditions
    if parsed.informational {
        return false;
    }
    if parsed.command.is_some() {
        return parsed.interactive; // -c is non-interactive unless -i is also set
    }
    if parsed.module.is_some() {
        return parsed.interactive; // -m is non-interactive unless -i is also set
    }
    if parsed.has_script {
        return parsed.interactive; // Script file is non-interactive unless -i is set
    }

    // Default to interactive (no script/command/module found)
    true
}

/// Prepare arguments for interactive shell mode
fn prepare_repl_args(invocation: &PythonInvocation, python_args: &[String]) -> Vec<String> {
    let mut shell_args = vec![];

    // Add isolation flag and repl module for interactive mode
    shell_args.push("-I".to_string());
    // Add any additional Python args that matter for interactive mode
    shell_args.extend(python_args.iter().cloned());

    shell_args.push("-m".to_string());
    shell_args.push("pi._internal.repl".to_string());

    // Add Python executable info
    shell_args.push("--python-executable".to_string());
    shell_args.push(invocation.python_executable.to_string_lossy().to_string());

    if let Some(prefix) = &invocation.python_prefix {
        shell_args.push("--python-prefix".to_string());
        shell_args.push(prefix.to_string_lossy().to_string());
    }

    shell_args
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_interactive_mode_no_args() {
        let args = ["python3"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_)));
        // The executable might be from detected venv or the requested one
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
        }
    }

    #[test]
    fn test_non_interactive_command() {
        let args = ["python3", "-c", "print('hello')"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        // The executable might be from detected venv or the requested one
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["-c", "print('hello')"]);
        }
    }

    #[test]
    fn test_non_interactive_module() {
        let args = ["python3", "-m", "json.tool"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["-m", "json.tool"]);
        }
    }

    #[test]
    fn test_non_interactive_script() {
        let args = ["python3", "script.py", "arg1"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["script.py", "arg1"]);
        }
    }

    #[test]
    fn test_forced_interactive() {
        let args = ["python3", "-i", "script.py"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
            assert!(shell_args.contains(&"-i".to_string()));
            assert!(shell_args.contains(&"script.py".to_string()));
        }
    }

    #[test]
    fn test_help_non_interactive() {
        let args = ["python3", "--help"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["--help"]);
        }
    }

    #[test]
    fn test_version_non_interactive() {
        let args = ["python3", "-V"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["-V"]);
        }
    }

    #[test]
    fn test_stdin_interactive() {
        let args = ["python3", "-"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
            assert!(shell_args.contains(&"-".to_string()));
        }
    }

    #[test]
    fn test_forced_interactive_with_command() {
        let args = ["python3", "-i", "-c", "import os"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
            assert!(shell_args.contains(&"-i".to_string()));
            assert!(shell_args.contains(&"-c".to_string()));
            assert!(shell_args.contains(&"import os".to_string()));
        }
    }

    #[test]
    fn test_forced_interactive_with_module() {
        let args = ["python3", "-i", "-m", "json.tool"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
            assert!(shell_args.contains(&"-i".to_string()));
            assert!(shell_args.contains(&"-m".to_string()));
            assert!(shell_args.contains(&"json.tool".to_string()));
        }
    }

    #[test]
    fn test_flags_passed_through() {
        let args = ["python3", "-O", "-W", "ignore", "-X", "dev", "script.py"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _))); // Script file
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(
                *direct_args,
                vec!["-O", "-W", "ignore", "-X", "dev", "script.py"]
            );
        }
    }

    #[test]
    fn test_complex_interactive_flags() {
        let args = ["python3", "-O", "-W", "ignore"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_))); // No script/command/module
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
            assert!(shell_args.contains(&"-O".to_string()));
            assert!(shell_args.contains(&"-W".to_string()));
            assert!(shell_args.contains(&"ignore".to_string()));
        }
    }

    #[test]
    fn test_malformed_command_flag() {
        let args = ["python3", "-c"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_))); // No command provided, defaults to interactive
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
            assert!(shell_args.contains(&"-c".to_string()));
        }
    }

    #[test]
    fn test_malformed_module_flag() {
        let args = ["python3", "-m"];

        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_))); // No module provided, defaults to interactive
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Repl(shell_args) = &result.mode {
            assert!(shell_args.contains(&"shell".to_string()));
            assert!(shell_args.contains(&"pi._internal.repl".to_string()));
            assert!(shell_args.contains(&"-m".to_string()));
        }
    }

    #[test]
    fn test_early_termination_with_command() {
        let args = ["python3", "-O", "-c", "print('hello')", "ignored", "args"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _))); // Has -c command
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(
                *direct_args,
                vec!["-O", "-c", "print('hello')", "ignored", "args"]
            );
        }
    }

    #[test]
    fn test_early_termination_with_module() {
        let args = [
            "python3",
            "-W",
            "ignore",
            "-m",
            "json.tool",
            "extra",
            "args",
        ];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _))); // Has -m module
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(
                *direct_args,
                vec!["-W", "ignore", "-m", "json.tool", "extra", "args"]
            );
        }
    }

    #[test]
    fn test_early_termination_with_script() {
        let args = ["python3", "-O", "script.py", "script", "args"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _))); // Has script file
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["-O", "script.py", "script", "args"]);
        }
    }

    #[test]
    fn test_help_env_non_interactive() {
        let args = ["python3", "--help-env"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["--help-env"]);
        }
    }

    #[test]
    fn test_help_xoptions_non_interactive() {
        let args = ["python3", "--help-xoptions"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["--help-xoptions"]);
        }
    }

    #[test]
    fn test_help_all_non_interactive() {
        let args = ["python3", "--help-all"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["--help-all"]);
        }
    }

    #[test]
    fn test_short_help_non_interactive() {
        let args = ["python3", "-h"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["-h"]);
        }
    }

    #[test]
    fn test_python_version_extraction() {
        // Test python3.12
        let args = ["python3.12"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Repl(_)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
    }

    #[test]
    fn test_python_version_specific_script() {
        let args = ["python3.11", "script.py"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["script.py"]);
        }
    }

    #[test]
    fn test_python_major_version() {
        let args = ["python3", "-c", "print('hello')"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["-c", "print('hello')"]);
        }
    }

    #[test]
    fn test_plain_python_executable() {
        let args = ["python", "--version"];
        let result = process_python_invocation(&args);
        assert!(matches!(result.mode, ExecutionMode::Direct(_, _)));
        assert!(
            result
                .python_executable
                .to_string_lossy()
                .contains("python")
        );
        if let ExecutionMode::Direct(direct_args, _) = &result.mode {
            assert_eq!(*direct_args, vec!["--version"]);
        }
    }
}
