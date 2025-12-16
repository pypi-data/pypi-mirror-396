use std::path::PathBuf;

const CAPTIVE_DIR: &str = "pishell-captive";

/// Get the platform-specific run directory for PID files and sockets
pub fn get_run_dir() -> PathBuf {
    // Try to get the system run directory first
    if let Some(run_dir) = dirs::runtime_dir() {
        run_dir.join(CAPTIVE_DIR)
    } else {
        // Fallback to temp directory if runtime directory is not available
        std::env::temp_dir().join(CAPTIVE_DIR)
    }
}

/// Get the platform-specific cache directory for log files
pub fn get_cache_dir() -> PathBuf {
    if let Some(cache_dir) = dirs::cache_dir() {
        cache_dir.join(CAPTIVE_DIR)
    } else {
        // Fallback to temp directory if cache directory is not available
        std::env::temp_dir().join(CAPTIVE_DIR)
    }
}

/// Ensure the given directory exists, creating it if necessary
pub fn ensure_dir_exists(path: &PathBuf) -> Result<(), std::io::Error> {
    if !path.exists() {
        std::fs::create_dir_all(path)?;
    }
    Ok(())
}
