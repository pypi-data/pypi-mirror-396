//! Process utility functions for retrieving comprehensive process information.
//!
//! This crate provides cross-platform process information retrieval using the
//! `sysinfo` crate. It offers functions to get process executable paths,
//! working directories, command line arguments, and environment variables.
//!
//! # Features
//!
//! - Cross-platform process information retrieval
//! - Comprehensive process information including PID, PPID, UIDs, GIDs,
//!   name, executable path, current working directory, command line arguments,
//!   and environment variables
//! - Built on the reliable `sysinfo` crate for consistent behavior across platforms
//!
//! # Platform Support
//!
//! Supports all platforms supported by the `sysinfo` crate, including:
//! - **Linux**
//! - **macOS**
//! - **Windows**
//! - **FreeBSD**
//! - And others
//!
//! # Example
//!
//! ```rust
//! use pishell_psutil::get_process_info;
//!
//! let current_pid = std::process::id();
//!
//! if let Some(info) = get_process_info(current_pid) {
//!     println!("Process name: {}", info.name);
//!     if let Some(cwd) = info.cwd {
//!         println!("Working directory: {:?}", cwd);
//!     }
//! }
//! ```

use std::collections::HashMap;
use std::path::PathBuf;

/// Comprehensive process information
#[derive(Debug, Clone)]
pub struct ProcessInfo {
    pub pid: u32,
    pub parent_pid: Option<u32>,
    pub uid: Option<u64>,
    pub euid: Option<u64>,
    pub gid: Option<u64>,
    pub egid: Option<u64>,
    pub name: String,
    pub exe: Option<PathBuf>,
    pub cwd: Option<PathBuf>,
    pub argv: Vec<String>,
    pub env: HashMap<String, String>,
}

/// Extract complete process information using the best available method for each platform
pub fn get_process_info(pid: u32) -> Option<ProcessInfo> {
    let yes = sysinfo::UpdateKind::Always;
    let sysinfo_pid = sysinfo::Pid::from_u32(pid);
    let mut system = sysinfo::System::new();
    system.refresh_processes_specifics(
        sysinfo::ProcessesToUpdate::Some(&[sysinfo_pid]),
        false,
        sysinfo::ProcessRefreshKind::new()
            .with_cmd(yes)
            .with_cwd(yes)
            .with_environ(yes)
            .with_exe(yes)
            .with_user(yes),
    );
    let process = system.process(sysinfo_pid)?;

    let parent_pid = process.parent().map(|p| p.as_u32());
    let name = process.name().to_string_lossy().to_string();
    let uid = process.user_id().map(|id| **id as u64);
    let euid = process.effective_user_id().map(|id| **id as u64);
    let gid = process.group_id().map(|id| *id as u64);
    let egid = process.effective_group_id().map(|id| *id as u64);
    let exe = process.exe().map(|p| p.to_path_buf());
    let cwd = process.cwd().map(|p| p.to_path_buf());
    let argv: Vec<String> = process
        .cmd()
        .iter()
        .map(|s| s.to_string_lossy().to_string())
        .collect();
    let env: HashMap<String, String> = process
        .environ()
        .iter()
        .filter_map(|s| {
            let s_str = s.to_string_lossy();
            if let Some((key, value)) = s_str.split_once('=') {
                Some((key.to_string(), value.to_string()))
            } else {
                Some((s_str.to_string(), String::new()))
            }
        })
        .collect();

    Some(ProcessInfo {
        pid,
        parent_pid,
        uid,
        euid,
        gid,
        egid,
        name,
        exe,
        cwd,
        argv,
        env,
    })
}
