"""
Voice Routes - STT/TTS APIs for voice assistant.
"""

from flask import Blueprint, jsonify, request

from services.voice_service import VoiceService
from services.llm_service import LLMService

voice_bp = Blueprint("voice", __name__)
voice_service = VoiceService()
llm_service = LLMService()


DISCLAIMERS = {
    "en": "Reminder: This is informational only, not a diagnosis.",
    "ur": "یاد رکھیں: یہ معلومات صرف آگاہی کے لیے ہیں، طبی تشخیص نہیں۔",
    "hi": "स्मरण: यह केवल जानकारी के लिए है, निदान नहीं।",
    "ar": "ملاحظة: هذه معلومات للتوعية فقط وليست تشخيصًا طبيًا.",
}


@voice_bp.route("/voice/transcribe", methods=["POST"])
def transcribe_voice():
    try:
        audio_file = request.files.get("audio")
        result = voice_service.transcribe_file(audio_file)
        return jsonify(result), 200
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@voice_bp.route("/voice/speak", methods=["POST"])
def speak_text():
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        include_disclaimer = bool(data.get("include_disclaimer", True))
        language = (data.get("language") or "en").lower().strip()

        if not text:
            return jsonify({"success": False, "error": "Text is required"}), 400

        # Translate body text first (before adding disclaimer) so we keep
        # the localized disclaimer untouched.
        speak_text_value = text
        if language and language != "en":
            try:
                speak_text_value = llm_service.translate_text(text, target_language=language)
            except Exception as translate_error:
                print(f"[voice/speak] translation failed, using original: {translate_error}")
                speak_text_value = text

        if include_disclaimer:
            disclaimer = DISCLAIMERS.get(language, DISCLAIMERS["en"])
            speak_text_value = f"{speak_text_value}\n\n{disclaimer}"

        result = voice_service.synthesize_text(speak_text_value, language=language)
        # Always return 200 so the client can still read translated text (text_used)
        # even when cloud TTS is unavailable. The body carries success=false in that case.
        return jsonify(result), 200
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
