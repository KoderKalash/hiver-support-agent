"""Labeling utilities. Automated labels are always called silver labels."""
from __future__ import annotations
from .constants import INTENTS, INTENT_KEYWORDS

def heuristic_intent(text: str) -> str:
    value = (text or "").lower()
    scores = {intent: sum(keyword in value for keyword in words)
              for intent, words in INTENT_KEYWORDS.items()}
    best = max(INTENTS, key=lambda intent: (scores[intent], -INTENTS.index(intent)))
    # Unclear tweets are assigned to apps/services only as a provisional bucket.
    return best if scores[best] else "apps_services"

def suggested_escalation(text: str, intent: str) -> str:
    value = (text or "").lower()
    risk_terms = ("refund", "charged", "password", "locked", "account", "fraud", "stolen", "urgent")
    return "ESCALATE" if intent in {"account_auth", "payments_purchases"} or any(t in value for t in risk_terms) else "AUTO_HANDLE"
