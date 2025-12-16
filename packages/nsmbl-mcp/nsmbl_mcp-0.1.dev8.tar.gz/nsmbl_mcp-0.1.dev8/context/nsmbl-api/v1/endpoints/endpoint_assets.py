"""
Assets endpoint for financial asset metadata and search.

Provides access to stocks, ETFs, mutual funds, and cryptocurrencies with 
rich metadata served from local database for fast, reliable access.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.core.middleware import get_current_user
from app.db.assets import get_asset_by_id, get_asset_by_symbol, list_assets
from app.services.internal.assets import search_hybrid
from app.api.v1.schemas.assets.schema_asset import (
    AssetResponse,
    PaginatedAssetResponse,
    AssetSearchResponse
)
from app.errors import handle_not_found_error
from app.core.logging import get_domain_logger

logger = get_domain_logger('api', __name__)

router = APIRouter()


@router.get(
    "/search",
    operation_id="searchAssets",
    summary="Natural Language Asset Search",
    description="""
Search for assets using natural language queries.

Supports complex queries like:
- "technology stocks with market cap over $10 billion"
- "S&P 500 ETFs with low expense ratios"
- "top cryptocurrencies by market cap"

Uses hybrid search combining full-text search and LLM-powered query understanding
for intelligent, context-aware results.
    """,
    response_description="List of matching assets",
    response_model=AssetSearchResponse,
    responses={
        200: {
            "description": "Search results",
            "content": {
                "application/json": {
                    "example": {
                        "assets": [
                            {
                                "id": "as-12345678-1234-5678-9abc-123456789012",
                                "symbol": "AAPL",
                                "name": "Apple Inc",
                                "instrument": "stock",
                                "exchange": "US",
                                "currency": "USD",
                                "delisted": False,
                                "updated_at": "2024-12-09T00:00:00Z",
                                "data": {
                                    "sector": "Technology",
                                    "market_cap": 3000000000000
                                }
                            }
                        ],
                        "query": "technology stocks over $1B",
                        "returned": 1
                    }
                }
            }
        }
    }
)
async def search_assets_endpoint(
    q: str = Query(
        ...,
        description="Natural language search query",
        example="technology stocks with market cap over $10 billion"
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    ),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search assets using natural language queries.
    
    Combines PostgreSQL full-text search with LLM-powered query understanding
    to deliver intelligent, context-aware results.
    """
    
    user_id, _ = current_user
    logger.info(f"Searching assets for user {user_id}: '{q}'")
    
    try:
        # Use hybrid search
        assets = search_hybrid(db, q, limit)
        
        logger.info(f"Search returned {len(assets)} results")
        
        return {
            "assets": assets,
            "query": q,
            "returned": len(assets)
        }
        
    except Exception as e:
        logger.error(f"Error searching assets: {str(e)}")
        raise


