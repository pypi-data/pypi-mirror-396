use pi_lang::{DetectedTool, DetectionConfig, Project, ToolType, ToolchainType, Workspace};
use pi_lang_python::detect_python_projects;
use std::fs;
use std::path::{Path, PathBuf};
use tempfile::TempDir;

#[test]
fn test_virtual_environment_info_in_results() {
    use std::fs;

    let temp_dir = TempDir::new().unwrap();

    // Create a Python project with lockfile and pyproject.toml to trigger venv detection
    fs::write(temp_dir.path().join("poetry.lock"), "# Poetry lockfile\n").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[tool.poetry]
name = "test-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.9"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);
    let project = &result[0];

    // Should find poetry as a packaging tool
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        tool_names.contains(&"poetry"),
        "Should detect poetry from poetry.lock"
    );

    // Virtual environments array should be accessible
    let venvs = &project.toolchain_envs;

    // Test that we can access virtual environment properties
    for venv in venvs {
        // These fields should be accessible and well-typed
        let _ = &venv.executable;
        let _ = &venv.prefix;
        let _ = &venv.name;
        let _ = &venv.version;
        let _ = &venv.project;

        // If we have an executable, it should be a valid path
        if let Some(exe) = &venv.executable {
            assert!(
                exe.is_absolute(),
                "Executable path should be absolute: {exe:?}"
            );
        }

        // If we have a prefix, it should be a valid path
        if let Some(prefix) = &venv.prefix {
            assert!(
                prefix.is_absolute(),
                "Prefix path should be absolute: {prefix:?}"
            );
        }
    }

    // Verify the structure is properly serializable (important for API usage)
    let _serialized = serde_json::to_string(&result).expect("Result should be serializable");
}

#[test]
fn test_detect_with_nested_lockfile() {
    let temp_dir = TempDir::new().unwrap();

    // Create nested structure
    let subdir = temp_dir.path().join("packages").join("backend");
    fs::create_dir_all(&subdir).unwrap();
    fs::write(subdir.join("pdm.lock"), "pdm lockfile").unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);
    let project = &result[0];
    // Should find the nested lockfile
    assert_eq!(project.tools.len(), 1);
    assert_eq!(project.tools[0].name, "pdm");
}

#[test]
fn test_detect_with_parent_directory_lockfile() {
    let temp_dir = TempDir::new().unwrap();

    // Create .git directory to mark repo root
    let git_dir = temp_dir.path().join(".git");
    fs::create_dir(&git_dir).unwrap();

    // Create lockfile in root
    fs::write(temp_dir.path().join("uv.lock"), "uv lockfile").unwrap();

    // Create nested subdirectory to run detection from
    let subdir = temp_dir.path().join("src").join("mypackage");
    fs::create_dir_all(&subdir).unwrap();

    let result = detect_python_projects(&subdir, None).unwrap();
    assert_eq!(result.len(), 1);
    let project = &result[0];
    // Should find the lockfile in the parent directory
    assert_eq!(project.tools.len(), 1);
    assert_eq!(project.tools[0].name, "uv");
}

#[test]
fn test_detect_stops_at_git_directory() {
    let temp_dir = TempDir::new().unwrap();

    // Create nested structure with multiple lockfiles
    let root = temp_dir.path();
    let git_root = root.join("project");
    let nested_dir = git_root.join("src").join("deep");

    fs::create_dir_all(&nested_dir).unwrap();

    // Create .git at project level
    fs::create_dir(git_root.join(".git")).unwrap();

    // Create lockfiles at different levels
    fs::write(root.join("poetry.lock"), "outer poetry").unwrap(); // Should be ignored
    fs::write(git_root.join("uv.lock"), "inner uv").unwrap(); // Should be found

    let result = detect_python_projects(&nested_dir, None).unwrap();
    assert_eq!(result.len(), 1);
    let project = &result[0];
    // Should only find uv.lock from git root, not poetry.lock from outside
    assert_eq!(project.tools.len(), 1);
    assert_eq!(project.tools[0].name, "uv");
}

#[test]
fn test_custom_config() {
    let temp_dir = TempDir::new().unwrap();

    // Create a custom skip directory
    let skip_dir = temp_dir.path().join("custom_skip");
    fs::create_dir(&skip_dir).unwrap();
    fs::write(skip_dir.join("poetry.lock"), "should be ignored").unwrap();

    let mut config = DetectionConfig::default();
    config.skip_dirs.push("custom_skip".to_string());
    config.max_depth = 1;

    let result = detect_python_projects(temp_dir.path(), Some(&config)).unwrap();

    // Should not find the lockfile in the skipped directory
    assert!(result.is_empty());
}

#[test]
fn test_comprehensive_python_project_detection() {
    let temp_dir = TempDir::new().unwrap();

    // Create a comprehensive Python project with multiple indicators
    fs::write(temp_dir.path().join("uv.lock"), "# uv lockfile\n").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "test-project"
version = "0.1.0"

[tool.uv]
dev-dependencies = ["pytest>=6.0"]
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1, "Should detect a project");
    let project = &result[0];

    // Should find uv as a packaging tool
    assert!(
        !project.tools.is_empty(),
        "Should detect at least uv from lockfile"
    );

    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(tool_names.contains(&"uv"), "Should detect uv from uv.lock");

    // Verify the uv tool has correct properties
    let uv_tool = project.tools.iter().find(|t| t.name == "uv").unwrap();
    assert_eq!(uv_tool.tool_type, ToolType::Manager);
    assert!(
        uv_tool.confidence >= 0.9,
        "uv detection should have high confidence"
    );
    assert!(uv_tool.evidence.contains(&"uv.lock".to_string()));
}

#[test]
fn test_pyproject_toml_detection_only() {
    let temp_dir = TempDir::new().unwrap();

    // Create a project with only pyproject.toml
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "test-project"
version = "0.1.0"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1, "Should detect a project");
    let project = &result[0];

    // Should detect poetry from both backend and tool sections
    assert!(
        !project.tools.is_empty(),
        "Should detect poetry from pyproject.toml"
    );

    let poetry_tools: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.name == "poetry")
        .collect();

    assert_eq!(
        poetry_tools.len(),
        2,
        "Should detect poetry as both backend and manager"
    );

    let backend_tool = poetry_tools
        .iter()
        .find(|t| t.tool_type == ToolType::Backend)
        .unwrap();
    let manager_tool = poetry_tools
        .iter()
        .find(|t| t.tool_type == ToolType::Manager)
        .unwrap();

    assert!(
        backend_tool
            .evidence
            .iter()
            .any(|e| e.contains("build-backend"))
    );
    assert!(
        manager_tool
            .evidence
            .iter()
            .any(|e| e.contains("tool.poetry"))
    );
}

#[test]
fn test_pyproject_toml_with_lockfile_priority() {
    let temp_dir = TempDir::new().unwrap();

    // Create both uv.lock and pyproject.toml with different tools
    fs::write(temp_dir.path().join("uv.lock"), "# uv lockfile\n").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.rye]
managed = true
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1, "Should detect a project");
    let project = &result[0];

    // Should detect both uv (from lockfile) and hatch/rye (from pyproject.toml)
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();

    assert!(tool_names.contains(&"uv"), "Should detect uv from lockfile");
    assert!(
        tool_names.contains(&"hatch"),
        "Should detect hatch from pyproject.toml backend"
    );
    assert!(
        tool_names.contains(&"rye"),
        "Should detect rye from pyproject.toml tool section"
    );

    // uv should have highest confidence due to lockfile
    let uv_tool = project.tools.iter().find(|t| t.name == "uv").unwrap();
    assert!(
        uv_tool.confidence >= 0.95,
        "uv from lockfile should have highest confidence"
    );
}

