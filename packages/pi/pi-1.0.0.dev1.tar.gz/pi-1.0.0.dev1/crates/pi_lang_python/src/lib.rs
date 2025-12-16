//! Python packaging detection library
//!
//! This crate provides functionality to detect Python packaging solutions
//! in arbitrary directories by analyzing lockfiles, configuration files,
//! and other packaging artifacts.

#![warn(clippy::pedantic)]

mod cli;
mod dependencies;
mod detection;
mod devtools;
mod lockfiles;
mod pyproject;
mod util;
mod venvs;

pub use cli::{ExecutionMode, PythonInvocation, process_python_invocation};
pub use detection::detect_python_projects;
pub use detection::find_possible_project_root;
pub use venvs::EnvironmentLookupConfig;
pub use venvs::detect_virtual_environments;
