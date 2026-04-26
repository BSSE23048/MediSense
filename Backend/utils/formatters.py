"""
Formatters Utility - Format API responses
"""

from datetime import datetime

class ResponseFormatter:
    """Utility class for formatting API responses"""
    
    @staticmethod
    def format_error(message, status_code=400):
        """Format error response"""
        return {
            'success': False,
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        }, status_code
    
    @staticmethod
    def format_success(data, status_code=200):
        """Format success response"""
        response = {
            'success': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        response.update(data)
        return response, status_code
    
    @staticmethod
    def format_ocr_response(text, confidence, file_type):
        """Format OCR response"""
        return {
            'success': True,
            'extracted_text': text,
            'confidence': round(confidence, 2),
            'file_type': file_type,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_summary_response(summary_data):
        """Format summary response"""
        return {
            'success': True,
            **summary_data,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_symptom_response(symptom_data):
        """Format symptom analysis response"""
        return {
            'success': True,
            **symptom_data,
            'timestamp': datetime.utcnow().isoformat()
        }

