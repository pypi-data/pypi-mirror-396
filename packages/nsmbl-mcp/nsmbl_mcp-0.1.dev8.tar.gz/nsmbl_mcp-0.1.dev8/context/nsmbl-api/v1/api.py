from fastapi import APIRouter
from app.api.v1.endpoints import endpoint_assets as assets, endpoint_strategies as strategies

api_router = APIRouter()

# Include the assets router under /assets prefix
api_router.include_router(
    assets.router, 
    prefix="/assets", 
    tags=["Assets"]
)

# Include the new agentic strategies router (replaces old strategies and backtests)
api_router.include_router(
    strategies.router,
    prefix="/strategies",
    tags=["Strategies"]
)
