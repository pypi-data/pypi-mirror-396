"""
GNS3 Copilot - AI-powered network automation assistant for GNS3.

This package provides a command-line interface for launching the GNS3 Copilot
Streamlit application with support for Streamlit parameter passthrough.
"""

# Dynamic version management
try:
    from importlib.metadata import version
    __version__ = version("gns3-copilot")
except ImportError:
    # Fallback for Python < 3.8
    try:
        import pkg_resources
        __version__ = pkg_resources.get_distribution("gns3-copilot")
    except Exception:
        __version__ = "unknown"
except Exception:
    __version__ = "unknown"

__author__ = "Guobin Yue"
__description__ = "AI-powered network automation assistant for GNS3"
__url__ = "https://github.com/yueguobin/gns3-copilot"
