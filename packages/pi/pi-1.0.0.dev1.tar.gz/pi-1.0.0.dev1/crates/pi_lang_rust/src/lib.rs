//! Rust project detection library
//!
//! This crate provides functionality to detect Rust projects and workspaces
//! using `cargo_metadata` to analyze Cargo.toml files and project structure.

#![warn(clippy::pedantic)]

mod dependencies;
mod devtools;

use cargo_metadata::{CargoOpt, MetadataCommand};
use ignore::WalkBuilder;
use pi_lang::{
    DetectedTool, DetectionConfig, Package, Project, ToolType, ToolchainEnvironment, ToolchainType,
    Workspace,
};
use rust_toolchain_file::{ParseStrategy, Parser, ToolchainFile};
use std::path::Path;
use tracing::warn;

/// Detect Rust projects in the given directory.
///
/// # Errors
///
/// Return `anyhow::Error` if the directory doesn't exist or isn't accessible.
pub fn detect_rust_projects<P: AsRef<Path>>(
    path: P,
    config: Option<&DetectionConfig>,
) -> Result<Vec<Project>, anyhow::Error> {
    let path = path.as_ref();

    // Check if the top-level path exists and is a directory
    if !path.exists() {
        return Err(anyhow::anyhow!(
            "Directory does not exist: {}",
            path.display()
        ));
    }
    if !path.is_dir() {
        return Err(anyhow::anyhow!(
            "Path is not a directory: {}",
            path.display()
        ));
    }

    let default_config = DetectionConfig::default();
    let config = config.unwrap_or(&default_config);

    // Convert to absolute path to handle relative paths correctly

    let absolute_path = if path.is_absolute() {
        path.to_path_buf()
    } else {
        match std::env::current_dir() {
            Ok(current) => current.join(path),
            Err(e) => {
                warn!("Error getting current directory: {}", e);
                path.to_path_buf()
            }
        }
    };

    // Collect all potential Rust projects
    let mut all_projects = Vec::new();
    all_projects.extend(scan_for_rust_projects(&absolute_path, config));
    if let Some(parent_project) = scan_up_for_rust_project(&absolute_path) {
        // Check if this parent project is not already in our list
        if !all_projects
            .iter()
            .any(|p| p.workspace.root == parent_project.workspace.root)
        {
            all_projects.push(parent_project);
        }
    }

    // Filter out workspace members if their workspace root is also detected
    let workspace_roots: std::collections::HashSet<_> = all_projects
        .iter()
        .filter(|p| !p.workspace.members.is_empty())
        .map(|p| p.workspace.root.clone())
        .collect();

    let filtered_projects = all_projects
        .into_iter()
        .filter(|project| {
            // Keep workspace roots
            if !project.workspace.members.is_empty() {
                return true;
            }

            // Check if this project is a member of any workspace root
            let is_workspace_member = workspace_roots.iter().any(|root| {
                // Use canonical comparison to handle symlinks
                let project_canonical = project
                    .workspace
                    .root
                    .canonicalize()
                    .unwrap_or_else(|_| project.workspace.root.clone());
                let root_canonical = root.canonicalize().unwrap_or_else(|_| root.clone());

                project_canonical.starts_with(&root_canonical)
                    && project_canonical != root_canonical
            });
            !is_workspace_member
        })
        .collect();

    Ok(filtered_projects)
}

/// Scan for Rust projects in subdirectories.
fn scan_for_rust_projects(root: &Path, config: &DetectionConfig) -> Vec<Project> {
    let mut projects = Vec::new();

    // Build walker with ignore support
    let mut walker = WalkBuilder::new(root);
    walker
        .max_depth(Some(config.max_depth))
        .follow_links(config.follow_links)
        .hidden(false)
        .git_ignore(true)
        .git_exclude(true);

    // Add custom ignore patterns
    for skip_dir in &config.skip_dirs {
        walker.add_ignore(format!("{skip_dir}/**"));
    }

    for entry in walker.build() {
        match entry {
            Ok(entry) => {
                let path = entry.path();

                if should_skip_directory(path, config) {
                    continue;
                }

                // Look for Cargo.toml files (only in directories, not files)
                if path.is_dir() {
                    let cargo_toml = path.join("Cargo.toml");
                    if cargo_toml.exists() {
                        let project = create_project_from_cargo_toml(&cargo_toml);
                        projects.push(project);
                    }
                }
            }
            Err(e) => {
                warn!("Error walking directory tree: {}", e);
            }
        }
    }

    projects
}

