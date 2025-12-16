use crate::{
    message_stream::MessageReaderStream,
    messages::{ErrorMessage, RegisterMessage, RegisterResponseMessage},
};
use serde_json;
use std::{
    collections::HashMap,
    env,
    io::Write,
    os::unix::net::{UnixListener, UnixStream},
    path::PathBuf,
    sync::{
        Arc, Mutex,
        atomic::{AtomicBool, Ordering},
        mpsc,
    },
    thread::{self, JoinHandle},
};
use tracing::{debug, error, info};
use uuid::Uuid;

use pishell_rpc_types::Router as RouterIface;
use pishell_rpc_types::RouterClient as RouterClientIface;

use crate::messages::{GenericMessage, Message};

#[derive(Debug, Clone)]
struct Client {
    id: Uuid,
    well_known_name: Option<String>,
    description: Option<String>,
    client_sender: mpsc::Sender<Vec<u8>>,
}

#[derive(Debug)]
pub struct MessageRouter {
    clients: HashMap<Uuid, Client>,
    well_known_names: HashMap<String, Uuid>,
    client_senders: HashMap<Uuid, mpsc::Sender<Vec<u8>>>,
}

impl MessageRouter {
    pub fn new() -> Self {
        Self {
            clients: HashMap::new(),
            well_known_names: HashMap::new(),
            client_senders: HashMap::new(),
        }
    }

    pub fn get_well_known_processes(&self) -> Vec<(String, Uuid, Option<String>)> {
        let mut processes = Vec::new();
        for (name, &client_id) in &self.well_known_names {
            if let Some(client) = self.clients.get(&client_id) {
                processes.push((name.clone(), client_id, client.description.clone()));
            }
        }
        processes
    }

    pub fn register_client(
        &mut self,
        well_known_name: Option<String>,
        description: Option<String>,
        client_sender: mpsc::Sender<Vec<u8>>,
    ) -> Result<Uuid, String> {
        let id = Uuid::new_v4();

        // If well-known name is provided, check for conflicts
        if let Some(name) = &well_known_name {
            if let Some(existing_id) = self.well_known_names.get(name) {
                // Deny registration if name is already taken
                error!(
                    "Registration denied: well-known name '{}' is already registered by client {}",
                    name, existing_id
                );
                return Err(format!(
                    "Well-known name '{}' is already registered by another client",
                    name
                ));
            }
        }

        let client = Client {
            id,
            well_known_name: well_known_name.clone(),
            description,
            client_sender: client_sender.clone(),
        };

        // Register the well-known name if provided
        if let Some(name) = &well_known_name {
            self.well_known_names.insert(name.clone(), id);
            info!("Registered client {} with well-known name '{}'", id, name);
        }

        self.clients.insert(id, client);
        self.client_senders.insert(id, client_sender);

        info!("Successfully registered client {}", id);
        Ok(id)
    }

    fn get_client_id(&self, receiver: &str) -> Option<Uuid> {
        // First try to parse as UUID
        if let Ok(uuid) = Uuid::parse_str(receiver) {
            if self.clients.contains_key(&uuid) {
                return Some(uuid);
            }
        }

        // Then try as well-known name
        self.well_known_names.get(receiver).copied()
    }

    fn remove_client(&mut self, id: Uuid) {
        if let Some(client) = self.clients.remove(&id) {
            if let Some(name) = client.well_known_name {
                self.well_known_names.remove(&name);
            }
        }
        self.client_senders.remove(&id);
    }
}

pub struct SocketServer {
    socket_path: PathBuf,
    router: Arc<Mutex<MessageRouter>>,
    listener_thread: Option<JoinHandle<()>>,
    shutdown: Option<Arc<AtomicBool>>,
}

impl SocketServer {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        // Get temp directory
        let temp_dir = env::temp_dir();
        let pid = std::process::id();
        let socket_path = temp_dir.join(format!("pishell_{}.sock", pid));

