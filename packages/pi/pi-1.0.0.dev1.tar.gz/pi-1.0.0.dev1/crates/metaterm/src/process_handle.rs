use std::os::unix::process::ExitStatusExt;
use std::process::ExitStatus;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use tracing::{debug, error, warn};

#[derive(Debug, Clone)]
pub struct ProcessGroupHandle {
    pgid: libc::pid_t,
}

impl ProcessGroupHandle {
    pub fn new(pgid: libc::pid_t) -> Self {
        Self { pgid }
    }

    pub fn kill(&self, signal: libc::c_int) -> Result<(), std::io::Error> {
        let result = unsafe { libc::killpg(self.pgid, signal) };
        if result == -1 {
            let err = std::io::Error::last_os_error();
            error!(
                "Failed to send signal {} to PGID {}: {}",
                signal, self.pgid, err
            );
            return Err(err);
        }
        Ok(())
    }

    /// Terminate the process gracefully (SIGTERM)
    pub fn terminate(&self) -> Result<(), std::io::Error> {
        self.kill(libc::SIGTERM)
    }

    /// Force kill the process (SIGKILL)
    pub fn force_kill(&self) -> Result<(), std::io::Error> {
        self.kill(libc::SIGKILL)
    }
}

/// Shared state for the process handle
#[derive(Debug)]
struct ProcessHandleInner {
    /// The actual process ID
    pid: libc::pid_t,
    /// Cached exit status once the process has been waited on
    exit_status: Option<ExitStatus>,
    /// Flag to track if wait has been called
    wait_called: bool,
}

/// A wrapper around libc::pid_t that ensures proper process cleanup and prevents zombies
#[derive(Debug, Clone)]
pub struct ProcessHandle {
    inner: Arc<Mutex<ProcessHandleInner>>,
}

impl ProcessHandle {
    /// Create a new ProcessHandle for the given PID
    pub fn new(pid: libc::pid_t) -> Self {
        Self {
            inner: Arc::new(Mutex::new(ProcessHandleInner {
                pid,
                exit_status: None,
                wait_called: false,
            })),
        }
    }

    /// Get the process ID
    pub fn pid(&self) -> libc::pid_t {
        let inner = self.inner.lock().unwrap();
        inner.pid
    }

    /// Wait for the process to exit and return its exit status
    ///
    /// This can be called from any clone of the ProcessHandle. If one clone
    /// successfully waits, all subsequent calls will return the cached exit status.
    pub fn wait(&self) -> Result<ExitStatus, std::io::Error> {
        let mut inner = self.inner.lock().unwrap();

        // If we already have a cached exit status, return it
        if let Some(exit_status) = inner.exit_status {
            debug!(
                "Returning cached exit status for PID {}: {:?}",
                inner.pid, exit_status
            );
            return Ok(exit_status);
        }

        // If wait has already been called but we don't have a status yet,
        // it means another thread is currently waiting. We'll wait for the result.
        if inner.wait_called {
            drop(inner); // Release the lock while we wait

            // Poll until we get the exit status
            loop {
                thread::sleep(Duration::from_millis(10));
                let inner = self.inner.lock().unwrap();
                if let Some(exit_status) = inner.exit_status {
                    debug!(
                        "Got cached exit status after waiting for PID {}: {:?}",
                        inner.pid, exit_status
                    );
                    return Ok(exit_status);
                }
            }
        }

        // Mark that wait has been called
        inner.wait_called = true;
        let pid = inner.pid;
        drop(inner); // Release the lock while we wait

        debug!("Calling waitpid for PID {}", pid);

        // Actually wait for the process
        let mut status: libc::c_int = 0;
        let result = unsafe { libc::waitpid(pid, &mut status, 0) };

        if result == -1 {
            let err = std::io::Error::last_os_error();
            error!("waitpid failed for PID {}: {}", pid, err);
            return Err(err);
        }

        // Convert the raw status to ExitStatus
        let exit_status = ExitStatus::from_raw(status);
        debug!("Process {} exited with status: {:?}", pid, exit_status);

        // Cache the exit status
        let mut inner = self.inner.lock().unwrap();
        inner.exit_status = Some(exit_status);

        Ok(exit_status)
    }

    /// Try to wait for the process without blocking
    ///
    /// Returns Ok(Some(exit_status)) if the process has exited,
    /// Ok(None) if the process is still running,
    /// Err(error) if there was an error.
    pub fn try_wait(&self) -> Result<Option<ExitStatus>, std::io::Error> {
        let mut inner = self.inner.lock().unwrap();

        // If we already have a cached exit status, return it
        if let Some(exit_status) = inner.exit_status {
            debug!(
                "Returning cached exit status for PID {}: {:?}",
                inner.pid, exit_status
            );
            return Ok(Some(exit_status));
        }

        let pid = inner.pid;
        debug!("Calling waitpid with WNOHANG for PID {}", pid);

        // Try to wait without blocking
        let mut status: libc::c_int = 0;
        let result = unsafe { libc::waitpid(pid, &mut status, libc::WNOHANG) };

        if result == -1 {
            let err = std::io::Error::last_os_error();
            error!("waitpid failed for PID {}: {}", pid, err);
            return Err(err);
        }

        if result == 0 {
            // Process is still running
            debug!("Process {} is still running", pid);
            return Ok(None);
        }

        // Process has exited
        let exit_status = ExitStatus::from_raw(status);
        debug!("Process {} exited with status: {:?}", pid, exit_status);

        // Cache the exit status
        inner.exit_status = Some(exit_status);
        inner.wait_called = true;

        Ok(Some(exit_status))
    }

