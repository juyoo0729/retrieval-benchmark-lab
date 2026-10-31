"""Binary relevance metrics; unanswerable queries are scored separately."""
import math


def score(ranked, relevant, k):
    if k < 1:
        raise ValueError("k must be positive")
    if not relevant:
        raise ValueError("No gold documents: evaluate as unanswerable")
    if len(ranked) != len(set(ranked)):
        raise ValueError("Duplicate retrieved document IDs")
    hits = [int(doc in relevant) for doc in ranked[:k]]
    ideal = sum(1 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return {
        f"recall@{k}": sum(hits) / len(relevant),
        f"mrr@{k}": next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0),
        f"ndcg@{k}": sum(hit / math.log2(i + 2) for i, hit in enumerate(hits)) / ideal,
    }


def percentile(values, quantile):
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * quantile
    lo, hi = math.floor(index), math.ceil(index)
    return values[lo] + (values[hi] - values[lo]) * (index - lo)
