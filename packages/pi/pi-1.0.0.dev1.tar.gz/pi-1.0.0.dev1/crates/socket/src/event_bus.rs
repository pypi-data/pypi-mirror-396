use serde::de::DeserializeOwned;
use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
};
use tracing::{debug, warn};

use crate::messages::{GenericMessage, Message, MessageTypeStatic};

/// Callback function type for handling typed messages
pub type TypedMessageHandler<T> = Box<dyn Fn(Message<T>) -> Option<GenericMessage> + Send + Sync>;

/// Callback function type for handling generic messages
pub type GenericMessageHandler =
    Box<dyn Fn(GenericMessage) -> Option<GenericMessage> + Send + Sync>;

/// Event bus for handling message routing and dispatching
#[derive(Clone)]
pub struct EventBus {
    inner: Arc<Mutex<EventBusInner>>,
}

struct EventBusInner {
    typed_handlers: HashMap<String, GenericMessageHandler>,
    generic_handlers: Vec<GenericMessageHandler>,
}

impl EventBus {
    /// Create a new event bus
    pub fn new() -> Self {
        Self {
            inner: Arc::new(Mutex::new(EventBusInner {
                typed_handlers: HashMap::new(),
                generic_handlers: Vec::new(),
            })),
        }
    }

    /// Subscribe to a specific message type with a typed handler
    pub fn subscribe<T: MessageTypeStatic + DeserializeOwned + Clone, F>(&self, handler: F)
    where
        F: Fn(Message<T>) -> Option<GenericMessage> + Send + Sync + 'static,
    {
        let message_type = <T as MessageTypeStatic>::message_type_name();
        let mut inner = self.inner.lock().unwrap();
        inner.typed_handlers.insert(
            message_type.to_string(),
            Box::new(move |generic_msg| {
                // Try to downcast the message to the specific type
                if let Ok(typed_msg) = generic_msg.downcast::<T>() {
                    handler(typed_msg)
                } else {
                    warn!("Failed to downcast message to type {}", message_type);
                    None
                }
            }),
        );

        debug!("Subscribed to message type: {}", message_type);
    }

    /// Subscribe to all messages with a generic handler
    pub fn subscribe_all<F>(&self, handler: F)
    where
        F: Fn(GenericMessage) -> Option<GenericMessage> + Send + Sync + 'static,
    {
        let mut inner = self.inner.lock().unwrap();
        inner.generic_handlers.push(Box::new(handler));
        debug!("Added generic message handler");
    }

    /// Unsubscribe from a specific message type
    pub fn unsubscribe(&self, message_type: &str) {
        let mut inner = self.inner.lock().unwrap();
        if inner.typed_handlers.remove(message_type).is_some() {
            debug!("Unsubscribed from message type: {}", message_type);
        }
    }

    /// Clear all handlers
    pub fn clear(&self) {
        let mut inner = self.inner.lock().unwrap();
        inner.typed_handlers.clear();
        inner.generic_handlers.clear();
        debug!("Cleared all event bus handlers");
    }

    /// Publish a message to all relevant handlers
    pub fn publish(&self, message: GenericMessage) -> Vec<GenericMessage> {
        let mut responses = Vec::new();
        let inner = self.inner.lock().unwrap();

        // Try to find a typed handler for this message type
        if let Some(handler) = inner.typed_handlers.get(&message.header.message_name) {
            if let Some(response) = handler(message.clone()) {
                responses.push(response);
            }
        }

        // Also call all generic handlers
        for handler in &inner.generic_handlers {
            if let Some(response) = handler(message.clone()) {
                responses.push(response);
            }
        }

        debug!(
            "Published message type '{}' to {} handlers, got {} responses",
            message.header.message_name,
            inner.typed_handlers.len() + inner.generic_handlers.len(),
            responses.len()
        );

        responses
    }

    /// Get the number of registered handlers
    pub fn handler_count(&self) -> usize {
        let inner = self.inner.lock().unwrap();
        inner.typed_handlers.len() + inner.generic_handlers.len()
    }

    /// Check if there are any handlers for a specific message type
    pub fn has_handler(&self, message_type: &str) -> bool {
        let inner = self.inner.lock().unwrap();
        inner.typed_handlers.contains_key(message_type)
    }
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}
