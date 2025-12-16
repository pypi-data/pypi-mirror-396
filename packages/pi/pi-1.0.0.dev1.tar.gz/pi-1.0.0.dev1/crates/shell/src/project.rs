//! Project detection and conversion utilities
//!
//! This module provides functionality to detect projects using pi_lang crates
//! and convert between pi_lang types and RPC types.

use pi_lang::{
    Dependency as LangDependency, DetectedTool as LangDetectedTool, DetectionConfig,
    Package as LangPackage, Project as LangProject, ToolType as LangToolType,
    ToolchainEnvironment as LangToolchainEnvironment, ToolchainType as LangToolchainType,
    Workspace as LangWorkspace,
};
use pi_lang_python::detect_python_projects;
use pi_lang_rust::detect_rust_projects;
use pishell_rpc_types::{ProjectInfo, RpcError};
use std::path::Path;
use tracing::debug;

/// Convert pi_lang ToolType to RPC ToolType
fn convert_tool_type(tool_type: LangToolType) -> ProjectInfo::ToolType {
    match tool_type {
        LangToolType::Manager => ProjectInfo::ToolType::Manager,
        LangToolType::Backend => ProjectInfo::ToolType::Backend,
        LangToolType::Environment => ProjectInfo::ToolType::Environment,
        LangToolType::Diagnostic => ProjectInfo::ToolType::Diagnostic,
        LangToolType::Formatter => ProjectInfo::ToolType::Formatter,
        LangToolType::Testing => ProjectInfo::ToolType::Testing,
        LangToolType::Documentation => ProjectInfo::ToolType::Documentation,
    }
}

/// Convert pi_lang ToolchainType to RPC ToolchainType
fn convert_toolchain_type(toolchain_type: LangToolchainType) -> ProjectInfo::ToolchainType {
    match toolchain_type {
        LangToolchainType::Python => ProjectInfo::ToolchainType::Python,
        LangToolchainType::Rust => ProjectInfo::ToolchainType::Rust,
    }
}

/// Convert pi_lang DetectedTool to RPC DetectedTool
fn convert_detected_tool(tool: &LangDetectedTool) -> Result<ProjectInfo::DetectedTool, RpcError> {
    ProjectInfo::DetectedTool::builder()
        .tool_type(convert_tool_type(tool.tool_type))
        .name(tool.name.clone())
        .confidence(tool.confidence)
        .evidence(tool.evidence.clone())
        .try_into()
        .map_err(|e| RpcError::Rpc(format!("Failed to build DetectedTool: {e}")))
}

/// Convert pi_lang Dependency to RPC Dependency
fn convert_dependency(dependency: &LangDependency) -> Result<ProjectInfo::Dependency, RpcError> {
    ProjectInfo::Dependency::builder()
        .name(dependency.name.clone())
        .version_constraint(dependency.version_constraint.clone())
        .url(dependency.url.clone())
        .optional(dependency.optional.clone())
        .group(dependency.group.clone())
        .environment_markers(dependency.environment_markers.clone())
        .source(dependency.source.clone())
        .features(dependency.features.clone())
        .try_into()
        .map_err(|e| RpcError::Rpc(format!("Failed to build Dependency: {e}")))
}

/// Convert pi_lang ToolchainEnvironment to RPC ToolchainEnvironment
fn convert_toolchain_environment(
    env: &LangToolchainEnvironment,
) -> Result<ProjectInfo::ToolchainEnvironment, RpcError> {
    ProjectInfo::ToolchainEnvironment::builder()
        .executable(
            env.executable
                .as_ref()
                .map(|p| p.to_string_lossy().to_string()),
        )
        .prefix(env.prefix.as_ref().map(|p| p.to_string_lossy().to_string()))
        .name(env.name.clone())
        .version(env.version.clone())
        .project(
            env.project
                .as_ref()
                .map(|p| p.to_string_lossy().to_string()),
        )
        .is_path_linked(env.is_path_linked)
        .is_env_specified(env.is_env_specified)
        .try_into()
        .map_err(|e| RpcError::Rpc(format!("Failed to build ToolchainEnvironment: {e}")))
}

/// Convert pi_lang Package to RPC Package
fn convert_package(package: &LangPackage) -> Result<ProjectInfo::Package, RpcError> {
    let tools = package
        .tools
        .iter()
        .map(convert_detected_tool)
        .collect::<Result<Vec<_>, _>>()?;

    let dependencies = package
        .dependencies
        .iter()
        .map(convert_dependency)
        .collect::<Result<Vec<_>, _>>()?;

    ProjectInfo::Package::builder()
        .name(package.name.clone())
        .path(package.path.to_string_lossy().to_string())
        .tools(tools)
        .dependencies(dependencies)
        .try_into()
        .map_err(|e| RpcError::Rpc(format!("Failed to build Package: {e}")))
}

/// Convert pi_lang Workspace to RPC Workspace
fn convert_workspace(workspace: &LangWorkspace) -> Result<ProjectInfo::Workspace, RpcError> {
    let members = workspace
        .members
        .iter()
        .map(convert_package)
        .collect::<Result<Vec<_>, _>>()?;

    ProjectInfo::Workspace::builder()
        .root(workspace.root.to_string_lossy().to_string())
        .members(members)
        .try_into()
        .map_err(|e| RpcError::Rpc(format!("Failed to build Workspace: {e}")))
}