    /// Check if the process is still running
    pub fn is_running(&self) -> bool {
        match self.try_wait() {
            Ok(Some(_)) => false, // Process has exited
            Ok(None) => true,     // Process is still running
            Err(_) => false,      // Error occurred, assume not running
        }
    }

    /// Send a signal to the process
    pub fn kill(&self, signal: libc::c_int) -> Result<(), std::io::Error> {
        let inner = self.inner.lock().unwrap();
        let pid = inner.pid;
        drop(inner);

        debug!("Sending signal {} to PID {}", signal, pid);

        let result = unsafe { libc::kill(pid, signal) };

        if result == -1 {
            let err = std::io::Error::last_os_error();
            error!("Failed to send signal {} to PID {}: {}", signal, pid, err);
            return Err(err);
        }

        Ok(())
    }

    /// Terminate the process gracefully (SIGTERM)
    pub fn terminate(&self) -> Result<(), std::io::Error> {
        self.kill(libc::SIGTERM)
    }

    /// Force kill the process (SIGKILL)
    pub fn force_kill(&self) -> Result<(), std::io::Error> {
        self.kill(libc::SIGKILL)
    }
}

impl Drop for ProcessHandle {
    fn drop(&mut self) {
        // Check if this is the last reference to the inner data
        if Arc::strong_count(&self.inner) == 1 {
            let inner = self.inner.lock().unwrap();
            let pid = inner.pid;
            let has_exit_status = inner.exit_status.is_some();
            drop(inner);

            if !has_exit_status {
                // This is the last ProcessHandle and we haven't waited for the process yet.
                // We need to wait to prevent it from becoming a zombie.
                warn!(
                    "Last ProcessHandle dropped without waiting for PID {}, cleaning up to prevent zombie",
                    pid
                );

                // Try to wait for the process in a non-blocking way first
                match self.try_wait() {
                    Ok(Some(exit_status)) => {
                        debug!("Cleaned up PID {} with exit status: {:?}", pid, exit_status);
                    }
                    Ok(None) => {
                        // Process is still running, we'll need to wait for it
                        warn!(
                            "PID {} is still running during cleanup, waiting for it to exit",
                            pid
                        );
                        if let Err(e) = self.wait() {
                            error!("Failed to wait for PID {} during cleanup: {}", pid, e);
                        }
                    }
                    Err(e) => {
                        // The process might already be dead or we don't have permission
                        debug!(
                            "Could not check status of PID {} during cleanup: {}",
                            pid, e
                        );
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::process::Command;
    use std::thread;

    #[test]
    fn test_process_handle_basic() {
        // Spawn a simple process that exits quickly
        let child = Command::new("true").spawn().unwrap();
        let pid = child.id() as libc::pid_t;

        // Don't wait on the child, let ProcessHandle manage it
        std::mem::forget(child);

        let handle = ProcessHandle::new(pid);

        // Wait for the process
        let exit_status = handle.wait().unwrap();
        assert!(exit_status.success());

        // Subsequent waits should return the same status
        let exit_status2 = handle.wait().unwrap();
        assert_eq!(exit_status.code(), exit_status2.code());
    }

    #[test]
    fn test_process_handle_multiple_clones() {
        // Spawn a process that sleeps for a short time
        let child = Command::new("sleep").arg("1").spawn().unwrap();
        let pid = child.id() as libc::pid_t;

        // Don't wait on the child, let ProcessHandle manage it
        std::mem::forget(child);

        let handle1 = ProcessHandle::new(pid);
        let handle2 = handle1.clone();
        let handle3 = handle1.clone();

        // All clones should be able to wait and get the same result
        let exit_status1 = handle1.wait().unwrap();
        let exit_status2 = handle2.wait().unwrap();
        let exit_status3 = handle3.wait().unwrap();

        assert_eq!(exit_status1.code(), exit_status2.code());
        assert_eq!(exit_status2.code(), exit_status3.code());
    }

    #[test]
    fn test_process_handle_concurrent_wait() {
        // Spawn a process that sleeps for a short time
        let child = Command::new("sleep").arg("1").spawn().unwrap();
        let pid = child.id() as libc::pid_t;

        // Don't wait on the child, let ProcessHandle manage it
        std::mem::forget(child);

        let handle = ProcessHandle::new(pid);
        let handle1 = handle.clone();
        let handle2 = handle.clone();

        // Start two threads that both try to wait
        let thread1 = {
            let handle = handle1;
            thread::spawn(move || handle.wait())
        };

        let thread2 = {
            let handle = handle2;
            thread::spawn(move || handle.wait())
        };

        // Both should succeed and return the same result
        let result1 = thread1.join().unwrap().unwrap();
        let result2 = thread2.join().unwrap().unwrap();

        assert_eq!(result1.code(), result2.code());
    }
}
