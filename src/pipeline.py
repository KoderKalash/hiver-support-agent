"""Disk-friendly conversation and retrieval preparation."""
from __future__ import annotations
import csv, json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
CONVERSATIONS = ROOT / "data/processed/apple_conversations.jsonl"
ARTIFACTS = ROOT / "data/artifacts"

def jsonl(path: Path) -> Iterable[dict]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)

def first_customer_and_response(conversation: dict):
    customer = next((m for m in conversation["messages"] if m["role"] == "customer" and (m.get("text") or "").strip()), None)
    if not customer:
        return None
    customer_index = conversation["messages"].index(customer)
    response = next((m for m in conversation["messages"][customer_index + 1:] if m["role"] == "brand" and (m.get("text") or "").strip()), None)
    return customer, response

def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

def build_retrieval_corpus(excluded_conversation_ids: set[str], limit: int = 20000) -> Path:
    """Create a capped corpus with customer-to-first-brand-response provenance."""
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    output = ARTIFACTS / "retrieval_corpus.jsonl"
    count = 0
    with output.open("w", encoding="utf-8") as handle:
        for conversation in jsonl(CONVERSATIONS):
            if str(conversation["conversation_id"]) in excluded_conversation_ids:
                continue
            pair = first_customer_and_response(conversation)
            if not pair or not pair[1]:
                continue
            customer, response = pair
            handle.write(json.dumps({
                "conversation_id": conversation["conversation_id"], "tweet_id": customer["tweet_id"],
                "customer_text": customer["text"], "brand_response": response["text"],
            }, ensure_ascii=False) + "\n")
            count += 1
            if count >= limit:
                break
    return output
