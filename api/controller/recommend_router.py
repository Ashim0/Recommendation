from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from recommendation.endpoint.recomendation_manager import RecommendationManager
from recommendation.repo.db import Database

router = APIRouter()

manager = RecommendationManager()


def serialize_mongo_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/recommend", tags=["Recommendation"])
async def get_recommendation(user_id: str = Query(..., description="User Id"),
                             top_k: int = Query(10, description="Number of recommendations to fetch")):
    if not user_id:
        raise HTTPException(status_code=400, detail="UserId is required")
    try:
        # Get recommended product IDs
        recommended_product_ids = manager.get_recommendation_service().get_recommendations(user_id, top_k)

        if not recommended_product_ids:
            return JSONResponse(content={"userId": user_id, "recommendations": []})

        # Fetch recommended product details from the database
        products_col = Database.get_collection("products")

        recommended_products = list(products_col.find(
            {"_id": {"$in": recommended_product_ids}},
            {"_id": 1, "name": 1, "price": 1, "images": 1}
        ))

        # Serialize MongoDB documents
        recommended_products = [serialize_mongo_doc(product) for product in recommended_products]

        return JSONResponse(content={"userId": user_id, "recommendations": recommended_products})

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
