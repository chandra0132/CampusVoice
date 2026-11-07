import os
import io
import logging
import base64
from typing import Optional, Dict, Any, Tuple
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("campusvoice.gnani")

# API Base URL and Endpoints
GNANI_BASE_URL = os.getenv("GNANI_BASE_URL", "https://api.vachana.ai")
PRISMA_STT_URL = f"{GNANI_BASE_URL}/stt/v3"
TIMBRE_TTS_URL = f"{GNANI_BASE_URL}/api/v1/tts/inference"

# Language and Voice Mapping
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
    # Direct match for known audio signatures
    if audio_bytes.startswith(b'RIFF') and b'WAVE' in audio_bytes[:16]:
        return audio_bytes, "audio/wav"
    if audio_bytes.startswith(b'ID3') or audio_bytes.startswith(b'\xff\xfb') or audio_bytes.startswith(b'\xff\xf3'):
        return audio_bytes, "audio/mp3"
    if audio_bytes.startswith(b'OggS'):
        return audio_bytes, "audio/ogg"
    if audio_bytes.startswith(b'fLaC'):
        return audio_bytes, "audio/flac"

    # For WebM or other formats, transcode using PyAV
    try:
        import av
        input_buffer = io.BytesIO(audio_bytes)
        output_buffer = io.BytesIO()
        with av.open(input_buffer) as in_container:
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
        return output_buffer.getvalue(), "audio/wav"
    except Exception as e:
        logger.warning("Audio transcoding error: %s. Forwarding original payload.", str(e))
        return audio_bytes, "audio/wav"

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
        """Return configuration and health status of speech models."""
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
        
        Returns:
            Dict containing transcript, detected/configured language, request ID, and model.
        """
        if not self.is_configured():
            raise RuntimeError("Gnani API key is not configured. Please set GNANI_API_KEY in backend/.env")

        if not audio_bytes or len(audio_bytes) == 0:
            raise ValueError("Audio recording is empty.")

        # Ensure audio is in supported format
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

        logger.info("Sending STT request to Prisma (language_code=%s, size=%d bytes)", lang_code, len(processed_audio))

        async with httpx.AsyncClient(timeout=self.client_timeout) as client:
            try:
                response = await client.post(PRISMA_STT_URL, headers=headers, files=files, data=data)
            except httpx.TimeoutException:
                logger.error("Prisma STT request timed out after %s seconds", self.client_timeout)
                raise TimeoutError("Speech recognition service timed out. Please try speaking again.")
            except httpx.RequestError as exc:
                logger.error("Network error while connecting to Prisma STT: %s", exc)
                raise RuntimeError("Failed to connect to speech recognition service.")

        if response.status_code != 200:
            error_msg = f"Prisma STT failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            try:
                err_json = response.json()
                detail = err_json.get("error", {}).get("message") or err_json.get("message") or response.text
            except Exception:
                detail = response.text
            raise RuntimeError(f"Speech recognition error ({response.status_code}): {detail}")

        result = response.json()
        logger.info("Prisma STT response: %s", result)

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

        Returns:
            Raw audio/wav binary bytes.
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

        logger.info("Sending TTS request to Timbre (voice=%s, lang=%s, chars=%d)", chosen_voice, lang_code, len(text))

        async with httpx.AsyncClient(timeout=self.client_timeout) as client:
            try:
                response = await client.post(TIMBRE_TTS_URL, headers=headers, json=payload)
            except httpx.TimeoutException:
                logger.error("Timbre TTS request timed out after %s seconds", self.client_timeout)
                raise TimeoutError("Voice synthesis service timed out.")
            except httpx.RequestError as exc:
                logger.error("Network error while connecting to Timbre TTS: %s", exc)
                raise RuntimeError("Failed to connect to voice synthesis service.")

        if response.status_code != 200:
            error_msg = f"Timbre TTS failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            try:
                err_json = response.json()
                detail = err_json.get("error", {}).get("message") or err_json.get("message") or response.text
            except Exception:
                detail = response.text
            raise RuntimeError(f"Voice synthesis error ({response.status_code}): {detail}")

        audio_bytes = response.content
        if len(audio_bytes) < 44 or not audio_bytes.startswith(b'RIFF'):
            logger.warning("Timbre returned unexpected payload without RIFF header: %s", audio_bytes[:100])

        return audio_bytes

gnani_service = GnaniService()
