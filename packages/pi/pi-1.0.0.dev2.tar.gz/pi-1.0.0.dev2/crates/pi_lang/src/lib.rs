//! Toolchain detection library
//!
//! This crate provides functionality to detect project toolchains
//! in arbitrary directories by analyzing lockfiles, configuration files,
//! and other packaging artifacts.

#![warn(clippy::pedantic)]

use std::path::PathBuf;

use serde::{Deserialize, Serialize};

/// Types of tools
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ToolType {
    /// Package manager (handles dependencies)
    Manager,
    /// Build backend (handles building/packaging)
    Backend,
    /// Environment manager (handles virtual environments)
    Environment,
    /// Diagnostic tool (type checkers, linters, security scanners)
    Diagnostic,
    /// Code formatter (formats and styles code)
    Formatter,
    /// Testing tool (test frameworks, coverage tools)
    Testing,
    /// Documentation tool (doc generators)
    Documentation,
}

/// Detected Python packaging tool
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DetectedTool {
    /// Type of tool
    pub tool_type: ToolType,
    /// Name of the tool
    pub name: String,
    /// Confidence score (0.0 to 1.0)
    pub confidence: f64,
    /// Evidence that led to this detection
    pub evidence: Vec<String>,
}

/// A dependency of a package
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Dependency {
    /// Name of the dependency
    pub name: String,
    /// Version constraint (e.g., ">=1.0.0", "^2.1.0", "~=3.9.0")
    pub version_constraint: Option<String>,
    /// URL for URL-based dependencies (e.g., Git repos, direct URLs)
    ///
    /// For Python: Git URLs, HTTP URLs, or file:// URLs as per PEP 508
    /// For Rust: Git URLs, path dependencies, or registry URLs
    /// When present, `version_constraint` should be None
    pub url: Option<String>,
    /// Features/extras that enable this dependency
    ///
    /// For Python: extra names from optional-dependencies (e.g., `["dev", "test"]`)
    /// For Rust: feature names that enable this optional dependency (e.g., `["serde"]`)
    /// Empty vector means this is a required dependency
    pub optional: Vec<String>,
    /// Dependency group/category (e.g., "dev", "test", "optional", "build")
    pub group: Option<String>,
    /// Environment markers for conditional dependencies
    ///
    /// For Python: PEP 508 markers like '`python_version` >= "3.9"'
    /// For Rust: cfg conditions like '`target_os` = "windows"'
    pub environment_markers: Option<String>,
    /// Source where this dependency was found (e.g., "pyproject.toml", "Cargo.toml")
    pub source: String,
    /// Features/extras enabled for this dependency
    ///
    /// For Python: extra names requested for this dependency (e.g., `["standard"]` for fastapi[standard])
    /// For Rust: feature names enabled for this dependency (e.g., `["serde"]`)
    /// Empty vector means no specific features/extras are requested
    pub features: Vec<String>,
}

/// Information about a package within a workspace
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Package {
    /// Name of the package
    pub name: String,
    /// Path to the package root directory
    pub path: PathBuf,
    /// Tools detected specifically for this package
    pub tools: Vec<DetectedTool>,
    /// Dependencies declared by this package
    pub dependencies: Vec<Dependency>,
}

/// Information about a detected workspace
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Workspace {
    /// Root directory of the workspace
    pub root: PathBuf,
    /// Workspace member packages
    pub members: Vec<Package>,
}

/// Toolchain types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ToolchainType {
    Python,
    Rust,
}

/// Detected toolchain environment (e.g Python venv)
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ToolchainEnvironment {
    /// Path to the main toolchain executable
    pub executable: Option<PathBuf>,
    /// Toolchain root directory
    pub prefix: Option<PathBuf>,
    /// Toolchain name (if available)
    pub name: Option<String>,
    /// Toolchain version (if detected)
    pub version: Option<String>,
    /// Project directory associated with this toolchain
    pub project: Option<PathBuf>,
    /// Whether the environment is local to a path
    pub is_path_linked: bool,
    /// Whether the environment is specified in the OS environment variable
    pub is_env_specified: bool,
}

