"""
Symptoms Route - Handles AI-powered symptom checking
"""

from flask import Blueprint, request, jsonify
from services.rag_service import RAGService
from services.llm_service import LLMService
from services.report_service import ReportService
from utils.auth_helpers import get_current_user_or_raise

symptoms_bp = Blueprint('symptoms', __name__)
rag_service = RAGService()
llm_service = LLMService()
report_service = ReportService()

@symptoms_bp.route('/symptom-check', methods=['POST'])
def check_symptoms():
    """
    Analyze symptoms and provide possible conditions with RAG-based insights
    
    Request Body:
        {
            "symptoms": str  # Comma-separated or natural language symptoms
        }
    
    Response:
        {
            "success": bool,
            "possible_conditions": [
                {
                    "name": str,
                    "probability": str,
                    "description": str
                }
            ],
            "urgency": str,
            "explanation": str,
            "recommendations": [str],
            "citations": [str],
            "seek_immediate_care_if": [str]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'error': 'Symptoms field is required'
            }), 400
        
        symptoms = data['symptoms']
        
        if not symptoms or not symptoms.strip():
            return jsonify({
                'success': False,
                'error': 'Symptoms cannot be empty'
            }), 400
        
        user_context = ""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                user = get_current_user_or_raise()
                user_context = report_service.get_recent_report_context(user["user_id"], limit=3)
            except Exception:
                user_context = ""

        # Retrieve merged context using RAG + user reports
        context_bundle = rag_service.build_context_bundle(symptoms, user_context=user_context)
        relevant_context = context_bundle.get("context", "")
        
        # Analyze symptoms with LLM using retrieved context
        result = llm_service.analyze_symptoms(symptoms, relevant_context)
        
        return jsonify({
            'success': True,
            **result,
            'context_sources': context_bundle.get("sources", [])
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

