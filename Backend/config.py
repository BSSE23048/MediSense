import os
import platform
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for MediSense AI Backend"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # Database Configuration
    CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'vectorstore')
    EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), 'database', 'embeddings')
    
    # OCR Configuration
    # Auto-detect Tesseract path based on platform
    if platform.system() == 'Windows':
        TESSERACT_CMD = os.environ.get('TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    else:
        # For Linux (Render, PythonAnywhere, Railway, etc.)
        TESSERACT_CMD = os.environ.get('TESSERACT_CMD', '/usr/bin/tesseract')
    USE_EASYOCR = os.environ.get('USE_EASYOCR', 'false').lower() == 'true'
    
    # LLM Configuration
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'gemini')  # gemini, openai, groq
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-pro')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    # Voice Assistant Configuration
    VOICE_STT_PROVIDER = os.environ.get('VOICE_STT_PROVIDER', 'groq')
    VOICE_STT_MODEL = os.environ.get('VOICE_STT_MODEL', 'whisper-large-v3-turbo')
    VOICE_STT_LANGUAGE = os.environ.get('VOICE_STT_LANGUAGE', 'en')
    VOICE_TTS_PROVIDER = os.environ.get('VOICE_TTS_PROVIDER', 'elevenlabs')
    VOICE_TTS_MODEL = os.environ.get('VOICE_TTS_MODEL', 'eleven_turbo_v2_5')
    VOICE_TTS_VOICE = os.environ.get('VOICE_TTS_VOICE', '21m00Tcm4TlvDq8ikWAM')
    VOICE_TTS_FORMAT = os.environ.get('VOICE_TTS_FORMAT', 'mp3')
    VOICE_TIMEOUT_SECONDS = int(os.environ.get('VOICE_TIMEOUT_SECONDS', '30'))
    VOICE_MAX_AUDIO_MB = int(os.environ.get('VOICE_MAX_AUDIO_MB', '8'))
    VOICE_MAX_TTS_CHARS = int(os.environ.get('VOICE_MAX_TTS_CHARS', '1200'))
    
    # RAG Configuration
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 500))
    CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', 50))
    TOP_K_RESULTS = int(os.environ.get('TOP_K_RESULTS', 5))
    
    # CORS Configuration
    # For production, set CORS_ORIGINS in environment variables
    # For development/testing, you can use '*' to allow all origins
    cors_origins_env = os.environ.get('CORS_ORIGINS', '*')  # Default to '*' for easier setup
    if cors_origins_env == '*':
        CORS_ORIGINS = ['*']
    else:
        # Split by comma and strip whitespace
        CORS_ORIGINS = [origin.strip() for origin in cors_origins_env.split(',')]
    
    # Cloudinary Configuration (Optional)
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

