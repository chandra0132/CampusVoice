import os
import base64
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

try:
    from backend.gnani_service import gnani_service, normalize_lang_code
    from backend.knowledge import knowledge_base
except ImportError:
    from gnani_service import gnani_service, normalize_lang_code
    from knowledge import knowledge_base

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("campusvoice.api")

app = FastAPI(
    title="CampusVoice API",
    description="Multilingual Voice-First Campus AI Assistant powered by Gnani AI (Prisma STT & Timbre TTS)",
    version="1.0.0"
)

# Hardened Production CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")

trusted_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
]
if frontend_url and frontend_url not in trusted_origins:
    trusted_origins.append(frontend_url)
if allowed_origins_env:
    for o in allowed_origins_env.split(","):
        clean_o = o.strip().rstrip("/")
        if clean_o and clean_o not in trusted_origins:
            trusted_origins.append(clean_o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=trusted_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Safely permits Vercel production and preview URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_LANGUAGES = {"te", "hi", "en", "te-in", "hi-in", "en-in"}

class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize into speech")
    language: str = Field("en", description="Target language: te, hi, or en")
    voice: Optional[str] = Field(None, description="Optional custom voice name")

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint returning API status and project identity."""
    return {
        "project": "CampusVoice",
        "tagline": "Your Campus. Your Language. Your Voice.",
        "status": "online",
        "version": "1.0.0",
        "pipeline": "Gnani Prisma STT -> Campus Knowledge Base -> Gnani Timbre TTS"
    }

@app.get("/api/health", tags=["Status"])
async def health_check():
    """
    Check backend health and verify Gnani service configuration
    without exposing sensitive API credentials.
    """
    gnani_status = gnani_service.get_status()
    return {
        "status": "healthy",
        "gnani": gnani_status,
        "knowledge_base": {
            "loaded_faqs": len(knowledge_base.faqs),
            "status": "ready" if len(knowledge_base.faqs) > 0 else "empty"
        }
    }

@app.post("/api/transcribe", tags=["Speech"])
async def transcribe_audio(
    audio: UploadFile = File(..., description="Multipart audio recording (WAV, MP3, WebM, etc.)"),
    language: str = Form("en", description="Target language code: te, hi, or en")
):
    """
    Transcribe spoken student query using Gnani Prisma STT.
    Returns transcript and detected language.
    """
    lang_clean = language.strip().lower()
    if lang_clean not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{language}'. Supported: te, hi, en."
        )

    audio_bytes = await audio.read()
    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Received empty audio recording. Please speak and try again."
        )

    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file exceeds 10MB limit."
        )

    if not gnani_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gnani AI speech services are not configured. Set GNANI_API_KEY in backend/.env"
        )

    try:
        stt_result = await gnani_service.transcribe(audio_bytes, lang_clean)
        return {
            "success": True,
            "transcript": stt_result["transcript"],
            "detected_language": stt_result["detected_language"],
            "model": stt_result["model"]
        }
    except Exception as e:
        logger.error("Transcription error in /api/transcribe: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Speech-to-text processing failed: {str(e)}"
        )

@app.post("/api/speak", tags=["Speech"])
async def synthesize_speech(request: SpeakRequest):
    """
    Convert text to speech using Gnani Timbre TTS.
    Returns playable audio/wav stream.
    """
    lang_clean = request.language.strip().lower()
    if lang_clean not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{request.language}'. Supported: te, hi, en."
        )

    if not gnani_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gnani AI speech services are not configured. Set GNANI_API_KEY in backend/.env"
        )

    try:
        audio_bytes = await gnani_service.synthesize(
            text=request.text,
            language=lang_clean,
            voice=request.voice
        )
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        logger.error("Speech synthesis error in /api/speak: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Text-to-speech synthesis failed: {str(e)}"
        )

@app.post("/api/ask", tags=["Assistant"])
async def ask_question(
    audio: UploadFile = File(..., description="Multipart audio recording"),
    language: str = Form("en", description="Target language code: te, hi, or en")
):
    """
    Complete CampusVoice Multilingual Pipeline:
    1. Transcribe incoming student voice using Gnani Prisma STT.
    2. Search campus FAQ knowledge base for grounded answer & source.
    3. Synthesize response audio using Gnani Timbre TTS.
    4. Return transcript, answer, source citation, and base64-encoded WAV audio.
    """
    lang_clean = language.strip().lower()
    if lang_clean not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{language}'. Supported: te, hi, en."
        )

    audio_bytes = await audio.read()
    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Received empty audio recording. Please speak and try again."
        )

    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file exceeds 10MB limit."
        )

    if not gnani_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gnani AI speech services are not configured. Set GNANI_API_KEY in backend/.env"
        )

    # Step 1: Speech-to-Text via Prisma
    try:
        stt_result = await gnani_service.transcribe(audio_bytes, lang_clean)
        transcript = stt_result["transcript"]
        detected_language = stt_result["detected_language"]
    except Exception as e:
        logger.error("Step 1 (Prisma STT) failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

    # Step 2: Campus Knowledge Base Retrieval
    faq_match = knowledge_base.search(transcript, lang_clean)
    answer = faq_match["answer"]
    source = faq_match["source"]
    category = faq_match.get("category")
    matched = faq_match.get("matched", False)

    # Step 3: Text-to-Speech via Timbre
    audio_base64 = None
    try:
        synth_bytes = await gnani_service.synthesize(text=answer, language=lang_clean)
        # Embed as standard base64 data URI for instant HTML5 audio playback
        audio_b64_str = base64.b64encode(synth_bytes).decode("utf-8")
        audio_base64 = f"data:audio/wav;base64,{audio_b64_str}"
    except Exception as e:
        logger.error("Step 3 (Timbre TTS) failed: %s", str(e))
        # Do not fail whole request if TTS has an issue; still return text answer
        audio_base64 = None

    return {
        "success": True,
        "transcript": transcript,
        "answer": answer,
        "detected_language": detected_language,
        "source": source,
        "category": category,
        "is_sample": faq_match.get("is_sample", False),
        "matched": matched,
        "audio": audio_base64,
        "has_audio": audio_base64 is not None
    }

class TextQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Question text to query")
    language: str = Field("en", description="Target language code: te, hi, or en")

@app.post("/api/query", tags=["Assistant"])
async def query_text(request: TextQueryRequest):
    """
    Direct text query workflow for suggested questions:
    1. Search campus FAQ knowledge base for grounded answer & source.
    2. Synthesize response audio using Gnani Timbre TTS.
    3. Return structured answer, source citation, and base64-encoded WAV audio.
    """
    lang_clean = request.language.strip().lower()
    if lang_clean not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{request.language}'. Supported: te, hi, en."
        )

    # 1. Search Knowledge Base
    faq_match = knowledge_base.search(request.query, lang_clean)
    answer = faq_match["answer"]
    source = faq_match["source"]
    category = faq_match.get("category")
    matched = faq_match.get("matched", False)

    # 2. Text-to-Speech via Timbre
    audio_base64 = None
    if gnani_service.is_configured():
        try:
            synth_bytes = await gnani_service.synthesize(text=answer, language=lang_clean)
            audio_b64_str = base64.b64encode(synth_bytes).decode("utf-8")
            audio_base64 = f"data:audio/wav;base64,{audio_b64_str}"
        except Exception as e:
            logger.error("Timbre TTS synthesis error in /api/query: %s", str(e))
            audio_base64 = None

    return {
        "success": True,
        "transcript": request.query,
        "answer": answer,
        "detected_language": lang_clean,
        "source": source,
        "category": category,
        "is_sample": faq_match.get("is_sample", False),
        "matched": matched,
        "audio": audio_base64,
        "has_audio": audio_base64 is not None
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
