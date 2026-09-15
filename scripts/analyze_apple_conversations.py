import json
import statistics
from pathlib import Path
from collections import Counter

INPUT_PATH = Path("data/processed/apple_conversations.jsonl")


def main():
    conversations = []

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            conversations.append(json.loads(line))

    print(f"\nTotal conversations: {len(conversations):,}")

    # Conversation lengths
    lengths = [
        len(c["messages"])
        for c in conversations
    ]

    print("\n--- Conversation Length ---")
    print(f"Min:    {min(lengths)}")
    print(f"Median: {statistics.median(lengths)}")
    print(f"Mean:   {statistics.mean(lengths):.2f}")
    print(f"Max:    {max(lengths)}")

    print("\nLength distribution:")
    for length, count in sorted(Counter(lengths).items()):
        if length <= 10:
            print(f"{length} messages: {count:,}")

    # Role counts
    customer_messages = 0
    brand_messages = 0

    customer_lengths = []
    brand_lengths = []

    for conversation in conversations:
        for message in conversation["messages"]:

            text = message["text"] or ""

            if message["role"] == "customer":
                customer_messages += 1
                customer_lengths.append(len(text))

            else:
                brand_messages += 1
                brand_lengths.append(len(text))

    print("\n--- Message Counts ---")
    print(f"Customer messages: {customer_messages:,}")
    print(f"Brand messages:    {brand_messages:,}")

    # One-turn conversations
    one_customer_one_brand = 0

    for conversation in conversations:

        roles = [
            m["role"]
            for m in conversation["messages"]
        ]

        if roles == ["customer", "brand"]:
            one_customer_one_brand += 1

    percentage = (
        one_customer_one_brand / len(conversations) * 100
    )

    print("\n--- Simple Conversations ---")
    print(
        f"Customer → Brand only: "
        f"{one_customer_one_brand:,} "
        f"({percentage:.2f}%)"
    )

    # Text length
    print("\n--- Text Length ---")
    print(
        f"Average customer message: "
        f"{statistics.mean(customer_lengths):.1f} characters"
    )

    print(
        f"Average brand response: "
        f"{statistics.mean(brand_lengths):.1f} characters"
    )

    # Most common customer opening messages
    print("\n--- Example Customer Messages ---")

    shown = 0

    for conversation in conversations:

        for message in conversation["messages"]:

            if message["role"] == "customer":

                text = (message["text"] or "").replace("\n", " ")

                if text.strip():
                    print(f"- {text[:250]}")
                    shown += 1

                break

        if shown >= 30:
            break


if __name__ == "__main__":
    main()