"""
Allocation model schemas with modern terminology.

Renamed from optimization_models to better reflect that this covers
both algorithmic optimization and rule-based allocation methods.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class AllocationModelType(str, Enum):
    """Available allocation model types"""
    RISK_PARITY = "risk_parity"  # Renamed from equal_risk_contributions
    EQUAL_WEIGHT = "equal_weight"
    FIXED_WEIGHT = "fixed_weight"
    INVERSE_VOLATILITY = "inverse_volatility"


class RiskParityConfig(BaseModel):
    """Risk parity allocation model configuration"""
    model_name: str = Field("risk_parity", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"lookback_days": 252},
        description="Parameters: lookback_days (int) - period for risk calculation",
        example={"lookback_days": 252}
    )


class EqualWeightConfig(BaseModel):
    """Equal weight allocation model configuration"""
    model_name: str = Field("equal_weight", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="No parameters required for equal weight allocation",
        example={}
    )


class FixedWeightConfig(BaseModel):
    """Fixed weight allocation model configuration"""
    model_name: str = Field("fixed_weight", const=True)
    model_params: Dict[str, Any] = Field(
        ...,
        description="Parameters: weights (array of floats) - must sum to 1.0",
        example={"weights": [0.4, 0.3, 0.2, 0.1]}
    )
    
    @validator('model_params')
    def validate_weights(cls, v):
        """Validate weights sum to 1.0"""
        weights = v.get('weights', [])
        if not weights:
            raise ValueError("weights parameter is required")
        if not isinstance(weights, list):
            raise ValueError("weights must be a list of numbers")
        if abs(sum(weights) - 1.0) > 0.001:  # Allow small floating point errors
            raise ValueError("weights must sum to 1.0")
        return v


class InverseVolatilityConfig(BaseModel):
    """Inverse volatility allocation model configuration"""
    model_name: str = Field("inverse_volatility", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"lookback_days": 252},
        description="Parameters: lookback_days (int) - period for volatility calculation",
        example={"lookback_days": 252}
    )