#[test]
fn test_pyproject_toml_rust_backend() {
    let temp_dir = TempDir::new().unwrap();

    // Create a Rust-Python project with maturin
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "my-rust-python-package"
version = "0.1.0"

[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1, "Should detect a project");
    let project = &result[0];

    assert!(!project.tools.is_empty(), "Should detect maturin");

    let maturin_tool = project.tools.iter().find(|t| t.name == "maturin").unwrap();
    assert_eq!(maturin_tool.tool_type, ToolType::Backend);
    assert!(maturin_tool.confidence >= 0.9);
    assert!(maturin_tool.evidence.iter().any(|e| e.contains("maturin")));
}

#[test]
fn test_nested_pyproject_toml_detection() {
    let temp_dir = TempDir::new().unwrap();

    // Create nested structure with pyproject.toml in subdirectory
    let subdir = temp_dir.path().join("packages").join("core");
    fs::create_dir_all(&subdir).unwrap();

    fs::write(
        subdir.join("pyproject.toml"),
        r#"
[project]
name = "core-package"
version = "0.1.0"

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"

[tool.pdm]
version = {source = "file", path = "src/__version__.py"}
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1, "Should detect a project");
    let project = &result[0];

    // Should find PDM in nested directory (within max_depth)
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        tool_names.contains(&"pdm"),
        "Should detect PDM from nested pyproject.toml"
    );

    let pdm_tools: Vec<_> = project.tools.iter().filter(|t| t.name == "pdm").collect();

    assert_eq!(
        pdm_tools.len(),
        2,
        "Should detect PDM as both backend and manager"
    );
}

#[test]
fn test_detect_python_projects_workspace() {
    let temp_dir = TempDir::new().unwrap();

    // Create workspace root
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "workspace-root"
version = "0.1.0"

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/excluded"]

[tool.uv]
dev-dependencies = ["pytest"]
"#,
    )
    .unwrap();

    // Create workspace members
    let member1 = temp_dir.path().join("packages").join("member1");
    fs::create_dir_all(&member1).unwrap();
    fs::write(
        member1.join("pyproject.toml"),
        r#"
[project]
name = "member1"
version = "0.1.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"#,
    )
    .unwrap();

    let member2 = temp_dir.path().join("packages").join("member2");
    fs::create_dir_all(&member2).unwrap();
    fs::write(
        member2.join("pyproject.toml"),
        r#"
[project]
name = "member2"
version = "0.1.0"

[tool.pdm]
version = {source = "file", path = "src/__version__.py"}
"#,
    )
    .unwrap();

    // Create excluded member
    let excluded = temp_dir.path().join("packages").join("excluded");
    fs::create_dir_all(&excluded).unwrap();
    fs::write(
        excluded.join("pyproject.toml"),
        r#"
[project]
name = "excluded"
version = "0.1.0"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    // Should only detect the workspace root, not the members or excluded paths
    assert_eq!(result.len(), 1, "Should detect only workspace root");

    let workspace_project = &result[0];
    let temp_dir_canonical = temp_dir.path().canonicalize().unwrap();
    assert_eq!(workspace_project.workspace.root, temp_dir_canonical);

    // Should have workspace information
    let workspace = &workspace_project.workspace;
    assert_eq!(workspace.root, temp_dir_canonical);
    assert_eq!(workspace.members.len(), 3); // workspace root + member1 + member2, but not excluded

    // Should detect uv as manager
    let tool_names: Vec<&str> = workspace_project
        .tools
        .iter()
        .map(|t| t.name.as_str())
        .collect();
    assert!(tool_names.contains(&"uv"));

    // Should have workspace root as a package member
    let workspace_root_pkg = workspace
        .members
        .iter()
        .find(|p| p.path == workspace.root)
        .expect("Should find workspace root as a package");

    // Workspace root should have uv tool
    let root_tool_names: Vec<&str> = workspace_root_pkg
        .tools
        .iter()
        .map(|t| t.name.as_str())
        .collect();
    assert!(
        root_tool_names.contains(&"uv"),
        "Workspace root package should have uv tool"
    );
}

#[test]
fn test_detect_python_projects_tool_only_config() {
    let temp_dir = TempDir::new().unwrap();

    // Create tool-only pyproject.toml (no [project] section)
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r"
[tool.ruff]
line-length = 88

[tool.mypy]
strict = true
",
    )
    .unwrap();
    fs::write(temp_dir.path().join("uv.lock"), "# uv lockfile\n").unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    assert_eq!(result.len(), 1);
    let project = &result[0];

    let temp_dir_canonical = temp_dir.path().canonicalize().unwrap();
    assert_eq!(project.workspace.root, temp_dir_canonical);
    assert_eq!(project.tools.len(), 4); // uv (manager) + ruff (diagnostic + formatter) + mypy (diagnostic)

    // Should detect uv from lockfile
    let uv_tool = project.tools.iter().find(|t| t.name == "uv").unwrap();
    assert_eq!(uv_tool.tool_type, ToolType::Manager);

    // Should detect diagnostic tools from pyproject.toml
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(tool_names.contains(&"ruff"));
    assert!(tool_names.contains(&"mypy"));

    // Verify diagnostic tools are correctly classified
    let diagnostic_tools: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.tool_type == ToolType::Diagnostic)
        .collect();
    assert_eq!(diagnostic_tools.len(), 2); // ruff and mypy as diagnostics

    // Verify formatter tools are correctly classified
    let formatter_tools: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.tool_type == ToolType::Formatter)
        .collect();
    assert_eq!(formatter_tools.len(), 1); // ruff as formatter
}

#[test]
fn test_detect_python_projects_multiple_independent() {
    let temp_dir = TempDir::new().unwrap();

    // Create multiple independent projects (no workspace)
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "project1"
version = "0.1.0"

[tool.poetry]
name = "project1"
"#,
    )
    .unwrap();

    let subdir = temp_dir.path().join("subproject");
    fs::create_dir_all(&subdir).unwrap();
    fs::write(
        subdir.join("pyproject.toml"),
        r#"
[project]
name = "project2"
version = "0.1.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    // Should detect both projects
    assert_eq!(result.len(), 2);

    let project_names: Vec<_> = result
        .iter()
        .map(|p| p.workspace.root.file_name().unwrap_or_default())
        .collect();

    // One should be the temp dir, one should be subproject
    assert!(project_names.iter().any(|name| name == &"subproject"));
}

#[test]
fn test_tool_deduplication() {
    let temp_dir = TempDir::new().unwrap();

    // Create a project with both uv.lock and pyproject.toml with [tool.uv]
    // This should result in deduplication (only highest confidence uv tool)
    fs::write(temp_dir.path().join("uv.lock"), "# Generated by uv").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"

[tool.uv]
dev-dependencies = ["pytest>=6.0"]
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    assert_eq!(result.len(), 1);
    let project = &result[0];

    // Count uv tools - should only be one (deduplicated)
    let uv_tools: Vec<_> = project.tools.iter().filter(|t| t.name == "uv").collect();
    assert_eq!(
        uv_tools.len(),
        1,
        "Should have exactly one uv tool after deduplication"
    );

    // The remaining uv tool should have the highest confidence (from lockfile)
    let uv_tool = uv_tools[0];
    assert!(
        (uv_tool.confidence - 0.95).abs() < f64::EPSILON,
        "Should keep the highest confidence uv tool"
    );
    assert!(
        uv_tool.evidence.contains(&"uv.lock".to_string()),
        "Should keep evidence from lockfile detection"
    );
}

