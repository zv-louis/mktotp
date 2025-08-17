# encoding: utf-8-sig

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import asyncio

from mktotp.mcp_impl import (
    mktotp_register_secret_impl,
    mktotp_generate_token_impl,
    mktotp_get_secret_info_list_impl,
    mktotp_remove_secrets_impl,
    mktotp_rename_secret_impl,
    handle_operation,
    validate_file_path,
    validate_secret_name
)


class TestMCPImpl:
    """Test class for MCP implementation functions"""

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
        import os
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def temp_secrets_file(self):
        """Create a temporary secrets file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            import json
            test_data = {
                "secrets": [
                    {
                        "name": "test_secret1",
                        "account": "test@example.com",
                        "issuer": "TestIssuer1",
                        "secret": "JBSWY3DPEHPK3PXP"
                    }
                ],
                "version": "1.0",
                "last_update": "2025-01-01T00:00:00.000000+00:00"
            }
            json.dump(test_data, f, indent=4, ensure_ascii=False)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        import os
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    # Test validate_file_path function
    def test_validate_file_path_required_missing(self):
        """Test validate_file_path with missing required file"""
        with pytest.raises(ValueError, match="File path is required"):
            validate_file_path(None, "test_operation", required=True)

    def test_validate_file_path_required_nonexistent(self):
        """Test validate_file_path with non-existent required file"""
        with pytest.raises(FileNotFoundError, match="File not found for test_operation"):
            validate_file_path("nonexistent_file.json", "test_operation", required=True)

    def test_validate_file_path_parent_not_exists(self):
        """Test validate_file_path with non-existent parent directory"""
        with pytest.raises(FileNotFoundError, match="Parent directory not found"):
            validate_file_path("/nonexistent/path/file.json", "test_operation", required=False)

    def test_validate_file_path_optional_none(self):
        """Test validate_file_path with optional None file"""
        # Should not raise exception
        validate_file_path(None, "test_operation", required=False)

    def test_validate_file_path_existing_file(self, temp_secrets_file):
        """Test validate_file_path with existing file"""
        # Should not raise exception
        validate_file_path(temp_secrets_file, "test_operation", required=True)

    # Test validate_secret_name function
    def test_validate_secret_name_empty(self):
        """Test validate_secret_name with empty name"""
        with pytest.raises(ValueError, match="Secret name cannot be empty"):
            validate_secret_name("", "test_operation")
        
        with pytest.raises(ValueError, match="Secret name cannot be empty"):
            validate_secret_name("   ", "test_operation")

    def test_validate_secret_name_too_long(self):
        """Test validate_secret_name with too long name"""
        long_name = "a" * 101
        with pytest.raises(ValueError, match="Secret name too long"):
            validate_secret_name(long_name, "test_operation")

    def test_validate_secret_name_valid(self):
        """Test validate_secret_name with valid name"""
        # Should not raise exception
        validate_secret_name("valid_name", "test_operation")
        validate_secret_name("a" * 100, "test_operation")  # Exactly 100 chars

    # Test handle_operation function
    @pytest.mark.asyncio
    async def test_handle_operation_success(self):
        """Test handle_operation with successful function"""
        def test_func(arg1, arg2):
            return f"result: {arg1} + {arg2}"
        
        result = await handle_operation("test_op", test_func, arg1="hello", arg2="world")
        assert result == "result: hello + world"

    @pytest.mark.asyncio
    async def test_handle_operation_file_not_found(self):
        """Test handle_operation with FileNotFoundError"""
        def test_func():
            raise FileNotFoundError("Test file not found")
        
        with pytest.raises(ValueError, match="File not found in test_op"):
            await handle_operation("test_op", test_func)

    @pytest.mark.asyncio
    async def test_handle_operation_permission_error(self):
        """Test handle_operation with PermissionError"""
        def test_func():
            raise PermissionError("Permission denied")
        
        with pytest.raises(ValueError, match="Permission denied in test_op"):
            await handle_operation("test_op", test_func)

    @pytest.mark.asyncio
    async def test_handle_operation_key_error(self):
        """Test handle_operation with KeyError"""
        def test_func():
            raise KeyError("missing_key")
        
        with pytest.raises(ValueError, match="Key not found in test_op"):
            await handle_operation("test_op", test_func)

    @pytest.mark.asyncio
    async def test_handle_operation_value_error(self):
        """Test handle_operation with ValueError"""
        def test_func():
            raise ValueError("Invalid value")
        
        with pytest.raises(ValueError, match="Value error in test_op"):
            await handle_operation("test_op", test_func)

    @pytest.mark.asyncio
    async def test_handle_operation_general_exception(self):
        """Test handle_operation with general exception"""
        def test_func():
            raise RuntimeError("Something went wrong")
        
        with pytest.raises(ValueError, match="Unexpected error in test_op"):
            await handle_operation("test_op", test_func)

    # Test MCP implementation functions
    @pytest.mark.asyncio
    async def test_mktotp_register_secret_impl_success(self, temp_qr_image_file, temp_secrets_file):
        """Test successful secret registration via MCP"""
        with patch('mktotp.mcp_impl.register_secret') as mock_register:
            mock_register.return_value = [{
                "name": "test_secret",
                "account": "test@example.com",
                "issuer": "Test",
                "secret": "JBSWY3DPEHPK3PXP"
            }]
            
            result = await mktotp_register_secret_impl(
                qr_code_image_file_path=temp_qr_image_file,
                new_name="test_secret",
                secrets_file=temp_secrets_file
            )
            
            assert len(result) == 1
            assert result[0]["name"] == "test_secret"
            mock_register.assert_called_once()

    @pytest.mark.asyncio
    async def test_mktotp_register_secret_impl_validation_errors(self, temp_qr_image_file):
        """Test mktotp_register_secret_impl with validation errors"""
        # Test missing QR file
        with pytest.raises((ValueError, FileNotFoundError)):
            await mktotp_register_secret_impl(
                qr_code_image_file_path="nonexistent.png",
                new_name="test",
                secrets_file=None
            )
        
        # Test empty secret name
        with pytest.raises(ValueError):
            await mktotp_register_secret_impl(
                qr_code_image_file_path=temp_qr_image_file,
                new_name="",
                secrets_file=None
            )

    @pytest.mark.asyncio
    async def test_mktotp_generate_token_impl_success(self, temp_secrets_file):
        """Test successful token generation via MCP"""
        with patch('mktotp.mcp_impl.gen_token') as mock_gen_token:
            mock_gen_token.return_value = "123456"
            
            result = await mktotp_generate_token_impl(
                secret_name="test_secret",
                secrets_file=temp_secrets_file
            )
            
            assert result == "123456"
            mock_gen_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_mktotp_generate_token_impl_validation_errors(self):
        """Test mktotp_generate_token_impl with validation errors"""
        # Test empty secret name
        with pytest.raises(ValueError):
            await mktotp_generate_token_impl(
                secret_name="",
                secrets_file="test.json"
            )

    @pytest.mark.asyncio
    async def test_mktotp_get_secret_info_list_impl_success(self, temp_secrets_file):
        """Test successful secret list retrieval via MCP"""
        with patch('mktotp.mcp_impl.get_secret_list') as mock_get_list:
            mock_get_list.return_value = [
                {"name": "test1", "account": "test1@example.com", "issuer": "Test1"},
                {"name": "test2", "account": "test2@example.com", "issuer": "Test2"}
            ]
            
            result = await mktotp_get_secret_info_list_impl(
                secrets_file=temp_secrets_file
            )
            
            assert len(result) == 2
            mock_get_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_mktotp_get_secret_info_list_impl_none_file(self):
        """Test mktotp_get_secret_info_list_impl with None file"""
        with patch('mktotp.mcp_impl.get_secret_list') as mock_get_list:
            mock_get_list.return_value = []
            
            result = await mktotp_get_secret_info_list_impl(
                secrets_file=None
            )
            
            assert result == []
            mock_get_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_mktotp_remove_secrets_impl_success(self, temp_secrets_file):
        """Test successful secret removal via MCP"""
        with patch('mktotp.mcp_impl.remove_secrets') as mock_remove:
            mock_remove.return_value = ["test1", "test2"]
            
            result = await mktotp_remove_secrets_impl(
                secret_names=["test1", "test2"],
                secrets_file=temp_secrets_file
            )
            
            assert result == ["test1", "test2"]
            mock_remove.assert_called_once()

    @pytest.mark.asyncio
    async def test_mktotp_remove_secrets_impl_validation_errors(self):
        """Test mktotp_remove_secrets_impl with validation errors"""
        # Test empty secret names list
        with pytest.raises(ValueError, match="At least one secret name must be provided"):
            await mktotp_remove_secrets_impl(
                secret_names=[],
                secrets_file="test.json"
            )
        
        # Test empty secret name in list
        with pytest.raises(ValueError):
            await mktotp_remove_secrets_impl(
                secret_names=["", "valid_name"],
                secrets_file="test.json"
            )

    @pytest.mark.asyncio
    async def test_mktotp_rename_secret_impl_success(self, temp_secrets_file):
        """Test successful secret renaming via MCP"""
        with patch('mktotp.mcp_impl.rename_secret') as mock_rename:
            mock_rename.return_value = True
            
            result = await mktotp_rename_secret_impl(
                old_name="old_name",
                new_name="new_name",
                secrets_file=temp_secrets_file
            )
            
            assert result is True
            mock_rename.assert_called_once()

    @pytest.mark.asyncio
    async def test_mktotp_rename_secret_impl_validation_errors(self):
        """Test mktotp_rename_secret_impl with validation errors"""
        # Test empty old name
        with pytest.raises(ValueError):
            await mktotp_rename_secret_impl(
                old_name="",
                new_name="new_name",
                secrets_file="test.json"
            )
        
        # Test empty new name
        with pytest.raises(ValueError):
            await mktotp_rename_secret_impl(
                old_name="old_name",
                new_name="",
                secrets_file="test.json"
            )
        
        # Test same old and new names
        with pytest.raises(ValueError, match="Old name and new name cannot be the same"):
            await mktotp_rename_secret_impl(
                old_name="same_name",
                new_name="same_name",
                secrets_file="test.json"
            )

    @pytest.mark.asyncio
    @patch('mktotp.mcp_impl.get_logger')
    async def test_mcp_functions_logging(self, mock_get_logger, temp_qr_image_file, temp_secrets_file):
        """Test that MCP functions log appropriately"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.mcp_impl.register_secret') as mock_register:
            mock_register.return_value = [{"name": "test", "account": "test@example.com", "issuer": "Test", "secret": "SECRET"}]
            
            await mktotp_register_secret_impl(
                qr_code_image_file_path=temp_qr_image_file,
                new_name="test",
                secrets_file=temp_secrets_file
            )
            
            # Should have logged info messages
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_all_mcp_functions_with_none_secrets_file(self, temp_qr_image_file):
        """Test all MCP functions with None secrets file"""
        with patch('mktotp.mcp_impl.register_secret') as mock_register, \
             patch('mktotp.mcp_impl.gen_token') as mock_gen_token, \
             patch('mktotp.mcp_impl.get_secret_list') as mock_get_list, \
             patch('mktotp.mcp_impl.remove_secrets') as mock_remove, \
             patch('mktotp.mcp_impl.rename_secret') as mock_rename:
            
            mock_register.return_value = []
            mock_gen_token.return_value = "123456"
            mock_get_list.return_value = []
            mock_remove.return_value = []
            mock_rename.return_value = True
            
            # All should work with None secrets_file
            await mktotp_register_secret_impl(temp_qr_image_file, "test", None)
            await mktotp_generate_token_impl("test", None)
            await mktotp_get_secret_info_list_impl(None)
            await mktotp_remove_secrets_impl(["test"], None)
            await mktotp_rename_secret_impl("old", "new", None)

    @pytest.mark.asyncio
    async def test_all_mcp_functions_with_empty_string_secrets_file(self, temp_qr_image_file):
        """Test all MCP functions with empty string secrets file"""
        with patch('mktotp.mcp_impl.register_secret') as mock_register, \
             patch('mktotp.mcp_impl.gen_token') as mock_gen_token, \
             patch('mktotp.mcp_impl.get_secret_list') as mock_get_list, \
             patch('mktotp.mcp_impl.remove_secrets') as mock_remove, \
             patch('mktotp.mcp_impl.rename_secret') as mock_rename:
            
            mock_register.return_value = []
            mock_gen_token.return_value = "123456"
            mock_get_list.return_value = []
            mock_remove.return_value = []
            mock_rename.return_value = True
            
            # All should work with empty string secrets_file (should use default)
            await mktotp_register_secret_impl(temp_qr_image_file, "test", "")
            await mktotp_generate_token_impl("test", "")
            await mktotp_get_secret_info_list_impl("")
            await mktotp_remove_secrets_impl(["test"], "")
            await mktotp_rename_secret_impl("old", "new", "")

    @pytest.mark.asyncio
    async def test_handle_operation_with_logging(self):
        """Test handle_operation logs operation details"""
        with patch('mktotp.mcp_impl.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            def test_func(arg1="test"):
                return f"result: {arg1}"
            
            result = await handle_operation("test_operation", test_func, arg1="value")
            
            assert result == "result: value"
            # Verify logging calls
            mock_logger.info.assert_called()
            mock_logger.debug.assert_called()
