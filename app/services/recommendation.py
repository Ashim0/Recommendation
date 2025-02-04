import pandas as pd
import numpy as np
import logging
import threading
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo.change_stream import ChangeStream
from sklearn.metrics.pairwise import cosine_similarity
from app.db import Database

# Global variables for caching
user_product_matrix = None
df = None
lock = threading.Lock()  # Ensures thread safety

# Connect to database
db = Database.get_connection()
interactions_col = Database.get_collection("interactions")

def fetch_user_product_matrix():
    """Fetches interactions from DB and creates the user-product matrix."""
    global user_product_matrix, df

    interactions = list(interactions_col.find({}, {"_id": 0, "userId": 1, "productId": 1, "clickCount": 1}))

    if not interactions:
        logging.warning("No interactions found in the database.")
        return None, None

    df = pd.DataFrame(interactions)

    if df.empty:
        logging.warning("No valid user-product interactions found.")
        return None, None

    with lock:  # Thread-safe update
        user_product_matrix = df.pivot_table(index="userId", columns="productId", values="clickCount", fill_value=0)

    logging.info("User-product matrix updated.")
    return user_product_matrix, df


def listen_for_db_updates():
    """Listens for new interactions and updates the matrix automatically."""
    global user_product_matrix, df

    try:
        with interactions_col.watch([{"$match": {"operationType": "insert"}}]) as stream:
            for change in stream:
                new_doc = change["fullDocument"]
                logging.info(f"New interaction detected: {new_doc}")

                with lock:  # Ensure thread safety
                    # Add new interaction to df
                    new_entry = pd.DataFrame([{
                        "userId": new_doc["userId"],
                        "productId": new_doc["productId"],
                        "clickCount": new_doc["clickCount"]
                    }])

                    df = pd.concat([df, new_entry], ignore_index=True)

                    # Rebuild the user-product matrix
                    user_product_matrix = df.pivot_table(index="userId", columns="productId", values="clickCount", fill_value=0)
                
                logging.info("User-product matrix updated after new interaction.")

    except Exception as e:
        logging.error(f"Error listening to DB updates: {e}")


# Start the background thread to listen for DB updates
listener_thread = threading.Thread(target=listen_for_db_updates, daemon=True)
listener_thread.start()


from bson import ObjectId

def get_recommendations(userId):
    global user_product_matrix, df

    # Convert userId to ObjectId if needed
    try:
        userId = ObjectId(userId)
    except:
        pass  # Assume it's already in correct format

    if user_product_matrix is None:
        logging.warning("User-product matrix not initialized. Fetching from DB...")
        user_product_matrix, df = fetch_user_product_matrix()

    if user_product_matrix is None:
        logging.warning("User-product matrix could not be created.")
        return []

    # Check if user exists in the matrix
    if userId not in user_product_matrix.index:
        logging.warning(f"User {userId} not found in the interaction matrix.")
        return []

    # Compute similarity between users
    similarity_matrix = cosine_similarity(user_product_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_product_matrix.index, columns=user_product_matrix.index)

    similar_users = similarity_df[userId].sort_values(ascending=False).index[1:6]

    recommended_products = []
    for similar_user in similar_users:
        user_clicks = df[df["userId"] == similar_user]["productId"].tolist()
        recommended_products.extend(user_clicks)

    recommended_products = pd.Series(recommended_products).value_counts().index.tolist()

    # Remove products the user has already clicked
    user_clicked_products = df[df["userId"] == userId]["productId"].tolist()
    final_recommendations = [p for p in recommended_products if p not in user_clicked_products]

    logging.info(f"Final recommendations for User {userId}: {final_recommendations}")

    return final_recommendations
