use pi_lang::{DetectedTool, ToolType};
use std::path::Path;
use tracing::debug;
/// Known development tool configuration files and their confidence scores
/// Format: (filename, `tool_name`, confidence)
static DEV_TOOL_CONFIG_FILES: &[(&str, &str, f64)] = &[
    // Type checkers
    ("mypy.ini", "mypy", 0.95),
    (".mypy.ini", "mypy", 0.95),
    ("pyproject.toml", "mypy", 0.85), // Will be handled separately
    ("pyrightconfig.json", "pyright", 0.95),
    (".pyrightconfig.json", "pyright", 0.95),
    ("pyre.configuration", "pyre", 0.95),
    (".pyre_configuration", "pyre", 0.95),
    // Linters and formatters
    ("ruff.toml", "ruff", 0.95),
    (".ruff.toml", "ruff", 0.95),
    ("setup.cfg", "ruff", 0.70), // Multi-tool config, lower confidence
    ("tox.ini", "ruff", 0.70),   // Multi-tool config, lower confidence
    (".flake8", "flake8", 0.95),
    ("setup.cfg", "flake8", 0.70), // Multi-tool config, lower confidence
    ("tox.ini", "flake8", 0.70),   // Multi-tool config, lower confidence
    (".pylintrc", "pylint", 0.95),
    ("pylintrc", "pylint", 0.95),
    (".isort.cfg", "isort", 0.95),
    ("isort.ini", "isort", 0.90),
    (".bandit", "bandit", 0.95),
    ("bandit.yaml", "bandit", 0.90),
    ("bandit.yml", "bandit", 0.90),
    // Testing tools
    ("pytest.ini", "pytest", 0.95),
    (".pytest.ini", "pytest", 0.95),
    ("tox.ini", "tox", 0.95),
    ("noxfile.py", "nox", 0.95),
    ("noxfile-py", "nox", 0.85),
    // Documentation tools
    ("conf.py", "sphinx", 0.90), // Sphinx configuration
    ("mkdocs.yml", "mkdocs", 0.95),
    ("mkdocs.yaml", "mkdocs", 0.95),
    // Coverage tools
    (".coveragerc", "coverage", 0.95),
    ("coverage.ini", "coverage", 0.90),
];
/// Tool sections that can appear in pyproject.toml
/// Format: (`section_name`, `tool_name`)
static PYPROJECT_DEV_TOOLS: &[(&str, &str)] = &[
    // Type checkers
    ("mypy", "mypy"),
    ("pyright", "pyright"),
    ("pyre", "pyre"),
    // Linters and formatters
    ("ruff", "ruff"),
    ("flake8", "flake8"),
    ("pylint", "pylint"),
    ("isort", "isort"),
    ("black", "black"),
    ("autopep8", "autopep8"),
    ("yapf", "yapf"),
    ("bandit", "bandit"),
    ("pytest", "pytest"),
    ("coverage", "coverage"),
    ("coverage:run", "coverage"),
    ("coverage:report", "coverage"),
    ("coverage:html", "coverage"),
    // Documentation tools
    ("sphinx", "sphinx"),
    // Other development tools
    ("semantic_release", "python-semantic-release"),
];
/// Detect development tools from configuration files in a directory.
pub(crate) fn detect_dev_tools<P: AsRef<Path>>(dir: P) -> Vec<DetectedTool> {
    let mut detected = Vec::new();
    let dir = dir.as_ref();

    debug!("Scanning for development tool config files in {:?}", dir);

    for &(filename, tool_name, confidence) in DEV_TOOL_CONFIG_FILES {
        let config_path = dir.join(filename);
        if config_path.is_file() {
            // For multi-tool config files, verify the tool is actually configured
            let actual_confidence = if matches!(filename, "setup.cfg" | "tox.ini") {
                verify_tool_in_config_file(&config_path, tool_name, confidence)
            } else {
                confidence
            };

            if actual_confidence > 0.0 {
                // Some tools serve multiple purposes (e.g., ruff does linting and formatting)
                let tool_types = get_tool_types(tool_name);
                for &tool_type in &tool_types {
                    detected.push(DetectedTool {
                        tool_type,
                        name: tool_name.to_string(),
                        confidence: actual_confidence,
                        evidence: vec![filename.to_string()],
                    });
                }
            }
        }
    }

    deduplicate_tools_by_name_and_type(detected)
}
/// Detect development tools from pyproject.toml [tool.*] sections.
pub(crate) fn detect_dev_tools_from_pyproject(
    tool_sections: &std::collections::HashMap<String, toml::Value>,
) -> Vec<DetectedTool> {
    let mut detected = Vec::new();

    for section_name in tool_sections.keys() {
        if let Some(tool_name) = find_dev_tool_name(section_name) {
            // Some tools serve multiple purposes (e.g., ruff does linting and formatting)
            let tool_types = get_tool_types(tool_name);
            for &tool_type in &tool_types {
                detected.push(DetectedTool {
                    tool_type,
                    name: tool_name.to_string(),
                    confidence: 0.90, // High confidence for explicit pyproject.toml sections
                    evidence: vec![format!("pyproject.toml:[tool.{}]", section_name)],
                });
            }
        }
    }

    deduplicate_tools_by_name_and_type(detected)
}
/// Map pyproject.toml [tool.*] section names to development tool names.
fn find_dev_tool_name(section_name: &str) -> Option<&str> {
    // Direct matches
    for &(pattern, tool_name) in PYPROJECT_DEV_TOOLS {
        if pattern == section_name {
            return Some(tool_name);
        }
    }
    // Handle sub-sections (e.g., coverage:run, mypy-path)
    for &(pattern, tool_name) in PYPROJECT_DEV_TOOLS {
        if pattern.contains(':') {
            let base_pattern = pattern.split(':').next().unwrap();
            if section_name.starts_with(base_pattern) {
                return Some(tool_name);
            }
        } else if section_name.starts_with(&format!("{pattern}-")) {
            // Handle tool-specific sub-sections like "mypy-path"
            return Some(tool_name);
        }
    }

    None
}
/// Verify if a tool is actually configured in a multi-tool config file.
fn verify_tool_in_config_file(config_path: &Path, tool_name: &str, base_confidence: f64) -> f64 {
    let Ok(content) = std::fs::read_to_string(config_path) else {
        return 0.0;
    };

    let lower_content = content.to_lowercase();
    let tool_patterns = get_tool_patterns(tool_name);
    let found = tool_patterns
        .iter()
        .any(|pattern| lower_content.contains(&pattern.to_lowercase()));

    if found { base_confidence * 0.8 } else { 0.0 }
}
/// Return search patterns for a tool in config files.
fn get_tool_patterns(tool_name: &str) -> Vec<String> {
    match tool_name {
        "ruff" => vec!["[ruff]", "ruff ", "select =", "ignore ="]
            .into_iter()
            .map(String::from)
            .collect(),
        "flake8" => vec!["[flake8]", "flake8", "max-line-length", "exclude ="]
            .into_iter()
            .map(String::from)
            .collect(),
        "mypy" => vec!["[mypy]", "mypy", "python_version", "disallow_untyped"]
            .into_iter()
            .map(String::from)
            .collect(),
        "pylint" => vec!["[pylint]", "pylint", "disable =", "enable ="]
            .into_iter()
            .map(String::from)
            .collect(),
        "isort" => vec!["[isort]", "isort", "profile =", "multi_line_output"]
            .into_iter()
            .map(String::from)
            .collect(),
        "black" => vec!["[black]", "black", "line-length", "target-version"]
            .into_iter()
            .map(String::from)
            .collect(),
        "coverage" => vec!["[coverage]", "coverage", "source =", "omit ="]
            .into_iter()
            .map(String::from)
            .collect(),
        "pytest" => vec!["[pytest]", "pytest", "testpaths", "python_files"]
            .into_iter()
            .map(String::from)
            .collect(),
        "bandit" => vec!["[bandit]", "bandit", "skips =", "exclude_dirs"]
            .into_iter()
            .map(String::from)
            .collect(),
        _ => vec![tool_name.to_string()],
    }
}
/// Return the appropriate ToolType(s) for a given tool name.
/// Some tools like ruff serve multiple purposes.
fn get_tool_types(tool_name: &str) -> Vec<ToolType> {
    match tool_name {
        "black" | "autopep8" | "yapf" | "isort" => vec![ToolType::Formatter],

        "ruff" => vec![ToolType::Diagnostic, ToolType::Formatter],
        "pytest" | "coverage" => vec![ToolType::Testing],

        "sphinx" | "mkdocs" => vec![ToolType::Documentation],

        _ => vec![ToolType::Diagnostic],
    }
}
/// Deduplicate detected tools by name and type, keeping the one with highest confidence.
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_detect_mypy_config() {
        let temp_dir = TempDir::new().unwrap();
        let mypy_config = temp_dir.path().join("mypy.ini");
        fs::write(&mypy_config, "[mypy]\npython_version = 3.9\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 1);
        assert_eq!(detected[0].name, "mypy");
        assert_eq!(detected[0].tool_type, ToolType::Diagnostic);
        assert!((detected[0].confidence - 0.95).abs() < f64::EPSILON);
        assert!(detected[0].evidence.contains(&"mypy.ini".to_string()));
    }

    #[test]
    fn test_detect_ruff_config() {
        let temp_dir = TempDir::new().unwrap();
        let ruff_config = temp_dir.path().join("ruff.toml");
        fs::write(&ruff_config, "line-length = 88\nselect = [\"E\", \"F\"]\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        // ruff should appear as both diagnostic and formatter
        assert_eq!(detected.len(), 2);

        let ruff_tools: Vec<_> = detected.iter().filter(|t| t.name == "ruff").collect();
        assert_eq!(ruff_tools.len(), 2);

        let tool_types: Vec<_> = ruff_tools.iter().map(|t| t.tool_type).collect();
        assert!(tool_types.contains(&ToolType::Diagnostic));
        assert!(tool_types.contains(&ToolType::Formatter));

        for tool in &ruff_tools {
            assert!((tool.confidence - 0.95).abs() < f64::EPSILON);
        }
    }

    #[test]
    fn test_detect_pytest_config() {
        let temp_dir = TempDir::new().unwrap();
        let pytest_config = temp_dir.path().join("pytest.ini");
        fs::write(&pytest_config, "[tool:pytest]\ntestpaths = tests\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 1);
        assert_eq!(detected[0].name, "pytest");
        assert_eq!(detected[0].tool_type, ToolType::Testing);
    }

    #[test]
    fn test_detect_multiple_tools() {
        let temp_dir = TempDir::new().unwrap();

        // Create multiple config files
        fs::write(temp_dir.path().join("mypy.ini"), "[mypy]\n").unwrap();
        fs::write(temp_dir.path().join("ruff.toml"), "line-length = 88\n").unwrap();
        fs::write(temp_dir.path().join("pytest.ini"), "[tool:pytest]\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        // mypy=1, ruff=2 (diagnostic+formatter), pytest=1 = 4 total
        assert_eq!(detected.len(), 4);

        let tool_names: Vec<&str> = detected.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"mypy"));
        assert!(tool_names.contains(&"ruff"));
        assert!(tool_names.contains(&"pytest"));
    }

    #[test]
    fn test_verify_tool_in_setup_cfg() {
        let temp_dir = TempDir::new().unwrap();
        let setup_cfg = temp_dir.path().join("setup.cfg");

        // setup.cfg with flake8 configuration
        fs::write(
            &setup_cfg,
            "[metadata]\nname = mypackage\n\n[flake8]\nmax-line-length = 88\n",
        )
        .unwrap();

        let detected = detect_dev_tools(temp_dir.path());

        // Should detect flake8 from setup.cfg
        let flake8_tools: Vec<_> = detected.iter().filter(|t| t.name == "flake8").collect();
        assert!(!flake8_tools.is_empty());
        assert!(flake8_tools[0].confidence > 0.0);
        assert!(flake8_tools[0].confidence < 0.95); // Reduced confidence for multi-tool file
    }

    #[test]
    fn test_setup_cfg_without_tool() {
        let temp_dir = TempDir::new().unwrap();
        let setup_cfg = temp_dir.path().join("setup.cfg");

        // setup.cfg without any diagnostic tool configuration
        fs::write(
            &setup_cfg,
            "[metadata]\nname = mypackage\nversion = 1.0.0\n",
        )
        .unwrap();

        let detected = detect_dev_tools(temp_dir.path());

        // Should not detect any tools from this setup.cfg
        assert!(detected.is_empty());
    }

    #[test]
    fn test_detect_from_pyproject_sections() {
        use std::collections::HashMap;

        let mut tool_sections = HashMap::new();
        tool_sections.insert("mypy".to_string(), toml::Value::Table(toml::Table::new()));
        tool_sections.insert("ruff".to_string(), toml::Value::Table(toml::Table::new()));
        tool_sections.insert("pytest".to_string(), toml::Value::Table(toml::Table::new()));

        let detected = detect_dev_tools_from_pyproject(&tool_sections);
        assert_eq!(detected.len(), 4); // ruff appears as both diagnostic and formatter

        let tool_names: Vec<&str> = detected.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"mypy"));
        assert!(tool_names.contains(&"ruff"));
        assert!(tool_names.contains(&"pytest"));

        // All should have high confidence and pyproject.toml evidence
        for tool in &detected {
            assert!((tool.confidence - 0.90).abs() < f64::EPSILON);
            assert!(tool.evidence.iter().any(|e| e.contains("pyproject.toml")));
        }
    }

    #[test]
    fn test_detect_coverage_subsections() {
        use std::collections::HashMap;

        let mut tool_sections = HashMap::new();
        tool_sections.insert(
            "coverage:run".to_string(),
            toml::Value::Table(toml::Table::new()),
        );
        tool_sections.insert(
            "coverage:report".to_string(),
            toml::Value::Table(toml::Table::new()),
        );

        let detected = detect_dev_tools_from_pyproject(&tool_sections);

        // Should detect coverage tool from both subsections but deduplicate
        let coverage_tools: Vec<_> = detected.iter().filter(|t| t.name == "coverage").collect();
        assert_eq!(coverage_tools.len(), 1);
        assert!((coverage_tools[0].confidence - 0.90).abs() < f64::EPSILON);
    }

    #[test]
    fn test_deduplication_keeps_highest_confidence() {
        let tools = vec![
            DetectedTool {
                tool_type: ToolType::Diagnostic,
                name: "mypy".to_string(),
                confidence: 0.85,
                evidence: vec!["pyproject.toml".to_string()],
            },
            DetectedTool {
                tool_type: ToolType::Diagnostic,
                name: "mypy".to_string(),
                confidence: 0.95,
                evidence: vec!["mypy.ini".to_string()],
            },
        ];

        let deduplicated = deduplicate_tools_by_name_and_type(tools);
        assert_eq!(deduplicated.len(), 1);
        assert!((deduplicated[0].confidence - 0.95).abs() < f64::EPSILON);
        assert!(deduplicated[0].evidence.contains(&"mypy.ini".to_string()));
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
        fs::write(temp_dir.path().join(".mypy.ini"), "[mypy]\n").unwrap();
        fs::write(temp_dir.path().join(".flake8"), "[flake8]\n").unwrap();

        let detected = detect_dev_tools(temp_dir.path());
        assert_eq!(detected.len(), 2);

        let tool_names: Vec<&str> = detected.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"mypy"));
        assert!(tool_names.contains(&"flake8"));
    }
}
