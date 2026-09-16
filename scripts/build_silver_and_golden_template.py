"""Create reproducible silver labels and a 200-row human-review template."""
import csv, json, random
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.labeling import heuristic_intent, suggested_escalation

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/apple_intent_sample.jsonl"
OUT = ROOT / "data/labels"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for line in SOURCE.open(encoding="utf-8"):
        item = json.loads(line)
        intent = heuristic_intent(item["text"])
        rows.append({"conversation_id": item["conversation_id"], "tweet_id": item["tweet_id"], "created_at": item["created_at"], "text": item["text"], "intent": intent, "escalation_label": suggested_escalation(item["text"], intent), "notes": "PROVISIONAL_SILVER: replace after human review", "label_source": "heuristic_silver"})
    with (OUT / "silver_labels.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    by_intent = defaultdict(list)
    for row in rows: by_intent[row["intent"]].append(row)
    random.seed(42); selection = []
    for intent in sorted(by_intent): selection.extend(random.sample(by_intent[intent], min(20, len(by_intent[intent]))))
    if len(selection) < 200:
        selected = {str(r["tweet_id"]) for r in selection}
        selection.extend(r for r in rows if str(r["tweet_id"]) not in selected)
    selection = selection[:200]
    for row in selection:
        row["intent"] = ""; row["escalation_label"] = ""; row["notes"] = "HUMAN_REVIEW_REQUIRED"; row["label_source"] = "human_pending"
    with (OUT / "golden_review_template.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=selection[0].keys()); writer.writeheader(); writer.writerows(selection)
    print(f"Wrote {len(rows)} silver labels and {len(selection)} human-review rows to {OUT}")
if __name__ == "__main__": main()
