"""
-- Created by: Ashok Kumar Pant
-- Email: asokpant@gmail.com
-- Created on: 06/02/2025
"""
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
        pass

    def fetch_user_product_matrix(self):
        interactions = list(
            self.interactions_collection.find({}, {"_id": 0, "userId": 1, "productId": 1, "clickCount": 1}))

        if not interactions:
            logger.warning("No interactions found in the database.")
            return None, None

        return pd.DataFrame(interactions)

    def fetch_products(self):
        products = list(self.item_collection.find({"isActive": True}))
        logging.debug(f"Fetched {len(products)} products.")
        return products
