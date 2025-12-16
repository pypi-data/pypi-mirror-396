from typing import List
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

def basic_hallucination_score(predictions: List[str], contexts: List[str]) -> float:
    """
    Basic heuristic: measure proportion of n-grams in prediction that don't appear in context.
    Lower is better (0 means prediction fully grounded in context).
    This is a simple heuristic — useful as a first-pass indicator.
    """
    if not predictions or not contexts or len(predictions) != len(contexts):
        raise ValueError("predictions and contexts must be same non-zero length lists")
    vectorizer = CountVectorizer(ngram_range=(1,2), analyzer="word").fit(predictions + contexts)
    preds_vec = vectorizer.transform(predictions)
    ctx_vec = vectorizer.transform(contexts)
    scores = []
    for i in range(preds_vec.shape[0]):
        pred_arr = preds_vec[i].toarray().ravel()
        ctx_arr = ctx_vec[i].toarray().ravel()
        pred_grams = pred_arr.sum()
        if pred_grams == 0:
            scores.append(0.0)
            continue
        # grams in pred that are absent in context
        absent = ((pred_arr > 0) & (ctx_arr == 0)).sum()
        scores.append(absent / float(pred_grams))
    return float(np.mean(scores))

