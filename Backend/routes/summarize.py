"""
Summarize Route - Handles medical report summarization
"""

from flask import Blueprint, request, jsonify
from services.llm_service import LLMService
from services.text_cleaner import TextCleaner
from services.report_service import ReportService
from services.medicine_service import MedicineService
from utils.auth_helpers import get_current_user_or_raise

summarize_bp = Blueprint('summarize', __name__)
llm_service = LLMService()
text_cleaner = TextCleaner()
report_service = ReportService()
medicine_service = MedicineService()

@summarize_bp.route('/summarize', methods=['POST'])
def summarize_report():
    """
    Summarize medical report text into patient-friendly and doctor-focused summaries
    
    Request Body:
        {
            "text": str  # Medical report text
        }
    
    Response:
        {
            "success": bool,
            "patient_summary": str,
            "doctor_summary": str,
            "key_findings": [str],
            "medications": [str],
            "critical_warnings": [str],
            "follow_up": str
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Text field is required'
            }), 400
        
        text = data['text']
        
        if not text or not text.strip():
            return jsonify({
                'success': False,
                'error': 'Text cannot be empty'
            }), 400
        
        # Clean and preprocess text
        cleaned_text = text_cleaner.clean_text(text)
        
        # Generate summaries using LLM
        result = llm_service.summarize_medical_report(cleaned_text)
        medicines = medicine_service.extract_medicines_from_report(
            cleaned_text,
            llm_medications=result.get("medications", []),
        )
        medicine_details = [medicine_service.get_medicine_details(name) for name in medicines]
        result["medicine_details"] = medicine_details
        
        response_payload = {
            'success': True,
            **result
        }

        # Optional persistence for authenticated users
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                user = get_current_user_or_raise()
                report_title = (data.get("report_title") or "Medical Report").strip()
                report_id = report_service.save_report(
                    user_id=user["user_id"],
                    report_title=report_title,
                    extracted_text=cleaned_text,
                    summary=result,
                    medicines=medicine_details,
                )
                response_payload["saved_report_id"] = report_id
            except Exception:
                response_payload["save_warning"] = "Report summary generated but could not be saved."

        return jsonify(response_payload), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

