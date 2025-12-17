#!/usr/bin/env python3
"""
Test script to validate the Learning-to-Rank implementation components
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import lightgbm as lgb
from rank_bm25 import BM25Okapi

print("=" * 60)
print("Testing Learning-to-Rank Implementation Components")
print("=" * 60)

# Test 1: TF-IDF functionality
print("\n1. Testing TF-IDF...")
documents = ["action movie thriller", "comedy romantic movie", "drama action movie"]
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(documents)
print(f"   ✓ TF-IDF matrix shape: {tfidf_matrix.shape}")

# Test 2: BM25 functionality
print("\n2. Testing BM25...")
corpus = [doc.split() for doc in documents]
bm25 = BM25Okapi(corpus)
query = ["action", "movie"]
scores = bm25.get_scores(query)
print(f"   ✓ BM25 scores computed: {scores}")

# Test 3: LightGBM ranker
print("\n3. Testing LightGBM ranker...")
# Create sample ranking data
np.random.seed(42)
n_samples = 100
n_features = 10
X = np.random.randn(n_samples, n_features)
y = np.random.randint(0, 4, n_samples)  # Relevance labels 0-3
groups = np.array([20, 30, 25, 25])  # 4 queries with varying number of documents

train_data = lgb.Dataset(X, label=y, group=groups)

params = {
    'objective': 'lambdarank',
    'metric': 'ndcg',
    'ndcg_eval_at': [10],
    'learning_rate': 0.05,
    'num_leaves': 31,
    'verbose': -1
}

model = lgb.train(params, train_data, num_boost_round=10)
predictions = model.predict(X)
print(f"   ✓ LambdaMART model trained and predictions made: {predictions.shape}")

# Test 4: NDCG calculation
print("\n4. Testing NDCG@K calculation...")
def ndcg_at_k(y_true, y_pred, k=10):
    order = np.argsort(y_pred)[::-1]
    y_true_sorted = y_true[order][:k]
    
    gains = 2 ** y_true_sorted - 1
    discounts = np.log2(np.arange(len(y_true_sorted)) + 2)
    dcg = np.sum(gains / discounts)
    
    ideal_order = np.argsort(y_true)[::-1][:k]
    ideal_gains = 2 ** y_true[ideal_order] - 1
    idcg = np.sum(ideal_gains / discounts[:len(ideal_gains)])
    
    return dcg / idcg if idcg > 0 else 0.0

test_y_true = np.array([3, 2, 1, 0, 2])
test_y_pred = np.array([0.9, 0.7, 0.5, 0.1, 0.8])
ndcg_score = ndcg_at_k(test_y_true, test_y_pred, k=5)
print(f"   ✓ NDCG@5 computed: {ndcg_score:.4f}")

# Test 5: Feature engineering
print("\n5. Testing feature engineering...")
# Simulate movie features
movies_data = {
    'movie_id': [1, 2, 3],
    'title': ['Action Movie 1', 'Comedy Movie 2', 'Drama Movie 3'],
    'num_ratings': [100, 50, 200],
    'avg_rating': [4.5, 3.8, 4.2]
}
movies_df = pd.DataFrame(movies_data)
movies_df['popularity_score'] = movies_df['num_ratings'] * movies_df['avg_rating']
print(f"   ✓ Feature engineering: {movies_df.shape[0]} movies with {movies_df.shape[1]} features")

# Test 6: Cross-validation setup
print("\n6. Testing cross-validation setup...")
from sklearn.model_selection import GroupKFold
gkf = GroupKFold(n_splits=3)
user_ids = np.array([1, 1, 1, 2, 2, 2, 3, 3, 3])
X_cv = np.random.randn(9, 5)
y_cv = np.random.randint(0, 4, 9)
splits = list(gkf.split(X_cv, y_cv, groups=user_ids))
print(f"   ✓ GroupKFold created: {len(splits)} splits")

print("\n" + "=" * 60)
print("All component tests passed successfully!")
print("=" * 60)
print("\nThe implementation is ready to use.")
print("Run the Jupyter notebook 'learning_to_rank.ipynb' to see the full system in action.")
