use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::fmt;
use std::path::PathBuf;
use std::time::{Duration, Instant};
use tracing::{info, warn};

// Custom serialization for Instant
mod instant_serde {
    use super::*;

    pub fn serialize<S>(instant: &Instant, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_u64(instant.elapsed().as_secs())
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Instant, D::Error>
    where
        D: Deserializer<'de>,
    {
        let secs = u64::deserialize(deserializer)?;
        Ok(Instant::now() - Duration::from_secs(secs))
    }
}

// Custom serialization for Duration
mod duration_serde {
    use super::*;

    pub fn serialize<S>(duration: &Duration, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_u64(duration.as_secs())
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Duration, D::Error>
    where
        D: Deserializer<'de>,
    {
        let secs = u64::deserialize(deserializer)?;
        Ok(Duration::from_secs(secs))
    }
}

#[derive(Debug)]
pub enum ProcessFilter {
    All,
    Pid(u32),
    Tag(String),
}

#[derive(Debug)]
pub struct ProcessInfoLocal {
    pub pid: u32,
    pub name: String,
    pub start_time: std::time::SystemTime,
    pub tag: Option<String>,
    pub log_file: std::path::PathBuf,
    pub socket_path: Option<std::path::PathBuf>,
    pub reachable: bool,
}

impl ProcessInfoLocal {
    pub fn id(&self) -> String {
        if let Some(tag) = &self.tag {
            format!("--pid {} --tag {}", self.pid, tag)
        } else {
            format!("--pid {}", self.pid)
        }
    }

