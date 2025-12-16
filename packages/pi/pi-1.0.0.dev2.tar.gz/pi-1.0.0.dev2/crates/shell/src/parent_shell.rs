use crate::babelshell::Shell;
use std::collections::HashSet;
use std::path::PathBuf;
use tracing::debug;

/// Detect the parent shell by traversing the process tree
pub fn detect_parent_shell() -> Option<PathBuf> {
    let mut current_pid = std::process::id();
    let mut visited = HashSet::new();

    for depth in 0..10 {
        // Prevent infinite loops
        if !visited.insert(current_pid) {
            debug!("Process cycle detected at PID {:?}", current_pid);
            return None;
        }

        let process = pishell_psutil::get_process_info(current_pid)?;

        // Skip the current process (pi shell itself)
        if depth > 0 {
            debug!(
                "Checking process at depth {}: PID {:?}, Name: {}, Exe: {:?}",
                depth, current_pid, process.name, process.exe,
            );

            // Check if it's a known shell
            if let Some(exe_path) = &process.exe
                && let Ok(shell) = Shell::try_from(exe_path)
            {
                debug!(
                    "Found parent shell: {} (PID: {:?}, path: {:?}, cmd: {:?})",
                    shell.shell_name(),
                    process.pid,
                    process.exe,
                    process.argv,
                );
                return Some(exe_path.clone());
            }
        }

        // Move to parent
        let parent_pid = process.parent_pid;
        if let Some(parent_pid) = parent_pid {
            if parent_pid <= 1 {
                debug!("Reached system process (PID: {:?})", parent_pid);
                break;
            }

            current_pid = parent_pid;
        } else {
            debug!("Process PID {:?} has no parent PID", process.pid);
            break;
        }
    }

    debug!("No shell found in process ancestry");
    None
}
