import streamlit as st
from data_loader import load_data
from recommender import generate_recommendations
from optimizer import optimize_route
from map_visualizer import display_map
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(layout="wide")
st.title("Intelligent Itinerary  – Down South Sri Lanka")

data = load_data()

category = st.multiselect("Choose attraction categories:", data['Category'].unique())
time_options = [0] + list(range(1, 13))
time_limit = st.selectbox("Available time (in hours):", time_options, index=0)

if 'route' not in st.session_state:
    st.session_state['route'] = None

# Get user location
loc = streamlit_geolocation()
user_location = None
if loc and loc["latitude"] and loc["longitude"]:
    user_location = (loc["latitude"], loc["longitude"])
    st.success(f"Your location: {user_location}")
else:
    st.info("Click 'Get my location' and allow location access in your browser.")

if st.button("Generate Itinerary"):
    recs = generate_recommendations(data, category)
    # Pass user_location to optimize_route if available
    st.session_state['route'] = optimize_route(recs, time_limit, start_location=user_location)

if st.session_state['route'] is not None:
    st.write("### Recommended Itinerary")
    st.dataframe(st.session_state['route'])
    st.write("Route columns:", st.session_state['route'].columns)
    st.write(st.session_state['route'].head())
    display_map(st.session_state['route'])
    st.write("Recommendations columns:", recs.columns)
    st.write(recs.head())
