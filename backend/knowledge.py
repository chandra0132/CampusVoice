import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).resolve().parent / "data" / "faqs.json"

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

    def search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search FAQs by matching keywords against query terms.
        Returns the most relevant FAQ entry or None if no match is found.
        """
        if not query or not self.faqs:
            return None

        query_lower = query.lower()
        query_words = set(query_lower.split())

        best_match = None
        highest_score = 0

        for faq in self.faqs:
            score = 0
            # Check keywords
            for keyword in faq.get("keywords", []):
                kw_lower = keyword.lower()
                if kw_lower in query_lower:
                    score += 3
                elif any(w in kw_lower for w in query_words if len(w) > 2):
                    score += 1

            # Check question text
            q_text = faq.get("question", "").lower()
            if any(w in q_text for w in query_words if len(w) > 3):
                score += 2

            # Check category
            cat_text = faq.get("category", "").lower()
            if cat_text in query_lower:
                score += 2

            if score > highest_score:
                highest_score = score
                best_match = faq

        # Match threshold to avoid false positives
        if highest_score >= 2:
            return best_match

        return None

knowledge_base = KnowledgeBase()
