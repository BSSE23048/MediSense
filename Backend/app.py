"""
MediSense AI - Main Flask Application
Unified Medical Report Summarizer & Symptom Checker Backend
"""

from flask import Flask
from flask_cors import CORS
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS with additional headers
cors_origins = app.config['CORS_ORIGINS']
if cors_origins == ['*']:
    # Allow all origins (for development/testing)
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         allow_headers=['Content-Type', 'Authorization', 'Accept'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=False)
else:
    # Allow specific origins
    CORS(app, 
         origins=cors_origins,
         allow_headers=['Content-Type', 'Authorization', 'Accept'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=False)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHROMA_DB_PATH'], exist_ok=True)
os.makedirs(app.config['EMBEDDINGS_PATH'], exist_ok=True)

# Register blueprints
from routes.summarize import summarize_bp
from routes.symptoms import symptoms_bp
from routes.ocr import ocr_bp
from routes.auth import auth_bp
from routes.reports import reports_bp
from routes.chat import chat_bp
from routes.voice import voice_bp

app.register_blueprint(summarize_bp, url_prefix='/api')
app.register_blueprint(symptoms_bp, url_prefix='/api')
app.register_blueprint(ocr_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(voice_bp, url_prefix='/api')

@app.route('/')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'MediSense AI Backend',
        'version': '1.0.0'
    }, 200

@app.route('/api/health')
def api_health():
    """API health check endpoint"""
    return {
        'status': 'healthy',
        'endpoints': {
            'ocr': '/api/ocr',
            'summarize': '/api/summarize',
            'symptom-check': '/api/symptom-check',
            'auth-register': '/api/auth/register',
            'auth-login': '/api/auth/login',
            'reports': '/api/reports',
            'chat-thread': '/api/chat/thread',
            'voice-transcribe': '/api/voice/transcribe',
            'voice-speak': '/api/voice/speak'
        }
    }, 200

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG if app.config['DEBUG'] else logging.INFO)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

