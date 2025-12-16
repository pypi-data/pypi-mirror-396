use path_absolutize::Absolutize;
use pi_lang::Dependency;
use std::collections::BTreeMap;
use std::path::Path;
use tracing::warn;
/// Detect and parse dependencies from a Rust project directory.
pub fn detect_dependencies(project_path: &Path) -> Vec<Dependency> {
    let mut dependencies = Vec::new();
    // Parse dependencies from Cargo.toml
    if let Some(mut cargo_deps) = parse_cargo_dependencies(project_path) {
        dependencies.append(&mut cargo_deps);
    }

    dependencies
}
/// Parse dependencies from Cargo.toml.
fn parse_cargo_dependencies(project_path: &Path) -> Option<Vec<Dependency>> {
    let cargo_toml_path = project_path.join("Cargo.toml");
    if !cargo_toml_path.exists() {
        return None;
    }

    let manifest = match cargo_toml::Manifest::from_path(&cargo_toml_path) {
        Ok(manifest) => manifest,
        Err(e) => {
            warn!(
                "Error parsing Cargo.toml at {}: {}",
                cargo_toml_path.display(),
                e
            );
            return None;
        }
    };

    let mut dependencies = Vec::new();
    // Parse regular dependencies
    for (name, dep) in &manifest.dependencies {
        let parsed_dep =
            parse_cargo_dependency(name, dep, None, None, "Cargo.toml", Some(project_path));
        dependencies.push(parsed_dep);
    }
    // Parse dev-dependencies
    for (name, dep) in &manifest.dev_dependencies {
        let parsed_dep = parse_cargo_dependency(
            name,
            dep,
            Some("dev".to_string()),
            None,
            "Cargo.toml",
            Some(project_path),
        );
        dependencies.push(parsed_dep);
    }
    // Parse build-dependencies
    for (name, dep) in &manifest.build_dependencies {
        let parsed_dep = parse_cargo_dependency(
            name,
            dep,
            Some("build".to_string()),
            None,
            "Cargo.toml",
            Some(project_path),
        );
        dependencies.push(parsed_dep);
    }
    // Parse target-specific dependencies
    for (target, target_config) in &manifest.target {
        let target_marker = format!("cfg({target})");
        // Regular dependencies for this target
        for (name, dep) in &target_config.dependencies {
            let parsed_dep = parse_cargo_dependency(
                name,
                dep,
                None,
                Some(target_marker.clone()),
                "Cargo.toml",
                Some(project_path),
            );
            dependencies.push(parsed_dep);
        }
        // Dev dependencies for this target
        for (name, dep) in &target_config.dev_dependencies {
            let parsed_dep = parse_cargo_dependency(
                name,
                dep,
                Some("dev".to_string()),
                Some(target_marker.clone()),
                "Cargo.toml",
                Some(project_path),
            );
            dependencies.push(parsed_dep);
        }
        // Build dependencies for this target
        for (name, dep) in &target_config.build_dependencies {
            let parsed_dep = parse_cargo_dependency(
                name,
                dep,
                Some("build".to_string()),
                Some(target_marker.clone()),
                "Cargo.toml",
                Some(project_path),
            );
            dependencies.push(parsed_dep);
        }
    }
    // Parse feature-gated dependencies from [features] section
    dependencies.extend(parse_feature_gated_dependencies(
        &manifest.features,
        "Cargo.toml",
    ));

    if dependencies.is_empty() {
        None
    } else {
        Some(dependencies)
    }
}
/// Parse a single Cargo dependency specification with base path for relative paths.
fn parse_cargo_dependency(
    name: &str,
    dep: &cargo_toml::Dependency,
    group: Option<String>,
    environment_markers: Option<String>,
    source: &str,
    base_path: Option<&Path>,
) -> Dependency {
    let (version_constraint, url, _optional, features, enabled_by_features) = match dep {
        cargo_toml::Dependency::Simple(version) => {
            (Some(version.clone()), None, false, vec![], vec![])
        }
        cargo_toml::Dependency::Detailed(detailed) => {
            let version = detailed.version.clone();
            let optional = detailed.optional;
            let features = detailed.features.clone();
            // Check for URL-based dependencies
            let url = detailed.git.as_ref().map_or_else(
                || {
                    detailed.path.as_ref().map(|path| {
                        let path_buf = std::path::Path::new(path);
                        let canonical_path = if path_buf.is_absolute() {
                            path.to_string()
                        } else if let Some(base) = base_path {
                            let joined = base.join(path);
                            joined.absolutize().map_or_else(
                                |_| joined.to_string_lossy().to_string(),
                                |absolute| absolute.to_string_lossy().to_string(),
                            )
                        } else {
                            path.to_string()
                        };
                        format!("file://{canonical_path}")
                    })
                },
                |git| {
                    let mut git_url = format!("git+{git}");
                    if let Some(branch) = &detailed.branch {
                        use std::fmt::Write;
                        write!(&mut git_url, "?branch={branch}").unwrap();
                    } else if let Some(tag) = &detailed.tag {
                        use std::fmt::Write;
                        write!(&mut git_url, "?tag={tag}").unwrap();
                    } else if let Some(rev) = &detailed.rev {
                        use std::fmt::Write;
                        write!(&mut git_url, "?rev={rev}").unwrap();
                    }
                    Some(git_url)
                },
            );

            let enabled_by_features = if optional {
                vec![name.to_string()]
            } else {
                vec![]
            };

            (version, url, optional, features, enabled_by_features)
        }
        cargo_toml::Dependency::Inherited(_inherited) => (None, None, false, vec![], vec![]),
    };

    Dependency {
        name: name.to_string(),
        version_constraint,
        url,
        optional: enabled_by_features,
        group,
        environment_markers,
        source: source.to_string(),
        features,
    }
}
/// Parse feature-gated dependencies from the [features] section.
fn parse_feature_gated_dependencies(
    features: &BTreeMap<String, Vec<String>>,
    source: &str,
) -> Vec<Dependency> {
    let mut dependencies = Vec::new();

    for (feature_name, feature_deps) in features {
        for dep in feature_deps {
            // Skip if this is just enabling another feature (contains '/')
            if dep.contains('/') {
                continue;
            }
            // Check if this is a dependency name (not just a feature activation)
            // In Cargo.toml features, dependencies are listed directly by name
            // Features that activate other features use 'dep:name' or 'name/feature' syntax
            if let Some(dep_name) = dep.strip_prefix("dep:") {
                // Remove "dep:" prefix
                dependencies.push(Dependency {
                    name: dep_name.to_string(),
                    version_constraint: None, // We don't know the version from the features table
                    url: None,
                    optional: vec![feature_name.clone()],
                    group: None,
                    environment_markers: None,
                    source: source.to_string(),
                    features: vec![],
                });
            } else if !dep.contains(':') && !dep.contains('/') {
                // This is likely a dependency name without version info
                // It's activated by this feature
                dependencies.push(Dependency {
                    name: dep.clone(),
                    version_constraint: None,
                    url: None,
                    optional: vec![feature_name.clone()],
                    group: None,
                    environment_markers: None,
                    source: source.to_string(),
                    features: vec![],
                });
            }
        }
    }

    dependencies
}
/// Resolve which features enable optional dependencies.
#[allow(dead_code)]
fn resolve_optional_dependency_features(
    dependencies: &mut [Dependency],
    features: &BTreeMap<String, Vec<String>>,
) {
    for dep in dependencies.iter_mut() {
        if dep.optional.len() == 1 && dep.optional[0] == dep.name {
            // This is an optional dependency that might be enabled by features
            // Find all features that enable this dependency
            let mut enabling_features = Vec::new();

            for (feature_name, feature_deps) in features {
                for feature_dep in feature_deps {
                    if feature_dep == &dep.name || feature_dep == &format!("dep:{}", dep.name) {
                        enabling_features.push(feature_name.clone());
                    }
                }
            }

            if !enabling_features.is_empty() {
                dep.optional = enabling_features;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_parse_basic_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let cargo_content = r#"
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
optional_dep = { version = "0.5", optional = true }

[dev-dependencies]
tokio-test = "0.4"

[build-dependencies]
cc = "1.0"
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(!dependencies.is_empty());

        // Check regular dependency
        let serde = dependencies.iter().find(|d| d.name == "serde").unwrap();
        assert_eq!(serde.version_constraint, Some("1.0".to_string()));
        assert!(serde.optional.is_empty());
        assert_eq!(serde.group, None);

        // Check dependency with features
        let tokio = dependencies.iter().find(|d| d.name == "tokio").unwrap();
        assert_eq!(tokio.features, vec!["full"]);
        assert!(tokio.optional.is_empty());

        // Check optional dependency
        let optional_dep = dependencies
            .iter()
            .find(|d| d.name == "optional_dep")
            .unwrap();
        assert_eq!(optional_dep.optional, vec!["optional_dep"]);

        // Check dev dependency
        let tokio_test = dependencies
            .iter()
            .find(|d| d.name == "tokio-test")
            .unwrap();
        assert_eq!(tokio_test.group, Some("dev".to_string()));

        // Check build dependency
        let cc = dependencies.iter().find(|d| d.name == "cc").unwrap();
        assert_eq!(cc.group, Some("build".to_string()));
    }

    #[test]
    fn test_parse_target_specific_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let cargo_content = r#"
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1.0"

[target.'cfg(windows)'.dependencies]
winapi = "0.3"

[target.'cfg(unix)'.dependencies]
libc = "0.2"

[target.'cfg(target_arch = "wasm32")'.dev-dependencies]
wasm-bindgen-test = "0.3"
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(!dependencies.is_empty());

        // Check regular dependency
        let serde = dependencies.iter().find(|d| d.name == "serde").unwrap();
        assert!(serde.environment_markers.is_none());

        // Check Windows-specific dependency
        let winapi = dependencies.iter().find(|d| d.name == "winapi").unwrap();
        assert_eq!(
            winapi.environment_markers,
            Some("cfg(cfg(windows))".to_string())
        );

        // Check Unix-specific dependency
        let libc = dependencies.iter().find(|d| d.name == "libc").unwrap();
        assert_eq!(libc.environment_markers, Some("cfg(cfg(unix))".to_string()));

        // Check WASM-specific dev dependency
        let wasm_bindgen_test = dependencies
            .iter()
            .find(|d| d.name == "wasm-bindgen-test")
            .unwrap();
        assert_eq!(wasm_bindgen_test.group, Some("dev".to_string()));
        assert_eq!(
            wasm_bindgen_test.environment_markers,
            Some("cfg(cfg(target_arch = \"wasm32\"))".to_string())
        );
    }

    #[test]
    fn test_parse_feature_gated_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let cargo_content = r#"
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", optional = true }
reqwest = { version = "0.11", optional = true }

[features]
json = ["serde"]
http = ["dep:reqwest", "reqwest/json"]
full = ["json", "http"]
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(!dependencies.is_empty());

        // Check optional dependency enabled by feature
        let serde_deps: Vec<_> = dependencies.iter().filter(|d| d.name == "serde").collect();
        assert!(!serde_deps.is_empty());

        // Should find serde as optional dependency
        let optional_serde = serde_deps
            .iter()
            .find(|d| d.optional.contains(&"serde".to_string()));
        assert!(optional_serde.is_some());

        // Check dependency with dep: syntax in features
        assert!(dependencies.iter().any(|d| d.name == "reqwest"));
    }

    #[test]
    fn test_workspace_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let cargo_content = r#"
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { workspace = true }
my-utils = { path = "../utils" }

[workspace]
members = ["utils"]

[workspace.dependencies]
serde = "1.0"
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(!dependencies.is_empty());

        // Should find serde (even if version comes from workspace)
        let serde = dependencies.iter().find(|d| d.name == "serde").unwrap();
        assert_eq!(serde.name, "serde");

        // Should find path dependency
        let my_utils = dependencies.iter().find(|d| d.name == "my-utils").unwrap();
        assert_eq!(my_utils.name, "my-utils");
    }

    #[test]
    fn test_no_cargo_toml() {
        let temp_dir = TempDir::new().unwrap();
        let dependencies = detect_dependencies(temp_dir.path());
        assert!(dependencies.is_empty());
    }

    #[test]
    fn test_invalid_cargo_toml() {
        let temp_dir = TempDir::new().unwrap();
        let invalid_content = r#"
[package
name = "invalid"
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), invalid_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(dependencies.is_empty());
    }

    #[test]
    fn test_complex_features() {
        let temp_dir = TempDir::new().unwrap();
        let cargo_content = r#"
[package]
name = "complex-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", optional = true }
serde_json = { version = "1.0", optional = true }
tokio = { version = "1.0", optional = true, features = ["rt"] }

