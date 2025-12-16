//! Development tool detection for Rust projects
//!
//! This module provides functionality to detect Rust development tools
//! like formatters (rustfmt), linters (clippy), security tools (cargo-audit, cargo-deny),
//! and other development utilities.

use pi_lang::{DetectedTool, ToolType};
use std::path::Path;
use tracing::debug;

/// Known development tool configuration files and their patterns
/// Format: (filename, `tool_name`, confidence)
static DEV_TOOL_CONFIG_FILES: &[(&str, &str, f64)] = &[
    ("rustfmt.toml", "rustfmt", 0.95),
    (".rustfmt.toml", "rustfmt", 0.95),
    ("clippy.toml", "clippy", 0.95),
    (".clippy.toml", "clippy", 0.95),
    ("deny.toml", "cargo-deny", 0.95),
    (".deny.toml", "cargo-deny", 0.95),
    ("audit.toml", "cargo-audit", 0.90),
    (".audit.toml", "cargo-audit", 0.90),
    ("nextest.toml", "cargo-nextest", 0.95),
    (".nextest.toml", "cargo-nextest", 0.95),
    ("cargo-doc.toml", "cargo-doc", 0.85),
    ("tarpaulin.toml", "cargo-tarpaulin", 0.90),
    ("flamegraph.toml", "cargo-flamegraph", 0.85),
    ("criterion.toml", "criterion", 0.85),
];

pub fn detect_dev_tools<P: AsRef<Path>>(dir: P) -> Vec<DetectedTool> {
    let mut detected = Vec::new();
    let dir = dir.as_ref();

    debug!(
        "Scanning for Rust development tool config files in {:?}",
        dir
    );

    // Check for direct configuration files
    for &(filename, tool_name, confidence) in DEV_TOOL_CONFIG_FILES {
        let config_path = dir.join(filename);
        if config_path.is_file() {
            // Get all tool types for this tool (some tools serve multiple purposes)
            let tool_types = get_tool_types(tool_name);
            for &tool_type in &tool_types {
                detected.push(DetectedTool {
                    tool_type,
                    name: tool_name.to_string(),
                    confidence,
                    evidence: vec![filename.to_string()],
                });
            }
        }
    }

    // Deduplicate by tool name and type, keeping highest confidence
    deduplicate_tools_by_name_and_type(detected)
}

/// Detect standard Rust tools that are implied by Cargo.toml existence.
/// These tools are part of the standard Rust toolchain.
pub fn detect_implied_rust_tools() -> Vec<DetectedTool> {
    vec![
        DetectedTool {
            tool_type: ToolType::Formatter,
            name: "rustfmt".to_string(),
            confidence: 0.80, // Lower confidence as it's implied, not explicitly configured
            evidence: vec!["Cargo.toml (implied)".to_string()],
        },
        DetectedTool {
            tool_type: ToolType::Diagnostic,
            name: "clippy".to_string(),
            confidence: 0.80, // Lower confidence as it's implied, not explicitly configured
            evidence: vec!["Cargo.toml (implied)".to_string()],
        },
    ]
}

/// Return the appropriate ToolType(s) for a given tool name.
fn get_tool_types(tool_name: &str) -> Vec<ToolType> {
    match tool_name {
        "rustfmt" => vec![ToolType::Formatter],

        "cargo-nextest" | "criterion" | "cargo-tarpaulin" => vec![ToolType::Testing],

        "cargo-doc" => vec![ToolType::Documentation],

        _ => vec![ToolType::Diagnostic],
    }
}

fn deduplicate_tools_by_name_and_type(tools: Vec<DetectedTool>) -> Vec<DetectedTool> {
    use std::collections::HashMap;

    let mut tool_map: HashMap<(String, ToolType), DetectedTool> = HashMap::new();

    for tool in tools {
        let key = (tool.name.clone(), tool.tool_type);
        match tool_map.get(&key) {
            Some(existing) if existing.confidence >= tool.confidence => {
                // Keep existing tool (higher or equal confidence)
            }
            _ => {
                // Replace with new tool (higher confidence) or insert new tool
                tool_map.insert(key, tool);
            }
        }
    }

    tool_map.into_values().collect()
}

