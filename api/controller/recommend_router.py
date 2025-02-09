from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from bson import ObjectId
from recommendation.repo.user_repo import UserRepo
from recommendation.service.recommendation_service import RecommendationService

router = APIRouter()

@router.get("/recommend")
async def get_recommendations(
    user_id: str = Query(..., alias="user_id"),  # Correcting the query param name here
    top_k: int = Query(10, alias="top_k")       # Default to 10 if top_k is not provided
):
    # Validate `user_id`
    try:
        user_oid = ObjectId(user_id)  # Convert to ObjectId
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    # Initialize repositories
    user_repo = UserRepo()
    recommendation_service = RecommendationService(user_repo=user_repo)

    # Fetch recommended product ObjectIds
    recommended_product_oids = recommendation_service.get_recommendations(user_oid, top_k)

    if not recommended_product_oids:
        return JSONResponse(content={"user_id": str(user_oid), "recommendations": []})

    # Convert product IDs to ObjectId before querying MongoDB
    products_col = user_repo.item_collection
    recommended_products = list(products_col.find(
        {"_id": {"$in": [ObjectId(pid) for pid in recommended_product_oids]}},
        {"_id": 1, "name": 1, "price": 1, "images": 1}
    ))

    # Serialize MongoDB documents
    recommended_products = [serialize_mongo_doc(product) for product in recommended_products]

    return {"user_id": str(user_oid), "recommendations": recommended_products}

def serialize_mongo_doc(doc):
    """ Convert MongoDB document to JSON-serializable format """
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc
