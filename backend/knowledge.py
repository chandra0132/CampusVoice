import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).resolve().parent / "data" / "faqs.json"

FALLBACK_MESSAGES = {
    "en": "I could not find official information matching your query in the NBKRIST institutional knowledge base. Please contact the Admissions Office at +91-9441572755 or the Principal's Office at ist@nbkrist.org for assistance.",
    "hi": "मुझे NBKRIST संस्थागत ज्ञानकोश में आपके प्रश्न से संबंधित कोई आधिकारिक जानकारी नहीं मिली। कृपया सहायता के लिए प्रवेश कार्यालय (+91-9441572755) या प्राचार्य कार्यालय (ist@nbkrist.org) से संपर्क करें।",
    "te": "మీ ప్రశ్నకు సంబంధించిన అధికారిక సమాచారం NBKRIST నాలెడ్జ్ బేస్‌లో కనుగొనబడలేదు. దయచేసి సహాయం కోసం అడ్మిషన్ల కార్యాలయాన్ని (+91-9441572755) లేదా ప్రిన్సిపాల్ కార్యాలయాన్ని (ist@nbkrist.org) సంప్రదించండి."
}

# Common conversational stop words across English, Hindi, and Telugu
STOP_WORDS = {
    # English conversational stop words & universal context words
    "what", "is", "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "are", "do", "does", "did", "can", "could", "would", "should", "will", "i", "you",
    "he", "she", "it", "we", "they", "me", "my", "your", "our", "their", "how", "when",
    "where", "why", "who", "which", "there", "this", "that", "these", "those", "have",
    "has", "had", "be", "been", "being", "with", "from", "about", "any", "some", "please",
    "tell", "know", "want", "give", "today", "tomorrow", "yesterday", "much", "many",
    "campus", "college", "university", "student", "students", "nbkrist",
    # Hindi common fillers & universal context words
    "क्या", "है", "हैं", "के", "की", "का", "में", "पर", "से", "को", "और", "या", "कृपया",
    "मुझे", "बताएं", "बताओ", "चाहिए", "होता", "होती", "होते", "था", "थी", "थे", "लिए",
    "कितना", "कितनी", "कितने", "कौन", "किसे", "कहाँ", "कब", "कैसे",
    "कॉलेज", "कैंपस", "छात्र", "छात्रों",
    # Telugu common fillers & universal context words
    "ఏమిటి", "ఏంటి", "ఉంది", "ఉన్నాయి", "లో", "కి", "కు", "మరియు", "లేదా", "దయచేసి",
    "నాకు", "చెప్పండి", "ఉంటాయి", "ఉంటుంది", "కోసం", "యొక్క", "గురించి",
    "ఎంత", "ఎన్ని", "ఎవరు", "ఎక్కడ", "ఎప్పుడు", "ఎలా",
    "కాలేజ్", "కాలేజీ", "క్యాంపస్", "విద్యార్థి", "విద్యార్థులు"
}

