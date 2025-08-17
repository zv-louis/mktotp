# encoding: utf-8-sig

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from mktotp.secrets import SecretMgr


# ----------------------------------------------------------------------------
class TestSecretMgr:
    """Test class for SecretMgr functionality"""

    # ----------------------------------------------------------------------------
    @pytest.fixture
    def temp_secrets_file(self):
        """Create a temporary secrets file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            test_data = {
                "secrets": [
                    {
                        "name": "test_secret1",
                        "account": "test@example.com",
                        "issuer": "TestIssuer1",
                        "secret": "JBSWY3DPEHPK3PXP"
                    },
                    {
                        "name": "test_secret2",
                        "account": "user@test.com",
                        "issuer": "TestIssuer2", 
                        "secret": "JBSWY3DPEHPK3PXQ"
                    }
                ],
                "version": "1.0",
                "last_update": "2025-01-01T00:00:00.000000+00:00"
            }
            json.dump(test_data, f, indent=4, ensure_ascii=False)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        # Also clean up backup file if it exists
        backup_path = Path(temp_path).with_suffix('.bak')
        if backup_path.exists():
            backup_path.unlink()

    # ----------------------------------------------------------------------------
    @pytest.fixture
    def empty_temp_file(self):
        """Create an empty temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    # ----------------------------------------------------------------------------
    def test_init_with_custom_path(self, temp_secrets_file):
        """Test SecretMgr initialization with custom path"""
        mgr = SecretMgr(temp_secrets_file)
        assert mgr.secrets_file == Path(temp_secrets_file)
        assert mgr.secret_data == {}

    # ----------------------------------------------------------------------------
    def test_init_with_empty_string_path(self):
        """Test SecretMgr initialization with empty string path uses default"""
        mgr = SecretMgr("")
        # Should use default path
        expected_default = Path(os.path.expanduser("~")) / ".mktotp" / "data" / "secrets.json"
        assert mgr.secrets_file == expected_default
        assert mgr.secret_data == {}

    # ----------------------------------------------------------------------------
    def test_init_with_none_path(self):
        """Test SecretMgr initialization with None path uses default"""
        mgr = SecretMgr(None)
        # Should use default path
        expected_default = Path(os.path.expanduser("~")) / ".mktotp" / "data" / "secrets.json"
        assert mgr.secrets_file == expected_default
        assert mgr.secret_data == {}

    # ----------------------------------------------------------------------------
    def test_load_secrets_success(self, temp_secrets_file):
        """Test successful loading of secrets from file"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        assert len(mgr.secret_data) == 2
        assert "test_secret1" in mgr.secret_data
        assert "test_secret2" in mgr.secret_data
        
        secret1 = mgr.secret_data["test_secret1"]
        assert secret1["account"] == "test@example.com"
        assert secret1["issuer"] == "TestIssuer1"
        assert secret1["secret"] == "JBSWY3DPEHPK3PXP"

    # ----------------------------------------------------------------------------
    def test_load_file_not_found(self, empty_temp_file):
        """Test loading when file doesn't exist"""
        # Use a path that definitely doesn't exist
        nonexistent_path = str(Path(empty_temp_file).parent / "definitely_nonexistent_file.json")
        mgr = SecretMgr(nonexistent_path)
        with pytest.raises(FileNotFoundError):
            mgr.load()

    # ----------------------------------------------------------------------------
    def test_load_invalid_json(self, empty_temp_file):
        """Test loading with invalid JSON content"""
        # Write invalid JSON to the file
        with open(empty_temp_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        mgr = SecretMgr(empty_temp_file)
        with pytest.raises(json.JSONDecodeError):
            mgr.load()

    # ----------------------------------------------------------------------------
    def test_load_invalid_data_format(self, empty_temp_file):
        """Test loading with invalid data format (not a dict)"""
        # Write invalid data format to the file
        with open(empty_temp_file, 'w', encoding='utf-8') as f:
            json.dump(["not", "a", "dict"], f)
        
        mgr = SecretMgr(empty_temp_file)
        with pytest.raises(ValueError, match="Invalid data format in secrets file"):
            mgr.load()
    # ----------------------------------------------------------------------------
    def test_get_secret_existing(self, temp_secrets_file):
        """Test getting an existing secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        secret = mgr.get_secret("test_secret1")
        assert secret == "JBSWY3DPEHPK3PXP"
    # ----------------------------------------------------------------------------
    def test_get_secret_nonexistent(self, temp_secrets_file):
        """Test getting a non-existent secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        secret = mgr.get_secret("nonexistent_secret")
        assert secret is None
    # ----------------------------------------------------------------------------
    def test_gen_totp_token_success(self, temp_secrets_file):
        """Test generating TOTP token for existing secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        token = mgr.gen_totp_token("test_secret1")
        # TOTP token should be 6 digits
        assert isinstance(token, str)
        assert len(token) == 6
        assert token.isdigit()
    # ----------------------------------------------------------------------------
    def test_gen_totp_token_nonexistent(self, temp_secrets_file):
        """Test generating TOTP token for non-existent secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        with pytest.raises(ValueError, match="Secret for token 'nonexistent' not found"):
            mgr.gen_totp_token("nonexistent")
    # ----------------------------------------------------------------------------
    def test_register_secret_success(self, temp_secrets_file):
        """Test registering a new secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        # Sample TOTP URI (this is a test URI, not a real secret)
        qr_data = "otpauth://totp/Test%20Service:testuser@example.com?secret=JBSWY3DPEHPK3PXR&issuer=Test%20Service"
        
        result = mgr.register_secret("new_secret", [qr_data])
        
        assert len(result) == 1
        assert result[0]["name"] == "new_secret"
        assert result[0]["account"] == "testuser@example.com"
        assert result[0]["issuer"] == "Test Service"
        assert result[0]["secret"] == "JBSWY3DPEHPK3PXR"
        
        # Check that it was added to secret_data
        assert "new_secret" in mgr.secret_data

    # ----------------------------------------------------------------------------
    def test_register_multiple_secrets(self, temp_secrets_file):
        """Test registering multiple secrets with same name"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        qr_data1 = "otpauth://totp/Service1:user1@example.com?secret=JBSWY3DPEHPK3PXR&issuer=Service1"
        qr_data2 = "otpauth://totp/Service2:user2@example.com?secret=JBSWY3DPEHPK3PXS&issuer=Service2"
        
        result = mgr.register_secret("multi_secret", [qr_data1, qr_data2])
        
        assert len(result) == 2
        assert result[0]["name"] == "multi_secret"
        assert result[1]["name"] == "multi_secret_2"
        
        # Check that both were added to secret_data
        assert "multi_secret" in mgr.secret_data
        assert "multi_secret_2" in mgr.secret_data

    # ----------------------------------------------------------------------------
    def test_register_secret_invalid_qr(self, temp_secrets_file):
        """Test registering with invalid QR code data"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        invalid_qr_data = "invalid_qr_code_data"
        
        with pytest.raises(ValueError, match="Invalid QR code data"):
            mgr.register_secret("invalid_secret", [invalid_qr_data])

    # ----------------------------------------------------------------------------
    def test_save_secrets(self, temp_secrets_file):
        """Test saving secrets to file"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        # Add a new secret
        qr_data = "otpauth://totp/Test:new@example.com?secret=JBSWY3DPEHPK3PXT&issuer=Test"
        mgr.register_secret("save_test", [qr_data])
        
        # Save and reload
        mgr.save()
        
        # Create new manager and load to verify save worked
        mgr2 = SecretMgr(temp_secrets_file)
        mgr2.load()
        
        assert "save_test" in mgr2.secret_data
        assert mgr2.secret_data["save_test"]["account"] == "new@example.com"

    # ----------------------------------------------------------------------------
    def test_remove_secrets_success(self, temp_secrets_file):
        """Test removing an existing secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        result = mgr.remove_secrets(["test_secret1"])
        
        assert result == ["test_secret1"]
        assert "test_secret1" not in mgr.secret_data
        assert "test_secret2" in mgr.secret_data  # Other secret should remain

    # ----------------------------------------------------------------------------
    def test_remove_secrets_multiple(self, temp_secrets_file):
        """Test removing multiple existing secrets"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        result = mgr.remove_secrets(["test_secret1", "test_secret2"])
        
        assert set(result) == {"test_secret1", "test_secret2"}
        assert "test_secret1" not in mgr.secret_data
        assert "test_secret2" not in mgr.secret_data
        assert len(mgr.secret_data) == 0

    # ----------------------------------------------------------------------------
    def test_remove_secrets_nonexistent(self, temp_secrets_file):
        """Test removing a non-existent secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        result = mgr.remove_secrets(["nonexistent_secret"])
        
        assert result == []
        assert len(mgr.secret_data) == 2  # Original secrets should remain

    # ----------------------------------------------------------------------------
    def test_remove_secrets_mixed(self, temp_secrets_file):
        """Test removing a mix of existing and non-existent secrets"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        result = mgr.remove_secrets(["test_secret1", "nonexistent_secret", "test_secret2"])
        
        assert set(result) == {"test_secret1", "test_secret2"}
        assert "test_secret1" not in mgr.secret_data
        assert "test_secret2" not in mgr.secret_data
        assert len(mgr.secret_data) == 0

    # ----------------------------------------------------------------------------
    def test_rename_secret_success(self, temp_secrets_file):
        """Test renaming an existing secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        result = mgr.rename_secret("test_secret1", "renamed_secret")
        
        assert result is True
        assert "test_secret1" not in mgr.secret_data
        assert "renamed_secret" in mgr.secret_data
        assert mgr.secret_data["renamed_secret"]["name"] == "renamed_secret"
        assert mgr.secret_data["renamed_secret"]["account"] == "test@example.com"

    # ----------------------------------------------------------------------------
    def test_rename_secret_nonexistent(self, temp_secrets_file):
        """Test renaming a non-existent secret"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        result = mgr.rename_secret("nonexistent_secret", "new_name")
        
        assert result is False
        assert "nonexistent_secret" not in mgr.secret_data
        assert "new_name" not in mgr.secret_data

    # ----------------------------------------------------------------------------
    def test_list_secrets(self, temp_secrets_file):
        """Test listing all secrets"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        secrets_list = mgr.list_secrets()
        
        assert len(secrets_list) == 2
        secret_names = [secret["name"] for secret in secrets_list]
        assert "test_secret1" in secret_names
        assert "test_secret2" in secret_names

    # ----------------------------------------------------------------------------
    def test_list_secrets_empty(self, empty_temp_file):
        """Test listing secrets when no secrets exist"""
        # Create an empty secrets file structure
        with open(empty_temp_file, 'w', encoding='utf-8') as f:
            json.dump({"secrets": [], "version": "1.0"}, f)
        
        mgr = SecretMgr(empty_temp_file)
        mgr.load()
        secrets_list = mgr.list_secrets()
        assert secrets_list == []

    # ----------------------------------------------------------------------------
    def test_str_representation(self, temp_secrets_file):
        """Test string representation of SecretMgr"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        str_repr = str(mgr)
        assert isinstance(str_repr, str)
        assert "test_secret1" in str_repr
        assert "test_secret2" in str_repr

    # ----------------------------------------------------------------------------
    def test_repr_representation(self, temp_secrets_file):
        """Test repr representation of SecretMgr"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        repr_str = repr(mgr)
        assert isinstance(repr_str, str)
        assert "test_secret1" in repr_str
        assert "test_secret2" in repr_str

    # ----------------------------------------------------------------------------
    @patch('mktotp.secrets.get_logger')
    def test_load_with_permission_error(self, mock_get_logger, temp_secrets_file):
        """Test loading with permission error"""
        # Make file unreadable (on Windows, this might not work as expected)
        # So we'll mock the open function instead
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mgr = SecretMgr(temp_secrets_file)
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                mgr.load()
        
        mock_logger.error.assert_called()

    # ----------------------------------------------------------------------------
    def test_save_creates_backup(self, temp_secrets_file):
        """Test that save creates a backup of existing file"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        # Save to create backup
        mgr.save()
        
        backup_path = Path(temp_secrets_file).with_suffix('.bak')
        assert backup_path.exists()
        
        # Cleanup
        if backup_path.exists():
            backup_path.unlink()

    # ----------------------------------------------------------------------------
    def test_file_permissions(self, temp_secrets_file):
        """Test that saved files have appropriate permissions"""
        mgr = SecretMgr(temp_secrets_file)
        mgr.load()
        
        # Add a secret and save
        qr_data = "otpauth://totp/Test:perm@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test"
        mgr.register_secret("perm_test", [qr_data])
        mgr.save()
        
        # Check that file exists and is readable by the current user
        assert Path(temp_secrets_file).exists()
        assert Path(temp_secrets_file).is_file()
        
        # On Unix-like systems, check specific permissions
        if os.name != 'nt':
            import stat
            file_stat = os.stat(temp_secrets_file)
            # Check that group and others don't have read/write permissions
            assert not (file_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)), \
                "File should not be readable/writable by group or others"

    # ----------------------------------------------------------------------------
    def test_directory_permissions(self):
        """Test that created directories have appropriate permissions"""
        import tempfile
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            test_secrets_path = Path(temp_dir) / "test_mktotp" / "data" / "secrets.json"
            
            mgr = SecretMgr(test_secrets_path)
            
            # Add a secret and save (this should create the directory)
            qr_data = "otpauth://totp/Test:dir@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test"
            mgr.register_secret("dir_test", [qr_data])
            mgr.save()
            
            # Check that directory was created
            assert test_secrets_path.parent.exists()
            assert test_secrets_path.parent.is_dir()
            
            # On Unix-like systems, check specific permissions
            if os.name != 'nt':
                import stat
                dir_stat = os.stat(test_secrets_path.parent)
                # Check that group and others don't have access
                assert not (dir_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | 
                                              stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)), \
                    "Directory should not be accessible by group or others"
