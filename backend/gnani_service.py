import os
import io
import asyncio
import logging
import base64
from typing import Optional, Dict, Any, Tuple
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from the backend directory regardless of cwd
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

logger = logging.getLogger("campusvoice.gnani")

# API Base URL and Endpoints
GNANI_BASE_URL = os.getenv("GNANI_BASE_URL", "https://api.vachana.ai").rstrip("/")
PRISMA_STT_URL = f"{GNANI_BASE_URL}/stt/v3"
TIMBRE_TTS_URL = f"{GNANI_BASE_URL}/api/v1/tts/inference"

LANGUAGE_CODE_MAP = {
    "te": "te-IN",
    "hi": "hi-IN",
    "en": "en-IN",
    "te-in": "te-IN",
    "hi-in": "hi-IN",
    "en-in": "en-IN"
}

DEFAULT_VOICES = {
    "te": os.getenv("VOICE_TELUGU", "Suhana"),
    "hi": os.getenv("VOICE_HINDI", "Nalini"),
    "en": os.getenv("VOICE_ENGLISH", "Kaveri")
}

def normalize_lang_code(language: str) -> str:
    """Normalize language code to Gnani standard: te-IN, hi-IN, en-IN."""
    if not language:
        return "en-IN"
    lang_clean = language.strip().lower()
    return LANGUAGE_CODE_MAP.get(lang_clean, "en-IN")

def transcode_to_wav_if_needed(audio_bytes: bytes, filename: str = "audio.wav") -> Tuple[bytes, str]:
    """
    Ensure the audio file is in a supported format for Gnani Prisma STT
    (WAV, MP3, FLAC, OGG, M4A, AAC).
    Converts WebM or unknown formats to standard WAV PCM (16kHz Mono).
    """
    # Direct match for clean standard WAV
    if audio_bytes.startswith(b'RIFF') and b'WAVE' in audio_bytes[:16]:
        return audio_bytes, "audio/wav"

    # For M4A, WebM, OGG, MP3, etc., decode with PyAV and standardize to 16kHz mono WAV
    try:
        import av
        input_buffer = io.BytesIO(audio_bytes)
        output_buffer = io.BytesIO()
        with av.open(input_buffer) as in_container:
            if not in_container.streams.audio:
                raise ValueError("No audio streams found in uploaded media file.")
            in_stream = in_container.streams.audio[0]
            resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
            with av.open(output_buffer, 'w', 'wav') as out_container:
                out_stream = out_container.add_stream('pcm_s16le', rate=16000, layout='mono')
                for frame in in_container.decode(in_stream):
                    for resampled_frame in resampler.resample(frame):
                        for packet in out_stream.encode(resampled_frame):
                            out_container.mux(packet)
                for resampled_frame in resampler.resample(None):
                    for packet in out_stream.encode(resampled_frame):
                        out_container.mux(packet)
                for packet in out_stream.encode(None):
                    out_container.mux(packet)
        wav_data = output_buffer.getvalue()
        if len(wav_data) > 44:
            return wav_data, "audio/wav"
        raise ValueError("Audio transcoding yielded empty output.")
    except Exception as e:
        logger.error("Audio processing/transcoding exception: [%s] %s", type(e).__name__, str(e))
        # If input was already standard MP3/FLAC, return as is
        if audio_bytes.startswith(b'ID3') or audio_bytes.startswith(b'\xff\xfb') or audio_bytes.startswith(b'\xff\xf3'):
            return audio_bytes, "audio/mp3"
        if audio_bytes.startswith(b'fLaC'):
            return audio_bytes, "audio/flac"
        if audio_bytes.startswith(b'OggS'):
            return audio_bytes, "audio/ogg"
        raise RuntimeError(f"Could not decode or convert audio format ({type(e).__name__}): {str(e)}")

