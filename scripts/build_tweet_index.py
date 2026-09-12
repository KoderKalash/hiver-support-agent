import sqlite3
from pathlib import Path

import pandas as pd


DATA_PATH = Path("data/raw/twcs/twcs.csv")
DB_PATH = Path("data/processed/twcs.db")

CHUNK_SIZE = 100_000


def build_index():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        print(f"Database already exists: {DB_PATH}")
        print("Delete it manually if you want to rebuild.")
        return

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE tweets (
            tweet_id INTEGER PRIMARY KEY,
            author_id TEXT,
            inbound INTEGER,
            created_at TEXT,
            text TEXT,
            response_tweet_id TEXT,
            in_response_to_tweet_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE INDEX idx_parent
        ON tweets(in_response_to_tweet_id)
    """)

    cursor.execute("""
        CREATE INDEX idx_author
        ON tweets(author_id)
    """)

    connection.commit()

    print("Building SQLite tweet index...")

    total_rows = 0

    for chunk in pd.read_csv(
        DATA_PATH,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        chunk = chunk.where(pd.notna(chunk), None)

        rows = [
            (
                int(row.tweet_id),
                str(row.author_id),
                int(row.inbound),
                str(row.created_at),
                row.text,
                row.response_tweet_id,
                row.in_response_to_tweet_id,
            )
            for row in chunk.itertuples(index=False)
        ]

        cursor.executemany(
            """
            INSERT INTO tweets (
                tweet_id,
                author_id,
                inbound,
                created_at,
                text,
                response_tweet_id,
                in_response_to_tweet_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

        connection.commit()

        total_rows += len(rows)

        print(f"Indexed {total_rows:,} tweets")

    connection.close()

    print(f"\nDone.")
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    build_index()