    /// Get the status of this process based on reachability and log file activity
    pub fn status(&self) -> String {
        if !self.reachable {
            return "not responding".to_string();
        }

        // Check if there's recent activity in the log file
        if let Ok(metadata) = std::fs::metadata(&self.log_file) {
            if let Ok(modified_time) = metadata.modified() {
                let now = std::time::SystemTime::now();
                if let Ok(duration) = now.duration_since(modified_time) {
                    if duration.as_secs() < 10 {
                        return "active".to_string();
                    } else {
                        return format!("idle for {}s", duration.as_secs());
                    }
                }
            }
        }
        "running".to_string()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessInfoSerializable {
    pub pid: u32,
    pub tag: String,
    pub cmd: String,
    pub args: Vec<String>,
    #[serde(with = "instant_serde")]
    pub start_time: Instant,
    #[serde(with = "instant_serde")]
    pub last_activity: Instant,
    #[serde(with = "duration_serde")]
    pub timeout: Duration,
    pub status: ProcessStatus,
    pub namespace: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Namespace {
    namespace: String,
}

impl Namespace {
    /// Create a new namespace with the given string
    pub fn new(namespace: String) -> Self {
        // Ensure that namespace contains only alphanumeric characters plus underscore and hyphen
        if !namespace
            .chars()
            .all(|c| c.is_alphanumeric() || c == '_' || c == '-')
        {
            panic!("PI_NAMESPACE contains invalid characters: {}", namespace);
        }
        Self { namespace }
    }

    /// Get namespace from environment variable PI_NAMESPACE, or default if not set
    pub fn get() -> Self {
        let namespace = std::env::var("PI_NAMESPACE").unwrap_or_else(|_| "default".to_string());
        Self::new(namespace)
    }

    /// Get the namespace string (owned)
    pub fn to_string(&self) -> String {
        self.namespace.clone()
    }

    /// Get the run directory for this namespace
    pub fn get_namespace_run_dir(&self) -> PathBuf {
        let base_run_dir = crate::dirs::get_run_dir();
        if self.namespace == "default" {
            base_run_dir
        } else {
            base_run_dir.join(&self.namespace)
        }
    }

    /// Get the cache directory for this namespace
    pub fn get_namespace_cache_dir(&self) -> PathBuf {
        let base_cache_dir = crate::dirs::get_cache_dir();
        if self.namespace == "default" {
            base_cache_dir
        } else {
            base_cache_dir.join(&self.namespace)
        }
    }

    /// Get socket path for a given PID in this namespace
    pub fn get_socket_path(&self, pid: u32) -> PathBuf {
        let run_dir = self.get_namespace_run_dir();
        crate::dirs::ensure_dir_exists(&run_dir).expect("Failed to create run directory");
        run_dir.join(format!("pishell-captive.{}.sock", pid))
    }

    /// Get log path for a given PID in this namespace
    pub fn get_log_path(&self, pid: u32) -> PathBuf {
        let run_dir = self.get_namespace_run_dir();
        crate::dirs::ensure_dir_exists(&run_dir).expect("Failed to create cache directory");
        run_dir.join(format!("pishell-captive.{}.log", pid))
    }

    /// Get tag path for a given tag in this namespace
    pub fn get_tag_path(&self, tag: &str) -> PathBuf {
        let run_dir = self.get_namespace_run_dir();
        crate::dirs::ensure_dir_exists(&run_dir).expect("Failed to create run directory");
        run_dir.join(format!("pishell-tag.{}", tag))
    }

    /// Get tag symlink path for a given tag in this namespace
    pub fn get_tag_symlink_path(&self, tag: &str) -> PathBuf {
        let run_dir = self.get_namespace_run_dir();
        crate::dirs::ensure_dir_exists(&run_dir).expect("Failed to create run directory");
        run_dir.join(format!("pishell-tag.{}", tag))
    }

    /// Create a symlink from tag to PID socket in this namespace
    pub fn create_tag_symlink(&self, tag: &str, pid: u32) -> Result<(), std::io::Error> {
        let tag_path = self.get_tag_symlink_path(tag);
        let socket_path = self.get_socket_path(pid);

        // Remove existing symlink if it exists
        if tag_path.exists() {
            std::fs::remove_file(&tag_path)?;
        }

        // Create symlink
        std::os::unix::fs::symlink(&socket_path, &tag_path)?;
        Ok(())
    }

    /// Remove a tag symlink in this namespace
    pub fn remove_tag_symlink(&self, tag: &str) -> Result<(), std::io::Error> {
        let tag_path = self.get_tag_symlink_path(tag);
        let _ = std::fs::remove_file(&tag_path);
        Ok(())
    }

    /// Get PID from tag symlink in this namespace
    pub fn get_pid_from_tag(&self, tag: &str) -> Result<Option<u32>, std::io::Error> {
        let tag_path = self.get_tag_symlink_path(tag);
        if !tag_path.exists() {
            return Ok(None);
        }

        // Read the symlink to get the socket path
        let socket_path = std::fs::read_link(&tag_path)?;
        let socket_name = socket_path
            .file_name()
            .and_then(|name| name.to_str())
            .ok_or_else(|| {
                std::io::Error::new(std::io::ErrorKind::InvalidData, "Invalid socket path")
            })?;

        // Extract PID from socket name (namespace is now in directory structure)
        if let Some(pid_str) = socket_name
            .strip_prefix("pishell-captive.")
            .and_then(|s| s.strip_suffix(".sock"))
        {
            if let Ok(pid) = pid_str.parse::<u32>() {
                return Ok(Some(pid));
            }
        }

        Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "Invalid socket name format",
        ))
    }
}

impl fmt::Display for Namespace {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.namespace)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProcessStatus {
    Running,
    WaitingForInput,
    Idle,
    Terminated,
}

pub fn get_process_list(
    filter: ProcessFilter,
    namespace: &Namespace,
) -> Result<Vec<ProcessInfoLocal>, Box<dyn std::error::Error>> {
    let run_dir = namespace.get_namespace_run_dir();

    if !run_dir.exists() {
        return Ok(Vec::new());
    }

    // Bidirectional maps for tag <-> pid mapping
    let mut tag_to_pid = std::collections::HashMap::new();
    let mut pid_to_tag = std::collections::HashMap::new();

    // Collections for socket and log file PIDs
    let mut socket_pids = std::collections::HashSet::new();
    let mut log_pids = std::collections::HashSet::new();
    let mut reachable_pids = std::collections::HashSet::new();

    // First pass: scan run directory for sockets and tags, and cache directory for logs
    let mut entries = Vec::new();

    // Scan run directory for sockets and tag symlinks
    if let Ok(run_entries) = std::fs::read_dir(&run_dir) {
        for entry in run_entries.filter_map(|entry| match entry {
            Ok(entry) => Some(entry),
            Err(e) => {
                warn!("Failed to read run directory entry: {}", e);
                None
            }
        }) {
            let path = entry.path();
            if let Some(file_name) = path.file_name() {
                if let Some(name_str) = file_name.to_str() {
                    entries.push((path.clone(), name_str.to_string()));
                } else {
                    warn!("Failed to convert file name to string: {:?}", file_name);
                }
            } else {
                warn!("Failed to get file name from path: {:?}", path);
            }
        }
    }

    for (path, name_str) in entries {
        // Handle tag symlinks
        if let Some(tag) = name_str.strip_prefix("pishell-tag.") {
            if let Some(target) = std::fs::read_link(&path)
                .ok()
                .and_then(|s| s.file_name().map(|s| s.to_string_lossy().to_string()))
            {
                if let Some(pid_str) = target
                    .strip_prefix("pishell-captive.")
                    .and_then(|s| s.strip_suffix(".sock"))
                {
                    if let Ok(pid) = pid_str.parse::<u32>() {
                        tag_to_pid.insert(tag.to_string(), pid);
                        pid_to_tag.insert(pid, tag.to_string());
                    } else {
                        warn!("Failed to parse PID from tag symlink target: {}", pid_str);
                    }
                } else {
                    warn!("Failed to understand symlink target name: {:?}", path);
                }
            } else {
                warn!("Failed to read symlink: {:?}", path);
            }
        }

        // Handle socket files
        if let Some(pid_str) = name_str
            .strip_prefix("pishell-captive.")
            .and_then(|s| s.strip_suffix(".sock"))
        {
            if let Ok(pid) = pid_str.parse::<u32>() {
                // Try to connect using a unix socket to verify it's active
                let socket_path = namespace.get_socket_path(pid);
                match std::os::unix::net::UnixStream::connect(&socket_path) {
                    Ok(_) => {
                        // Connection successful, socket is active
                        socket_pids.insert(pid);
                        reachable_pids.insert(pid);
                    }
                    Err(e) => {
                        warn!("Failed to connect to socket for PID {}: {}", pid, e);
                        // Process might have died, clean up socket
                        if let Err(remove_err) = std::fs::remove_file(&path) {
                            warn!(
                                "Failed to remove dead socket file {:?}: {}",
                                path, remove_err
                            );
                        }
                    }
                }
            } else {
                warn!("Failed to parse PID from socket file name: {}", pid_str);
            }
        }

        // Handle log files
        if let Some(pid_str) = name_str
            .strip_prefix("pishell-captive.")
            .and_then(|s| s.strip_suffix(".log"))
        {
            if let Ok(pid) = pid_str.parse::<u32>() {
                // Add all log file PIDs
                log_pids.insert(pid);
            } else {
                warn!("Failed to parse PID from log file name: {}", pid_str);
            }
        }
    }

    // Merge socket and log PIDs into a single collection
    let mut all_pids: std::collections::HashSet<u32> =
        socket_pids.union(&log_pids).cloned().collect();

    for (tag, pid) in &tag_to_pid {
        if !all_pids.contains(&pid) {
            let tag_path = namespace.get_tag_symlink_path(&tag);
            info!("tag path: {:?}", tag_path);
            // Check if symlink exists and verify its target
            if std::fs::symlink_metadata(&tag_path).is_ok() {
                // Verify the target still exists
                if let Ok(target_path) = std::fs::read_link(&tag_path) {
                    if !target_path.exists() {
                        std::fs::remove_file(&tag_path)?;
                        info!("Removed orphaned tag symlink: {:?}", tag_path);
                    }
                } else {
                    // Symlink target is invalid, remove it
                    std::fs::remove_file(&tag_path)?;
                    info!("Removed invalid tag symlink: {:?}", tag_path);
                }
            }
        }
    }

    // Apply filter if specified
    match filter {
        ProcessFilter::All => {
            // Keep all PIDs - no filtering needed
        }
        ProcessFilter::Pid(pid) => {
            if all_pids.contains(&pid) {
                // Keep only the filtered PID
                all_pids.clear();
                all_pids.insert(pid);
            } else {
                // Filtered PID not found, return empty result
                return Ok(Vec::new());
            }
        }
        ProcessFilter::Tag(tag) => {
            // Find PID by tag
            if let Some(&pid) = tag_to_pid.get(&tag) {
                if all_pids.contains(&pid) {
                    // Keep only the filtered PID
                    all_pids.clear();
                    all_pids.insert(pid);
                } else {
                    // Tag exists but PID not in all_pids, return empty result
                    return Ok(Vec::new());
                }
            } else {
                // Tag not found, return empty result
                return Ok(Vec::new());
            }
        }
    }

    // Post-process collections into ProcessInfo structs
    let mut processes = Vec::new();

    // Process all PIDs
    for &pid in &all_pids {
        let log_path = namespace.get_log_path(pid);
        let tag = pid_to_tag.remove(&pid);
        let has_socket = socket_pids.contains(&pid);

        // Get start time from log file metadata
        let start_time = if let Ok(metadata) = std::fs::metadata(&log_path) {
            metadata.created().unwrap_or_else(|_| {
                metadata
                    .modified()
                    .unwrap_or_else(|_| std::time::SystemTime::now())
            })
        } else {
            std::time::SystemTime::now()
        };

        // Get process name (use tag if available, otherwise "process")
        let name = tag.clone().unwrap_or_else(|| "process".to_string());

        processes.push(ProcessInfoLocal {
            pid,
            name,
            start_time,
            tag,
            log_file: log_path,
            socket_path: if has_socket {
                Some(namespace.get_socket_path(pid))
            } else {
                None
            },
            reachable: reachable_pids.contains(&pid),
        });
    }

    // Sort processes by start time (oldest first)
    processes.sort_by(|a, b| a.start_time.cmp(&b.start_time));

    Ok(processes)
}
