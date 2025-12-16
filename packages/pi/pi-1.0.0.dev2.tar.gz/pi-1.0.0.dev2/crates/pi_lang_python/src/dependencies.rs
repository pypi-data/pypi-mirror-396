use std::path::Path;

use path_absolutize::Absolutize;
use pep508_rs::Requirement;
use pi_lang::Dependency;
use tracing::{debug, warn};

pub(crate) fn detect_dependencies(project_path: &Path) -> Vec<Dependency> {
    let mut dependencies = Vec::new();

    if let Some(mut pyproject_deps) = parse_pyproject_dependencies(project_path) {
        dependencies.append(&mut pyproject_deps);
    }

    if let Some(mut requirements_deps) = parse_requirements_files(project_path) {
        dependencies.append(&mut requirements_deps);
    }

    if let Some(mut setup_deps) = parse_setup_dependencies(project_path) {
        dependencies.append(&mut setup_deps);
    }

    dependencies
}

fn parse_pyproject_dependencies(project_path: &Path) -> Option<Vec<Dependency>> {
    let pyproject_path = project_path.join("pyproject.toml");
    if !pyproject_path.exists() {
        return None;
    }

    let content = match std::fs::read_to_string(&pyproject_path) {
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

    let pyproject: toml::Value = match toml::from_str(&content) {
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

    let mut dependencies = Vec::new();
    parse_project_dependencies(&pyproject, project_path, &mut dependencies);
    // Parse PEP 735 dependency groups - newer standard for organizing dependencies
    parse_dependency_groups(&pyproject, project_path, &mut dependencies);

    // Parse tool-specific dependencies (UV, Poetry, PDM have different formats)
    parse_tool_dependencies(&pyproject, project_path, &mut dependencies);

    if dependencies.is_empty() {
        None
    } else {
        Some(dependencies)
    }
}

fn parse_project_dependencies(
    pyproject: &toml::Value,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    let Some(project) = pyproject.get("project") else {
        return;
    };
    if let Some(deps) = project.get("dependencies").and_then(|d| d.as_array()) {
        parse_dependency_array(
            deps,
            None,
            None,
            "pyproject.toml",
            project_path,
            dependencies,
        );
    }
    // Parse [project.optional-dependencies] - these become "optional" group
    let Some(optional_deps) = project
        .get("optional-dependencies")
        .and_then(|d| d.as_table())
    else {
        return;
    };

    for (extra_name, deps) in optional_deps {
        let Some(deps_array) = deps.as_array() else {
            continue;
        };

        parse_dependency_array(
            deps_array,
            Some(extra_name),
            Some("optional"),
            "pyproject.toml",
            project_path,
            dependencies,
        );
    }
}

fn parse_dependency_groups(
    pyproject: &toml::Value,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    let Some(dep_groups) = pyproject
        .get("dependency-groups")
        .and_then(|d| d.as_table())
    else {
        return;
    };

    for (group_name, deps) in dep_groups {
        let Some(deps_array) = deps.as_array() else {
            continue;
        };

        parse_dependency_array(
            deps_array,
            None,
            Some(group_name),
            "pyproject.toml",
            project_path,
            dependencies,
        );
    }
}

fn parse_tool_dependencies(
    pyproject: &toml::Value,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    let Some(tool) = pyproject.get("tool") else {
        return;
    };
    parse_uv_dependencies(tool, project_path, dependencies);

    parse_poetry_tool_dependencies(tool, project_path, dependencies);

    parse_pdm_dependencies(tool, project_path, dependencies);
}

fn parse_uv_dependencies(
    tool: &toml::Value,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    let Some(uv) = tool.get("uv") else {
        return;
    };

    let Some(dev_deps) = uv.get("dev-dependencies").and_then(|d| d.as_array()) else {
        return;
    };

    parse_dependency_array(
        dev_deps,
        None,
        Some("dev"),
        "pyproject.toml",
        project_path,
        dependencies,
    );
}

fn parse_poetry_tool_dependencies(
    tool: &toml::Value,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    let Some(poetry) = tool.get("poetry") else {
        return;
    };
    if let Some(deps) = poetry.get("dependencies").and_then(|d| d.as_table()) {
        parse_poetry_dependency_table(deps, None, "pyproject.toml", project_path, dependencies);
    }

    if let Some(dev_deps) = poetry.get("dev-dependencies").and_then(|d| d.as_table()) {
        parse_poetry_dependency_table(
            dev_deps,
            Some("dev"),
            "pyproject.toml",
            project_path,
            dependencies,
        );
    }

    parse_poetry_dependency_groups(poetry, "pyproject.toml", project_path, dependencies);
}

fn parse_poetry_dependency_groups(
    poetry: &toml::Value,
    source: &str,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    let Some(group) = poetry.get("group").and_then(|g| g.as_table()) else {
        return;
    };

    for (group_name, group_config) in group {
        let Some(group_deps) = group_config.get("dependencies").and_then(|d| d.as_table()) else {
            continue;
        };

        parse_poetry_dependency_table(
            group_deps,
            Some(group_name),
            source,
            project_path,
            dependencies,
        );
    }
}

fn parse_poetry_dependency_table(
    deps_table: &toml::Table,
    group: Option<&str>,
    source: &str,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    for (name, spec) in deps_table {
        if name == "python" {
            continue;
        }

        if let Some(dependency) =
            parse_poetry_dependency(name, spec, group, source, Some(project_path))
        {
            dependencies.push(dependency);
        }
    }
}

fn parse_pdm_dependencies(
    tool: &toml::Value,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    let Some(pdm) = tool.get("pdm") else {
        return;
    };

    let Some(dev_deps) = pdm.get("dev-dependencies").and_then(|d| d.as_table()) else {
        return;
    };

    for (group_name, deps) in dev_deps {
        let Some(deps_array) = deps.as_array() else {
            continue;
        };

        parse_dependency_array(
            deps_array,
            None,
            Some(group_name),
            "pyproject.toml",
            project_path,
            dependencies,
        );
    }
}

fn parse_dependency_array(
    deps_array: &[toml::Value],
    extra_name: Option<&str>,
    group: Option<&str>,
    source: &str,
    project_path: &Path,
    dependencies: &mut Vec<Dependency>,
) {
    for dep in deps_array {
        let Some(dep_str) = dep.as_str() else {
            continue;
        };

        if let Some(parsed_dep) =
            parse_pep508_requirement(dep_str, extra_name, group, source, Some(project_path))
        {
            dependencies.push(parsed_dep);
        }
    }
}

fn parse_pep508_requirement(
    requirement_str: &str,
    extra_name: Option<&str>,
    group: Option<&str>,
    source: &str,
    base_path: Option<&Path>,
) -> Option<Dependency> {
    use pep508_rs::VersionOrUrl;

    match requirement_str.parse::<Requirement>() {
        Ok(req) => {
            let (version_constraint, url) = match &req.version_or_url {
                Some(VersionOrUrl::VersionSpecifier(version_specifiers)) => {
                    // Standard version constraint like ">=1.0,<2.0"
                    (Some(version_specifiers.to_string()), None)
                }
                Some(VersionOrUrl::Url(verbatim_url)) => {
                    // URL-based dependency (git, file, etc.) - canonicalize file paths
                    let url_str = verbatim_url.to_string();
                    let canonical_url = if url_str.starts_with("file://") {
                        canonicalize_file_url(&url_str, base_path)
                    } else {
                        url_str
                    };
                    (None, Some(canonical_url))
                }
                None => (None, None),
            };

            let environment_markers = req.marker.map(|m| m.to_string());

            let optional = if let Some(extra) = extra_name {
                vec![extra.to_string()]
            } else {
                vec![]
            };
            let features = req
                .extras
                .iter()
                .map(std::string::ToString::to_string)
                .collect();

            Some(Dependency {
                name: req.name.to_string(),
                version_constraint,
                url,
                optional,
                group: group.map(str::to_string),
                environment_markers,
                source: source.to_string(),
                features,
            })
        }
        Err(e) => {
            warn!("Error parsing requirement '{}': {}", requirement_str, e);
            None
        }
    }
}

fn parse_poetry_dependency(
    name: &str,
    spec: &toml::Value,
    group: Option<&str>,
    source: &str,
    base_path: Option<&Path>,
) -> Option<Dependency> {
    let (version_constraint, url, optional, environment_markers, features) = match spec {
        toml::Value::String(version) => (Some(version.clone()), None, vec![], None, vec![]),
        toml::Value::Table(table) => {
            let (version, url) = extract_version_constraint_and_url(table, base_path);

            let optional_extras = if table
                .get("optional")
                .and_then(toml::Value::as_bool)
                .unwrap_or(false)
            {
                vec!["optional".to_string()]
            } else {
                vec![]
            };

            let markers = extract_environment_markers(table);
            let extras = extract_poetry_extras(table);

            (version, url, optional_extras, markers, extras)
        }
        toml::Value::Array(array) => {
            // Multiple constraints for different Python versions - take first for simplicity
            if let Some(first_spec) = array.first() {
                return parse_poetry_dependency(name, first_spec, group, source, base_path);
            }
            (None, None, vec![], None, vec![])
        }
        _ => {
            warn!("Unsupported dependency format for '{}': {:?}", name, spec);
            return None;
        }
    };

    Some(Dependency {
        name: name.to_string(),
        version_constraint,
        url,
        optional,
        group: group.map(str::to_string),
        environment_markers,
        source: source.to_string(),
        features,
    })
}

fn extract_version_constraint_and_url(
    table: &toml::Table,
    base_path: Option<&Path>,
) -> (Option<String>, Option<String>) {
    if let Some(version) = table.get("version").and_then(|v| v.as_str()) {
        return (Some(version.to_string()), None);
    }

    if let Some(git) = table.get("git").and_then(|v| v.as_str()) {
        let mut git_spec = format!("git+{git}");
        if let Some(branch) = table.get("branch").and_then(|v| v.as_str()) {
            use std::fmt::Write;
            write!(&mut git_spec, "@{branch}").unwrap();
        } else if let Some(tag) = table.get("tag").and_then(|v| v.as_str()) {
            use std::fmt::Write;
            write!(&mut git_spec, "@{tag}").unwrap();
        } else if let Some(rev) = table.get("rev").and_then(|v| v.as_str()) {
            use std::fmt::Write;
            write!(&mut git_spec, "@{rev}").unwrap();
        }
        // Git subdirectory support for monorepos
        if let Some(subdir) = table.get("subdirectory").and_then(|v| v.as_str()) {
            use std::fmt::Write;
            write!(&mut git_spec, "#subdirectory={subdir}").unwrap();
        }

        return (None, Some(git_spec));
    }

    if let Some(url) = table.get("url").and_then(|v| v.as_str()) {
        return (None, Some(url.to_string()));
    }

    if let Some(path) = table.get("path").and_then(|v| v.as_str()) {
        let path_buf = std::path::Path::new(path);
        let canonical_path = if path_buf.is_absolute() {
            path.to_string()
        } else if let Some(base) = base_path {
            let joined = base.join(path);
            match joined.absolutize() {
                Ok(absolute) => absolute.to_string_lossy().to_string(),
                Err(_) => joined.to_string_lossy().to_string(),
            }
        } else {
            path.to_string()
        };
        return (None, Some(format!("file://{canonical_path}")));
    }

    (None, None)
}

fn canonicalize_file_url(url: &str, base_path: Option<&Path>) -> String {
    if let Some(stripped) = url.strip_prefix("file://") {
        let path_part = stripped;
        let path_buf = std::path::Path::new(path_part);

        let canonical_path = if path_buf.is_absolute() {
            path_part.to_string()
        } else if let Some(base) = base_path {
            let joined = base.join(path_part);
            match joined.absolutize() {
                Ok(absolute) => absolute.to_string_lossy().to_string(),
                Err(_) => joined.to_string_lossy().to_string(),
            }
        } else {
            path_part.to_string()
        };

        format!("file://{canonical_path}")
    } else {
        url.to_string()
    }
}

fn extract_environment_markers(table: &toml::Table) -> Option<String> {
    let mut markers = Vec::new();
    if let Some(marker_str) = table.get("markers").and_then(|v| v.as_str()) {
        markers.push(marker_str.to_string());
    }
    // Poetry-specific Python version becomes environment marker
    if let Some(python) = table.get("python").and_then(|v| v.as_str()) {
        markers.push(format!("python_version {python}"));
    }

    if markers.is_empty() {
        None
    } else {
        Some(markers.join(" and "))
    }
}

fn extract_poetry_extras(table: &toml::Table) -> Vec<String> {
    table
        .get("extras")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str())
                .map(std::string::ToString::to_string)
                .collect()
        })
        .unwrap_or_default()
}

