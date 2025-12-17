"""Core Learning-to-Rank class with unified API."""

from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from .rankers import BaseRanker, LambdaMARTRanker, BM25Ranker
from .data import MovieLensLoader, MovieLensData, DatasetSplitter, rating_to_relevance
from .features import FeaturePipeline
from .evaluation import RankingEvaluator, evaluate_ranking


class RankerRegistry:
    """Registry for available ranking methods.

    Provides attribute-style access to ranker classes.

    Example:
        >>> registry = RankerRegistry()
        >>> model = registry.lambdamart(learning_rate=0.1)
        >>> model = registry.bm25(k1=1.5)
    """

    def __init__(self):
        self._rankers: Dict[str, Type[BaseRanker]] = {
            "lambdamart": LambdaMARTRanker,
            "bm25": BM25Ranker,
        }

    def __getattr__(self, name: str) -> Type[BaseRanker]:
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

        if name in self._rankers:
            return self._rankers[name]

        raise AttributeError(
            f"Unknown ranker: '{name}'. Available: {list(self._rankers.keys())}"
        )

    def register(self, name: str, ranker_class: Type[BaseRanker]) -> None:
        """Register a custom ranker class.

        Args:
            name: Name for attribute access
            ranker_class: Ranker class (must extend BaseRanker)
        """
        if not issubclass(ranker_class, BaseRanker):
            raise TypeError("ranker_class must be a subclass of BaseRanker")
        self._rankers[name] = ranker_class

    def list_rankers(self) -> List[str]:
        """List all available ranker names."""
        return list(self._rankers.keys())

    def get(self, name: str, **kwargs) -> BaseRanker:
        """Get an instantiated ranker by name.

        Args:
            name: Ranker name
            **kwargs: Parameters to pass to ranker constructor

        Returns:
            ranker: Instantiated ranker
        """
        if name not in self._rankers:
            raise ValueError(f"Unknown ranker: {name}")
        return self._rankers[name](**kwargs)


