#!/usr/bin/env python3
"""
Simple demonstration of the Learning-to-Rank system
This script provides a minimal example without downloading the full MovieLens dataset
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

print("\n" + "=" * 60)
print("Learning-to-Rank System Demonstration")
print("=" * 60 + "\n")

# Create sample movie dataset
print("1. Creating sample movie dataset...")
movies_data = {
    'movie_id': range(1, 11),
    'title': [
        'The Action Hero', 'Romantic Comedy', 'Sci-Fi Adventure',
        'Drama Story', 'Thriller Mystery', 'Comedy Special',
        'Action Thriller', 'Romance Drama', 'Sci-Fi Action', 'Comedy Romance'
    ],
    'genres': [
        'action', 'comedy romance', 'scifi adventure',
        'drama', 'thriller mystery', 'comedy',
        'action thriller', 'romance drama', 'scifi action', 'comedy romance'
    ]
}
movies_df = pd.DataFrame(movies_data)
print(f"   Created {len(movies_df)} sample movies\n")

# Create sample user-movie interactions
print("2. Creating sample user interactions...")
np.random.seed(42)
interactions = []
for user_id in range(1, 6):  # 5 users
    for movie_id in range(1, 11):  # Each user rates some movies
        if np.random.random() > 0.3:  # 70% chance of rating
            rating = np.random.randint(1, 6)
            relevance = 0 if rating <= 2 else (rating - 2)
            interactions.append({
                'user_id': user_id,
                'movie_id': movie_id,
                'rating': rating,
                'relevance': relevance
            })

interactions_df = pd.DataFrame(interactions)
print(f"   Created {len(interactions_df)} interactions\n")

# Compute features
print("3. Engineering features...")

# TF-IDF features
documents = [f"{row['title']} {row['genres']}" for _, row in movies_df.iterrows()]
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(documents)

# Popularity features
popularity = interactions_df.groupby('movie_id').agg({
    'rating': ['count', 'mean'],
}).reset_index()
popularity.columns = ['movie_id', 'num_ratings', 'avg_rating']

# Merge features
data = interactions_df.merge(movies_df, on='movie_id')
data = data.merge(popularity, on='movie_id')

# Compute TF-IDF similarity (simplified)
data['tfidf_score'] = np.random.uniform(0, 1, len(data))  # Simplified for demo

print(f"   Engineered {3} feature types\n")

# Prepare training data
print("4. Preparing data for LambdaMART...")
feature_columns = ['tfidf_score', 'num_ratings', 'avg_rating']
X = data[feature_columns].values
y = data['relevance'].values
groups = data.groupby('user_id').size().values

print(f"   Feature matrix: {X.shape}")
print(f"   Query groups: {len(groups)}\n")

# Train LambdaMART
print("5. Training LambdaMART model...")
train_data = lgb.Dataset(X, label=y, group=groups)

params = {
    'objective': 'lambdarank',
    'metric': 'ndcg',
    'ndcg_eval_at': [10],
    'learning_rate': 0.1,
    'num_leaves': 15,
    'verbose': -1
}

model = lgb.train(params, train_data, num_boost_round=50)
print("   Model trained successfully!\n")

# Make predictions
print("6. Making predictions...")
predictions = model.predict(X)

# Evaluate for one user
print("7. Example ranking for User 1:")
user_1_data = data[data['user_id'] == 1].copy()
user_1_data['predicted_score'] = predictions[:len(user_1_data)]
user_1_ranked = user_1_data.sort_values('predicted_score', ascending=False)

print("\n   Top 5 Recommended Movies:")
print("   " + "-" * 58)
for idx, (_, row) in enumerate(user_1_ranked.head(5).iterrows(), 1):
    print(f"   {idx}. {row['title']:25s} (Score: {row['predicted_score']:.3f}, Relevance: {int(row['relevance'])})")

# Compute NDCG
def ndcg_at_k(y_true, y_pred, k=5):
    order = np.argsort(y_pred)[::-1][:k]
    y_true_sorted = y_true[order]
    
    gains = 2 ** y_true_sorted - 1
    discounts = np.log2(np.arange(len(y_true_sorted)) + 2)
    dcg = np.sum(gains / discounts)
    
    ideal_order = np.argsort(y_true)[::-1][:k]
    ideal_gains = 2 ** y_true[ideal_order] - 1
    idcg = np.sum(ideal_gains / discounts[:len(ideal_gains)])
    
    return dcg / idcg if idcg > 0 else 0.0

ndcg = ndcg_at_k(user_1_data['relevance'].values, 
                  user_1_data['predicted_score'].values, k=5)

print(f"\n   NDCG@5 for User 1: {ndcg:.4f}")

# BM25 baseline
print("\n8. Comparing with BM25 baseline...")
corpus = [doc.split() for doc in documents]
bm25 = BM25Okapi(corpus)

# Create user profile (simplified)
user_1_profile = "action thriller"
query = user_1_profile.split()
bm25_scores = bm25.get_scores(query)

# Get scores for user 1's movies
user_1_movie_indices = user_1_data['movie_id'].values - 1
user_1_bm25_scores = bm25_scores[user_1_movie_indices]

ndcg_bm25 = ndcg_at_k(user_1_data['relevance'].values, user_1_bm25_scores, k=5)
print(f"   BM25 NDCG@5 for User 1: {ndcg_bm25:.4f}")

print("\n" + "=" * 60)
print("Demonstration completed!")
print("=" * 60)
print("\nFor the full implementation with MovieLens dataset,")
print("see the Jupyter notebook: learning_to_rank.ipynb")
print("=" * 60 + "\n")
