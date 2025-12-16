use std::error::Error;
use std::fmt::{self, Display};

#[derive(Debug)]
pub struct MetatermError {
    pub message: String,
    pub cause: Option<Box<dyn std::error::Error + Send + Sync + 'static>>,
}

impl MetatermError {
    pub fn cause(
        message: String,
        cause: Option<Box<dyn std::error::Error + Send + Sync + 'static>>,
    ) -> Self {
        Self { message, cause }
    }

    pub fn io(message: String, cause: std::io::Error) -> std::io::Error {
        std::io::Error::new(
            cause.kind(),
            MetatermError::cause(message, Some(Box::new(cause))),
        )
    }
}

impl Error for MetatermError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        self.cause
            .as_ref()
            .map(|e| e.as_ref() as &(dyn Error + 'static))
    }
}

impl Display for MetatermError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.message)
    }
}
