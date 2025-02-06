import logging

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recommendation.repo.user_repo import UserRepo


class SimilarityService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def get_similar_items(self, product_id, top_n=5):
        try:
            products = self.user_repo.fetch_products()
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
