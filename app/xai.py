import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

class XAIExplainer:
    def __init__(self):
        self.cluster_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    
    def explain_clustering(self, data, filtered_data, kmeans_model, selected_categories):
        """Explain how K-means clustering works for diversity"""
        st.markdown("### 🎯 **Clustering Explanation**: How We Ensure Diversity")
        
        # Show clustering logic
        st.markdown("""
        **Why Clustering?** We use advanced K-means clustering with multi-dimensional features to ensure your itinerary includes diverse attractions 
        rather than just similar ones clustered together.
        
        **Our Clustering Features:**
        - 🗺️ **Geographic Location**: Latitude & Longitude (normalized)
        - ⏱️ **Visit Duration**: Average time spent (normalized)
        - 💰 **Cost Tiers**: Free, Low-cost (<2000 LKR), High-cost (≥2000 LKR)
        - ⭐ **Popularity Score**: Attraction ratings (normalized)
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Cluster distribution
            cluster_counts = filtered_data['cluster'].value_counts().sort_index()
            fig_pie = px.pie(
                values=cluster_counts.values, 
                names=[f'Cluster {i}' for i in cluster_counts.index],
                title="Attraction Distribution Across Clusters",
                color_discrete_sequence=self.cluster_colors
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Show cluster characteristics
            st.markdown("**Cluster Characteristics:**")
            for cluster_id in sorted(filtered_data['cluster'].unique()):
                cluster_data = filtered_data[filtered_data['cluster'] == cluster_id]
                avg_lat = cluster_data['Latitude'].mean()
                avg_lon = cluster_data['Longitude'].mean()
                avg_time = cluster_data['AvgVisitTimeHrs'].mean()
                avg_cost = cluster_data['Cost'].mean()
                avg_popularity = cluster_data['Popularity'].mean()
                categories = cluster_data['Category'].unique()
                
                # Cost tier analysis
                free_count = len(cluster_data[cluster_data['Cost'] == 0])
                low_cost_count = len(cluster_data[(cluster_data['Cost'] > 0) & (cluster_data['Cost'] < 2000)])
                high_cost_count = len(cluster_data[cluster_data['Cost'] >= 2000])
                
                st.markdown(f"""
                **Cluster {cluster_id}** ({len(cluster_data)} attractions)
                - 📍 Geographic Center: {avg_lat:.3f}, {avg_lon:.3f}
                - ⏱️ Avg Visit Time: {avg_time:.1f}h
                - 💰 Avg Cost: LKR {avg_cost:.0f}
                - ⭐ Avg Popularity: {avg_popularity:.1f}
                - 🏷️ Categories: {', '.join(categories)}
                - 💸 Cost Distribution: Free({free_count}) | Low({low_cost_count}) | High({high_cost_count})
                """)
    
    def explain_elbow_method(self, explanation_data):
        """Explain how the optimal number of clusters was determined"""
        st.markdown("### 🎯 **Smart Clustering**: Why We Chose This Number of Clusters")
        
        st.markdown(f"""
        **Elbow Method Analysis:**
        
        Our AI automatically determined the optimal number of clusters (**{explanation_data.get('n_clusters', 'N/A')}**) using the elbow method:
        
        **How it works:**
        1. 📊 Tests different numbers of clusters (k=1 to k=8)
        2. 📉 Calculates WCSS (Within-Cluster Sum of Squares) for each k
        3. 📈 Finds the "elbow point" where adding more clusters provides diminishing returns
        4. 🎯 Selects the optimal k that balances diversity and coherence
        
        **Why this matters:**
        - **Too few clusters**: Attractions might be too similar
        - **Too many clusters**: Unnecessary complexity, scattered recommendations
        - **Just right**: Perfect balance of diversity and meaningful groupings
        """)
        
        # Add visual explanation if we have the data
        if 'kmeans_model' in explanation_data:
            st.info("💡 **Smart Algorithm**: The elbow method ensures your recommendations are diverse but not scattered randomly!")
    
    
    def explain_content_similarity(self, filtered_data, tfidf_matrix, selected_attraction_idx=None):
        """Explain content-based filtering using TF-IDF and cosine similarity"""
        st.markdown("### 📝 **Content Similarity Explanation**: Matching Your Interests")
        
        st.markdown("""
        **How it works:** We analyze attraction descriptions using TF-IDF (Term Frequency-Inverse Document Frequency) 
        to find attractions with similar content and themes.
        """)
        
        # Show TF-IDF top terms
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(filtered_data['Description'])
        feature_names = tfidf.get_feature_names_out()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Top TF-IDF terms across all descriptions
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            top_indices = mean_scores.argsort()[-15:][::-1]
            top_terms = [feature_names[i] for i in top_indices]
            top_scores = [mean_scores[i] for i in top_indices]
            
            fig_terms = px.bar(
                x=top_scores, 
                y=top_terms, 
                orientation='h',
                title="Most Important Terms in Selected Attractions",
                labels={'x': 'TF-IDF Score', 'y': 'Terms'}
            )
            fig_terms.update_layout(height=400)
            st.plotly_chart(fig_terms, use_container_width=True)
        
        with col2:
            # Content similarity heatmap
            if len(filtered_data) <= 10:  # Only for small datasets
                similarity_matrix = cosine_similarity(tfidf_matrix)
                
                fig_heatmap = px.imshow(
                    similarity_matrix,
                    x=filtered_data['Name'].tolist(),
                    y=filtered_data['Name'].tolist(),
                    title="Content Similarity Between Attractions",
                    color_continuous_scale="Blues"
                )
                fig_heatmap.update_layout(height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("📊 Similarity heatmap shown for datasets with ≤10 attractions")
    
    def explain_hybrid_scoring(self, filtered_data):
        """Explain how hybrid scoring combines different factors"""
        st.markdown("### ⚖️ **Hybrid Scoring Explanation**: How We Rank Attractions")
        
        st.markdown("""
        **Our Advanced Scoring System:**
        
        **Phase 1: Content & Diversity Scoring**
        - **Content Score (80%)**: TF-IDF similarity to your preferences
        - **Cluster Diversity Bonus (20%)**: Bonus for attractions in popular clusters
        
        **Phase 2: Multi-Factor Efficiency Scoring**
        - **Time Efficiency (40%)**: Score ÷ Total time needed
        - **Cost Efficiency (30%)**: Score ÷ Cost ratio
        - **Content Quality (20%)**: Base hybrid score
        - **Budget Optimization (10%)**: Score ÷ Budget utilization
        """)
        
        # Show score distribution
        if 'content_score' in filtered_data.columns and 'hybrid_score' in filtered_data.columns:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                fig_content = px.histogram(
                    filtered_data, 
                    x='content_score', 
                    title="Content Score Distribution",
                    nbins=20
                )
                st.plotly_chart(fig_content, use_container_width=True)
            
            with col2:
                fig_hybrid = px.histogram(
                    filtered_data, 
                    x='hybrid_score', 
                    title="Final Hybrid Score Distribution",
                    nbins=20
                )
                st.plotly_chart(fig_hybrid, use_container_width=True)
    
    def explain_route_optimization(self, route_data, distance_matrix=None):
        """Explain route optimization decisions"""
        st.markdown("### 🛣️ **Route Optimization Explanation**: Planning Your Journey")
        
        st.markdown("""
        **Advanced Optimization Strategy:**
        1. **Smart Starting Point**: Your current location (if available)
        2. **Multi-Objective Selection**: Using enhanced efficiency scoring
        3. **Top-K Candidate Evaluation**: Considers best 3 options at each step
        4. **Constraint Satisfaction**: Time limits and budget constraints
        5. **Dynamic Efficiency Metrics**:
           - Value-to-time ratio (40% weight)
           - Value-to-cost ratio (30% weight)
           - Content quality score (20% weight)  
           - Budget utilization efficiency (10% weight)
        """)
        
        if len(route_data) > 1:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Show route efficiency metrics
                if 'Cost' in route_data.columns:
                    total_cost = route_data['Cost'].sum()
                    avg_cost = route_data['Cost'].mean()
                    
                    st.markdown(f"""
                    **Route Metrics:**
                    - 🏛️ Total Attractions: {len(route_data)}
                    - 💰 Total Cost: LKR {total_cost:,.0f}
                    - 💱 Average Cost per Stop: LKR {avg_cost:,.0f}
                    """)
                    
                    if 'AvgVisitTimeHrs' in route_data.columns:
                        total_time = route_data['AvgVisitTimeHrs'].sum()
                        st.markdown(f"- ⏱️ Total Visit Time: {total_time:.1f} hours")
            
            with col2:
                # Cost per attraction
                if 'Cost' in route_data.columns:
                    fig_cost = px.bar(
                        route_data, 
                        x=range(len(route_data)), 
                        y='Cost',
                        title="Cost per Stop in Your Route",
                        labels={'x': 'Stop Number', 'y': 'Cost (LKR)'}
                    )
                    st.plotly_chart(fig_cost, use_container_width=True)
    
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
            st.info("📊 Decision factor analysis requires multiple attraction options to compare.")

    def create_feature_importance_chart(self, route_data):
        """Show which features were most important in selection"""
        st.markdown("### 📊 **Feature Importance**: What Influenced Your Recommendations")
        
        st.markdown("""
        **Advanced Feature Analysis**: Our AI considers multiple factors when selecting attractions:
        
        **Primary Selection Factors:**
        - 🎯 **Content Similarity**: How well attractions match your interests
        - 🕐 **Time Efficiency**: Attraction value relative to time investment
        - 💰 **Cost Efficiency**: Value relative to cost
        - 📍 **Geographic Diversity**: Ensuring variety in locations
        - ⭐ **Quality Scores**: Overall attraction ratings
        """)
        
        # Calculate feature correlations with selection
        features_to_analyze = ['AvgVisitTimeHrs', 'Cost', 'Popularity']
        feature_importance = {}
        
        for feature in features_to_analyze:
            if feature in route_data.columns:
                # Normalize the feature values
                values = route_data[feature].values
                if len(values) > 1:
                    normalized_values = (values - values.min()) / (values.max() - values.min() + 1e-8)
                    importance = np.mean(normalized_values)
                    feature_importance[feature] = importance
        
        if feature_importance:
            fig_importance = px.bar(
                x=list(feature_importance.keys()),
                y=list(feature_importance.values()),
                title="Feature Influence on Your Route Selection",
                labels={'x': 'Features', 'y': 'Normalized Importance Score'}
            )
            st.plotly_chart(fig_importance, use_container_width=True)
            
            # Explain what this means
            st.markdown("""
            **Interpretation Guide:**
            - **Higher bars** indicate features that had more influence on selecting these attractions
            - **Time Investment**: How much time each attraction requires
            - **Cost Impact**: How cost influenced the selection process
            - **Popularity Factor**: How attraction ratings affected choices
            
            This helps you understand what the AI prioritized for your specific preferences and constraints.
            """)