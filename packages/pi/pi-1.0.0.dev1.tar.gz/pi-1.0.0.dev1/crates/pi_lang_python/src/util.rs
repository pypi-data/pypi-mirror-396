use std::path::{Path, PathBuf};

/// Utility function to safely canonicalize a path, falling back to the
/// original if canonicalization fails
pub(crate) fn canonicalize_path<P: AsRef<Path>>(path: P) -> PathBuf {
    path.as_ref()
        .canonicalize()
        .unwrap_or_else(|_| path.as_ref().to_path_buf())
}

/// Canonicalize an optional `Path`, returning None if the original was None.
pub(crate) fn canonicalize_path_option(path: Option<&Path>) -> Option<PathBuf> {
    path.map(canonicalize_path)
}
