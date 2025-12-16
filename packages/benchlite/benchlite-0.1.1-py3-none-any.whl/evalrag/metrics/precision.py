from typing import List

def precision_at_k(retrieved_docs: List[List[str]], relevant_docs: List[set], k: int) -> float:
    """
    returns average precision@k
    """
    assert len(retrieved_docs) == len(relevant_docs)
    scores = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        topk = retrieved[:k]
        if not topk:
            scores.append(0.0)
            continue
        hit = sum(1 for d in topk if d in relevant)
        scores.append(hit / len(topk))
    return float(sum(scores) / len(scores)) if scores else 0.0