#[test]
fn test_toolchain_envs_not_in_tools() {
    let temp_dir = TempDir::new().unwrap();

    // Create a Python project
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"
"#,
    )
    .unwrap();

    // Create a virtual environment
    let venv_dir = temp_dir.path().join(".venv");
    fs::create_dir_all(venv_dir.join("bin")).unwrap();
    fs::write(
        venv_dir.join("bin").join("python"),
        "#!/usr/bin/env python3",
    )
    .unwrap();
    fs::write(
        venv_dir.join("pyvenv.cfg"),
        "home = /usr/bin\nversion = 3.13.7",
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    assert_eq!(result.len(), 1);
    let project = &result[0];

    // Virtual environments should NOT appear in tools list
    let env_tools: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.tool_type == ToolType::Environment)
        .collect();
    assert_eq!(
        env_tools.len(),
        0,
        "Virtual environments should not appear in tools list"
    );

    // But should appear in toolchain_envs list
    assert!(
        !project.toolchain_envs.is_empty(),
        "Should detect virtual environments separately"
    );
}

#[test]
fn test_deduplication_preserves_highest_confidence() {
    let temp_dir = TempDir::new().unwrap();

    // Create a scenario with multiple detections of the same tool with different confidence
    fs::write(temp_dir.path().join("poetry.lock"), "# Poetry lock file").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"

[tool.poetry]
name = "test-project"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    assert_eq!(result.len(), 1);
    let project = &result[0];

    // Should have exactly one poetry tool (manager) after deduplication
    let poetry_managers: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.name == "poetry" && t.tool_type == ToolType::Manager)
        .collect();
    assert_eq!(
        poetry_managers.len(),
        1,
        "Should deduplicate poetry manager tools"
    );

    // Should keep the highest confidence one (from lockfile)
    let poetry_manager = poetry_managers[0];
    assert!(
        (poetry_manager.confidence - 0.95).abs() < f64::EPSILON,
        "Should keep highest confidence poetry detection"
    );

    // Should also have poetry as backend
    let poetry_backends: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.name == "poetry" && t.tool_type == ToolType::Backend)
        .collect();
    assert_eq!(
        poetry_backends.len(),
        1,
        "Should have poetry backend detection"
    );
}

#[test]
fn test_virtual_environment_confidence_field() {
    let temp_dir = TempDir::new().unwrap();

    // Create a Python project
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);
    let project = &result[0];

    // Test that each virtual environment has all required fields
    for venv in &project.toolchain_envs {
        assert!(
            venv.executable.is_some() || venv.prefix.is_some(),
            "Virtual environment should have either executable or prefix"
        );
    }
}

#[test]
fn test_lockfile_evidence_inheritance_fixed() {
    let temp_dir = TempDir::new().unwrap();

    // Create main project with uv.lock
    fs::write(temp_dir.path().join("uv.lock"), "# Generated by uv").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "main-project"
version = "0.1.0"

[tool.uv]
dev-dependencies = ["pytest>=6.0"]
"#,
    )
    .unwrap();

    // Create subproject without uv.lock (should not inherit parent's lockfile)
    let subdir = temp_dir.path().canonicalize().unwrap().join("subproject");
    fs::create_dir_all(&subdir).unwrap();
    fs::write(
        subdir.join("pyproject.toml"),
        r#"
[project]
name = "sub-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    let canonical_temp = temp_dir.path().canonicalize().unwrap();

    // Should detect both projects
    assert_eq!(result.len(), 2);

    // Find main project and subproject
    let main_project = result
        .iter()
        .find(|p| p.workspace.root == canonical_temp)
        .expect("Should find main project");

    let sub_project = result
        .iter()
        .find(|p| p.workspace.root == subdir)
        .expect("Should find subproject");

    // Main project should have uv from lockfile
    let main_uv_tools: Vec<_> = main_project
        .tools
        .iter()
        .filter(|t| t.name == "uv" && t.tool_type == ToolType::Manager)
        .collect();
    assert_eq!(
        main_uv_tools.len(),
        1,
        "Main project should have uv manager from lockfile"
    );

    let main_uv = main_uv_tools[0];
    assert!(
        main_uv.evidence.contains(&"uv.lock".to_string()),
        "Main project uv should have lockfile evidence"
    );

    // Subproject should NOT have uv manager (no inheritance)
    let sub_uv_tools: Vec<_> = sub_project
        .tools
        .iter()
        .filter(|t| t.name == "uv" && t.tool_type == ToolType::Manager)
        .collect();
    assert_eq!(
        sub_uv_tools.len(),
        0,
        "Subproject should not inherit uv lockfile from parent directory"
    );

    // Subproject should have setuptools backend
    let sub_setuptools_tools: Vec<_> = sub_project
        .tools
        .iter()
        .filter(|t| t.name == "setuptools" && t.tool_type == ToolType::Backend)
        .collect();
    assert_eq!(
        sub_setuptools_tools.len(),
        1,
        "Subproject should have setuptools backend"
    );
}

#[test]
fn test_path_canonicalization() {
    let temp_dir = TempDir::new().unwrap();

    // Create a Python project
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"
"#,
    )
    .unwrap();

    // Create a virtual environment
    let venv_dir = temp_dir.path().join(".venv");
    fs::create_dir_all(venv_dir.join("bin")).unwrap();
    fs::write(
        venv_dir.join("bin").join("python"),
        "#!/usr/bin/env python3",
    )
    .unwrap();
    fs::write(
        venv_dir.join("pyvenv.cfg"),
        "home = /usr/bin\nversion = 3.13.7",
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    assert_eq!(result.len(), 1);
    let project = &result[0];

    // Workspace root should be canonical (absolute path)
    assert!(
        project.workspace.root.is_absolute(),
        "Workspace root should be absolute: {:?}",
        project.workspace.root
    );

    // The canonical path should resolve to the same location as the temp directory
    let canonical_temp = temp_dir.path().canonicalize().unwrap();
    assert_eq!(
        project.workspace.root, canonical_temp,
        "Workspace root should be canonicalized to match temp directory"
    );

    // Virtual environment paths should be canonical
    for venv in &project.toolchain_envs {
        if let Some(executable) = &venv.executable {
            assert!(
                executable.is_absolute(),
                "Virtual environment executable should be absolute: {executable:?}"
            );
        }
        if let Some(prefix) = &venv.prefix {
            assert!(
                prefix.is_absolute(),
                "Virtual environment prefix should be absolute: {prefix:?}"
            );
        }
        if let Some(project_path) = &venv.project {
            assert!(
                project_path.is_absolute(),
                "Virtual environment project path should be absolute: {project_path:?}"
            );
        }
    }

    // Workspace members should be canonical (if any)
    for member in &project.workspace.members {
        assert!(
            member.path.is_absolute(),
            "Workspace member should be absolute: {:?}",
            member.path
        );
    }
}

