# pishell-rpc-types

Generated Rust types, RPC interface traits, and client code for the Pi shell project.

## Overview

This crate provides automatically generated Rust types and trait definitions for RPC interfaces defined in JSON schemas. It combines the power of [typify](https://github.com/oxidecomputer/typify) for type generation with custom build-time trait generation and works together with procedural macros from `pishell-rpc-derive` for seamless RPC integration.

## Features

- **Automatic Type Generation**: Uses `typify` to generate Rust types from JSON schemas
- **Builder Pattern Support**: All generated types include builder patterns for easy construction
- **RPC Interface Traits**: Automatically generates sync traits for RPC interfaces
- **Client Code Generation**: Generates callback-based client code for each interface
- **Interface-Specific Modules**: Types, traits, and clients are organized into capitalized interface modules
- **Type Safety**: Full compile-time type checking for RPC method signatures

## Generated Code Structure

### Interface Module Organization

All generated code is organized into capitalized interface-specific modules:

```rust
// Types are available in interface modules (capitalized)
use pishell_rpc_types::Shell::TerminalInfo;
use pishell_rpc_types::Shell::TerminalInfoRequest;

// Service traits are in the same modules
use pishell_rpc_types::Shell::Service;

// Client structs are also available
use pishell_rpc_types::Shell::Client;

// Common error type is at the root
use pishell_rpc_types::RpcError;
```

### Types (via typify)

For each type definition in the schema's `$defs` section, typify generates:

- Rust struct with serde serialization support
- Builder pattern for construction
- Conversion traits and error handling

### RPC Service Traits (via build script)

For each interface in the schema's `interfaces` section, the build script generates:

- Sync trait with methods corresponding to RPC endpoints
- Proper type signatures using the generated request/response types
- Common `RpcError` enum for error handling

### Client Code (via build script)

For each interface, the build script generates:

- `Client` struct with callback-based methods for each RPC endpoint
- Generic `send_request` method for dynamic calls
- Proper error handling and message routing

## Usage Examples

### Server-side Implementation

```rust
use pishell_rpc_types::{Shell, RpcError};
use pishell_rpc_derive::rpc_interface;
use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct ShellService {
    shell: Arc<pishell_metaterm::Process>,
    terminal: Arc<pishell_metaterm::RealTerminal>,
}

// The rpc_interface macro generates registration code
#[rpc_interface(interface = "Shell")]
impl Shell::Service for ShellService {
    fn terminal_info(
        &self,
        _request: Shell::TerminalInfoRequest,
    ) -> Result<Shell::TerminalInfoResponse, RpcError> {
        let tinfo = self.terminal.terminal_info();
        let result = Shell::TerminalInfo::builder()
            .foreground_color(tinfo.foreground_color.clone())
            .background_color(tinfo.background_color.clone())
            .try_into()
            .map_err(|e| RpcError::Rpc(format!("Failed to build TerminalInfo: {}", e)))?;

        Ok(Shell::TerminalInfoResponse { result })
    }

    fn current_process_pid(
        &self,
        _request: Shell::CurrentProcessPidRequest,
    ) -> Result<Shell::CurrentProcessPidResponse, RpcError> {
        let result: i64 = self.shell.foreground_pid().unwrap_or(0).into();
        Ok(Shell::CurrentProcessPidResponse { result })
    }

    fn scrape(
        &self,
        _request: Shell::ScrapeRequest,
    ) -> Result<Shell::ScrapeResponse, RpcError> {
        let result = self.shell.virtual_pty().dump();
        Ok(Shell::ScrapeResponse { result })
    }
}

// Service Registration
pub fn setup_shell_service(
    shell: Arc<pishell_metaterm::Process>,
    terminal: Arc<pishell_metaterm::RealTerminal>,
    server: &pishell_socket::MessageServer,
) -> Result<Arc<ShellService>, Box<dyn std::error::Error>> {
    let service = Arc::new(ShellService { shell, terminal });

    // Using the generated registration method from rpc_interface macro
    ShellService::register_rpc_handlers(service.clone(), server);

    Ok(service)
}
```

### Client-side Usage

```rust
use pishell_rpc_types::{Shell, RpcError};
use pishell_socket::MessageServer;

pub fn use_shell_client() -> Result<(), Box<dyn std::error::Error>> {
    let message_server = MessageServer::new()?;
    let client = Shell::Client::new(message_server);

    // Call an RPC method using callback pattern
    let request = Shell::TerminalInfoRequest {};
    client.terminal_info(request, None, |result| {
        match result {
            Ok(response) => println!("Terminal info: {:?}", response.result),
            Err(e) => eprintln!("Error: {:?}", e),
        }
    })?;

    // Call with specific receiver instead of broadcast
    let request = Shell::CurrentProcessPidRequest {};
    client.current_process_pid(request, Some("shell_service"), |result| {
        match result {
            Ok(response) => println!("Current PID: {}", response.result),
            Err(e) => eprintln!("Error: {:?}", e),
        }
    })?;

    // Generic method is also available for dynamic calls
    let request = Shell::ScrapeRequest {};
    client.send_request("scrape", None, request, |result: Result<Shell::ScrapeResponse, RpcError>| {
        match result {
            Ok(response) => println!("Screen content: {}", response.result),
            Err(e) => eprintln!("Error: {:?}", e),
        }
    })?;

    Ok(())
}
```

## Current Interfaces

The crate currently supports the following RPC interfaces:

### Shell Interface

The `Shell` interface provides methods for interacting with terminal processes:

- `terminal_info()` - Get terminal color information
- `current_process_pid()` - Get the current foreground process PID
- `scrape()` - Get current screen content

## Key Benefits

### Unified Crate
- **Single Dependency**: Everything needed for RPC types in one crate
- **No Duplicate Schema Parsing**: Schema is parsed once during build
- **Consistent Module Structure**: Types, traits, and clients organized in matching interface modules

### Developer Experience
- **Non-blocking**: Client calls return immediately and use callbacks for responses
- **Type Safety**: All request/response types are validated at compile time
- **Schema Consistency**: Client and server are always in sync via shared schema
- **Simple APIs**: Clean callback-based interface for all RPC calls
- **Proper Error Handling**: Structured error types throughout

### Code Organization
- **Interface Modules**: Related types, traits, and clients grouped by interface (e.g., `Shell::`)
- **Capitalized Naming**: Interface modules use PascalCase (Shell, not shell)
- **Clear Separation**: Interface-specific organization prevents naming conflicts

## Message Naming Convention

RPC messages automatically use the "Interface:method" naming convention:

- Interface name comes from the schema: `Shell`
- Method name comes from the trait method: `terminal_info`
- Result: Message name becomes `"Shell:terminal_info"`

## Build Process

The crate uses a custom build script (`build.rs`) that:

1. Activates a Python virtual environment
2. Calls Python code to generate the JSON schema from protocol definitions
3. Uses `typify` to generate Rust types from the schema
4. Generates RPC interface traits by parsing the schema
5. Generates client code with callback-based methods
6. Outputs types, traits, and clients to the build directory
7. The procedural macros from `pishell-rpc-derive` use this generated code at compile time

To rebuild the generated code:

```bash
# Sync traits (default)
cargo build -p pishell-rpc-types
```

## Error Handling

The crate provides a comprehensive `RpcError` enum:

```rust
pub enum RpcError {
    #[error("Serialization error: {0}")]
    Serialization(String),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("RPC error: {0}")]
    Rpc(String),
}
```

## Schema Evolution

When the Python-side schema changes:

1. The build script automatically detects changes via `cargo:rerun-if-changed`
2. New types, traits, and clients are generated to match the updated schema
3. Existing implementations may need updates if method signatures change
4. The type system ensures compile-time safety during schema evolution

## Relationship with pishell-rpc-derive

This crate works together with `pishell-rpc-derive`:

- **pishell-rpc-types**: Provides the generated types, traits, and client code
- **pishell-rpc-derive**: Provides the `#[rpc_interface]` procedural macro for registration

Both crates are needed for a complete RPC implementation:

```toml
[dependencies]
pishell-rpc-types = { workspace = true }
pishell-rpc-derive = { workspace = true }  # For #[rpc_interface] macro
```

The procedural macro from `pishell-rpc-derive` can reference the exact generated types from this crate, ensuring perfect type safety and consistency.