/// Bump confidence for standard tools when their config files are found.
pub fn bump_tool_confidence(
    mut tools: Vec<DetectedTool>,
    config_tools: &[DetectedTool],
) -> Vec<DetectedTool> {
    for config_tool in config_tools {
        // Find matching tool in the existing tools list
        if let Some(existing_tool) = tools
            .iter_mut()
            .find(|t| t.name == config_tool.name && t.tool_type == config_tool.tool_type)
        {
            // If we found a config file, use the higher confidence and merge evidence
            if config_tool.confidence > existing_tool.confidence {
                existing_tool.confidence = config_tool.confidence;
                existing_tool.evidence.clone_from(&config_tool.evidence);
            }
        } else {
            // Add the config tool if it wasn't in the implied tools
            tools.push(config_tool.clone());
        }
    }

    // Re-deduplicate after bumping confidence
    deduplicate_tools_by_name_and_type(tools)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_detect_rustfmt_config() {
        let temp_dir = TempDir::new().unwrap();
        let rustfmt_config = temp_dir.path().join("rustfmt.toml");
        fs::write(&rustfmt_config, "max_width = 100\ntab_spaces = 2\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 1);
        assert_eq!(detected[0].name, "rustfmt");
        assert_eq!(detected[0].tool_type, ToolType::Formatter);
        assert!((detected[0].confidence - 0.95).abs() < f64::EPSILON);
        assert!(detected[0].evidence.contains(&"rustfmt.toml".to_string()));
    }

    #[test]
    fn test_detect_clippy_config() {
        let temp_dir = TempDir::new().unwrap();
        let clippy_config = temp_dir.path().join("clippy.toml");
        fs::write(&clippy_config, "cyclomatic-complexity-threshold = 25\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 1);
        assert_eq!(detected[0].name, "clippy");
        assert_eq!(detected[0].tool_type, ToolType::Diagnostic);
        assert!((detected[0].confidence - 0.95).abs() < f64::EPSILON);
    }

    #[test]
    fn test_detect_cargo_deny_config() {
        let temp_dir = TempDir::new().unwrap();
        let deny_config = temp_dir.path().join("deny.toml");
        fs::write(
            &deny_config,
            "[licenses]\nallow = [\"MIT\", \"Apache-2.0\"]\n",
        )
        .unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 1);
        assert_eq!(detected[0].name, "cargo-deny");
        assert_eq!(detected[0].tool_type, ToolType::Diagnostic);
        assert!((detected[0].confidence - 0.95).abs() < f64::EPSILON);
    }

    #[test]
    fn test_detect_multiple_tools() {
        let temp_dir = TempDir::new().unwrap();

        // Create multiple config files
        fs::write(temp_dir.path().join("rustfmt.toml"), "max_width = 100\n").unwrap();
        fs::write(
            temp_dir.path().join("clippy.toml"),
            "cyclomatic-complexity-threshold = 25\n",
        )
        .unwrap();
        fs::write(
            temp_dir.path().join("deny.toml"),
            "[licenses]\nallow = [\"MIT\"]\n",
        )
        .unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 3);

        let tool_names: Vec<&str> = detected.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"rustfmt"));
        assert!(tool_names.contains(&"clippy"));
        assert!(tool_names.contains(&"cargo-deny"));
    }

    #[test]
    fn test_detect_implied_rust_tools() {
        let implied = detect_implied_rust_tools();
        assert_eq!(implied.len(), 2);

        let tool_names: Vec<&str> = implied.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"rustfmt"));
        assert!(tool_names.contains(&"clippy"));

        // All implied tools should have moderate confidence
        for tool in &implied {
            assert!((tool.confidence - 0.80).abs() < f64::EPSILON);
            assert!(tool.evidence.iter().any(|e| e.contains("implied")));
        }
    }

    #[test]
    fn test_bump_tool_confidence() {
        let implied_tools = detect_implied_rust_tools();

        // Create config tools with higher confidence
        let config_tools = vec![DetectedTool {
            tool_type: ToolType::Formatter,
            name: "rustfmt".to_string(),
            confidence: 0.95,
            evidence: vec!["rustfmt.toml".to_string()],
        }];

        let bumped_tools = bump_tool_confidence(implied_tools, &config_tools);

        // Should still have 2 tools
        assert_eq!(bumped_tools.len(), 2);

        // rustfmt should now have higher confidence
        let rustfmt_tool = bumped_tools.iter().find(|t| t.name == "rustfmt").unwrap();
        assert!((rustfmt_tool.confidence - 0.95).abs() < f64::EPSILON);
        assert!(rustfmt_tool.evidence.contains(&"rustfmt.toml".to_string()));

        // clippy should still have original confidence
        let clippy_tool = bumped_tools.iter().find(|t| t.name == "clippy").unwrap();
        assert!((clippy_tool.confidence - 0.80).abs() < f64::EPSILON);
    }

    #[test]
    fn test_deduplication_keeps_highest_confidence() {
        let tools = vec![
            DetectedTool {
                tool_type: ToolType::Formatter,
                name: "rustfmt".to_string(),
                confidence: 0.80,
                evidence: vec!["Cargo.toml (implied)".to_string()],
            },
            DetectedTool {
                tool_type: ToolType::Formatter,
                name: "rustfmt".to_string(),
                confidence: 0.95,
                evidence: vec!["rustfmt.toml".to_string()],
            },
        ];

        let deduplicated = deduplicate_tools_by_name_and_type(tools);
        assert_eq!(deduplicated.len(), 1);
        assert!((deduplicated[0].confidence - 0.95).abs() < f64::EPSILON);
        assert!(
            deduplicated[0]
                .evidence
                .contains(&"rustfmt.toml".to_string())
        );
    }

    #[test]
    fn test_empty_directory() {
        let temp_dir = TempDir::new().unwrap();
        let detected = detect_dev_tools(temp_dir.path());
        assert!(detected.is_empty());
    }

    #[test]
    fn test_hidden_config_files() {
        let temp_dir = TempDir::new().unwrap();

        // Create hidden config files
        fs::write(temp_dir.path().join(".rustfmt.toml"), "max_width = 100\n").unwrap();
        fs::write(
            temp_dir.path().join(".clippy.toml"),
            "cyclomatic-complexity-threshold = 25\n",
        )
        .unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 2);

        let tool_names: Vec<&str> = detected.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"rustfmt"));
        assert!(tool_names.contains(&"clippy"));
    }

    #[test]
    fn test_nextest_config() {
        let temp_dir = TempDir::new().unwrap();
        let nextest_config = temp_dir.path().join("nextest.toml");
        fs::write(&nextest_config, "[profile.default]\nretries = 2\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 1);
        assert_eq!(detected[0].name, "cargo-nextest");
        assert_eq!(detected[0].tool_type, ToolType::Testing);
        assert!((detected[0].confidence - 0.95).abs() < f64::EPSILON);
    }

    #[test]
    fn test_tarpaulin_config() {
        let temp_dir = TempDir::new().unwrap();
        let tarpaulin_config = temp_dir.path().join("tarpaulin.toml");
        fs::write(&tarpaulin_config, "[report]\nout = [\"Html\"]\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 1);
        assert_eq!(detected[0].name, "cargo-tarpaulin");
        assert_eq!(detected[0].tool_type, ToolType::Testing);
        assert!((detected[0].confidence - 0.90).abs() < f64::EPSILON);
    }
}
