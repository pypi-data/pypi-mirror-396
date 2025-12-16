from typing import List, Optional, Callable, Any
import pandas as pd
from tqdm import tqdm

from .metrics.recall import recall_at_k
from .metrics.precision import precision_at_k
from .metrics.mrr import mrr_at_k
from .metrics.similarity import answer_similarity
from .metrics.hallucination import basic_hallucination_score
from .utils import top_k_texts_from_retrievals


class Evaluator:
    """
    Evaluator for RAG systems.

    Typical usage:
      evaluator = Evaluator(k=5)
      results = evaluator.evaluate(
          queries=queries,
          retrieveds=retrieved_documents,  # list of lists (each item either text id or (text, score))
          references=reference_answers,
          contexts=optional_contexts_used_by_model  # used for hallucination score
      )
    """

    def __init__(self, k: int = 5, similarity_model: str = "all-MiniLM-L6-v2"):
        self.k = k
        self.similarity_model = similarity_model

    def evaluate(
        self,
        queries: List[str],
        retrieveds: List[List[Any]],
        references: List[str],
        contexts: Optional[List[str]] = None,
        id_to_relevant: Optional[List[set]] = None,
        prediction_fn: Optional[Callable[[str, List[str]], str]] = None,
        verbose: bool = False,
    ) -> pd.DataFrame:
        """
        Evaluate using several metrics.

        - queries: list of query strings (for completeness; not used by all metrics)
        - retrieveds: list of lists; each inner list is either:
            - a list of doc ids / doc keys (strings)
            - OR a list of (doc_text, score) tuples. If tuples, first element is taken as the doc id/text.
        - references: list of ground-truth answers (strings)
        - contexts: list of long context strings used to generate predictions (optional)
        - id_to_relevant: optional list of sets containing relevant doc ids for each query (for recall/precision/mrr)
        - prediction_fn: optional callable( query, retrieved_texts ) -> predicted_answer
            If not provided, EvalRAG will not compute answer_similarity or hallucination (unless contexts/predictions provided)
        Returns a pandas DataFrame with overall metrics (one row).
        """
        n = len(queries)
        if len(retrieveds) != n or len(references) != n:
            raise ValueError("Length of queries, retrieveds, references must match")

        # normalize retrieveds to list of lists of doc ids/texts
        retrieved_text_lists = top_k_texts_from_retrievals(retrieveds)

        # compute retrieval metrics if id_to_relevant provided
        if id_to_relevant:
            recall = recall_at_k(retrieved_text_lists, id_to_relevant, self.k)
            precision = precision_at_k(retrieved_text_lists, id_to_relevant, self.k)
            mrr = mrr_at_k(retrieved_text_lists, id_to_relevant, self.k)
        else:
            recall = precision = mrr = None

        # predictions: either from prediction_fn or references (if references are model outputs)
        predictions = None
        if prediction_fn is not None:
            predictions = []
            for q, retrieved in tqdm(zip(queries, retrieved_text_lists), total=n, disable=not verbose):
                pred = prediction_fn(q, retrieved[: self.k])
                predictions.append(pred)
        # else user might pass predictions via contexts param: if contexts contains "predictions" we skip
        # compute answer similarity if predictions available
        answer_sim = None
        halluc = None
        if predictions is not None and references is not None:
            answer_sim = answer_similarity(predictions, references, model_name=self.similarity_model)
        # hallucination: needs both predictions and contexts
        if predictions is not None and contexts is not None:
            halluc = basic_hallucination_score(predictions, contexts)

        # aggregate into DataFrame
        data = {
            "num_queries": n,
            "k": self.k,
            "recall_at_k": recall,
            "precision_at_k": precision,
            "mrr_at_k": mrr,
            "answer_similarity": answer_sim,
            "hallucination_score": halluc,
        }
        df = pd.DataFrame([data])
        return df