/// Convert pi_lang Project to RPC Project
fn convert_project(project: &LangProject) -> Result<ProjectInfo::Project, RpcError> {
    let tools = project
        .tools
        .iter()
        .map(convert_detected_tool)
        .collect::<Result<Vec<_>, _>>()?;

    let toolchain_envs = project
        .toolchain_envs
        .iter()
        .map(convert_toolchain_environment)
        .collect::<Result<Vec<_>, _>>()?;

    let workspace = convert_workspace(&project.workspace)?;

    ProjectInfo::Project::builder()
        .name(project.name.clone())
        .description(project.description.clone())
        .toolchain_type(convert_toolchain_type(project.toolchain_type))
        .tools(tools)
        .toolchain_envs(toolchain_envs)
        .workspace(workspace)
        .toolchain_version_constraint(project.toolchain_version_constraint.clone())
        .try_into()
        .map_err(|e| RpcError::Rpc(format!("Failed to build Project: {e}")))
}

/// Detect projects in the given directory and convert to RPC types
pub fn detect_projects<P: AsRef<Path>>(path: P) -> Result<Vec<ProjectInfo::Project>, RpcError> {
    let path = path.as_ref();

    debug!("Detecting projects in: {}", path.display());

    // Use default detection config for now
    let config = DetectionConfig::default();

    // Detect Python projects
    let python_projects = detect_python_projects(path, Some(&config))
        .map_err(|e| RpcError::Rpc(format!("Failed to detect Python projects: {e}")))?;

    // Detect Rust projects
    let rust_projects = detect_rust_projects(path, Some(&config))
        .map_err(|e| RpcError::Rpc(format!("Failed to detect Rust projects: {e}")))?;

    // Combine all projects
    let mut all_projects = python_projects;
    all_projects.extend(rust_projects);

    debug!("Found {} projects total", all_projects.len());

    // Convert to RPC types
    let rpc_projects = all_projects
        .iter()
        .map(convert_project)
        .collect::<Result<Vec<_>, _>>()?;

    Ok(rpc_projects)
}

#[cfg(test)]
mod tests {
    use super::*;

    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_tool_type_conversion() {
        assert_eq!(
            convert_tool_type(LangToolType::Manager),
            ProjectInfo::ToolType::Manager
        );
        assert_eq!(
            convert_tool_type(LangToolType::Backend),
            ProjectInfo::ToolType::Backend
        );
        assert_eq!(
            convert_tool_type(LangToolType::Diagnostic),
            ProjectInfo::ToolType::Diagnostic
        );
    }

    #[test]
    fn test_toolchain_type_conversion() {
        assert_eq!(
            convert_toolchain_type(LangToolchainType::Python),
            ProjectInfo::ToolchainType::Python
        );
        assert_eq!(
            convert_toolchain_type(LangToolchainType::Rust),
            ProjectInfo::ToolchainType::Rust
        );
    }

    #[test]
    fn test_detected_tool_conversion() {
        let lang_tool = LangDetectedTool {
            tool_type: LangToolType::Manager,
            name: "uv".to_string(),
            confidence: 0.95,
            evidence: vec!["uv.lock".to_string()],
        };

        let rpc_tool = convert_detected_tool(&lang_tool).unwrap();
        assert_eq!(rpc_tool.name, "uv");
        assert!((rpc_tool.confidence - 0.95).abs() < f64::EPSILON);
        assert_eq!(rpc_tool.evidence, vec!["uv.lock"]);
    }

    #[test]
    fn test_detect_projects_empty_directory() {
        let temp_dir = TempDir::new().unwrap();
        let projects = detect_projects(temp_dir.path()).unwrap();
        assert!(projects.is_empty());
    }

    #[test]
    fn test_detect_projects_with_python_project() {
        let temp_dir = TempDir::new().unwrap();

        // Create a simple Python project
        fs::write(
            temp_dir.path().join("pyproject.toml"),
            r#"
[project]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"#,
        )
        .unwrap();

        let projects = detect_projects(temp_dir.path()).unwrap();
        assert_eq!(projects.len(), 1);

        let project = &projects[0];
        assert_eq!(project.name, Some("test-project".to_string()));
        assert_eq!(project.toolchain_type, ProjectInfo::ToolchainType::Python);
        assert!(!project.tools.is_empty());
    }

    #[test]
    fn test_detect_projects_with_rust_project() {
        let temp_dir = TempDir::new().unwrap();

        // Create a simple Rust project
        fs::write(
            temp_dir.path().join("Cargo.toml"),
            r#"
[package]
name = "test-project"
version = "0.1.0"
edition = "2021"
"#,
        )
        .unwrap();

        let projects = detect_projects(temp_dir.path()).unwrap();
        assert_eq!(projects.len(), 1);

        let project = &projects[0];
        assert_eq!(project.name, Some("test-project".to_string()));
        assert_eq!(project.toolchain_type, ProjectInfo::ToolchainType::Rust);
        assert!(!project.tools.is_empty());
    }
}
