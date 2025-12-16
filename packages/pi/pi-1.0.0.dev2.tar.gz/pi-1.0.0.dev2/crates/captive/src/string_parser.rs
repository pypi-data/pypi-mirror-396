use std::error::Error;
use std::fmt;

#[derive(Debug, Clone)]
pub enum StringParseError {
    UnexpectedEndOfString,
    InvalidEscapeSequence(char),
    InvalidUnicodeEscape(String),
    InvalidHexEscape(String),
}

impl fmt::Display for StringParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            StringParseError::UnexpectedEndOfString => {
                write!(f, "Unexpected end of string")
            }
            StringParseError::InvalidEscapeSequence(c) => {
                write!(f, "Invalid escape sequence: \\{}", c)
            }
            StringParseError::InvalidUnicodeEscape(s) => {
                write!(f, "Invalid unicode escape: \\u{{{}}}", s)
            }
            StringParseError::InvalidHexEscape(s) => {
                write!(f, "Invalid hex escape: \\x{}", s)
            }
        }
    }
}

impl Error for StringParseError {}

/// Parse a Rust string literal, handling all standard escape sequences
pub fn parse_rust_string(input: &str) -> Result<String, StringParseError> {
    let mut chars = input.chars().peekable();
    let mut result = String::new();

    while let Some(ch) = chars.next() {
        match ch {
            '\\' => {
                let escaped = parse_escape_sequence(&mut chars)?;
                result.push(escaped);
            }
            _ => {
                result.push(ch);
            }
        }
    }

    Ok(result)
}

fn parse_escape_sequence<I>(chars: &mut std::iter::Peekable<I>) -> Result<char, StringParseError>
where
    I: Iterator<Item = char>,
{
    let next_char = chars
        .next()
        .ok_or(StringParseError::UnexpectedEndOfString)?;

    match next_char {
        // Simple escapes
        'n' => Ok('\n'),
        'r' => Ok('\r'),
        't' => Ok('\t'),
        '\\' => Ok('\\'),
        '\'' => Ok('\''),
        '"' => Ok('"'),

        // Null character (special case)
        '0' => {
            // Check if the next character is a digit (0-7), which would make this an octal escape
            if let Some(&next_ch) = chars.peek() {
                if next_ch.is_ascii_digit() && next_ch < '8' {
                    // This is an octal escape, which is not supported
                    Err(StringParseError::InvalidEscapeSequence(next_char))
                } else {
                    // This is just \0
                    Ok('\0')
                }
            } else {
                // End of string, this is just \0
                Ok('\0')
            }
        }

        // Unicode escapes
        'u' => parse_unicode_escape(chars),

        // Hex escapes
        'x' => parse_hex_escape(chars),

        // Octal escapes (deprecated in Rust, not supported)
        '1'..='7' => {
            // In modern Rust, this would be an error, but for compatibility
            // we'll treat it as an invalid escape sequence
            Err(StringParseError::InvalidEscapeSequence(next_char))
        }

        // Invalid escape
        _ => Err(StringParseError::InvalidEscapeSequence(next_char)),
    }
}

fn parse_unicode_escape<I>(chars: &mut std::iter::Peekable<I>) -> Result<char, StringParseError>
where
    I: Iterator<Item = char>,
{
    // Expect opening brace
    let brace = chars
        .next()
        .ok_or(StringParseError::UnexpectedEndOfString)?;
    if brace != '{' {
        return Err(StringParseError::InvalidUnicodeEscape(format!(
            "missing opening brace, got '{}'",
            brace
        )));
    }

    let mut hex_str = String::new();

    // Read hex digits
    while let Some(&ch) = chars.peek() {
        if ch.is_ascii_hexdigit() {
            hex_str.push(chars.next().unwrap());
        } else if ch == '}' {
            chars.next(); // consume the closing brace
            break;
        } else {
            return Err(StringParseError::InvalidUnicodeEscape(format!(
                "invalid character in unicode escape: '{}'",
                ch
            )));
        }
    }

    if hex_str.is_empty() {
        return Err(StringParseError::InvalidUnicodeEscape(
            "empty unicode escape".to_string(),
        ));
    }

    // Parse hex value
    let code_point = u32::from_str_radix(&hex_str, 16)
        .map_err(|_| StringParseError::InvalidUnicodeEscape(hex_str.clone()))?;

    // Convert to char
    char::from_u32(code_point).ok_or_else(|| {
        StringParseError::InvalidUnicodeEscape(format!(
            "invalid unicode code point: {}",
            code_point
        ))
    })
}

