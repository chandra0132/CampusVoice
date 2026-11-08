# -*- coding: utf-8 -*-
"""
CampusVoice NBKRIST Official Knowledge Base V2 Test Suite
Validates:
1. Dataset integrity, schema compliance, and multilingual coverage
2. Retrieval accuracy for English, Hindi, Telugu, and Code-Mixed queries
3. Precision against out-of-domain / unsupported queries (fallback guard)
"""

import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.knowledge import knowledge_base

def run_dataset_integrity_tests():
    print("=" * 60)
    print("1. DATASET INTEGRITY & SCHEMA COMPLIANCE TESTS")
    print("=" * 60)
    
    faqs = knowledge_base.faqs
    total = len(faqs)
    print(f"Total FAQs loaded: {total}")
    assert total >= 60, f"Expected at least 60 FAQs, found {total}"

    required_keys = [
        "id", "category", "question", "question_hi", "question_te",
        "questions", "answer", "answers", "keywords",
        "source", "source_title", "source_url", "source_section",
        "academic_year", "applicable_regulation", "verified", "is_sample"
    ]

    for idx, faq in enumerate(faqs):
        for k in required_keys:
            assert k in faq, f"FAQ #{faq.get('id', idx)} missing required field '{k}'"
        
        # Check multilingual questions
        assert faq["questions"]["en"], f"FAQ #{faq['id']} empty English question"
        assert faq["questions"]["hi"], f"FAQ #{faq['id']} empty Hindi question"
        assert faq["questions"]["te"], f"FAQ #{faq['id']} empty Telugu question"

        # Check multilingual answers
        assert faq["answers"]["en"], f"FAQ #{faq['id']} empty English answer"
        assert faq["answers"]["hi"], f"FAQ #{faq['id']} empty Hindi answer"
        assert faq["answers"]["te"], f"FAQ #{faq['id']} empty Telugu answer"

        # Check sources and verification
        assert faq["source_url"].startswith("http"), f"FAQ #{faq['id']} invalid source URL: {faq['source_url']}"
        assert faq["verified"] is True, f"FAQ #{faq['id']} should have verified=True"
        assert faq["is_sample"] is False, f"FAQ #{faq['id']} should have is_sample=False"
        assert len(faq["keywords"]) >= 5, f"FAQ #{faq['id']} has insufficient keywords ({len(faq['keywords'])})"

    categories = set(f["category"] for f in faqs)
    print(f"Categories covered ({len(categories)}): {sorted(list(categories))}")
    print("[PASS] Dataset integrity and multilingual schema verified successfully.\n")

