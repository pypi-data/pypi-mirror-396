"""Feature engineering utilities for ranking models."""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFFeatureExtractor:
    """Extract TF-IDF based similarity features.

    Computes TF-IDF vectors for documents and calculates similarity
    between user profiles and candidate documents.

    Example:
        >>> extractor = TFIDFFeatureExtractor()
        >>> extractor.fit(documents)
        >>> user_profile = "action adventure sci-fi"
        >>> scores = extractor.get_similarity_scores(user_profile)
    """

    def __init__(
        self,
        max_features: Optional[int] = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 2,
        max_df: float = 0.95,
        stop_words: str = "english"
    ):
        """Initialize TF-IDF extractor.

        Args:
            max_features: Maximum vocabulary size
            ngram_range: Range of n-gram sizes
            min_df: Minimum document frequency
            max_df: Maximum document frequency (proportion)
            stop_words: Stop words to remove
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            stop_words=stop_words
        )
        self._doc_vectors: Optional[np.ndarray] = None
        self._is_fitted = False

    def fit(self, documents: List[str]) -> "TFIDFFeatureExtractor":
        """Fit TF-IDF vectorizer on documents.

        Args:
            documents: List of document strings

        Returns:
            self: The fitted extractor
        """
        self._doc_vectors = self.vectorizer.fit_transform(documents)
        self._is_fitted = True
        return self

    def transform(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Transform texts to TF-IDF vectors.

        Args:
            texts: Text(s) to transform

        Returns:
            vectors: TF-IDF vectors
        """
        if not self._is_fitted:
            raise ValueError("Extractor must be fitted first")

        if isinstance(texts, str):
            texts = [texts]

        return self.vectorizer.transform(texts)

    def get_similarity_scores(
        self,
        query: Union[str, np.ndarray],
        doc_indices: Optional[List[int]] = None
    ) -> np.ndarray:
        """Get similarity scores between query and documents.

        Args:
            query: Query text or precomputed query vector
            doc_indices: Specific document indices to score (None for all)

        Returns:
            scores: Cosine similarity scores
        """
        if not self._is_fitted:
            raise ValueError("Extractor must be fitted first")

        if isinstance(query, str):
            query_vec = self.transform(query)
        else:
            query_vec = query

        if doc_indices is not None:
            doc_vecs = self._doc_vectors[doc_indices]
        else:
            doc_vecs = self._doc_vectors

        return cosine_similarity(query_vec, doc_vecs).flatten()

    @property
    def vocabulary_size(self) -> int:
        """Get vocabulary size."""
        return len(self.vectorizer.vocabulary_) if self._is_fitted else 0

    @property
    def document_vectors(self) -> Optional[np.ndarray]:
        """Get document TF-IDF vectors."""
        return self._doc_vectors


class PopularityFeatureExtractor:
    """Extract popularity-based features from rating data.

    Computes various popularity metrics for items based on
    aggregate rating statistics.

    Features computed:
        - num_ratings: Number of ratings received
        - avg_rating: Mean rating value
        - std_rating: Standard deviation of ratings
        - num_users: Number of unique users who rated
        - popularity_score: Composite popularity metric
    """

    def __init__(self):
        self._item_stats: Optional[pd.DataFrame] = None
        self._is_fitted = False

    def fit(
        self,
        ratings: pd.DataFrame,
        item_col: str = "movie_id",
        rating_col: str = "rating",
        user_col: str = "user_id"
    ) -> "PopularityFeatureExtractor":
        """Compute popularity statistics from ratings.

        Args:
            ratings: DataFrame with rating data
            item_col: Column name for item IDs
            rating_col: Column name for ratings
            user_col: Column name for user IDs

        Returns:
            self: The fitted extractor
        """
        stats = ratings.groupby(item_col).agg({
            rating_col: ["count", "mean", "std"],
            user_col: "nunique"
        })

        stats.columns = ["num_ratings", "avg_rating", "std_rating", "num_users"]
        stats["std_rating"] = stats["std_rating"].fillna(0)
        stats["popularity_score"] = stats["num_ratings"] * stats["avg_rating"]

        self._item_stats = stats
        self._is_fitted = True

        return self

    def transform(
        self,
        item_ids: Union[List, np.ndarray, pd.Series]
    ) -> pd.DataFrame:
        """Get popularity features for items.

        Args:
            item_ids: Item IDs to get features for

        Returns:
            features: DataFrame with popularity features
        """
        if not self._is_fitted:
            raise ValueError("Extractor must be fitted first")

        features = self._item_stats.reindex(item_ids)
        features = features.fillna({
            "num_ratings": 0,
            "avg_rating": self._item_stats["avg_rating"].mean(),
            "std_rating": 0,
            "num_users": 0,
            "popularity_score": 0
        })

        return features.reset_index(drop=True)

    def get_feature_names(self) -> List[str]:
        """Get feature column names."""
        return ["num_ratings", "avg_rating", "std_rating", "num_users", "popularity_score"]

    @property
    def item_statistics(self) -> Optional[pd.DataFrame]:
        """Get computed item statistics."""
        return self._item_stats


