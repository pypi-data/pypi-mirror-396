# Development Setup Guide

This guide covers local development setup using [UV](https://docs.astral.sh/uv/) for fast, reliable dependency management.

## Prerequisites

- Python 3.10+
- [UV](https://docs.astral.sh/uv/) (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/AbhinaavRamesh/learning-to-rank-from-scratch.git
cd learning-to-rank-from-scratch

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package with dev dependencies
uv pip install -e ".[dev,viz]"

# Download MovieLens data for testing
uv run python -c "from ltr_lib.data import MovieLensLoader; MovieLensLoader('./data').download('100k')"

# Run tests
uv run pytest
```

## Project Structure

```
learning-to-rank-from-scratch/
├── ltr_lib/                 # Main package
│   ├── __init__.py          # Package exports
│   ├── core.py              # LTR main class
│   ├── cli.py               # Command-line interface
│   ├── rankers/             # Ranking algorithms
│   │   ├── base.py          # BaseRanker abstract class
│   │   ├── lambdamart.py    # LambdaMART (LightGBM)
│   │   └── bm25.py          # BM25 baseline
│   ├── data/                # Data loading
│   │   └── loaders.py       # MovieLens downloader
│   ├── features/            # Feature engineering
│   │   └── engineering.py   # TF-IDF, popularity, etc.
│   └── evaluation/          # Metrics
│       └── metrics.py       # NDCG, MAP, Precision, MRR
├── tests/                   # Test suite
├── data/                    # Local data (gitignored)
├── pyproject.toml           # Project configuration
└── DEV_README.md            # This file
```

## Development Commands

### Environment Management

```bash
# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate

# Install package in editable mode with all dev dependencies
uv pip install -e ".[dev,viz,notebook]"

# Update dependencies
uv pip compile pyproject.toml -o requirements.txt
uv pip sync requirements.txt
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=ltr_lib --cov-report=html

# Run specific test file
uv run pytest tests/test_metrics.py -v

# Run specific test
uv run pytest tests/test_metrics.py::TestNDCG::test_perfect_ranking -v
```

### Linting & Formatting

```bash
# Run ruff linter
uv run ruff check ltr_lib/

# Fix linting issues
uv run ruff check ltr_lib/ --fix

# Format code
uv run ruff format ltr_lib/

# Type checking
uv run mypy ltr_lib/
```

### CLI Commands

```bash
# Download data
uv run ltr-eval download --version 100k --output ./data

# Run demo
uv run ltr-eval demo --data ./data

# Evaluate saved model
uv run ltr-eval evaluate --model model.lgb --data ./data
```

## Local Testing Pipeline

### Quick Validation

```bash
# Run the quick validation script
uv run python scripts/validate.py
```

### Full Evaluation Pipeline

```python
from ltr_lib import LTR

# Initialize
ltr = LTR(data_dir='./data')

# Load data
data = ltr.load_movielens('100k')
X, y, groups = ltr.prepare_features(data)

# Train model
model = ltr.rankers.lambdamart(n_estimators=100)
ltr.train(model, X, y, groups)

# Evaluate
results = ltr.evaluate(model, X, y, groups, k=10)
print(f"NDCG@10: {results['ndcg_mean']:.4f}")

# Cross-validation
cv_results = ltr.cross_validate(model, n_folds=5)
print(f"CV NDCG@10: {cv_results['ndcg_mean']:.4f} ± {cv_results['ndcg_std']:.4f}")

# Compare models
bm25 = ltr.rankers.bm25()
comparison = ltr.compare_models([model, bm25])
print(comparison)
```

## Troubleshooting

### LightGBM Installation Issues

On macOS, LightGBM requires OpenMP. If you encounter issues:

```bash
# Install libomp via Homebrew
brew install libomp

# Or use conda
conda install -c conda-forge lightgbm
```

### Missing Data

If tests fail due to missing data:

```bash
# Download MovieLens 100k
uv run python -c "from ltr_lib.data import MovieLensLoader; MovieLensLoader('./data').download('100k')"
```

### Import Errors

Ensure the package is installed in editable mode:

```bash
uv pip install -e .
```

## Running Jupyter Notebooks

```bash
# Install notebook dependencies
uv pip install -e ".[notebook]"

# Start Jupyter
uv run jupyter notebook

# Or use JupyterLab
uv pip install jupyterlab
uv run jupyter lab
```

## Adding New Features

1. Create feature branch: `git checkout -b feature/my-feature`
2. Implement in appropriate module under `ltr_lib/`
3. Add tests in `tests/`
4. Run tests: `uv run pytest`
5. Run linter: `uv run ruff check ltr_lib/`
6. Create PR

## API Quick Reference

```python
from ltr_lib import LTR, LambdaMARTRanker, BM25Ranker
from ltr_lib import ndcg_at_k, precision_at_k, mean_average_precision
from ltr_lib import MovieLensLoader, FeaturePipeline

# Main interface
ltr = LTR(data_dir='./data')
ltr.load_movielens('100k')
X, y, groups = ltr.prepare_features()
model = ltr.rankers.lambdamart()
ltr.train(model)
results = ltr.evaluate(model)

# Direct ranker usage
ranker = LambdaMARTRanker(learning_rate=0.05, n_estimators=100)
ranker.fit(X, y, groups)
predictions = ranker.predict(X_test)

# Metrics
ndcg = ndcg_at_k(y_true, y_pred, k=10)
```