class LTR:
    """Main Learning-to-Rank interface.

    Provides a unified API for training, evaluating, and using
    ranking models on MovieLens and custom datasets.

    Attributes:
        rankers: Registry of available ranking methods (access via rankers.lambdamart, etc.)
        data_loader: MovieLens data loader
        feature_pipeline: Feature engineering pipeline
        evaluator: Ranking evaluator

    Example:
        >>> ltr = LTR()
        >>> data = ltr.load_movielens('100k')
        >>> X, y, groups = ltr.prepare_features(data)
        >>> model = ltr.rankers.lambdamart(learning_rate=0.05)
        >>> model.fit(X, y, groups)
        >>> results = ltr.evaluate(model, X, y, groups)
    """

    def __init__(
        self,
        data_dir: Optional[str] = None,
        random_state: Optional[int] = None
    ):
        """Initialize LTR system.

        Args:
            data_dir: Directory for storing data (default: ~/.ltr_data)
            random_state: Random seed for reproducibility
        """
        self.rankers = RankerRegistry()
        self.data_loader = MovieLensLoader(data_dir=data_dir)
        self.feature_pipeline: Optional[FeaturePipeline] = None
        self.evaluator = RankingEvaluator()
        self.random_state = random_state

        self._data: Optional[MovieLensData] = None
        self._X: Optional[np.ndarray] = None
        self._y: Optional[np.ndarray] = None
        self._groups: Optional[np.ndarray] = None

    def load_movielens(
        self,
        version: str = "100k",
        download_if_missing: bool = True
    ) -> MovieLensData:
        """Load MovieLens dataset.

        Args:
            version: Dataset version ('100k', '1m', '20m')
            download_if_missing: Download if not found locally

        Returns:
            data: MovieLensData object
        """
        self._data = self.data_loader.load(version, download_if_missing)
        return self._data

    def prepare_features(
        self,
        data: Optional[MovieLensData] = None,
        use_tfidf: bool = True,
        use_popularity: bool = True,
        use_engagement: bool = True,
        use_genres: bool = True,
        use_demographics: bool = True,
        liked_threshold: float = 4.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare feature matrix from data.

        Args:
            data: MovieLensData (uses cached if None)
            use_tfidf: Include TF-IDF similarity features
            use_popularity: Include popularity features
            use_engagement: Include user engagement features
            use_genres: Include genre features
            use_demographics: Include demographic features
            liked_threshold: Rating threshold for "liked" items

        Returns:
            X: Feature matrix
            y: Relevance labels
            groups: Query group sizes
        """
        if data is None:
            data = self._data
        if data is None:
            raise ValueError("No data available. Call load_movielens() first.")

        self.feature_pipeline = FeaturePipeline(
            use_tfidf=use_tfidf,
            use_popularity=use_popularity,
            use_engagement=use_engagement,
            use_genres=use_genres,
            use_demographics=use_demographics,
            liked_threshold=liked_threshold
        )

        self.feature_pipeline.fit(data.ratings, data.movies, data.users)
        self._X, self._y, self._groups = self.feature_pipeline.transform(data.ratings)

        return self._X, self._y, self._groups

    def train(
        self,
        model: BaseRanker,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
        **kwargs
    ) -> BaseRanker:
        """Train a ranking model.

        Args:
            model: Ranker instance to train
            X: Feature matrix (uses cached if None)
            y: Relevance labels (uses cached if None)
            groups: Query group sizes (uses cached if None)
            **kwargs: Additional parameters passed to model.fit()

        Returns:
            model: The trained model
        """
        X = X if X is not None else self._X
        y = y if y is not None else self._y
        groups = groups if groups is not None else self._groups

        if X is None or y is None or groups is None:
            raise ValueError("No data available. Call prepare_features() first.")

        if self.feature_pipeline:
            model.feature_names = self.feature_pipeline.get_feature_names()

        model.fit(X, y, groups, **kwargs)
        return model

    def evaluate(
        self,
        model: BaseRanker,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
        k: int = 10,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Evaluate a trained model.

        Args:
            model: Trained ranker
            X: Feature matrix (uses cached if None)
            y: True relevance labels (uses cached if None)
            groups: Query group sizes (uses cached if None)
            k: Cutoff for @k metrics
            metrics: List of metrics to compute

        Returns:
            results: Dictionary of metric values
        """
        X = X if X is not None else self._X
        y = y if y is not None else self._y
        groups = groups if groups is not None else self._groups

        if X is None or y is None or groups is None:
            raise ValueError("No data available. Call prepare_features() first.")

        predictions = model.predict(X)

        evaluator = RankingEvaluator(
            k=k,
            metrics=metrics or ["ndcg", "precision", "map", "mrr"]
        )

        return evaluator.evaluate_from_groups(y, predictions, groups)

    def cross_validate(
        self,
        model: BaseRanker,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
        n_folds: int = 5,
        k: int = 10,
        return_models: bool = False
    ) -> Dict[str, Any]:
        """Perform cross-validation.

        Args:
            model: Ranker instance (will be cloned for each fold)
            X: Feature matrix
            y: Relevance labels
            groups: Query group sizes
            n_folds: Number of CV folds
            k: Cutoff for @k metrics
            return_models: Whether to return trained models

        Returns:
            results: Dictionary with fold-level and aggregate metrics
        """
        X = X if X is not None else self._X
        y = y if y is not None else self._y
        groups = groups if groups is not None else self._groups

        if X is None or y is None or groups is None:
            raise ValueError("No data available. Call prepare_features() first.")

        user_ids = np.repeat(np.arange(len(groups)), groups)

        gkf = GroupKFold(n_splits=n_folds)

        fold_results = []
        models = []

        for fold_idx, (train_idx, test_idx) in enumerate(gkf.split(X, y, user_ids)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            train_user_ids = user_ids[train_idx]
            test_user_ids = user_ids[test_idx]

            train_groups = np.array([
                np.sum(train_user_ids == u)
                for u in np.unique(train_user_ids)
            ])
            test_groups = np.array([
                np.sum(test_user_ids == u)
                for u in np.unique(test_user_ids)
            ])

            fold_model = model.__class__(**model.get_params())

            if self.feature_pipeline:
                fold_model.feature_names = self.feature_pipeline.get_feature_names()

            fold_model.fit(X_train, y_train, train_groups)

            predictions = fold_model.predict(X_test)

            evaluator = RankingEvaluator(k=k)
            fold_metrics = evaluator.evaluate_from_groups(y_test, predictions, test_groups)

            fold_results.append({
                "fold": fold_idx,
                "ndcg": fold_metrics["ndcg_mean"],
                "precision": fold_metrics["precision_mean"],
                "map": fold_metrics["map_mean"],
            })

            if return_models:
                models.append(fold_model)

        results = {
            "fold_results": fold_results,
            "ndcg_mean": np.mean([r["ndcg"] for r in fold_results]),
            "ndcg_std": np.std([r["ndcg"] for r in fold_results]),
            "precision_mean": np.mean([r["precision"] for r in fold_results]),
            "precision_std": np.std([r["precision"] for r in fold_results]),
            "map_mean": np.mean([r["map"] for r in fold_results]),
            "map_std": np.std([r["map"] for r in fold_results]),
        }

        if return_models:
            results["models"] = models

        return results

    def train_test_split(
        self,
        test_size: float = 0.2,
        by_user: bool = True
    ) -> Tuple[Tuple[np.ndarray, np.ndarray, np.ndarray],
               Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Split data into train and test sets.

        Args:
            test_size: Fraction of data for testing
            by_user: If True, split within each user's ratings

        Returns:
            train_data: (X_train, y_train, groups_train)
            test_data: (X_test, y_test, groups_test)
        """
        if self._data is None:
            raise ValueError("No data available. Call load_movielens() first.")

        train_ratings, test_ratings = DatasetSplitter.train_test_split(
            self._data.ratings,
            test_size=test_size,
            random_state=self.random_state,
            by_user=by_user
        )

        X_train, y_train, groups_train = self.feature_pipeline.transform(train_ratings)
        X_test, y_test, groups_test = self.feature_pipeline.transform(test_ratings)

        return (X_train, y_train, groups_train), (X_test, y_test, groups_test)

    def compare_models(
        self,
        models: List[BaseRanker],
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
        n_folds: int = 5,
        k: int = 10
    ) -> pd.DataFrame:
        """Compare multiple models using cross-validation.

        Args:
            models: List of ranker instances to compare
            X: Feature matrix
            y: Relevance labels
            groups: Query group sizes
            n_folds: Number of CV folds
            k: Cutoff for @k metrics

        Returns:
            comparison: DataFrame with model comparison results
        """
        results = []

        for model in models:
            cv_results = self.cross_validate(
                model, X, y, groups, n_folds=n_folds, k=k
            )

            results.append({
                "model": model.name,
                "ndcg_mean": cv_results["ndcg_mean"],
                "ndcg_std": cv_results["ndcg_std"],
                "precision_mean": cv_results["precision_mean"],
                "precision_std": cv_results["precision_std"],
                "map_mean": cv_results["map_mean"],
                "map_std": cv_results["map_std"],
            })

        return pd.DataFrame(results)

    def get_feature_names(self) -> Optional[List[str]]:
        """Get feature names from the pipeline."""
        if self.feature_pipeline:
            return self.feature_pipeline.get_feature_names()
        return None

    @property
    def data(self) -> Optional[MovieLensData]:
        """Get loaded data."""
        return self._data

    @property
    def feature_matrix(self) -> Optional[np.ndarray]:
        """Get prepared feature matrix."""
        return self._X

    @property
    def labels(self) -> Optional[np.ndarray]:
        """Get prepared labels."""
        return self._y

    @property
    def query_groups(self) -> Optional[np.ndarray]:
        """Get query group sizes."""
        return self._groups
