"""
ltr_lib - Learning to Rank Library
==================================

A Python library for learning-to-rank with support for multiple ranking
algorithms, MovieLens dataset handling, and comprehensive evaluation metrics.

Quick Start
-----------
>>> from ltr_lib import LTR
>>>
>>> # Initialize and load data
>>> ltr = LTR()
>>> data = ltr.load_movielens('100k')
>>> X, y, groups = ltr.prepare_features(data)
>>>
>>> # Train a model
>>> model = ltr.rankers.lambdamart(learning_rate=0.05)
>>> ltr.train(model, X, y, groups)
>>>
>>> # Evaluate
>>> results = ltr.evaluate(model, X, y, groups)
>>> print(f"NDCG@10: {results['ndcg_mean']:.4f}")

Components
----------
- LTR: Main interface for training, evaluation, and cross-validation
- rankers: Module containing ranking algorithms (LambdaMART, BM25)
- data: Data loading utilities (MovieLens downloader)
- features: Feature engineering (TF-IDF, popularity, engagement)
- evaluation: Ranking metrics (NDCG, MAP, Precision, MRR, ERR)
"""

__version__ = "0.1.0"
__author__ = "Abhinaav Ramesh"

from .core import LTR, RankerRegistry

from .rankers import (
    BaseRanker,
    LambdaMARTRanker,
    BM25Ranker,
)

from .data import (
    MovieLensData,
    MovieLensLoader,
    DatasetSplitter,
    rating_to_relevance,
)

from .features import (
    TFIDFFeatureExtractor,
    PopularityFeatureExtractor,
    UserEngagementFeatureExtractor,
    GenreFeatureExtractor,
    FeaturePipeline,
)

from .evaluation import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    mean_average_precision,
    mrr,
    err,
    RankingEvaluator,
    evaluate_ranking,
)

__all__ = [
    # Main interface
    "LTR",
    "RankerRegistry",
    # Rankers
    "BaseRanker",
    "LambdaMARTRanker",
    "BM25Ranker",
    # Data
    "MovieLensData",
    "MovieLensLoader",
    "DatasetSplitter",
    "rating_to_relevance",
    # Features
    "TFIDFFeatureExtractor",
    "PopularityFeatureExtractor",
    "UserEngagementFeatureExtractor",
    "GenreFeatureExtractor",
    "FeaturePipeline",
    # Evaluation
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "mean_average_precision",
    "mrr",
    "err",
    "RankingEvaluator",
    "evaluate_ranking",
]
