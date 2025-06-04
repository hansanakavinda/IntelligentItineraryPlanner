from utils import haversine_distance
import pandas as pd

def optimize_route(attractions, time_limit, start_location=None):
    # If user location is provided, create a Series with the same structure as attractions
    if start_location is not None:
        # Create a dummy row for the user location
        start = attractions.iloc[0].copy()
        start['Latitude'] = start_location[0]
        start['Longitude'] = start_location[1]
        start['Name'] = 'Your Location'
        # Optionally, set other columns to None or default values
        for col in attractions.columns:
            if col not in ['Latitude', 'Longitude', 'Name']:
                start[col] = None
    else:
        start = attractions.iloc[0]

    route = [start]
    if start_location is not None:
        remaining = attractions.copy()
    else:
        remaining = attractions.iloc[1:].copy()
    current = start

    while not remaining.empty:
        remaining['distance'] = remaining.apply(lambda x: haversine_distance(current, x), axis=1)
        next_stop = remaining.loc[remaining['distance'].idxmin()]
        route.append(next_stop)
        current = next_stop
        remaining = remaining.drop(next_stop.name)

    # Remove the distance column if present
    route_df = pd.DataFrame(route)
    # if 'distance' in route_df.columns:
    #     route_df = route_df.drop(columns=['distance'])
    return route_df
