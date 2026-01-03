import streamlit as st
from data_loader import load_data
from route_optimizer import optimize_route
from map_visualizer import display_map
from streamlit_geolocation import streamlit_geolocation
from hybrid_recommender import hybrid_recommend
from xai import XAIExplainer

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
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Modern color palette */
    :root {
        --primary-gradient: #696FC7;
        --secondary-gradient: #636CCB;
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --accent-color: #00ff00;
        --background: transparent; 
        --surface: #ffffff;
        --surface-elevated: #ffffff;
        --text-primary: #ffffff;
        --text-secondary: #ffffff;
        --border-light: #696FC7;
        --shadow-soft: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-large: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
            
    [data-testid="stHeader"] {
        background: #A7AAE1 !important;           /* header background */
    }
    
    /* Global font settings */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
            
    /* Main content background */
    [data-testid="stAppViewContainer"] {
        background: #A7AAE1 !important;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background: #696FC7 !important;
        border-right: 1px solid #696FC7 !important;
    }
    
    /* Hide Streamlit branding */
    # #MainMenu {visibility: hidden;}
    # footer {visibility: hidden;}
    # header {visibility: hidden;}
    
    /* Main container */
        
    /* Glassmorphism header */
    .main-header {
        background: #696FC7;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow-large);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .main-header h1 {
        color: white;
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.25rem;
        font-weight: 300;
        margin: 1rem 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* Modern card design */
    .input-section {
        background: var(--surface);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: var(--shadow-medium);
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-light);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .input-section:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-large);
    }
    
    .input-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
        border-radius: 20px 20px 0 0;
    }
    
    /* Futuristic buttons */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 1rem 2.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        box-shadow: var(--shadow-medium);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: var(--shadow-large);
        color: white;
        background: var(--primary-gradient);
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    /* Button ripple effect */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transition: width 0.6s, height 0.6s, top 0.6s, left 0.6s;
        transform: translate(-50%, -50%);
    }
    
    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }
    
    /* Modern input fields */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stNumberInput > div > div,
    .stTextInput > div > div {
        background: var(--surface) !important;
        transition: all 0.3s ease !important;
    }
            
    
    .stMultiSelect > div > div,
    .stTextInput > div > div {
        border-radius: 12px !important;
        border: 2px solid var(--border-light) !important;
    }
    
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stTextInput > div > div:focus-within {
        
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1) !important;
        transform: translateY(-1px);
    }
       
    /* Modern sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--surface) 0%, var(--background) 100%);
        border-right: 1px solid var(--border-light);
    }
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--background);
        padding: 8px;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--surface) !important;
        color: var(--accent-color) !important;
        box-shadow: var(--shadow-soft);
    }
    
    /* Modern metrics */
    [data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--border-light);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: var(--shadow-soft);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
    }
    
    /* Modern expandable sections */
    .streamlit-expanderHeader {
        background: var(--surface) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-light) !important;
        font-weight: 600 !important;
        padding: 1rem 1.5rem !important;
    }
    
    .streamlit-expanderContent {
        background: var(--surface) !important;
        border: 1px solid var(--border-light) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
    }
    
    /* Success/Warning/Info messages */
    .stSuccess, .stWarning, .stInfo, .stError {
        border-radius: 16px !important;
        border: none !important;
        box-shadow: var(--shadow-soft) !important;
        padding: 1.5rem !important;
        font-weight: 500;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(75, 181, 67, 0.1) 0%, rgba(56, 142, 60, 0.1) 100%) !important;
        border-left: 4px solid #4caf50 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 167, 38, 0.1) 0%, rgba(251, 140, 0, 0.1) 100%) !important;
        border-left: 4px solid #ff9800 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(21, 101, 192, 0.1) 100%) !important;
        border-left: 4px solid #2196f3 !important;
    }
    
    /* Loading animations */
    .stSpinner > div {
        border-color: var(--accent-color) transparent transparent transparent !important;
    }
    
    /* Mobile responsive improvements */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .input-section {
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .results-section {
            padding: 1.5rem;
        }
        
        .stButton > button {
            padding: 0.875rem 1.5rem;
            font-size: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .input-section {
            padding: 1rem;
        }
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
    
    st.markdown("### 📍 Your Location")
    
   # Create columns - button column will be fixed at 280px
    button_col = st.container(width=31)  # Second number is just a large flex value
    
    with button_col:
        loc = streamlit_geolocation()
    
    user_location = None
    
    if loc and loc["latitude"] and loc["longitude"]:
        user_location = (loc["latitude"], loc["longitude"])
        st.success(f"📍 Location detected: {user_location[0]:.4f}, {user_location[1]:.4f}")
    else:
        st.info("🔍 Click 'Get my location' and allow location access for personalized routes")
    
    

with col2:
    # Trip summary card
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
    

# Generate itinerary button
if st.button("🚀 Generate Personalized Itinerary", key="generate_btn"):
    if not category:
        st.error("⚠️ Please select at least one attraction category")
    elif time_limit == 0:
        st.error("⚠️ Please set your available time")
    else:
        with st.spinner("🔍 Finding the perfect attractions for you..."):
            recs, explanation_data = hybrid_recommend(
                data, category, time_limit, budget, crowded_bool, user_location,
                return_explanation_data=True
            )
            
            if recs.empty:
                st.warning("😔 No attractions found matching your preferences. Try adjusting your filters!")
                st.session_state['route'] = None
                st.session_state['explanation_data'] = None
            else:
                with st.spinner("🗺️ Optimizing your route..."):
                    st.session_state['route'] = optimize_route(recs, time_limit, start_location=user_location)
                    st.session_state['explanation_data'] = explanation_data  # NEW: Store explanation data
                    attractionCount = len(st.session_state['route'])
                    # if Your Location is included, remove it from count
                    if 'Your Location' in st.session_state['route']['Name'].values:
                        attractionCount -= 1
                st.success(f"🎉 Found {attractionCount} amazing places for you!")

                # Auto-scroll after a brief delay
                st.components.v1.html("""
                <script>
                setTimeout(function() {
                    const resultsSection = window.parent.document.querySelector('.results-section');
                    if (resultsSection) {
                        resultsSection.scrollIntoView({ 
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }, 100);
                </script>
                """, height=0)

# Display results
if st.session_state['route'] is not None:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    st.markdown("### 🗺️ Your Personalized Itinerary")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📍 Attraction Details", "🗺️ Route Map", "🤖 AI Explanation"])

    with tab1:
        # NEW: Attraction Details Tab
        st.markdown("### 📍 Your Selected Attractions")
        st.markdown("*Detailed information about each attraction in your itinerary*")
        
        if len(st.session_state['route']) > 0:
            # Create info cards for each attraction
            for idx, attraction in st.session_state['route'].iterrows():
                # Skip if this is the starting location marker
                if attraction['Name'] == 'Your Location':
                    continue
                    
                # Create expandable card for each attraction
                with st.expander(f"🏛️ **{attraction['Name']}** - {attraction['Category']}", expanded=True):
                    # Create columns for better layout
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Description
                        st.markdown("**📖 Description:**")
                        st.markdown(f"{attraction['Description']}")
                        
                    
                    with col2:
                        # Cost metric
                        if attraction['Cost'] == 0:
                            st.metric(
                                label="💰 Entry Cost",
                                value="FREE",
                                help="No entrance fee required"
                            )
                        else:
                            st.metric(
                                label="💰 Entry Cost", 
                                value=f"LKR {attraction['Cost']:,}",
                                help="Entrance fee per person"
                            )
                        
                        # Visit time metric
                        st.metric(
                            label="⏱️ Visit Duration",
                            value=f"{attraction['AvgVisitTimeHrs']:.1f} hours",
                            help="Average time visitors spend here"
                        )
                        
                        # Popularity rating
                        popularity_stars = "⭐" * int(attraction['Popularity'])
                        st.metric(
                            label="⭐ Popularity Rating",
                            value=f"{attraction['Popularity']}/10",
                            delta=f"{popularity_stars}",
                            help="Visitor rating out of 10"
                        )
                        
                        # Crowded status
                        crowd_icon = "👥" if attraction['Crowded'] == 'Yes' else "🌟"
                        crowd_text = "Usually Crowded" if attraction['Crowded'] == 'Yes' else "Less Crowded"
                        st.info(f"{crowd_icon} {crowd_text}")
            
            # Summary statistics at the bottom
            st.markdown("---")
            st.markdown("### 📊 Trip Summary")

            route_excl_location = st.session_state['route']
            # create a new dataframe excluding 'Your Location'
            if 'Your Location' in st.session_state['route']['Name'].values:
                route_excl_location = st.session_state['route'][st.session_state['route']['Name'] != 'Your Location']
            # Calculate totals
            total_cost = route_excl_location['Cost'].sum()
            total_time = route_excl_location['AvgVisitTimeHrs'].sum()
            avg_popularity = route_excl_location['Popularity'].mean()
            total_attractions = len(route_excl_location)

            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "🏛️ Total Attractions",
                    f"{total_attractions}",
                    help="Number of places to visit"
                )
            
            with col2:
                st.metric(
                    "💰 Total Cost",
                    f"LKR {total_cost:,}",
                    help="Total entrance fees"
                )
            
            with col3:
                st.metric(
                    "⏱️ Total Visit Time",
                    f"{total_time:.1f} hours",
                    help="Time for visiting attractions (excluding travel)"
                )
            
            with col4:
                avg_stars = "⭐" * int(avg_popularity)
                st.metric(
                    "⭐ Average Rating",
                    f"{avg_popularity:.1f}/10",
                    delta=f"{avg_stars}",
                    help="Average popularity rating"
                )

        else:
            st.info("📍 Generate an itinerary first to see attraction details!")

    with tab2:
        # Map display
        display_map(st.session_state['route'])
    
    with tab3:
        # NEW: XAI Explanation Tab
        if 'explanation_data' in st.session_state and st.session_state['explanation_data']:
            explainer = XAIExplainer() 
            explanation_data = st.session_state['explanation_data']
            
            st.markdown("## 🤖 How the AI Made Your Recommendations")
            
            # Decision factors
            explainer.show_decision_factors(
                st.session_state['route'],
                explanation_data['filtered_data']
            )
            
            st.markdown("---")
            
            # Selection process explanation
            if 'selection_steps' in explanation_data:
                st.markdown("### 🎯 **Step-by-Step Selection Process**")
                
                for step in explanation_data['selection_steps']:
                    with st.expander(f"Step {step['step']}: Why we chose {step['selected_attraction']}"):
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown(f"""
                            **🏛️ Selected Attraction Details:**
                            - 💰 **Cost**: {step['cost']}
                            - ⏱️ **Visit Duration**: {step['visit_time']}
                            - ⭐ **Popularity**: {step['popularity']}
                            - 👥 **Crowded**: {step['crowded']}
                            - 🚗 **Travel Time**: {step['travel_time']}

                            """)
                        
                        with col2:
                            st.markdown(f"""
                            **📊 Trip Progress:**
                            - ⏱️ Total Time: {step['total_time_so_far']}
                            - 💰 Total Cost: {step['total_cost_so_far']}
                            - 🕒 Time Left: {step['time_remaining']}
                            - 💵 Budget Left: {step['budget_remaining']}
                            - 🎯 Options Available: {step['feasible_options']}  
                            """)
                        
                        if len(step['top_candidates']) > 1:
                            st.markdown("**Top Candidates Considered:**")
                            for i, candidate in enumerate(step['top_candidates'][:3]):
                                st.markdown(f"""
                                **{i+1}. {candidate['name']}** ({candidate['category']})
                                - Cost: {candidate['cost']} | Duration: {candidate['visit_time']} | Rating: {candidate['popularity']} | {candidate['crowded']} crowds
                                """)
        else:
            st.info("🤖 Generate an itinerary first to see AI explanations!")

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<!-- Feedback section at bottom -->
<div class="feedback-section" style="margin-top: 10px; text-align: center; padding: 20px; background-color: #696FC7; border-radius: 8px;">
    <h3 style="color: var(--text-primary); font-family: 'Poppins', sans-serif; font-weight: 600; margin-bottom: 1rem;">
        🌟 Love Your Experience?
    </h3>
    <p style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 1.1rem;">
        Help us improve by sharing your feedback
    </p>
    <a href="https://forms.gle/HRapWyJb8gyKf5zS6" 
       target="_blank" 
       class="btn btn-primary" 
       style="background-color: #4285f4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
        📝 Share Your Feedback
    </a>
    <p style="font-size: 12px; color: #eee; margin-top: 10px;">
        Takes less than 2 minutes • Help us serve you better
    </p>
</div>

<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🏝️ Discover Sri Lanka's Hidden Gems | Built with Streamlit</p>
</div>
            

""", unsafe_allow_html=True)