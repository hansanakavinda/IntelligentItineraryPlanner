import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from utils import haversine_distance
import numpy as np

# Helper to estimate travel time (in hours) given distance (km), assuming avg speed 40km/h
AVG_SPEED_KMH = 40

def estimate_travel_time_km(distance_km):
    return distance_km / AVG_SPEED_KMH

def hybrid_recommend(
    data,
    selected_categories,
    time_limit,
    budget,
    crowded_preference,
    user_location=None
):
    # Filter by category and crowded preference
    filtered = data[data['Category'].isin(selected_categories)].copy()
    if crowded_preference is not None:
        if crowded_preference:
            filtered = filtered[filtered['Crowded'] == 'Yes']
        else:
            filtered = filtered[filtered['Crowded'] == 'No']
    if filtered.empty:
        return pd.DataFrame([])

    # KMeans clustering for diversity (by location and duration)
    kmeans_features = filtered[['Latitude', 'Longitude', 'AvgVisitTimeHrs']]
    n_clusters = min(3, len(filtered))
    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    filtered['cluster'] = kmeans.fit_predict(kmeans_features)

    # Content-based filtering (TF-IDF on Description)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(filtered['Description'])
    # If user_location is provided, use it as the start; else, use first attraction
    if user_location is not None:
        start = filtered.iloc[0].copy()
        start['Latitude'] = user_location[0]
        start['Longitude'] = user_location[1]
        start['Name'] = 'Your Location'
        for col in filtered.columns:
            if col not in ['Latitude', 'Longitude', 'Name']:
                start[col] = None
    else:
        start = filtered.iloc[0]
    # Cosine similarity to all attractions (use mean vector for all descriptions)
    mean_vec = np.asarray(tfidf_matrix.mean(axis=0)).reshape(1, -1)
    similarity = cosine_similarity(tfidf_matrix, mean_vec)
    filtered['content_score'] = similarity.flatten()

    # Hybrid score: combine cluster diversity and content score
    filtered['hybrid_score'] = filtered['content_score'] + 0.2 * (filtered['cluster'] == filtered['cluster'].mode()[0])
    filtered = filtered.sort_values('hybrid_score', ascending=False)

    # Greedily select attractions under time and budget constraints
    selected = []
    total_time = 0
    total_cost = 0
    current = start
    remaining = filtered.copy()
    while not remaining.empty:
        # Estimate travel time from current to each remaining
        remaining['travel_time'] = remaining.apply(lambda x: estimate_travel_time_km(haversine_distance(current, x)), axis=1)
        # Total time = travel + visit
        remaining['total_time'] = remaining['travel_time'] + remaining['AvgVisitTimeHrs']
        # Select the best next attraction that fits constraints
        next_idx = None
        for idx, row in remaining.iterrows():
            if (total_time + row['total_time'] <= time_limit) and (total_cost + row['Cost'] <= budget):
                next_idx = idx
                break
        if next_idx is None:
            break
        next_attraction = remaining.loc[next_idx]
        selected.append(next_attraction)
        total_time += next_attraction['total_time']
        total_cost += next_attraction['Cost']
        current = next_attraction
        remaining = remaining.drop(next_idx)
    if selected:
        result = pd.DataFrame(selected)
        result = result.drop(columns=['cluster', 'content_score', 'hybrid_score', 'travel_time', 'total_time'], errors='ignore')
        return result.reset_index(drop=True)
    else:
        return pd.DataFrame([]) 