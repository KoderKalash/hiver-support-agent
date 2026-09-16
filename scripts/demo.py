"""Run an offline, provenance-preserving triage demo."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import build_retrieval_corpus, read_csv
from src.system import TfidfSystem

ROOT = Path(__file__).resolve().parents[1]
def main():
    # TWCS contains Unicode; make the Windows console demo robust.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = read_csv(ROOT / "data/labels/silver_labels.csv")
    system = TfidfSystem(rows, build_retrieval_corpus(set()), final=True)
    text = " ".join(sys.argv[1:]) or "My iPhone battery is draining quickly after the update."
    prediction = system.predict(text)
    print({"intent": prediction.intent, "confidence": round(prediction.confidence, 3), "reply": prediction.reply, "decision": prediction.decision, "reason": prediction.reason, "evidence": prediction.evidence})
if __name__ == "__main__": main()
