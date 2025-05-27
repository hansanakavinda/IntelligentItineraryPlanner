import folium
import streamlit as st

def display_map(route):
    # Use the correct column names (case-sensitive)
    lat_col = 'Latitude' if 'Latitude' in route.columns else 'latitude'
    lon_col = 'Longitude' if 'Longitude' in route.columns else 'longitude'
    m = folium.Map(location=[route.iloc[0][lat_col], route.iloc[0][lon_col]], zoom_start=11)
    for _, row in route.iterrows():
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=row.get('Name', 'Attraction')
        ).add_to(m)
    st.components.v1.html(m._repr_html_(), height=500)