#[test]
fn test_working_directory_relative_path() {
    let temp_dir = TempDir::new().unwrap();

    // Create directory structure: temp_dir/project/.git and temp_dir/project/src/internal
    let project_root = temp_dir.path().join("project");
    let src_dir = project_root.join("src");
    let internal_dir = src_dir.join("internal");

    fs::create_dir_all(&internal_dir).unwrap();
    fs::create_dir(project_root.join(".git")).unwrap();

    // Add uv.lock at project root (like the real pi project)
    fs::write(project_root.join("uv.lock"), "# Generated by uv").unwrap();

    // Test 1: Detection from parent directory targeting subdirectory (should work)
    std::env::set_current_dir(&project_root).unwrap();
    let result1 = detect_python_projects(Path::new("src/internal"), None).unwrap();

    // Test 2: Detection from within subdirectory using "." (currently broken)
    std::env::set_current_dir(&internal_dir).unwrap();
    let result2 = detect_python_projects(Path::new("."), None).unwrap();

    // Both should find the uv tool from the parent directory
    assert_eq!(result1.len(), 1);
    assert_eq!(result2.len(), 1);

    let tools1: Vec<&str> = result1[0].tools.iter().map(|t| t.name.as_str()).collect();
    let tools2: Vec<&str> = result2[0].tools.iter().map(|t| t.name.as_str()).collect();

    assert!(
        tools1.contains(&"uv"),
        "Should find uv tool when run from parent targeting subdirectory"
    );
    assert!(
        tools2.contains(&"uv"),
        "Should find uv tool when run from within subdirectory with '.'"
    );

    // Both results should be equivalent
    assert_eq!(
        tools1, tools2,
        "Results should be the same regardless of working directory"
    );
}
#[test]
fn test_dependency_features_integration() {
    let temp_dir = TempDir::new().unwrap();

    // Create a project with dependencies that have extras/features
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "fastapi[standard]>=0.104.0",
    "sqlalchemy[postgresql,asyncio]>=2.0",
    "requests>=2.25.0"
]

[project.optional-dependencies]
dev = ["pytest[coverage]>=6.0", "black"]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];
    let package = &project.workspace.members[0];

    // Verify fastapi[standard] is parsed correctly
    let fastapi = package
        .dependencies
        .iter()
        .find(|d| d.name == "fastapi")
        .expect("Should find fastapi dependency");
    assert_eq!(fastapi.features, vec!["standard"]);
    assert!(fastapi.optional.is_empty());
    assert_eq!(fastapi.group, None);

    // Verify sqlalchemy[postgresql,asyncio] is parsed correctly
    let sqlalchemy = package
        .dependencies
        .iter()
        .find(|d| d.name == "sqlalchemy")
        .expect("Should find sqlalchemy dependency");
    assert_eq!(sqlalchemy.features.len(), 2);
    assert!(sqlalchemy.features.contains(&"postgresql".to_string()));
    assert!(sqlalchemy.features.contains(&"asyncio".to_string()));
    assert!(sqlalchemy.optional.is_empty());
    assert_eq!(sqlalchemy.group, None);

    // Verify requests (no extras) is parsed correctly
    let requests = package
        .dependencies
        .iter()
        .find(|d| d.name == "requests")
        .expect("Should find requests dependency");
    assert!(requests.features.is_empty());
    assert!(requests.optional.is_empty());
    assert_eq!(requests.group, None);

    // Verify pytest[coverage] in optional-dependencies
    let pytest = package
        .dependencies
        .iter()
        .find(|d| d.name == "pytest")
        .expect("Should find pytest dependency");
    assert_eq!(pytest.features, vec!["coverage"]);
    assert_eq!(pytest.optional, vec!["dev"]);
    assert_eq!(pytest.group, Some("optional".to_string()));

    // Verify black (no extras) in optional-dependencies
    let black = package
        .dependencies
        .iter()
        .find(|d| d.name == "black")
        .expect("Should find black dependency");
    assert!(black.features.is_empty());
    assert_eq!(black.optional, vec!["dev"]);
    assert_eq!(black.group, Some("optional".to_string()));

    // Test the convenience methods
    let all_deps = project.all_dependencies();
    assert_eq!(all_deps.len(), 5); // fastapi, sqlalchemy, requests, pytest, black

    let optional_deps = project.optional_dependencies();
    assert_eq!(optional_deps.len(), 2); // pytest, black

    let required_deps = project.required_dependencies();
    assert_eq!(required_deps.len(), 3); // fastapi, sqlalchemy, requests
}

#[test]
#[allow(clippy::too_many_lines)]
fn test_poetry_dependency_features_integration() {
    let temp_dir = TempDir::new().unwrap();

    // Create a comprehensive Poetry project with various dependency features
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[tool.poetry]
name = "poetry-test-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.8"
# Dependencies with extras
fastapi = { version = "^0.104.0", extras = ["standard"] }
sqlalchemy = { version = "^2.0", extras = ["postgresql", "asyncio"] }
# Git dependency with extras
django = { git = "https://github.com/django/django.git", extras = ["bcrypt"] }
# Dependencies with environment markers
pathlib2 = { version = "^2.2", python = "<3.4" }
pywin32 = { version = "^306", markers = "sys_platform == 'win32'" }
# URL dependency
urllib3 = { url = "https://example.com/urllib3-2.0.4.tar.gz" }
# Simple dependencies
requests = "^2.25.0"

[tool.poetry.group.dev.dependencies]
pytest = { version = "^7.0", extras = ["coverage"] }
black = "^23.0"
mypy = { version = "^1.0", extras = ["reports"] }

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"#,
    )
    .unwrap();

    // Add poetry.lock to ensure detection
    fs::write(temp_dir.path().join("poetry.lock"), "# Poetry lock file").unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];
    let package = &project.workspace.members[0];

    // Verify Poetry is detected as the main tool
    let poetry_tools: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.name == "poetry")
        .collect();
    assert!(!poetry_tools.is_empty(), "Should detect Poetry tools");

    // Test dependencies with extras
    let fastapi = package
        .dependencies
        .iter()
        .find(|d| d.name == "fastapi")
        .expect("Should find fastapi dependency");
    assert_eq!(fastapi.features, vec!["standard"]);
    assert!(fastapi.optional.is_empty());
    assert_eq!(fastapi.group, None);

    let sqlalchemy = package
        .dependencies
        .iter()
        .find(|d| d.name == "sqlalchemy")
        .expect("Should find sqlalchemy dependency");
    assert_eq!(sqlalchemy.features.len(), 2);
    assert!(sqlalchemy.features.contains(&"postgresql".to_string()));
    assert!(sqlalchemy.features.contains(&"asyncio".to_string()));

    // Test git dependency with extras
    let django = package
        .dependencies
        .iter()
        .find(|d| d.name == "django")
        .expect("Should find django dependency");
    assert_eq!(django.features, vec!["bcrypt"]);
    assert_eq!(django.version_constraint, None);
    assert!(django.url.as_ref().unwrap().contains("git+"));

    // Test dependencies with environment markers
    let pathlib2 = package
        .dependencies
        .iter()
        .find(|d| d.name == "pathlib2")
        .expect("Should find pathlib2 dependency");
    assert!(
        pathlib2
            .environment_markers
            .as_ref()
            .unwrap()
            .contains("python_version")
    );

    let pywin32 = package
        .dependencies
        .iter()
        .find(|d| d.name == "pywin32")
        .expect("Should find pywin32 dependency");
    assert!(
        pywin32
            .environment_markers
            .as_ref()
            .unwrap()
            .contains("sys_platform")
    );

    // Test URL dependency
    let urllib3 = package
        .dependencies
        .iter()
        .find(|d| d.name == "urllib3")
        .expect("Should find urllib3 dependency");
    assert_eq!(urllib3.version_constraint, None);
    assert!(urllib3.url.as_ref().unwrap().contains("example.com"));

    // Test simple dependency without extras
    let requests = package
        .dependencies
        .iter()
        .find(|d| d.name == "requests")
        .expect("Should find requests dependency");
    assert!(requests.features.is_empty());
    assert!(requests.optional.is_empty());

    // Test dev dependencies with extras
    let pytest = package
        .dependencies
        .iter()
        .find(|d| d.name == "pytest" && d.group == Some("dev".to_string()))
        .expect("Should find pytest dev dependency");
    assert_eq!(pytest.features, vec!["coverage"]);
    assert!(pytest.optional.is_empty());
    assert_eq!(pytest.group, Some("dev".to_string()));

    let mypy = package
        .dependencies
        .iter()
        .find(|d| d.name == "mypy" && d.group == Some("dev".to_string()))
        .expect("Should find mypy dev dependency");
    assert_eq!(mypy.features, vec!["reports"]);
    assert_eq!(mypy.group, Some("dev".to_string()));

    // Test dev dependency without extras
    let black = package
        .dependencies
        .iter()
        .find(|d| d.name == "black" && d.group == Some("dev".to_string()))
        .expect("Should find black dev dependency");
    assert!(black.features.is_empty());
    assert_eq!(black.group, Some("dev".to_string()));

    // Test convenience methods work with Poetry dependencies
    let all_deps = project.all_dependencies();
    let deps_with_features: Vec<_> = all_deps.iter().filter(|d| !d.features.is_empty()).collect();
    assert!(deps_with_features.len() >= 4); // fastapi, sqlalchemy, django, pytest, mypy

    let optional_deps = project.optional_dependencies();
    assert!(optional_deps.is_empty()); // No optional dependencies in this test

    let required_deps = project.required_dependencies();
    assert!(!required_deps.is_empty()); // Should have main dependencies
}