def normalize_text(text: str) -> str:
    """Normalize input text by removing punctuation and extra whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s\u0900-\u097F\u0C00-\u0C7F]', ' ', text)
    return " ".join(text.split())

def extract_meaningful_tokens(text: str) -> set:
    """Extract content words excluding generic conversational stopwords."""
    norm = normalize_text(text)
    tokens = norm.split()
    return {w for w in tokens if w not in STOP_WORDS and len(w) > 1}

class KnowledgeBase:
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or DATA_PATH
        self.faqs: List[Dict[str, Any]] = []
        self.load_faqs()

    def load_faqs(self) -> None:
        """Load FAQ dataset from JSON storage."""
        try:
            if not self.data_path.exists():
                logger.warning("Knowledge base file not found at %s", self.data_path)
                self.faqs = []
                return

            with open(self.data_path, "r", encoding="utf-8") as f:
                self.faqs = json.load(f)
            logger.info("Loaded %d FAQs from %s", len(self.faqs), self.data_path)
        except Exception as e:
            logger.error("Failed to load FAQs: %s", str(e))
            self.faqs = []

    def get_fallback(self, language: str = "en") -> Tuple[str, str]:
        """Return safe grounded fallback response and source citation."""
        lang_key = language.split("-")[0].lower() if language else "en"
        msg = FALLBACK_MESSAGES.get(lang_key, FALLBACK_MESSAGES["en"])
        return msg, "NBKRIST Administration & Information Hub"

    def search(self, query: str, language: str = "en") -> Dict[str, Any]:
        """
        Search FAQs by matching keywords, questions, and semantic categories.
        Returns a dictionary with matched question, answer (in target language),
        verified institutional source citation, and match metadata.
        """
        lang_key = language.split("-")[0].lower() if language else "en"
        if lang_key not in {"te", "hi", "en"}:
            lang_key = "en"

        if not query or not query.strip() or not self.faqs:
            fallback_text, fallback_src = self.get_fallback(lang_key)
            return {
                "matched": False,
                "is_sample": False,
                "question": query,
                "answer": fallback_text,
                "source": fallback_src,
                "category": None
            }

        norm_query = normalize_text(query)
        content_words = extract_meaningful_tokens(query)

        if not content_words:
            fallback_text, fallback_src = self.get_fallback(lang_key)
            return {
                "matched": False,
                "is_sample": False,
                "question": query,
                "answer": fallback_text,
                "source": fallback_src,
                "category": None
            }

        best_faq = None
        highest_score = 0

        for faq in self.faqs:
            score = 0
            matched_content_tokens = set()
            exact_keyword_hit = False

            # 1. Match against keywords (exact phrases and token overlap)
            for kw in faq.get("keywords", []):
                norm_kw = normalize_text(kw)
                if not norm_kw:
                    continue
                # Exact keyword or phrase match in query
                if norm_kw in norm_query:
                    score += 10 if " " in norm_kw else 6
                    exact_keyword_hit = True
                    matched_content_tokens.update(norm_kw.split())
                else:
                    kw_tokens = set(norm_kw.split())
                    common = content_words.intersection(kw_tokens)
                    if common:
                        score += len(common) * 2
                        matched_content_tokens.update(common)
                    elif any((len(cw) >= 4 and len(kt) >= 4 and (cw in kt or kt in cw)) for cw in content_words for kt in kw_tokens):
                        for cw in content_words:
                            for kt in kw_tokens:
                                if len(cw) >= 4 and len(kt) >= 4 and (cw in kt or kt in cw):
                                    matched_content_tokens.add(cw)
                                    score += 2

            # 2. Match against questions in all languages
            for q_field in ["question", "question_hi", "question_te"]:
                q_text = faq.get(q_field, "")
                if not q_text:
                    continue
                q_tokens = extract_meaningful_tokens(q_text)
                overlap = content_words.intersection(q_tokens)
                if overlap:
                    score += len(overlap) * 3
                    matched_content_tokens.update(overlap)

            # 3. Match against category
            cat = normalize_text(faq.get("category", ""))
            if cat and (cat in norm_query or cat in content_words):
                score += 3
                if cat in content_words:
                    matched_content_tokens.add(cat)

            # Query token coverage bonus
            score += len(matched_content_tokens) * 3

            # Precision Guard: prevent out-of-domain false positives on isolated single unigrams
            if len(content_words) >= 3 and len(matched_content_tokens) < 2 and not exact_keyword_hit:
                score = 0

            if score > highest_score:
                highest_score = score
                best_faq = faq

        # Match threshold of 6 ensures only genuine domain matches trigger
        if best_faq and highest_score >= 6:
            answers_dict = best_faq.get("answers", {})
            answer_text = answers_dict.get(lang_key) or best_faq.get("answer") or answers_dict.get("en")

            matched_question = best_faq.get(f"question_{lang_key}") or best_faq.get("question")

            return {
                "matched": True,
                "id": best_faq.get("id"),
                "category": best_faq.get("category"),
                "is_sample": best_faq.get("is_sample", False),
                "question": matched_question,
                "answer": answer_text,
                "source": best_faq.get("source", "NBKRIST Academic Information"),
                "source_title": best_faq.get("source_title"),
                "source_url": best_faq.get("source_url"),
                "source_section": best_faq.get("source_section"),
                "academic_year": best_faq.get("academic_year"),
                "applicable_regulation": best_faq.get("applicable_regulation"),
                "verified": best_faq.get("verified", True),
                "score": highest_score
            }

        fallback_text, fallback_src = self.get_fallback(lang_key)
        return {
            "matched": False,
            "is_sample": False,
            "question": query,
            "answer": fallback_text,
            "source": fallback_src,
            "category": None
        }

knowledge_base = KnowledgeBase()
