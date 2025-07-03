import pytest
import pandas as pd
import numpy as np
from app.route_optimizer import optimize_route, haversine_matrix, solve_tsp
from app.data_loader import load_data

# Test data profiles for route optimization accuracy testing
ROUTE_TEST_PROFILES = [
    {
        "profile_name": "simple_triangle_route",
        "attractions": pd.DataFrame({
            'Name': ['Point A', 'Point B', 'Point C'],
            'Latitude': [6.0, 6.1, 6.05],
            'Longitude': [80.0, 80.0, 80.1],
            'Category': ['Beach', 'Nature', 'Cultural'],
            'Description': ['Beach A', 'Forest B', 'Temple C'],
            'Cost': [0, 500, 200],
            'AvgVisitTimeHrs': [1, 2, 1.5],
            'Popularity': [7, 8, 6],
            'Crowded': ['No', 'No', 'Yes']
        }),
        "time_limit": 8,
        "start_location": (6.0, 80.0),
        "expected_properties": {
            "starts_with_user_location": True,
            "visits_all_attractions": True,
            "max_attractions": 4  # 3 attractions + user location
        }
    },
    {
        "profile_name": "single_attraction",
        "attractions": pd.DataFrame({
            'Name': ['Solo Beach'],
            'Latitude': [6.0],
            'Longitude': [80.5],
            'Category': ['Beach'],
            'Description': ['Beautiful beach'],
            'Cost': [0],
            'AvgVisitTimeHrs': [2],
            'Popularity': [9],
            'Crowded': ['No']
        }),
        "time_limit": 4,
        "start_location": (6.05, 80.45),
        "expected_properties": {
            "starts_with_user_location": True,
            "visits_all_attractions": True,
            "max_attractions": 2  # 1 attraction + user location
        }
    },
    {
        "profile_name": "linear_coastal_route",
        "attractions": pd.DataFrame({
            'Name': ['Galle Fort', 'Unawatuna Beach', 'Mirissa Beach', 'Weligama Bay'],
            'Latitude': [6.0269, 6.0094, 5.9485, 5.973],
            'Longitude': [80.217, 80.2488, 80.455, 80.429],
            'Category': ['Historical', 'Beach', 'Beach', 'Beach'],
            'Description': ['Historic fort', 'Beach resort', 'Whale watching', 'Surf spot'],
            'Cost': [0, 0, 0, 0],
            'AvgVisitTimeHrs': [2, 2.5, 3, 2.5],
            'Popularity': [9, 8, 8, 7],
            'Crowded': ['Yes', 'Yes', 'Yes', 'Yes']
        }),
        "time_limit": 12,
        "start_location": None,  # No user location
        "expected_properties": {
            "starts_with_user_location": False,
            "visits_all_attractions": True,
            "max_attractions": 4
        }
    },
    {
        "profile_name": "distant_scattered_attractions",
        "attractions": pd.DataFrame({
            'Name': ['North Point', 'South Point', 'East Point', 'West Point', 'Center Point'],
            'Latitude': [6.2, 5.8, 6.0, 6.0, 6.0],
            'Longitude': [80.0, 80.0, 80.4, 79.6, 80.0],
            'Category': ['Nature', 'Beach', 'Wildlife', 'Cultural', 'Historical'],
            'Description': ['Northern reserve', 'Southern beach', 'Eastern safari', 'Western temple', 'Central fort'],
            'Cost': [1000, 0, 3500, 500, 0],
            'AvgVisitTimeHrs': [3, 2, 4, 1.5, 2],
            'Popularity': [7, 8, 10, 6, 9],
            'Crowded': ['No', 'Yes', 'Yes', 'No', 'Yes']
        }),
        "time_limit": 20,
        "start_location": (6.0, 80.0),  # Center point
        "expected_properties": {
            "starts_with_user_location": True,
            "visits_all_attractions": True,
            "max_attractions": 6  # 5 attractions + user location
        }
    },
    {
        "profile_name": "real_world_sample",
        "attractions": "load_from_data",  # Will use actual data
        "category_filter": ["Nature", "Beach"],
        "max_attractions": 5,
        "time_limit": 8,
        "start_location": (6.05, 80.22),
        "expected_properties": {
            "starts_with_user_location": True,
            "visits_all_attractions": True,
            "logical_geographic_order": True,
            "max_attractions": 6  # 5 attractions + user location
        }
    }
]

