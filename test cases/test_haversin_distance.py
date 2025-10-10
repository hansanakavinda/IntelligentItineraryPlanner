import sys
import os

# Add the app directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from utils import haversine_distance

# Test Case 1: Haversine Distance Calculation
print("Test Case 1: Haversine Distance Calculation")
print("-" * 40)

# Input coordinates
galle_fort = {'Latitude': 6.0535, 'Longitude': 80.2200}
unawatuna_beach = {'Latitude': 6.0211, 'Longitude': 80.2503}

print(f"Galle Fort: {galle_fort}")
print(f"Unawatuna Beach: {unawatuna_beach}")

# Calculate distance
distance = haversine_distance(galle_fort, unawatuna_beach)

print(f"\nCalculated Distance: {distance:.2f} km")
print(f"Expected Range: 4.5 - 5.0 km")

# Verify result
if 4.5 <= distance <= 5.0:
    print("\n✅ RESULT: PASS - Distance is within expected range")
else:
    print(f"\n❌ RESULT: FAIL - Distance {distance:.2f} km is outside expected range")

print("\nTest completed!")