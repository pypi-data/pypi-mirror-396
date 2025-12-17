"""LambdaMART ranking model using LightGBM."""

from typing import Any, Dict, List, Optional, Union

import lightgbm as lgb
import numpy as np

from .base import BaseRanker, RankerMixin


class LambdaMARTRanker(BaseRanker, RankerMixin):
    """LambdaMART ranking model implemented with LightGBM.

    LambdaMART is a pairwise learning-to-rank algorithm that uses
    gradient boosted decision trees to optimize ranking metrics directly.

    Attributes:
        learning_rate: Boosting learning rate
        num_leaves: Maximum number of leaves in one tree
        max_depth: Maximum tree depth (-1 for no limit)
        n_estimators: Number of boosting iterations
        min_child_samples: Minimum samples in a leaf
        feature_fraction: Fraction of features for each tree
        bagging_fraction: Fraction of data for each tree
        bagging_freq: Frequency for bagging (0 disables)
        ndcg_at: Positions to evaluate NDCG during training
        verbose: Verbosity level (-1 for silent)
    """

    def __init__(
        self,
        learning_rate: float = 0.05,
        num_leaves: int = 31,
        max_depth: int = 6,
        n_estimators: int = 100,
        min_child_samples: int = 20,
        feature_fraction: float = 0.8,
        bagging_fraction: float = 0.8,
        bagging_freq: int = 5,
        ndcg_at: List[int] = None,
        verbose: int = -1,
        random_state: Optional[int] = None,
        name: str = "LambdaMART"
    ):
        super().__init__(name=name)
        self.learning_rate = learning_rate
        self.num_leaves = num_leaves
        self.max_depth = max_depth
        self.n_estimators = n_estimators
        self.min_child_samples = min_child_samples
        self.feature_fraction = feature_fraction
        self.bagging_fraction = bagging_fraction
        self.bagging_freq = bagging_freq
        self.ndcg_at = ndcg_at or [10]
        self.verbose = verbose
        self.random_state = random_state

        self._model: Optional[lgb.Booster] = None
        self._feature_importance: Optional[np.ndarray] = None

    def _get_lgb_params(self) -> Dict[str, Any]:
        """Get LightGBM parameters dictionary."""
        return {
            "objective": "lambdarank",
            "metric": "ndcg",
            "ndcg_eval_at": self.ndcg_at,
            "learning_rate": self.learning_rate,
            "num_leaves": self.num_leaves,
            "max_depth": self.max_depth,
            "min_data_in_leaf": self.min_child_samples,
            "feature_fraction": self.feature_fraction,
            "bagging_fraction": self.bagging_fraction,
            "bagging_freq": self.bagging_freq,
            "verbose": self.verbose,
            "seed": self.random_state,
        }

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        groups_val: Optional[np.ndarray] = None,
        early_stopping_rounds: Optional[int] = None,
        callbacks: Optional[List] = None,
        **kwargs
    ) -> "LambdaMARTRanker":
        """Fit the LambdaMART model.

        Args:
            X: Training feature matrix
            y: Training relevance labels
            groups: Training query group sizes
            X_val: Validation feature matrix (optional)
            y_val: Validation relevance labels (optional)
            groups_val: Validation query group sizes (optional)
            early_stopping_rounds: Stop if no improvement (optional)
            callbacks: LightGBM callbacks (optional)
            **kwargs: Additional parameters passed to lgb.train

        Returns:
            self: The fitted ranker
        """
        self.validate_inputs(X, y, groups)

        train_set = lgb.Dataset(
            X, label=y, group=groups.tolist(),
            feature_name=self._feature_names
        )

        valid_sets = [train_set]
        valid_names = ["train"]

        if X_val is not None and y_val is not None and groups_val is not None:
            self.validate_inputs(X_val, y_val, groups_val)
            val_set = lgb.Dataset(
                X_val, label=y_val, group=groups_val.tolist(),
                reference=train_set
            )
            valid_sets.append(val_set)
            valid_names.append("valid")

        params = self._get_lgb_params()
        train_kwargs = {
            "params": params,
            "train_set": train_set,
            "num_boost_round": self.n_estimators,
            "valid_sets": valid_sets,
            "valid_names": valid_names,
        }

        if callbacks:
            train_kwargs["callbacks"] = callbacks

        if early_stopping_rounds and len(valid_sets) > 1:
            train_kwargs["callbacks"] = train_kwargs.get("callbacks", []) + [
                lgb.early_stopping(early_stopping_rounds, verbose=self.verbose > 0)
            ]

        train_kwargs.update(kwargs)
        self._model = lgb.train(**train_kwargs)
        self._is_fitted = True
        self._feature_importance = self._model.feature_importance(importance_type="gain")

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict relevance scores.

        Args:
            X: Feature matrix

        Returns:
            scores: Predicted relevance scores
        """
        if not self._is_fitted:
            raise ValueError("Model must be fitted before prediction")

        return self._model.predict(X)

    def score(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: np.ndarray,
        metric: str = "ndcg",
        k: int = 10
    ) -> float:
        """Compute ranking metric.

        Args:
            X: Feature matrix
            y: True relevance labels
            groups: Query group sizes
            metric: Metric name ('ndcg', 'map', 'precision')
            k: Cutoff for metric computation

        Returns:
            score: The computed metric value
        """
        from ..evaluation.metrics import ndcg_at_k, mean_average_precision, precision_at_k

        predictions = self.predict(X)
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

    def get_feature_importance(
        self,
        importance_type: str = "gain"
    ) -> Dict[str, float]:
        """Get feature importance scores.

        Args:
            importance_type: Type of importance ('gain', 'split')

        Returns:
            importance: Dictionary mapping feature names to importance scores
        """
        if not self._is_fitted:
            raise ValueError("Model must be fitted first")

        importance = self._model.feature_importance(importance_type=importance_type)

        if self._feature_names:
            return dict(zip(self._feature_names, importance))
        return dict(enumerate(importance))

    def get_params(self) -> Dict[str, Any]:
        """Get model parameters."""
        params = super().get_params()
        params.update({
            "learning_rate": self.learning_rate,
            "num_leaves": self.num_leaves,
            "max_depth": self.max_depth,
            "n_estimators": self.n_estimators,
            "min_child_samples": self.min_child_samples,
            "feature_fraction": self.feature_fraction,
            "bagging_fraction": self.bagging_fraction,
            "bagging_freq": self.bagging_freq,
            "ndcg_at": self.ndcg_at,
            "random_state": self.random_state,
        })
        return params

    def save(self, path: str) -> None:
        """Save model to file.

        Args:
            path: File path to save model
        """
        if not self._is_fitted:
            raise ValueError("Model must be fitted before saving")
        self._model.save_model(path)

    def load(self, path: str) -> "LambdaMARTRanker":
        """Load model from file.

        Args:
            path: File path to load model from

        Returns:
            self: The loaded ranker
        """
        self._model = lgb.Booster(model_file=path)
        self._is_fitted = True
        return self

    @property
    def model(self) -> Optional[lgb.Booster]:
        """Get the underlying LightGBM Booster."""
        return self._model