@pytest.mark.parametrize("profile", ROUTE_TEST_PROFILES)
def test_optimize_route(profile):
    """Test the route optimization function with various scenarios."""
    
    # Prepare test data
    if isinstance(profile["attractions"], str) and profile["attractions"] == "load_from_data":
        # Load real data and filter
        data = load_data()
        max_attractions = profile.get("max_attractions", 10)  # Default fallback
        attractions = data[data['Category'].isin(profile["category_filter"])].head(max_attractions)
    else:
        attractions = profile["attractions"]
    
    print(f"\n=== Testing {profile['profile_name']} ===")
    print(f"Input attractions: {len(attractions)}")
    print(f"Start location: {profile['start_location']}")
    print(f"Time limit: {profile['time_limit']}h")
    
    # Run optimization
    result = optimize_route(
        attractions=attractions,
        time_limit=profile["time_limit"],
        start_location=profile["start_location"]
    )
    
    print(f"Route result: {len(result)} stops")
    print("Route order:", result['Name'].tolist())
    
    # --- Test 1: Result is not empty ---
    assert not result.empty, f"[{profile['profile_name']}] Route optimization returned empty result"
    
    # --- Test 2: Required columns exist ---
    required_columns = ['Name', 'Latitude', 'Longitude']
    for col in required_columns:
        assert col in result.columns, f"[{profile['profile_name']}] Missing required column: {col}"
    
    # --- Test 3: Check if starts with user location (when provided) ---
    if profile["expected_properties"]["starts_with_user_location"]:
        assert result.iloc[0]['Name'] == 'Your Location', f"[{profile['profile_name']}] Route should start with user location"
        # Verify coordinates match
        assert abs(result.iloc[0]['Latitude'] - profile["start_location"][0]) < 0.001, "Start latitude mismatch"
        assert abs(result.iloc[0]['Longitude'] - profile["start_location"][1]) < 0.001, "Start longitude mismatch"
    
    # --- Test 4: Check number of attractions ---
    expected_count = profile["expected_properties"]["max_attractions"]
    assert len(result) <= expected_count, f"[{profile['profile_name']}] Too many attractions in route: {len(result)} > {expected_count}"
    
    if profile["expected_properties"]["visits_all_attractions"]:
        assert len(result) == expected_count, f"[{profile['profile_name']}] Should visit all attractions: {len(result)} != {expected_count}"
    
    # --- Test 5: No duplicate attractions (except user location) ---
    attraction_names = result[result['Name'] != 'Your Location']['Name'].tolist()
    assert len(attraction_names) == len(set(attraction_names)), f"[{profile['profile_name']}] Duplicate attractions found in route"
    
    # --- Test 6: Valid coordinates ---
    assert all(result['Latitude'].notna()), f"[{profile['profile_name']}] Found NaN latitudes"
    assert all(result['Longitude'].notna()), f"[{profile['profile_name']}] Found NaN longitudes"
    assert all((result['Latitude'] >= 5.5) & (result['Latitude'] <= 6.5)), f"[{profile['profile_name']}] Invalid latitudes (outside Sri Lanka south)"
    assert all((result['Longitude'] >= 79.5) & (result['Longitude'] <= 81.5)), f"[{profile['profile_name']}] Invalid longitudes (outside Sri Lanka south)"


