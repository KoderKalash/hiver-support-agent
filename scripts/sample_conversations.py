import sqlite3
import json
import random
from pathlib import Path


DB_PATH = Path("data/processed/twcs.db")
OUTPUT_DIR = Path("results/candidate_conversations")

BRANDS = [
    "AmazonHelp",
    "AppleSupport",
    "Uber_Support",
    "SpotifyCares",
    "TMobileHelp",
]

SAMPLES_PER_BRAND = 30


def get_conversation(tweet_id, connection):
    """
    Walk backwards through the reply chain to reconstruct
    the conversation containing the given tweet.
    """

    messages = []

    current_id = tweet_id
    visited = set()

    while current_id is not None and current_id not in visited:

        visited.add(current_id)

        row = connection.execute(
            """
            SELECT
                tweet_id,
                author_id,
                inbound,
                created_at,
                text,
                in_response_to_tweet_id
            FROM tweets
            WHERE tweet_id = ?
            """,
            (current_id,),
        ).fetchone()

        if row is None:
            break

        (
            tweet_id,
            author_id,
            inbound,
            created_at,
            text,
            parent_id,
        ) = row

        messages.append(
            {
                "tweet_id": tweet_id,
                "author_id": author_id,
                "role": "customer" if inbound else "brand",
                "created_at": created_at,
                "text": text,
            }
        )

        current_id = parent_id

    messages.reverse()

    return messages


def sample_brand(brand, connection):

    # Get outbound tweets from this brand
    rows = connection.execute(
        """
        SELECT tweet_id
        FROM tweets
        WHERE author_id = ?
          AND inbound = 0
          AND in_response_to_tweet_id IS NOT NULL
        ORDER BY RANDOM()
        LIMIT ?
        """,
        (brand, SAMPLES_PER_BRAND * 3),
    ).fetchall()

    conversations = []
    seen = set()

    for (tweet_id,) in rows:

        conversation = get_conversation(
            tweet_id,
            connection,
        )

        if len(conversation) < 2:
            continue

        # Use the earliest tweet as conversation ID
        conversation_id = conversation[0]["tweet_id"]

        if conversation_id in seen:
            continue

        seen.add(conversation_id)

        conversations.append(
            {
                "conversation_id": conversation_id,
                "brand": brand,
                "messages": conversation,
            }
        )

        if len(conversations) >= SAMPLES_PER_BRAND:
            break

    return conversations


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DB_PATH)

    for brand in BRANDS:

        print(f"\nSampling {brand}...")

        conversations = sample_brand(
            brand,
            connection,
        )

        output_path = (
            OUTPUT_DIR / f"{brand}.jsonl"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:

            for conversation in conversations:

                f.write(
                    json.dumps(
                        conversation,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        print(
            f"Saved {len(conversations)} conversations "
            f"to {output_path}"
        )

    connection.close()


if __name__ == "__main__":
    main()