fn parse_requirements_files(project_path: &Path) -> Option<Vec<Dependency>> {
    let mut dependencies = Vec::new();
    let requirements_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-test.txt",
        "requirements-docs.txt",
        "dev-requirements.txt",
        "test-requirements.txt",
    ];

    for filename in &requirements_files {
        let req_file = project_path.join(filename);
        if req_file.exists() {
            if let Some(mut file_deps) = parse_requirements_file(&req_file) {
                dependencies.append(&mut file_deps);
            }
        }
    }
    // Also scan requirements/ directory - common pattern for organized requirements
    let requirements_dir = project_path.join("requirements");
    if requirements_dir.is_dir() {
        if let Ok(entries) = std::fs::read_dir(&requirements_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.extension().is_some_and(|ext| ext == "txt") {
                    if let Some(mut file_deps) = parse_requirements_file(&path) {
                        dependencies.append(&mut file_deps);
                    }
                }
            }
        }
    }

    if dependencies.is_empty() {
        None
    } else {
        Some(dependencies)
    }
}

fn parse_requirements_file(file_path: &Path) -> Option<Vec<Dependency>> {
    let content = match std::fs::read_to_string(file_path) {
        Ok(content) => content,
        Err(e) => {
            debug!(
                "Error reading requirements file at {}: {}",
                file_path.display(),
                e
            );
            return None;
        }
    };

    let mut dependencies = Vec::new();
    let filename = file_path.file_name()?.to_str()?;
    let group = if filename.contains("dev") {
        Some("dev".to_string())
    } else if filename.contains("test") {
        Some("test".to_string())
    } else if filename.contains("docs") {
        Some("docs".to_string())
    } else {
        None
    };

    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        // Skip pip options like -r, -e, --index-url, etc.
        if line.starts_with('-') {
            continue;
        }

        if let Some(parsed_dep) = parse_pep508_requirement(
            line,
            None,
            group.as_deref(),
            filename,
            Some(file_path.parent().unwrap_or(std::path::Path::new("/"))),
        ) {
            dependencies.push(parsed_dep);
        }
    }

    if dependencies.is_empty() {
        None
    } else {
        Some(dependencies)
    }
}

