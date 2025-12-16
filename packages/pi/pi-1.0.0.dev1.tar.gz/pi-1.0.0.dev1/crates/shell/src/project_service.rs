//! Project detection RPC service implementation

use crate::project::detect_projects;
use pishell_rpc_types::{ProjectInfo, ProjectInfo::Service, RpcError, rpc_interface};
use std::sync::Arc;
use tracing::info;

#[derive(Clone)]
pub struct ProjectService {}

impl ProjectService {
    pub fn new() -> Self {
        Self {}
    }
}

impl Default for ProjectService {
    fn default() -> Self {
        Self::new()
    }
}

/// RPC interface implementation for project detection service
#[rpc_interface(interface = "ProjectInfo")]
impl ProjectInfo::Service for ProjectService {
    fn project_info(
        &self,
        request: ProjectInfo::ProjectInfoRequest,
    ) -> Result<ProjectInfo::ProjectInfoResponse, RpcError> {
        info!("Received project info request: {:?}", request);

        // Use directory from request or current directory as default
        let directory = if let Some(dir_str) = request.dir {
            std::path::PathBuf::from(dir_str)
        } else {
            std::env::current_dir()
                .map_err(|e| RpcError::Rpc(format!("Failed to get current directory: {e}")))?
        };

        let projects = detect_projects(&directory)?;

        info!("Detected {} projects", projects.len());
        Ok(ProjectInfo::ProjectInfoResponse { result: projects })
    }
}

pub fn setup(
    server: &pishell_socket::MessageServer,
) -> Result<Arc<ProjectService>, Box<dyn std::error::Error>> {
    // Create service instance
    let service = Arc::new(ProjectService::new());

    // Register RPC handlers using the procedural macro
    ProjectService::register_rpc_handlers(service.clone(), server);
    info!("Project detection service registered successfully");
    Ok(service)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_project_service_empty_directory() {
        let service = ProjectService::new();
        let temp_dir = TempDir::new().unwrap();

        let request = ProjectInfo::ProjectInfoRequest::builder()
            .dir(Some(temp_dir.path().to_string_lossy().to_string()))
            .try_into()
            .unwrap();

        let response = service.project_info(request).unwrap();
        assert!(response.result.is_empty());
    }

    #[test]
    fn test_project_service_with_python_project() {
        let service = ProjectService::new();
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

        let request = ProjectInfo::ProjectInfoRequest::builder()
            .dir(Some(temp_dir.path().to_string_lossy().to_string()))
            .try_into()
            .unwrap();

        let response = service.project_info(request).unwrap();
        assert_eq!(response.result.len(), 1);

        let project = &response.result[0];
        assert_eq!(project.name, Some("test-project".to_string()));
        assert_eq!(project.toolchain_type, ProjectInfo::ToolchainType::Python);
        assert!(!project.tools.is_empty());
    }

    #[test]
    fn test_project_service_with_rust_project() {
        let service = ProjectService::new();
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

        let request = ProjectInfo::ProjectInfoRequest::builder()
            .dir(Some(temp_dir.path().to_string_lossy().to_string()))
            .try_into()
            .unwrap();

        let response = service.project_info(request).unwrap();
        assert_eq!(response.result.len(), 1);

        let project = &response.result[0];
        assert_eq!(project.name, Some("test-project".to_string()));
        assert_eq!(project.toolchain_type, ProjectInfo::ToolchainType::Rust);
        assert!(!project.tools.is_empty());
    }

    #[test]
    fn test_project_service_current_directory_fallback() {
        let service = ProjectService::new();

        let request = ProjectInfo::ProjectInfoRequest::builder()
            .dir(None)
            .try_into()
            .unwrap();

        // This should not panic and should return some result
        // (might be empty if current directory has no projects)
        let response = service.project_info(request);
        assert!(response.is_ok());
    }
}
