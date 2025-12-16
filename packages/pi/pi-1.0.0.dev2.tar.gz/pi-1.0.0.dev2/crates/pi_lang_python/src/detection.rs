use glob::Pattern;
use ignore::WalkBuilder;
use std::path::{Path, PathBuf};

use crate::util::canonicalize_path;
use crate::{dependencies, devtools, lockfiles, pyproject, venvs};
use pi_lang::{
    DetectedTool, DetectionConfig, Package, Project, ToolchainEnvironment, ToolchainType, Workspace,
};
use tracing::warn;

#[derive(Debug, Clone)]
pub struct PossibleProjectRoot {
    path: PathBuf,
    lockfiles: Vec<DetectedTool>,
    toml: Option<pyproject::PyProjectInfo>,
    diagnostic_tools: Vec<DetectedTool>,
}

/// Detect all Python projects in a directory tree, handling workspaces correctly.
///
/// Use a multi-phase approach: scan down for all possible projects, scan up for
/// parent projects (workspaces), then consolidate to avoid duplicates.
///
/// # Errors
///
/// Return `anyhow::Error` if the root directory doesn't exist or isn't accessible.
pub fn detect_python_projects<P: AsRef<Path>>(
    root: P,
    config: Option<&DetectionConfig>,
) -> Result<Vec<Project>, anyhow::Error> {
    let root_path = root.as_ref();
    validate_root_path(root_path)?;

    let root = canonicalize_path(root_path);
    let default_config = DetectionConfig::default();
    let config = config.unwrap_or(&default_config);

    let possible_roots = collect_possible_roots(&root, config);
    let workspace_data = collect_workspace_data(&possible_roots);
    let projects = process_possible_roots(&possible_roots, &workspace_data);

    Ok(projects)
}

fn validate_root_path(root_path: &Path) -> Result<(), anyhow::Error> {
    if !root_path.exists() {
        return Err(anyhow::anyhow!(
            "Directory does not exist: {}",
            root_path.display()
        ));
    }
    if !root_path.is_dir() {
        return Err(anyhow::anyhow!(
            "Path is not a directory: {}",
            root_path.display()
        ));
    }
    Ok(())
}

fn collect_possible_roots(root: &Path, config: &DetectionConfig) -> Vec<PossibleProjectRoot> {
    let mut possible_roots: Vec<PossibleProjectRoot> = Vec::new();
    possible_roots.extend(scan_down_for_roots(root, config));
    possible_roots.extend(scan_up_for_roots(root, config));
    consolidate_diagnostic_only_projects(possible_roots)
}

#[must_use]
pub fn find_possible_project_root(root: &Path, config: &DetectionConfig) -> Option<PathBuf> {
    let mut possible_roots: Vec<PossibleProjectRoot> = Vec::new();
    possible_roots.extend(scan_up_for_roots(root, config));
    let possible_roots = consolidate_diagnostic_only_projects(possible_roots);
    if possible_roots.is_empty() {
        None
    } else {
        Some(possible_roots[0].path.clone())
    }
}

/// Workspace data: (`root_path`, `workspace_info`, `resolved_member_paths`)
type WorkspaceData<'a> = (PathBuf, &'a pyproject::WorkspaceInfo, Vec<PathBuf>);

fn collect_workspace_data(possible_roots: &[PossibleProjectRoot]) -> Vec<WorkspaceData<'_>> {
    let mut workspace_data = Vec::new();

    for possible_root in possible_roots {
        if let Some(toml) = &possible_root.toml
            && let Some(workspace_info) = &toml.workspace_info
        {
            let mut member_paths = Vec::new();
            // Resolve glob patterns to actual paths
            for member_pattern in &workspace_info.members {
                let paths = resolve_workspace_members(&possible_root.path, member_pattern);
                member_paths.extend(paths);
            }
            // Remove explicitly excluded paths
            for exclude_pattern in &workspace_info.exclude {
                let excluded_member_paths =
                    resolve_workspace_members(&possible_root.path, exclude_pattern);
                member_paths.retain(|m| !excluded_member_paths.contains(m));
            }

            workspace_data.push((possible_root.path.clone(), workspace_info, member_paths));
        }
    }

    workspace_data
}