fn parse_setup_dependencies(project_path: &Path) -> Option<Vec<Dependency>> {
    let mut dependencies = Vec::new();
    let setup_cfg = project_path.join("setup.cfg");
    if setup_cfg.exists() {
        if let Some(mut cfg_deps) = parse_setup_cfg(&setup_cfg) {
            dependencies.append(&mut cfg_deps);
        }
    }

    if dependencies.is_empty() {
        None
    } else {
        Some(dependencies)
    }
}

fn parse_setup_cfg(setup_cfg_path: &Path) -> Option<Vec<Dependency>> {
    let content = match std::fs::read_to_string(setup_cfg_path) {
        Ok(content) => content,
        Err(e) => {
            debug!(
                "Error reading setup.cfg at {}: {}",
                setup_cfg_path.display(),
                e
            );
            return None;
        }
    };
    // Parse INI-style configuration - setup.cfg uses ConfigParser format
    let mut dependencies = Vec::new();
    let mut in_install_requires = false;
    let mut in_extras_require = false;
    let current_extra = String::new();

    for line in content.lines() {
        let line = line.trim();

        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        if line.starts_with('[') && line.ends_with(']') {
            let current_section = line[1..line.len() - 1].to_string();
            in_install_requires = current_section == "options" || line.contains("install_requires");
            in_extras_require = line.contains("extras_require");
            continue;
        }

        if in_install_requires && line.starts_with("install_requires") {
            let deps_part = line.split('=').nth(1).unwrap_or("").trim();
            if !deps_part.is_empty() {
                for dep_line in deps_part.lines() {
                    let dep_line = dep_line.trim();
                    if !dep_line.is_empty() {
                        if let Some(parsed_dep) = parse_pep508_requirement(
                            dep_line,
                            None,
                            None,
                            "setup.cfg",
                            Some(setup_cfg_path.parent().unwrap_or(std::path::Path::new("/"))),
                        ) {
                            dependencies.push(parsed_dep);
                        }
                    }
                }
            }
            continue;
        }

        if in_extras_require && line.contains('=') {
            let parts: Vec<&str> = line.split('=').collect();
            if parts.len() == 2 {
                let deps_part = parts[1].trim();
                if !deps_part.is_empty() {
                    if let Some(parsed_dep) = parse_pep508_requirement(
                        deps_part,
                        Some(&current_extra),
                        Some("optional"),
                        "setup.cfg",
                        Some(setup_cfg_path.parent().unwrap_or(std::path::Path::new("/"))),
                    ) {
                        dependencies.push(parsed_dep);
                    }
                }
            }
        }
    }

    if dependencies.is_empty() {
        None
    } else {
        Some(dependencies)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_parse_pyproject_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[project]
name = "test-project"
dependencies = [
    "requests>=2.25.0",
    "click~=8.0",
    "importlib-metadata; python_version<'3.8'"
]

[project.optional-dependencies]
dev = ["pytest>=6.0", "black"]
test = ["coverage[toml]>=5.0"]

[dependency-groups]
docs = ["sphinx>=4.0", "sphinx-rtd-theme"]
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check main dependencies
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.optional.is_empty());
        assert_eq!(requests.group, None);
        assert!(requests.version_constraint.is_some());

        // Check optional dependencies
        let pytest = dependencies.iter().find(|d| d.name == "pytest").unwrap();
        assert_eq!(pytest.optional, vec!["dev"]);
        assert_eq!(pytest.group, Some("optional".to_string()));

        // Check dependency groups (PEP 735)
        let sphinx = dependencies.iter().find(|d| d.name == "sphinx").unwrap();
        assert!(sphinx.optional.is_empty());
        assert_eq!(sphinx.group, Some("docs".to_string()));

        // Check environment markers
        let importlib = dependencies
            .iter()
            .find(|d| d.name == "importlib-metadata")
            .unwrap();
        assert!(importlib.environment_markers.is_some());
        assert!(
            importlib
                .environment_markers
                .as_ref()
                .unwrap()
                .contains("python_version")
        );
    }

    #[test]
    fn test_parse_requirements_txt() {
        let temp_dir = TempDir::new().unwrap();
        let requirements_content = r"
# Main dependencies
requests>=2.25.0
click~=8.0

# Development tools
-e git+https://github.com/example/package.git#egg=package
";
        fs::write(
            temp_dir.path().join("requirements.txt"),
            requirements_content,
        )
        .unwrap();

        let requirements_dev_content = r"
pytest>=6.0
black==22.3.0
";
        fs::write(
            temp_dir.path().join("requirements-dev.txt"),
            requirements_dev_content,
        )
        .unwrap();

        let dependencies = parse_requirements_files(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check main dependencies
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.optional.is_empty());
        assert_eq!(requests.group, None);
        assert_eq!(requests.source, "requirements.txt");

        // Check dev dependencies
        let pytest = dependencies.iter().find(|d| d.name == "pytest").unwrap();
        assert!(pytest.optional.is_empty());
        assert_eq!(pytest.group, Some("dev".to_string()));
        assert_eq!(pytest.source, "requirements-dev.txt");
    }

    #[test]
    fn test_parse_poetry_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.25.0"
