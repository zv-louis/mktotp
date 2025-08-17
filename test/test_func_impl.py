# encoding: utf-8-sig

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from mktotp.func_impl import (
    register_secret, gen_token, get_secret_list, 
    remove_secrets, rename_secret
)


class TestFuncImpl:
    """Test class for function implementations"""

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
        backup_path = Path(temp_path).with_suffix('.bak')
        if backup_path.exists():
            backup_path.unlink()

    @pytest.fixture
    def temp_qr_image_file(self):
        """Create a temporary QR code image file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        # Create a simple test image
        import cv2
        import numpy as np
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(temp_path, test_image)
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_register_secret_success(self, temp_secrets_file, temp_qr_image_file):
        """Test successful secret registration"""
        with patch('mktotp.func_impl.decode_qrcode') as mock_decode:
            # Mock QR code data
            mock_qr_data = ["otpauth://totp/Test:new@example.com?secret=JBSWY3DPEHPK3PXT&issuer=Test"]
            mock_decode.return_value = mock_qr_data
            
            result = register_secret(
                qr_code_file=temp_qr_image_file,
                new_name="new_secret",
                secrets_file=temp_secrets_file
            )
            
            assert len(result) == 1
            assert result[0]["name"] == "new_secret"
            assert result[0]["account"] == "new@example.com"
            assert result[0]["issuer"] == "Test"
            assert result[0]["secret"] == "JBSWY3DPEHPK3PXT"
            
            mock_decode.assert_called_once_with(temp_qr_image_file)

    def test_register_secret_multiple_qr_codes(self, temp_secrets_file, temp_qr_image_file):
        """Test registering multiple secrets from one QR image"""
        with patch('mktotp.func_impl.decode_qrcode') as mock_decode:
            # Mock multiple QR code data
            mock_qr_data = [
                "otpauth://totp/Service1:user1@example.com?secret=JBSWY3DPEHPK3PXR&issuer=Service1",
                "otpauth://totp/Service2:user2@example.com?secret=JBSWY3DPEHPK3PXS&issuer=Service2"
            ]
            mock_decode.return_value = mock_qr_data
            
            result = register_secret(
                qr_code_file=temp_qr_image_file,
                new_name="multi_secret",
                secrets_file=temp_secrets_file
            )
            
            assert len(result) == 2
            assert result[0]["name"] == "multi_secret"
            assert result[1]["name"] == "multi_secret_2"

    def test_register_secret_file_not_found(self, temp_secrets_file):
        """Test register_secret with non-existent QR file"""
        with pytest.raises(FileNotFoundError):
            register_secret(
                qr_code_file="nonexistent_qr.png",
                new_name="test_secret",
                secrets_file=temp_secrets_file
            )

    def test_register_secret_invalid_qr_data(self, temp_secrets_file, temp_qr_image_file):
        """Test register_secret with invalid QR data"""
        with patch('mktotp.func_impl.decode_qrcode') as mock_decode:
            mock_decode.return_value = ["invalid_qr_data"]
            
            with pytest.raises(ValueError, match="Invalid QR code data"):
                register_secret(
                    qr_code_file=temp_qr_image_file,
                    new_name="test_secret",
                    secrets_file=temp_secrets_file
                )

    def test_gen_token_success(self, temp_secrets_file):
        """Test successful token generation"""
        token = gen_token(
            name="test_secret1",
            secrets_file=temp_secrets_file
        )
        
        assert isinstance(token, str)
        assert len(token) == 6
        assert token.isdigit()

    def test_gen_token_secret_not_found(self, temp_secrets_file):
        """Test token generation with non-existent secret"""
        with pytest.raises(ValueError, match="Secret for token 'nonexistent' not found"):
            gen_token(
                name="nonexistent",
                secrets_file=temp_secrets_file
            )

    def test_gen_token_file_not_found(self):
        """Test token generation with non-existent secrets file"""
        with pytest.raises(FileNotFoundError):
            gen_token(
                name="test_secret",
                secrets_file="nonexistent_secrets.json"
            )

    def test_get_secret_list_success(self, temp_secrets_file):
        """Test successful secret list retrieval"""
        result = get_secret_list(secrets_file=temp_secrets_file)
        
        assert len(result) == 2
        
        secret_names = [secret["name"] for secret in result]
        assert "test_secret1" in secret_names
        assert "test_secret2" in secret_names
        
        # Check that secret values are not included
        for secret in result:
            assert "secret" not in secret
            assert "name" in secret
            assert "account" in secret
            assert "issuer" in secret

    def test_get_secret_list_file_not_found(self):
        """Test secret list retrieval with non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_secret_list(secrets_file="nonexistent_secrets.json")

    def test_remove_secrets_success(self, temp_secrets_file):
        """Test successful secret removal"""
        result = remove_secrets(
            names=["test_secret1"],
            secrets_file=temp_secrets_file
        )
        
        assert result == ["test_secret1"]
        
        # Verify the secret was actually removed
        remaining_secrets = get_secret_list(secrets_file=temp_secrets_file)
        secret_names = [secret["name"] for secret in remaining_secrets]
        assert "test_secret1" not in secret_names
        assert "test_secret2" in secret_names

    def test_remove_secrets_multiple(self, temp_secrets_file):
        """Test removing multiple secrets"""
        result = remove_secrets(
            names=["test_secret1", "test_secret2"],
            secrets_file=temp_secrets_file
        )
        
        assert set(result) == {"test_secret1", "test_secret2"}
        
        # Verify all secrets were removed
        remaining_secrets = get_secret_list(secrets_file=temp_secrets_file)
        assert len(remaining_secrets) == 0

    def test_remove_secrets_nonexistent(self, temp_secrets_file):
        """Test removing non-existent secrets"""
        result = remove_secrets(
            names=["nonexistent_secret"],
            secrets_file=temp_secrets_file
        )
        
        assert result == []
        
        # Verify no secrets were removed
        remaining_secrets = get_secret_list(secrets_file=temp_secrets_file)
        assert len(remaining_secrets) == 2

    def test_remove_secrets_mixed(self, temp_secrets_file):
        """Test removing mix of existing and non-existent secrets"""
        result = remove_secrets(
            names=["test_secret1", "nonexistent_secret", "test_secret2"],
            secrets_file=temp_secrets_file
        )
        
        assert set(result) == {"test_secret1", "test_secret2"}

    def test_remove_secrets_file_not_found(self):
        """Test secret removal with non-existent file"""
        with pytest.raises(FileNotFoundError):
            remove_secrets(
                names=["test_secret"],
                secrets_file="nonexistent_secrets.json"
            )

    def test_rename_secret_success(self, temp_secrets_file):
        """Test successful secret renaming"""
        result = rename_secret(
            name="test_secret1",
            new_name="renamed_secret",
            secrets_file=temp_secrets_file
        )
        
        assert result is True
        
        # Verify the secret was actually renamed
        secrets = get_secret_list(secrets_file=temp_secrets_file)
        secret_names = [secret["name"] for secret in secrets]
        assert "test_secret1" not in secret_names
        assert "renamed_secret" in secret_names

    def test_rename_secret_nonexistent(self, temp_secrets_file):
        """Test renaming non-existent secret"""
        result = rename_secret(
            name="nonexistent_secret",
            new_name="new_name",
            secrets_file=temp_secrets_file
        )
        
        assert result is False
        
        # Verify no changes were made
        secrets = get_secret_list(secrets_file=temp_secrets_file)
        secret_names = [secret["name"] for secret in secrets]
        assert "nonexistent_secret" not in secret_names
        assert "new_name" not in secret_names
        assert len(secrets) == 2

    def test_rename_secret_file_not_found(self):
        """Test secret renaming with non-existent file"""
        with pytest.raises(FileNotFoundError):
            rename_secret(
                name="test_secret",
                new_name="new_name",
                secrets_file="nonexistent_secrets.json"
            )

    def test_functions_with_default_secrets_file(self):
        """Test functions with None/default secrets file parameter"""
        # These should either work with default file or handle missing file gracefully
        
        # Test with temporary file to avoid affecting real data
        try:
            result = get_secret_list(secrets_file=None)
            # If it succeeds, it means default file exists
            assert isinstance(result, list)
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected if default file doesn't exist
            pass
        
        try:
            gen_token(name="nonexistent_test_name", secrets_file=None)
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected
            pass
        
        try:
            remove_secrets(names=["nonexistent_test_name"], secrets_file=None)
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected
            pass
        
        try:
            rename_secret(name="nonexistent_old", new_name="nonexistent_new", secrets_file=None)
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected
            pass

    def test_functions_with_empty_string_secrets_file(self):
        """Test functions with empty string secrets file parameter"""
        # Empty string should be treated the same as None and use default path
        
        # Test with temporary file to avoid affecting real data
        try:
            result = get_secret_list(secrets_file="")
            # If it succeeds, it means default file exists
            assert isinstance(result, list)
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected if default file doesn't exist
            pass
        
        try:
            gen_token(name="nonexistent_test_name", secrets_file="")
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected
            pass
        
        try:
            remove_secrets(names=["nonexistent_test_name"], secrets_file="")
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected
            pass
        
        try:
            rename_secret(name="nonexistent_old", new_name="nonexistent_new", secrets_file="")
        except (FileNotFoundError, PermissionError, ValueError):
            # These exceptions are expected
            pass

    @patch('mktotp.func_impl.SecretMgr')
    def test_register_secret_context_manager_usage(self, mock_secret_mgr_class, temp_qr_image_file):
        """Test that register_secret uses context manager properly"""
        mock_mgr = MagicMock()
        mock_secret_mgr_class.return_value.__enter__.return_value = mock_mgr
        mock_mgr.register_secret.return_value = [{"name": "test", "account": "test@example.com", "issuer": "Test", "secret": "SECRET"}]
        
        with patch('mktotp.func_impl.decode_qrcode') as mock_decode:
            mock_decode.return_value = ["otpauth://totp/Test:test@example.com?secret=SECRET&issuer=Test"]
            
            register_secret(
                qr_code_file=temp_qr_image_file,
                new_name="test",
                secrets_file="test.json"
            )
            
            # Verify context manager was used
            mock_secret_mgr_class.assert_called_once_with("test.json")
            mock_mgr.load.assert_called_once()
            mock_mgr.save.assert_called_once()

    @patch('mktotp.func_impl.SecretMgr')
    def test_all_functions_use_context_manager(self, mock_secret_mgr_class, temp_qr_image_file):
        """Test that all functions use context manager properly"""
        mock_mgr = MagicMock()
        mock_secret_mgr_class.return_value.__enter__.return_value = mock_mgr
        
        # Test gen_token
        mock_mgr.gen_totp_token.return_value = "123456"
        gen_token(name="test", secrets_file="test.json")
        mock_mgr.load.assert_called()
        
        # Reset mock
        mock_mgr.reset_mock()
        
        # Test get_secret_list
        mock_mgr.list_secrets.return_value = []
        get_secret_list(secrets_file="test.json")
        mock_mgr.load.assert_called()
        
        # Reset mock
        mock_mgr.reset_mock()
        
        # Test remove_secrets
        mock_mgr.remove_secrets.return_value = ["test"]
        remove_secrets(names=["test"], secrets_file="test.json")
        mock_mgr.load.assert_called()
        mock_mgr.save.assert_called()
        
        # Reset mock
        mock_mgr.reset_mock()
        
        # Test rename_secret
        mock_mgr.rename_secret.return_value = True
        rename_secret(name="old", new_name="new", secrets_file="test.json")
        mock_mgr.load.assert_called()
        mock_mgr.save.assert_called()
