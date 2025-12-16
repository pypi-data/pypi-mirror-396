"""
GNS3 Client Package

This package provides a Python interface for interacting with GNS3 servers.
It's adapted from the upstream gns3fy project with modifications for compatibility
with langchain and reduced dependency conflicts.

Main classes:
- Gns3Connector: Connector for GNS3 server API interaction
- Project: GNS3 Project management
- Node: GNS3 Node management  
- Link: GNS3 Link management
- GNS3TopologyTool: GNS3 topology reading tool
"""

from .custom_gns3fy import (
    Gns3Connector,
    Project,
    Node,
    Link,
    NODE_TYPES,
    CONSOLE_TYPES,
    LINK_TYPES,
)
from .gns3_topology_reader import GNS3TopologyTool

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
    "Gns3Connector",
    "Project", 
    "Node",
    "Link",
    "NODE_TYPES",
    "CONSOLE_TYPES", 
    "LINK_TYPES",
    "GNS3TopologyTool",
]
