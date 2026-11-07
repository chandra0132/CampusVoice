# CampusVoice
> **Your Campus. Your Language. Your Voice.**

A multilingual, voice-first AI campus assistant built for the **Great Indian AI Internship Challenge** organized by **Gnani AI**.

---

## 🌟 Overview

CampusVoice breaks language barriers in higher education institutions by enabling students to interact with campus services in **Telugu**, **Hindi**, and **English** using natural speech.

Students can ask about:
- College events & technical fests
- Examination schedules & hall ticket issuance
- Attendance requirements & condonation rules
- Placement drives & eligibility criteria
- Academic curriculum & library timings
- Departments & student clubs

---

## 🛠️ Architecture & Tech Stack

```
React Frontend (Vite + Tailwind CSS + Lucide Icons)
        │
        ▼ (Multipart Audio + Language Code)
FastAPI Backend (Python 3.13 + Uvicorn + HTTPX)
        │
        ├────► Gnani Prisma STT (Speech-to-Text Transcription)
        │
        ├────► Campus Knowledge Base (FAQ Retrieval Engine)
        │
        └────► Gnani Timbre TTS (Voice Synthesis)
                │
                ▼
      Audio Playback & Rich Contextual Display
```

- **Frontend:** React 19, Vite 6, Tailwind CSS, Lucide React
- **Backend:** FastAPI, Uvicorn, HTTPX, Python-Multipart, Python-Dotenv
- **AI Speech Pipeline:** Gnani AI Prisma (STT) & Timbre (TTS)
- **Knowledge Retrieval:** Categorized JSON FAQ Store with Multilingual Keyword Matching

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- Gnani AI Developer Account & API Key ([Gnani AI Console](https://app.gnani.ai/voice))

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env and enter your GNANI_API_KEY

# Start Backend Server
uvicorn main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the application at: `http://localhost:5173`

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and identity |
| `GET` | `/api/health` | Backend and Gnani service health |
| `POST` | `/api/ask` | Voice-to-voice multilingual assistant endpoint |

---

## 🛡️ License & Submission
Built for the **Great Indian AI Internship Challenge** (Submission Deadline: November 10, 2026).
Project created by solo developer adhering to strict production guidelines.
