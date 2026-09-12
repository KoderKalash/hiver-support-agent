import sqlite3
import json
from pathlib import Path

#Idea: Turn the raw SQLite tweets into clean, complete AppleSupport conversations that we can later use for intent discovery, retrieval, training/test splits, and evaluation.

DB_PATH = Path("data/processed/twcs.db")
OUTPUT_PATH = Path("data/processed/apple_conversations.jsonl")
BRAND = "AppleSupport"

def get_conversation(tweet_id, connection):
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


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    # Find all AppleSupport replies
    rows = connection.execute(
        """
        SELECT tweet_id
        FROM tweets
        WHERE author_id = ?
          AND inbound = 0
          AND in_response_to_tweet_id IS NOT NULL
        ORDER BY tweet_id
        """,
        (BRAND,),
    ).fetchall()

    print(f"Found {len(rows):,} AppleSupport replies.")

    conversations_written = 0
    seen = set()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:

        for (tweet_id,) in rows:

            conversation = get_conversation(tweet_id, connection)

            if len(conversation) < 2:
                continue

            conversation_id = conversation[0]["tweet_id"]

            if conversation_id in seen:
                continue

            seen.add(conversation_id)

            record = {
                "conversation_id": conversation_id,
                "brand": BRAND,
                "messages": conversation,
            }

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

            conversations_written += 1

            if conversations_written % 10_000 == 0:
                print(
                    f"Processed {conversations_written:,} conversations..."
                )

    connection.close()

    print("\nDone.")
    print(f"Conversations written: {conversations_written:,}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()