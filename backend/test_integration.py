"""
CampusVoice Phase 2 Integration Test Suite:
Validates real Gnani Prisma STT, Timbre TTS, KnowledgeBase retrieval, and FastAPI endpoints.
"""
import os
import pathlib
import base64
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from main import app
from gnani_service import gnani_service
from knowledge import knowledge_base

load_dotenv()

client = TestClient(app)
test_dir = pathlib.Path("/tmp/campusvoice_tests")
test_dir.mkdir(parents=True, exist_ok=True)

def test_health():
    print("=== 1. Testing GET /api/health ===")
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    data = resp.json()
    print("Health Status:", data["status"])
    print("Gnani Configured:", data["gnani"]["configured"])
    print("Loaded FAQs:", data["knowledge_base"]["loaded_faqs"])
    assert data["gnani"]["configured"] is True
    assert data["knowledge_base"]["loaded_faqs"] >= 7
    print("-> HEALTH CHECK PASSED!\n")

def test_timbre_speak():
    print("=== 2. Testing POST /api/speak (Timbre TTS) ===")
    test_cases = [
        ("en", "Welcome to CampusVoice. How can I help you?", "Kaveri", "en_speak.wav"),
        ("hi", "कैंपस वॉयस में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?", "Nalini", "hi_speak.wav"),
        ("te", "క్యాంపస్ వాయిస్ కి స్వాగతం. నేను మీకు ఎలా సహాయం చేయగలను?", "Suhana", "te_speak.wav")
    ]
    for lang, text, voice, fname in test_cases:
        resp = client.post("/api/speak", json={"text": text, "language": lang, "voice": voice})
        assert resp.status_code == 200, f"Speak failed for {lang}: {resp.text}"
        assert resp.headers["content-type"] == "audio/wav"
        assert len(resp.content) > 1000
        assert resp.content.startswith(b"RIFF")
        (test_dir / fname).write_bytes(resp.content)
        print(f"-> {lang.upper()} TTS Success ({voice}): {len(resp.content)} bytes generated")
    print("-> ALL TIMBRE TTS TESTS PASSED!\n")

def test_prisma_transcribe():
    print("=== 3. Testing POST /api/transcribe (Prisma STT) ===")
    # Use real audio files generated from Timbre
    test_cases = [
        ("en", "en_test.wav", ["attendance", "minimum", "requirement"]),
        ("hi", "hi_test.wav", ["कॉलेज", "अटेंडेंस", "नियम"]),
        ("te", "te_test.wav", ["కాలేజీలో", "హాజరు", "నిబంధనలు"])
    ]
    for lang, fname, expected_keywords in test_cases:
        audio_path = test_dir / fname
        assert audio_path.exists(), f"Missing audio file {audio_path}"
        with open(audio_path, "rb") as f:
            resp = client.post(
                "/api/transcribe",
                files={"audio": (fname, f.read(), "audio/wav")},
                data={"language": lang}
            )
        assert resp.status_code == 200, f"Transcribe failed for {lang}: {resp.text}"
        data = resp.json()
        print(f"-> {lang.upper()} Transcript: \"{data['transcript']}\" (model: {data['model']})")
        assert any(kw in data["transcript"] for kw in expected_keywords), f"Transcript mismatch for {lang}"
    print("-> ALL PRISMA STT TESTS PASSED!\n")

def test_knowledge_base():
    print("=== 4. Testing Campus FAQ Retrieval ===")
    queries = [
        ("en", "What is the minimum attendance requirement?", "attendance", True),
        ("hi", "कॉलेज में अटेंडेंस के क्या नियम हैं", "attendance", True),
        ("te", "రేపు కాలేజీలో ఏమైనా ఈవెంట్స్ ఉన్నాయా", "events", True),
        ("en", "What are the admission fees for kindergarten?", None, False)
    ]
    for lang, q, expected_cat, should_match in queries:
        res = knowledge_base.search(q, lang)
        print(f"Query ({lang}): \"{q}\"")
        print(f"  Matched: {res['matched']}, Category: {res['category']}")
        print(f"  Answer: {res['answer'][:70]}...")
        assert res["matched"] == should_match
        if should_match:
            assert res["category"] == expected_cat
        else:
            assert "Campus Administration Fallback" in res["source"]
    print("-> ALL KNOWLEDGE BASE RETRIEVAL TESTS PASSED!\n")

def test_end_to_end_ask():
    print("=== 5. Testing Full POST /api/ask Pipeline ===")
    test_cases = [
        ("en", "en_test.wav", "attendance"),
        ("hi", "hi_test.wav", "attendance"),
        ("te", "te_test.wav", "attendance")
    ]
    for lang, fname, expected_cat in test_cases:
        audio_path = test_dir / fname
        with open(audio_path, "rb") as f:
            resp = client.post(
                "/api/ask",
                files={"audio": (fname, f.read(), "audio/wav")},
                data={"language": lang}
            )
        assert resp.status_code == 200, f"Ask failed for {lang}: {resp.text}"
        data = resp.json()
        print(f"=== {lang.upper()} Pipeline Result ===")
        print(f"  Transcript : {data['transcript']}")
        print(f"  Category   : {data['category']}")
        print(f"  Answer     : {data['answer'][:80]}...")
        print(f"  Source     : {data['source']}")
        print(f"  Has Audio  : {data['has_audio']}")
        assert data["success"] is True
        assert data["matched"] is True
        assert data["category"] == expected_cat
        assert data["has_audio"] is True
        assert data["audio"].startswith("data:audio/wav;base64,")
        # Validate base64 decodes to valid RIFF audio
        b64_raw = data["audio"].split(",")[1]
        decoded = base64.b64decode(b64_raw)
        assert decoded.startswith(b"RIFF")
        print(f"  Decoded WAV: {len(decoded)} bytes (Valid RIFF Header)")
        print()
    print("-> ALL END-TO-END /api/ask TESTS PASSED!")

if __name__ == "__main__":
    test_health()
    test_timbre_speak()
    test_prisma_transcribe()
    test_knowledge_base()
    test_end_to_end_ask()
    print("\n🎉 ALL PHASE 2 TESTS COMPLETED SUCCESSFULLY! 🎉")