class UserEngagementFeatureExtractor:
    """Extract user engagement and behavior features.

    Computes user-level activity statistics that can be used
    as features for personalized ranking.

    Features computed:
        - user_num_ratings: Total ratings by user
        - user_avg_rating: User's average rating
        - user_std_rating: User's rating variance
        - user_num_movies: Unique items rated by user
    """

    def __init__(self):
        self._user_stats: Optional[pd.DataFrame] = None
        self._is_fitted = False

    def fit(
        self,
        ratings: pd.DataFrame,
        user_col: str = "user_id",
        item_col: str = "movie_id",
        rating_col: str = "rating"
    ) -> "UserEngagementFeatureExtractor":
        """Compute user engagement statistics.

        Args:
            ratings: DataFrame with rating data
            user_col: Column name for user IDs
            item_col: Column name for item IDs
            rating_col: Column name for ratings

        Returns:
            self: The fitted extractor
        """
        stats = ratings.groupby(user_col).agg({
            rating_col: ["count", "mean", "std"],
            item_col: "nunique"
        })

        stats.columns = [
            "user_num_ratings", "user_avg_rating",
            "user_std_rating", "user_num_movies"
        ]
        stats["user_std_rating"] = stats["user_std_rating"].fillna(0)

        self._user_stats = stats
        self._is_fitted = True

        return self

    def transform(
        self,
        user_ids: Union[List, np.ndarray, pd.Series]
    ) -> pd.DataFrame:
        """Get engagement features for users.

        Args:
            user_ids: User IDs to get features for

        Returns:
            features: DataFrame with engagement features
        """
        if not self._is_fitted:
            raise ValueError("Extractor must be fitted first")

        features = self._user_stats.reindex(user_ids)
        features = features.fillna({
            "user_num_ratings": 0,
            "user_avg_rating": self._user_stats["user_avg_rating"].mean(),
            "user_std_rating": 0,
            "user_num_movies": 0
        })

        return features.reset_index(drop=True)

    def get_feature_names(self) -> List[str]:
        """Get feature column names."""
        return ["user_num_ratings", "user_avg_rating", "user_std_rating", "user_num_movies"]


