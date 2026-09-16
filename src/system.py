"""Baselines and a conservative offline final system."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics.pairwise import cosine_similarity
from .constants import HIGH_RISK

@dataclass
class Prediction:
    intent: str
    confidence: float
    reply: str
    decision: str
    reason: str
    evidence: list[dict]

class MajorityBaseline:
    def __init__(self, intent: str): self.intent = intent
    def predict(self, text: str) -> Prediction:
        return Prediction(self.intent, 0.0, "Thanks for reaching out. Please contact Apple Support for help.", "ESCALATE", "Trivial safety baseline always escalates.", [])

class TfidfSystem:
    def __init__(self, labels: list[dict], corpus_path: Path, final: bool = False):
        self.final = final
        self.model = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
                               ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))])
        self.model.fit([r["text"] for r in labels], [r["intent"] for r in labels])
        self.corpus = [json.loads(line) for line in corpus_path.open(encoding="utf-8")]
        self.retriever = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=30000, sublinear_tf=True)
        self.matrix = self.retriever.fit_transform([r["customer_text"] for r in self.corpus])
    def predict(self, text: str) -> Prediction:
        probabilities = self.model.predict_proba([text])[0]
        index = probabilities.argmax()
        intent, confidence = self.model.classes_[index], float(probabilities[index])
        scores = cosine_similarity(self.retriever.transform([text]), self.matrix)[0]
        top = scores.argsort()[-3:][::-1]
        evidence = [{**self.corpus[i], "similarity": round(float(scores[i]), 4)} for i in top]
        best = evidence[0]
        if not self.final:
            return Prediction(intent, confidence, best["brand_response"], "AUTO_HANDLE", "Simple baseline routes all retrieved replies automatically.", evidence)
        if intent in HIGH_RISK:
            return Prediction(intent, confidence, best["brand_response"], "ESCALATE", "Account or payment issue requires a support specialist.", evidence)
        if confidence < 0.38:
            return Prediction(intent, confidence, best["brand_response"], "ESCALATE", "Low intent confidence.", evidence)
        if best["similarity"] < 0.12:
            return Prediction(intent, confidence, best["brand_response"], "ESCALATE", "Insufficient similar historical evidence.", evidence)
        return Prediction(intent, confidence, best["brand_response"], "AUTO_HANDLE", "Confident intent with similar historical resolution.", evidence)
