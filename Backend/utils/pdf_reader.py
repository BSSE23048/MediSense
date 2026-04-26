"""
PDF Reader Utility - Extracts text from PDF files
"""

import os

class PDFReader:
    """Utility class for reading PDF files"""
    
    def __init__(self):
        try:
            import PyPDF2
            self.PyPDF2 = PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")
    
    def extract_text(self, pdf_path):
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text string
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            text_content = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = self.PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            # Combine all pages
            full_text = '\n\n'.join(text_content)
            
            return full_text
            
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def get_page_count(self, pdf_path):
        """
        Get number of pages in PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = self.PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            raise Exception(f"Failed to get page count: {str(e)}")

