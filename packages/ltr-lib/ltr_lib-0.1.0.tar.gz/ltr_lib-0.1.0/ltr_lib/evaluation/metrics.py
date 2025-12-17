"""Ranking evaluation metrics."""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np


def dcg_at_k(relevances: np.ndarray, k: int = 10) -> float:
    """Compute Discounted Cumulative Gain at k.

    DCG = sum_{i=1}^{k} (2^{rel_i} - 1) / log_2(i + 1)

    Args:
        relevances: Array of relevance scores in rank order
        k: Cutoff position

    Returns:
        dcg: DCG value at k
    """
    relevances = np.asarray(relevances)[:k]
    if len(relevances) == 0:
        return 0.0

    gains = 2 ** relevances - 1
    discounts = np.log2(np.arange(1, len(relevances) + 1) + 1)

    return np.sum(gains / discounts)


def ndcg_at_k(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k: int = 10
) -> float:
    """Compute Normalized Discounted Cumulative Gain at k.

    NDCG = DCG / IDCG where IDCG is the ideal (maximum possible) DCG.

    Args:
        y_true: True relevance labels
        y_pred: Predicted scores (higher = more relevant)
        k: Cutoff position

    Returns:
        ndcg: NDCG value at k (0 to 1)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    order = np.argsort(y_pred)[::-1]
    y_true_sorted = y_true[order]

    dcg = dcg_at_k(y_true_sorted, k)

    ideal_order = np.argsort(y_true)[::-1]
    y_true_ideal = y_true[ideal_order]
    idcg = dcg_at_k(y_true_ideal, k)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def precision_at_k(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k: int = 10,
    relevance_threshold: float = 0.5
) -> float:
    """Compute Precision at k.

    Precision@k = (# relevant items in top k) / k

    Args:
        y_true: True relevance labels
        y_pred: Predicted scores
        k: Cutoff position
        relevance_threshold: Threshold for considering item relevant

    Returns:
        precision: Precision at k (0 to 1)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    order = np.argsort(y_pred)[::-1][:k]
    relevant = y_true[order] > relevance_threshold

    return np.sum(relevant) / min(k, len(y_true))


def recall_at_k(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k: int = 10,
    relevance_threshold: float = 0.5
) -> float:
    """Compute Recall at k.

    Recall@k = (# relevant items in top k) / (total relevant items)

    Args:
        y_true: True relevance labels
        y_pred: Predicted scores
        k: Cutoff position
        relevance_threshold: Threshold for considering item relevant

    Returns:
        recall: Recall at k (0 to 1)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    total_relevant = np.sum(y_true > relevance_threshold)
    if total_relevant == 0:
        return 0.0

    order = np.argsort(y_pred)[::-1][:k]
    relevant_at_k = np.sum(y_true[order] > relevance_threshold)

    return relevant_at_k / total_relevant


def average_precision(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    relevance_threshold: float = 0.5
) -> float:
    """Compute Average Precision.

    AP = (1/R) * sum_{k=1}^{n} P(k) * rel(k)
    where R is total relevant items and rel(k) is 1 if item at k is relevant.

    Args:
        y_true: True relevance labels
        y_pred: Predicted scores
        relevance_threshold: Threshold for considering item relevant

    Returns:
        ap: Average precision (0 to 1)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    order = np.argsort(y_pred)[::-1]
    y_true_sorted = y_true[order]

    relevant = y_true_sorted > relevance_threshold
    total_relevant = np.sum(relevant)

    if total_relevant == 0:
        return 0.0

    precision_sum = 0.0
    relevant_count = 0

    for i, is_relevant in enumerate(relevant):
        if is_relevant:
            relevant_count += 1
            precision_sum += relevant_count / (i + 1)

    return precision_sum / total_relevant


def mean_average_precision(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    relevance_threshold: float = 0.5
) -> float:
    """Compute Mean Average Precision (alias for average_precision).

    For a single query, this is equivalent to Average Precision.
    For multiple queries, use evaluate_ranking to get MAP.

    Args:
        y_true: True relevance labels
        y_pred: Predicted scores
        relevance_threshold: Threshold for considering item relevant

    Returns:
        map: Mean average precision (0 to 1)
    """
    return average_precision(y_true, y_pred, relevance_threshold)


def mrr(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    relevance_threshold: float = 0.5
) -> float:
    """Compute Mean Reciprocal Rank.

    MRR = 1 / rank_of_first_relevant_item

    Args:
        y_true: True relevance labels
        y_pred: Predicted scores
        relevance_threshold: Threshold for considering item relevant

    Returns:
        mrr: Reciprocal rank (0 to 1)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    order = np.argsort(y_pred)[::-1]
    y_true_sorted = y_true[order]

    relevant_positions = np.where(y_true_sorted > relevance_threshold)[0]

    if len(relevant_positions) == 0:
        return 0.0

    return 1.0 / (relevant_positions[0] + 1)


def err(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    max_grade: int = 3
) -> float:
    """Compute Expected Reciprocal Rank.

    ERR models the probability that a user finds a relevant document
    at each position, accounting for earlier documents already examined.

    Args:
        y_true: True relevance grades (0 to max_grade)
        y_pred: Predicted scores
        max_grade: Maximum possible relevance grade

    Returns:
        err: Expected reciprocal rank
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    order = np.argsort(y_pred)[::-1]
    y_true_sorted = y_true[order]

    probability_of_relevance = (2 ** y_true_sorted - 1) / (2 ** max_grade)

    err_value = 0.0
    probability_of_reaching = 1.0

    for i, p_rel in enumerate(probability_of_relevance):
        err_value += probability_of_reaching * p_rel / (i + 1)
        probability_of_reaching *= (1 - p_rel)

    return err_value


class RankingEvaluator:
    """Evaluator for ranking models.

    Computes multiple ranking metrics across queries and provides
    aggregate statistics.

    Example:
        >>> evaluator = RankingEvaluator(k=10)
        >>> results = evaluator.evaluate(y_true_groups, y_pred_groups)
        >>> print(results['ndcg_mean'])
    """

    def __init__(
        self,
        k: int = 10,
        relevance_threshold: float = 0.5,
        metrics: Optional[List[str]] = None
    ):
        """Initialize evaluator.

        Args:
            k: Cutoff position for @k metrics
            relevance_threshold: Threshold for binary relevance
            metrics: List of metrics to compute (default: all)
        """
        self.k = k
        self.relevance_threshold = relevance_threshold
        self.metrics = metrics or [
            "ndcg", "precision", "recall", "map", "mrr", "err"
        ]

        self._metric_functions = {
            "ndcg": lambda y, p: ndcg_at_k(y, p, self.k),
            "precision": lambda y, p: precision_at_k(y, p, self.k, self.relevance_threshold),
            "recall": lambda y, p: recall_at_k(y, p, self.k, self.relevance_threshold),
            "map": lambda y, p: mean_average_precision(y, p, self.relevance_threshold),
            "mrr": lambda y, p: mrr(y, p, self.relevance_threshold),
            "err": lambda y, p: err(y, p),
        }

    def evaluate_query(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Evaluate metrics for a single query.

        Args:
            y_true: True relevance labels
            y_pred: Predicted scores

        Returns:
            metrics: Dictionary of metric values
        """
        results = {}
        for metric in self.metrics:
            if metric in self._metric_functions:
                results[metric] = self._metric_functions[metric](y_true, y_pred)
        return results

    def evaluate(
        self,
        y_true_groups: List[np.ndarray],
        y_pred_groups: List[np.ndarray]
    ) -> Dict[str, float]:
        """Evaluate metrics across multiple queries.

        Args:
            y_true_groups: List of true relevance arrays per query
            y_pred_groups: List of predicted score arrays per query

        Returns:
            results: Dictionary with mean, std, and per-query metrics
        """
        all_results = {metric: [] for metric in self.metrics}

        for y_true, y_pred in zip(y_true_groups, y_pred_groups):
            query_results = self.evaluate_query(y_true, y_pred)
            for metric, value in query_results.items():
                all_results[metric].append(value)

        results = {}
        for metric in self.metrics:
            values = np.array(all_results[metric])
            results[f"{metric}_mean"] = np.mean(values)
            results[f"{metric}_std"] = np.std(values)
            results[f"{metric}_values"] = values

        return results

    def evaluate_from_groups(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        groups: np.ndarray
    ) -> Dict[str, float]:
        """Evaluate metrics using group-based data format.

        Args:
            y_true: All true relevance labels
            y_pred: All predicted scores
            groups: Array of group sizes

        Returns:
            results: Dictionary with aggregate metrics
        """
        y_true_groups = []
        y_pred_groups = []

        start = 0
        for size in groups:
            end = start + size
            y_true_groups.append(y_true[start:end])
            y_pred_groups.append(y_pred[start:end])
            start = end

        return self.evaluate(y_true_groups, y_pred_groups)


def evaluate_ranking(
    y_true_groups: List[np.ndarray],
    y_pred_groups: List[np.ndarray],
    k: int = 10
) -> Dict[str, float]:
    """Convenience function to evaluate ranking metrics.

    Args:
        y_true_groups: List of true relevance arrays per query
        y_pred_groups: List of predicted score arrays per query
        k: Cutoff position

    Returns:
        results: Dictionary with NDCG, MAP, and Precision at k
    """
    evaluator = RankingEvaluator(k=k, metrics=["ndcg", "map", "precision"])
    return evaluator.evaluate(y_true_groups, y_pred_groups)
