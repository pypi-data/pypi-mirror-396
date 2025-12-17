#!/usr/bin/env python
"""Validation script for local testing of the LTR library.

This script provides a comprehensive validation pipeline that:
1. Tests all core components
2. Validates data loading
3. Trains and evaluates models
4. Compares different ranking algorithms

Usage:
    uv run python scripts/validate.py
    uv run python scripts/validate.py --quick     # Fast validation
    uv run python scripts/validate.py --full      # Full evaluation
"""

import argparse
import sys
import time
from pathlib import Path


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(name: str, passed: bool, message: str = ""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    msg = f" - {message}" if message else ""
    print(f"  {status}: {name}{msg}")


def validate_imports():
    """Validate all imports work correctly."""
    print_header("Validating Imports")

    tests = []

    try:
        from ltr_lib import LTR
        tests.append(("LTR class", True))
    except Exception as e:
        tests.append(("LTR class", False, str(e)))

    try:
        from ltr_lib import LambdaMARTRanker, BM25Ranker
        tests.append(("Rankers", True))
    except Exception as e:
        tests.append(("Rankers", False, str(e)))

    try:
        from ltr_lib import ndcg_at_k, precision_at_k, mean_average_precision
        tests.append(("Metrics", True))
    except Exception as e:
        tests.append(("Metrics", False, str(e)))

    try:
        from ltr_lib import MovieLensLoader, FeaturePipeline
        tests.append(("Data & Features", True))
    except Exception as e:
        tests.append(("Data & Features", False, str(e)))

    for t in tests:
        print_result(t[0], t[1], t[2] if len(t) > 2 else "")

    return all(t[1] for t in tests)


def validate_metrics():
    """Validate metric computations."""
    print_header("Validating Metrics")

    import numpy as np
    from ltr_lib.evaluation import ndcg_at_k, precision_at_k, mrr

    tests = []

    # NDCG test
    y_true = np.array([3, 2, 1, 0])
    y_pred = np.array([4, 3, 2, 1])
    ndcg = ndcg_at_k(y_true, y_pred, k=4)
    tests.append(("NDCG perfect ranking", ndcg == 1.0, f"value={ndcg:.4f}"))

    # Precision test
    y_true = np.array([1, 1, 0, 0])
    y_pred = np.array([4, 3, 2, 1])
    prec = precision_at_k(y_true, y_pred, k=2)
    tests.append(("Precision@2", prec == 1.0, f"value={prec:.4f}"))

    # MRR test
    y_true = np.array([0, 1, 0, 0])
    y_pred = np.array([4, 3, 2, 1])
    mrr_val = mrr(y_true, y_pred)
    tests.append(("MRR", mrr_val == 0.5, f"value={mrr_val:.4f}"))

    for t in tests:
        print_result(t[0], t[1], t[2])

    return all(t[1] for t in tests)


def validate_data_loading(data_dir: str):
    """Validate data loading."""
    print_header("Validating Data Loading")

    from ltr_lib.data import MovieLensLoader

    tests = []

    loader = MovieLensLoader(data_dir=data_dir)
    data_path = Path(data_dir) / "ml-100k"

    if not data_path.exists():
        print(f"  Downloading MovieLens 100k to {data_dir}...")
        try:
            loader.download("100k")
            tests.append(("Download", True))
        except Exception as e:
            tests.append(("Download", False, str(e)))
            for t in tests:
                print_result(t[0], t[1], t[2] if len(t) > 2 else "")
            return False

    try:
        data = loader.load("100k")
        tests.append(("Load ratings", len(data.ratings) == 100000, f"n={len(data.ratings)}"))
        tests.append(("Load movies", len(data.movies) > 0, f"n={len(data.movies)}"))
        tests.append(("Load users", len(data.users) > 0, f"n={len(data.users)}"))
    except Exception as e:
        tests.append(("Load data", False, str(e)))

    for t in tests:
        print_result(t[0], t[1], t[2] if len(t) > 2 else "")

    return all(t[1] for t in tests)


def validate_features(data_dir: str):
    """Validate feature engineering."""
    print_header("Validating Feature Engineering")

    from ltr_lib import LTR

    tests = []

    try:
        ltr = LTR(data_dir=data_dir)
        data = ltr.load_movielens("100k")
        X, y, groups = ltr.prepare_features(data)

        tests.append(("Feature matrix shape", X.shape[1] > 0, f"shape={X.shape}"))
        tests.append(("Labels", len(y) == len(X), f"n={len(y)}"))
        tests.append(("Groups", sum(groups) == len(y), f"n_groups={len(groups)}"))

        feature_names = ltr.get_feature_names()
        tests.append(("Feature names", len(feature_names) > 0, f"n_features={len(feature_names)}"))

    except Exception as e:
        tests.append(("Feature engineering", False, str(e)))

    for t in tests:
        print_result(t[0], t[1], t[2] if len(t) > 2 else "")

    return all(t[1] for t in tests)


def validate_training(data_dir: str, quick: bool = True):
    """Validate model training."""
    print_header("Validating Model Training")

    from ltr_lib import LTR

    tests = []
    n_estimators = 10 if quick else 50

    try:
        ltr = LTR(data_dir=data_dir)
        data = ltr.load_movielens("100k")
        X, y, groups = ltr.prepare_features(data)

        # Train LambdaMART
        print(f"  Training LambdaMART (n_estimators={n_estimators})...")
        start = time.time()
        model = ltr.rankers.lambdamart(n_estimators=n_estimators, verbose=-1)
        ltr.train(model, X, y, groups)
        train_time = time.time() - start

        tests.append(("LambdaMART training", model.is_fitted, f"time={train_time:.2f}s"))

        # Get predictions
        preds = model.predict(X)
        tests.append(("Predictions", len(preds) == len(X), f"n={len(preds)}"))

        # Feature importance
        importance = model.get_feature_importance()
        tests.append(("Feature importance", len(importance) > 0, f"n={len(importance)}"))

    except Exception as e:
        tests.append(("Training", False, str(e)))

    for t in tests:
        print_result(t[0], t[1], t[2] if len(t) > 2 else "")

    return all(t[1] for t in tests)


def validate_evaluation(data_dir: str, quick: bool = True):
    """Validate model evaluation."""
    print_header("Validating Model Evaluation")

    from ltr_lib import LTR

    tests = []
    n_estimators = 10 if quick else 50

    try:
        ltr = LTR(data_dir=data_dir)
        data = ltr.load_movielens("100k")
        X, y, groups = ltr.prepare_features(data)

        model = ltr.rankers.lambdamart(n_estimators=n_estimators, verbose=-1)
        ltr.train(model, X, y, groups)

        # Evaluate
        print("  Evaluating model...")
        results = ltr.evaluate(model, X, y, groups, k=10)

        ndcg = results.get("ndcg_mean", 0)
        prec = results.get("precision_mean", 0)
        map_val = results.get("map_mean", 0)

        tests.append(("NDCG@10", 0 < ndcg <= 1, f"value={ndcg:.4f}"))
        tests.append(("Precision@10", 0 <= prec <= 1, f"value={prec:.4f}"))
        tests.append(("MAP", 0 <= map_val <= 1, f"value={map_val:.4f}"))

    except Exception as e:
        tests.append(("Evaluation", False, str(e)))

    for t in tests:
        print_result(t[0], t[1], t[2] if len(t) > 2 else "")

    return all(t[1] for t in tests)


def validate_cross_validation(data_dir: str):
    """Validate cross-validation."""
    print_header("Validating Cross-Validation")

    from ltr_lib import LTR

    tests = []

    try:
        ltr = LTR(data_dir=data_dir)
        data = ltr.load_movielens("100k")
        X, y, groups = ltr.prepare_features(data)

        model = ltr.rankers.lambdamart(n_estimators=10, verbose=-1)

        print("  Running 3-fold cross-validation...")
        start = time.time()
        cv_results = ltr.cross_validate(model, X, y, groups, n_folds=3)
        cv_time = time.time() - start

        tests.append(("CV completed", "ndcg_mean" in cv_results, f"time={cv_time:.2f}s"))
        tests.append(("CV NDCG", cv_results["ndcg_mean"] > 0, f"value={cv_results['ndcg_mean']:.4f}"))
        tests.append(("CV std", cv_results["ndcg_std"] >= 0, f"std={cv_results['ndcg_std']:.4f}"))

    except Exception as e:
        tests.append(("Cross-validation", False, str(e)))

    for t in tests:
        print_result(t[0], t[1], t[2] if len(t) > 2 else "")

    return all(t[1] for t in tests)


def run_full_benchmark(data_dir: str):
    """Run full benchmark with multiple models."""
    print_header("Full Model Benchmark")

    from ltr_lib import LTR

    ltr = LTR(data_dir=data_dir)
    data = ltr.load_movielens("100k")
    X, y, groups = ltr.prepare_features(data)

    print("  Running 5-fold CV with LambdaMART...")
    model = ltr.rankers.lambdamart(n_estimators=100, verbose=-1)
    cv_results = ltr.cross_validate(model, X, y, groups, n_folds=5)

    print("\n  Results:")
    print(f"    NDCG@10:      {cv_results['ndcg_mean']:.4f} ± {cv_results['ndcg_std']:.4f}")
    print(f"    Precision@10: {cv_results['precision_mean']:.4f} ± {cv_results['precision_std']:.4f}")
    print(f"    MAP:          {cv_results['map_mean']:.4f} ± {cv_results['map_std']:.4f}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Validate LTR library")
    parser.add_argument("--data", default="./data", help="Data directory")
    parser.add_argument("--quick", action="store_true", help="Quick validation")
    parser.add_argument("--full", action="store_true", help="Full benchmark")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  LTR Library Validation")
    print("="*60)

    all_passed = True
    start_time = time.time()

    # Core validations
    all_passed &= validate_imports()
    all_passed &= validate_metrics()
    all_passed &= validate_data_loading(args.data)
    all_passed &= validate_features(args.data)
    all_passed &= validate_training(args.data, quick=not args.full)
    all_passed &= validate_evaluation(args.data, quick=not args.full)

    if not args.quick:
        all_passed &= validate_cross_validation(args.data)

    if args.full:
        run_full_benchmark(args.data)

    total_time = time.time() - start_time

    print_header("Summary")
    if all_passed:
        print(f"  ✓ All validations passed in {total_time:.2f}s")
        sys.exit(0)
    else:
        print(f"  ✗ Some validations failed in {total_time:.2f}s")
        sys.exit(1)


if __name__ == "__main__":
    main()
