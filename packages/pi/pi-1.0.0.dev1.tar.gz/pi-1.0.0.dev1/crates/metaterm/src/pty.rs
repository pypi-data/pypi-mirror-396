use crate::error::MetatermError;
use crate::terminal_size::TerminalSize;
use libc::termios;
use std::io;
use std::os::fd::RawFd;
use std::os::unix::process::CommandExt;
use std::process::Command;
use tracing::info;

/// Spawn a process in a PTY with the given size
pub fn spawn_in_pty(
    size: TerminalSize,
    mut cmd: Command,
    echo: bool,
) -> io::Result<(libc::pid_t, RawFd)> {
    info!("Spawning process in PTY: {:?}", cmd);

    // Create a new PTY
    let (master_fd, slave_fd) = create_pty(size)
        .map_err(|e| std::io::Error::new(e.kind(), format!("creating PTY failed: {}", e)))?;

    // If echo is disabled, set the termios to disable echo on the slave fd
    if !echo {
        unsafe {
            let mut termios: termios = std::mem::zeroed();

            #[cfg(target_os = "linux")]
            {
                use libc::{TCGETS, TCSETS};
                libc::ioctl(slave_fd, TCGETS, &termios);
                termios.c_lflag &= !(libc::ECHO);
                libc::ioctl(slave_fd, TCSETS, &termios);
            }
            #[cfg(target_os = "macos")]
            {
                // TODO: https://github.com/rust-lang/libc/pull/4736 needs to land
                const TIOCGETA: usize = 0x40487413;
                const TIOCSETA: usize = 0x80487414;
                libc::ioctl(slave_fd, TIOCGETA as _, &termios);
                termios.c_lflag &= !(libc::ECHO);
                libc::ioctl(slave_fd, TIOCSETA as _, &termios);
            }
        }
    }

    // Set the window size
    let winsize = size.winsize();
    unsafe {
        libc::ioctl(master_fd, libc::TIOCSWINSZ, &winsize);
    }

    // Set the controlling terminal
    unsafe {
        cmd.pre_exec(move || {
            let _ = libc::dup2(slave_fd, 0);
            let _ = libc::dup2(slave_fd, 1);
            let _ = libc::dup2(slave_fd, 2);

            // Create a new session
            if libc::setsid() == -1 {
                return Err(std::io::Error::last_os_error());
            }

            // Set the controlling terminal
            if libc::ioctl(0, libc::TIOCSCTTY.into(), 0) == -1 {
                return Err(std::io::Error::last_os_error());
            }

            Ok(())
        });
    }

    // Spawn the process
    let child = cmd.spawn().map_err(|e| {
        MetatermError::io(
            format!("Failed to spawn process {:?}", cmd.get_program()),
            e,
        )
    })?;

    // Close the slave fd in the parent
    unsafe {
        libc::close(slave_fd);
    }

    info!("Process spawned with master fd: {}", master_fd);
    Ok((child.id() as libc::pid_t, master_fd))
}

/// Create a new PTY pair
fn create_pty(size: TerminalSize) -> io::Result<(RawFd, RawFd)> {
    let mut master_fd: RawFd = -1;
    let mut slave_fd: RawFd = -1;
    let mut size = size.winsize();

    let result = unsafe {
        libc::openpty(
            &mut master_fd,
            &mut slave_fd,
            std::ptr::null_mut(),
            std::ptr::null_mut(),
            &mut size,
        )
    };

    if result == -1 {
        return Err(std::io::Error::last_os_error().into());
    }

    Ok((master_fd, slave_fd))
}
