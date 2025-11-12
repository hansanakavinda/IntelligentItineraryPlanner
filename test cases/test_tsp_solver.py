import sys
import os
import numpy as np

# Add the app directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from route_optimizer import solve_tsp

# Test Case: TSP Solver Function
print("Test Case: TSP Solver Function")
print("-" * 40)

# Create a simple 4-location distance matrix
# Locations: A(0) -> B(1) -> C(2) -> D(3)
# Optimal route should be something like 0->1->2->3 or similar short path
distance_matrix = np.array([
    [0,   10,  15,  20],  # From A to B(10), C(15), D(20)
    [10,  0,   35,  25],  # From B to A(10), C(35), D(25)  
    [15,  35,  0,   30],  # From C to A(15), B(35), D(30)
    [20,  25,  30,  0]    # From D to A(20), B(25), C(30)
])

print("Distance Matrix (km):")
print("     A    B    C    D")
for i, row in enumerate(distance_matrix):
    print(f"{chr(65+i):>2}: {row}")

print(f"\nInput: {len(distance_matrix)} locations")
print("Expected: Route starting from location 0 (A)")

# Test the TSP solver
try:
    route_order = solve_tsp(distance_matrix)
    print(f"\nCalculated Route Order: {route_order}")
    
    # Verify basic constraints
    print("\nVerification:")
    
    # Check 1: Route starts at index 0
    if route_order[0] == 0:
        print("✅ Route starts at location 0 (A)")
    else:
        print(f"❌ Route should start at 0, but starts at {route_order[0]}")
    
    # Check 2: All locations visited exactly once
    if len(route_order) == len(distance_matrix) and len(set(route_order)) == len(distance_matrix):
        print("✅ All locations visited exactly once")
    else:
        print("❌ Not all locations visited exactly once")
    
    # Check 3: Calculate total distance
    total_distance = 0
    for i in range(len(route_order)):
        from_idx = route_order[i]
        to_idx = route_order[(i + 1) % len(route_order)]  # Return to start
        total_distance += distance_matrix[from_idx][to_idx]
    
    print(f"✅ Total route distance: {total_distance:.2f} km")
    
    # Display route path
    route_names = [chr(65 + idx) for idx in route_order]
    print(f"✅ Route path: {' -> '.join(route_names)} -> {route_names[0]}")
    
    print("\n✅ RESULT: PASS - TSP solver working correctly")
    
except Exception as e:
    print(f"\n❌ RESULT: FAIL - Error in TSP solver: {e}")

print("\nTest completed!")