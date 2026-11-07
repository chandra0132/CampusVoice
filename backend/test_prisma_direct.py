"""
Targeted Verification Script:
Tests real Telugu & English audio transcription and end-to-end /api/ask
using the live FastAPI TestClient and real Gnani APIs.
"""
import os
import io
import pathlib
import base64
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from main import app
from gnani_service import gnani_service

load_dotenv()

client = TestClient(app)
test_dir = pathlib.Path("/tmp/campusvoice_tests")
test_dir.mkdir(parents=True, exist_ok=True)

def test_english_transcribe():
    print("\n--- 1. Testing Real English Audio via POST /api/transcribe ---")
    audio_path = test_dir / "en_test.wav"
    assert audio_path.exists(), f"Audio file not found: {audio_path}"
    with open(audio_path, "rb") as f:
        resp = client.post(
            "/api/transcribe",
            files={"audio": ("recording.wav", f.read(), "audio/wav")},
            data={"language": "en"}
        )
    print("HTTP Status:", resp.status_code)
    print("Response   :", resp.text)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "attendance" in data["transcript"].lower()
    print("✓ English transcription PASSED:", data["transcript"])

def test_telugu_transcribe():
    print("\n--- 2. Testing Real Telugu Audio via POST /api/transcribe ---")
    audio_path = test_dir / "te_test.wav"
    assert audio_path.exists(), f"Audio file not found: {audio_path}"
    with open(audio_path, "rb") as f:
        resp = client.post(
            "/api/transcribe",
            files={"audio": ("recording.wav", f.read(), "audio/wav")},
            data={"language": "te"}
        )
    print("HTTP Status:", resp.status_code)
    print("Response   :", resp.text)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "కాలేజీ" in data["transcript"] or "హాజరు" in data["transcript"]
    print("✓ Telugu transcription PASSED:", data["transcript"])

def test_telugu_ask():
    print("\n--- 3. Testing Real Telugu Audio via POST /api/ask ---")
    audio_path = test_dir / "te_test.wav"
    assert audio_path.exists(), f"Audio file not found: {audio_path}"
    with open(audio_path, "rb") as f:
        resp = client.post(
            "/api/ask",
            files={"audio": ("recording.wav", f.read(), "audio/wav")},
            data={"language": "te"}
        )
    print("HTTP Status:", resp.status_code)
    assert resp.status_code == 200
    data = resp.json()
    print("Transcript :", data["transcript"])
    print("Category   :", data["category"])
    print("Answer     :", data["answer"][:80], "...")
    print("Source     :", data["source"])
    print("Has Audio  :", data["has_audio"])
    assert data["success"] is True
    assert data["matched"] is True
    assert data["has_audio"] is True
    assert data["audio"].startswith("data:audio/wav;base64,")
    print("✓ Telugu /api/ask Pipeline PASSED!")

if __name__ == "__main__":
    test_english_transcribe()
    test_telugu_transcribe()
    test_telugu_ask()
    print("\n🎉 ALL TARGETED TESTS COMPLETED SUCCESSFULLY! 🎉")

