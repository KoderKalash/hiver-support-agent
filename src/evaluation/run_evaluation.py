"""Run leakage-safe offline evaluation and save machine-readable results."""
from __future__ import annotations
import csv, json, sys
from collections import Counter
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, f1_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.pipeline import build_retrieval_corpus, read_csv
from src.system import MajorityBaseline, TfidfSystem

SILVER_LABELS = ROOT / "data/labels/silver_labels.csv"
GOLD_LABELS = ROOT / "data/labels/golden_labels.csv"
RESULTS = ROOT / "results"

def metrics(rows, predictions):
    truth = [r["intent"] for r in rows]
    predicted = [p.intent for p in predictions]
    intent = {"accuracy": round(float(accuracy_score(truth, predicted)), 4),
              "macro_f1": round(float(f1_score(truth, predicted, average="macro", zero_division=0)), 4),
              "per_intent": classification_report(truth, predicted, output_dict=True, zero_division=0)}
    actual_auto = [r["escalation_label"] == "AUTO_HANDLE" for r in rows]
    predicted_auto = [p.decision == "AUTO_HANDLE" for p in predictions]
    auto_count = sum(predicted_auto)
    correct_auto = sum(a and b for a, b in zip(actual_auto, predicted_auto))
    false_auto = sum((not a) and b for a, b in zip(actual_auto, predicted_auto))
    escalation = {"auto_handle_coverage": round(auto_count / len(rows), 4),
                  "correct_auto_handle_rate": round(correct_auto / auto_count, 4) if auto_count else None,
                  "false_auto_handle_rate": round(false_auto / auto_count, 4) if auto_count else None,
                  "escalation_rate": round(1 - auto_count / len(rows), 4)}
    similarities = [p.evidence[0]["similarity"] for p in predictions if p.evidence]
    retrieval = {"evidence_available_rate": round(len(similarities) / len(rows), 4),
                 "mean_top1_similarity": round(sum(similarities) / len(similarities), 4) if similarities else None}
    return {"intent": intent, "escalation": escalation, "retrieval": retrieval}

def serialise_prediction(row, prediction):
    return {"tweet_id": row["tweet_id"], "conversation_id": row["conversation_id"], "text": row["text"],
            "gold_or_silver_intent": row["intent"], "prediction": prediction.intent, "confidence": round(prediction.confidence, 4),
            "decision": prediction.decision, "reason": prediction.reason, "reply": prediction.reply,
            "evidence": prediction.evidence}

def main():
    if not SILVER_LABELS.exists(): raise SystemExit("Run scripts/build_silver_and_golden_template.py first.")
    silver = read_csv(SILVER_LABELS)
    # A completed golden_labels.csv takes precedence. Until then this is a
    # deterministic silver-only smoke evaluation, never a headline result.
    using_gold = GOLD_LABELS.exists()
    test = read_csv(GOLD_LABELS) if using_gold else [r for r in silver if int(r["tweet_id"]) % 4 == 0]
    if any(not r.get("intent") or not r.get("escalation_label") for r in test):
        raise SystemExit("Golden labels must have intent and escalation_label completed.")
    test_ids = {str(r["conversation_id"]) for r in test}
    train = [r for r in silver if str(r["conversation_id"]) not in test_ids]
    excluded = {str(r["conversation_id"]) for r in test}
    corpus = build_retrieval_corpus(excluded)
    majority = MajorityBaseline(Counter(r["intent"] for r in train).most_common(1)[0][0])
    simple = TfidfSystem(train, corpus, final=False)
    final = TfidfSystem(train, corpus, final=True)
    systems = {"baseline_majority": [majority.predict(r["text"]) for r in test],
               "baseline_tfidf": [simple.predict(r["text"]) for r in test],
               "final_system": [final.predict(r["text"]) for r in test]}
    RESULTS.mkdir(exist_ok=True)
    summary = {"evaluation_label_status": "HUMAN_GOLDEN" if using_gold else "PROVISIONAL_SILVER_ONLY_NOT_A_GOLDEN_EVALUATION",
               "n_train": len(train), "n_test": len(test), "split": "tweet_id modulo 4, with test conversation IDs excluded from retrieval corpus",
               "llm_judge": {"available": False, "reason": "OPENAI_API_KEY was not available; no LLM quality or judge-agreement metrics were fabricated."},
               "systems": {}}
    for name, predictions in systems.items():
        result = metrics(test, predictions)
        summary["systems"][name] = result
        (RESULTS / f"{name}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        with (RESULTS / f"{name}_predictions.jsonl").open("w", encoding="utf-8") as f:
            for row, prediction in zip(test, predictions): f.write(json.dumps(serialise_prediction(row, prediction), ensure_ascii=False) + "\n")
    labels = sorted(set(r["intent"] for r in test) | set(r["intent"] for r in train))
    matrix = confusion_matrix([r["intent"] for r in test], systems["final_system"] and [p.intent for p in systems["final_system"]], labels=labels)
    with (RESULTS / "confusion_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(["actual/predicted", *labels])
        for label, line in zip(labels, matrix): writer.writerow([label, *line])
    (RESULTS / "evaluation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
if __name__ == "__main__": main()
