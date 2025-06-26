from utils import haversine_distance
import pandas as pd

# NEW: Import Google OR-Tools
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import numpy as np

def haversine_matrix(locations):
    """Compute a matrix of Haversine distances between all pairs of locations."""
    n = len(locations)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0
            else:
                matrix[i][j] = haversine_distance(locations.iloc[i], locations.iloc[j])
    return matrix

def solve_tsp(distance_matrix, visit_durations=None, time_limit=None):
    """Solves the TSP using Google OR-Tools, optionally respecting visit durations and time limits.
       Returns the order of indices to visit.
    """
    n = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node] * 1000)  # Convert to meters for better granularity

    transit_callback_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_idx)

    # If visit durations are provided, set up time windows
    if visit_durations is not None or time_limit is not None:
        time_matrix = distance_matrix / 40.0  # Assume average speed 40 km/h -> hours
        time_matrix = time_matrix * 60  # Convert to minutes
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = time_matrix[from_node][to_node]
            visit_time = visit_durations[to_node] if visit_durations is not None else 0
            return int(travel_time + visit_time)
        time_callback_idx = routing.RegisterTransitCallback(time_callback)
        routing.AddDimension(
            time_callback_idx,
            30,  # allow waiting time ("slack")
            int((time_limit or 24*60)),  # max route time in minutes, default 24h
            True,
            "Time"
        )
        if time_limit is not None:
            time_dimension = routing.GetDimensionOrDie("Time")
            for idx in range(n):
                time_dimension.CumulVar(idx).SetRange(0, int(time_limit))

    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = 10  # Safety timeout

    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        # Fallback: Return indices in input order
        return list(range(n))

    # Extract route
    index = routing.Start(0)
    route_indices = []
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route_indices.append(node)
        index = solution.Value(routing.NextVar(index))
    return route_indices

def optimize_route(attractions, time_limit, start_location=None):
    """Returns an efficient sequence of attractions, minimizing travel time and distance.
    Uses nearest neighbor for fallback, Google OR-Tools for optimal routing (TSP).
    - start_location: (lat, lon) tuple. If given, used as starting point.
    - time_limit: in hours.
    """
    # Prepare DataFrame
    attractions_cp = attractions.copy()
    if start_location is not None:
        start = attractions_cp.iloc[0].copy()
        start['Latitude'] = start_location[0]
        start['Longitude'] = start_location[1]
        start['Name'] = 'Your Location'
        start['Category'] = ''
        start['Description'] = ''
        start['Cost'] = 0
        start['AvgVisitTimeHrs'] = 0
        start['Popularity'] = 0
        start['Crowded'] = ""
        attractions_cp = pd.concat([pd.DataFrame([start]), attractions_cp], ignore_index=True)
    else:
        start = attractions_cp.iloc[0]

    # Build distance matrix (in km)
    distance_matrix = haversine_matrix(attractions_cp[['Latitude', 'Longitude', 'Name']])

    # Prepare visit durations (in minutes)
    if 'Visit_Duration' in attractions_cp.columns:
        visit_durations = attractions_cp['Visit_Duration'].fillna(0).astype(float).values
    else:
        visit_durations = None

    # Convert time_limit to minutes
    time_limit_minutes = time_limit * 60 if time_limit else None

    # Try TSP optimization
    try:
        order = solve_tsp(
            distance_matrix,
            visit_durations=visit_durations,
            time_limit=time_limit_minutes
        )
    except Exception as e:
        # If OR-Tools fails, fallback to nearest neighbor
        order = [0]
        remaining = set(range(1, len(attractions_cp)))
        current = 0
        while remaining:
            next_idx = min(remaining, key=lambda i: distance_matrix[current][i])
            order.append(next_idx)
            current = next_idx
            remaining.remove(next_idx)

    route_df = attractions_cp.iloc[order].reset_index(drop=True)
    return route_df