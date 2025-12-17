"""Tests for evaluation metrics."""

import numpy as np
import pytest

from ltr_lib.evaluation import (
    dcg_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    mean_average_precision,
    mrr,
    err,
    RankingEvaluator,
)


class TestDCG:
    """Tests for DCG computation."""

    def test_perfect_ranking(self):
        """DCG should be maximal for perfectly sorted relevances."""
        relevances = np.array([3, 2, 1, 0])
        dcg = dcg_at_k(relevances, k=4)
        assert dcg > 0

    def test_empty_relevances(self):
        """DCG of empty array should be 0."""
        assert dcg_at_k(np.array([]), k=5) == 0.0

    def test_all_zeros(self):
        """DCG should be 0 when all relevances are 0."""
        relevances = np.array([0, 0, 0, 0])
        assert dcg_at_k(relevances, k=4) == 0.0

    def test_k_truncation(self):
        """DCG should only consider first k items."""
        relevances = np.array([3, 2, 1, 0, 5])
        dcg_k3 = dcg_at_k(relevances, k=3)
        dcg_k5 = dcg_at_k(relevances, k=5)
        assert dcg_k3 < dcg_k5


class TestNDCG:
    """Tests for NDCG computation."""

    def test_perfect_ranking(self):
        """NDCG should be 1.0 for perfect ranking."""
        y_true = np.array([3, 2, 1, 0])
        y_pred = np.array([4, 3, 2, 1])  # Higher scores for higher relevance
        ndcg = ndcg_at_k(y_true, y_pred, k=4)
        assert ndcg == pytest.approx(1.0)

    def test_worst_ranking(self):
        """NDCG should be low for reversed ranking."""
        y_true = np.array([3, 2, 1, 0])
        y_pred = np.array([1, 2, 3, 4])  # Reversed
        ndcg = ndcg_at_k(y_true, y_pred, k=4)
        assert ndcg < 1.0

    def test_no_relevant_items(self):
        """NDCG should be 0 when no relevant items."""
        y_true = np.array([0, 0, 0, 0])
        y_pred = np.array([4, 3, 2, 1])
        ndcg = ndcg_at_k(y_true, y_pred, k=4)
        assert ndcg == 0.0

    def test_range(self):
        """NDCG should be between 0 and 1."""
        np.random.seed(42)
        for _ in range(10):
            y_true = np.random.randint(0, 4, size=10)
            y_pred = np.random.rand(10)
            ndcg = ndcg_at_k(y_true, y_pred, k=5)
            assert 0.0 <= ndcg <= 1.0


class TestPrecision:
    """Tests for Precision@k computation."""

    def test_all_relevant(self):
        """Precision should be 1.0 when all top-k are relevant."""
        y_true = np.array([1, 1, 1, 0, 0])
        y_pred = np.array([5, 4, 3, 2, 1])
        precision = precision_at_k(y_true, y_pred, k=3)
        assert precision == pytest.approx(1.0)

    def test_none_relevant(self):
        """Precision should be 0 when no top-k are relevant."""
        y_true = np.array([0, 0, 0, 1, 1])
        y_pred = np.array([5, 4, 3, 2, 1])
        precision = precision_at_k(y_true, y_pred, k=3)
        assert precision == 0.0

    def test_half_relevant(self):
        """Precision should be 0.5 when half of top-k are relevant."""
        y_true = np.array([1, 0, 1, 0])
        y_pred = np.array([4, 3, 2, 1])
        precision = precision_at_k(y_true, y_pred, k=4)
        assert precision == pytest.approx(0.5)


class TestRecall:
    """Tests for Recall@k computation."""

    def test_all_relevant_in_top_k(self):
        """Recall should be 1.0 when all relevant items in top-k."""
        y_true = np.array([1, 1, 0, 0, 0])
        y_pred = np.array([5, 4, 3, 2, 1])
        recall = recall_at_k(y_true, y_pred, k=3)
        assert recall == pytest.approx(1.0)

    def test_no_relevant_items(self):
        """Recall should be 0 when no relevant items exist."""
        y_true = np.array([0, 0, 0, 0])
        y_pred = np.array([4, 3, 2, 1])
        recall = recall_at_k(y_true, y_pred, k=2)
        assert recall == 0.0


class TestMAP:
    """Tests for Mean Average Precision."""

    def test_perfect_ranking(self):
        """MAP should be 1.0 for perfect ranking."""
        y_true = np.array([1, 1, 0, 0])
        y_pred = np.array([4, 3, 2, 1])
        map_score = mean_average_precision(y_true, y_pred)
        assert map_score == pytest.approx(1.0)

    def test_no_relevant_items(self):
        """MAP should be 0 when no relevant items."""
        y_true = np.array([0, 0, 0, 0])
        y_pred = np.array([4, 3, 2, 1])
        map_score = mean_average_precision(y_true, y_pred)
        assert map_score == 0.0


class TestMRR:
    """Tests for Mean Reciprocal Rank."""

    def test_first_is_relevant(self):
        """MRR should be 1.0 when first item is relevant."""
        y_true = np.array([1, 0, 0, 0])
        y_pred = np.array([4, 3, 2, 1])
        assert mrr(y_true, y_pred) == pytest.approx(1.0)

    def test_second_is_relevant(self):
        """MRR should be 0.5 when second item is first relevant."""
        y_true = np.array([0, 1, 0, 0])
        y_pred = np.array([4, 3, 2, 1])
        assert mrr(y_true, y_pred) == pytest.approx(0.5)

    def test_no_relevant(self):
        """MRR should be 0 when no relevant items."""
        y_true = np.array([0, 0, 0, 0])
        y_pred = np.array([4, 3, 2, 1])
        assert mrr(y_true, y_pred) == 0.0


class TestRankingEvaluator:
    """Tests for the RankingEvaluator class."""

    def test_evaluate_single_query(self):
        """Evaluator should work for single query."""
        evaluator = RankingEvaluator(k=3)
        y_true = np.array([3, 2, 1, 0])
        y_pred = np.array([4, 3, 2, 1])

        results = evaluator.evaluate_query(y_true, y_pred)
        assert "ndcg" in results
        assert "precision" in results
        assert "map" in results

    def test_evaluate_multiple_queries(self):
        """Evaluator should aggregate across queries."""
        evaluator = RankingEvaluator(k=3)
        y_true_groups = [
            np.array([3, 2, 1]),
            np.array([1, 2, 3]),
        ]
        y_pred_groups = [
            np.array([3, 2, 1]),
            np.array([1, 2, 3]),
        ]

        results = evaluator.evaluate(y_true_groups, y_pred_groups)
        assert "ndcg_mean" in results
        assert "ndcg_std" in results
        assert "ndcg_values" in results
