"""
Pydantic schemas for strategies endpoint
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class StrategyCreateRequest(BaseModel):
    """Request model for creating a new strategy"""
    prompt: str = Field(
        ...,
        description="Natural language description of the investment strategy",
        min_length=10,
        max_length=2000,
        example="Buy and hold SPY"
    )
    name: Optional[str] = Field(
        None,
        description="Override LLM-generated strategy name",
        max_length=100,
        example="My SPY Strategy"
    )


class StrategyUpdateRequest(BaseModel):
    """Request model for updating a strategy"""
    name: Optional[str] = Field(None, max_length=100, description="Update strategy name")
    symbol: Optional[str] = Field(None, max_length=10, description="Update strategy symbol")
    is_public: Optional[bool] = Field(None, description="Toggle public sharing")


class StrategyResponse(BaseModel):
    """Response model for strategy creation/list"""
    id: str = Field(..., description="Strategy ID")
    name: str = Field(..., description="Strategy name")
    symbol: str = Field(..., description="Strategy symbol")
    prompt: str = Field(..., description="Original user prompt")
    url: str = Field(..., description="Visualization URL")
    embed: str = Field(..., description="Embed iframe code")
    is_public: bool = Field(..., description="Public sharing enabled")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class StrategyUsage(BaseModel):
    """Billing usage stats for Stripe metering"""
    units: int
    base: int
    tokens: int
    seconds: int


class StrategyAvailability(BaseModel):
    """Data availability metadata"""
    partial: Optional[str] = None
    complete: Optional[str] = None


class StrategyTiming(BaseModel):
    """Pipeline execution timing breakdown"""
    pass  # Will contain dynamic node timing data


class StrategyDetailResponse(StrategyResponse):
    """Response model for strategy detail"""
    script: str = Field(..., description="LLM-generated Python code")
    usage: Optional[StrategyUsage] = None
    timing: Optional[Dict[str, Any]] = None
    availability: Optional[StrategyAvailability] = None


class StrategyHistoryResponse(BaseModel):
    """Response model for strategy price history"""
    dates: List[str] = Field(..., description="Array of dates")
    returns: List[float] = Field(..., description="Array of daily returns")
    positions: List[Dict[str, float]] = Field(..., description="Array of daily positions")
    availability: Optional[StrategyAvailability] = None


class StrategyMetricsResponse(BaseModel):
    """Response model for performance metrics"""
    cagr: float
    volatility: float
    sharpe: float
    max_drawdown: float
    trades: int = 0
    trading_days: int
