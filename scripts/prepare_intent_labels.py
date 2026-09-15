import json
import csv
from pathlib import Path

INPUT_PATH = Path("data/processed/apple_intent_sample.jsonl")
OUTPUT_PATH = Path("data/processed/apple_intent_labels.csv")

INTENTS = [
    "performance_stability",
    "keyboard_input",
    "battery_charging",
    "connectivity",
    "apps_services",
    "media_data",
    "account_auth",
    "payments_purchases",
    "communication",
    "hardware_accessories",
]

def main():
    rows = []

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            rows.append({
                "conversation_id": item["conversation_id"],
                "tweet_id": item["tweet_id"],
                "created_at": item["created_at"],
                "text": item["text"],
                "intent": "",
                "notes": "",
            })

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "conversation_id",
                "tweet_id",
                "created_at",
                "text",
                "intent",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Prepared {len(rows)} messages for labeling.")
    print(f"Output: {OUTPUT_PATH}")
    print("\nAllowed intents:")
    for intent in INTENTS:
        print(f"- {intent}")


if __name__ == "__main__":
    main()