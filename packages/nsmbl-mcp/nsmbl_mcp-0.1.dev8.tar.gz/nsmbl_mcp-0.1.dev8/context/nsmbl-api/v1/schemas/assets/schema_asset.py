"""
Asset schemas with rich metadata and comprehensive documentation
"""

from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AssetResponse(BaseModel):
    """Comprehensive asset information with instrument-specific metadata."""
    
    id: str = Field(
        ...,
        description="Unique asset identifier with 'as-' prefix",
        example="as-12345678-1234-5678-9abc-123456789012"
    )
    
    symbol: str = Field(
        ...,
        description="Trading symbol or ticker",
        example="AAPL"
    )
    
    name: str = Field(
        ...,
        description="Full legal name of the asset",
        example="Apple Inc"
    )
    
    instrument: str = Field(
        ...,
        description="Asset instrument type",
        example="stock"
    )
    
    exchange: str = Field(
        ...,
        description="Primary exchange or market",
        example="US"
    )
    
    currency: str = Field(
        ...,
        description="Trading currency (ISO 4217 code)",
        example="USD"
    )
    
    delisted: bool = Field(
        ...,
        description="Whether the asset is currently delisted/inactive",
        example=False
    )
    
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp for asset data",
        example="2024-12-09T00:00:00Z"
    )
    
    data: Dict[str, Any] = Field(
        ...,
        description="""Instrument-specific data. Fields vary by instrument type:
        
**Stocks:** sector, industry, country, market_cap, beta, pe_ratio, dividend_yield
**ETFs:** category, expense_ratio, aum, holdings_count, top_holdings, sector_weights
**Crypto:** circulating_supply, max_supply
**Funds:** fund_manager, inception_date, expense_ratio, category""",
        example={
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 3000000000000,
            "beta": 1.29
        }
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
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
                        "country": "USA",
                        "sector": "Technology",
                        "industry": "Consumer Electronics",
                        "market_cap": 3000000000000,
                        "beta": 1.29,
                        "pe_ratio": 28.5,
                        "dividend_yield": 0.55
                    }
                },
                {
                    "id": "as-87654321-4321-8765-cba9-210987654321",
                    "symbol": "SPY",
                    "name": "SPDR S&P 500 ETF Trust",
                    "instrument": "etf",
                    "exchange": "US",
                    "currency": "USD",
                    "delisted": False,
                    "updated_at": "2024-12-09T00:00:00Z",
                    "data": {
                        "category": "Large Cap Blend",
                        "expense_ratio": 0.0945,
                        "aum": 500000000000,
                        "holdings_count": 503,
                        "top_holdings": [
                            {"symbol": "AAPL", "weight": 7.2},
                            {"symbol": "MSFT", "weight": 6.8}
                        ],
                        "sector_weights": {"Technology": 28.5, "Healthcare": 13.2}
                    }
                },
                {
                    "id": "as-11111111-2222-3333-4444-555555555555",
                    "symbol": "BTC-USD",
                    "name": "Bitcoin",
                    "instrument": "crypto",
                    "exchange": "CC",
                    "currency": "USD",
                    "delisted": False,
                    "updated_at": "2024-12-09T00:00:00Z",
                    "data": {
                        "circulating_supply": 19500000,
                        "max_supply": 21000000
                    }
                }
            ]
        }


class PaginatedAssetResponse(BaseModel):
    """Paginated response for asset list endpoint with metadata"""
    
    assets: List[AssetResponse] = Field(
        ...,
        description="Array of assets for current page"
    )
    
    total: int = Field(
        ...,
        description="Total number of assets matching filters"
    )
    
    limit: int = Field(
        ...,
        description="Maximum items per page"
    )
    
    offset: int = Field(
        ...,
        description="Starting position in result set"
    )
    
    returned: int = Field(
        ...,
        description="Number of items in current response"
    )
    
    class Config:
        json_schema_extra = {
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


class AssetSearchResponse(BaseModel):
    """Response for natural language asset search"""
    
    assets: List[AssetResponse] = Field(
        ...,
        description="Array of matching assets"
    )
    
    query: str = Field(
        ...,
        description="Original search query"
    )
    
    returned: int = Field(
        ...,
        description="Number of results returned"
    )
