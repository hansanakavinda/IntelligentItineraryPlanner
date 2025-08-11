import folium
import streamlit as st
import openrouteservice as ors
import os
from dotenv import load_dotenv

load_dotenv()

def get_route_between_points(start_coords, end_coords):
    """
    Get actual road route between two points using OpenRouteService
    """
    try:
        api_key = os.getenv('OPENROUTESERVICE_API_KEY') 
        client = ors.Client(key=api_key)
        
        # Get route
        coords = [start_coords[::-1], end_coords[::-1]]  # ORS uses [lon, lat]
        route = client.directions(
            coordinates=coords,
            profile='driving-car',
            format='geojson'
        )
        
        # Extract coordinates
        route_coords = route['features'][0]['geometry']['coordinates']
        # Convert back to [lat, lon]
        route_coords = [[coord[1], coord[0]] for coord in route_coords]
        
        return route_coords
    except:
        # Fallback to straight line if API fails
        return [start_coords, end_coords]

def display_map(route):
    # Use the correct column names (case-sensitive)
    lat_col = 'Latitude' if 'Latitude' in route.columns else 'latitude'
    lon_col = 'Longitude' if 'Longitude' in route.columns else 'longitude'
    
    # Calculate center and bounds
    if len(route) > 1:
        min_lat, max_lat = route[lat_col].min(), route[lat_col].max()
        min_lon, max_lon = route[lon_col].min(), route[lon_col].max()
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        # Calculate distance span to determine appropriate zoom
        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon
        max_span = max(lat_span, lon_span)
        
        # Set zoom based on span (smaller span = higher zoom)
        if max_span < 0.01:  # Very close locations
            zoom_level = 14
        elif max_span < 0.05:  # Close locations
            zoom_level = 12
        elif max_span < 0.1:  # Medium distance
            zoom_level = 11
        elif max_span < 0.3:  # Larger distance
            zoom_level = 10
        else:  # Very far apart
            zoom_level = 9
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)
        
        # Add actual road routes between consecutive locations
        for i in range(len(route) - 1):
            start_point = [route.iloc[i][lat_col], route.iloc[i][lon_col]]
            end_point = [route.iloc[i+1][lat_col], route.iloc[i+1][lon_col]]
            
            # Get actual road route
            road_route = get_route_between_points(start_point, end_point)
            
            folium.PolyLine(
                locations=road_route,
                color='blue',
                weight=4,
                opacity=0.8,
                popup=f'Route from Stop {i+1} to Stop {i+2}'
            ).add_to(m)
            
        # Add small padding to bounds (much smaller than before)
        lat_margin = max(lat_span * 0.15, 0.005)  # Minimum margin
        lon_margin = max(lon_span * 0.15, 0.005)  # Minimum margin
        
        southwest = [min_lat - lat_margin, min_lon - lon_margin]
        northeast = [max_lat + lat_margin, max_lon + lon_margin]
        m.fit_bounds([southwest, northeast])
        
    else:
        # Single location - use a reasonable zoom level
        m = folium.Map(location=[route.iloc[0][lat_col], route.iloc[0][lon_col]], zoom_start=13)
    
    # Add markers
    for idx, row in route.iterrows():
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=f"Stop {idx+1}: {row.get('Name', 'Attraction')}",
            tooltip=f"Stop {idx+1}: {row.get('Name', 'Attraction')}"
        ).add_to(m)
    
    map_html = m._repr_html_()
    
    # Wrap with responsive container
    responsive_html = f"""
    <div style="width: 100%; height: 600px; border: none;">
        {map_html}
    </div>
    <script>
        // Force map to take full container size
        var mapDiv = document.querySelector('.folium-map');
        if (mapDiv) {{
            mapDiv.style.width = '100%';
            mapDiv.style.height = '600px';
        }}
    </script>
    """
    
    st.components.v1.html(
        responsive_html, 
        height=600,
        scrolling=False
    )