/// Scan up the directory tree for parent Rust projects.
fn scan_up_for_rust_project(start_path: &Path) -> Option<Project> {
    let cargo_toml_path = find_cargo_toml(start_path);
    cargo_toml_path.map(|path| create_project_from_cargo_toml(&path))
}

/// Create a Project from a Cargo.toml file path.
fn create_project_from_cargo_toml(cargo_toml_path: &Path) -> Project {
    let project_root = cargo_toml_path.parent().unwrap();

    let tools = detect_and_deduplicate_tools(project_root);
    let toolchain_envs = detect_rust_toolchain_files(project_root);
    let toolchain_version_constraint =
        get_toolchain_version_constraint(cargo_toml_path, &toolchain_envs);
    let workspace = build_workspace_from_metadata(cargo_toml_path, project_root);
    let (project_name, project_description) = extract_project_info(cargo_toml_path);

    Project {
        name: project_name,
        description: project_description,
        toolchain_type: ToolchainType::Rust,
        tools,
        toolchain_envs,
        workspace,
        toolchain_version_constraint,
    }
}

/// Detect all tools for a project and deduplicate them.
fn detect_and_deduplicate_tools(project_root: &Path) -> Vec<DetectedTool> {
    let mut tools = detect_cargo_tools(project_root);

    // Detect standard Rust dev tools (implied by Cargo.toml existence)
    let mut dev_tools = devtools::detect_implied_rust_tools();

    // Detect dev tools from configuration files and bump confidence if config files are found
    let config_tools = devtools::detect_dev_tools(project_root);
    dev_tools = devtools::bump_tool_confidence(dev_tools, &config_tools);

    tools.extend(dev_tools);

    // Deduplicate tools by name and type, keeping highest confidence
    tools.sort_by(|a, b| b.confidence.partial_cmp(&a.confidence).unwrap());
    tools.dedup_by(|a, b| a.name == b.name && a.tool_type == b.tool_type);

    tools
}

/// Detect Cargo-specific tools based on manifest and lock files.
fn detect_cargo_tools(project_root: &Path) -> Vec<DetectedTool> {
    let mut tools = Vec::new();

    // Always detect cargo as the primary manager when Cargo.toml exists
    tools.push(DetectedTool {
        tool_type: ToolType::Manager,
        name: "cargo".to_string(),
        confidence: 0.95,
        evidence: vec!["Cargo.toml".to_string()],
    });

    // Check if Cargo.lock exists for higher confidence
    if project_root.join("Cargo.lock").exists() {
        tools.push(DetectedTool {
            tool_type: ToolType::Manager,
            name: "cargo".to_string(),
            confidence: 0.98,
            evidence: vec!["Cargo.lock".to_string()],
        });
    }

    tools
}

/// Get toolchain version constraint from Cargo.toml or rust-toolchain files.
fn get_toolchain_version_constraint(
    cargo_toml_path: &Path,
    toolchain_envs: &[ToolchainEnvironment],
) -> Option<String> {
    extract_rust_version(cargo_toml_path)
        .or_else(|| toolchain_envs.iter().find_map(|env| env.version.clone()))
}

/// Build workspace structure from cargo metadata.
fn build_workspace_from_metadata(cargo_toml_path: &Path, project_root: &Path) -> Workspace {
    match MetadataCommand::new()
        .manifest_path(cargo_toml_path)
        .features(CargoOpt::AllFeatures)
        .no_deps() // Don't resolve dependencies to avoid errors
        .exec()
    {
        Ok(metadata) => {
            if metadata.workspace_members.len() > 1 {
                let is_workspace_root = metadata.workspace_root.as_std_path() == project_root;

                if is_workspace_root {
                    build_workspace_root(metadata)
                } else {
                    build_workspace_member(project_root)
                }
            } else {
                build_single_package_workspace(project_root)
            }
        }
        Err(_) => build_fallback_workspace(project_root),
    }
}

/// Build workspace structure for a workspace root.
fn build_workspace_root(metadata: cargo_metadata::Metadata) -> Workspace {
    let mut packages = Vec::new();

    for id in &metadata.workspace_members {
        if let Some(pkg) = metadata.packages.iter().find(|p| p.id == *id) {
            let package_path = pkg.manifest_path.parent().unwrap();
            let package_tools = detect_and_deduplicate_tools(package_path.as_std_path());
            let package_dependencies =
                dependencies::detect_dependencies(package_path.as_std_path());

            packages.push(Package {
                name: pkg.name.clone(),
                path: package_path.into(),
                tools: package_tools,
                dependencies: package_dependencies,
            });
        }
    }

    Workspace {
        root: metadata.workspace_root.into(),
        members: packages,
    }
}

