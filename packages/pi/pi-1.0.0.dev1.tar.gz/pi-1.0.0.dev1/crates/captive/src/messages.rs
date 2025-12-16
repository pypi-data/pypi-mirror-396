use serde::{Deserialize, Serialize};

use pishell_socket::messages::UnqualifiedMessage;

#[derive(Clone, Copy, Debug, Serialize, Deserialize, Eq, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum CaptiveState {
    Ready = 0,
    Active = 1,
    IdleNewline = 2,
    IdlePromptish = 3,
    IdleOther = 4,
    Exit = 5,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CaptiveMessage {
    pub state: CaptiveState,
    pub exit_code: Option<i32>,
}

impl UnqualifiedMessage for CaptiveMessage {}

/// Captive command message for communicating with captive processes
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CaptiveCommandMessage {
    pub command: String,
    pub data: Option<String>,
}

impl UnqualifiedMessage for CaptiveCommandMessage {}

/// Captive response message for responses from captive processes
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CaptiveResponseMessage {
    pub success: bool,
    pub message: String,
    pub data: Option<String>,
}

impl UnqualifiedMessage for CaptiveResponseMessage {}

/// Process information for listing and management
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ProcessListMessage {
    pub processes: Vec<ProcessInfo>,
}

impl UnqualifiedMessage for ProcessListMessage {}

/// Process information structure
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ProcessInfo {
    pub pid: u32,
    pub tag: String,
    pub cmd: String,
    pub args: Vec<String>,
    pub status: String,
    pub running_duration: u64, // seconds
    pub idle_duration: u64,    // seconds
    pub timeout: u64,          // seconds
    pub namespace: String,
}

impl UnqualifiedMessage for ProcessInfo {}

/// Timeout configuration
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TimeoutMessage {
    pub pid: u32,
    pub tag: String,
    pub timeout: u64, // seconds
}

impl UnqualifiedMessage for TimeoutMessage {}
