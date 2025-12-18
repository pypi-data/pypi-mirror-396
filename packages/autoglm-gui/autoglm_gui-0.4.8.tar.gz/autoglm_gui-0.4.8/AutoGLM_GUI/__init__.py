"""AutoGLM-GUI package metadata."""

from importlib import metadata

# Expose package version at runtime; fall back to "unknown" during editable/dev runs
try:
    __version__ = metadata.version("autoglm-gui")
except metadata.PackageNotFoundError:
    __version__ = "unknown"