/// Build workspace structure for a workspace member.
fn build_workspace_member(project_root: &Path) -> Workspace {
    Workspace {
        root: project_root.to_path_buf(),
        members: vec![],
    }
}

/// Build workspace structure for a single package.
fn build_single_package_workspace(project_root: &Path) -> Workspace {
    Workspace {
        root: project_root.to_path_buf(),
        members: vec![],
    }
}

/// Build fallback workspace when metadata fails.
fn build_fallback_workspace(project_root: &Path) -> Workspace {
    Workspace {
        root: project_root.to_path_buf(),
        members: vec![], // We'll detect members separately during scanning
    }
}

/// Find Cargo.toml by searching up the directory tree, preferring workspace roots.
fn find_cargo_toml(start_path: &Path) -> Option<std::path::PathBuf> {
    let mut current_dir = Some(start_path);
    let mut found_cargo_toml: Option<std::path::PathBuf> = None;

    while let Some(dir) = current_dir {
        let cargo_toml = dir.join("Cargo.toml");

        if cargo_toml.exists() {
            // Check if this is a workspace root or just a workspace member
            match std::fs::read_to_string(&cargo_toml) {
                Ok(content) => {
                    if content.contains("[workspace]") {
                        // This is a workspace root, prefer it over any member we found
                        return Some(cargo_toml);
                    } else if found_cargo_toml.is_none() {
                        // This is likely a workspace member, remember it but keep searching
                        found_cargo_toml = Some(cargo_toml);
                    }
                }
                Err(e) => {
                    warn!(
                        "Error reading Cargo.toml at {}: {}",
                        cargo_toml.display(),
                        e
                    );
                    if found_cargo_toml.is_none() {
                        // Can't read the file, but it exists - remember it
                        found_cargo_toml = Some(cargo_toml);
                    }
                }
            }
        }

        // Stop at filesystem root or git repository root
        if dir == Path::new("/") || dir.parent().is_none() {
            break;
        }
        if dir.join(".git").exists() {
            break;
        }

        current_dir = dir.parent();
    }

    found_cargo_toml
}

/// Determine if a directory should be skipped during scanning.
fn should_skip_directory(path: &Path, config: &DetectionConfig) -> bool {
    if let Some(dir_name) = path.file_name().and_then(|n| n.to_str()) {
        // Check if it's in our skip list
        if config.skip_dirs.iter().any(|skip| skip == dir_name) {
            return true;
        }

        // Skip common Rust build/cache directories
        if matches!(
            dir_name,
            "target" | "build" | ".git" | ".cargo" | "node_modules" | "__pycache__"
        ) {
            return true;
        }
    }

    false
}

/// Detect and parse rust-toolchain.toml and rust-toolchain files in the project.
fn detect_rust_toolchain_files(project_root: &Path) -> Vec<ToolchainEnvironment> {
    let mut toolchain_envs = Vec::new();

    // Check for rust-toolchain.toml
    let toolchain_toml_path = project_root.join("rust-toolchain.toml");
    if toolchain_toml_path.exists() {
        if let Some(env) = parse_rust_toolchain_file(&toolchain_toml_path, project_root) {
            toolchain_envs.push(env);
        }
    }

    // Check for rust-toolchain (legacy format)
    let toolchain_legacy_path = project_root.join("rust-toolchain");
    if toolchain_legacy_path.exists() && !toolchain_toml_path.exists() {
        if let Some(env) = parse_rust_toolchain_file(&toolchain_legacy_path, project_root) {
            toolchain_envs.push(env);
        }
    }

    toolchain_envs
}

