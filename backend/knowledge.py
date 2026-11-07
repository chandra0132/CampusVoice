import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).resolve().parent / "data" / "faqs.json"

FALLBACK_MESSAGES = {
    "en": "I could not find official information matching your query in the campus handbook. Please contact the Student Affairs or Administrative Office for assistance.",
    "hi": "मुझे कैंपस हैंडबुक में आपके प्रश्न से संबंधित कोई आधिकारिक जानकारी नहीं मिली। कृपया अधिक सहायता के लिए कॉलेज प्रशासनिक कार्यालय से संपर्क करें।",
    "te": "మీ ప్రశ్నకు సంబంధించిన అధికారిక సమాచారం క్యాంపస్ హ్యాండ్‌బుక్‌లో కనుగొనబడలేదు. దయచేసి సహాయం కోసం కళాశాల అడ్మినిస్ట్రేటివ్ కార్యాలయాన్ని సంప్రదించండి."
}

# Common conversational stop words across English, Hindi, and Telugu
STOP_WORDS = {
    # English
    "what", "is", "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "are", "do", "does", "did", "can", "could", "would", "should", "will", "i", "you",
    "he", "she", "it", "we", "they", "me", "my", "your", "our", "their", "how", "when",
    "where", "why", "who", "which", "there", "this", "that", "these", "those", "have",
    "has", "had", "be", "been", "being", "with", "from", "about", "any", "some", "please",
    "tell", "know", "want", "give", "today", "tomorrow", "yesterday",
    # Hindi common fillers
    "क्या", "है", "हैं", "के", "की", "का", "में", "पर", "से", "को", "और", "या", "कृपया",
    "मुझे", "बताएं", "बताओ", "चाहिए", "होता", "होती", "होते", "था", "थी", "थे", "लिए",
    # Telugu common fillers
    "ఏమిటి", "ఏంటి", "ఉంది", "ఉన్నాయి", "లో", "కి", "కు", "మరియు", "లేదా", "దయచేసి",
    "నాకు", "చెప్పండి", "ఉంటాయి", "ఉంటుంది", "కోసం", "యొక్క", "గురించి"
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
        return msg, "Campus Administration Fallback"

    def search(self, query: str, language: str = "en") -> Dict[str, Any]:
        """
        Search FAQs by matching keywords and questions.
        Returns a dictionary with matched question, answer (in target language),
        source, and match status.
        """
        lang_key = language.split("-")[0].lower() if language else "en"
        if lang_key not in {"te", "hi", "en"}:
            lang_key = "en"

        if not query or not query.strip() or not self.faqs:
            fallback_text, fallback_src = self.get_fallback(lang_key)
            return {
                "matched": False,
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
                "question": query,
                "answer": fallback_text,
                "source": fallback_src,
                "category": None
            }

        best_faq = None
        highest_score = 0

        for faq in self.faqs:
            score = 0

            # 1. Match against keywords
            for kw in faq.get("keywords", []):
                norm_kw = normalize_text(kw)
                if not norm_kw:
                    continue
                # Exact phrase match in query
                if norm_kw in norm_query:
                    score += 6 if " " in norm_kw else 4
                else:
                    # Token overlap with keyword
                    kw_tokens = set(norm_kw.split())
                    common = content_words.intersection(kw_tokens)
                    if common:
                        score += len(common) * 3

            # 2. Match against questions
            for q_field in ["question", "question_hi", "question_te"]:
                q_text = faq.get(q_field, "")
                if not q_text:
                    continue
                q_tokens = extract_meaningful_tokens(q_text)
                overlap = len(content_words.intersection(q_tokens))
                score += overlap * 3

            # 3. Match against category
            cat = normalize_text(faq.get("category", ""))
            if cat and (cat in norm_query or cat in content_words):
                score += 4

            if score > highest_score:
                highest_score = score
                best_faq = faq

        # Match threshold of 4 ensures only genuine domain matches trigger
        if best_faq and highest_score >= 4:
            answers_dict = best_faq.get("answers", {})
            answer_text = answers_dict.get(lang_key) or best_faq.get("answer") or answers_dict.get("en")

            if lang_key == "hi":
                matched_question = best_faq.get("question_hi") or best_faq.get("question")
            elif lang_key == "te":
                matched_question = best_faq.get("question_te") or best_faq.get("question")
            else:
                matched_question = best_faq.get("question")

            return {
                "matched": True,
                "id": best_faq.get("id"),
                "category": best_faq.get("category"),
                "question": matched_question,
                "answer": answer_text,
                "source": best_faq.get("source", "Campus Notice Board"),
                "score": highest_score
            }

        fallback_text, fallback_src = self.get_fallback(lang_key)
        return {
            "matched": False,
            "question": query,
            "answer": fallback_text,
            "source": fallback_src,
            "category": None
        }

knowledge_base = KnowledgeBase()