click = {version = "^8.0", optional = true}

[tool.poetry.group.dev.dependencies]
pytest = "^6.0"
black = "^22.0"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check regular dependencies
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.optional.is_empty());
        assert_eq!(requests.group, None);

        // Check optional dependencies
        let click = dependencies.iter().find(|d| d.name == "click").unwrap();
        assert_eq!(click.optional, vec!["optional"]);

        // Check dev group dependencies
        let pytest = dependencies.iter().find(|d| d.name == "pytest").unwrap();
        assert!(pytest.optional.is_empty());
        assert_eq!(pytest.group, Some("dev".to_string()));

        // Python version should be skipped
        assert!(!dependencies.iter().any(|d| d.name == "python"));
    }

    #[test]
    fn test_no_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let dependencies = detect_dependencies(temp_dir.path());
        assert!(dependencies.is_empty());
    }

    #[test]
    fn test_invalid_pyproject_toml() {
        let temp_dir = TempDir::new().unwrap();
        let invalid_content = r#"
[project
name = "invalid"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), invalid_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path());
        assert!(dependencies.is_none());
    }

    #[test]
    fn test_parse_uv_dev_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[project]
name = "test-project"
dependencies = ["requests>=2.25.0"]

[tool.uv]
dev-dependencies = ["pytest>=6.0", "black"]
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check main dependencies
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.optional.is_empty());
        assert_eq!(requests.group, None);

        // Check uv dev dependencies
        let pytest = dependencies.iter().find(|d| d.name == "pytest").unwrap();
        assert!(pytest.optional.is_empty());
        assert_eq!(pytest.group, Some("dev".to_string()));
    }

    #[test]
    fn test_parse_dependency_extras() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[project]