/// Parse a rust-toolchain file (either TOML or legacy format).
fn parse_rust_toolchain_file(
    toolchain_path: &Path,
    project_root: &Path,
) -> Option<ToolchainEnvironment> {
    let content = match std::fs::read_to_string(toolchain_path) {
        Ok(content) => content,
        Err(e) => {
            warn!(
                "Error reading toolchain file at {}: {}",
                toolchain_path.display(),
                e
            );
            return None;
        }
    };

    let parser = Parser::new(
        &content,
        ParseStrategy::Fallback {
            first: rust_toolchain_file::Variant::Toml,
            fallback_to: rust_toolchain_file::Variant::Legacy,
        },
    );

    match parser.parse() {
        Ok(toolchain_file) => {
            let (_channel, version, name) = match toolchain_file {
                ToolchainFile::Legacy(legacy) => {
                    let channel = legacy.spec().map_or_else(
                        || {
                            legacy.path().map_or_else(
                                || "unknown".to_string(),
                                |path| path.to_string_lossy().to_string(),
                            )
                        },
                        std::string::ToString::to_string,
                    );
                    (Some(channel.clone()), Some(channel.clone()), Some(channel))
                }
                ToolchainFile::Toml(toml) => {
                    toml.toolchain().spec().map_or_else(
                        || {
                            toml.toolchain().path().map_or_else(
                                || {
                                    // This shouldn't happen with valid TOML
                                    (None, None, None)
                                },
                                |path| {
                                    let path_str = path.path().to_string();
                                    (
                                        Some(path_str.clone()),
                                        Some(path_str.clone()),
                                        Some(path_str),
                                    )
                                },
                            )
                        },
                        |spec| {
                            spec.channel().map_or_else(
                                || {
                                    // TOML spec without channel
                                    (None, None, Some("custom".to_string()))
                                },
                                |channel| {
                                    let channel_name = channel.name().to_string();
                                    (
                                        Some(channel_name.clone()),
                                        Some(channel_name.clone()),
                                        Some(channel_name),
                                    )
                                },
                            )
                        },
                    )
                }
            };

            let toolchain_env = ToolchainEnvironment {
                executable: None, // We don't detect the actual rustc path here
                prefix: None,     // We don't detect the toolchain installation path
                name,
                version,
                project: Some(project_root.to_path_buf()),
                is_path_linked: true,
                is_env_specified: false,
            };

            Some(toolchain_env)
        }
        Err(e) => {
            tracing::warn!(
                "Failed to parse rust-toolchain file at {}: {}",
                toolchain_path.display(),
                e
            );
            // Return None instead of failing completely - we can still detect the project
            None
        }
    }
}

/// Extract project name and description from Cargo.toml.
fn extract_project_info(cargo_toml_path: &Path) -> (Option<String>, Option<String>) {
    match cargo_toml::Manifest::from_path(cargo_toml_path) {
        Ok(manifest) => {
            let mut name = None;
            let mut description = None;

            if let Some(ref package) = manifest.package {
                name = Some(package.name.clone());
                description = match &package.description {
                    Some(cargo_toml::Inheritable::Set(desc)) => Some(desc.clone()),
                    Some(cargo_toml::Inheritable::Inherited { .. }) | None => None,
                };
            }

            // If this is a workspace and we don't have info, try workspace metadata
            if let Some(ref workspace) = manifest.workspace {
                if let Some(ref workspace_package) = workspace.package {
                    // Workspace package doesn't have a name field, so we use directory name
                    // If we still don't have a name, use the directory name
                    if name.is_none() {
                        if let Some(dir_name) = cargo_toml_path
                            .parent()
                            .and_then(|p| p.file_name())
                            .and_then(|n| n.to_str())
                        {
                            name = Some(dir_name.to_string());
                        }
                    }
                    if description.is_none() {
                        description.clone_from(&workspace_package.description);
                    }
                }
            }

            if name.is_none() {
                if let Some(dir_name) = cargo_toml_path
                    .parent()
                    .and_then(|p| p.file_name())
                    .and_then(|n| n.to_str())
                {
                    name = Some(dir_name.to_string());
                }
            }

            (name, description)
        }
        Err(e) => {
            warn!(
                "Error parsing Cargo.toml at {}: {}",
                cargo_toml_path.display(),
                e
            );
            (None, None)
        }
    }
}

/// Extract rust-version from Cargo.toml using `cargo_toml` crate.
fn extract_rust_version(cargo_toml_path: &Path) -> Option<String> {
    match cargo_toml::Manifest::from_path(cargo_toml_path) {
        Ok(manifest) => {
            // Check package.rust_version first
            if let Some(ref package) = manifest.package {
                if let Some(ref rust_version) = package.rust_version {
                    match rust_version {
                        cargo_toml::Inheritable::Set(version) => return Some(version.clone()),
                        cargo_toml::Inheritable::Inherited { .. } => {
                            // If inherited, we'll check workspace.package below
                        }
                    }
                }
            }

            // Check workspace.package.rust_version
            if let Some(ref workspace) = manifest.workspace {
                if let Some(ref workspace_package) = workspace.package {
                    if let Some(ref rust_version) = workspace_package.rust_version {
                        return Some(rust_version.clone());
                    }
                }
            }

            None
        }
        Err(e) => {
            warn!(
                "Error parsing Cargo.toml at {}: {}",
                cargo_toml_path.display(),
                e
            );
            None
        }
    }
}
