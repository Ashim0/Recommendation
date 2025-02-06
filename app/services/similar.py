import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.db import Database
from bson import ObjectId
import logging

logging.basicConfig(level=logging.DEBUG)
# Fetch products
def fetch_products():
    try:
        collection = Database.get_collection("products")
        products = list(collection.find({"isActive": True}))
        logging.debug(f"Fetched {len(products)} products.")
        return products
    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        raise


def similar_products(product_id, top_n=5):
    try:
        products = fetch_products()
        if not products:
            raise ValueError("No products found.")
        
        df = pd.DataFrame(products)
        logging.debug(f"Fetched {len(df)} products for recommendations.")

       
        df["_id"] = df["_id"].astype(str)
        
        if product_id not in df["_id"].values:
            raise ValueError(f"Product with ID {product_id} not found.")
        
        
        df["combined_features"] = df.apply(
            lambda x: f"{x['name']} {x['description']} {' '.join(map(str, x['category']))}", axis=1
        )

        
        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(df["combined_features"])

        
        input_idx = df[df["_id"] == product_id].index[0]
        cosine_sim = cosine_similarity(tfidf_matrix[input_idx], tfidf_matrix).flatten()

        
        similar_indices = cosine_sim.argsort()[-(top_n + 1):][::-1][1:]
        recommendations = df.iloc[similar_indices]

        return recommendations[["_id", "name", "description", "price", "images"]].to_dict(orient="records")

    except Exception as e:
        logging.error(f"Error occurred in recommend_products: {str(e)}")
        raise 
