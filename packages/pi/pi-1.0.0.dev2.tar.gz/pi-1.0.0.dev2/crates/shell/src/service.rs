use pishell_eventbus::EventSource;
use pishell_rpc_types::{RpcError, Shell, Shell::Service, rpc_interface};
use std::sync::{Arc, Mutex};
use tracing::info;

#[derive(Clone)]
pub struct ShellService {
    shell: Arc<pishell_metaterm::Process>,
    terminal_info: pishell_metaterm::TerminalInfo,
    sidebar_close_event: Arc<Mutex<Option<EventSource<()>>>>,
}

impl ShellService {
    pub fn new(
        shell: Arc<pishell_metaterm::Process>,
        terminal_info: pishell_metaterm::TerminalInfo,
    ) -> Self {
        Self {
            shell,
            terminal_info,
            sidebar_close_event: Arc::new(Mutex::new(None)),
        }
    }

    pub fn set_sidebar_close_event(&self, event: EventSource<()>) {
        *self.sidebar_close_event.lock().unwrap() = Some(event);
    }
}

/// RPC interface implementation for terminal info service
#[rpc_interface(interface = "Shell")]
impl Shell::Service for ShellService {
    fn pi_info(&self, _request: Shell::PiInfoRequest) -> Result<Shell::PiInfoResponse, RpcError> {
        let path = std::env::current_exe()
            .map_err(|e| RpcError::Rpc(format!("could not determine PI exe path: {}", e)))?
            .to_string_lossy()
            .to_string();
        Ok(Shell::PiInfoResponse {
            result: Shell::PiInfo { path },
        })
    }

    fn current_process_pid(
        &self,
        request: Shell::CurrentProcessPidRequest,
    ) -> Result<Shell::CurrentProcessPidResponse, RpcError> {
        info!("Received current process message: {:?}", request);
        let result: i64 = self.shell.foreground_pid().unwrap_or(0).into();
        Ok(Shell::CurrentProcessPidResponse { result })
    }

    fn scrape(&self, request: Shell::ScrapeRequest) -> Result<Shell::ScrapeResponse, RpcError> {
        info!("Received scrape request: {:?}", request);
        let result = self.shell.virtual_pty().dump();
        Ok(Shell::ScrapeResponse { result })
    }

    fn terminal_info(
        &self,
        _request: Shell::TerminalInfoRequest,
    ) -> Result<Shell::TerminalInfoResponse, RpcError> {
        info!("Processing terminal info request");
        // Using the typify-generated builder pattern
        let result = Shell::TerminalInfo::builder()
            .foreground_color(self.terminal_info.foreground_color.clone())
            .background_color(self.terminal_info.background_color.clone())
            .cursor_blinking(self.terminal_info.cursor_blinking)
            .try_into()
            .map_err(|e| RpcError::Rpc(format!("Failed to build TerminalInfo: {}", e)))?;

        info!("Returning terminal info: {:?}", result);
        Ok(Shell::TerminalInfoResponse { result })
    }

    fn process_info(
        &self,
        _request: Shell::ProcessInfoRequest,
    ) -> Result<Shell::ProcessInfoResponse, RpcError> {
        info!("Processing process info request");

        // Get the foreground process PID
        let pid = self.shell.foreground_pid().unwrap_or(0);
        if pid == 0 {
            return Err(RpcError::Rpc("No foreground process found".to_string()));
        }

        info!("Getting process info for PID: {}", pid);
        let process_info = pishell_psutil::get_process_info(pid)
            .ok_or_else(|| RpcError::Rpc(format!("Process with PID {} not found", pid)))?;

        let (kind, ident) = if let Some(exe) = &process_info.exe
            && let Ok(shell_type) = crate::babelshell::Shell::try_from(exe)
        {
            (
                Shell::ProcessKind::Shell,
                Some(shell_type.shell_name().to_string()),
            )
        } else {
            (Shell::ProcessKind::Unknown, None)
        };

        let response_info = Shell::ProcessInfo::builder()
            .pid(pid as i64)
            .parent_pid(process_info.parent_pid.map(|i| i as i64))
            .name(process_info.name)
            .kind(kind)
            .identification(ident)
            .uid(process_info.uid.map(|u| u as i64))
            .euid(process_info.euid.map(|u| u as i64))
            .gid(process_info.gid.map(|u| u as i64))
            .egid(process_info.egid.map(|u| u as i64))
            .exe(process_info.exe.map(|p| p.to_string_lossy().to_string()))
            .cwd(process_info.cwd.map(|p| p.to_string_lossy().to_string()))
            .argv(process_info.argv)
            .env(process_info.env)
            .try_into()
            .map_err(|e| RpcError::Rpc(format!("Failed to build ProcessInfo: {}", e)))?;

        info!(
            "Returning process info for PID {}: {:?}",
            pid, response_info
        );
        Ok(Shell::ProcessInfoResponse {
            result: response_info,
        })
    }

