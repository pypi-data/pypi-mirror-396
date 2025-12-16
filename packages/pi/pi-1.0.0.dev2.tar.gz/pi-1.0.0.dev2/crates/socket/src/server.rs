use serde::{Serialize, de::DeserializeOwned};
use serde_json::{self};
use std::{
    io::Write,
    os::unix::net::UnixStream,
    path::PathBuf,
    sync::{Arc, Mutex},
    thread::{self, JoinHandle},
};
use tracing::{debug, error, info};
use uuid::Uuid;

use crate::event_bus::EventBus;
use crate::messages::{
    GenericMessage, Message, MessagePeer, MessageType, PingMessage, RegisterMessage,
    RegisterResponseMessage,
};
use crate::{message_stream::MessageReaderStream, messages::MessageTypeStatic};

/// Callback function type for handling registration responses
pub type RegistrationHandler = Box<dyn Fn(RegisterResponseMessage) + Send + Sync>;

/// Inner struct that holds the mutable state of the MessageServer
struct MessageServerInner {
    socket_path: PathBuf,
    stream: Option<UnixStream>,
    client_id: Option<Uuid>,
    event_bus: EventBus,
    running: Arc<Mutex<bool>>,
    _listener_thread: Option<JoinHandle<()>>,
}

/// High-level message server for easy service registration and message handling
#[derive(Clone)]
pub struct MessageServer {
    inner: Arc<Mutex<MessageServerInner>>,
}

impl MessageServerInner {
    /// Create a new message server inner instance
    fn new() -> Result<Self, Box<dyn std::error::Error>> {
        // Get socket path from PI_SOCKET env var or error
        let socket_path = std::env::var("PI_SOCKET")
            .map(PathBuf::from)
            .map_err(|_| "PI_SOCKET environment variable not set")?;

        Ok(Self {
            socket_path,
            stream: None,
            client_id: None,
            event_bus: EventBus::new(),
            running: Arc::new(Mutex::new(false)),
            _listener_thread: None,
        })
    }

    /// Create a new message server inner instance with a custom socket path
    fn with_socket_path<P: Into<PathBuf>>(
        socket_path: P,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        Ok(Self {
            socket_path: socket_path.into(),
            stream: None,
            client_id: None,
            event_bus: EventBus::new(),
            running: Arc::new(Mutex::new(false)),
            _listener_thread: None,
        })
    }

    /// Register with the message router
    fn register(
        &mut self,
        well_known_name: Option<String>,
        description: Option<String>,
    ) -> Result<Uuid, Box<dyn std::error::Error>> {
        // Connect to the socket
        let stream = UnixStream::connect(&self.socket_path)?;
        info!("Connected to socket: {:?}", self.socket_path);
        let stream_clone = stream.try_clone()?;
        self.stream = Some(stream);

        // Send registration message
        let register_msg = Message::new(
            "router".to_string(),
            Uuid::nil(),
            RegisterMessage {
                well_known_name,
                description,
            },
        );

        let register_json = serde_json::to_string(&register_msg)?;
        let mut register_bytes = register_json.into_bytes();
        register_bytes.push(0); // Add NUL terminator

        if let Some(ref mut stream) = self.stream {
            stream.write_all(&register_bytes)?;
        }

        // Read registration response using blocking read
        let mut message_stream = MessageReaderStream::new(stream_clone);
        let response = message_stream
            .next_message()
            .map_err(|e| format!("Failed to read message: {}", e))?;

        match response {
            Some(generic_message) => match generic_message.downcast::<RegisterResponseMessage>() {
                Ok(register_response) => {
                    self.client_id = Some(register_response.payload.client_id);
                    info!(
                        "Registered with ID: {}",
                        register_response.payload.client_id
                    );
                }
                Err(generic_message) => {
                    return Err(
                        format!("Invalid registration response: {:?}", generic_message).into(),
                    );
                }
            },
            None => {
                return Err("No registration response received".into());
            }
        };

        Ok(self.client_id.unwrap())
    }

    /// Send a message to another client
    fn send_message<T: MessageType + Serialize>(
        &mut self,
        receiver: &str,
        payload: T,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let client_id = self
            .client_id
            .ok_or("Client not registered. Call register() first.")?;

        let message = Message::new(receiver.to_string(), client_id, payload);

        let message_json = serde_json::to_string(&message)?;
        debug!("Sending message: {}", message_json);
        let mut message_bytes = message_json.into_bytes();
        message_bytes.push(0);

        if let Some(ref mut stream) = self.stream {
            stream.write_all(&message_bytes)?;
        }

        Ok(())
    }

    /// Send a ping message to another client
    fn ping(&mut self, receiver: &str, payload: &str) -> Result<(), Box<dyn std::error::Error>> {
        if self.client_id.is_none() {
            return Err("Client not registered. Call register() first.".into());
        }
        self.send_message(
            receiver,
            PingMessage {
                message: payload.to_string(),
            },
        )
    }

    /// Send a broadcast message to all clients
    fn broadcast<T: MessageType + Serialize>(
        &mut self,
        payload: T,
    ) -> Result<(), Box<dyn std::error::Error>> {
        if self.client_id.is_none() {
            return Err("Client not registered. Call register() first.".into());
        }
        self.send_message("broadcast", payload)
    }

