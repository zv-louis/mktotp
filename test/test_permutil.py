# encoding: utf-8-sig

import os
import stat
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from mktotp.permutil import set_secure_permissions, check_file_permissions


class TestPermUtil:
    """Test class for permission utility functions"""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        yield Path(temp_path)
        
        # Cleanup
        if Path(temp_path).exists():
            Path(temp_path).unlink()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        
        # Cleanup
        import shutil
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-specific test")
    def test_set_secure_permissions_unix(self, temp_file):
        """Test setting secure permissions on Unix systems"""
        # Create the file first
        temp_file.touch()
        
        # Set permissions to something insecure first
        temp_file.chmod(0o777)
        
        # Call the function
        set_secure_permissions(temp_file)
        
        # Check that permissions are now secure (0o600)
        file_stat = temp_file.stat()
        assert file_stat.st_mode & 0o777 == 0o600

    @pytest.mark.skipif(os.name != 'nt', reason="Windows-specific test")
    @patch('subprocess.run')
    @patch('os.getlogin')
    def test_set_secure_permissions_windows_success(self, mock_getlogin, mock_subprocess_run, temp_file):
        """Test setting secure permissions on Windows systems (success case)"""
        mock_getlogin.return_value = "testuser"
        mock_subprocess_run.return_value = MagicMock()
        
        # Create the file first
        temp_file.touch()
        
        # Call the function
        set_secure_permissions(temp_file)
        
        # Verify that subprocess.run was called with correct arguments
        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args
        assert 'icacls' in call_args[0][0][0]
        assert str(temp_file) in call_args[0][0][1]

    @pytest.mark.skipif(os.name != 'nt', reason="Windows-specific test")
    @patch('subprocess.run')
    @patch('os.getlogin')
    @patch('mktotp.permutil.get_logger')
    def test_set_secure_permissions_windows_failure(self, mock_get_logger, mock_getlogin, mock_subprocess_run, temp_file):
        """Test setting secure permissions on Windows systems (failure case)"""
        mock_getlogin.return_value = "testuser"
        mock_subprocess_run.side_effect = Exception("Command failed")
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Create the file first
        temp_file.touch()
        
        # Call the function (should not raise exception)
        set_secure_permissions(temp_file)
        
        # Verify that warning was logged
        mock_logger.warning.assert_called()

    @patch('mktotp.permutil.get_logger')
    def test_set_secure_permissions_general_exception(self, mock_get_logger, temp_file):
        """Test general exception handling in set_secure_permissions"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Use a non-existent file to trigger an exception
        non_existent_file = Path("definitely_does_not_exist.txt")
        
        # Call the function (should not raise exception)
        set_secure_permissions(non_existent_file)
        
        # Verify that warning was logged
        mock_logger.warning.assert_called()

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-specific test")
    def test_check_file_permissions_unix_secure(self, temp_file):
        """Test checking secure file permissions on Unix systems"""
        # Create the file first
        temp_file.touch()
        
        # Set secure permissions
        temp_file.chmod(0o600)
        
        # Check permissions
        result = check_file_permissions(temp_file)
        assert result is True

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-specific test")
    def test_check_file_permissions_unix_insecure(self, temp_file):
        """Test checking insecure file permissions on Unix systems"""
        # Create the file first
        temp_file.touch()
        
        # Set insecure permissions (readable by group/others)
        temp_file.chmod(0o644)
        
        # Check permissions
        result = check_file_permissions(temp_file)
        assert result is False

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-specific test")
    def test_check_file_permissions_unix_various_permissions(self, temp_file):
        """Test checking various file permissions on Unix systems"""
        # Create the file first
        temp_file.touch()
        
        # Test different permission combinations
        test_cases = [
            (0o600, True),   # Secure: owner read/write only
            (0o400, True),   # Secure: owner read only
            (0o644, False),  # Insecure: group/others can read
            (0o666, False),  # Insecure: group/others can read/write
            (0o777, False),  # Insecure: everyone can read/write/execute
            (0o640, False),  # Insecure: group can read
            (0o604, False),  # Insecure: others can read
        ]
        
        for permission, expected_secure in test_cases:
            temp_file.chmod(permission)
            result = check_file_permissions(temp_file)
            assert result == expected_secure, f"Permission {oct(permission)} should be {'secure' if expected_secure else 'insecure'}"

    @pytest.mark.skipif(os.name != 'nt', reason="Windows-specific test")
    def test_check_file_permissions_windows(self, temp_file):
        """Test checking file permissions on Windows systems"""
        # Create the file first
        temp_file.touch()
        
        # On Windows, this function should always return True
        result = check_file_permissions(temp_file)
        assert result is True

    def test_check_file_permissions_nonexistent_file(self):
        """Test checking permissions of non-existent file"""
        non_existent_file = Path("definitely_does_not_exist.txt")
        
        # Should handle non-existent file gracefully
        result = check_file_permissions(non_existent_file)
        # The function behavior for non-existent files may vary,
        # but it should not raise an exception
        assert isinstance(result, bool)

    @patch('mktotp.permutil.get_logger')
    def test_permission_functions_logging(self, mock_get_logger, temp_file):
        """Test that permission functions log appropriately"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Create the file first
        temp_file.touch()
        
        # Test set_secure_permissions logging
        set_secure_permissions(temp_file)
        
        # Should have called debug logging
        mock_logger.debug.assert_called()

    def test_permissions_with_directory(self, temp_dir):
        """Test permission functions with directories"""
        # Test that functions work with directories too
        test_dir = temp_dir / "test_subdir"
        test_dir.mkdir()
        
        # Should not raise exceptions
        set_secure_permissions(test_dir)
        result = check_file_permissions(test_dir)
        assert isinstance(result, bool)

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-specific test")
    def test_secure_permissions_after_setting(self, temp_file):
        """Test that file is actually secure after setting permissions"""
        # Create the file first
        temp_file.touch()
        
        # Start with insecure permissions
        temp_file.chmod(0o777)
        assert check_file_permissions(temp_file) is False
        
        # Set secure permissions
        set_secure_permissions(temp_file)
        
        # Verify it's now secure
        assert check_file_permissions(temp_file) is True

    def test_path_handling(self, temp_file):
        """Test that functions handle Path objects correctly"""
        # Create the file first
        temp_file.touch()
        
        # Functions should accept Path objects
        set_secure_permissions(temp_file)
        result = check_file_permissions(temp_file)
        assert isinstance(result, bool)

    def test_symlink_handling(self, temp_file, temp_dir):
        """Test permission handling with symlinks"""
        # Create the target file
        temp_file.touch()
        
        # Create a symlink
        symlink_path = temp_dir / "test_symlink"
        try:
            symlink_path.symlink_to(temp_file)
            
            # Functions should handle symlinks without crashing
            set_secure_permissions(symlink_path)
            result = check_file_permissions(symlink_path)
            assert isinstance(result, bool)
            
        except (OSError, NotImplementedError):
            # Skip if symlinks are not supported on this platform
            pytest.skip("Symlinks not supported on this platform")
