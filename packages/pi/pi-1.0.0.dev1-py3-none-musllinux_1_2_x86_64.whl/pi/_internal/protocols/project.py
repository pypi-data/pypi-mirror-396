from typing import Protocol
from dataclasses import dataclass
from pathlib import Path
import enum

from pi._internal import rpc
from pi._internal import bus as _bus


class ToolType(enum.StrEnum):
    """Types of tools"""

    Manager = "Manager"
    Backend = "Backend"
    Environment = "Environment"
    Diagnostic = "Diagnostic"
    Formatter = "Formatter"
    Testing = "Testing"
    Documentation = "Documentation"


@dataclass(frozen=True, kw_only=True)
class DetectedTool:
    """Detected Python packaging tool"""

    tool_type: ToolType
    """Type of tool"""

    name: str
    """Name of the tool"""

    confidence: float
    """Confidence score (0.0 to 1.0)"""

    evidence: list[str]
    """Evidence that led to this detection"""


@dataclass(frozen=True, kw_only=True)
class Dependency:
    """A dependency of a package"""

    name: str
    """Name of the dependency"""

    version_constraint: str | None
    """Version constraint (e.g., ">=1.0.0", "^2.1.0", "~=3.9.0")"""

    url: str | None
    """URL for URL-based dependencies (e.g., Git repos, direct URLs)

    For Python: Git URLs, HTTP URLs, or file:// URLs as per PEP 508
    For Rust: Git URLs, path dependencies, or registry URLs
    When present, `version_constraint` should be None
    """

    optional: list[str]
    """Features/extras that enable this dependency

    For Python: extra names from optional-dependencies
    (e.g., `["dev", "test"]`). For Rust: feature names
    that enable this optional dependency (e.g., `["serde"]`)
    Empty list means this is a required dependency
    """

    group: str | None
    """Dependency group/category (e.g., "dev", "test", "optional", "build")"""

    environment_markers: str | None
    """Environment markers for conditional dependencies

    For Python: PEP 508 markers like '`python_version` >= "3.9"'
    For Rust: cfg conditions like '`target_os` = "windows"'
    """

    source: str
    """Source where this dependency was found
    (e.g., "pyproject.toml", "Cargo.toml")"""

    features: list[str]
    """Features/extras enabled for this dependency

    For Python: extra names requested for this dependency (e.g., `["standard"]`
    for fastapi[standard])
    For Rust: feature names enabled for this dependency (e.g., `["serde"]`)
    Empty vector means no specific features/extras are requested
    """


@dataclass(frozen=True, kw_only=True)
class Package:
    """Information about a package within a workspace"""

    name: str
    """Name of the package"""

    path: Path
    """Path to the package root directory"""

    tools: list[DetectedTool]
    """Tools detected specifically for this package"""

    dependencies: list[Dependency]
    """Dependencies declared by this package"""


@dataclass(frozen=True, kw_only=True)
class Workspace:
    """Information about a detected workspace"""

    root: Path
    """Root directory of the workspace"""

    members: list[Package]
    """Workspace member packages"""


class ToolchainType(enum.StrEnum):
    """Toolchain types"""

    Python = "Python"
    Rust = "Rust"


@dataclass(frozen=True, kw_only=True)
class ToolchainEnvironment:
    """Detected toolchain environment (e.g Python venv)"""

    executable: Path | None
    """Path to the main toolchain executable"""

    prefix: Path | None
    """Toolchain root directory"""

    name: str | None
    """Toolchain name (if available)"""

    version: str | None
    """Toolchain version (if detected)"""

    project: Path | None
    """Project directory associated with this toolchain"""

    is_path_linked: bool
    """Whether the environment is local to a path"""

    is_env_specified: bool
    """Whether the environment is specified in the OS environment variable"""


@dataclass(frozen=True, kw_only=True)
class Project:
    """A detected project"""

    name: str | None
    """Project name

    For Python projects: extracted from `name` in pyproject.toml [project]
    section For Rust projects: extracted from `name` in Cargo.toml [package]
    section, or workspace name if this is a workspace root
    """

    description: str | None
    """Project description

    For Python projects: extracted from `description` in pyproject.toml
    [project] section For Rust projects: extracted from `description` in
    Cargo.toml [package] section, or workspace description if this is a
    workspace root """

    toolchain_type: ToolchainType
    """Toolchain type, most often the primary language"""

    tools: list[DetectedTool]
    """All detected tools, sorted by confidence (highest first)"""

    toolchain_envs: list[ToolchainEnvironment]
    """Detected toolchains (e.g Python venvs)"""

    workspace: Workspace
    """Workspace information (always present, contains project root)"""

    toolchain_version_constraint: str | None
    """Toolchain version constraint from project configuration

    For Python projects: extracted from `requires-python` in pyproject.toml
    For Rust projects: extracted from `rust-version` in Cargo.toml,
    or falls back to version from `rust-toolchain.toml`/`rust-toolchain` if
    not present.

    Examples:
    - Python: ">=3.9", "^3.10"
    - Rust: "1.70", "1.75.0", "stable"
    """


@rpc.export
class ProjectInfo(Protocol):
    async def project_info(
        self, *, dir: str | None = None
    ) -> list[Project]: ...


def interface(bus: _bus.Bus) -> ProjectInfo:
    return rpc.get_interface(ProjectInfo, bus, "shell")  # type: ignore [type-abstract]