name = "test-project"
dependencies = [
    "fastapi[standard]>=0.104.0",
    "sqlalchemy[postgresql,asyncio]>=2.0",
    "requests>=2.25.0"
]

[project.optional-dependencies]
dev = ["pytest[coverage]>=6.0", "black"]
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check fastapi with single extra
        let fastapi = dependencies.iter().find(|d| d.name == "fastapi").unwrap();
        assert!(fastapi.optional.is_empty());
        assert_eq!(fastapi.group, None);
        assert_eq!(fastapi.features, vec!["standard"]);

        // Check sqlalchemy with multiple extras
        let sqlalchemy = dependencies
            .iter()
            .find(|d| d.name == "sqlalchemy")
            .unwrap();
        assert!(sqlalchemy.optional.is_empty());
        assert_eq!(sqlalchemy.group, None);
        assert_eq!(sqlalchemy.features.len(), 2);
        assert!(sqlalchemy.features.contains(&"postgresql".to_string()));
        assert!(sqlalchemy.features.contains(&"asyncio".to_string()));

        // Check requests without extras
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.optional.is_empty());
        assert_eq!(requests.group, None);
        assert!(requests.features.is_empty());

        // Check pytest with extras in optional dependencies
        let pytest = dependencies.iter().find(|d| d.name == "pytest").unwrap();
        assert_eq!(pytest.optional, vec!["dev"]);
        assert_eq!(pytest.group, Some("optional".to_string()));
        assert_eq!(pytest.features, vec!["coverage"]);

        // Check black without extras in optional dependencies
        let black = dependencies.iter().find(|d| d.name == "black").unwrap();
        assert_eq!(black.optional, vec!["dev"]);
        assert_eq!(black.group, Some("optional".to_string()));
        assert!(black.features.is_empty());
    }

    #[test]
    fn test_parse_requirements_txt_with_extras() {
        let temp_dir = TempDir::new().unwrap();
        let requirements_content = r"
# Main dependencies with extras
fastapi[standard]>=0.104.0
sqlalchemy[postgresql,asyncio]>=2.0
requests>=2.25.0

# Development tools with extras
pytest[coverage]>=6.0
black==22.3.0
";
        fs::write(
            temp_dir.path().join("requirements.txt"),
            requirements_content,
        )
        .unwrap();

        let dependencies = parse_requirements_files(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check fastapi with single extra
        let fastapi = dependencies.iter().find(|d| d.name == "fastapi").unwrap();
        assert!(fastapi.optional.is_empty());
        assert_eq!(fastapi.group, None);
        assert_eq!(fastapi.features, vec!["standard"]);

        // Check sqlalchemy with multiple extras
        let sqlalchemy = dependencies
            .iter()
            .find(|d| d.name == "sqlalchemy")
            .unwrap();
        assert!(sqlalchemy.optional.is_empty());
        assert_eq!(sqlalchemy.group, None);
        assert_eq!(sqlalchemy.features.len(), 2);
        assert!(sqlalchemy.features.contains(&"postgresql".to_string()));
        assert!(sqlalchemy.features.contains(&"asyncio".to_string()));

        // Check requests without extras
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.optional.is_empty());
        assert_eq!(requests.group, None);
        assert!(requests.features.is_empty());

        // Check pytest with extras
        let pytest = dependencies.iter().find(|d| d.name == "pytest").unwrap();
        assert!(pytest.optional.is_empty());
        assert_eq!(pytest.group, None);
        assert_eq!(pytest.features, vec!["coverage"]);

        // Check black without extras
        let black = dependencies.iter().find(|d| d.name == "black").unwrap();
        assert!(black.optional.is_empty());
        assert_eq!(black.group, None);
        assert!(black.features.is_empty());
    }

    #[test]
    fn test_parse_poetry_dependencies_with_extras() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.8"
