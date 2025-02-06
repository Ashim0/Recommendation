from flask import Flask, jsonify, request
import logging
import traceback
from app.services.recommendation import get_recommendations
from app.db import Database

app = Flask(__name__)

def serialize_mongo_doc(doc):
    doc["_id"] = str(doc["_id"])  
    return doc

@app.route("/recommend", methods=["GET"])
def recommend():
    user_id = request.args.get("userId")

    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    try:
        # Get recommended product IDs
        recommended_product_ids = get_recommendations(user_id)

        # print(f"Recommendations for user {user_id}: {recommended_product_ids}")

        if not recommended_product_ids:
            return jsonify({"userId": user_id, "recommendations": []})  # No recommendations

        # Fetch recommended product details from the database
        products_col = Database.get_collection("products")
       
        recommended_products = list(products_col.find(
            {"_id": {"$in": recommended_product_ids}},  # Keep IDs as strings
            {"_id": 1, "name": 1, "price": 1,"images": 1}
        ))
        print(f"Recommendation_product: {recommended_products} ")
        # Serialize MongoDB documents
        recommended_products = [serialize_mongo_doc(product) for product in recommended_products]

        return jsonify({"userId": user_id, "recommendations": recommended_products})

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        print("".join(traceback.format_exception(None, e, e.__traceback__)))
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
