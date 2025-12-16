//! Generated Rust types and RPC interface traits for the Pi shell project.
//!
//! This crate provides automatically generated Rust types and trait definitions for RPC interfaces
//! defined in JSON schemas. It combines the power of [typify](https://github.com/oxidecomputer/typify)
//! for type generation with custom build-time trait generation for RPC interfaces.
//!
//! ## Features
//!
//! - **Automatic Type Generation**: Uses `typify` to generate Rust types from JSON schemas
//! - **Builder Pattern Support**: All generated types include builder patterns for easy construction
//! - **RPC Interface Traits**: Automatically generates sync or async traits for RPC interfaces
//! - **Procedural Macros**: Re-exports `#[rpc_interface]` macro for automatic RPC registration
//! - **Nested Module Structure**: Types and traits are organized into interface-specific modules
//! - **Type Safety**: Full compile-time type checking for RPC method signatures
//! - **Error Handling**: Structured error types with `thiserror` integration
//! - **Flexible Async Support**: Optional async/await support with `async-trait` (off by default)
//! - **Clean API**: Raw typify-generated types are hidden; only organized module aliases are exported
//!
//! ## Generated Module Structure
//!
//! The crate generates interface-specific modules (capitalized) containing both types and traits:
//!
//! ```rust,ignore
//! // Types are available in interface-specific modules with clean names
//! use pishell_rpc_types::Shell::TerminalInfo;
//! use pishell_rpc_types::Captive::CommandRequest;
//!
//! // Traits are in the same modules as `Service`
//! use pishell_rpc_types::Shell::Service as ShellService;
//! use pishell_rpc_types::Captive::Service as CaptiveService;
//!
//! // Client types are also available
//! use pishell_rpc_types::Shell::Client as ShellClient;
//! use pishell_rpc_types::Captive::Client as CaptiveClient;
//! ```
//!
//! ## Implementation Example
//!
//! ### Server-side Service Implementation
//!
//! Implement the generated `Service` trait for your RPC handlers:
//!
//! ```rust,ignore
//! use pishell_rpc_types::{Shell, RpcError};
//!
//! #[derive(Debug, Clone)]
//! pub struct MyShellService;
//!
//! impl Shell::Service for MyShellService {
//!     fn terminal_info(
//!         &self,
//!         request: Shell::TerminalInfoRequest,
//!     ) -> Result<Shell::TerminalInfoResponse, RpcError> {
//!         // Implementation here
//!         let info = Shell::TerminalInfo::builder()
//!             .cols(80)
//!             .rows(24)
//!             .build();
//!         Ok(Shell::TerminalInfoResponse::builder()
//!             .terminal_info(info)
//!             .build())
//!     }
//! }
//! ```
//!
//! ### Client-side Usage
//!
//! Use the generated `Client` for making RPC calls with callbacks:
//!
//! ```rust,ignore
//! use pishell_rpc_types::{Shell, RpcError};
//! use pishell_socket::MessageServer;
//!
//! let client = Shell::Client::new(message_server);
//!
//! // Callback-based RPC calls
//! let request = Shell::TerminalInfoRequest::builder().build();
//! client.terminal_info(request, None, |result| {
//!     match result {
//!         Ok(response) => println!("Got terminal info: {:?}", response.terminal_info),
//!         Err(e) => eprintln!("RPC error: {:?}", e),
//!     }
//! })?;
//! ```

// Base message definitions and traits
pub mod messages;

// Include generated types, traits, and clients
include!(concat!(env!("OUT_DIR"), "/rpc_types.rs"));

// Re-export the rpc_interface macro from the rpc_derive crate
pub use pishell_rpc_derive::rpc_interface;
