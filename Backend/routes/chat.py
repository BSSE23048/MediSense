"""
Chat Routes - Follow-up Q&A thread endpoints
"""

from flask import Blueprint, jsonify, request

from services.conversation_service import ConversationService
from services.llm_service import LLMService
from services.rag_service import RAGService
from services.report_service import ReportService
from utils.auth_helpers import get_current_user_or_raise

chat_bp = Blueprint("chat", __name__)
conversation_service = ConversationService()
llm_service = LLMService()
rag_service = RAGService()
report_service = ReportService()


@chat_bp.route("/chat/thread", methods=["POST"])
def create_or_resume_thread():
    try:
        user = get_current_user_or_raise()
        data = request.get_json() or {}
        report_id = data.get("report_id")
        title = (data.get("title") or "Report Follow-up").strip()
        thread = conversation_service.create_or_resume_thread(user["user_id"], report_id, title)
        return jsonify({"success": True, "thread": thread}), 200
    except PermissionError as error:
        return jsonify({"success": False, "error": str(error)}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@chat_bp.route("/chat/thread/<int:thread_id>/messages", methods=["GET"])
def get_chat_messages(thread_id: int):
    try:
        user = get_current_user_or_raise()
        messages = conversation_service.list_messages(user["user_id"], thread_id)
        return jsonify({"success": True, "messages": messages}), 200
    except PermissionError as error:
        return jsonify({"success": False, "error": str(error)}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@chat_bp.route("/chat/thread/<int:thread_id>/ask", methods=["POST"])
def ask_follow_up(thread_id: int):
    try:
        user = get_current_user_or_raise()
        data = request.get_json() or {}
        question = (data.get("question") or "").strip()
        if not question:
            return jsonify({"success": False, "error": "Question is required"}), 400

        conversation_service.add_message(thread_id, "user", question)
        memory = conversation_service.get_recent_memory(user["user_id"], thread_id, max_turns=8)
        report_context = report_service.get_recent_report_context(user["user_id"], limit=3)
        medical_context = rag_service.build_context_bundle(question, user_context=report_context, conversation_memory=memory)
        answer = llm_service.answer_followup(question, context_bundle=medical_context)
        sources = medical_context.get("sources", [])
        conversation_service.add_message(thread_id, "assistant", answer.get("answer", ""), sources)

        return jsonify({"success": True, **answer, "sources": sources}), 200
    except PermissionError as error:
        return jsonify({"success": False, "error": str(error)}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