[features]
default = []
json = ["dep:serde", "dep:serde_json"]
async = ["dep:tokio", "tokio/macros"]
full = ["json", "async"]
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(!dependencies.is_empty());

        // All dependencies should be marked as optional initially
        assert!(dependencies.iter().any(|d| d.name == "serde"));

        let tokio_deps: Vec<_> = dependencies.iter().filter(|d| d.name == "tokio").collect();
        assert!(!tokio_deps.is_empty());

        // Check that tokio has its base features
        let tokio_main = tokio_deps.iter().find(|d| !d.features.is_empty()).unwrap();
        assert!(tokio_main.features.contains(&"rt".to_string()));
    }

    #[test]
    fn test_git_and_path_dependencies() {
        let temp_dir = TempDir::new().unwrap();
        let cargo_content = r#"
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
my-git-dep = { git = "https://github.com/user/repo.git", branch = "main" }
my-path-dep = { path = "../local-crate" }
registry-dep = "1.0"
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(!dependencies.is_empty());

        // Should find all types of dependencies
        assert!(dependencies.iter().any(|d| d.name == "my-git-dep"));
        assert!(dependencies.iter().any(|d| d.name == "my-path-dep"));
        assert!(dependencies.iter().any(|d| d.name == "registry-dep"));

        // Git dependency should have URL
        let git_dep = dependencies
            .iter()
            .find(|d| d.name == "my-git-dep")
            .unwrap();
        assert_eq!(git_dep.version_constraint, None);
        assert!(git_dep.url.as_ref().unwrap().starts_with("git+"));
        assert!(git_dep.url.as_ref().unwrap().contains("branch=main"));

        // Path dependency should have URL
        let path_dep = dependencies
            .iter()
            .find(|d| d.name == "my-path-dep")
            .unwrap();
        assert_eq!(path_dep.version_constraint, None);
        assert!(path_dep.url.as_ref().unwrap().starts_with("file://"));

        // Registry dependency should have version
        let registry_dep = dependencies
            .iter()
            .find(|d| d.name == "registry-dep")
            .unwrap();
        assert_eq!(registry_dep.version_constraint, Some("1.0".to_string()));
        assert_eq!(registry_dep.url, None);
    }

    #[test]
    fn test_rust_url_dependencies_comprehensive() {
        let temp_dir = TempDir::new().unwrap();
        let cargo_content = r#"
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
# Git dependencies with various options
git-dep1 = { git = "https://github.com/user/repo.git" }
git-dep2 = { git = "https://github.com/user/repo.git", branch = "develop" }
git-dep3 = { git = "https://github.com/user/repo.git", tag = "v1.0" }
git-dep4 = { git = "https://github.com/user/repo.git", rev = "abc123" }

# Path dependencies
local-dep = { path = "../local-crate" }
relative-dep = { path = "crates/shared" }

# Regular version dependencies
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
"#;
        fs::write(temp_dir.path().join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(temp_dir.path());
        assert!(!dependencies.is_empty());

        // Check git dependency variants
        let git_dep1 = dependencies.iter().find(|d| d.name == "git-dep1").unwrap();
        assert_eq!(git_dep1.version_constraint, None);
        assert!(git_dep1.url.as_ref().unwrap().starts_with("git+https://"));
        assert!(!git_dep1.url.as_ref().unwrap().contains('?'));

        let git_dep2 = dependencies.iter().find(|d| d.name == "git-dep2").unwrap();
        assert_eq!(git_dep2.version_constraint, None);
        assert!(git_dep2.url.as_ref().unwrap().contains("?branch=develop"));

        let git_dep3 = dependencies.iter().find(|d| d.name == "git-dep3").unwrap();
        assert_eq!(git_dep3.version_constraint, None);
        assert!(git_dep3.url.as_ref().unwrap().contains("?tag=v1.0"));

        let git_dep4 = dependencies.iter().find(|d| d.name == "git-dep4").unwrap();
        assert_eq!(git_dep4.version_constraint, None);
        assert!(git_dep4.url.as_ref().unwrap().contains("?rev=abc123"));

        // Check path dependencies
        let local_dep = dependencies.iter().find(|d| d.name == "local-dep").unwrap();
        assert_eq!(local_dep.version_constraint, None);
        assert!(local_dep.url.as_ref().unwrap().starts_with("file://"));
        // Should be absolute path now, not relative
        assert!(!local_dep.url.as_ref().unwrap().contains("../"));

        let relative_dep = dependencies
            .iter()
            .find(|d| d.name == "relative-dep")
            .unwrap();
        assert_eq!(relative_dep.version_constraint, None);
        assert!(relative_dep.url.as_ref().unwrap().starts_with("file://"));
        // Should be absolute path now
        assert!(relative_dep.url.as_ref().unwrap().contains("crates/shared"));
        assert!(
            !relative_dep
                .url
                .as_ref()
                .unwrap()
                .starts_with("file://crates")
        );

        // Check version dependencies have no URL
        let serde = dependencies.iter().find(|d| d.name == "serde").unwrap();
        assert_eq!(serde.version_constraint, Some("1.0".to_string()));
        assert_eq!(serde.url, None);

        let tokio = dependencies.iter().find(|d| d.name == "tokio").unwrap();
        assert_eq!(tokio.version_constraint, Some("1.0".to_string()));
        assert_eq!(tokio.url, None);
        assert_eq!(tokio.features, vec!["full"]);
    }

    #[test]
    fn test_rust_relative_path_canonicalization() {
        let temp_dir = TempDir::new().unwrap();

        // Create a nested structure for testing relative paths
        let subdir = temp_dir.path().join("project");
        fs::create_dir_all(&subdir).unwrap();

        let cargo_content = r#"
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
# Relative path dependencies
local-dep = { path = "../local-crate" }
current-dep = { path = "./current" }
nested-dep = { path = "nested/shared" }

# Absolute path dependency
absolute-dep = { path = "/absolute/path" }

# Regular version dependency
serde = "1.0"
"#;
        fs::write(subdir.join("Cargo.toml"), cargo_content).unwrap();

        let dependencies = detect_dependencies(&subdir);
        assert!(!dependencies.is_empty());

        // Check relative path - should be canonicalized
        let local_dep = dependencies.iter().find(|d| d.name == "local-dep").unwrap();
        assert_eq!(local_dep.version_constraint, None);
        assert!(local_dep.url.as_ref().unwrap().starts_with("file://"));
        // Should be absolute path now, not relative
        assert!(!local_dep.url.as_ref().unwrap().contains("../"));

        // Check current directory relative path
        let current_dep = dependencies
            .iter()
            .find(|d| d.name == "current-dep")
            .unwrap();
        assert_eq!(current_dep.version_constraint, None);
        assert!(current_dep.url.as_ref().unwrap().starts_with("file://"));
        // Should be absolute path now
        assert!(!current_dep.url.as_ref().unwrap().contains("./"));

        // Check nested relative path
        let nested_dep = dependencies
            .iter()
            .find(|d| d.name == "nested-dep")
            .unwrap();
        assert_eq!(nested_dep.version_constraint, None);
        assert!(nested_dep.url.as_ref().unwrap().starts_with("file://"));
        // Should contain the nested path but be absolute
        assert!(nested_dep.url.as_ref().unwrap().contains("nested"));
        assert!(
            !nested_dep
                .url
                .as_ref()
                .unwrap()
                .starts_with("file://nested")
        );

        // Check absolute path - should remain unchanged
        let absolute_dep = dependencies
            .iter()
            .find(|d| d.name == "absolute-dep")
            .unwrap();
        assert_eq!(absolute_dep.version_constraint, None);
        assert_eq!(absolute_dep.url, Some("file:///absolute/path".to_string()));

        // Check version dependency has no URL
        let serde = dependencies.iter().find(|d| d.name == "serde").unwrap();
        assert_eq!(serde.version_constraint, Some("1.0".to_string()));
        assert_eq!(serde.url, None);
    }
}
