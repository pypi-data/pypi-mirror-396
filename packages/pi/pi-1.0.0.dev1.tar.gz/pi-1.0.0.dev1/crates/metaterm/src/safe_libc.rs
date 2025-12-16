//! Safe wrappers around libc system calls for read, write, and select operations.
//!
//! This module provides safe wrappers around libc system calls that handle
//! interrupted signals (EINTR) properly and provide better error handling
//! than direct libc calls.

use std::io;
use std::mem::MaybeUninit;
use std::time::Duration;

/// A safe wrapper around libc::fd_set that provides Rust-idiomatic methods
/// for managing file descriptor sets used with select().
#[derive(Debug)]
pub struct FdSet {
    inner: libc::fd_set,
    max_fd: libc::c_int,
}

impl FdSet {
    /// Create a new, empty FdSet
    pub fn new() -> Self {
        let mut fd_set = MaybeUninit::<libc::fd_set>::uninit();
        unsafe { libc::FD_ZERO(fd_set.as_mut_ptr()) };
        Self {
            inner: unsafe { fd_set.assume_init() },
            max_fd: -1,
        }
    }

    /// Add a file descriptor to the set
    pub fn set(&mut self, fd: libc::c_int) {
        unsafe { libc::FD_SET(fd, &mut self.inner as *mut _) };
        if fd > self.max_fd {
            self.max_fd = fd;
        }
    }

    /// Remove a file descriptor from the set
    pub fn clear(&mut self, fd: libc::c_int) {
        unsafe { libc::FD_CLR(fd, &mut self.inner as *mut _) };
        // If we cleared the max_fd, we need to recalculate
        if fd == self.max_fd {
            self.recalculate_max_fd();
        }
    }

    /// Check if a file descriptor is in the set
    pub fn is_set(&self, fd: libc::c_int) -> bool {
        unsafe { libc::FD_ISSET(fd, &self.inner as *const _ as *mut _) }
    }

    /// Clear all file descriptors from the set
    pub fn clear_all(&mut self) {
        unsafe { libc::FD_ZERO(&mut self.inner as *mut _) };
        self.max_fd = -1;
    }

    /// Add multiple file descriptors to the set
    pub fn set_multiple(&mut self, fds: &[libc::c_int]) {
        for &fd in fds {
            self.set(fd);
        }
    }

    /// Remove multiple file descriptors from the set
    pub fn clear_multiple(&mut self, fds: &[libc::c_int]) {
        for &fd in fds {
            self.clear(fd);
        }
    }

    /// Get the maximum file descriptor in the set
    pub fn max_fd(&self) -> libc::c_int {
        self.max_fd
    }

    /// Check if the set is empty
    pub fn is_empty(&self) -> bool {
        self.max_fd == -1
    }

    /// Get the number of file descriptors in the set (approximate)
    /// Note: This is an approximation since fd_set doesn't store a count
    pub fn len(&self) -> usize {
        if self.is_empty() {
            0
        } else {
            // This is an approximation - we can't get exact count from fd_set
            (self.max_fd + 1) as usize
        }
    }

    /// Recalculate the maximum file descriptor after clearing
    fn recalculate_max_fd(&mut self) {
        self.max_fd = -1;
        // We can't efficiently iterate through fd_set, so we'll just reset to -1
        // The max_fd will be updated when new FDs are added
    }

    /// Get the raw fd_set pointer for use with libc::select
    ///
    /// # Safety
    /// This returns a raw pointer that should only be used with libc::select
    /// and only for the duration of the select call. The caller must ensure
    /// that the FdSet remains valid during the select operation.
    pub(crate) unsafe fn as_raw_ptr(&mut self) -> *mut libc::fd_set {
        &mut self.inner as *mut _
    }
}

impl Clone for FdSet {
    fn clone(&self) -> Self {
        Self {
            inner: self.inner,
            max_fd: self.max_fd,
        }
    }
}

impl Default for FdSet {
    fn default() -> Self {
        Self::new()
    }
}

/// Read data from a file descriptor into a buffer slice.
///
/// # Returns
/// * `Ok(usize)` - Number of bytes read
/// * `Err(io::Error)` - Error that occurred during read
pub fn read_slice(fd: libc::c_int, buf: &mut [u8]) -> io::Result<usize> {
    loop {
        let result = unsafe { libc::read(fd, buf.as_mut_ptr() as *mut libc::c_void, buf.len()) };

        if result >= 0 {
            return Ok(result as usize);
        }

        let err = io::Error::last_os_error();
        if err.kind() != io::ErrorKind::Interrupted {
            return Err(err);
        }
        // EINTR occurred, retry the read
    }
}

/// Write data from a buffer slice to a file descriptor.
///
/// # Returns
/// * `Ok(usize)` - Number of bytes written
/// * `Err(io::Error)` - Error that occurred during write
pub fn write_slice(fd: libc::c_int, buf: &[u8]) -> io::Result<usize> {
    loop {
        let result = unsafe { libc::write(fd, buf.as_ptr() as *const libc::c_void, buf.len()) };

        if result >= 0 {
            return Ok(result as usize);
        }

        let err = io::Error::last_os_error();
        if err.kind() != io::ErrorKind::Interrupted {
            return Err(err);
        }
        // EINTR occurred, retry the write
    }
}