#[test]
fn test_multiple_project_detection_on_actual_project() {
    // Test the new multiple project detection on the actual project
    let current_dir = std::env::current_dir().unwrap();
    let project_root = current_dir
        .ancestors()
        .find(|path| path.join(".git").exists())
        .expect("Could not find project root with .git directory");

    let result = detect_python_projects(project_root, None).unwrap();

    // Should detect at least one project (the main project)
    assert!(
        !result.is_empty(),
        "Should detect at least one Python project"
    );

    // The main project should be detected
    let main_project = result
        .iter()
        .find(|p| p.workspace.root == project_root)
        .expect("Should find the main project root");

    // Should detect uv and potentially maturin
    let tool_names: Vec<&str> = main_project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        tool_names.contains(&"uv"),
        "Should detect uv from lockfile and/or pyproject.toml"
    );

    // The project uses a custom maturin_wrapper backend, should be detected as maturin
    let has_maturin_backend = main_project
        .tools
        .iter()
        .any(|t| t.name == "maturin" && t.tool_type == ToolType::Backend);

    if has_maturin_backend {
        let maturin_tool = main_project
            .tools
            .iter()
            .find(|t| t.name == "maturin" && t.tool_type == ToolType::Backend)
            .unwrap();
        assert!(
            maturin_tool
                .evidence
                .iter()
                .any(|e| e.contains("maturin_wrapper")),
            "Should detect custom maturin_wrapper backend"
        );
    }

    // Verify serialization works with the new structure
    let _serialized = serde_json::to_string(&result).expect("Should serialize successfully");
}

#[test]
fn test_lenient_error_handling_nonexistent_directory() {
    let nonexistent_path = Path::new("/this/path/definitely/does/not/exist");
    let result = detect_python_projects(nonexistent_path, None);

    // Should return an error for non-existent top-level directory
    assert!(result.is_err());
    let error = result.err().unwrap();
    assert!(error.to_string().contains("Directory does not exist"));
}

#[test]
fn test_lenient_error_handling_file_instead_of_directory() {
    let temp_dir = TempDir::new().unwrap();
    let file_path = temp_dir.path().join("not_a_directory.txt");
    fs::write(&file_path, "This is a file, not a directory").unwrap();

    let result = detect_python_projects(&file_path, None);

    // Should return an error when given a file instead of directory
    assert!(result.is_err());
    let error = result.err().unwrap();
    assert!(error.to_string().contains("Path is not a directory"));
}

#[test]
fn test_lenient_error_handling_continues_on_internal_errors() {
    let temp_dir = TempDir::new().unwrap();

    // Create a valid project
    fs::write(temp_dir.path().join("uv.lock"), "# uv lockfile").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"

[tool.uv]
dev-dependencies = ["pytest"]
"#,
    )
    .unwrap();

    // Create a subdirectory with permission issues (on Unix systems)
    let problematic_dir = temp_dir.path().join("problematic");
    fs::create_dir(&problematic_dir).unwrap();

    // Create a lockfile in the problematic directory
    fs::write(problematic_dir.join("poetry.lock"), "poetry lock").unwrap();

    // Make the directory unreadable (this will cause errors during scanning)
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&problematic_dir).unwrap().permissions();
        perms.set_mode(0o000); // No permissions
        fs::set_permissions(&problematic_dir, perms).unwrap();
    }

    // Detection should succeed despite internal errors
    let result = detect_python_projects(temp_dir.path(), None);

    // Restore permissions for cleanup
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&problematic_dir).unwrap().permissions();
        perms.set_mode(0o755); // Full permissions
        fs::set_permissions(&problematic_dir, perms).unwrap();
    }

    // Should succeed and detect at least the main project
    assert!(result.is_ok());
    let projects = result.unwrap();
    assert!(!projects.is_empty());

    // Should detect uv from the main directory
    let main_project = &projects[0];
    let tool_names: Vec<&str> = main_project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(tool_names.contains(&"uv"));
}

#[test]
fn test_lenient_error_handling_invalid_toml_files() {
    let temp_dir = TempDir::new().unwrap();

    // Create a valid lockfile
    fs::write(temp_dir.path().join("uv.lock"), "# uv lockfile").unwrap();

    // Create an invalid pyproject.toml that will cause parsing errors
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = # This is invalid TOML - missing value
"#,
    )
    .unwrap();

    // Detection should continue despite TOML parsing errors
    let result = detect_python_projects(temp_dir.path(), None);
    assert!(result.is_ok());

    let projects = result.unwrap();
    assert!(!projects.is_empty());

    // Should still detect uv from lockfile
    let project = &projects[0];
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(tool_names.contains(&"uv"));
}

#[test]
fn test_lenient_error_handling_empty_directory() {
    let temp_dir = TempDir::new().unwrap();

    // Detection on empty directory should succeed but find nothing
    let result = detect_python_projects(temp_dir.path(), None);
    assert!(result.is_ok());

    let projects = result.unwrap();
    assert!(projects.is_empty());
}

