use serde::{de::DeserializeOwned, Deserialize, Serialize, Serializer};
use std::{
    any::{type_name, Any},
    fmt::Debug,
    sync::Arc,
};
use tracing::debug;
use uuid::Uuid;

/// Marker trait for messages that should use the default
/// unqualified MessageType implementation. Generated RPC messages
/// do NOT implement this trait and instead have explicit MessageType
/// implementations.
pub trait UnqualifiedMessage {}

// Implement for unit type used in methods with no response
impl UnqualifiedMessage for () {}

/// Trait for message types that can provide their type name
pub trait MessageType: Send + Sync + Debug + Any + 'static {
    /// Returns the type name of this message
    fn message_type_name(&self) -> &'static str;

    fn to_json(&self) -> serde_json::Value;
}

/// Trait for message types that can provide their type name
pub trait MessageTypeStatic: MessageType + Send + Sync + Debug + Any + 'static {
    /// Returns the type name of this message
    fn message_type_name() -> &'static str;
}

/// Default implementation for unqualified messages
impl<T> MessageType for T
where
    T: UnqualifiedMessage + Serialize + Clone + Debug + Any + Send + Sync + 'static,
{
    fn message_type_name(&self) -> &'static str {
        type_name::<Self>().rsplit_once("::").unwrap().1
    }

    fn to_json(&self) -> serde_json::Value {
        serde_json::to_value(self).unwrap()
    }
}

impl<T> MessageTypeStatic for T
where
    T: MessageType + UnqualifiedMessage + Serialize + Clone + Debug + Any + Send + Sync + 'static,
{
    fn message_type_name() -> &'static str {
        type_name::<Self>().rsplit_once("::").unwrap().1
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MessageHeader {
    pub receiver: String,
    pub sender: Uuid,

    pub id: Uuid,
    pub response_to: Option<Uuid>,
    pub message_name: String,
}

/// A message sent between processes.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Message<T>
where
    T: MessageType,
{
    #[serde(flatten)]
    pub header: MessageHeader,

    pub payload: T,
}

impl<T: MessageType> Message<T> {
    pub fn into_generic(self) -> GenericMessage {
        GenericMessage {
            header: self.header,
            payload: GenericPayload::new(self.payload),
        }
    }

    pub fn response<R: MessageTypeStatic>(&self, msg: R) -> Message<GenericPayload> {
        Message {
            header: MessageHeader {
                receiver: self.header.sender.to_string(),
                sender: Uuid::parse_str(&self.header.receiver).unwrap_or(Uuid::new_v4()),
                id: Uuid::new_v4(),
                response_to: Some(self.header.id),
                message_name: <R as MessageTypeStatic>::message_type_name().to_string(),
            },
            payload: GenericPayload::new(msg),
        }
    }

    pub fn new(receiver: String, sender: Uuid, payload: T) -> Self {
        Self {
            header: MessageHeader {
                receiver,
                sender,
                id: Uuid::new_v4(),
                message_name: payload.message_type_name().to_string(),
                response_to: None,
            },
            payload,
        }
    }
}

#[derive(Debug, Clone)]
pub struct GenericPayload {
    inner: Arc<dyn MessageType>,
}

impl UnqualifiedMessage for GenericPayload {}

impl Serialize for GenericPayload {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        self.inner.to_json().serialize(serializer)
    }
}

impl GenericPayload {
    pub fn new(message: impl MessageType) -> Self {
        Self {
            inner: Arc::new(message),
        }
    }

    pub fn new_arc(message: Arc<dyn MessageType>) -> Self {
        Self { inner: message }
    }
}

pub type GenericMessage = Message<GenericPayload>;

impl GenericMessage {
    /// Custom deserialization that consults the message registry
    pub fn deserialize_with_registry(
        json_str: &str,
    ) -> Result<Self, Box<dyn std::error::Error + Send + Sync>> {
        #[derive(Debug, Serialize, Deserialize, Clone)]
        struct GenericMessageWrapper {
            #[serde(flatten)]
            header: MessageHeader,

            payload: serde_json::Value,
        }

        let generic_message_wrapper = serde_json::from_str::<GenericMessageWrapper>(json_str)?;
        let header = generic_message_wrapper.header;
        let payload = generic_message_wrapper.payload;

        debug!("Deserializing message header: {:?}", header);
        #[derive(Clone, Debug)]
        struct UnregisteredMessage {
            data: serde_json::Value,
        }

        impl UnqualifiedMessage for UnregisteredMessage {}

        impl MessageType for UnregisteredMessage {
            fn message_type_name(&self) -> &'static str {
                "UnregisteredMessage"
            }

            fn to_json(&self) -> serde_json::Value {
                self.data.clone()
            }
        }

        Ok(GenericMessage {
            header,
            payload: GenericPayload::new(UnregisteredMessage { data: payload }),
        })
    }

    pub fn to_json(&self) -> serde_json::Value {
        let mut header = serde_json::to_value(&self.header).unwrap();
        header
            .as_object_mut()
            .unwrap()
            .insert("payload".to_string(), self.payload.to_json());
        header
    }

    pub fn downcast<T>(self) -> Result<Message<T>, Self>
    where
        T: MessageTypeStatic + DeserializeOwned,
    {
        let message_type = <T as MessageTypeStatic>::message_type_name();
        let orig = self.payload.inner.clone();
        if message_type != self.header.message_name {
            return Err(Self {
                header: self.header,
                payload: GenericPayload::new_arc(orig),
            });
        }

        let json = self.payload.to_json();
        let Ok(payload) = serde_json::from_value(json) else {
            return Err(Self {
                header: self.header,
                payload: GenericPayload::new_arc(orig),
            });
        };

        Ok(Message {
            header: self.header,
            payload,
        })
    }
}

pub trait MessagePeer {
    /// Subscribe to a specific message type with a typed handler
    fn on_message<T: MessageTypeStatic + DeserializeOwned + Clone, F>(&self, handler: F)
    where
        F: Fn(Message<T>) -> Option<GenericMessage> + Send + Sync + 'static;

    /// Subscribe to all messages with a generic handler
    fn on_all_messages<F>(&self, handler: F)
    where
        F: Fn(GenericMessage) -> Option<GenericMessage> + Send + Sync + 'static;

    /// Send a message to another client
    fn send_message<T: MessageType + Serialize>(
        &self,
        receiver: &str,
        payload: T,
    ) -> Result<(), Box<dyn std::error::Error>>;
}
