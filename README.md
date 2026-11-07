# CampusVoice
> **"Your Campus. Your Language. Your Voice."**

A multilingual, voice-first AI campus assistant designed to eliminate language barriers in higher education institutions, built for the **Great Indian AI Internship Challenge** organized by **Gnani AI** (Submission Target: November 10, 2026).

---

## 🏛️ 1. Problem Statement & Solution

### The Challenge
In higher education across India, administrative notifications, circulars, and campus guidelines are predominantly published in English. A significant segment of students whose primary languages are Telugu or Hindi encounter language barriers when navigating critical procedures regarding examinations, minimum attendance regulations, scholarship deadlines, and placement eligibility.

### The CampusVoice Solution
CampusVoice provides an accessible, voice-first artificial intelligence assistant allowing students to ask questions naturally in **Telugu (తెలుగు)**, **Hindi (हिन्दी)**, or **English**. 

The system leverages:
1. **Gnani Prisma STT:** State-of-the-art speech-to-text transcription specialized for Indian languages and code-switching.
2. **Campus Knowledge Retrieval Engine:** High-precision, grounded FAQ retrieval delivering verifiable campus guidelines without LLM hallucinations.
3. **Gnani Timbre TTS:** Natural, expressive voice synthesis in regional Indian accents, enabling a complete voice-in, voice-out assistant.

---

## 🌟 2. Key Features

- 🎙️ **Voice-First Multilingual Interaction:** Speak campus questions naturally in Telugu, Hindi, or English.
- 🇮🇳 **Code-Mixed Language Support:** Understands colloquial phrasing and English-Indic code-mixing (e.g., *"College events ఎప్పుడు ఉంటాయి?"*).
- 🎨 **Monsoon Editorial Design:** An authentic, warm editorial visual identity inspired by contemporary Indian publication design (Warm Ivory `#F3EFE5`, Deep Ink `#171B1A`, Forest Green `#174B43`, and Marigold `#E8B44A`).
- 🛡️ **Zero-Hallucination Retrieval:** Questions are matched against categorized campus FAQ data with clear source citations. Out-of-domain queries return a safe, grounded administrative fallback notice.
- 🔊 **Direct Audio Playback:** Text answers are spoken aloud using Gnani Timbre voices (`Suhana` for Telugu, `Nalini` for Hindi, `Kaveri` for English).
- 📜 **Session History:** Track and re-listen to previous questions and responses throughout the active session.
- 📱 **Fully Responsive & Accessible:** Designed with mobile touch targets, semantic typography, and WCAG-compliant color contrast.

---

## 🛠️ 3. Architecture & Tech Stack

```
               ┌────────────────────────────────────────────────────────┐
               │           React Frontend (Vite + Tailwind)             │
               │               "Monsoon Editorial UI"                   │
               └──────────────────────────┬─────────────────────────────┘
                                          │ Multipart Audio / JSON
                                          ▼
               ┌────────────────────────────────────────────────────────┐
               │              FastAPI Backend (Python 3.13)             │
               │   CORS Security • PyAV Transcoding • Error Handling    │
               └────────────┬──────────────────┬─────────────────┬──────┘
                            │                  │                 │
                            ▼                  ▼                 ▼
                 ┌───────────────────┐ ┌──────────────┐ ┌────────────────┐
                 │ Gnani Prisma STT  │ │ Campus FAQ   │ │ Gnani Timbre   │
                 │   v3.0 REST API   │ │  Knowledge   │ │  v2.5 TTS API  │
                 │ (Speech-to-Text)  │ │  Retrieval   │ │(Voice Synthesis│
                 └───────────────────┘ └──────────────┘ └────────────────┘
```

- **Frontend:** React 19, Vite 6, Tailwind CSS v3, Lucide React
- **Backend:** FastAPI, Uvicorn, HTTPX, Python-Multipart, PyAV (`av`), Python-Dotenv
- **Speech Intelligence:** Gnani AI Prisma (`prisma-v3.0`) and Timbre (`timbre-v2.5`)
- **Deployment Targets:** Vercel (Frontend SPA) + Render (FastAPI Web Service)

---

## 📁 4. Project Directory Structure