# Simple extras
gunicorn = { version = "^20.1", extras = ["gevent"] }
# Multiple extras
sqlalchemy = { version = "^2.0", extras = ["postgresql", "asyncio"] }
# No extras
requests = "^2.25.0"
# Git dependency with extras
django = { git = "https://github.com/django/django.git", extras = ["bcrypt"] }
# Path dependency with extras
local-package = { path = "../local", extras = ["dev"] }
# URL dependency with extras
remote-package = { url = "https://example.com/package.tar.gz", extras = ["extra1"] }
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check gunicorn with single extra
        let gunicorn = dependencies.iter().find(|d| d.name == "gunicorn").unwrap();
        assert!(gunicorn.optional.is_empty());
        assert_eq!(gunicorn.group, None);
        assert_eq!(gunicorn.features, vec!["gevent"]);
        assert!(
            gunicorn
                .version_constraint
                .as_ref()
                .unwrap()
                .contains("20.1")
        );

        // Check sqlalchemy with multiple extras
        let sqlalchemy = dependencies
            .iter()
            .find(|d| d.name == "sqlalchemy")
            .unwrap();
        assert!(sqlalchemy.optional.is_empty());
        assert_eq!(sqlalchemy.group, None);
        assert_eq!(sqlalchemy.features.len(), 2);
        assert!(sqlalchemy.features.contains(&"postgresql".to_string()));
        assert!(sqlalchemy.features.contains(&"asyncio".to_string()));

        // Check requests without extras
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.optional.is_empty());
        assert_eq!(requests.group, None);
        assert!(requests.features.is_empty());

        // Check git dependency with extras
        let django = dependencies.iter().find(|d| d.name == "django").unwrap();
        assert!(django.optional.is_empty());
        assert_eq!(django.group, None);
        assert_eq!(django.features, vec!["bcrypt"]);
        assert_eq!(django.version_constraint, None);
        assert!(django.url.as_ref().unwrap().contains("git+"));

        // Check path dependency with extras
        let local_pkg = dependencies
            .iter()
            .find(|d| d.name == "local-package")
            .unwrap();
        assert!(local_pkg.optional.is_empty());
        assert_eq!(local_pkg.group, None);
        assert_eq!(local_pkg.features, vec!["dev"]);
        assert_eq!(local_pkg.version_constraint, None);
        assert!(local_pkg.url.as_ref().unwrap().contains("file://"));

        // Check URL dependency with extras
        let remote_pkg = dependencies
            .iter()
            .find(|d| d.name == "remote-package")
            .unwrap();
        assert!(remote_pkg.optional.is_empty());
        assert_eq!(remote_pkg.group, None);
        assert_eq!(remote_pkg.features, vec!["extra1"]);
        assert_eq!(remote_pkg.version_constraint, None);
        assert!(remote_pkg.url.as_ref().unwrap().contains("example.com"));

        // Python version should be skipped
        assert!(!dependencies.iter().any(|d| d.name == "python"));
    }

    #[test]
    fn test_parse_poetry_dependencies_advanced_features() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.8"
