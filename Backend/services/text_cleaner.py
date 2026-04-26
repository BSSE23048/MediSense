"""
Text Cleaner Service - Preprocesses and cleans medical text
"""

import re

class TextCleaner:
    """Utility class for cleaning and preprocessing medical text"""
    
    def clean_text(self, text):
        """
        Clean and normalize medical report text
        
        Args:
            text: Raw text from OCR or PDF
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep medical symbols
        # Keep: letters, numbers, common punctuation, medical symbols
        text = re.sub(r'[^\w\s\.\,\;\:\-\+\%\°\/\(\)]', ' ', text)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def extract_sections(self, text):
        """
        Extract common sections from medical reports
        
        Args:
            text: Medical report text
            
        Returns:
            Dictionary with section names and content
        """
        sections = {}
        
        # Common section headers
        section_patterns = {
            'diagnosis': r'(?:diagnosis|diagnoses|dx)[:]\s*(.+?)(?=\n\n|\n[A-Z]|$)',
            'medications': r'(?:medications|meds|prescription|rx)[:]\s*(.+?)(?=\n\n|\n[A-Z]|$)',
            'test_results': r'(?:test results|lab results|findings)[:]\s*(.+?)(?=\n\n|\n[A-Z]|$)',
            'recommendations': r'(?:recommendations|follow.?up|advice)[:]\s*(.+?)(?=\n\n|\n[A-Z]|$)'
        }
        
        for section_name, pattern in section_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                sections[section_name] = matches[0].strip()
        
        return sections