    fn command_history(
        &self,
        request: Shell::CommandHistoryRequest,
    ) -> Result<Shell::CommandHistoryResponse, RpcError> {
        info!("Processing command history request for n={}", request.n);

        let n = request.n as usize;
        let mut result = Vec::new();
        for cmd_hist in self.shell.virtual_pty().command_history(n) {
            let rpc_command_history = Shell::CommandHistory::builder()
                .command_number(cmd_hist.command_number as i64)
                .command(cmd_hist.command.clone())
                .exit_code(cmd_hist.exit_code.map(|code| code as i64))
                .start_time(cmd_hist.start_time.and_then(|t| {
                    t.duration_since(std::time::UNIX_EPOCH).ok().and_then(|d| {
                        chrono::DateTime::from_timestamp(d.as_secs() as i64, d.subsec_nanos())
                    })
                }))
                .end_time(cmd_hist.end_time.and_then(|t| {
                    t.duration_since(std::time::UNIX_EPOCH).ok().and_then(|d| {
                        chrono::DateTime::from_timestamp(d.as_secs() as i64, d.subsec_nanos())
                    })
                }))
                .try_into()
                .map_err(|e| RpcError::Rpc(format!("Failed to build CommandHistory: {}", e)))?;

            result.push(rpc_command_history);
        }

        info!("Returning {} command history entries", result.len());
        Ok(Shell::CommandHistoryResponse { result })
    }

    fn command_output(
        &self,
        request: Shell::CommandOutputRequest,
    ) -> Result<Shell::CommandOutputResponse, RpcError> {
        info!(
            "Processing command output request for command_number={}",
            request.command_number
        );

        let result = usize::try_from(request.command_number).map_or(None, |n| {
            self.shell.virtual_pty().command_output_by_number(n)
        });

        info!(
            "Returning command output for command {}: {}",
            request.command_number,
            if result.is_some() {
                "found"
            } else {
                "not found"
            }
        );

        Ok(Shell::CommandOutputResponse { result })
    }

    fn close_sidebar(
        &self,
        _: Shell::CloseSidebarRequest,
    ) -> Result<Shell::CloseSidebarResponse, RpcError> {
        info!("Processing close sidebar request");

        if let Some(event) = self.sidebar_close_event.lock().unwrap().as_ref() {
            event.send(());
            info!("Sidebar close event sent");
            Ok(Shell::CloseSidebarResponse { result: () })
        } else {
            Err(RpcError::Rpc("Sidebar is not currently open".to_string()))
        }
    }
}

pub fn setup(
    shell: Arc<pishell_metaterm::Process>,
    terminal_info: pishell_metaterm::TerminalInfo,
    server: &pishell_socket::MessageServer,
) -> Result<Arc<ShellService>, Box<dyn std::error::Error>> {
    // Create service instance
    let service = Arc::new(ShellService::new(shell, terminal_info));

    // Register RPC handlers using the procedural macro
    ShellService::register_rpc_handlers(service.clone(), server);
    info!("Terminal 'shell' service registered successfully");
    Ok(service)
}
