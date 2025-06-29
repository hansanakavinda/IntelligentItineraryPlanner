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
    user_location=None,
    top_k_candidates=3  # NEW PARAMETER: Number of top candidates to consider at each step
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
    
    # Set up starting location
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
    
    # Cosine similarity to all attractions
    mean_vec = np.asarray(tfidf_matrix.mean(axis=0)).reshape(1, -1)
    similarity = cosine_similarity(tfidf_matrix, mean_vec)
    filtered['content_score'] = similarity.flatten()

    # Hybrid score: combine cluster diversity and content score
    filtered['hybrid_score'] = filtered['content_score'] + 0.2 * (filtered['cluster'] == filtered['cluster'].mode()[0])

    # ===== IMPROVED GREEDY SELECTION ALGORITHM =====
    selected = []
    total_time = 0
    total_cost = 0
    current = start
    remaining = filtered.copy()
    
    while not remaining.empty:
        # Calculate travel time from current location to each remaining attraction
        remaining['travel_time'] = remaining.apply(
            lambda x: estimate_travel_time_km(haversine_distance(current, x)), axis=1
        )
        remaining['total_time'] = remaining['travel_time'] + remaining['AvgVisitTimeHrs']
        
        # NEW: Calculate efficiency metrics for better selection
        remaining['value_time_ratio'] = remaining['hybrid_score'] / remaining['total_time']
        remaining['value_cost_ratio'] = remaining['hybrid_score'] / (remaining['Cost'] + 0.01)  # Avoid division by zero
        remaining['value_budget_ratio'] = remaining['hybrid_score'] / (remaining['Cost'] / budget + 0.01)
        
        # NEW: Combined efficiency score that considers multiple factors
        remaining['efficiency_score'] = (
            0.4 * remaining['value_time_ratio'] + 
            0.3 * remaining['value_cost_ratio'] + 
            0.2 * remaining['hybrid_score'] +
            0.1 * remaining['value_budget_ratio']
        )
        
        # Filter attractions that fit within constraints
        feasible_attractions = remaining[
            (total_time + remaining['total_time'] <= time_limit) & 
            (total_cost + remaining['Cost'] <= budget)
        ].copy()
        
        if feasible_attractions.empty:
            break
        
        # NEW: Instead of taking the first feasible option, consider top-K candidates
        # Sort by efficiency score and take the best among top-K feasible options
        top_candidates = feasible_attractions.nlargest(
            min(top_k_candidates, len(feasible_attractions)), 
            'efficiency_score'
        )
        
        # NEW: Among top candidates, select the one with highest efficiency score
        best_candidate = top_candidates.iloc[0]
        next_idx = best_candidate.name
        
        # Add selected attraction to itinerary
        next_attraction = remaining.loc[next_idx]
        selected.append(next_attraction)
        total_time += next_attraction['total_time']
        total_cost += next_attraction['Cost']
        current = next_attraction
        remaining = remaining.drop(next_idx)
    
    # Return results
    if selected:
        result = pd.DataFrame(selected)
        # Clean up temporary columns
        columns_to_drop = [
            'cluster', 'content_score', 'hybrid_score', 'travel_time', 'total_time',
            'value_time_ratio', 'value_cost_ratio', 'value_budget_ratio', 'efficiency_score'
        ]
        result = result.drop(columns=columns_to_drop, errors='ignore')
        return result.reset_index(drop=True)
    else:
        return pd.DataFrame([])