    /// Start listening for messages
    fn listen(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if self.client_id.is_none() {
            return Err("Client not registered. Call register() first.".into());
        }

        let stream = if let Some(stream) = &self.stream {
            stream.try_clone()?
        } else {
            return Err("No connection available".into());
        };

        let event_bus = self.event_bus.clone();
        let running = Arc::clone(&self.running);

        *running.lock().unwrap() = true;

        let listener_thread = thread::spawn(move || {
            Self::listen_loop(stream, event_bus, running);
        });

        self._listener_thread = Some(listener_thread);

        Ok(())
    }

    /// Stop listening for messages
    fn stop(&mut self) {
        *self.running.lock().unwrap() = false;

        // Wait for listener thread to finish
        // if let Some(handle) = self._listener_thread.take() {
        //     if let Err(e) = handle.join() {
        //         error!("Error joining listener thread: {:?}", e);
        //     }
        // }
    }

    /// Get the client ID
    fn client_id(&self) -> Option<Uuid> {
        self.client_id
    }

    /// Get the socket path
    fn socket_path(&self) -> &PathBuf {
        &self.socket_path
    }

    /// Get a reference to the event bus
    fn event_bus(&self) -> &EventBus {
        &self.event_bus
    }

    fn listen_loop(stream: UnixStream, event_bus: EventBus, running: Arc<Mutex<bool>>) {
        let mut message_stream = MessageReaderStream::new(stream.try_clone().unwrap());
        let mut writer = stream;

        while *running.lock().unwrap() {
            match message_stream.next_message() {
                Ok(Some(generic_message)) => {
                    // Publish the message to the event bus
                    let responses = event_bus.publish(generic_message);

                    // Send any responses back
                    for response in responses {
                        let response_json = serde_json::to_string(&response).unwrap();
                        let mut response_bytes = response_json.into_bytes();
                        response_bytes.push(0);

                        if let Err(e) = writer.write_all(&response_bytes) {
                            error!("Error writing response: {}", e);
                        }
                    }
                }
                Ok(None) => {
                    // No message received, continue
                    std::thread::sleep(std::time::Duration::from_millis(10));
                }
                Err(e) => {
                    error!("Error reading message: {}", e);
                    break;
                }
            }
        }
    }
}

impl MessagePeer for MessageServer {
    /// Subscribe to a specific message type with a typed handler
    fn on_message<T: MessageTypeStatic + DeserializeOwned + Clone, F>(&self, handler: F)
    where
        F: Fn(Message<T>) -> Option<GenericMessage> + Send + Sync + 'static,
    {
        let inner = self.inner.lock().unwrap();
        inner.event_bus().subscribe(handler);
    }

    /// Subscribe to all messages with a generic handler
    fn on_all_messages<F>(&self, handler: F)
    where
        F: Fn(GenericMessage) -> Option<GenericMessage> + Send + Sync + 'static,
    {
        let inner = self.inner.lock().unwrap();
        inner.event_bus().subscribe_all(handler);
    }

    /// Send a message to another client
    fn send_message<T: MessageType + Serialize>(
        &self,
        receiver: &str,
        payload: T,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let mut inner = self.inner.lock().unwrap();
        inner.send_message(receiver, payload)
    }
}

impl MessageServer {
    /// Create a new message server instance
    /// Gets socket path from PI_SOCKET environment variable
    /// Returns an error if PI_SOCKET is not set
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let inner = MessageServerInner::new()?;
        Ok(Self {
            inner: Arc::new(Mutex::new(inner)),
        })
    }

    /// Create a new message server instance with a custom socket path
    pub fn with_socket_path<P: Into<PathBuf>>(
        socket_path: P,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        let inner = MessageServerInner::with_socket_path(socket_path)?;
        Ok(Self {
            inner: Arc::new(Mutex::new(inner)),
        })
    }

    /// Register with the message router
    pub fn register(
        &self,
        well_known_name: Option<String>,
        description: Option<String>,
    ) -> Result<Uuid, Box<dyn std::error::Error>> {
        let mut inner = self.inner.lock().unwrap();
        inner.register(well_known_name, description)
    }

    /// Send a ping message to another client
    pub fn ping(&self, receiver: &str, payload: &str) -> Result<(), Box<dyn std::error::Error>> {
        let mut inner = self.inner.lock().unwrap();
        inner.ping(receiver, payload)
    }

    /// Send a broadcast message to all clients
    pub fn broadcast<T: MessageType + Serialize>(
        &self,
        payload: T,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let mut inner = self.inner.lock().unwrap();
        inner.broadcast(payload)
    }

    /// Start listening for messages
    pub fn listen(&self) -> Result<(), Box<dyn std::error::Error>> {
        let mut inner = self.inner.lock().unwrap();
        inner.listen()
    }

    /// Stop listening for messages
    pub fn stop(&self) {
        let mut inner = self.inner.lock().unwrap();
        inner.stop();
    }

    /// Get the client ID
    pub fn client_id(&self) -> Option<Uuid> {
        let inner = self.inner.lock().unwrap();
        inner.client_id()
    }

    /// Get the socket path
    pub fn socket_path(&self) -> PathBuf {
        let inner = self.inner.lock().unwrap();
        inner.socket_path().clone()
    }

    /// Get a reference to the event bus for advanced usage
    pub fn event_bus(&self) -> EventBus {
        let inner = self.inner.lock().unwrap();
        inner.event_bus().clone()
    }
}

impl Drop for MessageServerInner {
    fn drop(&mut self) {
        debug!("Dropping MessageServerInner, stopping listener thread");
        self.stop();
        debug!("MessageServerInner drop completed");
    }
}
