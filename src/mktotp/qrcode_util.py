# encoding: utf-8-sig

import cv2

from pathlib import Path
from .logutil import get_logger

# ----------------------------------------------------------------------------
def decode_qrcode(file_path: str) -> list[str]:
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
    if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        log_obj.error(f"Unsupported file format: {file_path}")
        raise ValueError(f"Unsupported file format: {file_path}")

    decoded_info = []
    img = cv2.imread(file_path)
    if img is not None:
        detector = cv2.QRCodeDetector()
        retval, data_seq, _, _ = detector.detectAndDecodeMulti(img)
        if retval:
            # Filter out empty strings from the decoded info
            decoded_info = [data for data in data_seq if data != '']

    return decoded_info

