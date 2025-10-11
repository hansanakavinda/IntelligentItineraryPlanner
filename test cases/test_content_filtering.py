import sys
import os
import pandas as pd

# Change to project root directory
project_root = os.path.join(os.path.dirname(__file__), '..')
os.chdir(project_root)

# Add the app directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from data_loader import load_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Test Case 3: Content-Based Filtering
print("Test Case 3: Content-Based Filtering")
print("-" * 60)

# Load data
print("Loading attractions data...")
data = load_data()
print(f"Dataset loaded: {len(data)} attractions")

# User selects category
selected_category = "Water Activity"
print(f"User Selected Category: {selected_category}")

# Step 1: Filter by selected category
filtered_attractions = data[data['Category'] == selected_category]
print(f"filtered attractions found: {len(filtered_attractions)}")

print("Filtered attractions:")
for i, attraction in filtered_attractions.iterrows():
    print(f"  - {attraction['Name']}: {attraction['Description'][:50]}...")

# Step 2: Create user preference from Water Activity descriptions
Filtered_descriptions = filtered_attractions['Description'].tolist()
user_preference = " ".join(Filtered_descriptions)

print(f"\nUser preference created from {len(Filtered_descriptions)} descriptions")

# Step 3: Test against ALL attractions
print(f"\nTesting TF-IDF + Cosine Similarity...")

# Get all descriptions
all_descriptions = data['Description'].tolist()
documents = [user_preference] + all_descriptions

# Create TF-IDF matrix
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(documents)

# Calculate similarity
user_description_vector = tfidf_matrix[0:1]
all_descriptions_vector = tfidf_matrix[1:]
similarity_scores = cosine_similarity(user_description_vector, all_descriptions_vector)[0]

# Add scores to data and get top 5 recommendations
results = data.copy()
results['similarity_score'] = similarity_scores
top_recommendations = results.nlargest(5, 'similarity_score')

print(f"✅ Similarity calculated successfully")
print(f"\nTop 5 Content-Based Recommendations:")
print("-" * 60)

user_preference_matches = 0
for i, (idx, rec) in enumerate(top_recommendations.iterrows(), 1):
    category = rec['Category']
    score = rec['similarity_score']
    
    print(f"{i}. {rec['Name']} ({category})")
    print(f"   Similarity: {score:.4f} | Cost: LKR {rec['Cost']:,}")
    print(f"   Description: {rec['Description'][:60]}...")
    
    if category == selected_category:
        user_preference_matches += 1
    print()

# Final check
print("-" * 60)
print(f"matching attractions in top 5: {user_preference_matches}")
print(f"Success rate: {user_preference_matches}/5 = {user_preference_matches/5*100:.1f}%")

if user_preference_matches >= 1:
    print("✅ RESULT: PASS - Content-based filtering found matching attractions")
else:
    print("❌ RESULT: FAIL - No matching attractions in top recommendations")

print("\nTest completed!")