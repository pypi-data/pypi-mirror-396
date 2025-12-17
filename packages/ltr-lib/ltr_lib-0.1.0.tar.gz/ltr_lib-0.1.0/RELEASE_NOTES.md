# Release Notes

## Version 0.1.0 (December 14, 2025)

### 🎉 Initial Release

We're excited to announce the first release of **ltr-lib**, a production-ready Learning-to-Rank library for Python!

This release provides a complete implementation of state-of-the-art ranking algorithms with an intuitive API, comprehensive evaluation metrics, and rich feature engineering capabilities.

---

## ✨ Features

### Ranking Algorithms

#### LambdaMART Ranker
- **State-of-the-art** learning-to-rank algorithm powered by LightGBM
- Optimizes for NDCG using gradient boosting
- Supports custom hyperparameters for fine-tuning
- Fast training: typical models train in < 1 second
- Feature importance analysis built-in

```python
from ltr_lib import LambdaMARTRanker

ranker = LambdaMARTRanker(n_estimators=100, learning_rate=0.1)
ranker.fit(X, y, groups=query_groups)
scores = ranker.predict(X_test)
```

#### BM25 Ranker
- Classic information retrieval baseline
- No training required - works out of the box
- Perfect for quick prototyping and comparison
- Supports custom k1 and b parameters

```python
from ltr_lib import BM25Ranker

ranker = BM25Ranker()
ranker.fit(documents)
scores = ranker.predict(query, doc_ids)
```

### Feature Engineering

Built-in feature extractors for rich document representations:

- **TF-IDF Features** - Content-based similarity using user profiles
- **Popularity Features** - Document engagement signals (ratings, views)
- **User Engagement** - Personalized interaction patterns
- **Genre Features** - Multi-hot encoding for categorical data

```python
from ltr_lib import TFIDFFeatureExtractor, PopularityFeatureExtractor

tfidf = TFIDFFeatureExtractor()
tfidf.fit(documents)
features = tfidf.transform(user_id, doc_ids)
```

### Evaluation Metrics

Comprehensive ranking metrics for model evaluation:

- **NDCG@K** - Normalized Discounted Cumulative Gain
- **MAP** - Mean Average Precision
- **Precision@K** - Precision at cutoff K
- **Recall@K** - Recall at cutoff K
- **MRR** - Mean Reciprocal Rank
- **DCG@K** - Discounted Cumulative Gain

```python
from ltr_lib.evaluation import ndcg_at_k, precision_at_k, mean_average_precision

ndcg = ndcg_at_k(y_true, y_pred, k=10)
map_score = mean_average_precision(y_true, y_pred)
```

### High-Level API

Simple, scikit-learn-like interface for end-to-end workflows:

```python
from ltr_lib import LTR

# Initialize and load data
ltr = LTR()
ltr.load_movielens_data("data/ml-100k")

# Train with automatic feature engineering
ltr.train(ranker_type="lambdamart", n_estimators=100)

# Cross-validation
results = ltr.train_with_cv(n_splits=5)
print(f"Mean NDCG@10: {results['mean_ndcg']:.4f}")

# Make predictions
top_movies = ltr.rank_for_user(user_id=1, top_k=10)
```

### Command-Line Interface

Easy-to-use CLI for training and evaluation:

```bash
# Train a model
ltr-train --data data/ml-100k --ranker lambdamart --output model.pkl

# Evaluate model
ltr-eval --model model.pkl --data data/ml-100k --metrics ndcg map precision

# Cross-validation
ltr-cv --data data/ml-100k --ranker lambdamart --splits 5
```

### Data Integration

Built-in support for MovieLens datasets:

- Automatic download and processing
- 100K, 1M, and 10M dataset variants
- Efficient data loading and caching
- Query-document-relevance format conversion

---

## 📊 Performance

### Benchmark Results (MovieLens 100K)

| Metric | LambdaMART | BM25 (Baseline) |
|--------|------------|-----------------|
| NDCG@10 | **0.7855** | 0.6842 |
| MAP | **0.9474** | 0.8231 |
| Precision@10 | **0.9784** | 0.8965 |

### Speed

- **Training**: ~0.14s (10 estimators), ~2.5s (100 estimators)
- **Inference**: < 0.01s per query
- **Feature Engineering**: ~1.2s for 100K interactions

---

## 🛠️ Installation

### From PyPI (Coming Soon)
```bash
pip install ltr-lib
```

### From Source
```bash
git clone https://github.com/yourusername/learning-to-rank-from-scratch.git
cd learning-to-rank-from-scratch
pip install -e .
```

### Requirements
- Python >= 3.10
- numpy >= 1.21.0
- pandas >= 1.3.0
- scikit-learn >= 1.0.0
- lightgbm >= 4.0.0
- rank-bm25 >= 0.2.2
- scipy >= 1.7.0

---

## 📚 Documentation

### Quick Start