fn parse_hex_escape<I>(chars: &mut std::iter::Peekable<I>) -> Result<char, StringParseError>
where
    I: Iterator<Item = char>,
{
    let mut hex_str = String::new();

    // Read exactly 2 hex digits
    for _ in 0..2 {
        let ch = chars
            .next()
            .ok_or(StringParseError::UnexpectedEndOfString)?;
        if ch.is_ascii_hexdigit() {
            hex_str.push(ch);
        } else {
            return Err(StringParseError::InvalidHexEscape(format!(
                "invalid hex digit: '{}'",
                ch
            )));
        }
    }

    // Parse hex value
    let byte_value = u8::from_str_radix(&hex_str, 16)
        .map_err(|_| StringParseError::InvalidHexEscape(hex_str.clone()))?;

    Ok(byte_value as char)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_escapes() {
        assert_eq!(parse_rust_string("\\n").unwrap(), "\n");
        assert_eq!(parse_rust_string("\\r").unwrap(), "\r");
        assert_eq!(parse_rust_string("\\t").unwrap(), "\t");
        assert_eq!(parse_rust_string("\\\\").unwrap(), "\\");
        assert_eq!(parse_rust_string("\\0").unwrap(), "\0");
        assert_eq!(parse_rust_string("\\'").unwrap(), "'");
        assert_eq!(parse_rust_string("\\\"").unwrap(), "\"");
    }

    #[test]
    fn test_unicode_escapes() {
        assert_eq!(parse_rust_string("\\u{41}").unwrap(), "A");
        assert_eq!(parse_rust_string("\\u{1F600}").unwrap(), "😀");
        assert_eq!(parse_rust_string("\\u{20}").unwrap(), " ");
    }

    #[test]
    fn test_hex_escapes() {
        assert_eq!(parse_rust_string("\\x41").unwrap(), "A");
        assert_eq!(parse_rust_string("\\x20").unwrap(), " ");
        assert_eq!(parse_rust_string("\\x7F").unwrap(), "\x7F");
    }

    #[test]
    fn test_octal_escapes() {
        // Octal escapes are not supported in modern Rust
        assert!(parse_rust_string("\\101").is_err());
        assert!(parse_rust_string("\\040").is_err());
    }

    #[test]
    fn test_mixed_content() {
        assert_eq!(
            parse_rust_string("Hello\\nWorld\\t!").unwrap(),
            "Hello\nWorld\t!"
        );
        assert_eq!(
            parse_rust_string("\\u{48}ello\\x20World").unwrap(),
            "Hello World"
        );
    }

    #[test]
    fn test_no_escapes() {
        assert_eq!(parse_rust_string("Hello World").unwrap(), "Hello World");
        assert_eq!(parse_rust_string("").unwrap(), "");
    }

    #[test]
    fn test_error_cases() {
        assert!(parse_rust_string("\\").is_err());
        assert!(parse_rust_string("\\x").is_err());
        assert!(parse_rust_string("\\xG").is_err());
        assert!(parse_rust_string("\\u{").is_err());
        assert!(parse_rust_string("\\u{G}").is_err());
        assert!(parse_rust_string("\\u{}").is_err());
        assert!(parse_rust_string("\\z").is_err());
    }

    #[test]
    fn test_comprehensive_examples() {
        // Test all supported escape sequences
        assert_eq!(parse_rust_string("Hello\\nWorld").unwrap(), "Hello\nWorld");
        assert_eq!(
            parse_rust_string("Tab\\tseparated").unwrap(),
            "Tab\tseparated"
        );
        assert_eq!(
            parse_rust_string("Carriage\\rreturn").unwrap(),
            "Carriage\rreturn"
        );
        assert_eq!(
            parse_rust_string("Backslash\\\\test").unwrap(),
            "Backslash\\test"
        );
        assert_eq!(
            parse_rust_string("Null\\0terminated").unwrap(),
            "Null\0terminated"
        );
        assert_eq!(parse_rust_string("Quote\\\"test").unwrap(), "Quote\"test");
        assert_eq!(
            parse_rust_string("Apostrophe\\'test").unwrap(),
            "Apostrophe'test"
        );

        // Unicode escapes
        assert_eq!(parse_rust_string("\\u{41}BC").unwrap(), "ABC");
        assert_eq!(parse_rust_string("\\u{1F600}").unwrap(), "😀");
        assert_eq!(parse_rust_string("\\u{20}space").unwrap(), " space");

        // Hex escapes
        assert_eq!(parse_rust_string("\\x41BC").unwrap(), "ABC");
        assert_eq!(parse_rust_string("\\x20space").unwrap(), " space");

        // Mixed content
        assert_eq!(
            parse_rust_string("Hello\\n\\u{57}orld\\t!\\x21").unwrap(),
            "Hello\nWorld\t!!"
        );

        // No escapes
        assert_eq!(parse_rust_string("Plain text").unwrap(), "Plain text");
        assert_eq!(parse_rust_string("").unwrap(), "");
    }
}
