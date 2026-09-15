import json
import random
from pathlib import Path

INPUT_PATH = Path("data/processed/apple_conversations.jsonl")
OUTPUT_PATH = Path("data/processed/apple_intent_sample.jsonl")

SAMPLE_SIZE = 800
SEED = 42


def main():
    random.seed(SEED)

    customer_messages = []

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            conversation = json.loads(line)

            messages = conversation["messages"]

            # First customer message = primary intent candidate
            customer = next(
                (m for m in messages if m["role"] == "customer"),
                None,
            )

            if customer is None:
                continue

            text = (customer["text"] or "").strip()

            if not text:
                continue

            customer_messages.append(
                {
                    "conversation_id": conversation["conversation_id"],
                    "tweet_id": customer["tweet_id"],
                    "created_at": customer["created_at"],
                    "text": text,
                }
            )

    print(
        f"Available customer messages: "
        f"{len(customer_messages):,}"
    )

    sample_size = min(SAMPLE_SIZE, len(customer_messages))

    sample = random.sample(
        customer_messages,
        sample_size,
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in sample:
            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(f"Sampled: {len(sample):,}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()