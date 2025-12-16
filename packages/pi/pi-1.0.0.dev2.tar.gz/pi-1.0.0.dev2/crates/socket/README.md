# Pishell Socket

A Unix domain socket-based message passing system for inter-process communication.

## Features

- Unix domain socket communication
- Type-safe message handling with EventBus
- Automatic message serialization/deserialization
- Support for typed and generic message handlers
- Thread-safe and cloneable MessageServer instances

## Quick Start

### Basic Usage with EventBus

```rust
use pishell_socket::{MessageServer, PingMessage, ErrorMessage};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a message server
    let server = MessageServer::new()?;
    
    // Subscribe to specific message types with typed handlers
    server.on_message::<PingMessage, _>(|ping_msg| {
        println!("Received ping: {}", ping_msg.payload.message);
        
        // Send a response back
        Some(ping_msg.response(ErrorMessage {
            error: "Pong!".to_string(),
            id: Some(ping_msg.header.id),
        }))
    });
    
    // Subscribe to all messages with a generic handler
    server.on_all_messages(|generic_msg| {
        println!("Received message: {} from {}", 
                 generic_msg.header.message_name, 
                 generic_msg.header.sender);
        None // No response from this handler
    });
    
    // Register with the router
    server.register(Some("my_service".to_string()), 
                   Some("My service description".to_string()))?;
    
    // Start listening for messages
    server.listen()?;
    
    // Keep the server running
    loop {
        std::thread::sleep(std::time::Duration::from_secs(1));
    }
}
```

### Advanced EventBus Usage

You can also use the EventBus directly for more advanced scenarios:

```rust
use pishell_socket::{EventBus, PingMessage, ErrorMessage};

fn main() {
    let event_bus = EventBus::new();
    
    // Subscribe to typed messages
    event_bus.subscribe::<PingMessage, _>(|ping_msg| {
        println!("Handling ping: {}", ping_msg.payload.message);
        Some(ping_msg.response(ErrorMessage {
            error: "Response".to_string(),
            id: Some(ping_msg.header.id),
        }))
    });
    
    // Subscribe to all messages
    event_bus.subscribe_all(|generic_msg| {
        println!("Generic handler: {}", generic_msg.header.message_name);
        None
    });
    
    // Publish messages
    let ping_msg = Message::new(
        "receiver".to_string(),
        Uuid::new_v4(),
        PingMessage { message: "Hello".to_string() }
    ).into_generic();
    
    let responses = event_bus.publish(ping_msg);
    println!("Got {} responses", responses.len());
}
```

## Message Types

The system supports any type that implements the `MessageType` trait. Built-in message types include:

- `PingMessage` - Simple ping/pong messages
- `ErrorMessage` - Error responses
- `RegisterMessage` - Service registration
- `RegisterResponseMessage` - Registration confirmation
- `ListServersMessage` - List available services
- `ListServersResponseMessage` - Service list response

## Creating Custom Message Types

```rust
use pishell_socket::{MessageType, MessageTypeStatic};
use serde::{Serialize, Deserialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MyCustomMessage {
    pub data: String,
    pub timestamp: i64,
}

// The trait is automatically implemented for types that implement the required traits
impl MessageTypeStatic for MyCustomMessage {}
```

## Thread Safety

The `MessageServer` is designed to be thread-safe and cloneable. You can share a single server instance across multiple threads:

```rust
let server = MessageServer::new()?;
let server_clone = server.clone();

// Use in different threads
std::thread::spawn(move || {
    server_clone.send_message("other_service", some_payload)?;
    Ok::<(), Box<dyn std::error::Error>>(())
});
```

## Architecture

The system uses an EventBus pattern where:

1. **EventBus**: Handles message routing and dispatching
2. **MessageServer**: High-level interface for socket communication
3. **GenericMessage**: Type-erased message container
4. **Typed Handlers**: Type-safe callbacks that receive properly typed messages

This design allows for:
- Type safety when handling specific message types
- Flexibility to handle generic messages
- Easy testing and mocking
- Clean separation of concerns
