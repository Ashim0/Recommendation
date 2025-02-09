import logging
import pandas as pd
from recommendation.repo.db import Database

logger = logging.getLogger(__name__)

class UserRepo:
    def __init__(self):
        self.db = Database()
        self.interactions_collection = self.db.get_collection("interactions")
        self.item_collection = self.db.get_collection("products")
        self.user_item_matrix = None

    def get_user(self, user_id):
        """ Placeholder for user fetching logic """
        pass

    def fetch_user_product_matrix(self):
        # Fetch interactions from the database
        interactions = list(
            self.interactions_collection.find({}, {"_id": 0, "userId": 1, "productId": 1, "clickCount": 1})
        )

        if not interactions:
            logger.warning("No interactions found in the database.")
            return None

        # Convert to DataFrame for analysis
        interactions_df = pd.DataFrame(interactions)

        if interactions_df.empty:
            logger.warning("Interaction DataFrame is empty.")
            return None

        # Create user-item interaction matrix
        user_item_matrix = interactions_df.pivot_table(
            index='userId', columns='productId', values='clickCount', fill_value=0
        )
        
        
        logger.debug(f"Generated user-item matrix with shape {user_item_matrix.shape}")

        return user_item_matrix

    def fetch_products(self):
        products = list(self.item_collection.find({"isActive": True}))
        logging.debug(f"Fetched {len(products)} products.")
        return products
