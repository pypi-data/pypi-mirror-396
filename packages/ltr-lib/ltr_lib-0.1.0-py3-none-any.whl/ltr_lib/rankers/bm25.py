"""BM25 ranking model for text-based retrieval."""

from typing import Any, Dict, List, Optional, Union

import numpy as np
from rank_bm25 import BM25Okapi

from .base import BaseRanker, RankerMixin


class BM25Ranker(BaseRanker, RankerMixin):
    """BM25 (Best Matching 25) ranking model.

    BM25 is a probabilistic retrieval function based on TF-IDF that
    scores documents based on query term frequency, document length,
    and collection statistics.

    This implementation uses text documents directly rather than
    feature matrices. It serves as a strong baseline for comparing
    learning-to-rank models.

    Attributes:
        k1: Term frequency saturation parameter (default: 1.5)
        b: Document length normalization parameter (default: 0.75)
        epsilon: Floor value for IDF (default: 0.25)
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        epsilon: float = 0.25,
        name: str = "BM25"
    ):
        super().__init__(name=name)
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon

        self._bm25: Optional[BM25Okapi] = None
        self._corpus: Optional[List[List[str]]] = None
        self._doc_ids: Optional[List[Any]] = None

    def fit(
        self,
        documents: List[str],
        doc_ids: Optional[List[Any]] = None,
        **kwargs
    ) -> "BM25Ranker":
        """Fit the BM25 model on a corpus of documents.

        Args:
            documents: List of document strings to index
            doc_ids: Optional list of document identifiers
            **kwargs: Ignored (for API compatibility)

        Returns:
            self: The fitted ranker
        """
        self._corpus = [doc.lower().split() for doc in documents]
        self._doc_ids = doc_ids or list(range(len(documents)))

        self._bm25 = BM25Okapi(
            self._corpus,
            k1=self.k1,
            b=self.b,
            epsilon=self.epsilon
        )
        self._is_fitted = True

        return self

    def predict(self, query: Union[str, List[str]]) -> np.ndarray:
        """Get BM25 scores for documents given a query.

        Args:
            query: Query string or list of query tokens

        Returns:
            scores: BM25 scores for each document in the corpus
        """
        if not self._is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(query, str):
            query_tokens = query.lower().split()
        else:
            query_tokens = [t.lower() for t in query]

        return self._bm25.get_scores(query_tokens)

    def predict_batch(
        self,
        queries: List[Union[str, List[str]]]
    ) -> List[np.ndarray]:
        """Get BM25 scores for multiple queries.

        Args:
            queries: List of query strings or token lists

        Returns:
            scores_list: List of score arrays, one per query
        """
        return [self.predict(q) for q in queries]

    def rank(
        self,
        query: Union[str, List[str]],
        top_k: Optional[int] = None
    ) -> List[tuple]:
        """Get ranked documents for a query.

        Args:
            query: Query string or list of query tokens
            top_k: Number of top documents to return (None for all)

        Returns:
            ranked: List of (doc_id, score) tuples sorted by score
        """
        scores = self.predict(query)
        indices = np.argsort(scores)[::-1]

        if top_k:
            indices = indices[:top_k]

        return [(self._doc_ids[i], scores[i]) for i in indices]

    def score(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: np.ndarray,
        metric: str = "ndcg",
        k: int = 10,
        queries: Optional[List[str]] = None,
        doc_indices: Optional[np.ndarray] = None
    ) -> float:
        """Compute ranking metric using precomputed BM25 scores.

        For BM25, this method expects either precomputed scores in X
        or queries and document indices to compute scores.

        Args:
            X: Precomputed BM25 scores or feature matrix
            y: True relevance labels
            groups: Query group sizes
            metric: Metric name ('ndcg', 'map', 'precision')
            k: Cutoff for metric computation
            queries: Query strings (if X doesn't contain BM25 scores)
            doc_indices: Document indices for each sample

        Returns:
            score: The computed metric value
        """
        from ..evaluation.metrics import ndcg_at_k, mean_average_precision, precision_at_k

        if X.ndim == 2 and X.shape[1] == 1:
            predictions = X.flatten()
        elif X.ndim == 1:
            predictions = X
        else:
            raise ValueError(
                "BM25 score() expects precomputed BM25 scores. "
                "Use predict() to get scores first."
            )

        query_data = self.split_by_groups(
            predictions.reshape(-1, 1), y, groups
        )

        scores = []
        for preds, labels in query_data:
            preds = preds.flatten()
            if metric == "ndcg":
                scores.append(ndcg_at_k(labels, preds, k))
            elif metric == "map":
                scores.append(mean_average_precision(labels, preds))
            elif metric == "precision":
                scores.append(precision_at_k(labels, preds, k))
            else:
                raise ValueError(f"Unknown metric: {metric}")

        return np.mean(scores)

    def get_params(self) -> Dict[str, Any]:
        """Get model parameters."""
        params = super().get_params()
        params.update({
            "k1": self.k1,
            "b": self.b,
            "epsilon": self.epsilon,
        })
        return params

    @property
    def corpus_size(self) -> int:
        """Get the number of documents in the corpus."""
        return len(self._corpus) if self._corpus else 0

    @property
    def average_doc_length(self) -> float:
        """Get average document length in the corpus."""
        if not self._bm25:
            return 0.0
        return self._bm25.avgdl
