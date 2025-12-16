//! Detection logic for pyproject.toml files
//!
//! This module handles parsing and analyzing pyproject.toml files to detect
//! build backends and packaging tools based on the PLAN.md specifications.

use std::collections::HashMap;
use std::fs;
use std::path::Path;

use serde::Deserialize;
use tracing::warn;

use crate::devtools;
use pi_lang::{DetectedTool, ToolType};

/// Represents the structure of a pyproject.toml file for detection purposes
#[derive(Debug, Deserialize)]
struct PyProjectToml {
    #[serde(rename = "build-system")]
    build_system: Option<BuildSystem>,
    tool: Option<HashMap<String, toml::Value>>,
    project: Option<ProjectSection>,
}

/// Project section configuration from pyproject.toml
#[derive(Debug, Deserialize)]
struct ProjectSection {
    name: Option<String>,
    description: Option<String>,
    #[serde(rename = "requires-python")]
    requires_python: Option<String>,
}

/// Build system configuration from pyproject.toml
#[derive(Debug, Deserialize)]
struct BuildSystem {
    #[serde(rename = "build-backend")]
    build_backend: Option<String>,
}

/// UV workspace configuration
#[derive(Debug, Deserialize)]
struct UvWorkspace {
    members: Option<Vec<String>>,
    exclude: Option<Vec<String>>,
}

/// UV tool configuration
#[derive(Debug, Deserialize)]
struct UvTool {
    workspace: Option<UvWorkspace>,
}

/// Information about a parsed pyproject.toml file
#[derive(Debug, Clone)]
pub(crate) struct PyProjectInfo {
    pub(crate) tools: Vec<DetectedTool>,
    pub(crate) has_project_section: bool,
    pub(crate) workspace_info: Option<WorkspaceInfo>,
    pub(crate) requires_python: Option<String>,
    pub(crate) name: Option<String>,
    pub(crate) description: Option<String>,
}

/// Workspace information extracted from pyproject.toml
#[derive(Debug, Clone)]
pub(crate) struct WorkspaceInfo {
    pub(crate) members: Vec<String>,
    pub(crate) exclude: Vec<String>,
}

/// Analyze a pyproject.toml file and return comprehensive information.
pub(crate) fn analyze_pyproject_toml(path: &Path) -> Option<PyProjectInfo> {
    let pyproject_path = path.join("pyproject.toml");

    if !pyproject_path.exists() {
        return None;
    }

    let content = match fs::read_to_string(&pyproject_path) {
        Ok(content) => content,
        Err(e) => {
            warn!(
                "Error reading pyproject.toml at {}: {}",
                pyproject_path.display(),
                e
            );
            return None;
        }
    };

    let pyproject: PyProjectToml = match toml::from_str(&content) {
        Ok(pyproject) => pyproject,
        Err(e) => {
            warn!(
                "Error parsing pyproject.toml at {}: {}",
                pyproject_path.display(),
                e
            );
            return None;
        }
    };

    let mut detected = Vec::new();

    // Detect build backend
    if let Some(build_system) = &pyproject.build_system {
        if let Some(backend) = &build_system.build_backend {
            let tool = detect_build_backend(backend);
            detected.push(tool);
        }
    }

    // Detect tools from [tool.*] sections
    let mut workspace_info = None;
    if let Some(tool_sections) = &pyproject.tool {
        for (tool_name, value) in tool_sections {
            if let Some(tool) = detect_tool_section(tool_name) {
                detected.push(tool);
            }

            // Parse UV workspace information
            if tool_name == "uv" {
                if let Ok(uv_config) = value.clone().try_into::<UvTool>() {
                    if let Some(workspace) = uv_config.workspace {
                        workspace_info = Some(WorkspaceInfo {
                            members: workspace.members.unwrap_or_default(),
                            exclude: workspace.exclude.unwrap_or_default(),
                        });
                    }
                }
            }
        }

        // Detect diagnostic tools from [tool.*] sections
        let diagnostic_tools = devtools::detect_dev_tools_from_pyproject(tool_sections);
        detected.extend(diagnostic_tools);
    }

    let has_project_section = pyproject.project.is_some();
    let requires_python = pyproject
        .project
        .as_ref()
        .and_then(|project| project.requires_python.clone());
    let name = pyproject
        .project
        .as_ref()
        .and_then(|project| project.name.clone());
    let description = pyproject
        .project
        .as_ref()
        .and_then(|project| project.description.clone());

    Some(PyProjectInfo {
        tools: detected,
        has_project_section,
        workspace_info,
        requires_python,
        name,
        description,
    })
}

