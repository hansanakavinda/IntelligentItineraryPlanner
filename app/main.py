import streamlit as st
from data_loader import load_data
# from recommender import generate_recommendations
# from optimizer import optimize_route
from route_optimizer import optimize_route
from map_visualizer import display_map
from streamlit_geolocation import streamlit_geolocation
from hybrid_recommender import hybrid_recommend

st.set_page_config(layout="wide")
st.title("Intelligent Itinerary  – Down South Sri Lanka")

data = load_data()

category = st.multiselect("Choose attraction categories:", data['Category'].unique())
time_options = [0] + list(range(1, 13))
time_limit = st.selectbox("Available time (in hours):", time_options, index=0)
budget = st.number_input("Enter your budget (LKR):", min_value=0, value=5000, step=500)
crowded_preference = st.radio("Do you like crowded places?", ("No preference", "Yes", "No"))
crowded_bool = None
if crowded_preference == "Yes":
    crowded_bool = True
elif crowded_preference == "No":
    crowded_bool = False

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

if st.button("Generate Hybrid Itinerary"):
    recs = hybrid_recommend(data, category, time_limit, budget, crowded_bool, user_location)
    if recs.empty:
        st.warning("No attractions found matching your preferences and constraints.")
        st.session_state['route'] = None
    else:
        st.session_state['route'] = optimize_route(recs, time_limit, start_location=user_location)

if st.session_state['route'] is not None:
    st.write("### Recommended Itinerary")
    st.dataframe(st.session_state['route'])
    display_map(st.session_state['route'])