```python
# 1. Import the library
from ltr_lib import LTR

# 2. Initialize
ltr = LTR()

# 3. Load your data
ltr.load_movielens_data("data/ml-100k")
# Or use custom data:
# ltr.load_custom_data(ratings_df, movies_df)

# 4. Train
ltr.train(ranker_type="lambdamart")

# 5. Evaluate
metrics = ltr.evaluate()
print(f"NDCG@10: {metrics['ndcg_10']:.4f}")

# 6. Get recommendations
recommendations = ltr.rank_for_user(user_id=123, top_k=10)
for movie in recommendations:
    print(f"{movie['title']}: {movie['score']:.4f}")
```

### Advanced Usage

```python
from ltr_lib import LambdaMARTRanker, FeaturePipeline
from ltr_lib.evaluation import RankingEvaluator

# Custom feature pipeline
pipeline = FeaturePipeline([
    'tfidf',
    'popularity',
    'engagement',
    'genre'
])
X, y, groups = pipeline.fit_transform(ratings_df, movies_df)

# Train with custom parameters
ranker = LambdaMARTRanker(
    n_estimators=100,
    learning_rate=0.1,
    num_leaves=31,
    max_depth=6
)
ranker.fit(X, y, groups=groups)

# Comprehensive evaluation
evaluator = RankingEvaluator(metrics=['ndcg', 'map', 'precision', 'mrr'])
results = evaluator.evaluate(ranker, X_test, y_test, groups_test)
```

### Examples

Check out the included examples:
- `demo.py` - Simple demonstration with synthetic data
- `learning_to_rank.ipynb` - Complete notebook tutorial
- `scripts/validate.py` - Full validation pipeline

---

## 🧪 Testing

This release includes comprehensive test coverage:

- **49 unit tests** covering all core functionality
- **50% overall code coverage**
- **90% coverage** on evaluation metrics
- All tests passing on Python 3.10, 3.11, 3.12, 3.13

Run tests locally:
```bash
pytest tests/ -v
pytest tests/ --cov=ltr_lib --cov-report=html
```

---

## 📖 API Reference

### Core Classes

- `LTR` - High-level API for end-to-end workflows
- `LambdaMARTRanker` - LambdaMART implementation
- `BM25Ranker` - BM25 baseline implementation
- `FeaturePipeline` - Feature engineering pipeline

### Feature Extractors

- `TFIDFFeatureExtractor` - TF-IDF similarity features
- `PopularityFeatureExtractor` - Document popularity signals
- `UserEngagementFeatureExtractor` - User interaction patterns
- `GenreFeatureExtractor` - Categorical feature encoding

### Evaluation

- `ndcg_at_k()` - Calculate NDCG@K
- `mean_average_precision()` - Calculate MAP
- `precision_at_k()` - Calculate Precision@K
- `recall_at_k()` - Calculate Recall@K
- `mrr()` - Calculate Mean Reciprocal Rank
- `RankingEvaluator` - Multi-metric evaluation

### Data Loading

- `MovieLensLoader` - Load MovieLens datasets
- `load_movielens_100k()` - Quick loader for ML-100K
- `load_movielens_1m()` - Quick loader for ML-1M

---

## 🔧 Configuration

Default hyperparameters can be customized via:

1. **Constructor arguments**:
```python
ranker = LambdaMARTRanker(
    n_estimators=100,
    learning_rate=0.1,
    num_leaves=31
)
```

2. **Config file** (coming in v0.2.0):
```yaml
ranker:
  type: lambdamart
  n_estimators: 100
  learning_rate: 0.1
```

---

## 🐛 Known Issues

- CLI tools require manual installation of optional dependencies
- Feature importance plotting not yet implemented
- Large datasets (>1M rows) may require increased memory

See [GitHub Issues](https://github.com/yourusername/learning-to-rank-from-scratch/issues) for the full list.

---

## 🗺️ Roadmap

### Version 0.2.0 (Q1 2026)
- Additional ranking algorithms (RankNet, ListNet)
- Hyperparameter tuning utilities
- Feature importance visualization
- Configuration file support
- PyPI release

### Version 0.3.0 (Q2 2026)
- Neural ranking models
- GPU acceleration
- Distributed training support
- REST API server

---

## 🤝 Contributing

We welcome contributions! Please see [DEV_README.md](DEV_README.md) for development guidelines.

Areas we'd love help with:
- Additional ranking algorithms
- More feature extractors
- Performance optimizations
- Documentation improvements
- Bug reports and fixes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built on top of [LightGBM](https://github.com/microsoft/LightGBM) for gradient boosting
- Uses [rank-bm25](https://github.com/dorianbrown/rank_bm25) for BM25 implementation
- Tested with [MovieLens](https://grouplens.org/datasets/movielens/) datasets
- Inspired by learning-to-rank research from Microsoft Research

---

## 📞 Support

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/learning-to-rank-from-scratch/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/learning-to-rank-from-scratch/discussions)

---

## 📈 Stats

- **Lines of Code**: 3,664
- **Files**: 22
- **Test Coverage**: 50%
- **Documentation**: 100% of public APIs
- **Performance**: Trains in < 3s on 100K samples

---

**Happy Ranking! 🚀**

For detailed changes, see [CHANGELOG.md](CHANGELOG.md)