#[test]
fn test_convenience_methods() {
    // Create test tools with different types and confidence levels (pre-sorted by confidence)
    let high_confidence_manager = DetectedTool {
        tool_type: ToolType::Manager,
        name: "uv".to_string(),
        confidence: 0.95,
        evidence: vec!["uv.lock".to_string()],
    };

    let high_confidence_env = DetectedTool {
        tool_type: ToolType::Environment,
        name: "venv".to_string(),
        confidence: 0.85,
        evidence: vec![".venv/".to_string()],
    };

    let medium_confidence_backend = DetectedTool {
        tool_type: ToolType::Backend,
        name: "setuptools".to_string(),
        confidence: 0.75,
        evidence: vec!["setup.py".to_string()],
    };

    let low_confidence_manager = DetectedTool {
        tool_type: ToolType::Manager,
        name: "pip".to_string(),
        confidence: 0.5,
        evidence: vec!["requirements.txt".to_string()],
    };

    let project = Project {
        name: None,
        description: None,
        // Tools are pre-sorted by confidence (highest first)
        toolchain_type: ToolchainType::Python,
        tools: vec![
            high_confidence_manager.clone(),
            high_confidence_env.clone(),
            medium_confidence_backend.clone(),
            low_confidence_manager.clone(),
        ],
        toolchain_envs: vec![],
        workspace: Workspace {
            root: PathBuf::from("/test"),
            members: vec![],
        },
        toolchain_version_constraint: None,
    };

    // Test tools_of_type - should return tools in confidence order
    let managers = project.tools_of_type(ToolType::Manager);
    assert_eq!(managers.len(), 2);
    assert_eq!(managers[0].name, "uv"); // Higher confidence first
    assert_eq!(managers[1].name, "pip");

    let backends = project.tools_of_type(ToolType::Backend);
    assert_eq!(backends.len(), 1);
    assert_eq!(backends[0].name, "setuptools");

    let environments = project.tools_of_type(ToolType::Environment);
    assert_eq!(environments.len(), 1);
    assert_eq!(environments[0].name, "venv");

    // Test top_tool_of_type
    let top_manager = project.top_tool_of_type(ToolType::Manager);
    assert!(top_manager.is_some());
    assert_eq!(top_manager.unwrap().name, "uv");

    let top_backend = project.top_tool_of_type(ToolType::Backend);
    assert!(top_backend.is_some());
    assert_eq!(top_backend.unwrap().name, "setuptools");

    let top_env = project.top_tool_of_type(ToolType::Environment);
    assert!(top_env.is_some());
    assert_eq!(top_env.unwrap().name, "venv");
}

#[test]
fn test_convenience_methods_empty_project() {
    let empty_project = Project {
        name: None,
        description: None,
        toolchain_type: ToolchainType::Python,
        tools: vec![],
        toolchain_envs: vec![],
        workspace: Workspace {
            root: PathBuf::from("/empty"),
            members: vec![],
        },
        toolchain_version_constraint: None,
    };

    // All methods should handle empty tools gracefully
    assert_eq!(empty_project.tools_of_type(ToolType::Manager).len(), 0);
    assert!(empty_project.top_tool_of_type(ToolType::Manager).is_none());
    assert_eq!(empty_project.tools_of_type(ToolType::Backend).len(), 0);
    assert!(
        empty_project
            .top_tool_of_type(ToolType::Environment)
            .is_none()
    );
}

#[test]
fn test_diagnostic_tools_detection() {
    let temp_dir = TempDir::new().unwrap();

    // Create a comprehensive project with both packaging and diagnostic tools
    fs::write(temp_dir.path().join("uv.lock"), "# Generated by uv").unwrap();
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.uv]
dev-dependencies = ["pytest>=6.0"]

[tool.mypy]
python_version = "3.9"
strict = true

[tool.ruff]
line-length = 88
select = ["E", "F", "UP", "B"]

[tool.pytest]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.coverage:run]
source = ["src"]

[tool.black]
line-length = 88
"#,
    )
    .unwrap();

    // Create standalone config files
    fs::write(
        temp_dir.path().join(".flake8"),
        "[flake8]\nmax-line-length = 88",
    )
    .unwrap();
    fs::write(
        temp_dir.path().join("pytest.ini"),
        "[tool:pytest]\ntestpaths = tests",
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);
    let project = &result[0];

    // Verify we detect both packaging and diagnostic tools
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();

    // Packaging tools
    assert!(tool_names.contains(&"uv"), "Should detect uv from lockfile");

    // Diagnostic tools from pyproject.toml
    assert!(
        tool_names.contains(&"mypy"),
        "Should detect mypy from pyproject.toml"
    );

    // Diagnostic tools from standalone config files
    assert!(
        tool_names.contains(&"flake8"),
        "Should detect flake8 from .flake8"
    );

    // Verify tool types are correct
    let packaging_tools: Vec<_> = project
        .tools
        .iter()
        .filter(|t| matches!(t.tool_type, ToolType::Manager | ToolType::Backend))
        .collect();
    assert!(!packaging_tools.is_empty(), "Should have packaging tools");

    let diagnostic_tools: Vec<_> = project
        .tools
        .iter()
        .filter(|t| t.tool_type == ToolType::Diagnostic)
        .collect();
    assert!(
        diagnostic_tools.len() >= 2,
        "Should have multiple diagnostic tools"
    );

    // Verify confidence levels
    for tool in &project.tools {
        assert!(
            tool.confidence > 0.0,
            "All tools should have confidence > 0"
        );
        assert!(
            tool.confidence <= 1.0,
            "All tools should have confidence <= 1.0"
        );

        // Lockfile tools should have highest confidence
        if tool.name == "uv" && tool.tool_type == ToolType::Manager {
            assert!(
                tool.confidence >= 0.95,
                "Lockfile tools should have high confidence"
            );
        }
    }

    // Verify evidence is provided
    for tool in &project.tools {
        assert!(!tool.evidence.is_empty(), "All tools should have evidence");
    }
}

