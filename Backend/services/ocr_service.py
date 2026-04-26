"""
OCR Service - Handles text extraction from images
"""

import os
from config import Config

class OCRService:
    """Service for Optical Character Recognition from medical document images"""
    
    def __init__(self):
        self.use_easyocr = Config.USE_EASYOCR
        
        if self.use_easyocr:
            try:
                import easyocr
                self.reader = easyocr.Reader(['en'], gpu=False)
                self.ocr_method = 'easyocr'
            except ImportError:
                self.ocr_method = 'tesseract'
                self._init_tesseract()
        else:
            self.ocr_method = 'tesseract'
            self._init_tesseract()
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR"""
        try:
            import pytesseract
            from PIL import Image
            import platform
            
            # Set Tesseract command path if provided (Windows)
            if Config.TESSERACT_CMD:
                pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
            elif platform.system() == 'Windows':
                # Try default Windows installation path
                default_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
                ]
                for path in default_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
            
            self.pytesseract = pytesseract
            self.Image = Image
        except ImportError:
            raise ImportError("pytesseract and Pillow are required for OCR. Install with: pip install pytesseract pillow")
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from image file using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if self.ocr_method == 'easyocr':
            return self._extract_with_easyocr(image_path)
        else:
            return self._extract_with_tesseract(image_path)
    
    def _extract_with_easyocr(self, image_path):
        """Extract text using EasyOCR"""
        results = self.reader.readtext(image_path)
        
        # Combine all detected text
        extracted_text = ' '.join([result[1] for result in results])
        
        # Calculate average confidence
        if results:
            confidence = sum([result[2] for result in results]) / len(results)
        else:
            confidence = 0.0
        
        return extracted_text, confidence
    
    def _extract_with_tesseract(self, image_path):
        """Extract text using Tesseract OCR"""
        try:
            # Check if Tesseract is available
            try:
                self.pytesseract.get_tesseract_version()
            except Exception as e:
                raise Exception(f"Tesseract OCR not found. Please install Tesseract OCR. Error: {str(e)}")
            
            image = self.Image.open(image_path)
            
            # Extract text
            extracted_text = self.pytesseract.image_to_string(image)
            
            # Get confidence data
            data = self.pytesseract.image_to_data(image, output_type=self.pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            
            return extracted_text, confidence
            
        except FileNotFoundError as e:
            raise Exception(f"Tesseract OCR executable not found. Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki")
        except Exception as e:
            error_msg = str(e)
            if 'tesseract' in error_msg.lower() and 'not found' in error_msg.lower():
                raise Exception(f"Tesseract OCR not installed. Please install it from https://github.com/UB-Mannheim/tesseract/wiki")
            raise Exception(f"OCR extraction failed: {error_msg}")

