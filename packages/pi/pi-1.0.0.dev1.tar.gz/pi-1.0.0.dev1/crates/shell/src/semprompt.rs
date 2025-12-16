//! Semantic prompt a.k.a. shell integration a.k.a OSC 133

use std::collections::HashSet;
use std::io;
use std::path::Path;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use tracing::{debug, info};

use pishell_metaterm::{
    OutputEvent, ProcessSetupBuilder, Terminal, TerminalSize, osc133::Osc133Type,
};

use crate::babelshell::Shell;

/// Result of OSC 133 probing
#[derive(Debug, Clone)]
pub struct Osc133ProbeResult {
    /// Which specific sequences were detected if any
    pub detected_sequences: HashSet<Osc133Type>,
    /// How long the probe took
    pub probe_duration: Duration,
}

/// Configuration for OSC 133 probing
#[derive(Debug, Clone)]
pub struct Osc133ProbeConfig {
    /// Maximum time to wait for sequences
    pub timeout: Duration,
}

impl Default for Osc133ProbeConfig {
    fn default() -> Self {
        Self {
            timeout: Duration::from_millis(400),
        }
    }
}

/// Probe a shell for OSC 133 support
pub fn probe_shell(shell: Shell, shell_path: &Path) -> io::Result<Osc133ProbeResult> {
    probe_shell_with_config(shell, shell_path, &Osc133ProbeConfig::default())
}

/// Probe a shell for OSC 133 support with custom configuration
pub fn probe_shell_with_config(
    shell: Shell,
    shell_path: &Path,
    config: &Osc133ProbeConfig,
) -> io::Result<Osc133ProbeResult> {
    let start_time = Instant::now();
    info!("Starting OSC 133 probe for shell: {}", shell.shell_name());

    let terminal = Terminal::new();

    let (i_args, i_env) = shell.interactive_mode();
    let (s_args, s_env) = shell.scratch_mode();
    let process_setup = ProcessSetupBuilder::new()
        .with_id("shell-osc133-probe")
        .with_command(shell_path.to_string_lossy().to_string())
        .with_args(i_args.iter().chain(s_args).map(|s| s.to_string()).collect())
        .with_echo(false)
        .with_env(
            i_env
                .iter()
                .chain(s_env)
                .map(|(k, v)| (k.to_string(), v.to_string()))
                .collect(),
        )
        .build();

    // Create the probe process in virtual mode (no direct I/O)
    let probe_process = terminal.create_process(process_setup, TerminalSize::default())?;

    // Set up OSC 133 sequence detection
    let detected_sequences = Arc::new(Mutex::new(HashSet::new()));

    // Subscribe to output events to catch OSC 133 sequences
    let got_output = Arc::new(AtomicBool::new(false));
    let _listener = probe_process.on_event({
        let sequences = detected_sequences.clone();
        let got_output = got_output.clone();
        move |event| match event {
            OutputEvent::Prompt(osc133_sequence) => {
                debug!(
                    "Detected OSC 133 sequence: {:?}",
                    osc133_sequence.sequence_type
                );
                if let Ok(mut detected) = sequences.lock() {
                    detected.insert(osc133_sequence.sequence_type);
                }
            }
            OutputEvent::FirstByte => {
                got_output.store(true, Ordering::Relaxed);
            }
            _ => (),
        }
    });

    // Send exit command to trigger prompt sequences and exit
    let test_command = "exit\n";
    debug!("Sending exit command to probe shell");
    probe_process.write_stdin(test_command.as_bytes());

    // Wait for the process to exit with timeout using channels
    let (sender, receiver) = std::sync::mpsc::channel();
    let wait_process = probe_process.clone();

    std::thread::spawn(move || {
        let result = wait_process.wait().map_err(|e| e.to_string());
        let _ = sender.send(result);
    });

    // Wait for completion or timeout
    match receiver.recv_timeout(config.timeout) {
        Ok(Ok(status)) if status.success() => {
            if !got_output.load(Ordering::Relaxed) {
                return Err(io::Error::new(
                    io::ErrorKind::Other,
                    format!("Shell process {:?} exited without output", shell_path),
                ));
            }
            debug!("Shell process exited successfully");
        }
        Ok(Ok(status)) => {
            debug!(
                "OSC 133 probe: Shell process exited with status: {}",
                status
            );
            return Err(io::Error::new(
                io::ErrorKind::Other,
                format!(
                    "Shell process {:?} exited with status: {}",
                    shell_path, status
                ),
            ));
        }
        Ok(Err(e)) => {
            debug!("OSC 133 probe: Shell process wait failed: {}", e);
        }
        Err(_) => {
            debug!("OSC 133 probe: Timeout reached, killing process");
        }
    }
    probe_process.kill();

    terminal.shutdown();

    let probe_duration = start_time.elapsed();
    let detected_sequences = detected_sequences.lock().unwrap().clone();

    let result = Osc133ProbeResult {
        detected_sequences,
        probe_duration,
    };

    info!(
        "OSC 133 probe completed for {}: supported={}, sequences={:?}, duration={:?}",
        shell.shell_name(),
        !result.detected_sequences.is_empty(),
        result.detected_sequences,
        result.probe_duration
    );

    Ok(result)
}