def run_retrieval_benchmark():
    print("=" * 60)
    print("2. MULTILINGUAL & CODE-MIXED RETRIEVAL BENCHMARK")
    print("=" * 60)

    test_cases = [
        # --- 10 ENGLISH QUERIES ---
        {"lang": "en", "query": "What is the minimum attendance required under R-23?", "expected_cat": "attendance", "expected_id": 13},
        {"lang": "en", "query": "What is the intake for Computer Science and Engineering?", "expected_cat": "academic_programmes", "expected_id": 8},
        {"lang": "en", "query": "How much is the annual college bus fee for Nellore?", "expected_cat": "transportation", "expected_id": 45},
        {"lang": "en", "query": "What are the management quota fees for AI and Data Science?", "expected_cat": "fees", "expected_id": 38},
        {"lang": "en", "query": "What is the highest package offered in campus placements?", "expected_cat": "placements", "expected_id": 53},
        {"lang": "en", "query": "What are the working hours of the Central Library?", "expected_cat": "library", "expected_id": 59},
        {"lang": "en", "query": "What is the eligibility for B.Tech with Honours degree?", "expected_cat": "academic_regulations", "expected_id": 32},
        {"lang": "en", "query": "How many credits are needed to graduate B.Tech under R-23?", "expected_cat": "academic_regulations", "expected_id": 25},
        {"lang": "en", "query": "What are the rules for attendance condonation on medical grounds?", "expected_cat": "attendance", "expected_id": 14},
        {"lang": "en", "query": "Is there an anti-ragging helpline available?", "expected_cat": "student_support", "expected_id": 71},

        # --- 10 TELUGU QUERIES ---
        {"lang": "te", "query": "R-23 నిబంధనల ప్రకారం కనీస హాజరు శాతం ఎంత ఉండాలి?", "expected_cat": "attendance", "expected_id": 13},
        {"lang": "te", "query": "కంప్యూటర్ సైన్స్ బ్రాంచ్ లో ఎన్ని సీట్లు ఉన్నాయి?", "expected_cat": "academic_programmes", "expected_id": 8},
        {"lang": "te", "query": "నెల్లూరు రూట్ కాలేజీ బస్సు ఫీజు ఎంత?", "expected_cat": "transportation", "expected_id": 45},
        {"lang": "te", "query": "ల్యూమెన్ టెక్నాలజీస్ లో ఎంత ప్యాకేజీ వచ్చింది?", "expected_cat": "placements", "expected_id": 53},
        {"lang": "te", "query": "సెంట్రల్ లైబ్రరీ సమయాలు ఏమిటి?", "expected_cat": "library", "expected_id": 59},
        {"lang": "te", "query": "హాస్టల్ భోజనం మరియు మెస్ సదుపాయాలు ఎలా ఉన్నాయి?", "expected_cat": "hostels", "expected_id": 64},
        {"lang": "te", "query": "డిప్లొమా తర్వాత లేటరల్ ఎంట్రీ ద్వారా బిటెక్ లో ఎలా చేరవచ్చు?", "expected_cat": "admissions", "expected_id": 3},
        {"lang": "te", "query": "థియరీ సబ్జెక్టులో పాస్ కావడానికి కనీసం ఎన్ని మార్కులు రావాలి?", "expected_cat": "examinations", "expected_id": 20},
        {"lang": "te", "query": "మేనేజ్‌మెంట్ కోటా ఏఐడీఎస్ ఫీజు ఎంత?", "expected_cat": "fees", "expected_id": 38},
        {"lang": "te", "query": "జగనన్న విద్యా దీవెన ఫీజు రీయింబర్స్‌మెంట్ ఎలా లభిస్తుంది?", "expected_cat": "scholarships", "expected_id": 77},

        # --- 10 HINDI QUERIES ---
        {"lang": "hi", "query": "R-23 नियमों के तहत न्यूनतम उपस्थिति कितनी होनी चाहिए?", "expected_cat": "attendance", "expected_id": 13},
        {"lang": "hi", "query": "कंप्यूटर साइंस इंजीनियरिंग (CSE) में कुल कितनी सीटें हैं?", "expected_cat": "academic_programmes", "expected_id": 8},
        {"lang": "hi", "query": "नेल्लूर के लिए कॉलेज बस की फीस कितनी है?", "expected_cat": "transportation", "expected_id": 45},
        {"lang": "hi", "query": "कैंपस प्लेसमेंट में सबसे अधिक पैकेज कितना मिला है?", "expected_cat": "placements", "expected_id": 53},
        {"lang": "hi", "query": "सेंट्रल लाइब्रेरी के खुलने और बंद होने का समय क्या है?", "expected_cat": "library", "expected_id": 59},
        {"lang": "hi", "query": "हॉस्टल में भोजन और मेस की क्या सुविधाएं हैं?", "expected_cat": "hostels", "expected_id": 64},
        {"lang": "hi", "query": "डिप्लोमा के बाद लेटरल एंट्री से एडमिशन कैसे लें?", "expected_cat": "admissions", "expected_id": 3},
        {"lang": "hi", "query": "थ्योरी परीक्षा में पास होने के लिए न्यूनतम कितने अंक चाहिए?", "expected_cat": "examinations", "expected_id": 20},
        {"lang": "hi", "query": "मैनेजमेंट कोटा में AI&DS की फीस कितनी है?", "expected_cat": "fees", "expected_id": 38},
        {"lang": "hi", "query": "एंटी-रैगिंग समिति और हेल्पलाइन की जानकारी क्या है?", "expected_cat": "student_support", "expected_id": 71},

        # --- 5 CODE-MIXED / TRANSLITERATED QUERIES ---
        {"lang": "en", "query": "attendance percentage entha undali r23 lo", "expected_cat": "attendance", "expected_id": 13},
        {"lang": "en", "query": "nellore bus fee entha", "expected_cat": "transportation", "expected_id": 45},
        {"lang": "en", "query": "cse branch lo enni seats unnai", "expected_cat": "academic_programmes", "expected_id": 8},
        {"lang": "en", "query": "highest package kitna hai placement me", "expected_cat": "placements", "expected_id": 53},
        {"lang": "en", "query": "hostel facilities ela untayi boys ki", "expected_cat": "hostels", "expected_id": 62},

        # --- 5 UNSUPPORTED / OUT-OF-DOMAIN QUERIES (MUST NOT MATCH) ---
        {"lang": "en", "query": "can I fly a rocket to jupiter from campus", "expected_cat": None, "expected_id": None},
        {"lang": "en", "query": "how to bake a chocolate fudge cake at home", "expected_cat": None, "expected_id": None},
        {"lang": "en", "query": "who won the cricket world cup 2023 final match", "expected_cat": None, "expected_id": None},
        {"lang": "en", "query": "what is the authentic hyderabadi biryani recipe", "expected_cat": None, "expected_id": None},
        {"lang": "en", "query": "can I buy bitcoin and cryptocurrency inside the campus", "expected_cat": None, "expected_id": None}
    ]

    passed = 0
    failed = 0

    for idx, tc in enumerate(test_cases, 1):
        lang = tc["lang"]
        q = tc["query"]
        is_supported = tc["expected_id"] is not None

        result = knowledge_base.search(q, lang)

        if is_supported:
            matched = result.get("matched", False)
            match_id = result.get("id")
            match_cat = result.get("category")
            score = result.get("score")

            if matched and (match_id == tc["expected_id"] or match_cat == tc["expected_cat"]):
                print(f"[PASS] #{idx:02d} ({lang.upper()}) '{q[:40]}...' -> Matched FAQ #{match_id} ({match_cat}) [Score: {score}]")
                passed += 1
            else:
                print(f"[FAIL] #{idx:02d} ({lang.upper()}) '{q}' -> Got #{match_id} ({match_cat}), Expected #{tc['expected_id']} ({tc['expected_cat']})")
                failed += 1
        else:
            matched = result.get("matched", False)
            if not matched:
                print(f"[PASS] #{idx:02d} (OOD) '{q[:40]}...' -> Correctly returned Grounded Fallback")
                passed += 1
            else:
                print(f"[FAIL] #{idx:02d} (OOD) '{q}' -> False Positive on FAQ #{result.get('id')} ({result.get('category')})")
                failed += 1

    print("\n" + "=" * 60)
    print(f"BENCHMARK RESULTS: {passed} PASSED, {failed} FAILED out of {len(test_cases)} tests")
    print("=" * 60)
    assert failed == 0, f"{failed} test cases failed"

if __name__ == "__main__":
    run_dataset_integrity_tests()
    run_retrieval_benchmark()
