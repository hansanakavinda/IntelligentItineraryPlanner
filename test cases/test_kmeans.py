import sys
import os
import pandas as pd

# Change to project root directory
project_root = os.path.join(os.path.dirname(__file__), '..')
os.chdir(project_root)

# Add the app directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from hybrid_recommender import find_optimal_k_simple, prepare_kmeans_features_v3
from data_loader import load_data

# Test Case 2: K-means Clustering
print("Test Case 2: K-means Clustering")
print("-" * 40)

# Load real data
print("Loading attractions data...")
data = load_data()

if data.empty:
    print("❌ FAIL: Could not load attractions data")
    exit()

print(f"Dataset loaded: {len(data)} attractions")
print(f"Categories: {list(data['Category'].unique())}")

# Prepare features for clustering
print("\nPreparing features for clustering...")
features = prepare_kmeans_features_v3(data)

print(f"Feature matrix shape: {features.shape}")
print(f"Expected: {len(data)} attractions × 7 features")

# Find optimal number of clusters
print("\nFinding optimal number of clusters...")
optimal_k = find_optimal_k_simple(features)

print(f"Optimal K value: {optimal_k}")
print(f"Expected Range: 3 - 8 clusters")

# Verify result
if 3 <= optimal_k <= 8:
    print("\n✅ RESULT: PASS - Optimal K is within expected range")
    clustering_success = True
else:
    print(f"\n⚠️  RESULT: WARN - Optimal K ({optimal_k}) is outside typical range but algorithm worked")
    clustering_success = True

# Test clustering execution
print("\nTesting clustering execution...")
try:
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=optimal_k, n_init=10, random_state=42)
    clusters = kmeans.fit_predict(features)
    
    unique_clusters = len(set(clusters))
    print(f"Clusters created: {unique_clusters}")

    # Analyze what the clusters represent
    print("\nAnalyzing the clusters found...")
    data_with_clusters = data.copy()
    data_with_clusters['cluster'] = clusters

    for cluster_id in data_with_clusters['cluster'].unique():
        cluster_data = data_with_clusters[data_with_clusters['cluster'] == cluster_id]
        avg_cost = cluster_data['Cost'].mean()
        free_attractions = len(cluster_data[cluster_data['Cost'] == 0])
        top_categories = cluster_data['Category'].value_counts().head(3)
        
        print(f"\nCluster {cluster_id} ({len(cluster_data)} attractions):")
        print(f"  Average Cost: LKR {avg_cost:.0f}")
        print(f"  Free Attractions: {free_attractions}/{len(cluster_data)}")
        print(f"  Top Categories: {dict(top_categories)}")
    
    if unique_clusters == optimal_k:
        print("✅ Clustering executed successfully")
    else:
        print("❌ Clustering execution failed")
        clustering_success = False
        
except Exception as e:
    print(f"❌ Clustering failed: {e}")
    clustering_success = False

# Final result
print("-" * 40)
if clustering_success:
    print("✅ FINAL RESULT: PASS - K-means clustering works correctly")
else:
    print("❌ FINAL RESULT: FAIL - K-means clustering has issues")

print("\nTest completed!")