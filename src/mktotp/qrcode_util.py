# encoding: utf-8-sig

import os

from pathlib import Path
from .logutil import get_logger

# ----------------------------------------------------------------------------
# Function to decode QR codes from an image file
def decode_qrcode_impl(file_path: str | os.PathLike) -> list[str]:
    """
    Decode QR codes from an image file.

    This function reads an image file, detects QR codes within it, and returns
    the decoded strings. It supports various image formats including PNG, JPG,
    JPEG, BMP, TIFF, and SVG (which is converted to PNG before decoding).

    Args:
        file_path (str): Path to the image file containing QR codes.

    Returns:
        list[str]: A list of decoded strings from the QR codes.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file format is unsupported.
    """
    import cv2
    decoded_info = []
    img = cv2.imread(str(file_path))
    if img is not None:
        detector = cv2.QRCodeDetector()
        retval, data_seq, _, _ = detector.detectAndDecodeMulti(img)
        if retval:
            # Filter out empty strings from the decoded info
            decoded_info = [data for data in data_seq if data != '']

    return decoded_info

# ----------------------------------------------------------------------------
def decode_qrcode(file_path: str | os.PathLike) -> list[str]:
    """
    Decode QR codes from an image file.

    Args:
        file_path (str): Path to the image file containing QR codes.

    Returns:
        list[str]: A list of decoded strings from the QR codes.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file format is unsupported.
    """
    log_obj = get_logger()
    image_path = Path(file_path)
    if not image_path.is_file():
        log_obj.error(f"File not found: {file_path}")  
        raise FileNotFoundError(f"File not found: {file_path}")
    
    decoded_info = []
    lowwer_path = str(file_path).lower()
    if lowwer_path.endswith('.svg'):
        # convert SVG to PNG before decoding
        try:
            import cairosvg
            import tempfile
            from PIL import Image
            
            # make temporary file path for the PNG
            with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as temp_file:
                temp_png_path = Path(temp_file.name)
                
                # Convert SVG to PNG
                cairosvg.svg2png(url=str(file_path), write_to=str(temp_png_path))
                
                # read PNG to PIL Image and add white background with margin
                img = Image.open(temp_png_path)
                
                # Define the margin size
                margin = 10
                # new dimensions with margin
                new_width = img.width + margin * 2
                new_height = img.height + margin * 2
                
                # Create a new image with white background
                background = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 255))
                # Paste the original image onto the background
                background.paste(img, (margin, margin), mask=img if img.mode == 'RGBA' else None)
                
                # Save the processed image back to the same temp file
                background.save(temp_png_path, format='PNG')
                
                # Decode QR code from the processed image
                decoded_info = decode_qrcode_impl(temp_png_path)
                
        except ImportError as e:
            log_obj.error(f"Required library not available for SVG processing: {e}")
            raise ValueError(f"SVG support requires cairosvg and pillow: {e}")
        except Exception as e:
            log_obj.error(f"Error processing SVG file: {e}")
            raise ValueError(f"Failed to process SVG file: {e}")
    elif lowwer_path.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        decoded_info = decode_qrcode_impl(image_path)
    else:
        log_obj.error(f"Unsupported file format: {file_path}")
        raise ValueError(f"Unsupported file format: {file_path}")

    return decoded_info

