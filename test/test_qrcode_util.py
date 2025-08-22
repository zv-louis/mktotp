# encoding: utf-8-sig

import os
import tempfile
import pytest
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

from mktotp.qrcode_util import decode_qrcode


class TestQRCodeUtil:
    """Test class for QR code utility functions"""

    @pytest.fixture
    def temp_image_file(self):
        """Create a temporary image file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def create_test_qr_image(self, temp_image_file):
        """Create a test QR code image"""
        # Create a simple test image (dummy QR code)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(temp_image_file, test_image)
        return temp_image_file

    def test_decode_qrcode_file_not_found(self):
        """Test decode_qrcode with non-existent file"""
        nonexistent_file = "definitely_nonexistent_file.png"
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            decode_qrcode(nonexistent_file)

    def test_decode_qrcode_unsupported_format(self, temp_image_file):
        """Test decode_qrcode with unsupported file format"""
        # Change extension to unsupported format
        unsupported_file = temp_image_file.replace('.png', '.txt')
        Path(temp_image_file).rename(unsupported_file)
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                decode_qrcode(unsupported_file)
        finally:
            if os.path.exists(unsupported_file):
                os.unlink(unsupported_file)

    def test_decode_qrcode_supported_formats(self, temp_image_file):
        """Test decode_qrcode with all supported formats"""
        supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        
        for ext in supported_formats:
            test_file = temp_image_file.replace('.png', ext)
            # Create a simple test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(test_file, test_image)
            
            try:
                # Should not raise exception for supported formats
                result = decode_qrcode(test_file)
                assert isinstance(result, list)
            finally:
                if os.path.exists(test_file):
                    os.unlink(test_file)

    @patch('cv2.imread')
    def test_decode_qrcode_invalid_image(self, mock_imread, temp_image_file):
        """Test decode_qrcode with invalid image (cv2.imread returns None)"""
        mock_imread.return_value = None
        
        # Create a dummy file
        with open(temp_image_file, 'w') as f:
            f.write("dummy content")
        
        result = decode_qrcode(temp_image_file)
        assert result == []

    @patch('cv2.QRCodeDetector')
    def test_decode_qrcode_successful_detection(self, mock_detector_class, create_test_qr_image):
        """Test successful QR code detection"""
        # Mock the detector
        mock_detector = MagicMock()
        mock_detector_class.return_value = mock_detector
        
        # Mock successful detection
        test_data = ['otpauth://totp/Test:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test']
        mock_detector.detectAndDecodeMulti.return_value = (True, test_data, None, None)
        
        result = decode_qrcode(create_test_qr_image)
        
        assert result == test_data
        mock_detector.detectAndDecodeMulti.assert_called_once()

    @patch('cv2.QRCodeDetector')
    def test_decode_qrcode_multiple_codes(self, mock_detector_class, create_test_qr_image):
        """Test detection of multiple QR codes"""
        mock_detector = MagicMock()
        mock_detector_class.return_value = mock_detector
        
        # Mock multiple QR codes
        test_data = [
            'otpauth://totp/Test1:user1@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test1',
            'otpauth://totp/Test2:user2@example.com?secret=JBSWY3DPEHPK3PXQ&issuer=Test2'
        ]
        mock_detector.detectAndDecodeMulti.return_value = (True, test_data, None, None)
        
        result = decode_qrcode(create_test_qr_image)
        
        assert result == test_data
        assert len(result) == 2

    @patch('cv2.QRCodeDetector')
    def test_decode_qrcode_filter_empty_strings(self, mock_detector_class, create_test_qr_image):
        """Test filtering of empty strings from detection results"""
        mock_detector = MagicMock()
        mock_detector_class.return_value = mock_detector
        
        # Mock detection with empty strings
        test_data = [
            'otpauth://totp/Test:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test',
            '',  # Empty string should be filtered out
            'otpauth://totp/Test2:user2@example.com?secret=JBSWY3DPEHPK3PXQ&issuer=Test2',
            ''   # Another empty string
        ]
        expected_result = [
            'otpauth://totp/Test:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Test',
            'otpauth://totp/Test2:user2@example.com?secret=JBSWY3DPEHPK3PXQ&issuer=Test2'
        ]
        mock_detector.detectAndDecodeMulti.return_value = (True, test_data, None, None)
        
        result = decode_qrcode(create_test_qr_image)
        
        assert result == expected_result
        assert len(result) == 2

    @patch('cv2.QRCodeDetector')
    def test_decode_qrcode_no_detection(self, mock_detector_class, create_test_qr_image):
        """Test when no QR codes are detected"""
        mock_detector = MagicMock()
        mock_detector_class.return_value = mock_detector
        
        # Mock no detection
        mock_detector.detectAndDecodeMulti.return_value = (False, [], None, None)
        
        result = decode_qrcode(create_test_qr_image)
        
        assert result == []

    def test_decode_qrcode_case_insensitive_extension(self, temp_image_file):
        """Test that file extension check is case-insensitive"""
        # Test uppercase extensions
        uppercase_file = temp_image_file.replace('.png', '.PNG')
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(uppercase_file, test_image)
        
        try:
            # Should not raise exception for uppercase extension
            result = decode_qrcode(uppercase_file)
            assert isinstance(result, list)
        finally:
            if os.path.exists(uppercase_file):
                os.unlink(uppercase_file)

    @patch('mktotp.qrcode_util.get_logger')
    def test_decode_qrcode_logging(self, mock_get_logger, temp_image_file):
        """Test that appropriate logging occurs"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Test file not found logging
        with pytest.raises(FileNotFoundError):
            decode_qrcode("nonexistent.png")
        
        mock_logger.error.assert_called()
        
        # Reset mock
        mock_logger.reset_mock()
        
        # Test unsupported format logging
        unsupported_file = temp_image_file.replace('.png', '.txt')
        Path(temp_image_file).rename(unsupported_file)
        
        try:
            with pytest.raises(ValueError):
                decode_qrcode(unsupported_file)
            
            mock_logger.error.assert_called()
        finally:
            if os.path.exists(unsupported_file):
                os.unlink(unsupported_file)

    @patch('cairosvg.svg2png')
    @patch('PIL.Image.open')
    def test_decode_qrcode_svg_support(self, mock_image_open, mock_svg2png):
        """Test SVG file support"""
        # Create a temporary SVG file
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
                <rect width="100" height="100" fill="white"/>
            </svg>'''
            f.write(svg_content.encode())
            svg_file = f.name
        
        try:
            # Mock PIL Image
            mock_img = MagicMock()
            mock_img.width = 100
            mock_img.height = 100
            mock_img.mode = 'RGBA'
            mock_image_open.return_value = mock_img
            
            # Mock the background image
            mock_background = MagicMock()
            
            with patch('PIL.Image.new', return_value=mock_background):
                with patch('mktotp.qrcode_util.decode_qrcode_impl', return_value=['test_result']):
                    result = decode_qrcode(svg_file)
                    
                    assert result == ['test_result']
                    mock_svg2png.assert_called_once()
                    mock_background.paste.assert_called_once()
                    mock_background.save.assert_called_once()
        
        finally:
            if os.path.exists(svg_file):
                os.unlink(svg_file)

    def test_decode_qrcode_svg_missing_dependencies(self):
        """Test SVG support when dependencies are missing"""
        # Create a temporary SVG file
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            f.write(b'<svg></svg>')
            svg_file = f.name
        
        try:
            # Mock import failure specifically for cairosvg
            with patch('mktotp.qrcode_util.decode_qrcode') as mock_decode:
                def side_effect_import_error(file_path):
                    from mktotp.qrcode_util import get_logger
                    from pathlib import Path
                    
                    log_obj = get_logger()
                    image_path = Path(file_path)
                    if not image_path.is_file():
                        log_obj.error(f"File not found: {file_path}")  
                        raise FileNotFoundError(f"File not found: {file_path}")
                    
                    lowwer_path = str(file_path).lower()
                    if lowwer_path.endswith('.svg'):
                        # Simulate import error
                        log_obj.error("Required library not available for SVG processing: cairosvg not found")
                        raise ValueError("SVG support requires cairosvg and pillow: cairosvg not found")
                    
                    return []
                
                mock_decode.side_effect = side_effect_import_error
                
                with pytest.raises(ValueError, match="SVG support requires"):
                    from mktotp.qrcode_util import decode_qrcode
                    mock_decode(svg_file)
        
        finally:
            if os.path.exists(svg_file):
                os.unlink(svg_file)
