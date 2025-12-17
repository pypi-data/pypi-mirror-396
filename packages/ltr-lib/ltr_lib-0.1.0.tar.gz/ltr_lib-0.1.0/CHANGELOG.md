# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-14

### Added

#### Core Framework
- High-level `LTR` class for end-to-end learning-to-rank workflows
- Modular architecture with separate modules for rankers, features, evaluation, and data loading
- Package configuration with `pyproject.toml` for pip installation
- Command-line interface (CLI) for training and evaluation

#### Ranking Algorithms
- **LambdaMARTRanker**: LightGBM-based learning-to-rank implementation
  - Support for custom hyperparameters (n_estimators, learning_rate, num_leaves, etc.)
  - Feature importance extraction
  - Model persistence (save/load)
  - Query group awareness for listwise learning
- **BM25Ranker**: Classic IR baseline for comparison
  - Configurable k1 and b parameters
  - Fast inference without training
  - Document ranking and scoring

#### Feature Engineering
- **TFIDFFeatureExtractor**: Content-based similarity features
  - User profile creation from historical interactions
  - Cosine similarity computation
  - Configurable max_features parameter
- **PopularityFeatureExtractor**: Document popularity signals
  - Rating count and average rating features
  - Popularity score calculation
  - Normalization support
- **UserEngagementFeatureExtractor**: Personalized interaction features
  - User-specific engagement metrics
  - Historical interaction patterns
  - Temporal features
- **GenreFeatureExtractor**: Categorical feature encoding
  - Multi-hot encoding for genres
  - Binary feature vectors
  - Efficient sparse representation
- **FeaturePipeline**: Unified feature engineering workflow
  - Sequential feature extraction
  - Automatic feature concatenation
  - Feature name tracking

#### Evaluation Metrics
- **NDCG@K**: Normalized Discounted Cumulative Gain at position K
- **MAP**: Mean Average Precision
- **Precision@K**: Precision at cutoff K
- **Recall@K**: Recall at cutoff K
- **MRR**: Mean Reciprocal Rank
- **DCG@K**: Discounted Cumulative Gain at position K
- **RankingEvaluator**: Multi-metric evaluation framework
  - Single and batch evaluation
  - Per-query and aggregate metrics
  - Configurable evaluation metrics

#### Data Loading
- **MovieLensLoader**: Comprehensive MovieLens dataset integration
  - Support for MovieLens 100K, 1M, and 10M datasets
  - Automatic data parsing and preprocessing
  - Relevance label conversion
  - Query-document format transformation
- Custom data loading utilities for user-provided datasets

#### Testing & Validation
- 49 comprehensive unit tests covering all core functionality
- Test fixtures for sample data generation (`conftest.py`)
- **test_features.py**: 15 tests for feature extractors
- **test_metrics.py**: 19 tests for evaluation metrics
- **test_rankers.py**: 15 tests for ranking algorithms
- Validation script (`scripts/validate.py`) for end-to-end testing
  - Import validation
  - Metrics validation
  - Data loading validation
  - Feature engineering validation
  - Model training validation
  - Cross-validation validation

#### Documentation
- Comprehensive README with quick start guide
- Developer documentation (DEV_README.md)
- API documentation via docstrings
- Usage examples in demo.py
- Jupyter notebook tutorial (learning_to_rank.ipynb)
- Package metadata and dependencies in pyproject.toml

#### Examples
- `demo.py`: Simple demonstration with synthetic data
- `test_implementation.py`: Component testing script
- `learning_to_rank.ipynb`: Interactive tutorial notebook

### Performance
- Training speed: ~0.14s for 10 estimators, ~2.5s for 100 estimators
- Inference: < 0.01s per query
- Feature engineering: ~1.2s for 100K interactions
- NDCG@10 benchmark: 0.7855 on MovieLens 100K

### Dependencies
- Python >= 3.10
- numpy >= 1.21.0
- pandas >= 1.3.0
- scikit-learn >= 1.0.0
- lightgbm >= 4.0.0
- rank-bm25 >= 0.2.2
- scipy >= 1.7.0

### Infrastructure
- Package build configuration with setuptools
- Test coverage reporting with pytest-cov
- Development environment configuration
- Git hooks for code quality (optional)

---

## [Unreleased]

### Planned for 0.2.0
- Additional ranking algorithms (RankNet, ListNet)
- Hyperparameter tuning utilities (GridSearchCV, RandomSearchCV)
- Feature importance visualization
- Configuration file support (YAML/JSON)
- PyPI package release
- CI/CD pipeline (GitHub Actions)
- Docker container for easy deployment

### Planned for 0.3.0
- Neural ranking models (BERT-based)
- GPU acceleration support
- Distributed training with Dask/Ray
- REST API server
- Model serving utilities
- Online learning support

### Ideas for Future Versions
- AutoML for automatic ranker selection
- Explainability tools (SHAP, LIME)
- A/B testing utilities
- Production monitoring dashboard
- Additional datasets (MS MARCO, TREC)
- Multi-language support

---

## Release Notes Format

Each release follows this structure:

### Added
New features and capabilities

### Changed
Changes to existing functionality

### Deprecated
Features marked for removal in future releases

### Removed
Features removed in this release

### Fixed
Bug fixes

### Security
Security-related changes

---

## Version History

- **0.1.0** (2025-12-14) - Initial release

---

## Links

- [Repository](https://github.com/yourusername/learning-to-rank-from-scratch)
- [Issue Tracker](https://github.com/yourusername/learning-to-rank-from-scratch/issues)
- [Documentation](https://github.com/yourusername/learning-to-rank-from-scratch/blob/main/README.md)

---

## Upgrade Notes

### From Development to 0.1.0

This is the first official release. If you've been using the development version:

1. Install the package: `pip install -e .`
2. Update imports from module paths to `ltr_lib`
3. Review API documentation for any changes
4. Run tests to ensure compatibility: `pytest tests/`

No breaking changes from the development version.
