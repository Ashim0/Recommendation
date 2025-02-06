from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.controller import recommend_router, similar_router


def create_app():
    app = FastAPI(
        title="Recommendation API",
        description="API for product recommendations",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API route
    app.include_router(recommend_router.router, prefix="/api")
    app.include_router(similar_router.router, prefix="/api")

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="debug")
