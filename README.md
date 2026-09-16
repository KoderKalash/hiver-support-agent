# AppleSupport grounded support triage

An offline, evidence-preserving take-home implementation for the Kaggle **thoughtvector/customer-support-on-twitter** dataset. Given an incoming AppleSupport customer tweet, it predicts one fixed intent, retrieves comparable historical AppleSupport resolutions, returns the historical reply with its provenance, and chooses `AUTO_HANDLE` or `ESCALATE` conservatively.

## Submission status

The runnable pipeline, two baselines, retrieval-leakage guard, reports, and machine-readable results are complete. The required genuinely human-labelled golden evaluation remains the one manual task: review the 200 rows in `data/labels/golden_review_template.csv`, then save the completed file as `data/labels/golden_labels.csv`. Until that is done, every reported metric is conspicuously marked **PROVISIONAL_SILVER_ONLY** and is not a valid headline result. No OpenAI API key was available, so LLM judge and human/LLM agreement scores are unavailable rather than invented.

## System

`tweet + context → TF-IDF/logistic intent → TF-IDF top-3 historical resolutions → verbatim grounded reply + provenance → conservative router`

The final router escalates account/payment issues, low intent confidence (<0.38), and weak historical evidence (top-1 similarity <0.12). It never creates a new intent name. Retrieval construction excludes every evaluation conversation ID.

## Taxonomy

`performance_stability`, `keyboard_input`, `battery_charging`, `connectivity`, `apps_services`, `media_data`, `account_auth`, `payments_purchases`, `communication`, `hardware_accessories`.

See [the labeling guide](report/labeling_guide.md) for definitions and boundaries. In particular, an iOS update is context; label its actionable consequence.

## Reproduce

Requires Python 3.10+ and the Kaggle CSV at `data/raw/twcs/twcs.csv` (not committed). The included `data/processed/twcs.db` and `apple_conversations.jsonl` allow a quick evaluation without rebuilding raw data.

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# Only if processed assets are absent; this takes time.
.\.venv\Scripts\python scripts\build_tweet_index.py
.\.venv\Scripts\python scripts\build_apple_conversations.py
.\.venv\Scripts\python scripts\create_intent_sample.py

# Creates 800 clearly marked silver labels and a 200-row human-review CSV.
.\.venv\Scripts\python scripts\build_silver_and_golden_template.py

# Run the current reproducible, silver-only smoke evaluation.
.\.venv\Scripts\python scripts\run_evaluation.py

# After human review, place completed CSV at data/labels/golden_labels.csv and rerun.
.\.venv\Scripts\python scripts\run_evaluation.py

# One input demo (prints evidence provenance and routing reason).
.\.venv\Scripts\python scripts\demo.py "My iPhone battery is draining quickly"
```

Evaluation writes `results/baseline_majority.json`, `results/baseline_tfidf.json`, `results/final_system.json`, prediction JSONL with retrieved tweet provenance, `results/confusion_matrix.csv`, and `results/evaluation_summary.json`.

## Current executed smoke result (not a headline)

On 609/191 conversation-isolated silver train/test rows, majority baseline macro-F1 was 0.0714; TF-IDF/final classifier macro-F1 was 0.4284 and accuracy 0.6545. The final conservative router auto-handled 1.57% of rows and had a silver-label false-auto-handle rate of 0.0. The simple baseline auto-handled everything and its silver-label false-auto-handle rate was 5.76%. These numbers measure agreement with heuristic labels, not customer-support quality or human ground truth.

## Scope deliberately excluded

No UI, authentication, Twitter integration, service deployment, fine-tuning, microservices, or account access. The response is a historical AppleSupport response rather than new policy generation, which keeps grounding auditable but does not guarantee policy currency.

See [report/report.md](report/report.md), [failure analysis](report/failure_analysis.md), and [decision log](report/decision_log.md) before submission.
