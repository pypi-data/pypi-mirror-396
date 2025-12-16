//! OSC 133 (Shell Integration) sequence detection and utilities
//!
//! OSC 133 is a protocol for shell integration that allows terminal emulators
//! to track command boundaries, prompt locations, and command execution status.
//!
//! The sequences are:
//! - OSC 133;A ST - Mark start of prompt
//! - OSC 133;B ST - Mark end of prompt (start of command input)
//! - OSC 133;C ST - Mark start of command execution
//! - OSC 133;D;[exit_code] ST - Mark end of command execution

use pishell_eventbus::Eventable;
use serde::{Deserialize, Serialize};
use std::fmt;
use tracing::debug;
use vt_push_parser::event::VTEvent;

/// OSC 133 sequence types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, strum::EnumIter)]
pub enum Osc133Type {
    /// OSC 133;A - Start of prompt
    PromptStart,
    /// OSC 133;B - End of prompt, start of command input
    PromptEnd,
    /// OSC 133;C - Start of command execution
    CommandStart,
    /// OSC 133;D - End of command execution (with optional exit code)
    CommandEnd,
}

impl fmt::Display for Osc133Type {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Osc133Type::PromptStart => write!(f, "PromptStart"),
            Osc133Type::PromptEnd => write!(f, "PromptEnd"),
            Osc133Type::CommandStart => write!(f, "CommandStart"),
            Osc133Type::CommandEnd => write!(f, "CommandEnd"),
        }
    }
}

/// An OSC 133 sequence with optional data
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Osc133Sequence {
    /// The type of OSC 133 sequence
    pub sequence_type: Osc133Type,
    /// Optional data (e.g., exit code for CommandEnd)
    pub data: Option<String>,
}

impl Eventable for Osc133Sequence {
    type Recv<'a> = &'a Osc133Sequence;

    fn cast(data: &pishell_eventbus::EventData) -> Self::Recv<'_> {
        match data {
            pishell_eventbus::EventData::Boxed(boxed) => {
                boxed.downcast_ref::<Osc133Sequence>().unwrap()
            }
            _ => unreachable!(),
        }
    }

    fn cast_send(self) -> pishell_eventbus::EventData {
        pishell_eventbus::EventData::Boxed(Box::new(self))
    }
}

impl Osc133Sequence {
    /// Create a new OSC 133 sequence
    pub fn new(sequence_type: Osc133Type, data: Option<String>) -> Self {
        Self {
            sequence_type,
            data,
        }
    }

    /// Parse OSC 133 sequence from OSC data bytes
    pub fn from_osc_data(data: &[u8]) -> Option<Self> {
        // OSC 133 sequences start with "133;"
        if !data.starts_with(b"133;") {
            return None;
        }

        if data.len() < 5 {
            return None;
        }

        let sequence_type = data[4];
        let sequence_type = match sequence_type {
            b'A' => Osc133Type::PromptStart,
            b'B' => Osc133Type::PromptEnd,
            b'C' => Osc133Type::CommandStart,
            b'D' => Osc133Type::CommandEnd,
            _ => return None,
        };

        // Extract optional data after the sequence type
        let extra_data = if data.len() > 5 && data[5] == b';' {
            // There's additional data after the sequence type
            let data_bytes = &data[6..];
            Some(String::from_utf8_lossy(data_bytes).to_string())
        } else {
            None
        };

        Some(Self::new(sequence_type, extra_data))
    }

    /// Parse OSC 133 sequence from a VTEvent
    pub fn from_vt_event(event: &VTEvent<'_>) -> Option<Self> {
        match event {
            // TODO: This may be multiple packets
            VTEvent::OscData(osc_data) | VTEvent::OscEnd { data: osc_data, .. } => {
                Self::from_osc_data(osc_data)
            }
            _ => None,
        }
    }

    /// Generate the OSC sequence bytes for this sequence
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut result = b"133;".to_vec();

        let type_char = match self.sequence_type {
            Osc133Type::PromptStart => b'A',
            Osc133Type::PromptEnd => b'B',
            Osc133Type::CommandStart => b'C',
            Osc133Type::CommandEnd => b'D',
        };
        result.push(type_char);

        if let Some(ref data) = self.data {
            result.push(b';');
            result.extend(data.as_bytes());
        }

