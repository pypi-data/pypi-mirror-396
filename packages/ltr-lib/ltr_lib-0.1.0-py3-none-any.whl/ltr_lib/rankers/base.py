"""Base classes and interfaces for ranking models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


class BaseRanker(ABC):
    """Abstract base class for all ranking models.

    All rankers must implement fit, predict, and score methods.
    This ensures a consistent API across different ranking algorithms.
    """

    def __init__(self, name: str = "BaseRanker"):
        self.name = name
        self._is_fitted = False
        self._feature_names: Optional[List[str]] = None

    @abstractmethod
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: np.ndarray,
        **kwargs
    ) -> "BaseRanker":
        """Fit the ranking model.

        Args:
            X: Feature matrix of shape (n_samples, n_features)
            y: Relevance labels of shape (n_samples,)
            groups: Query group sizes of shape (n_queries,)
            **kwargs: Additional model-specific parameters

        Returns:
            self: The fitted ranker
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict relevance scores for samples.

        Args:
            X: Feature matrix of shape (n_samples, n_features)

        Returns:
            scores: Predicted relevance scores of shape (n_samples,)
        """
        pass

    @abstractmethod
    def score(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: np.ndarray,
        metric: str = "ndcg",
        k: int = 10
    ) -> float:
        """Compute ranking metric on given data.

        Args:
            X: Feature matrix of shape (n_samples, n_features)
            y: True relevance labels of shape (n_samples,)
            groups: Query group sizes of shape (n_queries,)
            metric: Metric name ('ndcg', 'map', 'precision')
            k: Cutoff for metric computation

        Returns:
            score: The computed metric value
        """
        pass

    def get_params(self) -> Dict[str, Any]:
        """Get model parameters.

        Returns:
            params: Dictionary of model parameters
        """
        return {"name": self.name}

    def set_params(self, **params) -> "BaseRanker":
        """Set model parameters.

        Args:
            **params: Parameters to set

        Returns:
            self: The ranker with updated parameters
        """
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    @property
    def is_fitted(self) -> bool:
        """Check if the model has been fitted."""
        return self._is_fitted

    @property
    def feature_names(self) -> Optional[List[str]]:
        """Get feature names if available."""
        return self._feature_names

    @feature_names.setter
    def feature_names(self, names: List[str]) -> None:
        """Set feature names."""
        self._feature_names = names

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class RankerMixin:
    """Mixin class providing common ranking utilities."""

    @staticmethod
    def split_by_groups(
        X: np.ndarray,
        y: np.ndarray,
        groups: np.ndarray
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Split data by query groups.

        Args:
            X: Feature matrix
            y: Labels
            groups: Group sizes

        Returns:
            List of (X_group, y_group) tuples for each query
        """
        result = []
        start = 0
        for size in groups:
            end = start + size
            result.append((X[start:end], y[start:end]))
            start = end
        return result

    @staticmethod
    def validate_inputs(
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None
    ) -> None:
        """Validate input arrays.

        Args:
            X: Feature matrix
            y: Labels (optional)
            groups: Group sizes (optional)

        Raises:
            ValueError: If inputs are invalid
        """
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")

        if y is not None:
            if y.ndim != 1:
                raise ValueError(f"y must be 1D, got {y.ndim}D")
            if len(y) != len(X):
                raise ValueError(
                    f"X and y must have same length, got {len(X)} and {len(y)}"
                )

        if groups is not None:
            if groups.ndim != 1:
                raise ValueError(f"groups must be 1D, got {groups.ndim}D")
            if y is not None and groups.sum() != len(y):
                raise ValueError(
                    f"Sum of groups ({groups.sum()}) must equal length of y ({len(y)})"
                )