class GenreFeatureExtractor:
    """Extract genre-based binary features.

    Creates one-hot encoded features for item genres.
    """

    def __init__(self, separator: str = "|"):
        """Initialize genre extractor.

        Args:
            separator: Character separating multiple genres
        """
        self.separator = separator
        self._all_genres: Optional[List[str]] = None
        self._is_fitted = False

    def fit(
        self,
        genres: Union[List[str], pd.Series]
    ) -> "GenreFeatureExtractor":
        """Learn all unique genres.

        Args:
            genres: Genre strings (e.g., "Action|Comedy|Drama")

        Returns:
            self: The fitted extractor
        """
        all_genres = set()
        for g in genres:
            if pd.notna(g) and g:
                all_genres.update(g.split(self.separator))

        self._all_genres = sorted(all_genres)
        self._is_fitted = True

        return self

    def transform(
        self,
        genres: Union[List[str], pd.Series]
    ) -> pd.DataFrame:
        """Convert genre strings to binary features.

        Args:
            genres: Genre strings to transform

        Returns:
            features: DataFrame with binary genre columns
        """
        if not self._is_fitted:
            raise ValueError("Extractor must be fitted first")

        features = pd.DataFrame(0, index=range(len(genres)), columns=self._all_genres)

        for i, g in enumerate(genres):
            if pd.notna(g) and g:
                for genre in g.split(self.separator):
                    if genre in self._all_genres:
                        features.loc[i, genre] = 1

        return features

    def get_feature_names(self) -> List[str]:
        """Get genre column names."""
        return self._all_genres or []


