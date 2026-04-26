"""
Voice Service - Cloud STT/TTS wrapper with safe fallbacks.
"""

import base64
import os
import tempfile
from typing import Dict

from config import Config


class VoiceService:
    """Handles speech-to-text and text-to-speech via cloud providers."""

    SUPPORTED_AUDIO_EXTENSIONS = {".webm", ".wav", ".mp3", ".m4a", ".ogg"}

    ELEVENLABS_FORMAT_MAP = {
        "mp3": ("mp3_44100_128", "audio/mpeg"),
        "mp3_high": ("mp3_44100_192", "audio/mpeg"),
        "wav": ("pcm_44100", "audio/wav"),
        "ogg": ("ogg_44100", "audio/ogg"),
    }

    def __init__(self):
        self.stt_provider = (Config.VOICE_STT_PROVIDER or "groq").lower()
        self.tts_provider = (Config.VOICE_TTS_PROVIDER or "elevenlabs").lower()
        self.timeout_seconds = Config.VOICE_TIMEOUT_SECONDS
        self.max_audio_mb = Config.VOICE_MAX_AUDIO_MB

    def transcribe_file(self, uploaded_file) -> Dict:
        """Transcribe uploaded audio into text."""
        if uploaded_file is None:
            raise ValueError("Audio file is required")
        if not uploaded_file.filename:
            raise ValueError("Audio filename is missing")

        ext = os.path.splitext(uploaded_file.filename)[1].lower()
        if ext not in self.SUPPORTED_AUDIO_EXTENSIONS:
            raise ValueError("Unsupported audio format. Use webm/wav/mp3/m4a/ogg")

        uploaded_file.stream.seek(0, os.SEEK_END)
        size_bytes = uploaded_file.stream.tell()
        uploaded_file.stream.seek(0)
        if size_bytes > self.max_audio_mb * 1024 * 1024:
            raise ValueError(f"Audio file too large. Max size is {self.max_audio_mb}MB")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            uploaded_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            transcript = self._transcribe_with_groq(tmp_path)
            return {"success": True, "transcript": transcript.strip()}
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def synthesize_text(self, text: str, language: str = "en") -> Dict:
        """Generate speech for a text string in the requested language."""
        clean_text = (text or "").strip()
        if not clean_text:
            raise ValueError("Text is required for speech synthesis")

        if len(clean_text) > Config.VOICE_MAX_TTS_CHARS:
            clean_text = clean_text[: Config.VOICE_MAX_TTS_CHARS]

        lang = (language or "en").lower().strip()

        last_error = None
        if self.tts_provider == "elevenlabs":
            payload = self._speak_with_elevenlabs(clean_text, lang)
            if payload.get("success"):
                payload["text_used"] = clean_text
                payload["language"] = lang
                return payload
            last_error = payload.get("error")

        if self.tts_provider == "groq":
            payload = self._speak_with_groq(clean_text)
            if payload.get("success"):
                payload["text_used"] = clean_text
                payload["language"] = lang
                return payload
            last_error = payload.get("error")

        if self.tts_provider not in {"elevenlabs", "groq"}:
            payload = self._speak_with_elevenlabs(clean_text, lang)
            if payload.get("success"):
                payload["text_used"] = clean_text
                payload["language"] = lang
                return payload
            last_error = payload.get("error")

        # Final no-key fallback: Google Translate TTS via gTTS.
        # Crucial for non-English languages when ElevenLabs is unavailable
        # and the client OS lacks a native voice (e.g. Urdu on Windows).
        gtts_payload = self._speak_with_gtts(clean_text, lang)
        if gtts_payload.get("success"):
            gtts_payload["text_used"] = clean_text
            gtts_payload["language"] = lang
            return gtts_payload
        last_error = gtts_payload.get("error") or last_error

        return {
            "success": False,
            "error": last_error or "Cloud TTS is not available right now. Please use text response.",
            "text_used": clean_text,
            "language": lang,
        }

    def _transcribe_with_groq(self, file_path: str) -> str:
        if not Config.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is required for voice transcription")
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("Groq SDK not installed. Install with: pip install groq") from exc

        client = Groq(api_key=Config.GROQ_API_KEY, timeout=self.timeout_seconds)
        stt_kwargs = {
            "model": Config.VOICE_STT_MODEL,
            "temperature": 0,
            "response_format": "verbose_json",
            "prompt": (
                "The speaker is asking about medical symptoms, prescriptions, "
                "medicines, dosages, lab results, and follow-up health questions."
            ),
        }
        language = (Config.VOICE_STT_LANGUAGE or "").strip().lower()
        if language and language != "auto":
            stt_kwargs["language"] = language

        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                file=audio_file,
                **stt_kwargs,
            )

        text = getattr(response, "text", "") or ""
        detected_lang = getattr(response, "language", None)
        if detected_lang:
            print(f"[STT] detected_language={detected_lang} chars={len(text)}")
        if not text.strip():
            raise RuntimeError("No speech recognized from audio")
        return text

    def _speak_with_groq(self, text: str) -> Dict:
        if not Config.GROQ_API_KEY:
            return {"success": False, "error": "GROQ_API_KEY missing"}
        try:
            from groq import Groq
        except ImportError:
            return {"success": False, "error": "Groq SDK missing"}

        try:
            client = Groq(api_key=Config.GROQ_API_KEY, timeout=self.timeout_seconds)
            response = client.audio.speech.create(
                model=Config.VOICE_TTS_MODEL,
                voice=Config.VOICE_TTS_VOICE,
                input=text,
                response_format=Config.VOICE_TTS_FORMAT,
            )

            audio_bytes = b""
            if hasattr(response, "read"):
                audio_bytes = response.read()
            elif hasattr(response, "content"):
                audio_bytes = response.content
            elif isinstance(response, (bytes, bytearray)):
                audio_bytes = bytes(response)

            if not audio_bytes:
                return {"success": False, "error": "No audio generated by TTS provider"}

            return {
                "success": True,
                "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
                "mime_type": f"audio/{Config.VOICE_TTS_FORMAT}",
            }
        except Exception as exc:
            return {"success": False, "error": f"TTS provider error: {exc}"}

    def _speak_with_elevenlabs(self, text: str, language: str = "en") -> Dict:
        if not Config.ELEVENLABS_API_KEY:
            return {"success": False, "error": "ELEVENLABS_API_KEY missing"}
        try:
            import requests
        except ImportError:
            return {"success": False, "error": "'requests' library is required for ElevenLabs TTS"}

        voice_id = (Config.VOICE_TTS_VOICE or "21m00Tcm4TlvDq8ikWAM").strip()
        configured_model = (Config.VOICE_TTS_MODEL or "eleven_turbo_v2_5").strip()
        # ElevenLabs' English-only models can't speak Urdu/Hindi/etc.;
        # auto-upgrade to the multilingual model when caller requests non-English.
        if language and language != "en" and "multilingual" not in configured_model:
            model_id = "eleven_multilingual_v2"
        else:
            model_id = configured_model
        fmt_key = (Config.VOICE_TTS_FORMAT or "mp3").lower()
        output_format, mime_type = self.ELEVENLABS_FORMAT_MAP.get(
            fmt_key, ("mp3_44100_128", "audio/mpeg")
        )

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": Config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": mime_type,
        }
        params = {"output_format": output_format}
        body = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                params=params,
                json=body,
                timeout=self.timeout_seconds,
            )
        except Exception as exc:
            return {"success": False, "error": f"ElevenLabs network error: {exc}"}

        if response.status_code != 200:
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:200]
            return {
                "success": False,
                "error": f"ElevenLabs error {response.status_code}: {detail}",
            }

        audio_bytes = response.content
        if not audio_bytes:
            return {"success": False, "error": "ElevenLabs returned empty audio"}

        return {
            "success": True,
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "mime_type": mime_type,
        }

    GTTS_LANG_MAP = {
        "en": "en",
        "ur": "ur",
        "hi": "hi",
        "ar": "ar",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "tr": "tr",
        "fa": "fa",
        "bn": "bn",
        "pa": "pa",
    }

    def _speak_with_gtts(self, text: str, language: str = "en") -> Dict:
        """Fallback TTS using Google Translate (no API key required).

        Streams MP3 bytes for the requested language. Used when ElevenLabs
        is unavailable so non-English playback (e.g. Urdu) still works.
        """
        try:
            from gtts import gTTS
        except ImportError:
            return {
                "success": False,
                "error": "gTTS not installed. Add 'gTTS' to requirements.txt",
            }

        try:
            import io as _io
        except ImportError:  # pragma: no cover
            return {"success": False, "error": "io module unavailable"}

        lang_code = self.GTTS_LANG_MAP.get((language or "en").lower(), language or "en")
        try:
            tts = gTTS(text=text, lang=lang_code, slow=False)
            buffer = _io.BytesIO()
            tts.write_to_fp(buffer)
            audio_bytes = buffer.getvalue()
        except Exception as exc:
            return {"success": False, "error": f"gTTS error: {exc}"}

        if not audio_bytes:
            return {"success": False, "error": "gTTS returned empty audio"}

        return {
            "success": True,
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "mime_type": "audio/mpeg",
        }
