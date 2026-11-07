"""
CampusVoice Phase 5: Comprehensive Testing Suite
Covers:
1. Telugu Audio Test
2. Hindi Audio Test
3. English Audio Test
4. Code-Mixed Telugu-English Test
5. Unknown Question Fallback Test
6. Empty Audio Edge-Case Test
7. API Validation / Failure Handling Test
"""
import os
import pathlib
import base64
import httpx
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from main import app
from gnani_service import gnani_service
from knowledge import knowledge_base

load_dotenv()

client = TestClient(app)
test_dir = pathlib.Path("/tmp/campusvoice_tests")
test_dir.mkdir(parents=True, exist_ok=True)

def generate_audio_if_needed(text: str, lang: str, voice: str, filename: str) -> pathlib.Path:
    filepath = test_dir / filename
    if not filepath.exists():
        url = "https://api.vachana.ai/api/v1/tts/inference"
        headers = {
            "X-API-Key-ID": os.getenv("GNANI_API_KEY"),
            "Content-Type": "application/json"
        }
        lang_code = f"{lang}-IN" if not lang.endswith("-IN") else lang
        payload = {
            "text": text,
            "voice": voice,
            "model": "timbre-v2.5",
            "language": lang_code,
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 48000,
                "num_channels": 1,
                "encoding": "linear_pcm",
                "container": "wav"
            }
        }
        with httpx.Client(timeout=30.0) as http_client:
            resp = http_client.post(url, headers=headers, json=payload)
            assert resp.status_code == 200, f"Failed to generate {filename}: {resp.text}"
            filepath.write_bytes(resp.content)
            print(f"Generated {filename} ({len(resp.content)} bytes)")
    return filepath

def test_1_telugu():
    print("\n--- TEST 1: Telugu Spoken Question ---")
    audio_path = generate_audio_if_needed(
        "రేపు కాలేజీలో ఏమైనా ఈవెంట్స్ ఉన్నాయా?", "te", "Suhana", "te_events_p5.wav"
    )
    with open(audio_path, "rb") as f:
        resp = client.post("/api/ask", files={"audio": ("query.wav", f.read(), "audio/wav")}, data={"language": "te"})
    assert resp.status_code == 200
    data = resp.json()
    print("Transcript :", data["transcript"])
    print("Answer     :", data["answer"][:70], "...")
    print("Source     :", data["source"])
    print("Category   :", data["category"])
    assert data["success"] is True
    assert data["matched"] is True
    assert data["category"] == "events"
    assert "ఈవెంట్స్" in data["transcript"] or "ఉత్సవాలు" in data["transcript"] or "టెక్" in data["answer"]
    assert data["has_audio"] is True
    print("✓ TEST 1 (Telugu) PASSED!")

def test_2_hindi():
    print("\n--- TEST 2: Hindi Spoken Question ---")
    audio_path = generate_audio_if_needed(
        "कॉलेज में अटेंडेंस के क्या नियम हैं?", "hi", "Nalini", "hi_attend_p5.wav"
    )
    with open(audio_path, "rb") as f:
        resp = client.post("/api/ask", files={"audio": ("query.wav", f.read(), "audio/wav")}, data={"language": "hi"})
    assert resp.status_code == 200
    data = resp.json()
    print("Transcript :", data["transcript"])
    print("Answer     :", data["answer"][:70], "...")
    print("Source     :", data["source"])
    print("Category   :", data["category"])
    assert data["success"] is True
    assert data["matched"] is True
    assert data["category"] == "attendance"
    assert data["has_audio"] is True
    print("✓ TEST 2 (Hindi) PASSED!")

def test_3_english():
    print("\n--- TEST 3: English Spoken Question ---")
    audio_path = generate_audio_if_needed(
        "What is the minimum attendance requirement?", "en", "Kaveri", "en_attend_p5.wav"
    )
    with open(audio_path, "rb") as f:
        resp = client.post("/api/ask", files={"audio": ("query.wav", f.read(), "audio/wav")}, data={"language": "en"})
    assert resp.status_code == 200
    data = resp.json()
    print("Transcript :", data["transcript"])
    print("Answer     :", data["answer"][:70], "...")
    print("Source     :", data["source"])
    print("Category   :", data["category"])
    assert data["success"] is True
    assert data["matched"] is True
    assert data["category"] == "attendance"
    assert data["has_audio"] is True
    print("✓ TEST 3 (English) PASSED!")

def test_4_codemixed():
    print("\n--- TEST 4: Code-Mixed (Telugu-English) Question ---")
    audio_path = generate_audio_if_needed(
        "College events ఎప్పుడు ఉంటాయి?", "te", "Suhana", "te_codemix_p5.wav"
    )
    with open(audio_path, "rb") as f:
        resp = client.post("/api/ask", files={"audio": ("query.wav", f.read(), "audio/wav")}, data={"language": "te"})
    assert resp.status_code == 200
    data = resp.json()
    print("Transcript :", data["transcript"])
    print("Answer     :", data["answer"][:70], "...")
    print("Category   :", data["category"])
    assert data["success"] is True
    assert data["matched"] is True
    assert data["category"] == "events"
    assert data["has_audio"] is True
    print("✓ TEST 4 (Code-Mixed) PASSED!")

def test_5_unknown_question():
    print("\n--- TEST 5: Out-of-Domain Unknown Question Fallback ---")
    audio_path = generate_audio_if_needed(
        "Can I fly a rocket to Jupiter from campus?", "en", "Kaveri", "unknown_p5.wav"
    )
    with open(audio_path, "rb") as f:
        resp = client.post("/api/ask", files={"audio": ("query.wav", f.read(), "audio/wav")}, data={"language": "en"})
    assert resp.status_code == 200
    data = resp.json()
    print("Transcript :", data["transcript"])
    print("Answer     :", data["answer"])
    print("Source     :", data["source"])
    print("Matched    :", data["matched"])
    assert data["matched"] is False
    assert data["category"] is None
    assert "Campus Administration Fallback" in data["source"]
    assert "could not find official information" in data["answer"].lower()
    print("✓ TEST 5 (Unknown Question Fallback) PASSED!")

def test_6_empty_audio():
    print("\n--- TEST 6: Empty Audio Validation ---")
    resp = client.post("/api/ask", files={"audio": ("empty.wav", b"", "audio/wav")}, data={"language": "en"})
    print("HTTP Status:", resp.status_code)
    print("Detail     :", resp.json().get("detail"))
    assert resp.status_code == 400
    assert "empty audio" in resp.json().get("detail", "").lower()
    print("✓ TEST 6 (Empty Audio) PASSED!")

def test_7_invalid_language():
    print("\n--- TEST 7: Invalid Language Handling ---")
    resp = client.post("/api/ask", files={"audio": ("dummy.wav", b"12345678", "audio/wav")}, data={"language": "fr"})
    print("HTTP Status:", resp.status_code)
    print("Detail     :", resp.json().get("detail"))
    assert resp.status_code == 400
    assert "unsupported language" in resp.json().get("detail", "").lower()
    print("✓ TEST 7 (Invalid Language) PASSED!")

if __name__ == "__main__":
    test_1_telugu()
    test_2_hindi()
    test_3_english()
    test_4_codemixed()
    test_5_unknown_question()
    test_6_empty_audio()
    test_7_invalid_language()
    print("\n==========================================")
    print("🎉 ALL 7 PHASE 5 TEST SCENARIOS PASSED! 🎉")
    print("==========================================")

