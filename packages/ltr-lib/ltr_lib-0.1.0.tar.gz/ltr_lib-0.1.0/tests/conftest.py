"""Pytest configuration and shared fixtures."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_ratings():
    """Create sample ratings DataFrame."""
    np.random.seed(42)
    n_users = 10
    n_movies = 20
    n_ratings = 100

    data = {
        "user_id": np.random.randint(1, n_users + 1, n_ratings),
        "movie_id": np.random.randint(1, n_movies + 1, n_ratings),
        "rating": np.random.randint(1, 6, n_ratings),
        "timestamp": np.random.randint(0, 1000000, n_ratings),
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_movies():
    """Create sample movies DataFrame."""
    movies = pd.DataFrame({
        "movie_id": range(1, 21),
        "title": [f"Movie {i}" for i in range(1, 21)],
        "genres": [
            "Action|Adventure", "Comedy|Romance", "Drama",
            "Sci-Fi|Thriller", "Animation|Children's",
            "Horror", "Documentary", "Musical",
            "Action|Comedy", "Drama|Romance",
            "Sci-Fi", "Thriller", "Comedy",
            "Action", "Adventure|Fantasy",
            "Crime|Drama", "War", "Western",
            "Film-Noir", "Mystery"
        ],
    })
    # Add genre columns for 100k format
    genres = [
        "unknown", "Action", "Adventure", "Animation", "Children's",
        "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
        "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
        "Sci-Fi", "Thriller", "War", "Western"
    ]
    for g in genres:
        movies[g] = movies["genres"].str.contains(g, regex=False).astype(int)
    return movies


@pytest.fixture
def sample_users():
    """Create sample users DataFrame."""
    return pd.DataFrame({
        "user_id": range(1, 11),
        "age": np.random.randint(18, 65, 10),
        "gender": np.random.choice(["M", "F"], 10),
        "occupation": np.random.choice(["engineer", "student", "artist"], 10),
        "zip_code": ["00000"] * 10,
    })


@pytest.fixture
def sample_feature_matrix():
    """Create sample feature matrix for ranker testing."""
    np.random.seed(42)
    n_samples = 100
    n_features = 10

    X = np.random.rand(n_samples, n_features)
    y = np.random.randint(0, 4, n_samples)
    groups = np.array([20, 20, 20, 20, 20])

    return X, y, groups