fn process_possible_roots(
    possible_roots: &[PossibleProjectRoot],
    workspace_data: &[WorkspaceData<'_>],
) -> Vec<Project> {
    let (all_workspace_members, excluded_paths) = collect_workspace_member_paths(workspace_data);
    let mut projects = Vec::new();

    for possible_root in possible_roots {
        let path = &possible_root.path;

        if should_skip_possible_root(path, &all_workspace_members, &excluded_paths, possible_root) {
            continue;
        }

        let project_tools = collect_project_tools(possible_root);
        let deduplicated_project_tools = deduplicate_tools(project_tools);
        let venvs =
            venvs::detect_virtual_environments(path, venvs::EnvironmentLookupConfig::default());
        let workspace = build_workspace_for_project(
            path,
            workspace_data,
            possible_roots,
            &deduplicated_project_tools,
        );

        let project = create_project(possible_root, deduplicated_project_tools, venvs, workspace);
        projects.push(project);
    }

    projects
}

fn collect_workspace_member_paths(
    workspace_data: &[WorkspaceData<'_>],
) -> (
    std::collections::HashSet<PathBuf>,
    std::collections::HashSet<PathBuf>,
) {
    let mut all_workspace_members = std::collections::HashSet::new();
    let mut excluded_paths = std::collections::HashSet::new();

    for (workspace_path, workspace_info, member_paths) in workspace_data {
        all_workspace_members.extend(member_paths.iter().cloned());
        for exclude_pattern in &workspace_info.exclude {
            let excluded_member_paths = resolve_workspace_members(workspace_path, exclude_pattern);
            excluded_paths.extend(excluded_member_paths);
        }
    }

    (all_workspace_members, excluded_paths)
}

fn should_skip_possible_root(
    path: &Path,
    all_workspace_members: &std::collections::HashSet<PathBuf>,
    excluded_paths: &std::collections::HashSet<PathBuf>,
    possible_root: &PossibleProjectRoot,
) -> bool {
    // Skip workspace members - they'll be included in their workspace root
    if all_workspace_members.contains(path) || excluded_paths.contains(path) {
        return true;
    }
    // Skip tool-only configs without lockfiles - likely not standalone projects

    if let Some(toml) = &possible_root.toml
        && !toml.has_project_section
        && possible_root.lockfiles.is_empty()
    {
        return true;
    }

    false
}

fn collect_project_tools(possible_root: &PossibleProjectRoot) -> Vec<DetectedTool> {
    let mut project_tools = Vec::new();
    project_tools.extend(possible_root.lockfiles.clone());
    if let Some(toml) = &possible_root.toml {
        project_tools.extend(toml.tools.clone());
    }
    project_tools.extend(possible_root.diagnostic_tools.clone());
    project_tools
}

fn deduplicate_tools(mut tools: Vec<DetectedTool>) -> Vec<DetectedTool> {
    let mut deduplicated_tools = Vec::new();
    // Sort by confidence first to prefer higher-confidence detections
    tools.sort_by(|a, b| {
        b.confidence
            .partial_cmp(&a.confidence)
            .unwrap_or(std::cmp::Ordering::Equal)
    });

    let mut seen_tools = std::collections::HashSet::new();

    for tool in tools {
        let key = (tool.name.clone(), tool.tool_type);
        if seen_tools.insert(key) {
            deduplicated_tools.push(tool);
        }
    }

    deduplicated_tools
}

fn build_workspace_for_project(
    path: &Path,
    workspace_data: &[WorkspaceData<'_>],
    possible_roots: &[PossibleProjectRoot],
    deduplicated_project_tools: &[DetectedTool],
) -> Workspace {
    if let Some((ws_path, _, member_paths)) = workspace_data
        .iter()
        .find(|(ws_path, _, _)| ws_path == path)
    {
        build_multi_package_workspace(
            ws_path,
            member_paths,
            possible_roots,
            deduplicated_project_tools,
        )
    } else {
        build_single_package_workspace(path, deduplicated_project_tools)
    }
}

fn build_multi_package_workspace(
    ws_path: &Path,
    member_paths: &[PathBuf],
    possible_roots: &[PossibleProjectRoot],
    deduplicated_project_tools: &[DetectedTool],
) -> Workspace {
    let mut packages = Vec::new();
    // Always include workspace root as a package - it may contain its own dependencies
    let root_package = create_package_from_path(ws_path, "workspace", deduplicated_project_tools);
    packages.push(root_package);
    // Add each member as a separate package
    for member_path in member_paths {
        if let Some(member_possible_root) = possible_roots.iter().find(|pr| pr.path == *member_path)
        {
            let package_tools = collect_project_tools(member_possible_root);
            let deduplicated_package_tools = deduplicate_tools(package_tools);
            let package =
                create_package_from_path(member_path, "unknown", &deduplicated_package_tools);
            packages.push(package);
        }
    }

    Workspace {
        root: canonicalize_path(ws_path),
        members: packages,
    }
}

fn build_single_package_workspace(
    path: &Path,
    deduplicated_project_tools: &[DetectedTool],
) -> Workspace {
    let current_package = create_package_from_path(path, "project", deduplicated_project_tools);

    Workspace {
        root: canonicalize_path(path),
        members: vec![current_package],
    }
}

fn create_package_from_path(path: &Path, default_name: &str, tools: &[DetectedTool]) -> Package {
    let package_name = path
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or(default_name)
        .to_string();

    let package_dependencies = dependencies::detect_dependencies(path);
    Package {
        name: package_name,
        path: canonicalize_path(path),
        tools: tools.to_vec(),
        dependencies: package_dependencies,
    }
}

fn create_project(
    possible_root: &PossibleProjectRoot,
    deduplicated_project_tools: Vec<DetectedTool>,
    venvs: Vec<ToolchainEnvironment>,
    workspace: Workspace,
) -> Project {
    let toolchain_version_constraint = possible_root
        .toml
        .as_ref()
        .and_then(|toml| toml.requires_python.clone());

    let project_name = possible_root
        .toml
        .as_ref()
        .and_then(|toml| toml.name.clone());
    let project_description = possible_root
        .toml
        .as_ref()
        .and_then(|toml| toml.description.clone());

    Project {
        name: project_name,
        description: project_description,
        toolchain_type: ToolchainType::Python,
        tools: deduplicated_project_tools,
        toolchain_envs: venvs,
        workspace,
        toolchain_version_constraint,
    }
}

fn analyze_path(path: &Path, config: &DetectionConfig) -> Option<PossibleProjectRoot> {
    if !path.is_dir() || (path.is_dir() && should_skip_directory(path, config)) {
        return None;
    }

    let dir_lockfiles = lockfiles::detect_lockfiles(path);
    let toml = pyproject::analyze_pyproject_toml(path);
    let diagnostic_tools = devtools::detect_dev_tools(path);

    if !dir_lockfiles.is_empty() || toml.is_some() || !diagnostic_tools.is_empty() {
        Some(PossibleProjectRoot {
            path: path.to_path_buf(),
            lockfiles: dir_lockfiles,
            toml,
            diagnostic_tools,
        })
    } else {
        None
    }
}

fn scan_down_for_roots(root: &Path, config: &DetectionConfig) -> Vec<PossibleProjectRoot> {
    let mut detected = Vec::new();

    let mut walker = WalkBuilder::new(root);
    walker
        .max_depth(Some(config.max_depth))
        .follow_links(config.follow_links)
        .hidden(false) // Need to see .venv directories to skip them properly
        .git_ignore(true)
        .git_exclude(true);
    for skip_dir in &config.skip_dirs {
        walker.add_ignore(format!("{skip_dir}/**"));
    }

    for entry in walker.build() {
        match entry {
            Ok(entry) => {
                if let Some(project_root) = analyze_path(entry.path(), config) {
                    detected.push(project_root);
                }
            }
            Err(e) => {
                warn!("Error walking directory tree: {}", e);
            }
        }
    }

    detected
}

fn scan_up_for_roots(start: &Path, config: &DetectionConfig) -> Vec<PossibleProjectRoot> {
    let mut detected = Vec::new();
    let mut current_dir = start.parent();

    while let Some(dir) = current_dir {
        if let Some(project_root) = analyze_path(dir, config) {
            detected.push(project_root);
        }
        // Stop at filesystem boundaries or git repo boundaries
        if dir == Path::new("/") || dir.parent().is_none() || dir.join(".git").exists() {
            break;
        }

        current_dir = dir.parent();
    }

    detected
}

fn resolve_workspace_members(workspace_root: &Path, pattern: &str) -> Vec<PathBuf> {
    let mut results = Vec::new();
    let glob_pattern = if let Some(stripped) = pattern.strip_prefix('/') {
        stripped.to_string() // Remove leading slash for relative matching
    } else {
        pattern.to_string()
    };
    // Validate glob pattern before using it

    if let Err(e) = Pattern::new(&glob_pattern) {
        warn!("Invalid glob pattern '{}': {}", pattern, e);
        return results;
    }

    let search_pattern = workspace_root
        .join(&glob_pattern)
        .to_string_lossy()
        .to_string();
    match glob::glob(&search_pattern) {
        Ok(paths) => {
            for path_result in paths {
                match path_result {
                    Ok(path) => {
                        if path.is_dir() && path.join("pyproject.toml").exists() {
                            results.push(path);
                        }
                    }
                    Err(e) => {
                        warn!("Error processing glob match: {}", e);
                    }
                }
            }
        }
        Err(e) => {
            warn!("Error executing glob pattern '{}': {}", search_pattern, e);
        }
    }

    results
}

fn should_skip_directory(path: &Path, config: &DetectionConfig) -> bool {
    if let Some(dir_name) = path.file_name().and_then(|n| n.to_str()) {
        if config.skip_dirs.iter().any(|skip| skip == dir_name) {
            return true;
        }

        if is_virtual_environment(path) {
            return true;
        }
    }

    false
}

fn consolidate_diagnostic_only_projects(
    mut possible_roots: Vec<PossibleProjectRoot>,
) -> Vec<PossibleProjectRoot> {
    possible_roots.sort_by_key(|root| root.path.components().count());

    let mut consolidated_roots: Vec<PossibleProjectRoot> = Vec::new();
    let mut paths_to_skip = std::collections::HashSet::new();

    for possible_root in possible_roots {
        // Skip paths already consolidated into parent projects
        if paths_to_skip.contains(&possible_root.path) {
            continue;
        }

        let is_diagnostic_only = possible_root.lockfiles.is_empty()
            && possible_root
                .toml
                .as_ref()
                .is_none_or(|toml| !toml.has_project_section);

        if is_diagnostic_only {
            let mut found_parent = false;
            // Try to consolidate diagnostic tools into a parent project
            for parent_root in &mut consolidated_roots {
                if possible_root.path.starts_with(&parent_root.path)
                    && possible_root.path != parent_root.path
                {
                    parent_root
                        .diagnostic_tools
                        .extend(possible_root.diagnostic_tools.clone());
                    paths_to_skip.insert(possible_root.path.clone());
                    found_parent = true;
                    break;
                }
            }

            if !found_parent {
                consolidated_roots.push(possible_root);
            }
        } else {
            consolidated_roots.push(possible_root);
        }
    }

    consolidated_roots
}

fn is_virtual_environment(path: &Path) -> bool {
    // Check for PEP 405 virtual environment marker
    let pyvenv_cfg = path.join("pyvenv.cfg");
    pyvenv_cfg.is_file()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_should_skip_directory() {
        let config = DetectionConfig::default();
        let temp_dir = TempDir::new().unwrap();

        // Create directories to test
        let venv_dir = temp_dir.path().join("venv");
        fs::create_dir(&venv_dir).unwrap();

        let normal_dir = temp_dir.path().join("src");
        fs::create_dir(&normal_dir).unwrap();

        assert!(should_skip_directory(&venv_dir, &config));
        assert!(!should_skip_directory(&normal_dir, &config));
    }

    #[test]
    fn test_is_virtual_environment() {
        let temp_dir = TempDir::new().unwrap();

        // Create a directory with pyvenv.cfg
        let venv_dir = temp_dir.path().join("test_venv");
        fs::create_dir(&venv_dir).unwrap();
        fs::write(venv_dir.join("pyvenv.cfg"), "home = /usr/bin\n").unwrap();

        assert!(is_virtual_environment(&venv_dir));

        // Test regular directory
        let normal_dir = temp_dir.path().join("src");
        fs::create_dir(&normal_dir).unwrap();

        assert!(!is_virtual_environment(&normal_dir));
    }

    #[test]
    fn test_resolve_workspace_members() {
        let temp_dir = TempDir::new().unwrap();
        let workspace_root = temp_dir.path();

        // Create test structure
        let packages_dir = workspace_root.join("packages");
        fs::create_dir_all(&packages_dir).unwrap();

        // Create two package directories with pyproject.toml
        let pkg1_dir = packages_dir.join("pkg1");
        let pkg2_dir = packages_dir.join("pkg2");
        fs::create_dir(&pkg1_dir).unwrap();
        fs::create_dir(&pkg2_dir).unwrap();
        fs::write(
            pkg1_dir.join("pyproject.toml"),
            "[project]\nname = \"pkg1\"",
        )
        .unwrap();
        fs::write(
            pkg2_dir.join("pyproject.toml"),
            "[project]\nname = \"pkg2\"",
        )
        .unwrap();

        // Create a directory without pyproject.toml (should be ignored)
        let non_pkg_dir = packages_dir.join("not-a-package");
        fs::create_dir(&non_pkg_dir).unwrap();

        // Test glob pattern matching
        let results = resolve_workspace_members(workspace_root, "packages/*");
        assert_eq!(results.len(), 2);
        assert!(results.contains(&pkg1_dir));
        assert!(results.contains(&pkg2_dir));
        assert!(!results.iter().any(|p| p == &non_pkg_dir));

        // Test direct path matching
        let direct_results = resolve_workspace_members(workspace_root, "packages/pkg1");
        assert_eq!(direct_results.len(), 1);
        assert_eq!(direct_results[0], pkg1_dir);

        // Test non-existent pattern
        let empty_results = resolve_workspace_members(workspace_root, "nonexistent/*");
        assert!(empty_results.is_empty());
    }
}