def test_haversine_matrix():
    """Test the haversine distance matrix calculation."""
    # Create simple test data
    test_locations = pd.DataFrame({
        'Latitude': [6.0, 6.1, 6.0],
        'Longitude': [80.0, 80.0, 80.1],
        'Name': ['A', 'B', 'C']
    })
    
    matrix = haversine_matrix(test_locations)
    
    # --- Test 1: Matrix properties ---
    assert matrix.shape == (3, 3), "Distance matrix should be 3x3"
    assert np.all(np.diag(matrix) == 0), "Diagonal should be zero (distance to self)"
    assert np.allclose(matrix, matrix.T), "Matrix should be symmetric"
    
    # --- Test 2: Positive distances ---
    mask = ~np.eye(3, dtype=bool)  # Exclude diagonal
    assert np.all(matrix[mask] > 0), "All distances should be positive"
    
    # --- Test 3: Reasonable distance values ---
    # Distance from (6.0, 80.0) to (6.1, 80.0) should be ~11km
    distance_AB = matrix[0, 1]
    assert 10 < distance_AB < 15, f"Distance A-B seems unrealistic: {distance_AB}km"


def test_solve_tsp():
    """Test the TSP solver with known optimal solutions."""
    # Simple 3-point triangle - optimal route should be short
    distance_matrix = np.array([
        [0, 10, 15],
        [10, 0, 20],
        [15, 20, 0]
    ])
    
    route = solve_tsp(distance_matrix)
    
    # --- Test 1: Valid route ---
    assert len(route) == 3, "Route should visit all 3 points"
    assert set(route) == {0, 1, 2}, "Route should include all indices"
    assert route[0] == 0, "Route should start from depot (index 0)"
    
    # --- Test 2: Calculate total distance ---
    total_distance = sum(distance_matrix[route[i], route[(i+1) % len(route)]] for i in range(len(route)))
    
    # For this simple case, optimal should be around 45 (10+20+15 or 10+15+20)
    assert total_distance <= 50, f"TSP solution seems suboptimal: {total_distance}"


def test_edge_cases():
    """Test edge cases and error handling."""
    
    # --- Test 1: Empty attractions ---
    empty_df = pd.DataFrame(columns=['Name', 'Latitude', 'Longitude', 'Category', 'Cost', 'AvgVisitTimeHrs'])
    
    with pytest.raises(Exception):
        optimize_route(empty_df, time_limit=5)
    
    # --- Test 2: Single attraction ---
    single_attraction = pd.DataFrame({
        'Name': ['Test Beach'],
        'Latitude': [6.0],
        'Longitude': [80.0],
        'Category': ['Beach'],
        'Description': ['Test'],
        'Cost': [0],
        'AvgVisitTimeHrs': [2],
        'Popularity': [7],
        'Crowded': ['No']
    })
    
    result = optimize_route(single_attraction, time_limit=5, start_location=(6.05, 80.05))
    assert len(result) == 2, "Should have user location + 1 attraction"
    assert result.iloc[0]['Name'] == 'Your Location'
    assert result.iloc[1]['Name'] == 'Test Beach'


def test_route_efficiency():
    """Test if the route is reasonably efficient (not completely random)."""
    # Create attractions in a line - optimal route should follow the line
    linear_attractions = pd.DataFrame({
        'Name': [f'Point_{i}' for i in range(5)],
        'Latitude': [6.0 + i*0.01 for i in range(5)],  # 6.0, 6.01, 6.02, 6.03, 6.04
        'Longitude': [80.0] * 5,  # All on same longitude
        'Category': ['Beach'] * 5,
        'Description': ['Test'] * 5,
        'Cost': [0] * 5,
        'AvgVisitTimeHrs': [1] * 5,
        'Popularity': [7] * 5,
        'Crowded': ['No'] * 5
    })
    
    result = optimize_route(linear_attractions, time_limit=10, start_location=(6.0, 80.0))
    
    # Check if route generally follows the linear order (allowing some flexibility)
    latitudes = result['Latitude'].tolist()
    
    # Route should be somewhat monotonic (not jumping back and forth excessively)
    direction_changes = 0
    for i in range(1, len(latitudes)-1):
        if (latitudes[i] - latitudes[i-1]) * (latitudes[i+1] - latitudes[i]) < 0:
            direction_changes += 1
    
    # Allow some direction changes but not too many for a linear route
    assert direction_changes <= len(latitudes) // 2, f"Route has too many direction changes: {direction_changes}"


# Run with: pytest tests/test_route_optimizer.py -v -s
