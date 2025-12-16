use std::collections::HashMap;

/// Parse a key string into the appropriate stdin escape sequence
pub fn parse_key(key: &str) -> Result<Vec<u8>, String> {
    let key = key.trim().to_lowercase();

    // Common key mappings
    let mut key_map: HashMap<&str, &[u8]> = HashMap::new();

    // Control keys
    key_map.insert("ctrl+a", b"\x01");
    key_map.insert("ctrl+b", b"\x02");
    key_map.insert("ctrl+c", b"\x03");
    key_map.insert("ctrl+d", b"\x04");
    key_map.insert("ctrl+e", b"\x05");
    key_map.insert("ctrl+f", b"\x06");
    key_map.insert("ctrl+g", b"\x07");
    key_map.insert("ctrl+h", b"\x08");
    key_map.insert("ctrl+i", b"\x09");
    key_map.insert("ctrl+j", b"\x0a");
    key_map.insert("ctrl+k", b"\x0b");
    key_map.insert("ctrl+l", b"\x0c");
    key_map.insert("ctrl+m", b"\x0d");
    key_map.insert("ctrl+n", b"\x0e");
    key_map.insert("ctrl+o", b"\x0f");
    key_map.insert("ctrl+p", b"\x10");
    key_map.insert("ctrl+q", b"\x11");
    key_map.insert("ctrl+r", b"\x12");
    key_map.insert("ctrl+s", b"\x13");
    key_map.insert("ctrl+t", b"\x14");
    key_map.insert("ctrl+u", b"\x15");
    key_map.insert("ctrl+v", b"\x16");
    key_map.insert("ctrl+w", b"\x17");
    key_map.insert("ctrl+x", b"\x18");
    key_map.insert("ctrl+y", b"\x19");
    key_map.insert("ctrl+z", b"\x1a");

    // Special keys
    key_map.insert("escape", b"\x1b");
    key_map.insert("esc", b"\x1b");
    key_map.insert("tab", b"\x09");
    key_map.insert("enter", b"\x0d");
    key_map.insert("return", b"\x0d");
    key_map.insert("backspace", b"\x08");
    key_map.insert("delete", b"\x7f");
    key_map.insert("space", b" ");

    // Arrow keys (simplified - in a real terminal these would be escape sequences)
    key_map.insert("up", b"\x1b[A");
    key_map.insert("down", b"\x1b[B");
    key_map.insert("right", b"\x1b[C");
    key_map.insert("left", b"\x1b[D");

    // Function keys
    key_map.insert("f1", b"\x1bOP");
    key_map.insert("f2", b"\x1bOQ");
    key_map.insert("f3", b"\x1bOR");
    key_map.insert("f4", b"\x1bOS");
    key_map.insert("f5", b"\x1b[15~");
    key_map.insert("f6", b"\x1b[17~");
    key_map.insert("f7", b"\x1b[18~");
    key_map.insert("f8", b"\x1b[19~");
    key_map.insert("f9", b"\x1b[20~");
    key_map.insert("f10", b"\x1b[21~");
    key_map.insert("f11", b"\x1b[23~");
    key_map.insert("f12", b"\x1b[24~");

    // Check if it's a mapped key
    if let Some(&bytes) = key_map.get(key.as_str()) {
        return Ok(bytes.to_vec());
    }

    // If it's a single character, return it as bytes
    if key.len() == 1 {
        return Ok(key.as_bytes().to_vec());
    }

    // If it's a quoted string, treat it as literal text
    if (key.starts_with('"') && key.ends_with('"'))
        || (key.starts_with('\'') && key.ends_with('\''))
    {
        let content = &key[1..key.len() - 1];
        return Ok(content.as_bytes().to_vec());
    }

    Err(format!("Unknown key: {}", key))
}

/// Parse multiple keys and return their combined byte sequences
pub fn parse_keys(keys: &[String]) -> Result<Vec<u8>, String> {
    let mut result = Vec::new();

    for key in keys {
        let bytes = parse_key(key)?;
        result.extend(bytes);
    }

    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_single_key() {
        assert_eq!(parse_key("a").unwrap(), b"a");
        assert_eq!(parse_key("escape").unwrap(), b"\x1b");
        assert_eq!(parse_key("ctrl+c").unwrap(), b"\x03");
        assert_eq!(parse_key("enter").unwrap(), b"\x0d");
    }

    #[test]
    fn test_parse_multiple_keys() {
        let keys = vec!["ctrl+k".to_string(), "escape".to_string()];
        let result = parse_keys(&keys).unwrap();
        assert_eq!(result, vec![0x0b, 0x1b]);
    }

    #[test]
    fn test_parse_quoted_string() {
        assert_eq!(parse_key("\"hello\"").unwrap(), b"hello");
        assert_eq!(parse_key("'world'").unwrap(), b"world");
    }
}
