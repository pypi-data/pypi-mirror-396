"""
Packaging utilities for PyInstaller environment detection and path handling.

This module provides functions to detect PyInstaller environment and
dynamically resolve paths for bundled resources and binaries.
"""

import sys
import os
from pathlib import Path
from typing import Optional


def is_pyinstaller_bundle() -> bool:
    """
    Check if the application is running in a PyInstaller bundle.
    
    Returns:
        bool: True if running in PyInstaller bundle, False otherwise.
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_bundle_dir() -> Path:
    """
    Get the directory where the PyInstaller bundle is located.
    
    Returns:
        Path: Bundle directory path in PyInstaller environment,
              or current working directory in development environment.
    """
    if is_pyinstaller_bundle():
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return Path(sys._MEIPASS)
    else:
        # Development environment - use current working directory
        return Path.cwd()


def get_executable_dir() -> Path:
    """
    Get the directory where the executable is located.
    
    Returns:
        Path: Directory containing the executable file.
    """
    if is_pyinstaller_bundle():
        # In PyInstaller bundle, sys.executable points to the bundled executable
        return Path(sys.executable).parent
    else:
        # Development environment - use current working directory
        return Path.cwd()


def get_mitmdump_path() -> str:
    """
    Get the path to mitmdump binary, handling both development and PyInstaller environments.

    Returns:
        str: Path to mitmdump binary.
    """
    if is_pyinstaller_bundle():
        # In PyInstaller bundle, mitmdump should be in the same directory as the executable
        bundle_dir = get_bundle_dir()
        mitmdump_path = bundle_dir / 'mitmdump'
        
        if mitmdump_path.exists():
            return str(mitmdump_path)
        else:
            # Fallback: try in the executable directory
            exec_dir = get_executable_dir()
            mitmdump_fallback = exec_dir / 'mitmdump'
            if mitmdump_fallback.exists():
                return str(mitmdump_fallback)
            else:
                # Last resort: use system mitmdump
                return 'mitmdump'
    else:
        # Development environment
        # First try the packaging_env/bin/mitmdump
        current_dir = Path.cwd()
        packaging_mitmdump = current_dir / 'packaging_env' / 'bin' / 'mitmdump'
        
        if packaging_mitmdump.exists():
            return str(packaging_mitmdump)
        else:
            # Fallback to system mitmdump
            return 'mitmdump'


def find_mitmdump_executable() -> str | None:
    """
    Enhanced mitmdump finder that checks multiple locations including Python package installations.
    
    Returns:
        str | None: Path to mitmdump executable if found, None otherwise.
    """
    import sys
    import subprocess
    import shutil
    
    # 1. Try the packaging utils function first
    try:
        mitmdump_path = get_mitmdump_path()
        if mitmdump_path != "mitmdump" and Path(mitmdump_path).exists():
            return mitmdump_path
    except Exception:
        pass
    
    # 2. Try system PATH
    system_mitmdump = shutil.which("mitmdump")
    if system_mitmdump:
        return system_mitmdump
    
    # 3. Try to find mitmdump in the same Python environment
    try:
        # Check if mitmproxy module is available
        import mitmproxy
        
        # Try to find mitmdump in the same directory as mitmproxy
        mitmproxy_dir = Path(mitmproxy.__file__).parent
        possible_paths = [
            mitmproxy_dir / "tools" / "mitmdump",
            mitmproxy_dir / "tools" / "mitmdump.py",
            mitmproxy_dir.parent / "bin" / "mitmdump",
            mitmproxy_dir.parent / "Scripts" / "mitmdump.exe",  # Windows
            mitmproxy_dir.parent / "Scripts" / "mitmdump",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
                
        # Try to run mitmdump as a Python module
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mitmproxy.tools.mitmdump", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return f"{sys.executable} -m mitmproxy.tools.mitmdump"
        except Exception:
            pass
            
    except ImportError:
        pass
    
    # 4. Try common installation locations
    common_paths = [
        Path(sys.executable).parent / "mitmdump",
        Path(sys.executable).parent / "mitmdump.exe",
        Path(sys.executable).parent / "Scripts" / "mitmdump.exe",
        Path(sys.executable).parent / "Scripts" / "mitmdump",
        Path("/usr/local/bin/mitmdump"),
        Path("/opt/homebrew/bin/mitmdump"),
    ]
    
    for path in common_paths:
        if path.exists():
            return str(path)
    
    return None


def get_resource_path(relative_path: str) -> Path:
    """
    Get the absolute path to a resource file, handling both development and PyInstaller environments.
    
    Args:
        relative_path (str): Relative path to the resource file.
        
    Returns:
        Path: Absolute path to the resource file.
    """
    if is_pyinstaller_bundle():
        # In PyInstaller bundle, resources are in the temp directory
        base_path = Path(sys._MEIPASS)
    else:
        # Development environment - relative to current working directory
        base_path = Path.cwd()
    
    return base_path / relative_path


def get_config_dir() -> Path:
    """
    Get the configuration directory for the application.
    
    Returns:
        Path: Configuration directory path.
    """
    if is_pyinstaller_bundle():
        # In bundled app, use user's home directory for config
        home_dir = Path.home()
        config_dir = home_dir / '.sensitive-check'
    else:
        # Development environment - use project directory
        config_dir = Path.cwd() / 'sensitive_check_local' / 'config'
    
    # Ensure config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir() -> Path:
    """
    Get the data directory for the application (logs, cache, etc.).
    
    Returns:
        Path: Data directory path.
    """
    if is_pyinstaller_bundle():
        # In bundled app, use user's home directory for data
        home_dir = Path.home()
        data_dir = home_dir / '.sensitive-check' / 'data'
    else:
        # Development environment - use project directory
        data_dir = Path.cwd() / 'data'
    
    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_log_dir() -> Path:
    """
    Get the log directory for the application.
    
    Returns:
        Path: Log directory path.
    """
    if is_pyinstaller_bundle():
        # In bundled app, use user's home directory for logs
        home_dir = Path.home()
        log_dir = home_dir / '.sensitive-check' / 'logs'
    else:
        # Development environment - use project directory
        log_dir = Path.cwd() / 'logs'
    
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_bundled_environment():
    """
    Setup environment variables and paths for bundled application.
    
    This function should be called early in the application startup
    when running in a PyInstaller bundle.
    """
    if not is_pyinstaller_bundle():
        return
    
    # Set up environment variables for bundled app
    bundle_dir = get_bundle_dir()
    
    # Add bundle directory to PATH so mitmdump can be found
    current_path = os.environ.get('PATH', '')
    if str(bundle_dir) not in current_path:
        os.environ['PATH'] = f"{bundle_dir}{os.pathsep}{current_path}"
    
    # Certificate management is now handled by cert_manager module
    # No longer set certificate path here as it will use persistent ~/.mitmproxy/


def print_environment_info():
    """
    Print environment information for debugging purposes.
    """
    print("=== Environment Information ===")
    print(f"PyInstaller Bundle: {is_pyinstaller_bundle()}")
    print(f"Bundle Directory: {get_bundle_dir()}")
    print(f"Executable Directory: {get_executable_dir()}")
    print(f"Mitmdump Path: {get_mitmdump_path()}")
    print(f"Config Directory: {get_config_dir()}")
    print(f"Data Directory: {get_data_dir()}")
    print(f"Log Directory: {get_log_dir()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {Path.cwd()}")
    if is_pyinstaller_bundle():
        print(f"PyInstaller _MEIPASS: {sys._MEIPASS}")
    print("==============================")


if __name__ == "__main__":
    # For testing purposes
    print_environment_info()