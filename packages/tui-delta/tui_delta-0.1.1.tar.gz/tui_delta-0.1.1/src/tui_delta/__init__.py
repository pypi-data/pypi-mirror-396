"""tui_delta - Run TUI applications with real-time delta processing."""

# Version is managed by hatch-vcs and set during build
try:
    from ._version import __version__
except ImportError:
    # Fallback for development installs without build
    __version__ = "0.0.0.dev0+unknown"

from .clear_rules import ClearRules
from .run import run_tui_with_pipeline

__all__ = [
    "__version__",
    "ClearRules",
    "run_tui_with_pipeline",
]