/// Map build-backend strings to detected tools.
fn detect_build_backend(backend: &str) -> DetectedTool {
    let (name, confidence) = match backend {
        "setuptools.build_meta" | "setuptools.build_meta:__legacy__" => ("setuptools", 0.95),
        "poetry.core.masonry.api" => ("poetry", 0.95),
        "hatchling.build" => ("hatch", 0.95),
        "flit_core.buildapi" => ("flit", 0.95),
        "pdm.backend" => ("pdm", 0.95),
        "scikit_build_core.build" => ("scikit-build-core", 0.90),
        "mesonpy" => ("meson-python", 0.90),
        "maturin" => ("maturin", 0.90),

        // Handle custom backends with lower confidence
        custom if custom.contains("maturin") => ("maturin", 0.85),
        custom if custom.contains("setuptools") => ("setuptools", 0.80),
        custom if custom.contains("poetry") => ("poetry", 0.80),
        custom if custom.contains("hatch") => ("hatch", 0.80),
        custom if custom.contains("flit") => ("flit", 0.80),
        custom if custom.contains("pdm") => ("pdm", 0.80),
        // Fallback for any other custom backend
        custom => {
            // Extract potential tool name from custom backend string
            let tool_name = if let Some(first_part) = custom.split('.').next() {
                first_part
            } else {
                custom
            };
            (tool_name, 0.70)
        }
    };

    DetectedTool {
        tool_type: ToolType::Backend,
        name: name.to_string(),
        confidence,
        evidence: vec![format!(
            "pyproject.toml:[build-system].build-backend={}",
            backend
        )],
    }
}

/// Maps [tool.*] section names to detected tools
fn detect_tool_section(section_name: &str) -> Option<DetectedTool> {
    let (name, tool_type, confidence) = match section_name {
        "poetry" => ("poetry", ToolType::Manager, 0.90),
        "hatch" => ("hatch", ToolType::Manager, 0.90),
        "pdm" => ("pdm", ToolType::Manager, 0.90),
        "uv" => ("uv", ToolType::Manager, 0.90),
        "rye" => ("rye", ToolType::Manager, 0.85), // Lower confidence as Rye often migrates to uv
        _ => return None,
    };

    Some(DetectedTool {
        tool_type,
        name: name.to_string(),
        confidence,
        evidence: vec![format!("pyproject.toml:[tool.{}]", section_name)],
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_detect_setuptools_backend() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 1);
        assert_eq!(info.tools[0].name, "setuptools");
        assert_eq!(info.tools[0].tool_type, ToolType::Backend);
        assert!(info.tools[0].confidence >= 0.9);
    }

    #[test]
    fn test_detect_poetry_backend_and_tool() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "my-package"
version = "0.1.0"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 2);

        let backend_tool = info
            .tools
            .iter()
            .find(|t| t.tool_type == ToolType::Backend)
            .unwrap();
        let manager_tool = info
            .tools
            .iter()
            .find(|t| t.tool_type == ToolType::Manager)
            .unwrap();

        assert_eq!(backend_tool.name, "poetry");
        assert_eq!(manager_tool.name, "poetry");
    }

    #[test]
    fn test_detect_hatch() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "src/__about__.py"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 2);

        let names: Vec<&str> = info.tools.iter().map(|t| t.name.as_str()).collect();
        assert!(names.contains(&"hatch"));
    }

    #[test]
    fn test_detect_uv_tool() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[project]
name = "my-package"
version = "0.1.0"

[tool.uv]
dev-dependencies = ["pytest"]
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 1);
        assert_eq!(info.tools[0].name, "uv");
        assert_eq!(info.tools[0].tool_type, ToolType::Manager);
    }

    #[test]
    fn test_detect_maturin_rust_backend() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "my-rust-python-package"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 1);
        assert_eq!(info.tools[0].name, "maturin");
        assert_eq!(info.tools[0].tool_type, ToolType::Backend);
        assert!(info.tools[0].confidence >= 0.9);
    }

    #[test]
    fn test_no_pyproject_toml() {
        let temp_dir = TempDir::new().unwrap();
        let info = analyze_pyproject_toml(temp_dir.path());
        assert!(info.is_none());
    }

    #[test]
    fn test_empty_pyproject_toml() {
        let temp_dir = TempDir::new().unwrap();
        fs::write(temp_dir.path().join("pyproject.toml"), "").unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 0);
    }

    #[test]
    fn test_rye_tool_section() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[tool.rye]
managed = true
dev-dependencies = ["pytest"]

[tool.rye.sources]
some-package = { git = "https://github.com/example/package.git" }
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 1);
        assert_eq!(info.tools[0].name, "rye");
        assert_eq!(info.tools[0].tool_type, ToolType::Manager);
        // Rye should have slightly lower confidence as it often migrates to uv
        assert!(info.tools[0].confidence < 0.9);
    }

    #[test]
    fn test_pdm_backend_and_tool() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"

[tool.pdm]
version = { source = "file", path = "src/__version__.py" }

