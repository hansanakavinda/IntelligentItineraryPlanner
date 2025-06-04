from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def generate_recommendations(data, selected_categories):
    filtered = data[data['Category'].isin(selected_categories)].copy()  # Make a copy to avoid the warning
    tfidf = TfidfVectorizer(stop_words='english') #create TF-IDF vectorizer that ignores common words like "the", "and", "is"
    tfidf_matrix = tfidf.fit_transform(filtered['Description']) #transform the Description column into a TF-IDF matrix
    similarity = cosine_similarity(tfidf_matrix) #calculate the cosine similarity between the TF-IDF matrices
    filtered['score'] = similarity.sum(axis=1) #sum the similarity scores for each row
    return filtered.sort_values("score", ascending=False).head(10) #sort the rows by the score in descending order and return the top 10 rows
