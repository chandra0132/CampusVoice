import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

try:
    from backend.gnani_service import gnani_service
    from backend.knowledge import knowledge_base
except ImportError:
    from gnani_service import gnani_service
    from knowledge import knowledge_base

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("campusvoice")

app = FastAPI(
    title="CampusVoice API",
    description="Multilingual Voice-First Campus AI Assistant for the Great Indian AI Internship Challenge (Gnani AI)",
    version="1.0.0"
)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [
    frontend_url,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local dev and preview environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_LANGUAGES = {"te", "hi", "en"}

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint returning API status and service identity."""
    return {
        "project": "CampusVoice",
        "tagline": "Your Campus. Your Language. Your Voice.",
        "status": "online",
        "version": "1.0.0",
        "description": "Multilingual Voice-First Campus AI Assistant"
    }

@app.get("/api/health", tags=["Status"])
async def health_check():
    """Return backend health, knowledge base statistics, and configured model status."""
    gnani_status = gnani_service.get_status()
    return {
        "status": "healthy",
        "gnani": gnani_status,
        "knowledge_base": {
            "loaded_faqs": len(knowledge_base.faqs),
            "status": "ready" if len(knowledge_base.faqs) > 0 else "empty"
        }
    }

@app.post("/api/ask", tags=["Assistant"])
async def ask_question(
    audio: UploadFile = File(..., description="Multipart audio recording"),
    language: str = Form("en", description="Target language code: te, hi, or en")
):
    """
    Process spoken student question:
    1. Validate audio and language input.
    2. Transcribe audio via Gnani Prisma STT.
    3. Retrieve relevant answer from campus knowledge base.
    4. Generate speech audio via Gnani Timbre TTS.
    5. Return complete transcript, contextual response, source, and audio.
    """
    # 1. Input validation
    if language not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{language}'. Supported languages: {list(ALLOWED_LANGUAGES)}"
        )

    audio_bytes = await audio.read()
    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Received empty audio recording. Please record your question and try again."
        )

    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file exceeds maximum allowed size of {MAX_AUDIO_SIZE // (1024 * 1024)}MB."
        )

    # 2. Check Gnani Service Configuration
    if not gnani_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gnani AI speech services are not configured. Please supply valid GNANI_API_KEY in the backend environment."
        )

    # Core pipeline calls (to be completed and verified in Phases 2 & 3)
    try:
        transcript = await gnani_service.transcribe(audio_bytes, language)
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Prisma STT integration is pending API credential verification in Phase 2."
        )
    except Exception as e:
        logger.error("Transcription error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Speech recognition service error."
        )

    # Search knowledge base
    faq_match = knowledge_base.search(transcript)
    if faq_match:
        answer = faq_match["answer"]
        source = faq_match.get("source", "Campus Notice Board")
    else:
        answer = "I could not find official information matching your query in the campus handbook. Please contact the student administrative office for assistance."
        source = "Campus Administration Fallback"

    # Synthesize response
    try:
        audio_response = await gnani_service.synthesize(answer, language)
    except Exception as e:
        logger.error("Synthesis error: %s", str(e))
        audio_response = None

    return {
        "transcript": transcript,
        "answer": answer,
        "source": source,
        "language": language,
        "has_audio": audio_response is not None
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
