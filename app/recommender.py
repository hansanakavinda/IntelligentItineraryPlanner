from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def generate_recommendations(data, selected_categories):
    filtered = data[data['Category'].isin(selected_categories)].copy()  # Make a copy to avoid the warning
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(filtered['Description'])
    similarity = cosine_similarity(tfidf_matrix)
    filtered['score'] = similarity.sum(axis=1)
    return filtered.sort_values("score", ascending=False).head(10)
