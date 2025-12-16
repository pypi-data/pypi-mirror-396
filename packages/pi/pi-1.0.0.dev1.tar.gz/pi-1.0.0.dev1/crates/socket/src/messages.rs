use serde::{Deserialize, Serialize};
use std::fmt::Debug;
use uuid::Uuid;

/// The well-known name of the router process.
pub const ROUTER_WELL_KNOWN_NAME: &str = "router";

/// Reexport for compatibility
pub use pishell_rpc_types::messages::{
    GenericMessage, GenericPayload, Message, MessageHeader, MessagePeer, MessageType,
    MessageTypeStatic, UnqualifiedMessage,
};

/// Ping payload
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PingMessage {
    pub message: String,
}

impl UnqualifiedMessage for PingMessage {}

/// Error message
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ErrorMessage {
    pub error: String,
    pub id: Option<Uuid>,
}

impl UnqualifiedMessage for ErrorMessage {}

/// Empty message for list servers
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ListServersMessage {}

impl UnqualifiedMessage for ListServersMessage {}

/// List servers response message
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ListServersResponseMessage {
    pub servers: Vec<Server>,
}

impl UnqualifiedMessage for ListServersResponseMessage {}

/// A server.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Server {
    pub id: Uuid,
    pub description: Option<String>,
    pub well_known_name: Option<String>,
}

/// Register message
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RegisterMessage {
    pub well_known_name: Option<String>,
    pub description: Option<String>,
}

impl UnqualifiedMessage for RegisterMessage {}

/// Register response message
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RegisterResponseMessage {
    pub client_id: Uuid,
}

impl UnqualifiedMessage for RegisterResponseMessage {}

/// Deregistered response message
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DeregisteredResponseMessage {
    pub well_known_name: String,
}

impl UnqualifiedMessage for DeregisteredResponseMessage {}
