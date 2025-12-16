from typing import List

def recall_at_k(retrieved_docs: List[List[str]], relevant_docs: List[set], k: int) -> float:
    """
    retrieved_docs: list (N queries) of lists (ranked docs, doc ids or text)
    relevant_docs: list (N queries) of sets (relevant doc ids or strings)
    returns average recall@k across queries
    """
    assert len(retrieved_docs) == len(relevant_docs)
    scores = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        topk = retrieved[:k]
        if not relevant:
            scores.append(0.0)
            continue
        hit = sum(1 for d in topk if d in relevant)
        scores.append(hit / len(relevant))
    return float(sum(scores) / len(scores)) if scores else 0.0
