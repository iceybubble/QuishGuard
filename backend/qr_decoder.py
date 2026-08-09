"""
Phase 1: QR Code Decoding
Decodes QR codes from images using OpenCV's built-in detector (avoids zbar system dependency)
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

class QRDecoder:
    """Decode QR codes from images using OpenCV"""
    
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
    
    def decode_from_file(self, image_path: str) -> Optional[str]:
        """
        Decode QR code from an image file.
        
        Args:
            image_path: Path to image file (jpg, png, etc.)
            
        Returns:
            Decoded string (URL, UPI link, etc.) or None if no QR found
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Decode QR
            data, bbox, _ = self.detector.detectAndDecode(image)
            
            if data:
                return data.strip()
            return None
            
        except Exception as e:
            print(f"Error decoding QR from {image_path}: {e}")
            return None
    
    def decode_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        """
        Decode QR code from image bytes (useful for uploaded files).
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Decoded string or None if no QR found
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None
            
            # Decode QR
            data, bbox, _ = self.detector.detectAndDecode(image)
            
            if data:
                return data.strip()
            return None
            
        except Exception as e:
            print(f"Error decoding QR from bytes: {e}")
            return None


def test_qr_decoder():
    """Quick test of QR decoder with sample QR codes"""
    decoder = QRDecoder()
    
    # This is a simple test function
    # In practice, you'd run this with real test images
    print("QR Decoder initialized and ready")
    print("Test: decode_from_file() - pass image path")
    print("Test: decode_from_bytes() - pass image bytes")


if __name__ == "__main__":
    test_qr_decoder()
