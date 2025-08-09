# encoding: utf-8-sig

import os
import stat
import subprocess
from pathlib import Path
from .logutil import get_logger

# ----------------------------------------------------------------------------
def set_secure_permissions(file_path: Path) -> None:
    """
    Set secure permissions on a file (owner-only access).
    Works on both Unix-like systems and Windows.
    On Windows, it uses icacls to set permissions.
    
    Args:
        file_path (Path): The path to the file for which to set permissions.
    
    Raises:
        Exception: If setting permissions fails, a warning is logged.
    
    Note:
        On Windows, this function attempts to remove inheritance and grant full control
        only to the current user. It does not set Unix-style permissions.
        On Unix-like systems, it sets permissions to 600 (read/write for owner only).
    """
    try:
        if os.name == 'nt':  # Windows
            # On Windows, we can't easily set Unix-style permissions
            # but we can try to make the file less accessible
            try:
                # Remove inheritance and grant full control only to current user
                subprocess.run([
                    'icacls', str(file_path), '/inheritance:r', '/grant:r', 
                    f'{os.getlogin()}:F'
                ], check=True, capture_output=True)
                get_logger().debug(f"Set Windows permissions on {file_path}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # If icacls fails, just log a warning
                get_logger().warning(f"Could not set secure permissions on {file_path}")
        else:  # Unix-like systems
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
            get_logger().debug(f"Set Unix permissions (600) on {file_path}")
    except Exception as e:
        get_logger().warning(f"Could not set secure permissions on {file_path}: {e}")

def check_file_permissions(file_path: Path) -> bool:
    """
    Check if file has secure permissions.
    Returns True if permissions are acceptable, False otherwise.
    
    Args:
        file_path (Path): The path to the file to check permissions for.
    
    Returns:
        bool: True if permissions are secure, False if not.
    
    Note:
        On Windows, this function cannot check Unix-style permissions,
        so it will always return True but log a warning.
        On Unix-like systems, it checks if the file is readable/writable by group or others.
        If the file does not exist, it returns True (no problem).
    """
    try:
        if not file_path.exists():
            return True  # File doesn't exist, no problem

        if os.name == 'nt':  # Windows
            # On Windows, we can't easily check Unix-style permissions
            # Just warn the user
            get_logger().info(f"Please ensure {file_path} is only accessible by you")
            return True
        else:  # Unix-like systems
            file_stat = file_path.stat()
            # Check if file is readable/writable by group or others
            if file_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
                return False
            return True
    except Exception as e:
        get_logger().warning(f"Could not check permissions on {file_path}: {e}")
        return True  # Assume it's okay if we can't check
