# Decision log

1. **AppleSupport** — selected for volume and simple customer-to-brand threads. Tradeoff: historical Twitter language/policy is dated.
2. **SQLite source index** — avoids loading 516 MB CSV repeatedly. Tradeoff: build is a one-time preprocessing step.
3. **Conversation ID split** — prevents response/retrieval leakage. Tradeoff: fewer usable labelled examples.
4. **Ten fixed intents** — actionable and reviewable. Tradeoff: edge cases are forced to one primary label.
5. **No update intent** — updates are causes, not support actions. Tradeoff: loses a common surface phrase.
6. **Silver labels are separate** — heuristic labels bootstrap a runnable system. Tradeoff: results cannot be headline claims.
7. **200-row human template** — fits review time and assignment target. Tradeoff: wide uncertainty for rare intents.
8. **TF-IDF + logistic regression** — quick, local, reproducible baseline/fallback. Tradeoff: weak semantic generalisation.
9. **TF-IDF retrieval** — no embedding download or external service. Tradeoff: lexical rather than semantic matching.
10. **Top-three provenance** — makes every reply auditable. Tradeoff: reply uses only the top historical response.
11. **Verbatim historical reply** — strongest grounding available offline. Tradeoff: may be stale or account-specific in tone.
12. **Conservative router** — protects against false auto-handles. Tradeoff: very low auto-handle coverage before calibration.
13. **Account/payment escalation** — these topics require specialist/account context. Tradeoff: lower automation.
14. **No LLM judge without a key** — avoids fabricated quality scores. Tradeoff: no automated qualitative metric or agreement statistic.
15. **No frontend/fine-tuning** — preserves time for reproducibility and evidence. Tradeoff: not production UX or model quality.
