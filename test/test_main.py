# encoding: utf-8-sig

import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the main module
import mktotp.__main__ as main_module


class TestMain:
    """Test class for main module functions"""

    @pytest.fixture
    def temp_secrets_file(self):
        """Create a temporary secrets file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            import json
            test_data = {
                "secrets": [
                    {
                        "name": "test_secret",
                        "account": "test@example.com",
                        "issuer": "TestIssuer",
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

    def test_main_module_import(self):
        """Test that main module can be imported without errors"""
        # Module should be imported successfully
        assert main_module is not None

    @patch('mktotp.__main__.get_logger')
    @patch('sys.argv', ['mktotp', 'add', '-nn', 'test', '-f', 'test.png'])
    def test_main_with_add_command(self, mock_get_logger):
        """Test main function with add command"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.__main__.handle_add') as mock_handle_add:
            try:
                main_module.main()
            except SystemExit:
                pass  # main() may call sys.exit()
        
            mock_handle_add.assert_called_once()

    @patch('mktotp.__main__.get_logger')
    @patch('sys.argv', ['mktotp', 'get', '-n', 'test'])
    def test_main_with_get_command(self, mock_get_logger):
        """Test main function with get command"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.__main__.handle_get') as mock_handle_get:
            try:
                main_module.main()
            except SystemExit:
                pass
        
            mock_handle_get.assert_called_once()

    @patch('mktotp.__main__.get_logger')
    @patch('sys.argv', ['mktotp', 'list'])
    def test_main_with_list_command(self, mock_get_logger):
        """Test main function with list command"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.__main__.handle_list') as mock_handle_list:
            try:
                main_module.main()
            except SystemExit:
                pass
        
            mock_handle_list.assert_called_once()

    @patch('mktotp.__main__.get_logger')
    @patch('sys.argv', ['mktotp', 'remove', '-n', 'test'])
    def test_main_with_remove_command(self, mock_get_logger):
        """Test main function with remove command"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.__main__.handle_remove') as mock_handle_remove:
            try:
                main_module.main()
            except SystemExit:
                pass
        
            mock_handle_remove.assert_called_once()

    @patch('mktotp.__main__.get_logger')
    @patch('sys.argv', ['mktotp', 'rename', '-n', 'old', '-nn', 'new'])
    def test_main_with_rename_command(self, mock_get_logger):
        """Test main function with rename command"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.__main__.handle_rename') as mock_handle_rename:
            try:
                main_module.main()
            except SystemExit:
                pass
        
            mock_handle_rename.assert_called_once()

    @patch('mktotp.__main__.get_logger')
    @patch('sys.argv', ['mktotp', 'mcp'])
    def test_main_with_mcp_command(self, mock_get_logger):
        """Test main function with mcp command"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.__main__.handle_mcp') as mock_handle_mcp:
            try:
                main_module.main()
            except SystemExit:
                pass
        
            mock_handle_mcp.assert_called_once()

    @patch('mktotp.__main__.get_logger')
    @patch('sys.argv', ['mktotp', 'list', '-v', '2'])
    def test_main_with_verbose_logging(self, mock_get_logger):
        """Test main function with verbose logging"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('mktotp.__main__.handle_list') as mock_handle_list:
            try:
                main_module.main()
            except SystemExit:
                pass
            
            mock_get_logger.assert_called_once_with(verbose_level=2)

    @patch('mktotp.__main__.register_secret')
    def test_handle_add_success(self, mock_register, temp_qr_image_file, temp_secrets_file):
        """Test handle_add function with successful registration"""
        mock_register.return_value = [{
            "name": "test_secret",
            "account": "test@example.com", 
            "issuer": "Test",
            "secret": "JBSWY3DPEHPK3PXP"
        }]
        
        args = MagicMock()
        args.new_name = "test_secret"
        args.file = temp_qr_image_file
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_add(args)
            
            mock_register.assert_called_once_with(
                qr_code_file=temp_qr_image_file,
                new_name="test_secret",
                secrets_file=temp_secrets_file
            )
            mock_print.assert_called()

    @patch('mktotp.__main__.register_secret')
    def test_handle_add_failure(self, mock_register, temp_qr_image_file, temp_secrets_file):
        """Test handle_add function with registration failure"""
        mock_register.side_effect = ValueError("Test error")
        
        args = MagicMock()
        args.new_name = "test_secret"
        args.file = temp_qr_image_file
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            # The function should handle exceptions internally
            try:
                main_module.handle_add(args)
            except ValueError:
                pass  # Exception is expected
            
            # Should call the register_secret function
            mock_register.assert_called_once()

    @patch('mktotp.__main__.gen_token')
    def test_handle_get_success(self, mock_gen_token, temp_secrets_file):
        """Test handle_get function with successful token generation"""
        mock_gen_token.return_value = "123456"
        
        args = MagicMock()
        args.name = "test_secret"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_get(args)
            
            mock_gen_token.assert_called_once_with(
                name="test_secret",
                secrets_file=temp_secrets_file
            )
            mock_print.assert_called_with("123456")

    @patch('mktotp.__main__.gen_token')
    def test_handle_get_failure(self, mock_gen_token, temp_secrets_file):
        """Test handle_get function with token generation failure"""
        mock_gen_token.side_effect = ValueError("Secret not found")
        
        args = MagicMock()
        args.name = "nonexistent"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            # The function should handle exceptions internally
            try:
                main_module.handle_get(args)
            except ValueError:
                pass  # Exception is expected
            
            # Should call the gen_token function
            mock_gen_token.assert_called_once()

    @patch('mktotp.__main__.get_secret_list')
    def test_handle_list_success(self, mock_get_list, temp_secrets_file):
        """Test handle_list function with successful list retrieval"""
        mock_get_list.return_value = [
            {"name": "test1", "account": "test1@example.com", "issuer": "Test1"},
            {"name": "test2", "account": "test2@example.com", "issuer": "Test2"}
        ]
        
        args = MagicMock()
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_list(args)
            
            mock_get_list.assert_called_once_with(secrets_file=temp_secrets_file)
            # Should print list information
            assert mock_print.call_count > 0

    @patch('mktotp.__main__.get_secret_list')
    def test_handle_list_empty(self, mock_get_list, temp_secrets_file):
        """Test handle_list function with empty list"""
        mock_get_list.return_value = []
        
        args = MagicMock()
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_list(args)
            
            mock_print.assert_called_with("No secrets found.")

    @patch('mktotp.__main__.get_secret_list')
    def test_handle_list_failure(self, mock_get_list, temp_secrets_file):
        """Test handle_list function with list retrieval failure"""
        mock_get_list.side_effect = FileNotFoundError("Secrets file not found")
        
        args = MagicMock()
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            # The function should handle exceptions internally
            try:
                main_module.handle_list(args)
            except FileNotFoundError:
                pass  # Exception is expected
            
            # Should call the get_secret_list function
            mock_get_list.assert_called_once()

    @patch('mktotp.__main__.remove_secrets')
    def test_handle_remove_success(self, mock_remove, temp_secrets_file):
        """Test handle_remove function with successful removal"""
        mock_remove.return_value = ["test_secret"]
        
        args = MagicMock()
        args.name = "test_secret"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_remove(args)
            
            mock_remove.assert_called_once_with(
                names=["test_secret"],
                secrets_file=temp_secrets_file
            )
            mock_print.assert_called()

    @patch('mktotp.__main__.remove_secrets')
    def test_handle_remove_not_found(self, mock_remove, temp_secrets_file):
        """Test handle_remove function when secret not found"""
        mock_remove.return_value = []
        
        args = MagicMock()
        args.name = "nonexistent"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_remove(args)
            
            mock_print.assert_called_with("Secret 'nonexistent' not found.")

    @patch('mktotp.__main__.remove_secrets')
    def test_handle_remove_failure(self, mock_remove, temp_secrets_file):
        """Test handle_remove function with removal failure"""
        mock_remove.side_effect = ValueError("Test error")
        
        args = MagicMock()
        args.name = "test_secret"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            # The function should handle exceptions internally
            try:
                main_module.handle_remove(args)
            except ValueError:
                pass  # Exception is expected
            
            # Should call the remove_secrets function
            mock_remove.assert_called_once()

    @patch('mktotp.__main__.rename_secret')
    def test_handle_rename_success(self, mock_rename, temp_secrets_file):
        """Test handle_rename function with successful rename"""
        mock_rename.return_value = True
        
        args = MagicMock()
        args.name = "old_name"
        args.new_name = "new_name"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_rename(args)
            
            mock_rename.assert_called_once_with(
                name="old_name",
                new_name="new_name",
                secrets_file=temp_secrets_file
            )
            mock_print.assert_called()

    @patch('mktotp.__main__.rename_secret')
    def test_handle_rename_not_found(self, mock_rename, temp_secrets_file):
        """Test handle_rename function when secret not found"""
        mock_rename.return_value = False
        
        args = MagicMock()
        args.name = "nonexistent"
        args.new_name = "new_name"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            main_module.handle_rename(args)
            
            mock_print.assert_called_with("Secret 'nonexistent' not found or rename failed.")

    @patch('mktotp.__main__.rename_secret')
    def test_handle_rename_failure(self, mock_rename, temp_secrets_file):
        """Test handle_rename function with rename failure"""
        mock_rename.side_effect = ValueError("Test error")
        
        args = MagicMock()
        args.name = "old_name"
        args.new_name = "new_name"
        args.secrets_file = temp_secrets_file
        
        with patch('builtins.print') as mock_print:
            # The function should handle exceptions internally
            try:
                main_module.handle_rename(args)
            except ValueError:
                pass  # Exception is expected
            
            # Should call the rename_secret function
            mock_rename.assert_called_once()

    @patch('mktotp.__main__.run_as_mcp_server')
    def test_handle_mcp_server_mode(self, mock_run_server):
        """Test handle_mcp function in server mode"""
        args = MagicMock()
        args.mcp_server = True
        
        main_module.handle_mcp(args)
        
        mock_run_server.assert_called_once()

    @patch('mktotp.__main__.disp_tools')
    def test_handle_mcp_client_mode(self, mock_disp_tools):
        """Test handle_mcp function in client mode"""
        args = MagicMock()
        args.mcp_server = False
        
        main_module.handle_mcp(args)
        
        mock_disp_tools.assert_called_once()

    def test_main_function_exists(self):
        """Test that main function exists and is callable"""
        assert hasattr(main_module, 'main')
        assert callable(main_module.main)

    def test_main_argument_parsing(self):
        """Test that main function parses arguments correctly"""
        with patch('mktotp.__main__.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            with patch('mktotp.__main__.handle_list') as mock_handle_list:
                with patch('sys.argv', ['mktotp', 'list']):
                    try:
                        main_module.main()
                    except SystemExit:
                        pass
                
                    mock_handle_list.assert_called_once()

    def test_main_module_structure(self):
        """Test that main module has expected structure"""
        # Test that the if __name__ == "__main__" pattern exists
        with open(main_module.__file__, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'if __name__ == "__main__"' in content
            assert 'main()' in content

    def test_exception_handling_in_main(self):
        """Test that main function handles exceptions gracefully"""
        with patch('mktotp.__main__.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Test exception handling by providing invalid arguments
            with patch('sys.argv', ['mktotp', 'invalid_command']):
                with patch('builtins.print') as mock_print:
                    try:
                        main_module.main()
                    except SystemExit:
                        pass  # ArgumentParser raises SystemExit for invalid commands
                    
                    # Function should handle gracefully