        info!("Creating socket server at: {:?}", socket_path);

        // Remove existing socket file if it exists
        if socket_path.exists() {
            std::fs::remove_file(&socket_path)?;
            info!("Removed existing socket file");
        }

        Ok(Self {
            socket_path,
            router: Arc::new(Mutex::new(MessageRouter::new())),
            listener_thread: None,
            shutdown: None,
        })
    }

    pub fn with_path(socket_path: PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        info!("Creating socket server at: {:?}", socket_path);

        // Create parent directory if it doesn't exist
        if let Some(parent) = socket_path.parent() {
            std::fs::create_dir_all(parent)?;
        }

        // Remove existing socket file if it exists
        if socket_path.exists() {
            std::fs::remove_file(&socket_path)?;
            info!("Removed existing socket file");
        }

        Ok(Self {
            socket_path,
            router: Arc::new(Mutex::new(MessageRouter::new())),
            listener_thread: None,
            shutdown: None,
        })
    }

    pub fn start(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        // Create Unix socket listener
        let listener = UnixListener::bind(&self.socket_path)?;

        // Set socket file permissions to user only (600)
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&self.socket_path, std::fs::Permissions::from_mode(0o600))?;

        info!(
            "Socket server started and listening on: {:?}",
            self.socket_path
        );

        // Start listening thread
        let router = Arc::clone(&self.router);
        let shutdown = Arc::new(AtomicBool::new(false));
        self.shutdown = Some(shutdown.clone());
        let listener_thread = thread::spawn(move || {
            Self::listen_for_connections(listener, router, shutdown);
        });
        self.listener_thread = Some(listener_thread);

        Ok(())
    }

    fn listen_for_connections(
        listener: UnixListener,
        router: Arc<Mutex<MessageRouter>>,
        shutdown: Arc<AtomicBool>,
    ) {
        info!("Socket listener thread started");

        for stream in listener.incoming() {
            if shutdown.load(Ordering::Relaxed) {
                info!("Shutting down socket listener thread");
                break;
            }
            match stream {
                Ok(stream) => {
                    info!("New connection accepted");

                    // Spawn a new thread for each connection
                    let router = Arc::clone(&router);
                    thread::spawn(move || {
                        Self::handle_connection(stream, router);
                    });
                }
                Err(e) => {
                    error!("Error accepting connection: {}", e);
                }
            }
        }
    }

    fn handle_connection(stream: UnixStream, router: Arc<Mutex<MessageRouter>>) {
        info!("Handling connection in thread");

        let mut message_stream = MessageReaderStream::new(stream.try_clone().unwrap());
        let mut writer = stream;
        let mut client_id: Option<Uuid> = None;

        // Create channel for receiving messages from router
        let (tx, rx) = mpsc::channel::<Vec<u8>>();
        let mut tx_clone = Some(tx);

        // Start a thread to handle incoming messages from the router
        let mut writer_clone = writer.try_clone().unwrap();
        thread::spawn(move || {
            for msg_bytes in rx {
                if let Err(e) = writer_clone.write_all(&msg_bytes) {
                    error!("Error writing message to client: {}", e);
                    break;
                }
                writer_clone.write_all(b"\0");
            }
        });

        loop {
            // Read next message using MessageStream
            match message_stream.next_message() {
                Ok(Some(generic_message)) => {
                    info!("Received message: {:?}", generic_message);

                    let (response, broadcast): (Option<GenericMessage>, Option<GenericMessage>) =
                        if client_id.is_some() {
                            (Self::process_message(generic_message, &router), None)
                        } else {
                            let (response, new_client_id, broadcast) =
                                Self::process_handshake(generic_message, &router, &mut tx_clone);
                            if new_client_id.is_some() {
                                client_id = new_client_id;
                            }
                            (Some(response), broadcast)
                        };

                    debug!("Sending response: {:?}", response);

                    // Send response if any
                    if let Some(response) = response {
                        let target_id = router
                            .lock()
                            .unwrap()
                            .get_client_id(&response.header.receiver);
                        if let Some(target_id) = target_id {
                            info!("Sending response to client: {}", target_id);
                            let client_sender = router
                                .lock()
                                .unwrap()
                                .client_senders
                                .get(&target_id)
                                .unwrap()
                                .clone();
                            let response_bytes = response.to_json().to_string().into_bytes();
                            if let Err(e) = client_sender.send(response_bytes) {
                                error!("Error sending response to client {}: {}", target_id, e);
                            }
                        } else {
                            error!("Target client not found: {}", response.header.receiver);
                            let mut response_bytes = response.to_json().to_string().into_bytes();
                            response_bytes.push(0); // Add null terminator
                            if let Err(e) = writer.write_all(&response_bytes) {
                                error!("Error writing response: {}", e);
                                break;
                            }
                        }
                    }

                    if let Some(broadcast) = broadcast {
                        Self::send_broadcast_message(broadcast, &router);
                    }
                }
                Ok(None) => {
                    info!("Connection closed by client");
                    break;
                }
                Err(e) => {
                    error!("Error reading message: {}", e);
                    let error_response = serde_json::json!({
                        "error": "Failed to read message",
                        "details": e.to_string()
                    });
                    let mut response_bytes = error_response.to_string().into_bytes();
                    response_bytes.push(0);

                    if let Err(e) = writer.write_all(&response_bytes) {
                        error!("Error writing error response: {}", e);
                    }
                    break;
                }
            }
        }

        // Clean up client registration
        if let Some(id) = client_id {
            if let Ok(mut router) = router.lock() {
                router.remove_client(id);
                info!("Removed client {} from router", id);
            }
        }

        info!("Connection handler thread finished");
    }

    fn process_handshake(
        generic_message: GenericMessage,
        router: &Arc<Mutex<MessageRouter>>,
        client_sender: &mut Option<mpsc::Sender<Vec<u8>>>,
    ) -> (GenericMessage, Option<Uuid>, Option<GenericMessage>) {
        let (response, client_id, well_known_name): (GenericMessage, Option<Uuid>, Option<String>) =
            match generic_message.downcast::<RegisterMessage>() {
                Ok(mut register_message) => {
                    debug!("Received register message: {:?}", register_message);
                    let well_known_name = register_message.payload.well_known_name.clone();
                    let description = register_message.payload.description.clone();
                    match router.lock().unwrap().register_client(
                        well_known_name.clone(),
                        description.clone(),
                        client_sender.take().unwrap(),
                    ) {
                        Ok(id) => {
                            register_message.header.sender = id;
                            let response = register_message
                                .response(RegisterResponseMessage { client_id: id });
                            (response, Some(id), well_known_name)
                        }
                        Err(error_msg) => (
                            register_message.response(ErrorMessage {
                                error: error_msg,
                                id: None,
                            }),
                            None,
                            None,
                        ),
                    }
                }
                Err(_) => (
                    Message::new(
                        "router".to_string(),
                        Uuid::nil(),
                        ErrorMessage {
                            error: "protocol error: initial message is not a RegisterMessage"
                                .to_string(),
                            id: None,
                        },
                    )
                    .into_generic(),
                    None,
                    None,
                ),
            };

        let broadcast = match (client_id, well_known_name) {
            (Some(id), Some(_name)) => {
                let notification = RouterClientIface::WellKnownPeersChangedRequest {
                    peers: Self::get_well_known_peers_notification(router),
                };

                Some(Message::new("broadcast".to_string(), id, notification).into_generic())
            }
            _ => None,
        };

        (response, client_id, broadcast)
    }

    fn get_well_known_peers(
        router: &Arc<Mutex<MessageRouter>>,
    ) -> HashMap<String, RouterIface::WellKnownProcess> {
        let router = router.lock().unwrap();
        let mut well_known_names: HashMap<String, RouterIface::WellKnownProcess> = HashMap::new();

        for (name, &client_uuid) in &router.well_known_names {
            if let Some(client) = router.clients.get(&client_uuid) {
                well_known_names.insert(
                    name.clone(),
                    RouterIface::WellKnownProcess {
                        name: name.clone(),
                        client_id: client_uuid.to_string(),
                        description: client.description.clone(),
                    },
                );
            }
        }

        well_known_names
    }

    fn get_well_known_peers_notification(
        router: &Arc<Mutex<MessageRouter>>,
    ) -> HashMap<String, RouterClientIface::WellKnownProcess> {
        let router = router.lock().unwrap();
        let mut well_known_names: HashMap<String, RouterClientIface::WellKnownProcess> =
            HashMap::new();

        for (name, &client_uuid) in &router.well_known_names {
            if let Some(client) = router.clients.get(&client_uuid) {
                well_known_names.insert(
                    name.clone(),
                    RouterClientIface::WellKnownProcess {
                        name: name.clone(),
                        client_id: client_uuid.to_string(),
                        description: client.description.clone(),
                    },
                );
            }
        }

        well_known_names
    }

    pub fn process_message(
        generic_message: GenericMessage,
        router: &Arc<Mutex<MessageRouter>>,
    ) -> Option<GenericMessage> {
        debug!("Processing message: {:?}", generic_message);

        // Handle ListWellKnownNames message
        let generic_message =
            match generic_message.downcast::<RouterIface::ListWellKnownProcessesRequest>() {
                Ok(list_message) => {
                    debug!("Received list well-known names message");
                    return Some(list_message.response(
                        RouterIface::ListWellKnownProcessesResponse {
                            result: Self::get_well_known_peers(router),
                        },
                    ));
                }
                Err(generic_message) => generic_message,
            };

        // Check if this is a broadcast message
        if generic_message.header.receiver == "broadcast" {
            Self::send_broadcast_message(generic_message, router);
            None
        } else {
            Some(generic_message)
        }
    }

    fn send_broadcast_message(generic_message: GenericMessage, router: &Arc<Mutex<MessageRouter>>) {
        // Broadcast to all clients except the sender
        let client_ids: Vec<Uuid> = router
            .lock()
            .unwrap()
            .clients
            .keys()
            .filter(|&&id| id != generic_message.header.sender)
            .cloned()
            .collect();

        info!(
            "Broadcasting message from {} to {} other client(s)",
            generic_message.header.sender,
            client_ids.len()
        );

        // Actually send the broadcast message to all target clients
        for target_id in &client_ids {
            let json = generic_message.to_json();
            let message_string = serde_json::to_string(&json).unwrap();
            debug!(
                "Sending broadcast message to client {}: {}",
                target_id, message_string
            );
            if let Err(e) = router
                .lock()
                .unwrap()
                .clients
                .get(target_id)
                .unwrap()
                .client_sender
                .send(message_string.clone().into_bytes())
            {
                error!("Failed to send broadcast to client {}: {}", target_id, e);
            }
        }
    }

    pub fn socket_path(&self) -> String {
        self.socket_path.to_string_lossy().to_string()
    }

    pub fn router(&self) -> Arc<Mutex<MessageRouter>> {
        Arc::clone(&self.router)
    }

    pub fn stop(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        info!("Stopping socket server");

        // Remove socket file
        if self.socket_path.exists() {
            std::fs::remove_file(&self.socket_path)?;
            info!("Removed socket file");
        }

        if let Some(shutdown) = self.shutdown.take() {
            shutdown.store(true, Ordering::Relaxed);
        }

        Ok(())
    }
}

impl Drop for SocketServer {
    fn drop(&mut self) {
        info!("Dropping SocketServer, stopping listener thread");
        if let Err(e) = self.stop() {
            error!("Error stopping socket server during drop: {}", e);
        }
        info!("SocketServer drop completed");
    }
}