# Dependency with Python version constraint
pathlib2 = { version = "^2.2", python = "^3.9" }
# Dependency with markers
win-package = { version = "^1.0", markers = "sys_platform == 'win32'" }
# Dependency with both markers and Python constraint
complex-dep = { version = "^1.0", python = ">=3.8", markers = "platform_machine == 'x86_64'" }
# Git dependency with branch and subdirectory
git-complex = { git = "https://github.com/user/repo.git", branch = "main", subdirectory = "subdir" }
# Optional dependency
optional-dep = { version = "^1.0", optional = true }

[tool.poetry.group.dev.dependencies]
# Dev dependency with extras
pytest = { version = "^6.0", extras = ["coverage"] }
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check pathlib2 with Python version constraint
        let pathlib2 = dependencies.iter().find(|d| d.name == "pathlib2").unwrap();
        assert!(
            pathlib2
                .environment_markers
                .as_ref()
                .unwrap()
                .contains("python_version")
        );

        // Check win-package with markers
        let win_pkg = dependencies
            .iter()
            .find(|d| d.name == "win-package")
            .unwrap();
        assert!(
            win_pkg
                .environment_markers
                .as_ref()
                .unwrap()
                .contains("sys_platform")
        );

        // Check complex dependency with both Python and markers
        let complex_dep = dependencies
            .iter()
            .find(|d| d.name == "complex-dep")
            .unwrap();
        let markers = complex_dep.environment_markers.as_ref().unwrap();
        assert!(markers.contains("python_version"));
        assert!(markers.contains("platform_machine"));

        // Check git dependency with branch and subdirectory
        let git_complex = dependencies
            .iter()
            .find(|d| d.name == "git-complex")
            .unwrap();
        assert_eq!(git_complex.version_constraint, None);
        let git_url = git_complex.url.as_ref().unwrap();
        assert!(git_url.contains("git+"));
        assert!(git_url.contains("@main"));
        assert!(git_url.contains("#subdirectory=subdir"));

        // Check optional dependency
        let optional_dep = dependencies
            .iter()
            .find(|d| d.name == "optional-dep")
            .unwrap();
        assert_eq!(optional_dep.optional, vec!["optional"]);

        // Check dev dependency with extras
        let pytest = dependencies
            .iter()
            .find(|d| d.name == "pytest" && d.group == Some("dev".to_string()))
            .unwrap();
        assert!(pytest.optional.is_empty());
        assert_eq!(pytest.group, Some("dev".to_string()));
        assert_eq!(pytest.features, vec!["coverage"]);
    }

    #[test]
    fn test_pep508_version_constraint_parsing() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[project]