class FeaturePipeline:
    """Pipeline for combining multiple feature extractors.

    Combines TF-IDF, popularity, engagement, and genre features
    into a single feature matrix.

    Example:
        >>> pipeline = FeaturePipeline()
        >>> pipeline.fit(ratings, movies, users)
        >>> X, y, groups = pipeline.transform(ratings)
    """

    def __init__(
        self,
        use_tfidf: bool = True,
        use_popularity: bool = True,
        use_engagement: bool = True,
        use_genres: bool = True,
        use_demographics: bool = True,
        liked_threshold: float = 4.0
    ):
        """Initialize feature pipeline.

        Args:
            use_tfidf: Include TF-IDF similarity features
            use_popularity: Include popularity features
            use_engagement: Include user engagement features
            use_genres: Include genre features
            use_demographics: Include user demographic features
            liked_threshold: Rating threshold for "liked" items
        """
        self.use_tfidf = use_tfidf
        self.use_popularity = use_popularity
        self.use_engagement = use_engagement
        self.use_genres = use_genres
        self.use_demographics = use_demographics
        self.liked_threshold = liked_threshold

        self.tfidf_extractor = TFIDFFeatureExtractor() if use_tfidf else None
        self.popularity_extractor = PopularityFeatureExtractor() if use_popularity else None
        self.engagement_extractor = UserEngagementFeatureExtractor() if use_engagement else None
        self.genre_extractor = GenreFeatureExtractor() if use_genres else None

        self._movies: Optional[pd.DataFrame] = None
        self._users: Optional[pd.DataFrame] = None
        self._user_profiles: Optional[Dict] = None
        self._is_fitted = False

    def fit(
        self,
        ratings: pd.DataFrame,
        movies: pd.DataFrame,
        users: Optional[pd.DataFrame] = None
    ) -> "FeaturePipeline":
        """Fit all feature extractors.

        Args:
            ratings: Rating data
            movies: Movie metadata
            users: User metadata (optional)

        Returns:
            self: The fitted pipeline
        """
        self._movies = movies.set_index("movie_id") if "movie_id" in movies.columns else movies
        self._users = users.set_index("user_id") if users is not None and "user_id" in users.columns else users

        if self.use_tfidf:
            documents = self._create_movie_documents(movies)
            self.tfidf_extractor.fit(documents)
            self._user_profiles = self._create_user_profiles(ratings, movies)

        if self.use_popularity:
            self.popularity_extractor.fit(ratings)

        if self.use_engagement:
            self.engagement_extractor.fit(ratings)

        if self.use_genres:
            genres = movies["genres"] if "genres" in movies.columns else pd.Series([""] * len(movies))
            self.genre_extractor.fit(genres)

        self._is_fitted = True
        return self

    def transform(
        self,
        ratings: pd.DataFrame,
        return_groups: bool = True
    ) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
        """Transform ratings into feature matrix.

        Args:
            ratings: Rating data to transform
            return_groups: Whether to return group sizes

        Returns:
            X: Feature matrix
            y: Relevance labels
            groups: Query group sizes (if return_groups=True)
        """
        if not self._is_fitted:
            raise ValueError("Pipeline must be fitted first")

        from ..data.loaders import rating_to_relevance

        features_list = []

        if self.use_tfidf:
            tfidf_scores = self._compute_tfidf_scores(ratings)
            features_list.append(pd.DataFrame({"tfidf_similarity": tfidf_scores}))

        if self.use_popularity:
            pop_features = self.popularity_extractor.transform(ratings["movie_id"])
            features_list.append(pop_features)

        if self.use_engagement:
            eng_features = self.engagement_extractor.transform(ratings["user_id"])
            features_list.append(eng_features)

        if self.use_demographics and self._users is not None:
            demo_features = self._get_demographic_features(ratings["user_id"])
            features_list.append(demo_features)

        if self.use_genres:
            genres = self._movies.loc[ratings["movie_id"], "genres"].values
            genre_features = self.genre_extractor.transform(genres)
            features_list.append(genre_features)

        X = pd.concat(features_list, axis=1).values
        y = ratings["rating"].apply(
            lambda r: rating_to_relevance(r, self.liked_threshold)
        ).values

        if return_groups:
            groups = ratings.groupby("user_id").size().values
            return X, y, groups

        return X, y

    def get_feature_names(self) -> List[str]:
        """Get all feature names."""
        names = []

        if self.use_tfidf:
            names.append("tfidf_similarity")

        if self.use_popularity:
            names.extend(self.popularity_extractor.get_feature_names())

        if self.use_engagement:
            names.extend(self.engagement_extractor.get_feature_names())

        if self.use_demographics:
            names.extend(["age", "gender_encoded"])

        if self.use_genres:
            names.extend(self.genre_extractor.get_feature_names())

        return names

    def _create_movie_documents(self, movies: pd.DataFrame) -> List[str]:
        """Create text documents from movie metadata."""
        documents = []
        for _, row in movies.iterrows():
            title = row.get("title", "")
            genres = row.get("genres", "").replace("|", " ")
            documents.append(f"{title} {genres}")
        return documents

    def _create_user_profiles(
        self,
        ratings: pd.DataFrame,
        movies: pd.DataFrame
    ) -> Dict[int, str]:
        """Create user profile documents from liked movies."""
        profiles = {}
        liked = ratings[ratings["rating"] >= self.liked_threshold]

        movie_docs = dict(zip(
            movies["movie_id"],
            self._create_movie_documents(movies)
        ))

        for user_id, group in liked.groupby("user_id"):
            user_docs = [movie_docs.get(mid, "") for mid in group["movie_id"]]
            profiles[user_id] = " ".join(user_docs)

        return profiles

    def _compute_tfidf_scores(self, ratings: pd.DataFrame) -> np.ndarray:
        """Compute TF-IDF similarity scores for user-movie pairs."""
        scores = np.zeros(len(ratings))

        movie_indices = {
            mid: i for i, mid in enumerate(self._movies.index)
        }

        for user_id, group in ratings.groupby("user_id"):
            profile = self._user_profiles.get(user_id, "")
            if not profile:
                continue

            indices = group.index
            movie_ids = group["movie_id"].values
            doc_indices = [movie_indices.get(mid, 0) for mid in movie_ids]

            user_scores = self.tfidf_extractor.get_similarity_scores(
                profile, doc_indices
            )
            scores[indices] = user_scores

        return scores

    def _get_demographic_features(
        self,
        user_ids: pd.Series
    ) -> pd.DataFrame:
        """Get demographic features for users."""
        features = pd.DataFrame(index=range(len(user_ids)))

        if self._users is not None:
            user_data = self._users.reindex(user_ids)
            features["age"] = user_data["age"].fillna(
                self._users["age"].mean()
            ).values
            features["gender_encoded"] = (
                user_data["gender"].map({"M": 1, "F": 0}).fillna(0.5).values
            )
        else:
            features["age"] = 30
            features["gender_encoded"] = 0.5

        return features
