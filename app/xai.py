import streamlit as st

class XAIExplainer:
    """Simplified XAI focused on user-friendly explanations for tourists"""
    def __init__(self):
        pass
    
    def show_decision_factors(self, selected_route, all_filtered_data):
        """Show why specific attractions were selected vs others"""
        st.markdown("### 🤔 **Decision Factors**: Why These Attractions?")
        
        if len(selected_route) > 0 and len(all_filtered_data) > len(selected_route):
            selected_names = selected_route['Name'].tolist()
            selected_data = all_filtered_data[all_filtered_data['Name'].isin(selected_names)]
            not_selected_data = all_filtered_data[~all_filtered_data['Name'].isin(selected_names)]
            
            st.markdown("**🎯 Selection Analysis:** Here's how your chosen attractions compare to alternatives:")
            
            col1, col2, col3 = st.columns(3)
            
            # Time comparison
            if 'AvgVisitTimeHrs' in selected_data.columns:
                with col1:
                    selected_time = selected_data['AvgVisitTimeHrs'].mean()
                    rejected_time = not_selected_data['AvgVisitTimeHrs'].mean()
                    time_diff = selected_time - rejected_time
                    
                    st.metric(
                        "⏱️ Visit Duration",
                        f"{selected_time:.1f} hours",
                        f"{time_diff:+.1f}h vs alternatives",
                        delta_color="normal"
                    )
            
            # Cost comparison  
            if 'Cost' in selected_data.columns:
                with col2:
                    selected_cost = selected_data['Cost'].mean()
                    rejected_cost = not_selected_data['Cost'].mean()
                    cost_diff = selected_cost - rejected_cost
                    
                    st.metric(
                        "💰 Average Cost",
                        f"LKR {selected_cost:,.0f}",
                        f"LKR {cost_diff:+,.0f} vs alternatives",
                        delta_color="inverse"  # Lower cost is better
                    )
            
            # Popularity comparison
            if 'Popularity' in selected_data.columns:
                with col3:
                    selected_pop = selected_data['Popularity'].mean()
                    rejected_pop = not_selected_data['Popularity'].mean()
                    pop_diff = selected_pop - rejected_pop
                    
                    st.metric(
                        "⭐ Popularity Rating", 
                        f"{selected_pop:.1f}/10",
                        f"{pop_diff:+.1f} vs alternatives",
                        delta_color="normal"
                    )
            
            # Summary interpretation
            st.markdown("""
            ---
            **🧠 AI Decision Summary:**
            
            The algorithm selected attractions based on your specific constraints and preferences. The metrics above show how 
            your final itinerary compares to the attractions that didn't make the cut.
            
            **What this means:**
            - **Positive time difference**: AI prioritized substantial experiences over quick stops
            - **Negative cost difference**: AI optimized for budget efficiency  
            - **Positive popularity difference**: AI chose higher-rated attractions
            """)
        
        else:
            st.info("📊 Decision factor analysis requires multiple alternative attraction options to compare.")