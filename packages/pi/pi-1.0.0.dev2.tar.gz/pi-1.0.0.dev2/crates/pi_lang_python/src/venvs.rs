//! Virtual environment detection using python-environment-tools
//!
//! This module provides functionality to detect Python virtual environments
//! using the python-environment-tools (PET) crate.

use std::cmp::Ordering;
use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::str::FromStr;
use std::sync::Arc;

use tracing::debug;

use pet_core::Configuration;
use pet_core::os_environment::Environment;
use pet_core::python_environment::{PythonEnvironment, PythonEnvironmentKind};

use crate::util::{canonicalize_path, canonicalize_path_option};
use pi_lang::ToolchainEnvironment;

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct EnvironmentLookupConfig {
    /// Whether to look for Python installations in global locations
    /// (as opposed to known virtual environments locations)
    pub include_global: bool,
}

/// Environment API implementation for PET
#[derive(Default)]
struct EnvironmentApi {
    pet_env: pet_core::os_environment::EnvironmentApi,
    config: EnvironmentLookupConfig,
}

impl EnvironmentApi {
    pub fn new(config: EnvironmentLookupConfig) -> Self {
        EnvironmentApi {
            pet_env: pet_core::os_environment::EnvironmentApi::new(),
            config,
        }
    }
}
/// The Environment for PET is intentionally local-only
/// because we only care about project-local toolchains.
impl Environment for EnvironmentApi {
    fn get_user_home(&self) -> Option<PathBuf> {
        self.pet_env.get_user_home()
    }

    fn get_root(&self) -> Option<PathBuf> {
        None
    }

    fn get_env_var(&self, key: String) -> Option<String> {
        self.pet_env.get_env_var(key)
    }

    fn get_know_global_search_locations(&self) -> Vec<PathBuf> {
        if self.config.include_global {
            self.pet_env.get_know_global_search_locations()
        } else {
            vec![]
        }
    }
}
/// Environment priority list (higher priority = lower index)
static ENV_PRIORITY_LIST: &[PythonEnvironmentKind] = &[
    // Project-local environments
    PythonEnvironmentKind::Poetry,
    PythonEnvironmentKind::Pipenv,
    PythonEnvironmentKind::Venv,
    PythonEnvironmentKind::VirtualEnv,
    PythonEnvironmentKind::VirtualEnvWrapper,
    PythonEnvironmentKind::PyenvVirtualEnv,
    PythonEnvironmentKind::Conda,
    // Managed global Python installs
    PythonEnvironmentKind::Pixi,
    PythonEnvironmentKind::Pyenv,
    PythonEnvironmentKind::Homebrew,
    PythonEnvironmentKind::GlobalPaths,
];

fn env_priority(kind: Option<PythonEnvironmentKind>) -> usize {
    if let Some(kind) = kind {
        ENV_PRIORITY_LIST
            .iter()
            .position(|blessed_env| blessed_env == &kind)
            .unwrap_or(ENV_PRIORITY_LIST.len())
    } else {
        ENV_PRIORITY_LIST.len() + 1
    }
}

/// Return the name of environment declared in <path>/.venv.
///
/// <https://virtualfish.readthedocs.io/en/latest/plugins.html#auto-activation-auto-activation>
fn get_path_venv_declaration(path: &Path) -> Option<String> {
    let venv_file = path.join(".venv");
    if !venv_file.is_file() {
        return None;
    }

    let content = std::fs::read_to_string(&venv_file).ok()?;
    let venv_name = content.lines().next()?.trim();

    if venv_name.is_empty() {
        None
    } else {
        Some(venv_name.to_string())
    }
}

/// Whether the venv is linked to `path` (or `path` parent) via
/// the venv project declaration.
fn is_tree_linked_venv(venv: &PythonEnvironment, path: &Path) -> bool {
    venv.project
        .as_ref()
        .is_some_and(|p| p == path || path.starts_with(p))
}

/// Whether the venv prefix is nested in path (e.g uv's .venv)
fn is_subtree_venv(venv: &PythonEnvironment, path: &Path) -> bool {
    venv.prefix.as_ref().is_some_and(|p| p.starts_with(path))
}

/// Whether the venv's name matches `venv_name`
fn is_named_venv(venv: &PythonEnvironment, venv_name: &str) -> bool {
    venv.name.as_ref().is_some_and(|n| n == venv_name)
}

/// Check if `venv` is linked to the given path somehow (either via path or name)
fn is_linked_venv(venv: &PythonEnvironment, path: &Path, path_venv_name: Option<&str>) -> bool {
    is_tree_linked_venv(venv, path)
        || is_subtree_venv(venv, path)
        || path_venv_name.is_some_and(|n| is_named_venv(venv, n))
}

