from utils import haversine_distance
import pandas as pd

def optimize_route(attractions, time_limit, start_location=None):
    # Use start_location as the starting point if provided
    # Otherwise, use the first attraction as the start
    if start_location is not None:
        start = start_location
    else:
        start = attractions.iloc[0]

    route = [start]
    remaining = attractions.iloc[1:].copy()
    current = start

    while not remaining.empty:
        remaining['distance'] = remaining.apply(lambda x: haversine_distance(current, x), axis=1)
        next_stop = remaining.loc[remaining['distance'].idxmin()]
        route.append(next_stop)
        current = next_stop
        remaining = remaining.drop(next_stop.name)

    return pd.DataFrame(route)

def optimize_route(recommendations, time_limit, start_location=None):
    # ...your route optimization logic...
    # Example: return the recommendations as is (ensure columns exist)
    columns_needed = ['Name', 'Latitude', 'Longitude']
    if all(col in recommendations.columns for col in columns_needed):
        return recommendations[columns_needed]
    else:
        # Fallback: return recommendations with all columns
        return recommendations