        result
    }

    /// Get the exit code if this is a CommandEnd sequence
    pub fn exit_code(&self) -> Option<i32> {
        if self.sequence_type == Osc133Type::CommandEnd {
            if let Some(ref data) = self.data {
                data.parse().ok()
            } else {
                Some(0) // Default to 0 if no exit code specified
            }
        } else {
            None
        }
    }

    /// Check if this sequence indicates a successful command execution
    pub fn is_command_success(&self) -> Option<bool> {
        self.exit_code().map(|code| code == 0)
    }
}

impl fmt::Display for Osc133Sequence {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match &self.data {
            Some(data) => {
                let type_char = match self.sequence_type {
                    Osc133Type::PromptStart => "A",
                    Osc133Type::PromptEnd => "B",
                    Osc133Type::CommandStart => "C",
                    Osc133Type::CommandEnd => "D",
                };
                write!(f, "OSC 133;{type_char};{data}")
            }
            None => {
                let type_char = match self.sequence_type {
                    Osc133Type::PromptStart => "A",
                    Osc133Type::PromptEnd => "B",
                    Osc133Type::CommandStart => "C",
                    Osc133Type::CommandEnd => "D",
                };
                write!(f, "OSC 133;{type_char}")
            }
        }
    }
}

/// Shell integration state tracker using OSC 133 sequences
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ShellState {
    /// Currently showing a prompt
    AtPrompt,
    /// User is typing a command
    InputtingCommand,
    /// Command is being executed
    ExecutingCommand,
    /// Command execution finished
    CommandFinished { exit_code: Option<i32> },
    /// Unknown state
    Unknown,
}

impl Default for ShellState {
    fn default() -> Self {
        Self::Unknown
    }
}

/// Shell integration tracker that maintains state based on OSC 133 sequences
#[derive(Debug, Clone)]
pub struct ShellIntegrationTracker {
    state: ShellState,
    last_sequence: Option<Osc133Sequence>,
}

impl ShellIntegrationTracker {
    /// Create a new shell integration tracker
    pub fn new() -> Self {
        Self {
            state: ShellState::Unknown,
            last_sequence: None,
        }
    }

    /// Process an OSC 133 sequence and update the shell state
    pub fn process_sequence(&mut self, sequence: Osc133Sequence) {
        debug!(
            "Processing OSC 133 sequence: {} (current state: {:?})",
            sequence, self.state
        );

        self.state = match sequence.sequence_type {
            Osc133Type::PromptStart => ShellState::AtPrompt,
            Osc133Type::PromptEnd => ShellState::InputtingCommand,
            Osc133Type::CommandStart => ShellState::ExecutingCommand,
            Osc133Type::CommandEnd => ShellState::CommandFinished {
                exit_code: sequence.exit_code(),
            },
        };

        self.last_sequence = Some(sequence);
    }

    /// Process a VT event for OSC 133 sequences
    pub fn process_vt_event(&mut self, event: &VTEvent<'_>) {
        if let Some(sequence) = Osc133Sequence::from_vt_event(event) {
            self.process_sequence(sequence);
        }
    }

    /// Get the current shell state
    pub fn current_state(&self) -> &ShellState {
        &self.state
    }

    /// Get the last processed OSC 133 sequence
    pub fn last_sequence(&self) -> Option<&Osc133Sequence> {
        self.last_sequence.as_ref()
    }

    /// Check if the shell is currently idle (at prompt or command finished)
    pub fn is_idle(&self) -> bool {
        matches!(
            self.state,
            ShellState::AtPrompt | ShellState::CommandFinished { .. }
        )
    }

    /// Check if a command is currently running
    pub fn is_executing_command(&self) -> bool {
        matches!(self.state, ShellState::ExecutingCommand)
    }

    /// Get the exit code of the last finished command, if available
    pub fn last_exit_code(&self) -> Option<i32> {
        match &self.state {
            ShellState::CommandFinished { exit_code } => *exit_code,
            _ => None,
        }
    }
}

