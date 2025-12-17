"""Tests for ranking models."""

import numpy as np
import pytest

from ltr_lib.rankers import BaseRanker, LambdaMARTRanker, BM25Ranker


class TestLambdaMARTRanker:
    """Tests for LambdaMART ranker."""

    @pytest.fixture
    def sample_data(self):
        """Create sample training data."""
        np.random.seed(42)
        n_samples = 100
        n_features = 10
        n_queries = 5

        X = np.random.rand(n_samples, n_features)
        y = np.random.randint(0, 4, n_samples)
        groups = np.array([20] * n_queries)

        return X, y, groups

    def test_init(self):
        """Test ranker initialization."""
        ranker = LambdaMARTRanker(learning_rate=0.1, n_estimators=50)
        assert ranker.learning_rate == 0.1
        assert ranker.n_estimators == 50
        assert not ranker.is_fitted

    def test_fit(self, sample_data):
        """Test model fitting."""
        X, y, groups = sample_data
        ranker = LambdaMARTRanker(n_estimators=10, verbose=-1)
        ranker.fit(X, y, groups)

        assert ranker.is_fitted
        assert ranker.model is not None

    def test_predict(self, sample_data):
        """Test prediction."""
        X, y, groups = sample_data
        ranker = LambdaMARTRanker(n_estimators=10, verbose=-1)
        ranker.fit(X, y, groups)

        predictions = ranker.predict(X)
        assert predictions.shape == (len(X),)
        assert not np.any(np.isnan(predictions))

    def test_predict_before_fit(self, sample_data):
        """Predict before fit should raise error."""
        X, _, _ = sample_data
        ranker = LambdaMARTRanker()

        with pytest.raises(ValueError, match="fitted"):
            ranker.predict(X)

    def test_score(self, sample_data):
        """Test scoring."""
        X, y, groups = sample_data
        ranker = LambdaMARTRanker(n_estimators=10, verbose=-1)
        ranker.fit(X, y, groups)

        ndcg = ranker.score(X, y, groups, metric="ndcg", k=5)
        assert 0.0 <= ndcg <= 1.0

    def test_get_params(self):
        """Test get_params."""
        ranker = LambdaMARTRanker(learning_rate=0.1, n_estimators=50)
        params = ranker.get_params()

        assert params["learning_rate"] == 0.1
        assert params["n_estimators"] == 50

    def test_feature_importance(self, sample_data):
        """Test feature importance extraction."""
        X, y, groups = sample_data
        ranker = LambdaMARTRanker(n_estimators=10, verbose=-1)
        ranker.fit(X, y, groups)

        importance = ranker.get_feature_importance()
        assert len(importance) == X.shape[1]


class TestBM25Ranker:
    """Tests for BM25 ranker."""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents."""
        return [
            "the quick brown fox jumps over the lazy dog",
            "a quick brown dog outpaces a quick fox",
            "the lazy dog sleeps all day",
            "foxes are quick and clever animals",
            "dogs are loyal and friendly pets",
        ]

    def test_init(self):
        """Test ranker initialization."""
        ranker = BM25Ranker(k1=1.5, b=0.75)
        assert ranker.k1 == 1.5
        assert ranker.b == 0.75
        assert not ranker.is_fitted

    def test_fit(self, sample_documents):
        """Test model fitting."""
        ranker = BM25Ranker()
        ranker.fit(sample_documents)

        assert ranker.is_fitted
        assert ranker.corpus_size == len(sample_documents)

    def test_predict(self, sample_documents):
        """Test prediction."""
        ranker = BM25Ranker()
        ranker.fit(sample_documents)

        scores = ranker.predict("quick fox")
        assert scores.shape == (len(sample_documents),)
        assert not np.any(np.isnan(scores))

    def test_rank(self, sample_documents):
        """Test ranking."""
        ranker = BM25Ranker()
        ranker.fit(sample_documents)

        ranked = ranker.rank("quick fox", top_k=3)
        assert len(ranked) == 3
        assert all(isinstance(r, tuple) for r in ranked)

    def test_predict_before_fit(self):
        """Predict before fit should raise error."""
        ranker = BM25Ranker()

        with pytest.raises(ValueError, match="fitted"):
            ranker.predict("query")


class TestBaseRanker:
    """Tests for BaseRanker interface."""

    def test_abstract_methods(self):
        """BaseRanker should not be instantiable."""

        class IncompleteRanker(BaseRanker):
            pass

        with pytest.raises(TypeError):
            IncompleteRanker()

    def test_complete_implementation(self):
        """Complete implementation should be instantiable."""

        class ConcreteRanker(BaseRanker):
            def fit(self, X, y, groups, **kwargs):
                self._is_fitted = True
                return self

            def predict(self, X):
                return np.zeros(len(X))

            def score(self, X, y, groups, metric="ndcg", k=10):
                return 0.5

        ranker = ConcreteRanker(name="test")
        assert ranker.name == "test"
        assert not ranker.is_fitted
