# MediSense AI - Backend Setup Guide

## 📋 Overview

This is the Flask backend for MediSense AI, providing APIs for:

- Medical report OCR and text extraction
- AI-powered report summarization (using LangChain + Gemini)
- Symptom checking with RAG-based analysis

**✨ New:** Summarization module now uses LangChain with structured outputs for better accuracy and reliability!

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Tesseract OCR (for image text extraction)
- API key for LLM service (Gemini recommended)

### Installation Steps

#### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Install Tesseract OCR

**Windows (Quick Setup):**

Run the helper script:

```powershell
powershell -ExecutionPolicy Bypass -File install_tesseract_windows.ps1
```

Or manually:

- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR`
- Or set `TESSERACT_CMD` in `.env` file

**Note:** See `TESSERACT_SETUP.md` for detailed instructions.

**Linux:**

```bash
sudo apt-get install tesseract-ocr
```

**Mac:**

```bash
brew install tesseract
```

#### 4. Configure Environment Variables

Copy `env.example` to `.env`:

```bash
copy env.example .env  # Windows
# or
cp env.example .env    # Linux/Mac
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

**Get Gemini API Key:**

1. Visit: https://makersuite.google.com/app/apikey
2. Create a new API key (free tier available)

#### 5. Initialize RAG Database (Optional)

```bash
python database/dataset_loader.py
```

#### 6. Test Summarization (Optional)

```bash
python test_summarization.py
```

This will verify that LangChain and Gemini are working correctly.

#### 7. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## 📁 Project Structure

```
Backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── routes/               # API route handlers
│   ├── ocr.py           # OCR endpoints
│   ├── summarize.py     # Summarization endpoints
│   └── symptoms.py      # Symptom checking endpoints
├── services/            # Business logic
│   ├── ocr_service.py   # OCR processing
│   ├── llm_service.py  # LLM interactions
│   ├── rag_service.py  # RAG pipeline
│   └── text_cleaner.py # Text preprocessing
├── utils/               # Utility functions
│   ├── pdf_reader.py   # PDF text extraction
│   └── formatters.py   # Response formatting
├── database/            # RAG database
│   ├── vectorstore/    # ChromaDB storage
│   └── dataset_loader.py # Initialize knowledge base
└── uploads/             # Temporary file storage
```

## 🔌 API Endpoints

### Health Check

```
GET /
GET /api/health
```

### OCR Text Extraction

```
POST /api/ocr
Content-Type: multipart/form-data
Body: file (PDF or image)
```

### Report Summarization

```
POST /api/summarize
Content-Type: application/json
Body: { "text": "medical report text..." }
```

### Symptom Analysis

```
POST /api/symptom-check
Content-Type: application/json
Body: { "symptoms": "fever, cough, headache" }
```

## ⚙️ Configuration Options

### LLM Providers

- **Gemini** (Recommended - Free tier available)
- **OpenAI GPT** (Requires API key)
- **Groq** (Fast, free tier available)

Set `LLM_PROVIDER` in `.env` file.

### OCR Options

- **Tesseract** (Default, requires installation)
- **EasyOCR** (Set `USE_EASYOCR=true` in `.env`)

## 🧪 Testing

Test the API endpoints using curl or Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Summarize (example)
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient presents with elevated blood glucose..."}'
```

## 🐛 Troubleshooting

### Tesseract Not Found

- Windows: Set `TESSERACT_CMD` in `.env` to full path
- Linux/Mac: Ensure Tesseract is in PATH

### Import Errors

- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### API Key Issues

- Verify API key is set in `.env` file
- Check API key is valid and has credits/quota

### ChromaDB Issues

- Delete `database/vectorstore/` folder and reinitialize
- Run `python database/dataset_loader.py` again

## 📝 Notes

- Uploaded files are automatically deleted after processing
- RAG database is optional but recommended for better symptom analysis
- For production, change `SECRET_KEY` and set `FLASK_ENV=production`
