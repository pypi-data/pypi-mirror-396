from typing import List

def mrr_at_k(retrieved_docs: List[List[str]], relevant_docs: List[set], k: int) -> float:
    """
    Mean Reciprocal Rank at K
    """
    assert len(retrieved_docs) == len(relevant_docs)
    rr_scores = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        rank = 0.0
        for i, d in enumerate(retrieved[:k], start=1):
            if d in relevant:
                rank = 1.0 / i
                break
        rr_scores.append(rank)
    return float(sum(rr_scores) / len(rr_scores)) if rr_scores else 0.0
