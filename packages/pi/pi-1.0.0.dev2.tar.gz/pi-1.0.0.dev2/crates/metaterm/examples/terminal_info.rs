use pishell_metaterm::{TerminalGuard, TerminalInfo, terminal_info};
use tracing::{debug, info};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing with environment-based configuration
    let _ = tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .try_init();

    info!("Attempting to query real terminal information...");
    debug!("This will send escape sequences to query terminal capabilities");
    debug!("Watch for debug messages showing escape sequences being sent");

    // Create a terminal guard to ensure raw mode
    debug!("Creating terminal guard for raw mode...");
    let info = {
        let _guard = TerminalGuard::new()?;
        terminal_info()
    };
    debug!("Terminal is now in raw mode");

    // Try to query real terminal information
    debug!("Attempting to query terminal info directly...");
    match info {
        Ok(terminal_info) => {
            debug!("Successfully queried terminal information");
            info!(
                "Terminal querying completed - some values may be unset if terminal doesn't support certain queries"
            );
            {
                let terminal_info: &TerminalInfo = &terminal_info;
                // Print terminal information in verbose debug format
                println!("Terminal Information (Real Query Results):");
                println!("{:#?}", terminal_info);
            };
        }
        Err(e) => {
            info!("Failed to query real terminal info: {}", e);
            info!("This example requires a real terminal to work properly.");
            info!("Try running this example in a terminal emulator.");
            return Err(e.into());
        }
    }

    Ok(())
}
