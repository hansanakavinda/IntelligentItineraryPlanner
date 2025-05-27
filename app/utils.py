from math import radians, cos, sin, asin, sqrt

def haversine_distance(a, b):
    lat1, lon1 = a['Latitude'], a['Longitude']
    lat2, lon2 = b['Latitude'], b['Longitude']
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r