@router.get(
    "",
    operation_id="listAssets",
    summary="List Financial Assets",
    description="""
Retrieve a paginated list of financial assets with filtering capabilities.

Assets include stocks, ETFs, mutual funds, and cryptocurrencies with rich metadata
including sector classification, market capitalization, holdings data, and more.

Use filters to narrow results by instrument type, exchange, sector, or market cap.
All data served from local database for fast, reliable access.
    """,
    response_description="Paginated list of assets with metadata",
    response_model=PaginatedAssetResponse,
    responses={
        200: {
            "description": "Successfully retrieved assets",
            "content": {
                "application/json": {
                    "example": {
                        "assets": [
                            {
                                "id": "as-12345678-1234-5678-9abc-123456789012",
                                "symbol": "AAPL",
                                "name": "Apple Inc",
                                "instrument": "stock",
                                "exchange": "US",
                                "currency": "USD",
                                "delisted": False,
                                "updated_at": "2024-12-09T00:00:00Z",
                                "data": {
                                    "sector": "Technology",
                                    "market_cap": 3000000000000
                                }
                            }
                        ],
                        "total": 15000,
                        "limit": 50,
                        "offset": 0,
                        "returned": 50
                    }
                }
            }
        },
        422: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "validation_error",
                            "message": "Invalid instrument type. Must be one of: stock, etf, fund, crypto"
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "internal_error",
                            "message": "An unexpected error occurred"
                        }
                    }
                }
            }
        }
    }
)
async def list_assets_endpoint(
    instrument: Optional[str] = Query(
        default=None,
        description="Filter by asset type. Options: 'stock', 'etf', 'fund', 'crypto'",
        example="stock"
    ),
    exchange: Optional[str] = Query(
        default=None,
        description="Filter by exchange code. Examples: 'US' (US markets), 'CC' (cryptocurrencies)",
        example="US"
    ),
    sector: Optional[str] = Query(
        default=None,
        description="Filter stocks by sector. Examples: 'Technology', 'Healthcare', 'Financials'",
        example="Technology"
    ),
    min_market_cap: Optional[int] = Query(
        default=None,
        description="Minimum market capitalization in USD. Example: 1000000000 for $1B+",
        example=1000000000
    ),
    delisted: bool = Query(
        default=False,
        description="Include delisted/inactive assets"
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of assets to return per page"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Starting position in result set (for pagination)"
    ),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all tradeable assets with pagination and filtering.
    
    Returns paginated, alphabetically sorted array of assets with metadata for use in 
    investment analysis and strategy construction. All data served from local database
    with no external API calls required.
    """
    
    user_id, _ = current_user
    logger.info(f"Listing assets for user {user_id}, filters: instrument={instrument}, exchange={exchange}, sector={sector}, limit={limit}, offset={offset}")
    
    try:
        # Query assets from database
        result = list_assets(
            db=db,
            instrument=instrument,
            exchange=exchange,
            sector=sector,
            min_market_cap=min_market_cap,
            delisted=delisted,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Returning {result['returned']} assets (total: {result['total']})")
        return result
        
    except Exception as e:
        logger.error(f"Error listing assets: {str(e)}")
        raise


@router.get(
    "/{identifier}",
    operation_id="getAsset",
    summary="Get Asset Details",
    description="""
Retrieve detailed information for a specific asset by ID or symbol.

Supports lookup by:
- Asset ID (e.g., 'as-12345678-1234-5678-9abc-123456789012')
- Symbol (e.g., 'AAPL', 'BTC-USD', 'SPY')

Returns comprehensive metadata including fundamentals, holdings, and technical indicators
depending on the instrument type.
    """,
    response_description="Asset details with instrument-specific metadata",
    response_model=AssetResponse,
    responses={
        200: {
            "description": "Asset retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "as-12345678-1234-5678-9abc-123456789012",
                        "symbol": "AAPL",
                        "name": "Apple Inc",
                        "instrument": "stock",
                        "exchange": "US",
                        "currency": "USD",
                        "delisted": False,
                        "updated_at": "2024-12-09T00:00:00Z",
                        "data": {
                            "sector": "Technology",
                            "industry": "Consumer Electronics",
                            "market_cap": 3000000000000,
                            "beta": 1.29
                        }
                    }
                }
            }
        },
        404: {
            "description": "Asset not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "not_found",
                            "message": "Asset not found: INVALID"
                        }
                    }
                }
            }
        }
    }
)
async def get_asset_endpoint(
    identifier: str = Path(
        ...,
        description="Asset symbol (e.g., 'AAPL') or asset ID (e.g., 'as-12345678-1234-5678-9abc-123456789012')",
        examples=["AAPL", "SPY", "BTC-USD", "as-12345678-1234-5678-9abc-123456789012"]
    ),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve asset metadata by symbol or ID.
    
    Returns asset information for use in investment analysis and portfolio construction.
    """
    
    user_id, _ = current_user
    logger.info(f"Fetching asset {identifier} for user {user_id}")
    
    try:
        # Try by ID first if it starts with "as-"
        if identifier.startswith("as-"):
            asset = get_asset_by_id(db, identifier)
        else:
            # Try by symbol
            asset = get_asset_by_symbol(db, identifier)
        
        if not asset:
            logger.warning(f"Asset not found: {identifier}")
            raise handle_not_found_error("Asset", identifier)
        
        logger.info(f"Returning asset: {asset.symbol}")
        return asset
        
    except Exception as e:
        if "not_found" in str(e):
            raise
        logger.error(f"Error fetching asset {identifier}: {str(e)}")
        raise