impl Default for ShellIntegrationTracker {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_osc133_sequence_parsing() {
        // Test basic sequences
        assert_eq!(
            Osc133Sequence::from_osc_data(b"133;A"),
            Some(Osc133Sequence::new(Osc133Type::PromptStart, None))
        );
        assert_eq!(
            Osc133Sequence::from_osc_data(b"133;B"),
            Some(Osc133Sequence::new(Osc133Type::PromptEnd, None))
        );
        assert_eq!(
            Osc133Sequence::from_osc_data(b"133;C"),
            Some(Osc133Sequence::new(Osc133Type::CommandStart, None))
        );
        assert_eq!(
            Osc133Sequence::from_osc_data(b"133;D"),
            Some(Osc133Sequence::new(Osc133Type::CommandEnd, None))
        );

        // Test sequence with data
        assert_eq!(
            Osc133Sequence::from_osc_data(b"133;D;0"),
            Some(Osc133Sequence::new(
                Osc133Type::CommandEnd,
                Some("0".to_string())
            ))
        );
        assert_eq!(
            Osc133Sequence::from_osc_data(b"133;D;1"),
            Some(Osc133Sequence::new(
                Osc133Type::CommandEnd,
                Some("1".to_string())
            ))
        );

        // Test invalid sequences
        assert_eq!(Osc133Sequence::from_osc_data(b"133;X"), None);
        assert_eq!(Osc133Sequence::from_osc_data(b"132;A"), None);
        assert_eq!(Osc133Sequence::from_osc_data(b"133"), None);
    }

    #[test]
    fn test_exit_code_parsing() {
        let seq = Osc133Sequence::new(Osc133Type::CommandEnd, Some("42".to_string()));
        assert_eq!(seq.exit_code(), Some(42));
        assert_eq!(seq.is_command_success(), Some(false));

        let seq = Osc133Sequence::new(Osc133Type::CommandEnd, Some("0".to_string()));
        assert_eq!(seq.exit_code(), Some(0));
        assert_eq!(seq.is_command_success(), Some(true));

        let seq = Osc133Sequence::new(Osc133Type::CommandEnd, None);
        assert_eq!(seq.exit_code(), Some(0));
        assert_eq!(seq.is_command_success(), Some(true));

        let seq = Osc133Sequence::new(Osc133Type::PromptStart, None);
        assert_eq!(seq.exit_code(), None);
        assert_eq!(seq.is_command_success(), None);
    }

    #[test]
    fn test_shell_integration_tracker() {
        let mut tracker = ShellIntegrationTracker::new();
        assert_eq!(tracker.current_state(), &ShellState::Unknown);

        // Simulate a command cycle
        tracker.process_sequence(Osc133Sequence::new(Osc133Type::PromptStart, None));
        assert_eq!(tracker.current_state(), &ShellState::AtPrompt);
        assert!(tracker.is_idle());

        tracker.process_sequence(Osc133Sequence::new(Osc133Type::PromptEnd, None));
        assert_eq!(tracker.current_state(), &ShellState::InputtingCommand);
        assert!(!tracker.is_idle());

        tracker.process_sequence(Osc133Sequence::new(Osc133Type::CommandStart, None));
        assert_eq!(tracker.current_state(), &ShellState::ExecutingCommand);
        assert!(tracker.is_executing_command());

        tracker.process_sequence(Osc133Sequence::new(
            Osc133Type::CommandEnd,
            Some("0".to_string()),
        ));
        assert_eq!(
            tracker.current_state(),
            &ShellState::CommandFinished { exit_code: Some(0) }
        );
        assert!(tracker.is_idle());
        assert_eq!(tracker.last_exit_code(), Some(0));
    }

    #[test]
    fn test_sequence_to_bytes() {
        let seq = Osc133Sequence::new(Osc133Type::PromptStart, None);
        assert_eq!(seq.to_bytes(), b"133;A");

        let seq = Osc133Sequence::new(Osc133Type::CommandEnd, Some("42".to_string()));
        assert_eq!(seq.to_bytes(), b"133;D;42");
    }

    #[test]
    fn test_display_formatting() {
        let seq = Osc133Sequence::new(Osc133Type::PromptStart, None);
        assert_eq!(seq.to_string(), "OSC 133;A");

        let seq = Osc133Sequence::new(Osc133Type::CommandEnd, Some("1".to_string()));
        assert_eq!(seq.to_string(), "OSC 133;D;1");
    }
}
