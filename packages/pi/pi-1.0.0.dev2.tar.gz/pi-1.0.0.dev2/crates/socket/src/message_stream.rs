use tracing::debug;

use std::io::{BufRead, BufReader, Read};

/// A message reader stream that yields messages using blocking reads
pub struct MessageReaderStream<R> {
    reader: BufReader<R>,
}

impl<R: Read> MessageReaderStream<R> {
    /// Create a new message reader stream
    pub fn new(reader: R) -> Self {
        Self {
            reader: BufReader::new(reader),
        }
    }

    /// Read the next message from the stream (blocking)
    pub fn next_message(
        &mut self,
    ) -> Result<Option<crate::messages::GenericMessage>, Box<dyn std::error::Error + Send + Sync>>
    {
        let mut buffer = Vec::new();

        // Read until NUL terminator
        let bytes_read = self.reader.read_until(0, &mut buffer)?;
        if bytes_read == 0 {
            return Ok(None); // EOF
        }

        // Remove NUL terminator
        if buffer.ends_with(&[0]) {
            buffer.pop();
        }

        // Convert to string
        let json_str = String::from_utf8(buffer)?;
        debug!("Received message: {}", json_str);

        // Use custom deserializer that consults the registry
        let message = crate::messages::GenericMessage::deserialize_with_registry(&json_str)?;
        Ok(Some(message))
    }

    /// Read all messages from the stream
    pub fn read_all(
        &mut self,
    ) -> Result<Vec<crate::messages::GenericMessage>, Box<dyn std::error::Error + Send + Sync>>
    {
        let mut messages = Vec::new();

        while let Some(message) = self.next_message()? {
            messages.push(message);
        }

        Ok(messages)
    }
}

/// Convenience function to create a message reader stream from any reader
pub fn create_message_stream<R: Read>(reader: R) -> MessageReaderStream<R> {
    MessageReaderStream::new(reader)
}

/// Extension trait for readers to add message reading capabilities
pub trait MessageReaderExt<R: Read> {
    fn into_message_stream(self) -> MessageReaderStream<R>;
}

impl<R: Read> MessageReaderExt<R> for R {
    fn into_message_stream(self) -> MessageReaderStream<R> {
        MessageReaderStream::new(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::io::Cursor;

    #[test]
    fn test_message_stream() {
        // Create test message
        let message = json!({
            "receiver": "test",
            "sender": "00000000-0000-0000-0000-000000000000",
            "id": "00000000-0000-0000-0000-000000000000",
            "response_to": null,
            "message_name": "GenericMessage",
            "payload": {"data": "test"}
        });

        let mut message_bytes = message.to_string().into_bytes();
        message_bytes.push(0); // Add NUL terminator

        let cursor = Cursor::new(message_bytes);
        let mut stream = MessageReaderStream::new(cursor);

        let result = stream.next_message().unwrap();
        assert!(result.is_some());

        let message = result.unwrap();
        // Just verify we got a message, don't call message_type_name() since it's not available
        assert!(message.header.message_name == "GenericMessage");
    }
}
