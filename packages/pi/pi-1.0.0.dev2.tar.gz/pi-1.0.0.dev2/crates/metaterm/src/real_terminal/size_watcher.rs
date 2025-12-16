// nix = { version = "0.29", default-features = false, features = ["signal","ioctl","term"] }

use nix::libc;
use nix::sys::signal::{SaFlags, SigAction, SigHandler, SigSet, Signal, sigaction};
use std::io;
use std::mem;
use std::os::fd::RawFd;
use std::sync::atomic::{AtomicI32, Ordering};
use std::sync::{Once, OnceLock};
use std::thread;

use crate::safe_libc;
use crate::terminal_size::TerminalSize;
use pishell_eventbus::{DISPATCHER, EventListeners, EventSource, ListenerHandle};

// -------- Public API --------

/// Optionally select which fd to query for the size (e.g., a PTY slave).
/// Call before your first `subscribe()`.
pub fn set_query_fd(fd: RawFd) {
    QUERY_FD.store(fd as i32, Ordering::Relaxed);
}

/// Installs the SIGWINCH handler and background thread (idempotent).
pub fn install() {
    init_once();
}

/// Subscribe to resize events through the DISPATCHER system.
/// Returns a ListenerHandle that can be used to unsubscribe.
pub fn subscribe<F>(mut callback: F) -> ListenerHandle
where
    F: FnMut(()) + Send + 'static,
{
    init_once();

    callback(());

    // Register with the DISPATCHER
    get_event_listeners().subscribe(callback)
}

static EVENT: OnceLock<(EventSource<()>, EventListeners<()>)> = OnceLock::new();

fn get_event_source() -> &'static EventSource<()> {
    &EVENT.get_or_init(|| DISPATCHER.tear_off()).0
}

fn get_event_listeners() -> &'static EventListeners<()> {
    &EVENT.get_or_init(|| DISPATCHER.tear_off()).1
}

// -------- Internals --------

static INIT: Once = Once::new();

// Self-pipe (signal-safe nudge from handler -> monitor thread)
static PIPE_RD: AtomicI32 = AtomicI32::new(-1);
static PIPE_WR: AtomicI32 = AtomicI32::new(-1);

// Which fd to query via TIOCGWINSZ (default: STDOUT_FILENO = 1)
static QUERY_FD: AtomicI32 = AtomicI32::new(1);

fn init_once() {
    INIT.call_once(|| {
        // Self-pipe
        let mut fds = [0i32; 2];
        unsafe {
            if libc::pipe(fds.as_mut_ptr()) != 0 {
                panic!("pipe() failed: {}", io::Error::last_os_error());
            }
            // non-blocking write end avoids handler stalls; read end can block
            let flags_w = libc::fcntl(fds[1], libc::F_GETFL);
            libc::fcntl(fds[1], libc::F_SETFL, flags_w | libc::O_NONBLOCK);
        }
        PIPE_RD.store(fds[0], Ordering::Relaxed);
        PIPE_WR.store(fds[1], Ordering::Relaxed);

        // SIGWINCH handler (async-signal-safe)
        unsafe {
            let sa = SigAction::new(
                SigHandler::Handler(sigwinch_handler),
                SaFlags::SA_RESTART,
                SigSet::empty(),
            );
            sigaction(Signal::SIGWINCH, &sa).expect("sigaction(SIGWINCH)");
        }

        // Monitor: wait for nudges, query size, send events through DISPATCHER.
        thread::Builder::new()
            .name("size-monitor".into())
            .spawn(monitor_loop)
            .expect("spawn size-monitor");
    });
}

extern "C" fn sigwinch_handler(_: i32) {
    // One byte; ignore EAGAIN. Spurious writes are fine.
    let b: [u8; 1] = [1];
    let wr = PIPE_WR.load(Ordering::Relaxed);
    if wr >= 0 {
        let _ = safe_libc::write_slice(wr, &b);
    }
}

fn monitor_loop() {
    let rd = PIPE_RD.load(Ordering::Relaxed);
    let mut buf = [0u8; 256];

    loop {
        // Block until at least one byte arrives; EINTR is handled automatically
        match safe_libc::read_slice(rd, &mut buf) {
            Ok(0) => return, // pipe closed
            Ok(_) => { /* got data, continue processing */ }
            Err(_) => return, // error occurred
        }

        get_event_source().send(());
    }
}

pub fn query_winsize() -> io::Result<TerminalSize> {
    let fd = QUERY_FD.load(Ordering::Relaxed);
    if fd < 0 {
        return Err(io::Error::new(io::ErrorKind::Other, "no query fd"));
    }
    let mut ws: libc::winsize = unsafe { mem::zeroed() };
    let rc = unsafe {
        libc::ioctl(
            fd,
            libc::TIOCGWINSZ,
            &mut ws as *mut libc::winsize as *mut libc::c_void,
        )
    };
    if rc == -1 {
        return Err(io::Error::last_os_error());
    }
    Ok(TerminalSize::from_winsize(ws))
}
