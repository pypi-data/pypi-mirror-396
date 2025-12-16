from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

from sklearn.metrics.pairwise import cosine_similarity

MODEL_CACHE = {}

def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    if model_name in MODEL_CACHE:
        return MODEL_CACHE[model_name]
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers not installed. Install `sentence-transformers` to use answer similarity.")
    model = SentenceTransformer(model_name)
    MODEL_CACHE[model_name] = model
    return model

def answer_similarity(predictions: List[str], references: List[str], model_name: str = "all-MiniLM-L6-v2") -> float:
    """
    Compute mean cosine similarity between predicted answers and reference answers using sentence-transformers embeddings.
    predictions / references should be same length lists.
    Returns average similarity in [0,1].
    """
    if len(predictions) != len(references):
        raise ValueError("predictions and references must have same length")
    if not predictions:
        return 0.0

    model = _get_model(model_name)
    emb_pred = model.encode(predictions, convert_to_numpy=True)
    emb_ref = model.encode(references, convert_to_numpy=True)
    sims = []
    for p, r in zip(emb_pred, emb_ref):
        sim = cosine_similarity(p.reshape(1, -1), r.reshape(1, -1))[0, 0]
        sims.append(float(sim))
    # normalize similarities from [-1,1] to [0,1]
    sims = [(s + 1) / 2 for s in sims]
    return float(sum(sims) / len(sims))
