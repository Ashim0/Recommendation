import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from recommendation.repo.user_repo import UserRepo

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class RecommendationService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def get_recommendations(self, userId: str, top_k: int = 10):
        # Fetch the user-item interaction matrix
        user_item_matrix = self.user_repo.fetch_user_product_matrix()

        if user_item_matrix is None or user_item_matrix.empty:
            logging.warning("User-product matrix is empty or not found.")
            return []

        # Print the matrix for debugging purposes
        print("User-Item Interaction Matrix:")
        print(user_item_matrix)

        if userId not in user_item_matrix.index:
            logging.warning(f"User {userId} not found in the interaction matrix.")
            return []

        user_row = user_item_matrix.loc[userId].values.reshape(1, -1)

        # Compute similarity between the user and all other users
        similarity_matrix = cosine_similarity(user_item_matrix, user_row)
        similarity_df = pd.DataFrame(similarity_matrix, index=user_item_matrix.index, columns=['similarity'])

        # Get top 5 similar users (excluding the current user)
        similar_users = similarity_df.sort_values(by='similarity', ascending=False).index[1:6]
        logging.info(f"Top 5 similar users to {userId}: {similar_users.tolist()}")

        recommended_products = []
        for similar_user in similar_users:
            similar_user_items = user_item_matrix.loc[similar_user][user_item_matrix.loc[similar_user] > 0].index.tolist()
            recommended_products.extend(similar_user_items)

        # Rank recommendations by frequency (most common first)
        ranked_recommendations = [product for product, _ in Counter(recommended_products).most_common()]

        # Remove products the user has already interacted with
        user_clicked_products = set(user_item_matrix.loc[userId][user_item_matrix.loc[userId] > 0].index.tolist())
        final_recommendations = list(set(ranked_recommendations) - user_clicked_products)

        logging.info(f"Final recommendations for User {userId}: {final_recommendations[:top_k]}")

        # Ensure recommendations do not exceed top_k and return the final list
        return final_recommendations[:top_k]

    def plot_user_product_matrix(self):
        """Visualizes the user-product interaction matrix."""
        user_product_matrix = self.user_repo.fetch_user_product_matrix()

        if user_product_matrix is None or user_product_matrix.empty:
            print("No interactions found.")
            return

        print("User-Product Matrix:")
        print(tabulate(user_product_matrix, headers='keys', tablefmt='psql'))

        # Create the heatmap to visualize interactions
        plt.figure(figsize=(12, 6))
        sns.heatmap(user_product_matrix, cmap="YlGnBu")
        plt.title("User-Product Interaction Matrix")
        plt.xlabel("Products")
        plt.ylabel("Users")
        plt.show()