class GnaniService:
    """
    Production client for Gnani AI Speech APIs:
    - Prisma STT: High-accuracy multilingual speech-to-text
    - Timbre TTS: Expressive Indian-accented speech synthesis
    """
    def __init__(self):
        self.api_key: Optional[str] = os.getenv("GNANI_API_KEY")
        raw_prisma = os.getenv("PRISMA_MODEL", "prisma-v3.0")
        self.prisma_model: str = "prisma-v3.0" if raw_prisma in {"default", "", None} else raw_prisma
        raw_timbre = os.getenv("TIMBRE_MODEL", "timbre-v2.5")
        self.timbre_model: str = "timbre-v2.5" if raw_timbre in {"default", "", None} else raw_timbre
        self.client_timeout: float = float(os.getenv("GNANI_TIMEOUT", "30.0"))

    def is_configured(self) -> bool:
        """Verify whether required Gnani API credentials are provided."""
        return bool(self.api_key and self.api_key.strip() and self.api_key != "your_gnani_api_key_here")

    def get_status(self) -> Dict[str, Any]:
        """Return configuration and health status of speech models without exposing secrets."""
        configured = self.is_configured()
        return {
            "configured": configured,
            "prisma_model": self.prisma_model,
            "timbre_model": self.timbre_model,
            "available_languages": ["te-IN", "hi-IN", "en-IN"],
            "voices": DEFAULT_VOICES,
            "status": "ready" if configured else "credentials_required"
        }

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe speech audio using Gnani Prisma STT (POST /stt/v3).
        Provides granular diagnostics for network, DNS, and HTTP errors.
        """
        if not self.is_configured():
            raise RuntimeError("Gnani API key is not configured. Please set GNANI_API_KEY in backend/.env")

        if not audio_bytes or len(audio_bytes) == 0:
            raise ValueError("Audio recording is empty.")

        # Ensure audio is properly decoded and formatted
        processed_audio, mime_type = transcode_to_wav_if_needed(audio_bytes)
        lang_code = normalize_lang_code(language)

        headers = {
            "X-API-Key-ID": self.api_key
        }

        files = {
            "audio_file": ("recording.wav", processed_audio, mime_type)
        }

        data = {
            "language_code": lang_code
        }

        logger.info(
            "Dispatching Prisma STT request -> URL: %s | Host: api.vachana.ai | Lang: %s | Payload Size: %d bytes",
            PRISMA_STT_URL, lang_code, len(processed_audio)
        )

        response = None
        max_attempts = 2

        async with httpx.AsyncClient(timeout=self.client_timeout) as client:
            for attempt in range(1, max_attempts + 1):
                try:
                    response = await client.post(PRISMA_STT_URL, headers=headers, files=files, data=data)
                    # Retry on transient upstream 502/503/504
                    if response.status_code in {502, 503, 504} and attempt < max_attempts:
                        logger.warning(
                            "Prisma STT upstream %d Gateway/Service error (attempt %d/%d). Retrying in 1.2s...",
                            response.status_code, attempt, max_attempts
                        )
                        await asyncio.sleep(1.2)
                        continue
                    break
                except httpx.ConnectTimeout as exc:
                    logger.error("Prisma STT connection timed out connecting to api.vachana.ai: %s", exc)
                    raise TimeoutError(f"Connection timeout to Gnani STT service ({type(exc).__name__})")
                except httpx.ReadTimeout as exc:
                    logger.error("Prisma STT read timed out waiting for audio transcription: %s", exc)
                    raise TimeoutError(f"Transcription read timeout after {self.client_timeout}s ({type(exc).__name__})")
                except httpx.ConnectError as exc:
                    err_msg = str(exc)
                    if "nodename nor servname provided" in err_msg or "gaierror" in err_msg:
                        logger.error(
                            "Prisma STT DNS resolution failed for api.vachana.ai. "
                            "Ensure the backend process has outbound internet/DNS access. Details: %s", err_msg
                        )
                        raise RuntimeError(f"DNS resolution failed for api.vachana.ai. Please check host internet connection: {err_msg}")
                    elif "Connection refused" in err_msg:
                        logger.error("Prisma STT connection refused by api.vachana.ai: %s", err_msg)
                        raise RuntimeError(f"Connection refused by Gnani STT endpoint: {err_msg}")
                    else:
                        logger.error("Prisma STT connection error [%s]: %s", type(exc).__name__, err_msg)
                        raise RuntimeError(f"Cannot connect to Gnani STT service ({type(exc).__name__}): {err_msg}")
                except httpx.RemoteProtocolError as exc:
                    logger.error("Prisma STT remote protocol error: %s", exc)
                    raise RuntimeError(f"Upstream protocol error from Gnani STT: {exc}")
                except httpx.RequestError as exc:
                    logger.error("Prisma STT HTTP request error [%s]: %s", type(exc).__name__, exc)
                    raise RuntimeError(f"Network request error reaching Gnani STT ({type(exc).__name__}): {exc}")

        if response is None:
            raise RuntimeError("Prisma STT failed to receive any HTTP response.")

        if response.status_code != 200:
            status_code = response.status_code
            raw_text = response.text
            # Sanitize response body to avoid dumping huge HTML
            clean_snippet = raw_text[:300].strip()
            logger.error("Prisma STT returned non-200 status [%d]: %s", status_code, clean_snippet)
            
            try:
                err_json = response.json()
                detail = err_json.get("error", {}).get("message") or err_json.get("message") or clean_snippet
            except Exception:
                detail = clean_snippet
            raise RuntimeError(f"Gnani STT API error ({status_code}): {detail}")

        result = response.json()
        logger.info("Prisma STT successful response: request_id=%s, model=%s", result.get("request_id"), result.get("model"))

        transcript = result.get("transcript", "").strip()
        detected_lang = result.get("detected_language") or lang_code

        return {
            "transcript": transcript,
            "detected_language": detected_lang,
            "request_id": result.get("request_id"),
            "model": result.get("model", self.prisma_model),
            "success": result.get("success", True)
        }

    async def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None) -> bytes:
        """
        Synthesize text into speech using Gnani Timbre TTS (POST /api/v1/tts/inference).
        Provides granular diagnostics for network, DNS, and HTTP errors.
        """
        if not self.is_configured():
            raise RuntimeError("Gnani API key is not configured. Please set GNANI_API_KEY in backend/.env")

        if not text or not text.strip():
            raise ValueError("Text to synthesize cannot be empty.")

        lang_code = normalize_lang_code(language)
        lang_key = lang_code.split("-")[0].lower()
        chosen_voice = voice or DEFAULT_VOICES.get(lang_key, "Kaveri")

        headers = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text.strip(),
            "voice": chosen_voice,
            "model": self.timbre_model,
            "language": lang_code,
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 48000,
                "num_channels": 1,
                "encoding": "linear_pcm",
                "container": "wav"
            }
        }

        logger.info(
            "Dispatching Timbre TTS request -> Voice: %s | Lang: %s | Chars: %d",
            chosen_voice, lang_code, len(text)
        )

        response = None
        max_attempts = 2

        async with httpx.AsyncClient(timeout=self.client_timeout) as client:
            for attempt in range(1, max_attempts + 1):
                try:
                    response = await client.post(TIMBRE_TTS_URL, headers=headers, json=payload)
                    if response.status_code in {502, 503, 504} and attempt < max_attempts:
                        logger.warning(
                            "Timbre TTS upstream %d error (attempt %d/%d). Retrying in 1.2s...",
                            response.status_code, attempt, max_attempts
                        )
                        await asyncio.sleep(1.2)
                        continue
                    break
                except httpx.ConnectTimeout as exc:
                    logger.error("Timbre TTS connection timeout: %s", exc)
                    raise TimeoutError(f"Connection timeout to Gnani TTS service ({type(exc).__name__})")
                except httpx.ReadTimeout as exc:
                    logger.error("Timbre TTS read timeout: %s", exc)
                    raise TimeoutError(f"Voice synthesis read timeout ({type(exc).__name__})")
                except httpx.ConnectError as exc:
                    err_msg = str(exc)
                    if "nodename nor servname provided" in err_msg or "gaierror" in err_msg:
                        logger.error("Timbre TTS DNS resolution failed for api.vachana.ai: %s", err_msg)
                        raise RuntimeError(f"DNS resolution failed for api.vachana.ai. Please check internet access: {err_msg}")
                    else:
                        logger.error("Timbre TTS connection error [%s]: %s", type(exc).__name__, err_msg)
                        raise RuntimeError(f"Cannot connect to Gnani TTS service ({type(exc).__name__}): {err_msg}")
                except httpx.RequestError as exc:
                    logger.error("Timbre TTS HTTP request error [%s]: %s", type(exc).__name__, exc)
                    raise RuntimeError(f"Network request error reaching Gnani TTS ({type(exc).__name__}): {exc}")

        if response is None:
            raise RuntimeError("Timbre TTS failed to receive any HTTP response.")

        if response.status_code != 200:
            status_code = response.status_code
            clean_snippet = response.text[:300].strip()
            logger.error("Timbre TTS returned non-200 status [%d]: %s", status_code, clean_snippet)
            try:
                err_json = response.json()
                detail = err_json.get("error", {}).get("message") or err_json.get("message") or clean_snippet
            except Exception:
                detail = clean_snippet
            raise RuntimeError(f"Gnani TTS API error ({status_code}): {detail}")

        audio_bytes = response.content
        if len(audio_bytes) < 44 or not audio_bytes.startswith(b'RIFF'):
            logger.warning("Timbre returned unexpected audio payload without RIFF header (%d bytes)", len(audio_bytes))

        return audio_bytes

gnani_service = GnaniService()