/// High-level API: Wait for a single file descriptor to become ready for reading.
///
/// # Arguments
/// * `fd` - The file descriptor to wait for
/// * `timeout` - Optional timeout duration
///
/// # Returns
/// * `Ok(bool)` - True if the file descriptor is ready for reading
/// * `Err(io::Error)` - Error that occurred during select
pub fn wait_for_read(fd: libc::c_int, timeout: Option<Duration>) -> io::Result<bool> {
    wait_for_read_fdset(fd, timeout)
}

/// High-level API: Wait for a single file descriptor to become ready for writing.
///
/// # Arguments
/// * `fd` - The file descriptor to wait for
/// * `timeout` - Optional timeout duration
///
/// # Returns
/// * `Ok(bool)` - True if the file descriptor is ready for writing
/// * `Err(io::Error)` - Error that occurred during select
pub fn wait_for_write(fd: libc::c_int, timeout: Option<Duration>) -> io::Result<bool> {
    wait_for_write_fdset(fd, timeout)
}

/// High-level API: Write all data from a slice, retrying until complete or error.
///
/// # Arguments
/// * `fd` - The file descriptor to write to
/// * `buf` - Buffer slice containing data to write
///
/// # Returns
/// * `Ok(())` - All data was written successfully
/// * `Err(io::Error)` - Error that occurred during write
pub fn write_all(fd: libc::c_int, mut buf: &[u8]) -> io::Result<()> {
    while !buf.is_empty() {
        match write_slice(fd, buf) {
            Ok(0) => {
                return Err(io::Error::new(
                    io::ErrorKind::WriteZero,
                    "failed to write whole buffer",
                ));
            }
            Ok(n) => buf = &buf[n..],
            Err(e) => return Err(e),
        }
    }
    Ok(())
}

/// Safe wrapper around libc::select that handles EINTR properly using FdSet with Duration.
///
/// # Arguments
/// * `readfds` - Optional FdSet for read readiness
/// * `writefds` - Optional FdSet for write readiness  
/// * `exceptfds` - Optional FdSet for exceptional conditions
/// * `timeout` - Optional timeout duration
///
/// # Returns
/// * `Ok(i32)` - Number of file descriptors that are ready (>= 0)
/// * `Err(io::Error)` - Error that occurred during select
pub fn select(
    mut readfds: Option<&mut FdSet>,
    mut writefds: Option<&mut FdSet>,
    mut exceptfds: Option<&mut FdSet>,
    timeout: Option<Duration>,
) -> io::Result<i32> {
    // Calculate the maximum file descriptor from all sets
    let max_fd = [
        readfds.as_ref().map(|fds| fds.max_fd()).unwrap_or(-1),
        writefds.as_ref().map(|fds| fds.max_fd()).unwrap_or(-1),
        exceptfds.as_ref().map(|fds| fds.max_fd()).unwrap_or(-1),
    ]
    .iter()
    .filter(|&&fd| fd >= 0)
    .max()
    .copied()
    .unwrap_or(-1);

    if max_fd < 0 {
        return Ok(0);
    }

    // Convert timeout to timeval if provided
    let mut timeout_val = match timeout {
        Some(duration) => Some(libc::timeval {
            tv_sec: duration.as_secs() as libc::time_t,
            tv_usec: duration.subsec_micros() as libc::suseconds_t,
        }),
        None => None,
    };

    loop {
        let result = unsafe {
            libc::select(
                max_fd + 1,
                readfds
                    .as_mut()
                    .map(|fds| fds.as_raw_ptr())
                    .unwrap_or(std::ptr::null_mut()),
                writefds
                    .as_mut()
                    .map(|fds| fds.as_raw_ptr())
                    .unwrap_or(std::ptr::null_mut()),
                exceptfds
                    .as_mut()
                    .map(|fds| fds.as_raw_ptr())
                    .unwrap_or(std::ptr::null_mut()),
                timeout_val
                    .as_mut()
                    .map(|tv| tv as *mut _)
                    .unwrap_or(std::ptr::null_mut()),
            )
        };

        if result >= 0 {
            return Ok(result);
        }

        let err = io::Error::last_os_error();
        if err.kind() != io::ErrorKind::Interrupted {
            return Err(err);
        }
        // EINTR occurred, retry the select
    }
}

// ============================================================================
// Convenience functions for FdSet operations
// ============================================================================

/// Wait for a single file descriptor to become ready for reading using FdSet.
///
/// # Arguments
/// * `fd` - The file descriptor to wait for
/// * `timeout` - Optional timeout duration
///
/// # Returns
/// * `Ok(bool)` - True if the file descriptor is ready for reading
/// * `Err(io::Error)` - Error that occurred during select
pub fn wait_for_read_fdset(fd: libc::c_int, timeout: Option<Duration>) -> io::Result<bool> {
    let mut read_fds = FdSet::new();
    read_fds.set(fd);

    let result = select(Some(&mut read_fds), None, None, timeout)?;

    Ok(result > 0)
}

/// Wait for a single file descriptor to become ready for writing using FdSet.
///
/// # Arguments
/// * `fd` - The file descriptor to wait for
/// * `timeout` - Optional timeout duration
///
/// # Returns
/// * `Ok(bool)` - True if the file descriptor is ready for writing
/// * `Err(io::Error)` - Error that occurred during select
pub fn wait_for_write_fdset(fd: libc::c_int, timeout: Option<Duration>) -> io::Result<bool> {
    let mut write_fds = FdSet::new();
    write_fds.set(fd);

    let result = select(None, Some(&mut write_fds), None, timeout)?;

    Ok(result > 0)
}