[tool.pdm.dev-dependencies]
test = ["pytest"]
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 2);

        let backend_tool = info
            .tools
            .iter()
            .find(|t| t.tool_type == ToolType::Backend)
            .unwrap();
        let manager_tool = info
            .tools
            .iter()
            .find(|t| t.tool_type == ToolType::Manager)
            .unwrap();

        assert_eq!(backend_tool.name, "pdm");
        assert_eq!(manager_tool.name, "pdm");
    }

    #[test]
    fn test_scientific_backends() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["scikit-build-core>=0.3.3", "pybind11"]
build-backend = "scikit_build_core.build"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 1);
        assert_eq!(info.tools[0].name, "scikit-build-core");
        assert_eq!(info.tools[0].tool_type, ToolType::Backend);
    }

    #[test]
    fn test_multiple_tool_sections() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "src/__about__.py"

[tool.rye]
managed = true

# This should detect both hatch and rye as managers, plus hatch as backend
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 3);

        let tool_names: Vec<&str> = info.tools.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"hatch"));
        assert!(tool_names.contains(&"rye"));

        let backend_count = info
            .tools
            .iter()
            .filter(|t| t.tool_type == ToolType::Backend)
            .count();
        let manager_count = info
            .tools
            .iter()
            .filter(|t| t.tool_type == ToolType::Manager)
            .count();

        assert_eq!(backend_count, 1); // hatch backend
        assert_eq!(manager_count, 2); // hatch and rye managers
    }

    #[test]
    fn test_custom_backend_detection() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["maturin>=1.0,<2.0", "custom-wrapper"]
build-backend = "maturin_wrapper"

[tool.custom]
some-config = "value"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert!(!info.tools.is_empty());

        // Should detect maturin from custom backend name
        let backend_tool = info
            .tools
            .iter()
            .find(|t| t.tool_type == ToolType::Backend)
            .unwrap();
        assert_eq!(backend_tool.name, "maturin");
        assert!(backend_tool.confidence >= 0.8);
        assert!(
            backend_tool
                .evidence
                .iter()
                .any(|e| e.contains("maturin_wrapper"))
        );
    }

    #[test]
    fn test_unknown_custom_backend() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[build-system]
requires = ["some-custom-backend"]
build-backend = "custom_company.build_system.backend"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();
        assert_eq!(info.tools.len(), 1);

        let backend_tool = &info.tools[0];
        assert_eq!(backend_tool.name, "custom_company");
        assert_eq!(backend_tool.tool_type, ToolType::Backend);
        assert!(backend_tool.confidence >= 0.7);
        assert!(
            backend_tool
                .evidence
                .iter()
                .any(|e| e.contains("custom_company.build_system.backend"))
        );
    }

    #[test]
    fn test_analyze_pyproject_toml_with_workspace() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[project]
name = "workspace-root"
version = "0.1.0"

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/excluded"]

[tool.uv]
dev-dependencies = ["pytest"]
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();

        assert!(info.has_project_section);
        assert!(info.workspace_info.is_some());

        let workspace = info.workspace_info.unwrap();
        assert_eq!(workspace.members, vec!["packages/*"]);
        assert_eq!(workspace.exclude, vec!["packages/excluded"]);

        // Should detect uv as manager
        let uv_tool = info.tools.iter().find(|t| t.name == "uv").unwrap();
        assert_eq!(uv_tool.tool_type, ToolType::Manager);
    }

    #[test]
    fn test_analyze_pyproject_toml_no_project_section() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r"
[tool.ruff]
line-length = 88

[tool.mypy]
strict = true
";
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let info = analyze_pyproject_toml(temp_dir.path()).unwrap();

        assert!(!info.has_project_section);
        assert!(info.workspace_info.is_none());
        assert_eq!(info.tools.len(), 3); // Should detect ruff (diagnostic + formatter) and mypy (diagnostic)

        let tool_names: Vec<&str> = info.tools.iter().map(|t| t.name.as_str()).collect();
        assert!(tool_names.contains(&"ruff"));
        assert!(tool_names.contains(&"mypy"));

        // Should have diagnostic tools
        let diagnostic_tools: Vec<_> = info
            .tools
            .iter()
            .filter(|t| t.tool_type == ToolType::Diagnostic)
            .collect();
        assert_eq!(diagnostic_tools.len(), 2); // ruff and mypy as diagnostics

        // Should have formatter tools
        let formatter_tools: Vec<_> = info
            .tools
            .iter()
            .filter(|t| t.tool_type == ToolType::Formatter)
            .collect();
        assert_eq!(formatter_tools.len(), 1); // ruff as formatter
    }

    #[test]
    fn test_analyze_pyproject_toml_nonexistent() {
        let temp_dir = TempDir::new().unwrap();
        let info = analyze_pyproject_toml(temp_dir.path());
        assert!(info.is_none());
    }
}