#[test]
fn test_package_struct_usage_in_workspace() {
    let temp_dir = TempDir::new().unwrap();

    // Create workspace root
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "workspace-root"
version = "0.1.0"

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv]
dev-dependencies = ["pytest"]
"#,
    )
    .unwrap();

    // Create workspace member 1
    let member1 = temp_dir.path().join("packages").join("member1");
    fs::create_dir_all(&member1).unwrap();
    fs::write(
        member1.join("pyproject.toml"),
        r#"
[project]
name = "member1"
version = "0.1.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.mypy]
strict = true
"#,
    )
    .unwrap();

    // Create workspace member 2
    let member2 = temp_dir.path().join("packages").join("member2");
    fs::create_dir_all(&member2).unwrap();
    fs::write(
        member2.join("pyproject.toml"),
        r#"
[project]
name = "member2"
version = "0.1.0"

[tool.poetry]
name = "member2"

[tool.ruff]
line-length = 88
"#,
    )
    .unwrap();
    fs::write(member2.join("poetry.lock"), "# Generated by Poetry").unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];

    // Should detect uv at project level
    let uv_tools: Vec<_> = project.tools.iter().filter(|t| t.name == "uv").collect();
    assert!(!uv_tools.is_empty(), "Should detect uv at project level");

    // Should have workspace members with their own tools
    assert_eq!(project.workspace.members.len(), 3); // workspace root + member1 + member2

    // Check workspace root package
    let workspace_root_pkg = project
        .workspace
        .members
        .iter()
        .find(|p| p.path == project.workspace.root)
        .expect("Should find workspace root as a package");

    let root_tool_names: Vec<&str> = workspace_root_pkg
        .tools
        .iter()
        .map(|t| t.name.as_str())
        .collect();
    assert!(
        root_tool_names.contains(&"uv"),
        "Workspace root should have uv tool"
    );

    // Check member1 package
    let member1_pkg = project
        .workspace
        .members
        .iter()
        .find(|p| p.name == "member1")
        .expect("Should find member1 package");

    let member1_tool_names: Vec<&str> = member1_pkg.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        member1_tool_names.contains(&"hatch"),
        "member1 should have hatch backend"
    );
    assert!(
        member1_tool_names.contains(&"mypy"),
        "member1 should have mypy diagnostic"
    );

    // Check member2 package
    let member2_pkg = project
        .workspace
        .members
        .iter()
        .find(|p| p.name == "member2")
        .expect("Should find member2 package");

    let member2_tool_names: Vec<&str> = member2_pkg.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        member2_tool_names.contains(&"poetry"),
        "member2 should have poetry from lockfile and tool section"
    );
    assert!(
        member2_tool_names.contains(&"ruff"),
        "member2 should have ruff diagnostic/formatter"
    );

    // Test new convenience methods for getting all tools from workspace
    let all_diagnostic_tools = project.all_tools_of_type(ToolType::Diagnostic);
    let diagnostic_names: Vec<&str> = all_diagnostic_tools
        .iter()
        .map(|t| t.name.as_str())
        .collect();
    assert!(
        diagnostic_names.contains(&"mypy"),
        "Should find mypy from member1"
    );
    assert!(
        diagnostic_names.contains(&"ruff"),
        "Should find ruff from member2"
    );

    let all_manager_tools = project.all_tools_of_type(ToolType::Manager);
    let manager_names: Vec<&str> = all_manager_tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        manager_names.contains(&"uv"),
        "Should find uv from project level"
    );
    assert!(
        manager_names.contains(&"poetry"),
        "Should find poetry from member2"
    );

    // Test holistic view - should include tools from both project and packages
    let all_tools = project.all_tools();
    assert!(
        all_tools.len() > project.tools.len(),
        "Should have more tools when including packages"
    );

    // Verify tools are sorted by confidence
    for i in 1..all_tools.len() {
        assert!(
            all_tools[i - 1].confidence >= all_tools[i].confidence,
            "All tools should be sorted by confidence"
        );
    }

    // Verify package paths are canonical
    for package in &project.workspace.members {
        assert!(
            package.path.is_absolute(),
            "Package path should be absolute"
        );
    }
}

#[test]
fn test_single_package_project_includes_itself_as_package() {
    let temp_dir = TempDir::new().unwrap();

    // Create a single-package project (not a workspace)
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "single-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.mypy]
strict = true

[tool.ruff]
line-length = 88
"#,
    )
    .unwrap();
    fs::write(temp_dir.path().join("poetry.lock"), "# Generated by Poetry").unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];

    // Should have tools at project level
    assert!(
        !project.tools.is_empty(),
        "Should have tools at project level"
    );
    let project_tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        project_tool_names.contains(&"poetry"),
        "Should have poetry from lockfile"
    );
    assert!(
        project_tool_names.contains(&"setuptools"),
        "Should have setuptools from backend"
    );

    // Should also have itself as a package in workspace members
    assert_eq!(
        project.workspace.members.len(),
        1,
        "Should have one package in workspace members"
    );

    let package = &project.workspace.members[0];
    assert_eq!(
        package.name,
        temp_dir.path().file_name().unwrap().to_str().unwrap()
    );
    assert_eq!(
        package.path, project.workspace.root,
        "Package path should match workspace root"
    );

    // Package should have the same tools (duplicative but consistent)
    assert!(!package.tools.is_empty(), "Package should have tools");
    let package_tool_names: Vec<&str> = package.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        package_tool_names.contains(&"poetry"),
        "Package should have poetry from lockfile"
    );
    assert!(
        package_tool_names.contains(&"setuptools"),
        "Package should have setuptools from backend"
    );
    assert!(
        package_tool_names.contains(&"mypy"),
        "Package should have mypy diagnostic"
    );
    assert!(
        package_tool_names.contains(&"ruff"),
        "Package should have ruff diagnostic/formatter"
    );

    // Verify convenience methods work correctly
    let all_tools = project.all_tools();
    assert!(
        all_tools.len() >= project.tools.len(),
        "Should have at least as many tools in holistic view"
    );

    // Test that we can distinguish between project-level and package-level access
    let project_managers = project.tools_of_type(ToolType::Manager);
    let all_managers = project.all_tools_of_type(ToolType::Manager);

    // Both should contain the same tools since it's a single package
    assert!(
        !project_managers.is_empty(),
        "Should have managers at project level"
    );
    assert!(
        !all_managers.is_empty(),
        "Should have managers in holistic view"
    );
}

#[test]
fn test_workspace_root_always_included_as_package() {
    let temp_dir = TempDir::new().unwrap();

    // Create a multi-package workspace
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "workspace-root"
version = "0.1.0"

[tool.uv.workspace]
members = ["packages/member1"]

[tool.uv]
dev-dependencies = ["pytest"]

[tool.mypy]
strict = true
"#,
    )
    .unwrap();

    // Create workspace member
    let member1 = temp_dir.path().join("packages").join("member1");
    fs::create_dir_all(&member1).unwrap();
    fs::write(
        member1.join("pyproject.toml"),
        r#"
[project]
name = "member1"
version = "0.1.0"

[tool.ruff]
line-length = 88
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];

    // Should have 2 packages: workspace root + member1
    assert_eq!(project.workspace.members.len(), 2);

    // Verify workspace root is included as a package
    let workspace_root_pkg = project
        .workspace
        .members
        .iter()
        .find(|p| p.path == project.workspace.root)
        .expect("Workspace root should always be included as a package");

    // Workspace root package should have expected name
    let expected_name = temp_dir.path().file_name().unwrap().to_str().unwrap();
    assert_eq!(workspace_root_pkg.name, expected_name);

    // Workspace root package should have its tools
    let root_tool_names: Vec<&str> = workspace_root_pkg
        .tools
        .iter()
        .map(|t| t.name.as_str())
        .collect();
    assert!(
        root_tool_names.contains(&"uv"),
        "Workspace root should have uv"
    );
    assert!(
        root_tool_names.contains(&"mypy"),
        "Workspace root should have mypy"
    );

    // Member1 should also be present
    let member1_pkg = project
        .workspace
        .members
        .iter()
        .find(|p| p.name == "member1")
        .expect("Should find member1 package");

    let member1_tool_names: Vec<&str> = member1_pkg.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        member1_tool_names.contains(&"ruff"),
        "Member1 should have ruff"
    );

    // Verify tools exist at both project level and package level
    let project_tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        project_tool_names.contains(&"uv"),
        "Project level should have uv"
    );
    assert!(
        project_tool_names.contains(&"mypy"),
        "Project level should have mypy"
    );
}

#[test]
fn test_tools_ordering() {
    // Test that tools maintain their sorted order
    let high_confidence_tool = DetectedTool {
        tool_type: ToolType::Manager,
        name: "poetry".to_string(),
        confidence: 0.8,
        evidence: vec!["poetry.lock".to_string()],
    };

    let low_confidence_tool = DetectedTool {
        tool_type: ToolType::Backend,
        name: "flit".to_string(),
        confidence: 0.6,
        evidence: vec!["pyproject.toml".to_string()],
    };

    let project = Project {
        name: None,
        description: None,
        toolchain_type: ToolchainType::Python,
        // Tools are pre-sorted by confidence (highest first)
        tools: vec![high_confidence_tool.clone(), low_confidence_tool.clone()],
        toolchain_envs: vec![],
        workspace: Workspace {
            root: PathBuf::from("/test"),
            members: vec![],
        },
        toolchain_version_constraint: None,
    };

    // Verify tools maintain sorted order
    assert!((project.tools[0].confidence - 0.8).abs() < f64::EPSILON);
    assert!((project.tools[1].confidence - 0.6).abs() < f64::EPSILON);
    assert_eq!(project.tools[0].name, "poetry");
    assert_eq!(project.tools[1].name, "flit");
}

