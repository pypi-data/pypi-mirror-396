#!/usr/bin/env python3
"""
GNS3 Copilot main entry point.

This module provides a command-line interface for launching the GNS3 Copilot
Streamlit application with support for Streamlit parameter passthrough.
"""

import argparse
import sys
import subprocess
from pathlib import Path

# Conditional imports at top level
try:
    import streamlit
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import gns3_copilot
    from gns3_copilot import __version__
    GNS3_COPILOT_AVAILABLE = True
except ImportError:
    gns3_copilot = None
    __version__ = "unknown"
    GNS3_COPILOT_AVAILABLE = False

def get_app_path():
    """Get the path to the app.py file."""
    # Try to find app.py in the current directory first
    current_dir = Path.cwd()
    app_path = current_dir / "app.py"

    if app_path.exists():
        return str(app_path)

    # If not found, try to find it relative to this script
    script_dir = Path(__file__).parent.parent
    app_path = script_dir / "app.py"

    if app_path.exists():
        return str(app_path)

    # As a last resort, try to find it in the package installation
    try:
        package_dir = Path(gns3_copilot.__file__).parent
        app_path = package_dir / "app.py"
        if app_path.exists():
            return str(app_path)
    except ImportError:
        pass

    return None


def check_streamlit():
    """Check if streamlit is available."""
    return STREAMLIT_AVAILABLE


def print_help():
    """Print help information."""
    help_text = """
GNS3 Copilot - AI-powered network automation assistant for GNS3

USAGE:
    gns3-copilot [STREAMLIT_OPTIONS]

EXAMPLES:
    # Basic startup
    gns3-copilot
    
    # Specify custom port
    gns3-copilot --server.port 8080
    
    # Specify address and port
    gns3-copilot --server.address 0.0.0.0 --server.port 8080
    
    # Run in headless mode
    gns3-copilot --server.headless true
    
    # Set log level
    gns3-copilot --logger.level debug
    
    # Disable usage statistics
    gns3-copilot --browser.gatherUsageStats false

COMMON STREAMLIT OPTIONS:
    --server.port PORT           Port to run on (default: 8501)
    --server.address ADDRESS     Address to bind to (default: localhost)
    --server.headless true/false Run in headless mode
    --logger.level LEVEL         Log level (error, warning, info, debug)
    --browser.gatherUsageStats true/false
                                Gather usage statistics
    --theme.base light/dark      Set base theme

For a complete list of Streamlit options, run:
    streamlit run --help

ALTERNATIVE USAGE:
    You can also run the app directly with streamlit:
    streamlit run app.py [STREAMLIT_OPTIONS]
"""
    print(help_text)


def print_version():
    """Print version information."""
    if GNS3_COPILOT_AVAILABLE:
        print(f"GNS3 Copilot version {__version__}")
    else:
        print("GNS3 Copilot version unknown")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="gns3-copilot",
        description="GNS3 Copilot - AI-powered network automation assistant for GNS3",
        add_help=False  # We'll handle help ourselves to allow unknown args
    )

    # Add our custom arguments
    parser.add_argument(
        "--help", "-h", action="store_true", help="Show this help message and exit")
    parser.add_argument(
        "--version", "-v", action="store_true", help="Show version information and exit")

    # Parse known args, leaving unknown args for streamlit
    args, unknown_args = parser.parse_known_args()

    # Handle our custom arguments
    if args.help:
        print_help()
        return 0

    if args.version:
        print_version()
        return 0

    # Check if streamlit is available
    if not check_streamlit():
        print("Error: Streamlit is not installed. Please install it with:")
        print("  pip install streamlit")
        return 1

    # Find the app.py file
    app_path = get_app_path()
    if not app_path:
        print("Error: Could not find app.py file.")
        print(
            "Please ensure you're running this from the project directory "
            "or that the package is properly installed."
            )
        return 1

    # Build the streamlit command
    cmd = ["streamlit", "run", app_path] + unknown_args

    # Print startup information
    print("Starting GNS3 Copilot...")
    print(f"App file: {app_path}")
    if unknown_args:
        print(f"Additional arguments: {' '.join(unknown_args)}")
    print()

    exit_code = 0
    try:
        # Run streamlit
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        exit_code = 1
    except KeyboardInterrupt:
        print("\nGNS3 Copilot stopped by user.")
        exit_code = 0
    except FileNotFoundError:
        print(
            "Error: 'streamlit' command not found. "
            "Please ensure Streamlit is installed and in your PATH."
            )
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
