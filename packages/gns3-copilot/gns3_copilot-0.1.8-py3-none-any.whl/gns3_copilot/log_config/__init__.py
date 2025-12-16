"""
Log configuration package for GNS3 Copilot tools.

This package provides centralized logging configuration utilities
to eliminate duplicate logging setup code across modules.
"""

from .logging_config import (
    setup_logger,
    get_logger,
    configure_package_logging,
    setup_tool_logger,
    LOGGER_CONFIGS,
)

# Dynamic version management
try:
    from importlib.metadata import version
    __version__ = version("gns3-copilot")
except ImportError:
    # Fallback for Python < 3.8
    try:
        import pkg_resources
        __version__ = pkg_resources.get_distribution("gns3-copilot").version
    except Exception:
        __version__ = "unknown"
except Exception:
    __version__ = "unknown"

__author__ = "Guobin Yue"
__description__ = "AI-powered network automation assistant for GNS3"
__url__ = "https://github.com/yueguobin/gns3-copilot"

__all__ = [
    "setup_logger",
    "get_logger", 
    "configure_package_logging",
    "setup_tool_logger",
    "LOGGER_CONFIGS",
]
