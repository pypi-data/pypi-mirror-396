pub mod event_bus;
pub mod message_stream;
pub mod messages;
pub mod router;
pub mod server;

pub use event_bus::EventBus;
pub use message_stream::{MessageReaderExt, MessageReaderStream, create_message_stream};
pub use router::{MessageRouter, SocketServer};
pub use server::MessageServer;

// Re-export commonly used message types
pub use messages::{
    ErrorMessage, GenericMessage, ListServersMessage, ListServersResponseMessage, Message,
    MessageType, MessageTypeStatic, PingMessage, RegisterMessage, RegisterResponseMessage, Server,
};
