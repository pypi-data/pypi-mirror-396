"""
Leverage model schemas for future implementation.

Currently not implemented - all strategies default to 1x leverage (no leverage).
"""

from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class LeverageModelType(str, Enum):
    """Available leverage model types (future implementation)"""
    FIXED_RATIO = "fixed_ratio"
    VOLATILITY_TARGET = "volatility_target"


class FixedRatioConfig(BaseModel):
    """Fixed ratio leverage model configuration"""
    model_name: str = Field("fixed_ratio", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"leverage": 1.0},
        description="Parameters: leverage (float) - leverage ratio (1.0 = no leverage)",
        example={"leverage": 1.0}
    )
    
    @validator('model_params')
    def validate_leverage_params(cls, v):
        """Validate leverage parameters"""
        leverage = v.get('leverage', 1.0)
        
        if not isinstance(leverage, (int, float)) or leverage <= 0:
            raise ValueError("leverage must be a positive number")
        
        if leverage > 3.0:
            raise ValueError("leverage cannot exceed 3.0x for risk management")
        
        return v


class VolatilityTargetConfig(BaseModel):
    """Volatility target leverage model configuration (future)"""
    model_name: str = Field("volatility_target", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"target_volatility": 0.15, "lookback_days": 252},
        description="Parameters: target_volatility (float), lookback_days (int)",
        example={"target_volatility": 0.15, "lookback_days": 252}
    )
