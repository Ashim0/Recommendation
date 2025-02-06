from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from recommendation.endpoint.recomendation_manager import RecommendationManager

router = APIRouter()
manager = RecommendationManager()


def serialize_mongo_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/similar", tags=["Recommendation"])
async def get_similar_products(item_id: str = Query(..., description="Item Id"),
                               top_k: int = Query(10, description="Tok K similar products to fetch")):
    if not item_id:
        raise HTTPException(status_code=400, detail="ItemId is required")
    try:
        recommended_product_ids = manager.get_similarity_service().get_similar_items(item_id, top_k)

        return JSONResponse(content={"item_item": item_id, "recommendations": recommended_product_ids})

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