```
Campusvoice/
├── README.md                       # Complete documentation
├── .gitignore                      # Git exclusion rules (secrets & environments)
├── render.yaml                     # Render backend blueprint specification
├── backend/
│   ├── .env                        # Local environment variables (DO NOT COMMIT)
│   ├── .env.example                # Template with configuration keys
│   ├── main.py                     # FastAPI server with CORS & endpoints
│   ├── gnani_service.py            # Production client for Prisma & Timbre
│   ├── knowledge.py                # Normalized keyword & FAQ search engine
│   ├── requirements.txt            # Python dependencies (FastAPI, PyAV, etc.)
│   ├── data/
│   │   └── faqs.json               # 7 Multilingual FAQ categories (Sample Dataset)
│   ├── test_integration.py         # Phase 2 integration test suite
│   ├── test_prisma_direct.py       # Targeted STT & audio upload tests
│   └── test_phase5_suite.py        # 7-scenario automated QA test suite
└── frontend/
    ├── index.html                  # HTML5 template with DM Serif & Manrope fonts
    ├── package.json                # Frontend dependencies
    ├── vite.config.js              # Vite configuration
    ├── tailwind.config.js          # Monsoon Editorial theme tokens
    ├── vercel.json                 # Vercel SPA routing configuration
    ├── .env.example                # Frontend environment template
    └── src/
        ├── App.jsx                 # Main stateful application coordinator
        ├── App.css                 # Pulse and waveform animations
        ├── index.css               # Typography and CSS variables
        ├── components/
        │   ├── Header.jsx          # Brand header & connection status
        │   ├── LanguageSelector.jsx# Native-script language switcher
        │   ├── WelcomeSection.jsx  # Headline & clickable suggested questions
        │   ├── VoiceRecorder.jsx   # Centerpiece audio capture & progress
        │   ├── TranscriptCard.jsx  # Recognized speech card
        │   ├── AnswerCard.jsx      # Response card with source & sample label
        │   ├── AudioPlayer.jsx     # Custom audio player
        │   └── ConversationHistory.jsx # Session conversation history
        └── services/
            └── api.js              # Fetch client for backend endpoints
```

---

## 🚀 5. Local Installation & Execution

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Gnani AI Developer Account ([app.gnani.ai/voice](https://app.gnani.ai/voice))

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env and enter your GNANI_API_KEY

# Start Backend Server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install

# Start Vite Development Server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 6. Automated QA & Verification

To run the complete automated test suite verifying all 7 production scenarios:
```bash
cd backend
source venv/bin/activate
python3 test_phase5_suite.py
```

### Verified Test Matrix:
1. **Telugu Speech Query (`te-IN`):** Transcribes Telugu audio, searches FAQ notices, and synthesizes audio via voice `Suhana`.
2. **Hindi Speech Query (`hi-IN`):** Transcribes Hindi audio, retrieves regulations, and synthesizes audio via voice `Nalini`.
3. **English Speech Query (`en-IN`):** Transcribes English audio, retrieves guidelines, and synthesizes audio via voice `Kaveri`.
4. **Code-Mixed Query:** Transcribes mixed English-Indic inputs (e.g. *"College events ఎప్పుడు ఉంటాయి"*).
5. **Out-of-Domain Query:** Questions outside campus guidelines return a safe, grounded administrative fallback notice without hallucination.
6. **Empty Audio Validation:** Rejects 0-byte recordings with HTTP 400 and clear user guidance.
7. **Invalid Language Handling:** Validates supported language codes (`te`, `hi`, `en`).

---

## 🌐 7. Production Deployment Instructions

### Deploying Backend on Render
1. Create a **New Web Service** connected to your GitHub repository.
2. Set **Root Directory:** `backend`
3. Set **Runtime:** `Python 3`
4. Set **Build Command:** `pip install -r requirements.txt`
5. Set **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Configure Environment Variables in Render Dashboard:
   - `GNANI_API_KEY`: *(Your confidential Gnani AI API key)*
   - `PRISMA_MODEL`: `prisma-v3.0`
   - `TIMBRE_MODEL`: `timbre-v2.5`
   - `FRONTEND_URL`: `https://your-app.vercel.app`
   - `ALLOWED_ORIGINS`: `https://your-app.vercel.app`
7. Health Check Path: `/api/health`

### Deploying Frontend on Vercel
1. Import your GitHub repository into Vercel.
2. Set **Root Directory:** `frontend`
3. Framework Preset: **Vite**
4. Configure Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend-service.onrender.com`
5. Deploy.

---

## 🔒 8. Security & Data Policy

- **No Secrets in Bundles:** `GNANI_API_KEY` is strictly confined to the backend server environment and is never sent to the browser.
- **Strict CORS Protection:** Wildcard credentials are disabled; only trusted production domains and localhost are allowed.
- **In-Memory Transcoding:** Audio conversion via PyAV occurs entirely in memory without writing student audio to public disk.
- **Sample Dataset Transparency:** Sample FAQ records are explicitly tagged as `Sample FAQ Dataset` in the interface to distinguish demonstration records from official university notices.

---

## 📄 9. License & Challenge Submission
Created by solo developer for the **Great Indian AI Internship Challenge** organized by **Gnani AI** (Submission Deadline: November 10, 2026).
