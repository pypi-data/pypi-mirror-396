"""Command-line interface for LTR library."""

import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Learning-to-Rank Library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download MovieLens dataset")
    download_parser.add_argument(
        "--version",
        choices=["100k", "1m", "20m"],
        default="100k",
        help="Dataset version (default: 100k)",
    )
    download_parser.add_argument(
        "--output",
        type=str,
        default="./data",
        help="Output directory (default: ./data)",
    )

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a trained model")
    eval_parser.add_argument("--model", type=str, required=True, help="Path to saved model")
    eval_parser.add_argument("--data", type=str, default="./data", help="Data directory")
    eval_parser.add_argument("--k", type=int, default=10, help="Cutoff for @k metrics")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run a quick demo")
    demo_parser.add_argument("--data", type=str, default="./data", help="Data directory")

    args = parser.parse_args()

    if args.command == "download":
        _download(args.version, args.output)
    elif args.command == "evaluate":
        _evaluate(args.model, args.data, args.k)
    elif args.command == "demo":
        _demo(args.data)
    else:
        parser.print_help()
        sys.exit(1)


def _download(version: str, output: str):
    """Download MovieLens dataset."""
    from .data import MovieLensLoader

    print(f"Downloading MovieLens {version} to {output}...")
    loader = MovieLensLoader(data_dir=output)
    path = loader.download(version)
    print(f"Downloaded to: {path}")


def _evaluate(model_path: str, data_dir: str, k: int):
    """Evaluate a trained model."""
    from .core import LTR
    from .rankers import LambdaMARTRanker

    print(f"Loading model from {model_path}...")
    model = LambdaMARTRanker()
    model.load(model_path)

    print(f"Loading data from {data_dir}...")
    ltr = LTR(data_dir=data_dir)
    data = ltr.load_movielens("100k")
    X, y, groups = ltr.prepare_features(data)

    print(f"Evaluating with k={k}...")
    results = ltr.evaluate(model, X, y, groups, k=k)

    print("\nResults:")
    print(f"  NDCG@{k}:      {results['ndcg_mean']:.4f}")
    print(f"  Precision@{k}: {results['precision_mean']:.4f}")
    print(f"  MAP:          {results['map_mean']:.4f}")


def _demo(data_dir: str):
    """Run a quick demo."""
    from .core import LTR

    print("Running LTR demo...")
    print(f"Data directory: {data_dir}\n")

    ltr = LTR(data_dir=data_dir)

    print("Loading MovieLens 100k...")
    data = ltr.load_movielens("100k")
    print(f"  Ratings: {len(data.ratings):,}")
    print(f"  Movies:  {len(data.movies):,}")
    print(f"  Users:   {len(data.users):,}\n")

    print("Preparing features...")
    X, y, groups = ltr.prepare_features(data)
    print(f"  Feature matrix: {X.shape}")
    print(f"  Features: {ltr.get_feature_names()[:5]}...\n")

    print("Training LambdaMART (quick demo with 20 trees)...")
    model = ltr.rankers.lambdamart(n_estimators=20, verbose=-1)
    ltr.train(model, X, y, groups)

    print("Evaluating...")
    results = ltr.evaluate(model, X, y, groups, k=10)

    print("\nResults:")
    print(f"  NDCG@10:      {results['ndcg_mean']:.4f}")
    print(f"  Precision@10: {results['precision_mean']:.4f}")
    print(f"  MAP:          {results['map_mean']:.4f}")
    print("\nDemo complete!")


if __name__ == "__main__":
    main()
