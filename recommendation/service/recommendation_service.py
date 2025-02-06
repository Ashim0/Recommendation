import logging

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from recommendation.repo.user_repo import UserRepo


class RecommendationService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def get_recommendations(self, user_id: str, top_k: int = 10):
        user_item_matrix = self.user_repo.fetch_user_product_matrix()

        if user_item_matrix is None:
            logging.warning("User-product matrix could not be created.")
            return []

        if user_id not in user_item_matrix.index:
            logging.warning(f"User {user_id} not found in the interaction matrix.")
            return []

        user_row = user_item_matrix.loc[user_id]

        similarity_matrix = cosine_similarity(user_item_matrix, [user_row])
        similarity_df = pd.DataFrame(similarity_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)

        similar_users = similarity_df[user_id].sort_values(ascending=False).index[1:6]

        recommended_products = []
        for similar_user in similar_users:
            similar_user_items = user_item_matrix.loc[similar_user][
                user_item_matrix.loc[similar_user] > 0].index.tolist()
            recommended_products.extend(similar_user_items)

        recommended_products = pd.Series(recommended_products).value_counts().index.tolist()

        user_clicked_products = user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index.tolist()
        final_recommendations = [p for p in recommended_products if p not in user_clicked_products]

        logging.info(f"Final recommendations for User {user_id}: {final_recommendations}")

        return final_recommendations

    def plot_user_product_matrix(self):
        """Visualizes the user-product interaction matrix."""
        user_product_matrix, _ = self.user_repo.fetch_user_product_matrix()
        print("User-Product Matrix:")
        print(tabulate(user_product_matrix, headers='keys', tablefmt='psql'))

        if user_product_matrix is None:
            print("No interactions found.")
            return

        plt.figure(figsize=(12, 6))
        sns.heatmap(user_product_matrix, cmap="coolwarm", linewidths=0.5)
        plt.xlabel("Products")
        plt.ylabel("Users")
        plt.title("User-Product Interaction Matrix")
        plt.show()

    def show_user_interactions(self):
        """Print all user interactions in a tabulated format."""
        _, df = self.user_repo.fetch_user_product_matrix()
        if df is None:
            print("No interactions found.")
            return
        print("\nUser Interactions:")
        print(tabulate(df, headers='keys', tablefmt='psql'))

    def evaluate_recommendations(self):
        """Evaluate recommendations using accuracy score."""
        user_product_matrix, df = self.user_repo.fetch_user_product_matrix()

        if user_product_matrix is None:
            print("No interactions found.")
            return

        actual = []
        predicted = []
        results = []

        for user_id in user_product_matrix.index:
            actual_products = df[df["userId"] == user_id]["productId"].tolist()
            recommended_products = self.get_recommendations(user_id)

            actual.append(set(actual_products))
            predicted.append(set(recommended_products))

            results.append([user_id, actual_products, recommended_products])

        print("\nUser-wise Recommendations:")
        print(tabulate(results, headers=["User ID", "Actual Products", "Recommended Products"], tablefmt='psql'))

        accuracy = sum(len(act & pred) / max(len(act), 1) for act, pred in zip(actual, predicted)) / len(actual)

        print(f"\nRecommendation Accuracy: {accuracy:.6f}")