#[test]
fn test_python_requires_python_constraint() {
    let temp_dir = TempDir::new().unwrap();

    // Create a project with requires-python constraint
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.9"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];
    assert_eq!(project.toolchain_type, ToolchainType::Python);
    assert_eq!(
        project.toolchain_version_constraint,
        Some(">=3.9".to_string())
    );
}

#[test]
fn test_python_project_name_and_description() {
    let temp_dir = TempDir::new().unwrap();

    // Test project with name and description
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "my-awesome-python-project"
version = "0.1.0"
description = "A really awesome Python project that does amazing things"
authors = ["Test Author <test@example.com>"]
requires-python = ">=3.9"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];
    assert_eq!(project.toolchain_type, ToolchainType::Python);
    assert_eq!(project.name, Some("my-awesome-python-project".to_string()));
    assert_eq!(
        project.description,
        Some("A really awesome Python project that does amazing things".to_string())
    );
    assert_eq!(
        project.toolchain_version_constraint,
        Some(">=3.9".to_string())
    );
}

#[test]
fn test_python_project_name_only() {
    let temp_dir = TempDir::new().unwrap();

    // Test project with name but no description
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "simple-python-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"#,
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];
    assert_eq!(project.name, Some("simple-python-project".to_string()));
    assert_eq!(project.description, None);
    assert_eq!(project.toolchain_version_constraint, None);
}

#[test]
fn test_python_no_requires_python_constraint() {
    let temp_dir = TempDir::new().unwrap();

    // Create a project without requires-python constraint
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

    let result = detect_python_projects(temp_dir.path(), None).unwrap();
    assert_eq!(result.len(), 1);

    let project = &result[0];
    assert_eq!(project.toolchain_type, ToolchainType::Python);
    assert_eq!(project.toolchain_version_constraint, None);
}

#[test]
fn test_sphinx_docs_directory_not_standalone_project() {
    let temp_dir = TempDir::new().unwrap();

    // Create main Python project with pyproject.toml
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "main-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.sphinx]
nitpicky = true
"#,
    )
    .unwrap();

    // Create docs directory with Sphinx configuration (conf.py)
    let docs_dir = temp_dir.path().join("docs");
    fs::create_dir_all(&docs_dir).unwrap();
    fs::write(
        docs_dir.join("conf.py"),
        r"
# Sphinx configuration file
project = 'Main Project'
author = 'Test Author'
extensions = ['sphinx.ext.autodoc']
",
    )
    .unwrap();

    // Create a requirements.txt in docs (common pattern for docs dependencies)
    fs::write(
        docs_dir.join("requirements.txt"),
        "sphinx>=4.0\nsphinx-rtd-theme\n",
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    // Should detect only ONE project (the main project), not treat docs/ as standalone
    assert_eq!(
        result.len(),
        1,
        "Should detect only main project, not docs as standalone"
    );

    let project = &result[0];

    // The detected project should be at the root level
    let temp_dir_canonical = temp_dir.path().canonicalize().unwrap();
    assert_eq!(project.workspace.root, temp_dir_canonical);

    // Should detect setuptools from main project and sphinx from tool.sphinx
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        tool_names.contains(&"setuptools"),
        "Should detect setuptools from main project"
    );
    assert!(
        tool_names.contains(&"sphinx"),
        "Should detect sphinx from [tool.sphinx] in main project"
    );

    // Verify that docs directory is not treated as a separate project
    // by checking that all detected tools come from the root directory
    for tool in &project.tools {
        for evidence in &tool.evidence {
            assert!(
                !evidence.contains("docs/") || evidence.contains("pyproject.toml"),
                "Tools should primarily come from main project, not docs directory. Found evidence: {evidence}"
            );
        }
    }
}

#[test]
fn test_sphinx_docs_directory_standalone_when_no_parent_project() {
    let temp_dir = TempDir::new().unwrap();

    // Create ONLY docs directory with Sphinx configuration, no parent project
    let docs_dir = temp_dir.path().join("docs");
    fs::create_dir_all(&docs_dir).unwrap();
    fs::write(
        docs_dir.join("conf.py"),
        r"
# Sphinx configuration file
project = 'Standalone Docs'
author = 'Test Author'
extensions = ['sphinx.ext.autodoc']
",
    )
    .unwrap();

    // Create a requirements.txt in docs
    fs::write(
        docs_dir.join("requirements.txt"),
        "sphinx>=4.0\nsphinx-rtd-theme\n",
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    // Should detect the docs directory as a standalone project since there's no enclosing Python project
    assert_eq!(
        result.len(),
        1,
        "Should detect docs as standalone project when no parent exists"
    );

    let project = &result[0];

    // The detected project should be at the docs directory level
    let docs_dir_canonical = docs_dir.canonicalize().unwrap();
    assert_eq!(project.workspace.root, docs_dir_canonical);

    // Should detect sphinx from conf.py
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        tool_names.contains(&"sphinx"),
        "Should detect sphinx from conf.py"
    );
}

#[test]
fn test_multiple_docs_directories_consolidated_into_parent() {
    let temp_dir = TempDir::new().unwrap();

    // Create main Python project
    fs::write(
        temp_dir.path().join("pyproject.toml"),
        r#"
[project]
name = "main-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"#,
    )
    .unwrap();

    // Create multiple docs directories
    let docs_dir = temp_dir.path().join("docs");
    fs::create_dir_all(&docs_dir).unwrap();
    fs::write(
        docs_dir.join("conf.py"),
        "project = 'Main Docs'\nextensions = ['sphinx.ext.autodoc']",
    )
    .unwrap();

    let api_docs_dir = temp_dir.path().join("api-docs");
    fs::create_dir_all(&api_docs_dir).unwrap();
    fs::write(
        api_docs_dir.join("conf.py"),
        "project = 'API Docs'\nextensions = ['sphinx.ext.autodoc']",
    )
    .unwrap();

    // Each docs dir has its own requirements
    fs::write(docs_dir.join("requirements.txt"), "sphinx>=4.0\n").unwrap();
    fs::write(
        api_docs_dir.join("requirements.txt"),
        "sphinx>=4.0\nsphinx-autodoc-typehints\n",
    )
    .unwrap();

    let result = detect_python_projects(temp_dir.path(), None).unwrap();

    // Should detect only the main project, with docs directories consolidated
    assert_eq!(
        result.len(),
        1,
        "Should consolidate all docs directories into parent project"
    );

    let project = &result[0];
    let temp_dir_canonical = temp_dir.path().canonicalize().unwrap();
    assert_eq!(project.workspace.root, temp_dir_canonical);

    // Should detect tools from main project
    let tool_names: Vec<&str> = project.tools.iter().map(|t| t.name.as_str()).collect();
    assert!(
        tool_names.contains(&"setuptools"),
        "Should detect setuptools from main project"
    );

    // Should detect sphinx from conf.py files but consolidated at project level
    assert!(
        tool_names.contains(&"sphinx"),
        "Should detect sphinx from docs directories"
    );
}
