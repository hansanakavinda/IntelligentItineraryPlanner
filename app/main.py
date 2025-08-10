import streamlit as st
from data_loader import load_data
from route_optimizer import optimize_route
from map_visualizer import display_map
from streamlit_geolocation import streamlit_geolocation
from hybrid_recommender import hybrid_recommend

# Page configuration with custom theme
st.set_page_config(
    page_title="Travelio",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colors and mobile responsiveness
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1E88E5; 
        --secondary-color: #FFC107;
        --accent-color: #4CAF50;
        --background-color: #F8F9FA; 
        --text-color: #2C3E50;
        --card-background: #FFFFFF;
        --border-color: #E0E0E0;
    }
    
    /* Hide default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    # header {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #1E88E5 0%, #1976D2 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(30, 136, 229, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: #E3F2FD;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Input section styling */
    .input-section {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #45A049 0%, #4CAF50 100%);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        transform: translateY(-2px);
        color: white;
    }
    
    /* Results section */
    .results-section {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    /* Success/Warning message styling */
    .stSuccess {
        background-color: #E8F5E8;
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stWarning {
        background-color: #FFF3E0;
        border: 1px solid #FF9800;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stInfo {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .input-section {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .stButton > button {
            padding: 0.6rem 1.5rem;
            font-size: 1rem;
        }
        
        /* Stack columns on mobile */
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            padding: 1.5rem 0.5rem;
        }
        
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .input-section {
            padding: 0.75rem;
        }
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--background-color);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Loading spinner */
    .stSpinner {
        text-align: center;
        color: var(--primary-color);
    }
    
    /* Custom metric cards */
    .metric-card {
        background: var(--card-background);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid var(--border-color);
    }
    
    /* Input field improvements */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid var(--border-color);
    }
    
    .stMultiSelect > div > div {
        border-radius: 10px;
        border: 2px solid var(--border-color);
    }
    
    .stNumberInput > div > div {
        border-radius: 10px;
        border: 2px solid var(--border-color);
    }
    
    /* Focus states */
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Custom header with enhanced styling
st.markdown("""
<div class="main-header">
    <h1>🏝️ Intelligent Itinerary Planner</h1>
    <p>Discover the Beautiful South Coast of Sri Lanka</p>
</div>
""", unsafe_allow_html=True)

# Load data
data = load_data()

# Sidebar for mobile-friendly input organization
with st.sidebar:
    st.markdown("### 🎯 Plan Your Trip")
    
    # Category selection with enhanced styling
    st.markdown("#### 📍 **Choose Categories**")
    category = st.multiselect(
        "Select attraction types:",
        data['Category'].unique(),
        help="Choose one or more types of attractions you're interested in"
    )
    
    # Time limit selection
    st.markdown("#### ⏰ **Available Time**")
    time_options = [0] + list(range(1, 13))
    time_limit = st.selectbox(
        "How many hours do you have?",
        time_options,
        index=0,
        help="Select your available time for sightseeing"
    )
    
    # Budget input
    st.markdown("#### 💰 **Budget**")
    budget = st.number_input(
        "Enter your budget (LKR):",
        min_value=0,
        value=5000,
        step=500,
        help="Set your spending limit for attractions"
    )
    
    # Crowded preference
    st.markdown("#### 👥 **Crowd Preference**")
    crowded_preference = st.radio(
        "Do you prefer crowded places?",
        ("No preference", "Yes", "No"),
        help="Choose based on your preference for tourist density"
    )

# Convert crowded preference to boolean
crowded_bool = None
if crowded_preference == "Yes":
    crowded_bool = True
elif crowded_preference == "No":
    crowded_bool = False

# Initialize session state
if 'route' not in st.session_state:
    st.session_state['route'] = None

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Location section
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📍 Your Location")
    
    # Get user location
    loc = streamlit_geolocation()
    user_location = None
    
    if loc and loc["latitude"] and loc["longitude"]:
        user_location = (loc["latitude"], loc["longitude"])
        st.success(f"📍 Location detected: {user_location[0]:.4f}, {user_location[1]:.4f}")
    else:
        st.info("🔍 Click 'Get my location' and allow location access for personalized routes")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Trip summary card
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📊 Trip Summary")
    
    # Display current selections
    if category:
        st.markdown(f"**Categories:** {', '.join(category)}")
    else:
        st.markdown("**Categories:** Not selected")
    
    if time_limit > 0:
        st.markdown(f"**Duration:** {time_limit} hours")
    else:
        st.markdown("**Duration:** Not set")
    
    st.markdown(f"**Budget:** LKR {budget:,}")
    st.markdown(f"**Crowd Preference:** {crowded_preference}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Generate itinerary button
st.markdown('<div class="input-section">', unsafe_allow_html=True)
if st.button("🚀 Generate Personalized Itinerary", key="generate_btn"):
    if not category:
        st.error("⚠️ Please select at least one attraction category")
    elif time_limit == 0:
        st.error("⚠️ Please set your available time")
    else:
        with st.spinner("🔍 Finding the perfect attractions for you..."):
            recs = hybrid_recommend(data, category, time_limit, budget, crowded_bool, user_location)
            
            if recs.empty:
                st.warning("😔 No attractions found matching your preferences. Try adjusting your filters!")
                st.session_state['route'] = None
            else:
                with st.spinner("🗺️ Optimizing your route..."):
                    st.session_state['route'] = optimize_route(recs, time_limit, start_location=user_location)
                st.success(f"🎉 Found {len(st.session_state['route'])} amazing places for you!")

st.markdown('</div>', unsafe_allow_html=True)

# Display results
if st.session_state['route'] is not None:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    st.markdown("### 🗺️ Your Personalized Itinerary")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Itinerary Details", "🗺️ Route Map", "📊 Trip Analytics"])
    
    with tab1:
        # Enhanced dataframe display
        route_df = st.session_state['route']
        
        # Add trip metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🏛️ Total Stops", len(route_df))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if 'Cost' in route_df.columns:
                total_cost = route_df['Cost'].sum()
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("💰 Total Cost", f"LKR {total_cost:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            if 'AvgVisitTimeHrs' in route_df.columns:
                total_time = route_df['AvgVisitTimeHrs'].sum()
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("⏱️ Total Time", f"{total_time:.1f} hours")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            if 'Popularity' in route_df.columns:
                avg_popularity = route_df['Popularity'].mean()
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("⭐ Avg. Rating", f"{avg_popularity:.1f}/10")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display the route table
        st.dataframe(
            route_df,
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        # Map display
        display_map(st.session_state['route'])
    
    with tab3:
        # Trip analytics
        if len(route_df) > 1:
            # Category distribution
            if 'Category' in route_df.columns:
                st.markdown("#### 📊 Attraction Categories")
                category_counts = route_df['Category'].value_counts()
                st.bar_chart(category_counts)
            
            # Cost distribution
            if 'Cost' in route_df.columns:
                st.markdown("#### 💰 Cost Distribution")
                st.bar_chart(route_df.set_index('Name')['Cost'])
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🏝️ Discover Sri Lanka's Hidden Gems | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)