"""Tests for feature engineering."""

import numpy as np
import pandas as pd
import pytest

from ltr_lib.features import (
    TFIDFFeatureExtractor,
    PopularityFeatureExtractor,
    UserEngagementFeatureExtractor,
    GenreFeatureExtractor,
)


class TestTFIDFFeatureExtractor:
    """Tests for TF-IDF feature extraction."""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents."""
        return [
            "action adventure movie with great stunts",
            "romantic comedy film about love",
            "sci-fi thriller with aliens",
            "drama about family relationships",
            "action comedy with funny scenes",
        ]

    def test_fit(self, sample_documents):
        """Test fitting the extractor."""
        extractor = TFIDFFeatureExtractor(min_df=1)
        extractor.fit(sample_documents)

        assert extractor._is_fitted
        assert extractor.vocabulary_size > 0

    def test_transform(self, sample_documents):
        """Test transforming text."""
        extractor = TFIDFFeatureExtractor(min_df=1)
        extractor.fit(sample_documents)

        vectors = extractor.transform("action movie")
        assert vectors.shape[0] == 1

    def test_similarity_scores(self, sample_documents):
        """Test similarity computation."""
        extractor = TFIDFFeatureExtractor(min_df=1)
        extractor.fit(sample_documents)

        scores = extractor.get_similarity_scores("action movie")
        assert len(scores) == len(sample_documents)
        assert all(0 <= s <= 1 for s in scores)

    def test_similarity_with_indices(self, sample_documents):
        """Test similarity for specific documents."""
        extractor = TFIDFFeatureExtractor(min_df=1)
        extractor.fit(sample_documents)

        scores = extractor.get_similarity_scores("action movie", doc_indices=[0, 4])
        assert len(scores) == 2


class TestPopularityFeatureExtractor:
    """Tests for popularity feature extraction."""

    @pytest.fixture
    def sample_ratings(self):
        """Create sample ratings data."""
        return pd.DataFrame({
            "user_id": [1, 1, 2, 2, 3, 3, 3],
            "movie_id": [1, 2, 1, 3, 1, 2, 3],
            "rating": [5, 4, 4, 3, 5, 3, 4],
        })

    def test_fit(self, sample_ratings):
        """Test fitting the extractor."""
        extractor = PopularityFeatureExtractor()
        extractor.fit(sample_ratings)

        assert extractor._is_fitted
        assert extractor.item_statistics is not None

    def test_transform(self, sample_ratings):
        """Test transforming item IDs."""
        extractor = PopularityFeatureExtractor()
        extractor.fit(sample_ratings)

        features = extractor.transform([1, 2, 3])
        assert len(features) == 3
        assert "num_ratings" in features.columns
        assert "avg_rating" in features.columns

    def test_popularity_values(self, sample_ratings):
        """Test computed popularity values."""
        extractor = PopularityFeatureExtractor()
        extractor.fit(sample_ratings)

        stats = extractor.item_statistics
        # Movie 1 has 3 ratings
        assert stats.loc[1, "num_ratings"] == 3

    def test_feature_names(self, sample_ratings):
        """Test feature name list."""
        extractor = PopularityFeatureExtractor()
        extractor.fit(sample_ratings)

        names = extractor.get_feature_names()
        assert "num_ratings" in names
        assert "avg_rating" in names
        assert "popularity_score" in names


class TestUserEngagementFeatureExtractor:
    """Tests for user engagement feature extraction."""

    @pytest.fixture
    def sample_ratings(self):
        """Create sample ratings data."""
        return pd.DataFrame({
            "user_id": [1, 1, 1, 2, 2, 3],
            "movie_id": [1, 2, 3, 1, 2, 1],
            "rating": [5, 4, 3, 4, 4, 5],
        })

    def test_fit(self, sample_ratings):
        """Test fitting the extractor."""
        extractor = UserEngagementFeatureExtractor()
        extractor.fit(sample_ratings)

        assert extractor._is_fitted

    def test_transform(self, sample_ratings):
        """Test transforming user IDs."""
        extractor = UserEngagementFeatureExtractor()
        extractor.fit(sample_ratings)

        features = extractor.transform([1, 2, 3])
        assert len(features) == 3
        assert "user_num_ratings" in features.columns

    def test_engagement_values(self, sample_ratings):
        """Test computed engagement values."""
        extractor = UserEngagementFeatureExtractor()
        extractor.fit(sample_ratings)

        # User 1 has 3 ratings
        features = extractor.transform([1])
        assert features.iloc[0]["user_num_ratings"] == 3


class TestGenreFeatureExtractor:
    """Tests for genre feature extraction."""

    @pytest.fixture
    def sample_genres(self):
        """Create sample genre strings."""
        return pd.Series([
            "Action|Adventure",
            "Comedy|Romance",
            "Action|Sci-Fi",
            "Drama",
            "Comedy",
        ])

    def test_fit(self, sample_genres):
        """Test fitting the extractor."""
        extractor = GenreFeatureExtractor()
        extractor.fit(sample_genres)

        assert extractor._is_fitted
        assert len(extractor.get_feature_names()) > 0

    def test_transform(self, sample_genres):
        """Test transforming genre strings."""
        extractor = GenreFeatureExtractor()
        extractor.fit(sample_genres)

        features = extractor.transform(sample_genres)
        assert len(features) == len(sample_genres)

    def test_binary_encoding(self, sample_genres):
        """Test that encoding is binary."""
        extractor = GenreFeatureExtractor()
        extractor.fit(sample_genres)

        features = extractor.transform(sample_genres)
        assert features.max().max() == 1
        assert features.min().min() == 0

    def test_genre_coverage(self, sample_genres):
        """Test that all genres are covered."""
        extractor = GenreFeatureExtractor()
        extractor.fit(sample_genres)

        names = extractor.get_feature_names()
        assert "Action" in names
        assert "Comedy" in names
        assert "Romance" in names
