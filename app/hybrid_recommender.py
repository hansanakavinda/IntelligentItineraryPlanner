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

def find_optimal_k_simple(features, max_k=8):
    """Simple elbow method implementation with detailed logging"""
    print(f"\n=== ELBOW METHOD DEBUG ===")
    print(f"Input features shape: {features.shape}")
    print(f"Features used: {list(features.columns)}")
    print(f"Max k to test: {max_k}")
    
    if len(features) <= 2:
        print(f"Too few data points ({len(features)}), returning k=1")
        return 1
    
    max_k = min(max_k, len(features))
    print(f"Adjusted max_k (limited by data size): {max_k}")
    
    wcss = []
    print(f"\n--- Calculating WCSS for different k values ---")
    
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        kmeans.fit(features)
        wcss_value = kmeans.inertia_
        wcss.append(wcss_value)
        print(f"k={k}: WCSS = {wcss_value:.2f}")
    
    print(f"\nWCSS values: {[f'{w:.2f}' for w in wcss]}")
    
    # Find elbow using rate of change
    if len(wcss) >= 3:
        print(f"\n--- Finding Elbow Point ---")
        differences = [wcss[i-1] - wcss[i] for i in range(1, len(wcss))]
        print(f"First differences (WCSS reduction): {[f'{d:.2f}' for d in differences]}")
        
        max_difference = max(differences)
        max_diff_index = differences.index(max_difference)
        optimal_k = max_diff_index + 2  # +2 because differences start from k=2
        
        print(f"Maximum WCSS reduction: {max_difference:.2f} (between k={max_diff_index+1} and k={max_diff_index+2})")
        print(f"Elbow point found at k={optimal_k}")
        
        # Show why this k is optimal
        if optimal_k > 1:
            improvement_before = differences[max_diff_index]
            if max_diff_index + 1 < len(differences):
                improvement_after = differences[max_diff_index + 1]
                print(f"WCSS reduction at optimal k: {improvement_before:.2f}")
                print(f"WCSS reduction after optimal k: {improvement_after:.2f}")
                print(f"Diminishing returns ratio: {improvement_after/improvement_before:.2f}")
        
        final_k = min(optimal_k, max_k)
        print(f"Final optimal k: {final_k}")
        return final_k
    else:
        print(f"Not enough k values to find elbow, returning k={len(wcss)}")
        return len(wcss)

def hybrid_recommend(
    data,
    selected_categories,
    time_limit,
    budget,
    crowded_preference,
    user_location=None,
    top_k_candidates=3,
    return_explanation_data=False  # NEW: Return data for XAI explanation
):
    # Filter by category and crowded preference
    filtered = data[data['Category'].isin(selected_categories)].copy()
    if crowded_preference is not None:
        if crowded_preference:
            filtered = filtered[filtered['Crowded'] == 'Yes']
        else:
            filtered = filtered[filtered['Crowded'] == 'No']
    if filtered.empty:
        if return_explanation_data:
            return pd.DataFrame([]), {}
        return pd.DataFrame([])

    # KMeans clustering for diversity (by location and duration)
    kmeans_features = filtered[['Latitude', 'Longitude', 'AvgVisitTimeHrs']]
    n_clusters = find_optimal_k_simple(kmeans_features)
    print(f"Optimal clusters using elbow method: {n_clusters}")
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    filtered['cluster'] = kmeans.fit_predict(kmeans_features)
    
    print(f"Number of clusters formed: {n_clusters}")

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

    # Store original filtered data for explanation
    explanation_data = {
        'original_data': data.copy(),
        'filtered_data': filtered.copy(),
        'kmeans_model': kmeans,
        'tfidf_matrix': tfidf_matrix,
        'tfidf_vectorizer': tfidf,
        'selected_categories': selected_categories,
        'time_limit': time_limit,
        'budget': budget,
        'crowded_preference': crowded_preference,
        'user_location': user_location,
        'n_clusters': n_clusters
    }

    # ===== IMPROVED GREEDY SELECTION ALGORITHM =====
    selected = []
    total_time = 0
    total_cost = 0
    current = start
    remaining = filtered.copy()
    selection_steps = []  # NEW: Track selection process for explanation
    
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
        
        # Store selection step for explanation
        selection_steps.append({
            'step': len(selected) + 1,
            'selected_attraction': best_candidate['Name'],
            'efficiency_score': best_candidate['efficiency_score'],
            'content_score': best_candidate['content_score'],
            'hybrid_score': best_candidate['hybrid_score'],
            'travel_time': best_candidate['travel_time'],
            'total_time_so_far': total_time + best_candidate['total_time'],
            'total_cost_so_far': total_cost + best_candidate['Cost'],
            'feasible_options': len(feasible_attractions),
            'top_candidates': top_candidates[['Name', 'efficiency_score']].to_dict('records')
        })
        
        # Add selected attraction to itinerary
        next_attraction = remaining.loc[next_idx]
        selected.append(next_attraction)
        total_time += next_attraction['total_time']
        total_cost += next_attraction['Cost']
        current = next_attraction
        remaining = remaining.drop(next_idx)
    
    # Add selection steps to explanation data
    explanation_data['selection_steps'] = selection_steps
    
    # Return results
    if selected:
        result = pd.DataFrame(selected)
        # Clean up temporary columns
        columns_to_drop = [
            'cluster', 'content_score', 'hybrid_score', 'travel_time', 'total_time',
            'value_time_ratio', 'value_cost_ratio', 'value_budget_ratio', 'efficiency_score'
        ]
        result = result.drop(columns=columns_to_drop, errors='ignore')
        result = result.reset_index(drop=True)
        
        if return_explanation_data:
            explanation_data['final_route'] = result
            return result, explanation_data
        return result
    else:
        if return_explanation_data:
            return pd.DataFrame([]), explanation_data
        return pd.DataFrame([])