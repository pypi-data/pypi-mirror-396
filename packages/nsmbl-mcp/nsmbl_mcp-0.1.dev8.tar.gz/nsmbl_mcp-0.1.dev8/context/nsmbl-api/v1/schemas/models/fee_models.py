"""
Fee model schemas for future implementation.

Currently not implemented - all strategies default to 0 fees.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class FeeModelType(str, Enum):
    """Available fee model types (future implementation)"""
    FIXED_PERCENTAGE = "fixed_percentage"
    TIERED_PERCENTAGE = "tiered_percentage"
    FIXED_AMOUNT = "fixed_amount"


class FixedPercentageConfig(BaseModel):
    """Fixed percentage fee model configuration"""
    model_name: str = Field("fixed_percentage", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"fee_percentage": 0.0},
        description="Parameters: fee_percentage (float) - percentage fee per trade",
        example={"fee_percentage": 0.001}  # 0.1% fee
    )


class TieredPercentageConfig(BaseModel):
    """Tiered percentage fee model configuration (future)"""
    model_name: str = Field("tiered_percentage", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"tiers": [{"threshold": 0, "fee": 0.001}]},
        description="Parameters: tiers (list) - fee tiers based on trade size",
        example={"tiers": [{"threshold": 0, "fee": 0.001}, {"threshold": 100000, "fee": 0.0005}]}
    )


class FixedAmountConfig(BaseModel):
    """Fixed amount fee model configuration (future)"""
    model_name: str = Field("fixed_amount", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"fee_amount": 0.0},
        description="Parameters: fee_amount (float) - fixed fee per trade in USD",
        example={"fee_amount": 1.0}  # $1 per trade
    )