name = "test-project"
dependencies = [
    "requests>=2.25.0",
    "django @ https://github.com/django/django/archive/main.zip",
    "my-package @ git+https://github.com/user/repo.git",
    "local-package @ file:///path/to/local/package"
]
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check version constraint dependency
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert_eq!(requests.version_constraint, Some(">=2.25.0".to_string()));
        assert_eq!(requests.url, None);

        // Check URL-based dependencies
        let django = dependencies.iter().find(|d| d.name == "django").unwrap();
        assert_eq!(django.version_constraint, None);
        assert_eq!(
            django.url,
            Some("https://github.com/django/django/archive/main.zip".to_string())
        );

        let my_package = dependencies
            .iter()
            .find(|d| d.name == "my-package")
            .unwrap();
        assert_eq!(my_package.version_constraint, None);
        assert!(my_package.url.as_ref().unwrap().starts_with("git+https://"));

        let local_package = dependencies
            .iter()
            .find(|d| d.name == "local-package")
            .unwrap();
        assert_eq!(local_package.version_constraint, None);
        assert!(local_package.url.as_ref().unwrap().starts_with("file://"));
    }

    #[test]
    fn test_parse_poetry_url_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let pyproject_content = r#"
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.8"
# Git dependency
django = { git = "https://github.com/django/django.git", branch = "main" }
# URL dependency
urllib3 = { url = "https://example.com/urllib3-2.0.4.tar.gz" }
# Path dependency
local-package = { path = "../local" }
# Regular version dependency
requests = "^2.25.0"
"#;
        fs::write(temp_dir.path().join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(temp_dir.path()).unwrap();
        assert!(!dependencies.is_empty());

        // Check Git dependency
        let django = dependencies.iter().find(|d| d.name == "django").unwrap();
        assert_eq!(django.version_constraint, None);
        assert!(django.url.as_ref().unwrap().starts_with("git+https://"));
        assert!(django.url.as_ref().unwrap().contains("@main"));

        // Check URL dependency
        let urllib3 = dependencies.iter().find(|d| d.name == "urllib3").unwrap();
        assert_eq!(urllib3.version_constraint, None);
        assert_eq!(
            urllib3.url,
            Some("https://example.com/urllib3-2.0.4.tar.gz".to_string())
        );

        // Check path dependency - should be canonicalized to absolute path
        let local_pkg = dependencies
            .iter()
            .find(|d| d.name == "local-package")
            .unwrap();
        assert_eq!(local_pkg.version_constraint, None);
        assert!(local_pkg.url.as_ref().unwrap().starts_with("file://"));
        // The path should be absolute now, not relative
        assert!(!local_pkg.url.as_ref().unwrap().contains("../"));

        // Check regular version dependency
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.version_constraint.is_some());
        assert_eq!(requests.url, None);

        // Python version should be skipped
        assert!(!dependencies.iter().any(|d| d.name == "python"));
    }

    #[test]
    fn test_parse_poetry_relative_path_canonicalization() {
        let temp_dir = TempDir::new().unwrap();

        // Create a nested structure for testing relative paths
        let subdir = temp_dir.path().join("project");
        fs::create_dir_all(&subdir).unwrap();

        let pyproject_content = r#"
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.8"
# Relative path dependencies (Poetry style)
local-package = { path = "../local" }
current-package = { path = "./current" }
nested-package = { path = "nested/shared" }
# Absolute path dependency
absolute-package = { path = "/absolute/path" }
# Regular version dependency
requests = "^2.25.0"
"#;
        fs::write(subdir.join("pyproject.toml"), pyproject_content).unwrap();

        let dependencies = parse_pyproject_dependencies(&subdir).unwrap();
        assert!(!dependencies.is_empty());

        // Debug: Print all found dependencies
        for dep in &dependencies {
            println!(
                "Found dependency: {} with version_constraint={:?} and url={:?}",
                dep.name, dep.version_constraint, dep.url
            );
        }

        // Check regular version dependency
        let requests = dependencies.iter().find(|d| d.name == "requests").unwrap();
        assert!(requests.version_constraint.is_some());
        assert_eq!(requests.url, None);

        // Check relative path - should be canonicalized to absolute path
        let local_package = dependencies
            .iter()
            .find(|d| d.name == "local-package")
            .unwrap();
        assert_eq!(local_package.version_constraint, None);
        assert!(local_package.url.as_ref().unwrap().starts_with("file://"));
        // Should be absolute path now, not relative
        assert!(!local_package.url.as_ref().unwrap().contains("../"));

        // Check current directory relative path
        let current_package = dependencies
            .iter()
            .find(|d| d.name == "current-package")
            .unwrap();
        assert_eq!(current_package.version_constraint, None);
        assert!(current_package.url.as_ref().unwrap().starts_with("file://"));
        // Should be absolute path now
        assert!(!current_package.url.as_ref().unwrap().contains("./"));

        // Check nested relative path
        let nested_package = dependencies
            .iter()
            .find(|d| d.name == "nested-package")
            .unwrap();
        assert_eq!(nested_package.version_constraint, None);
        assert!(nested_package.url.as_ref().unwrap().starts_with("file://"));
        // Should contain the nested path but be absolute
        assert!(nested_package.url.as_ref().unwrap().contains("nested"));

        // Check absolute path - should remain unchanged
        let absolute_package = dependencies
            .iter()
            .find(|d| d.name == "absolute-package")
            .unwrap();
        assert_eq!(absolute_package.version_constraint, None);
        assert_eq!(
            absolute_package.url,
            Some("file:///absolute/path".to_string())
        );

        // Python version should be skipped
        assert!(!dependencies.iter().any(|d| d.name == "python"));
    }
}