/// A detected project
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Project {
    /// Project name
    ///
    /// For Python projects: extracted from `name` in pyproject.toml [project] section
    /// For Rust projects: extracted from `name` in Cargo.toml [package] section,
    /// or workspace name if this is a workspace root
    pub name: Option<String>,
    /// Project description
    ///
    /// For Python projects: extracted from `description` in pyproject.toml [project] section
    /// For Rust projects: extracted from `description` in Cargo.toml [package] section,
    /// or workspace description if this is a workspace root
    pub description: Option<String>,
    /// Toolchain type, most often the primary language
    pub toolchain_type: ToolchainType,
    /// All detected tools, sorted by confidence (highest first)
    pub tools: Vec<DetectedTool>,
    /// Detected toolchains (e.g Python venvs)
    pub toolchain_envs: Vec<ToolchainEnvironment>,
    /// Workspace information (always present, contains project root)
    pub workspace: Workspace,
    /// Toolchain version constraint from project configuration
    ///
    /// For Python projects: extracted from `requires-python` in pyproject.toml
    /// For Rust projects: extracted from `rust-version` in Cargo.toml,
    /// or falls back to version from `rust-toolchain.toml`/`rust-toolchain` if not present
    ///
    /// Examples:
    /// - Python: ">=3.9", "^3.10"
    /// - Rust: "1.70", "1.75.0", "stable"
    pub toolchain_version_constraint: Option<String>,
}

impl Project {
    /// Get all tools of a given type from the project (already sorted by confidence, highest first)
    #[must_use]
    pub fn tools_of_type(&self, tool_type: ToolType) -> Vec<&DetectedTool> {
        self.tools
            .iter()
            .filter(|tool| tool.tool_type == tool_type)
            .collect()
    }

    /// Get the top tool of a given type from the project (highest confidence)
    #[must_use]
    pub fn top_tool_of_type(&self, tool_type: ToolType) -> Option<&DetectedTool> {
        self.tools.iter().find(|tool| tool.tool_type == tool_type)
    }

    /// Get all tools of a given type from all packages in the workspace
    #[must_use]
    pub fn all_tools_of_type(&self, tool_type: ToolType) -> Vec<&DetectedTool> {
        let mut all_tools = self.tools_of_type(tool_type);

        for package in &self.workspace.members {
            all_tools.extend(
                package
                    .tools
                    .iter()
                    .filter(|tool| tool.tool_type == tool_type),
            );
        }

        // Sort by confidence (highest first)
        all_tools.sort_by(|a, b| {
            b.confidence
                .partial_cmp(&a.confidence)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        all_tools
    }

    /// Get all tools from all packages in the workspace, grouped by type
    #[must_use]
    pub fn all_tools(&self) -> Vec<&DetectedTool> {
        let mut all_tools: Vec<&DetectedTool> = self.tools.iter().collect();

        for package in &self.workspace.members {
            all_tools.extend(package.tools.iter());
        }

        // Sort by confidence (highest first)
        all_tools.sort_by(|a, b| {
            b.confidence
                .partial_cmp(&a.confidence)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        all_tools
    }

    /// Get all dependencies from all packages in the workspace
    #[must_use]
    pub fn all_dependencies(&self) -> Vec<&Dependency> {
        let mut all_deps = Vec::new();
        for package in &self.workspace.members {
            all_deps.extend(package.dependencies.iter());
        }
        all_deps
    }

    /// Get dependencies by group from all packages in the workspace
    #[must_use]
    pub fn dependencies_by_group(&self, group: Option<&str>) -> Vec<&Dependency> {
        self.all_dependencies()
            .into_iter()
            .filter(|dep| dep.group.as_deref() == group)
            .collect()
    }

    /// Get all required dependencies (not behind any optional features)
    #[must_use]
    pub fn required_dependencies(&self) -> Vec<&Dependency> {
        self.all_dependencies()
            .into_iter()
            .filter(|dep| dep.optional.is_empty())
            .collect()
    }

    /// Get all optional dependencies (behind features/extras)
    #[must_use]
    pub fn optional_dependencies(&self) -> Vec<&Dependency> {
        self.all_dependencies()
            .into_iter()
            .filter(|dep| !dep.optional.is_empty())
            .collect()
    }

    /// Get dependencies enabled by a specific feature/extra
    #[must_use]
    pub fn dependencies_for_feature(&self, feature: &str) -> Vec<&Dependency> {
        self.all_dependencies()
            .into_iter()
            .filter(|dep| dep.optional.contains(&feature.to_string()))
            .collect()
    }
}

/// Configuration for the detection process
#[derive(Debug, Clone)]
pub struct DetectionConfig {
    /// Maximum depth to search for packaging files
    pub max_depth: usize,
    /// Whether to follow symbolic links
    pub follow_links: bool,
    /// Additional directories to skip beyond the defaults
    pub skip_dirs: Vec<String>,
}

impl Default for DetectionConfig {
    fn default() -> Self {
        Self {
            max_depth: 3,
            follow_links: false,
            skip_dirs: vec![
                "venv".to_string(),
                ".venv".to_string(),
                ".tox".to_string(),
                "__pycache__".to_string(),
                "dist".to_string(),
                "build".to_string(),
                ".git".to_string(),
                "node_modules".to_string(),
            ],
        }
    }
}
