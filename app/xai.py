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
        **Why Clustering?** We use K-means clustering to ensure your itinerary includes diverse attractions 
        rather than just similar ones clustered together geographically.
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
                categories = cluster_data['Category'].unique()
                
                st.markdown(f"""
                **Cluster {cluster_id}** ({len(cluster_data)} attractions)
                - 📍 Center: {avg_lat:.3f}, {avg_lon:.3f}
                - ⏱️ Avg Visit Time: {avg_time:.1f}h
                - 🏷️ Categories: {', '.join(categories)}
                """)
    
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
        **Our Scoring Formula:**
        - **Content Score (80%)**: Based on description similarity
        - **Cluster Diversity Bonus (20%)**: Bonus for attractions in popular clusters
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
        **Optimization Strategy:**
        1. **Starting Point**: Your current location (if available)
        2. **Distance Minimization**: Using Traveling Salesman Problem (TSP) optimization
        3. **Time Constraints**: Considering travel time and visit duration
        4. **Budget Constraints**: Staying within your specified budget
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
            # Compare selected vs not selected
            selected_names = selected_route['Name'].tolist()
            selected_data = all_filtered_data[all_filtered_data['Name'].isin(selected_names)]
            not_selected_data = all_filtered_data[~all_filtered_data['Name'].isin(selected_names)]
            
            comparison_metrics = []
            
            for metric in ['AvgVisitTimeHrs', 'Cost', 'Popularity']:
                if metric in selected_data.columns:
                    selected_avg = selected_data[metric].mean()
                    not_selected_avg = not_selected_data[metric].mean()
                    
                    comparison_metrics.append({
                        'Metric': metric,
                        'Selected Attractions': selected_avg,
                        'Not Selected': not_selected_avg,
                        'Difference': selected_avg - not_selected_avg
                    })
            
            if comparison_metrics:
                df_comparison = pd.DataFrame(comparison_metrics)
                
                fig_comparison = px.bar(
                    df_comparison.melt(id_vars=['Metric'], 
                                     value_vars=['Selected Attractions', 'Not Selected']),
                    x='Metric', 
                    y='value', 
                    color='variable',
                    barmode='group',
                    title="Selected vs Non-Selected Attractions Comparison"
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
    
    def create_feature_importance_chart(self, route_data):
        """Show which features were most important in selection"""
        st.markdown("### 📊 **Feature Importance**: What Influenced Your Recommendations")
        
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
            **What this means:**
            - Higher bars indicate features that had more influence on selecting these attractions
            - This helps you understand what the AI prioritized for your specific preferences
            """)