/// Return venv prefix possibly specified in a `varname` environment variable
fn venv_prefix_in_os_env(varname: &str) -> Option<PathBuf> {
    std::env::var(varname)
        .ok()
        .filter(|pfx| !pfx.is_empty())
        .map(PathBuf::from)
}

/// Check if `venv` matches the prefix specified in the environment
/// via `VIRTUAL_ENV` (or `CONDA_PREFIX` for conda envs)
fn is_env_specified_venv(venv: &PythonEnvironment) -> bool {
    let conda_prefix = if venv.kind == Some(PythonEnvironmentKind::Conda) {
        venv_prefix_in_os_env("CONDA_PREFIX")
    } else {
        None
    };

    if let Some(prefix) = conda_prefix.or_else(|| venv_prefix_in_os_env("VIRTUAL_ENV")) {
        venv.prefix
            .as_ref()
            .is_some_and(|venv_pfx| venv_pfx == &prefix)
            || venv
                .executable
                .as_ref()
                .is_some_and(|venv_exe| venv_exe.starts_with(prefix))
    } else {
        false
    }
}

/// Sort environments by priority: path-linked > env-specified > kind priority > version
fn env_ordering(
    a: &(ToolchainEnvironment, Option<PythonEnvironmentKind>),
    b: &(ToolchainEnvironment, Option<PythonEnvironmentKind>),
) -> Ordering {
    b.0.is_path_linked
        .cmp(&a.0.is_path_linked)
        .then_with(|| b.0.is_env_specified.cmp(&a.0.is_env_specified))
        .then_with(|| env_priority(a.1).cmp(&env_priority(b.1)))
        .then_with(|| {
            let a_ver =
                a.0.version
                    .as_deref()
                    .and_then(|v| pep440_rs::Version::from_str(v).ok());
            let b_ver =
                b.0.version
                    .as_deref()
                    .and_then(|v| pep440_rs::Version::from_str(v).ok());
            match (a_ver, b_ver) {
                (Some(l), Some(r)) => r.cmp(&l),
                (Some(_), None) => Ordering::Less,
                (None, Some(_)) => Ordering::Greater,
                (None, None) => Ordering::Equal,
            }
        })
}

/// Detect virtual environments in the given workspace.
pub fn detect_virtual_environments(
    root: &Path,
    lookup_config: EnvironmentLookupConfig,
) -> Vec<ToolchainEnvironment> {
    let environment = EnvironmentApi::new(lookup_config);
    let locators = pet::locators::create_locators(
        Arc::new(pet_conda::Conda::from(&environment)),
        Arc::new(pet_poetry::Poetry::from(&environment)),
        &environment,
    );

    let root = canonicalize_path(root);
    debug!("looking for virtual environments in {root:?}");

    let config = Configuration {
        workspace_directories: Some(vec![root.clone()]),
        ..Configuration::default()
    };

    for locator in locators.iter() {
        locator.configure(&config);
    }

    let path_venv_name = get_path_venv_declaration(&root);
    let reporter = pet_reporter::collect::create_reporter();
    pet::find::find_and_report_envs(&reporter, config, &locators, &environment, None);

    let mut env_with_kinds: Vec<(ToolchainEnvironment, Option<PythonEnvironmentKind>)> = reporter
        .environments
        .lock()
        .as_deref()
        .map_or(Vec::new(), |envs| {
            envs.iter()
                .filter_map(|env| {
                    let is_path_linked = is_linked_venv(env, &root, path_venv_name.as_deref());
                    let is_env_specified = is_env_specified_venv(env);
                    let should_include = match env.kind {
                        Some(
                            PythonEnvironmentKind::Poetry
                            | PythonEnvironmentKind::Pipenv
                            | PythonEnvironmentKind::Venv
                            | PythonEnvironmentKind::VirtualEnv
                            | PythonEnvironmentKind::PyenvVirtualEnv
                            | PythonEnvironmentKind::VirtualEnvWrapper
                            | PythonEnvironmentKind::Conda,
                        ) => is_path_linked || is_env_specified,
                        _ => lookup_config.include_global,
                    };

                    if should_include {
                        let toolchain_env = ToolchainEnvironment {
                            executable: env.executable.clone(),
                            prefix: canonicalize_path_option(env.prefix.as_deref()),
                            name: env.name.clone(),
                            version: env.version.clone(),
                            project: canonicalize_path_option(env.project.as_deref()),
                            is_path_linked,
                            is_env_specified,
                        };
                        Some((toolchain_env, env.kind))
                    } else {
                        None
                    }
                })
                .collect()
        });

    env_with_kinds.sort_by(env_ordering);

    // Deduplicate by prefix path, keeping first (highest priority)
    let mut seen_paths = HashSet::new();
    env_with_kinds
        .into_iter()
        .map(|(env, _)| env)
        .filter(|env| {
            env.prefix
                .as_ref()
                .is_none_or(|prefix| seen_paths.insert(prefix.clone()))
        })
        .collect()
}
