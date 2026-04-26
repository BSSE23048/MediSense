# MediSense AI

> **Your personal AI-powered medical companion — turn confusing reports into clear answers, in any language.**

MediSense AI lets a patient upload a medical report (PDF or image), and within seconds it produces a plain-language summary, identifies prescribed medicines, suggests locally-available alternatives (Pakistan-first), answers follow-up questions in chat, and can read everything aloud — including in **Urdu**.

It is a full-stack hackathon project built around four ideas:

1. **Bridge the doctor↔patient communication gap** with reliable, grounded AI summaries.
2. **Treat every report as long-term memory**, so the AI gets smarter about each patient over time.
3. **Be useful in the real Pakistan healthcare context**, not a generic Western tool — local medicine catalog, Urdu voice, low bandwidth friendly.
4. **Stay safe** — every output is grounded in the user's report and a curated medical knowledge base, with explicit disclaimers, red-flag triage, and a doctor handoff path.

---

## Table of Contents

- [Demo Walkthrough](#demo-walkthrough)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Tesseract OCR](#tesseract-ocr-required-for-image-reports)
- [Configuration Reference](#configuration-reference)
- [API Reference](#api-reference)
- [Voice Assistant](#voice-assistant)
- [Medicine Intelligence](#medicine-intelligence)
- [RAG & Report Memory](#rag--report-memory)
- [Authentication](#authentication)
- [Testing & CI](#testing--ci)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

---

## Demo Walkthrough

A typical user journey:

1. **Sign up / log in** → all reports are tied to the user account.
2. **Upload a prescription or lab report** (PDF / PNG / JPG).
3. **OCR pipeline** extracts text (Tesseract → EasyOCR fallback).
4. **LLM (Groq Llama-3.3 70B)** summarizes for both patient and doctor, lists key findings, medications, and red-flag warnings.
5. **Medicine cards** appear under the summary — click any medicine to see ingredients, uses, and Pakistan-market alternatives sourced from the local catalog (and OpenFDA for international fallback).
6. **Read Aloud** in English or Urdu using the multilingual TTS pipeline (ElevenLabs → browser fallback).
7. **Ask follow-ups** in the symptoms chat — every answer is grounded in your saved reports + medical RAG context.
8. **My Reports** shows the longitudinal history; the AI uses it as context for new symptom analyses.

---

## Key Features

### Core medical pipeline
- **OCR ingestion** of PDF and image medical reports (Tesseract + optional EasyOCR fallback)
- **Patient + Doctor summaries** via LLM with Pydantic-validated structured output
- **Key findings, medications, critical warnings, follow-up plan** as separate fields
- **Symptom checker** that returns possible conditions, urgency, and tailored recommendations

### Memory & context
- **User accounts** with hashed passwords + signed-token auth
- **Report memory** — each summary is persisted to SQLite (extracted text + structured summary only, never the original file)
- **Longitudinal RAG** — symptom analyses and chat answers automatically pull in the user's recent reports
- **Multi-turn chat threads** with per-thread message history

### Medicine intelligence
- **Pakistan-first local catalog** (Panadol, Augmentin, Brufen, Crocin, Disprol, Calpol, Flagyl, Septran, Ventolin, etc.) with generic name, ingredients, uses, alternatives
- **OpenFDA fallback** for international/uncatalogued drugs
- **Click-to-expand medicine cards** in the report view
- **Same-formula alternatives** suggested for cost/availability concerns

### Voice assistant
- **Speech-to-text** for symptoms and follow-up questions (Groq Whisper Large v3 Turbo, language-locked to English by default to avoid mis-detection)
- **Text-to-speech** in **English and Urdu** with automatic translation via the LLM
- **Cloud TTS** (ElevenLabs multilingual) with **browser-native** SpeechSynthesis fallback so the demo never breaks
- **Localized disclaimers** added automatically (English / Urdu / Hindi / Arabic)

### Safety & UX
- **Explicit disclaimers** on every AI output ("informational only, not a diagnosis")
- **Source/citation surfacing** so users can see what was used to answer
- **Graceful degradation** — every external dependency (Tesseract, Groq, ElevenLabs, ChromaDB, EasyOCR) has a fallback path so the app keeps working
- **CI workflow** runs on push (GitHub Actions)

---

## Architecture

```
┌─────────────────────────┐         ┌────────────────────────────────────────┐
│        Angular 19        │  HTTPS  │              Flask Backend             │
│   (Standalone, no NgM.)  │ ──────▶ │  /api/auth   /api/ocr     /api/voice  │
│                         │         │  /api/summarize  /api/reports          │
│  Pages: Home / Report   │         │  /api/symptom-check  /api/chat/...     │
│  Symptoms / My-Reports  │         └─────────────┬──────────────────────────┘
│  Auth / About           │                       │
│                         │              ┌────────┴─────────┐
│  Services:              │              │                  │
│   - api.service         │       ┌──────▼──────┐    ┌──────▼──────┐
│   - voice-assistant     │       │  Services   │    │   Routes    │
└─────────────────────────┘       │  (business) │    │ (Flask BP)  │
                                  └──────┬──────┘    └─────────────┘
                                         │
        ┌────────────────────────────────┼─────────────────────────────────────┐
        │                                │                                     │
   ┌────▼─────┐  ┌────────────┐  ┌───────▼───────┐  ┌───────────┐  ┌──────────▼─┐
   │   OCR    │  │    LLM     │  │     RAG       │  │ Medicine  │  │   Voice    │
   │ Tesseract│  │ Groq Llama │  │  Knowledge +  │  │  Catalog  │  │ Groq STT + │
   │ EasyOCR  │  │  Gemini /  │  │  User reports │  │ + OpenFDA │  │ ElevenLabs │
   │          │  │  OpenAI    │  │   (Chroma)    │  │           │  │            │
   └──────────┘  └──────┬─────┘  └───────────────┘  └───────────┘  └────────────┘
                        │
                  ┌─────▼─────┐
                  │  SQLite   │
                  │  users    │
                  │  reports  │
                  │  threads  │
                  │  messages │
                  └───────────┘
```

### Request flow examples

**Upload a report**

```
PDF/JPG → /api/ocr ─→ extracted text
       → /api/summarize ─→ {patient_summary, doctor_summary, medications, ...}
                            │
                            ├─ stored in SQLite (reports table) for the user
                            └─ medicines piped through MedicineService
```

**Ask a follow-up in chat**

```
question → /api/chat/thread/<id>/ask
            │
            ├─ RAGService.build_context_bundle(report_id, user_id)
            │    ├── medical knowledge KB
            │    ├── current report summary
            │    └── prior chat messages
            │
            └─ LLMService.answer_followup(question, context_bundle)
                  └── stored back as a message
```

**Voice "Read Aloud" in Urdu**

```
text → /api/voice/speak {language: "ur"}
        │
        ├─ LLMService.translate_text(text, "ur")  ← Groq Llama
        ├─ disclaimer (Urdu) appended
        ├─ ElevenLabs eleven_multilingual_v2  → audio  (preferred)
        └─ if cloud fails → returns text_used so the
           browser SpeechSynthesis can speak it with ur-PK
```

---

## Tech Stack

| Layer        | Technology |
|--------------|------------|
| Frontend     | Angular 19 (standalone components), TypeScript, RxJS, MediaRecorder API, SpeechSynthesis |
| Backend      | Python 3.11, Flask 3, Flask-CORS, Gunicorn |
| Auth         | `werkzeug.security` (PBKDF2), `itsdangerous` URLSafeTimedSerializer (Bearer tokens) |
| LLM          | Groq Llama-3.3 70B (default), Google Gemini, OpenAI — via LangChain or direct SDK |
| RAG          | LangChain + sentence-transformers (`all-MiniLM-L6-v2`) + ChromaDB (optional) |
| OCR          | Tesseract (primary), EasyOCR (optional fallback), PyPDF2 for PDFs |
| Storage      | SQLite (users / reports / chat_threads / chat_messages) |
| Medicine     | Local Pakistan catalog (in-process) + OpenFDA REST API |
| Voice STT    | Groq Whisper Large v3 Turbo (language-locked to English by default) |
| Voice TTS    | ElevenLabs (`eleven_turbo_v2_5` / `eleven_multilingual_v2`) → browser SpeechSynthesis fallback |
| CI           | GitHub Actions |

---

## Project Structure

```
Shelby-Stack/
├── Backend/
│   ├── app.py                     # Flask entrypoint, blueprint registration, CORS
│   ├── config.py                  # All environment-driven config (LLM, voice, RAG, OCR)
│   ├── requirements.txt
│   ├── env.example                # Copy to .env and fill in keys
│   ├── routes/
│   │   ├── auth.py                # /api/auth/register, /api/auth/login
│   │   ├── ocr.py                 # /api/ocr
│   │   ├── summarize.py           # /api/summarize  (saves report, extracts medicines)
│   │   ├── symptoms.py            # /api/symptom-check  (uses report + RAG context)
│   │   ├── reports.py             # /api/reports, /api/reports/:id, /api/medicines/:name
│   │   ├── chat.py                # /api/chat/thread, /api/chat/thread/:id/ask, ...
│   │   └── voice.py               # /api/voice/transcribe, /api/voice/speak
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── storage_service.py     # SQLite layer (CRUD)
│   │   ├── report_service.py
│   │   ├── conversation_service.py
│   │   ├── medicine_service.py    # Pakistan catalog + OpenFDA
│   │   ├── ocr_service.py
│   │   ├── llm_service.py         # LangChain + direct Groq, JSON-safe extraction, translate_text
│   │   ├── rag_service.py         # build_context_bundle()
│   │   ├── voice_service.py       # Groq STT + ElevenLabs / Groq TTS
│   │   └── text_cleaner.py
│   ├── utils/
│   │   ├── auth_helpers.py
│   │   ├── pdf_reader.py
│   │   └── formatters.py
│   ├── database/
│   │   └── dataset_loader.py      # Medical knowledge KB loader
│   └── test_new_flows.py          # Auth + report + chat smoke tests
├── Frontend/
│   ├── src/app/
│   │   ├── app.routes.ts          # /, /report, /symptoms, /auth, /my-reports, /about
│   │   ├── components/            # navbar, footer, loader, text-slider
│   │   ├── pages/
│   │   │   ├── home/
│   │   │   ├── report/            # OCR + summary + medicine cards + read aloud
│   │   │   ├── symptoms/          # Symptom analysis + follow-up chat + voice
│   │   │   ├── my-reports/        # Saved reports list & detail
│   │   │   ├── auth/              # Login / register
│   │   │   └── about/
│   │   └── services/
│   │       ├── api.service.ts            # All HTTP calls
│   │       └── voice-assistant.service.ts # Mic capture, STT, TTS (cloud + browser)
│   └── angular.json
├── Research/                      # Reference notebooks / dataset notes
├── .github/workflows/ci.yml       # CI: lint + tests
└── README.md (this file)
```

---

## Quick Start

> **Prerequisites:** Python 3.11+, Node.js 20+, Tesseract OCR (system install). On Windows, PowerShell is fine.

Clone the repo:

```bash
git clone https://github.com/<your-fork>/Shelby-Stack.git
cd Shelby-Stack
```

### Backend Setup

```bash
cd Backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

cp env.example .env       # then edit .env with your keys
# Required at minimum: GROQ_API_KEY  (or GEMINI_API_KEY)
# Optional but recommended: ELEVENLABS_API_KEY (for studio-quality voice)

# Run the API
python app.py
# → http://localhost:5000
# → Health check: http://localhost:5000/api/health
```

### Frontend Setup

```bash
cd ../Frontend
npm install
npm start
# → http://localhost:4200
```

The frontend already points at `http://localhost:5000/api`. Adjust in `Frontend/src/environments/environment.ts` if needed.

### Tesseract OCR (required for image reports)

| OS       | Install |
|----------|---------|
| Windows  | Download installer from [tesseract-ocr/tesseract releases](https://github.com/tesseract-ocr/tesseract). Default path `C:\Program Files\Tesseract-OCR\tesseract.exe` is auto-detected. Override with `TESSERACT_CMD` in `.env`. |
| macOS    | `brew install tesseract` |
| Linux    | `sudo apt-get install tesseract-ocr` |

Without Tesseract, OCR will fail with a clear error message; PDFs that contain selectable text still work via PyPDF2.

---

## Configuration Reference

All configuration is read from `Backend/.env` (see `Backend/env.example`).

### Core

| Variable          | Default                  | Description |
|-------------------|--------------------------|-------------|
| `SECRET_KEY`      | `dev-secret-key-...`     | Flask + auth token signing key. **Rotate in production.** |
| `FLASK_ENV`       | `development`            | Set to `production` to disable debug + reloader |
| `PORT`            | `5000`                   | Backend port |
| `CORS_ORIGINS`    | `*`                      | Comma-separated list, or `*` for development |

### LLM

| Variable          | Default                       | Description |
|-------------------|-------------------------------|-------------|
| `LLM_PROVIDER`    | `groq`                        | `groq` / `gemini` / `openai` |
| `GROQ_API_KEY`    | —                             | Required if provider = groq |
| `GROQ_MODEL`      | `llama-3.3-70b-versatile`     | Used for summary, symptom, chat, translation |
| `GEMINI_API_KEY`  | —                             | Required if provider = gemini |
| `GEMINI_MODEL`    | `gemini-2.5-flash`            | |
| `OPENAI_API_KEY`  | —                             | Required if provider = openai |

### Voice

| Variable               | Default                          | Description |
|------------------------|----------------------------------|-------------|
| `VOICE_STT_PROVIDER`   | `groq`                           | Speech-to-text provider |
| `VOICE_STT_MODEL`      | `whisper-large-v3-turbo`         | Groq Whisper variant |
| `VOICE_STT_LANGUAGE`   | `en`                             | ISO-639-1 or `auto` for autodetect (not recommended) |
| `VOICE_TTS_PROVIDER`   | `elevenlabs`                     | TTS provider (`elevenlabs` / `groq`) |
| `VOICE_TTS_MODEL`      | `eleven_turbo_v2_5`              | Auto-upgrades to `eleven_multilingual_v2` for non-English |
| `VOICE_TTS_VOICE`      | `21m00Tcm4TlvDq8ikWAM` (Rachel)  | ElevenLabs voice ID. **Note:** library voices require a paid ElevenLabs plan |
| `VOICE_TTS_FORMAT`     | `mp3`                            | `mp3` / `mp3_high` / `wav` / `ogg` |
| `VOICE_TIMEOUT_SECONDS`| `30`                             | HTTP timeout for STT/TTS |
| `VOICE_MAX_AUDIO_MB`   | `8`                              | Reject uploads larger than this |
| `VOICE_MAX_TTS_CHARS`  | `1200`                           | Truncate text passed to TTS |
| `ELEVENLABS_API_KEY`   | —                                | Required for cloud TTS; omit to use browser-only TTS |

### OCR / RAG

| Variable          | Default                                 | Description |
|-------------------|-----------------------------------------|-------------|
| `TESSERACT_CMD`   | `C:\Program Files\Tesseract-OCR\tesseract.exe` (Win) / `/usr/bin/tesseract` (Linux) | Override Tesseract binary path |
| `USE_EASYOCR`     | `false`                                 | Enable EasyOCR fallback when Tesseract fails |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2`                      | sentence-transformers model |
| `CHUNK_SIZE`      | `500`                                   | KB chunking |
| `CHUNK_OVERLAP`   | `50`                                    | |
| `TOP_K_RESULTS`   | `5`                                     | RAG top-k |

---

## API Reference

All endpoints live under `/api`. Endpoints that touch a user's data require a Bearer token in the `Authorization` header.

### Auth

```
POST /api/auth/register   { "email": "...", "password": "..." }
POST /api/auth/login      { "email": "...", "password": "..." }
→ { "success": true, "user_id": 1, "email": "...", "token": "..." }
```

### OCR

```
POST /api/ocr             multipart-form-data: file=<pdf|image>
→ { "success": true, "extracted_text": "...", "confidence": 0.87 }
```

### Summarize

```
POST /api/summarize       (auth optional)
{
  "text": "<extracted text>",
  "report_title": "Lab Report.pdf"
}
→ {
  "success": true,
  "patient_summary": "...",
  "doctor_summary": "...",
  "key_findings": [...],
  "medications": [...],
  "medicine_details": [{ "name": "Panadol", "generic_name": "Paracetamol", ... }],
  "critical_warnings": [...],
  "follow_up": "...",
  "saved_report_id": 12        // when user is authenticated
}
```

### Reports (auth required)

```
GET    /api/reports                  → list of {id, report_title, created_at}
GET    /api/reports/:id              → full saved report including summary
GET    /api/medicines/:name          → { medicine, alternatives }
```

### Symptom Checker

```
POST /api/symptom-check  (auth optional — adds report context when authenticated)
{ "symptoms": "fever, cough, body aches for 3 days" }
→ {
  "possible_conditions": [{ "name": "...", "probability": "...", "description": "..." }],
  "urgency": "low|medium|high",
  "explanation": "...",
  "recommendations": [...],
  "context_sources": ["medical-kb", "user-report:12"],
  "seek_immediate_care_if": [...]
}
```

### Chat (auth required)

```
POST /api/chat/thread                          { "report_id": 12 (optional) }
GET  /api/chat/thread/:tid/messages
POST /api/chat/thread/:tid/ask                 { "question": "Should I take this with food?" }
```

### Voice

```
POST /api/voice/transcribe   multipart-form-data: audio=<webm|wav|mp3|m4a|ogg>
→ { "success": true, "transcript": "..." }

POST /api/voice/speak
{
  "text": "...",
  "include_disclaimer": true,
  "language": "en"   // or "ur", "hi", "ar", ...
}
→ {
  "success": true|false,
  "audio_base64": "...",      // when cloud TTS succeeds
  "mime_type": "audio/mpeg",
  "text_used": "<translated + disclaimer>",  // always present, used for browser fallback
  "language": "ur"
}
```

> The `/api/voice/speak` endpoint **always returns 200** — `success:false` simply means cloud TTS was unavailable, but the translated `text_used` is still provided so the client can use browser SpeechSynthesis.

---

## Voice Assistant

The voice layer has two ends:

### Backend
- **STT** uses Groq's hosted Whisper (`whisper-large-v3-turbo`) with `language="en"` locked by default — set `VOICE_STT_LANGUAGE=auto` to let Whisper guess (not recommended for short or noisy clips). A medical-domain prompt biases decoding toward terms like "panadol", "augmentin", "fever", etc.
- **TTS** prefers ElevenLabs. When `language != en` it auto-switches the model to `eleven_multilingual_v2`. The text is first **translated by the LLM** (`LLMService.translate_text`) preserving numbers, dosages, and brand names verbatim. Localized disclaimers are appended automatically.

### Frontend
- `voice-assistant.service.ts` records audio via `MediaRecorder` (audio/webm), uploads it to `/api/voice/transcribe`, and streams the result back into the form.
- For playback, it tries cloud TTS first; if cloud is unavailable it uses the browser's `SpeechSynthesis` API with `utterance.lang = ur-PK` (or whichever language the user picked). Voice picking matches both `voice.lang` and `voice.name` so it correctly finds Microsoft Asad / Uzma Urdu voices on Windows.
- Console logs `[voice] selected="..."` so you can see which engine is speaking.

### Notes on Urdu specifically
- **Best quality:** ElevenLabs paid plan with `eleven_multilingual_v2`.
- **Free path:** Windows + browser. Install **Settings → Time & Language → Add language → Urdu (Pakistan) → Speech (Download)**, then refresh the browser. You'll get `Microsoft Asad / Uzma — Urdu (Pakistan)` voices.

---

## Medicine Intelligence

Powered by `services/medicine_service.py`. Resolution order for `GET /api/medicines/<name>`:

1. **Local Pakistan catalog** (covers ~10 of the most-prescribed brand names: Panadol, Calpol, Augmentin, Brufen, Disprol, Crocin, Flagyl, Septran, Ventolin, Cipro, etc.) — returns generic name, ingredients, uses, and same-formula alternatives that are widely available in Pakistan.
2. **OpenFDA fallback** (`https://api.fda.gov/drug/label.json?search=...`) for international and uncatalogued drugs.
3. **Graceful "not found"** when both miss, with a hint to consult the prescribing physician.

When `/api/summarize` extracts a medicine list from a report, each medicine is enriched with this data and bundled in `medicine_details` so the frontend can render rich medicine cards immediately — no second click required.

---

## RAG & Report Memory

Two layers are merged in every reasoning call:

1. **Static medical knowledge base** — chunked + embedded into ChromaDB (or in-memory cosine fallback) using sentence-transformers `all-MiniLM-L6-v2`.
2. **User memory** — recent reports for the authenticated user are loaded from SQLite and included as context (`user-report:<id>` source tag).

`RAGService.build_context_bundle(question, user_id, report_id, thread_id)` returns a single `context` string + a list of `sources`, which is then injected into:
- `LLMService.analyze_symptoms`
- `LLMService.answer_followup`

This is what powers the "What does my last lipid panel mean?" or "Should I worry about my BP given my history?" experience.

---

## Authentication

- **Storage:** SQLite `users` table. Passwords are hashed with `werkzeug.security.generate_password_hash` (PBKDF2-SHA256).
- **Tokens:** Generated by `itsdangerous.URLSafeTimedSerializer` and signed with `SECRET_KEY`. Sent as `Authorization: Bearer <token>`.
- **Verification:** `utils/auth_helpers.py::verify_token_payload` is called by every protected route.
- **Token TTL:** 7 days by default (configurable in `auth_service.py`).

---

## Testing & CI

```bash
cd Backend
python -m unittest test_new_flows.py
```

The smoke test covers register → login → save report → list reports → create chat thread → ask follow-up. It uses an isolated temp SQLite file so it won't pollute your dev database.

CI runs the same flow on every push via `.github/workflows/ci.yml`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Summary comes back as a fallback ("Fallback summary mode is active...") | LLM API key missing or invalid | Check `GROQ_API_KEY` (or your chosen provider) in `.env`, restart backend |
| `/api/ocr` returns 500 with "Tesseract not installed" | Missing system Tesseract | Install Tesseract or set `TESSERACT_CMD` |
| `/api/voice/speak` returns `success:false` with `paid_plan_required` | ElevenLabs free tier blocks library voices | Either upgrade ElevenLabs plan, swap to a personal voice ID, or rely on browser TTS (still works) |
| STT transcribes in the wrong language | Whisper auto-detection mis-fires on short clips | Keep `VOICE_STT_LANGUAGE=en` (default) |
| Read-aloud speaks Urdu text with English pronunciation | No Urdu speech voice on the OS | Install Windows Urdu (Pakistan) speech pack and reload the browser |
| `Cannot connect to the server` from the Angular app | Backend isn't running on port 5000 | `python Backend/app.py` and confirm http://localhost:5000/api/health |

---

## Roadmap

Things we'd love to add next:

- [ ] **Specialized medical LLM** (Med-PaLM 2 / BioMistral) for grounded clinical reasoning
- [ ] **Red-flag triage panel** — pre-canned vital-sign / lab thresholds with explanations
- [ ] **Medication conflict checker** across the user's report history
- [ ] **Timeline view** of patient reports with delta highlighting
- [ ] **Doctor handoff export** — one-click PDF that re-folds the AI summary back into clinical language
- [ ] **Mobile-responsive PWA** + offline mode for low-connectivity rural use

---

## License

MIT — see [`LICENSE`](LICENSE) (add one if missing).

> ⚠️ **Disclaimer:** MediSense AI is an educational/assistive tool. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified physician with any questions you may have regarding a medical condition.
