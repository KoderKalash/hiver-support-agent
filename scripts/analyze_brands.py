import pandas as pd
from collections import defaultdict
from pathlib import Path

# Core Function: Which brands have enough useful customer-support conversations for my project?

DATA_PATH = Path("data/raw/twcs/twcs.csv")
OUTPUT_PATH = Path("results/brand_analysis.csv")

CHUNK_SIZE = 100_000


def analyze_brands():
    print("Pass 1/2: Building tweet → author lookup...")

    tweet_author = {}

    for chunk in pd.read_csv(
        DATA_PATH,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        for row in chunk.itertuples(index=False):
            tweet_author[row.tweet_id] = row.author_id

    print(f"Stored {len(tweet_author):,} tweet → author mappings.")

    print("\nPass 2/2: Analyzing brand interactions...")

    stats = defaultdict(
        lambda: {
            "inbound": 0,
            "outbound": 0,
            "responded_to": 0,
            "unique_customers": set(),
        }
    )

    for chunk in pd.read_csv(
        DATA_PATH,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        for row in chunk.itertuples(index=False):

            # Outbound tweet = brand/support account replying to customer
            if row.inbound is False:

                brand = row.author_id

                stats[brand]["outbound"] += 1

                # Find the customer tweet this brand replied to
                if pd.notna(row.in_response_to_tweet_id):

                    parent_id = int(row.in_response_to_tweet_id)

                    if parent_id in tweet_author:
                        customer_id = tweet_author[parent_id]

                        stats[brand]["responded_to"] += 1
                        stats[brand]["unique_customers"].add(
                            customer_id
                        )

    results = []

    for brand, data in stats.items():

        outbound = data["outbound"]

        response_rate = (
            data["responded_to"] / outbound
            if outbound > 0
            else 0
        )

        results.append(
            {
                "brand": brand,
                "outbound": outbound,
                "responded_to": data["responded_to"],
                "response_rate": response_rate,
                "unique_customers": len(
                    data["unique_customers"]
                ),
            }
        )

    df = pd.DataFrame(results)

    df = df.sort_values(
        by=["outbound", "response_rate"],
        ascending=False,
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nTop 30 support accounts:\n")

    print(
        df.head(30).to_string(index=False)
    )

    print(
        f"\nSaved results to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    analyze_brands()