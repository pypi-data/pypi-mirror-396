"""
Tactical model schemas for signal generation.

Renamed from signal_models to align with tactical strategy terminology.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class TacticalModelType(str, Enum):
    """Available tactical model types"""
    MOMENTUM = "momentum"
    CONTRARIAN = "contrarian"  # Renamed from mean_reversion


class MomentumConfig(BaseModel):
    """Momentum tactical model configuration"""
    model_name: str = Field("momentum", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"lookback_days": 21, "n_positions": 3},
        description="Parameters: lookback_days (int), n_positions (int) - number of top positions to select",
        example={"lookback_days": 21, "n_positions": 3}
    )
    
    @validator('model_params')
    def validate_momentum_params(cls, v):
        """Validate momentum parameters"""
        lookback_days = v.get('lookback_days', 21)
        n_positions = v.get('n_positions', 3)
        
        if not isinstance(lookback_days, int) or lookback_days < 1:
            raise ValueError("lookback_days must be a positive integer")
        
        if not isinstance(n_positions, int) or n_positions < 1:
            raise ValueError("n_positions must be a positive integer")
        
        return v


class ContrarianConfig(BaseModel):
    """Contrarian tactical model configuration"""
    model_name: str = Field("contrarian", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"lookback_days": 21, "n_positions": 3},
        description="Parameters: lookback_days (int), n_positions (int) - number of worst-performing positions to select",
        example={"lookback_days": 21, "n_positions": 3}
    )
    
    @validator('model_params')
    def validate_contrarian_params(cls, v):
        """Validate contrarian parameters"""
        lookback_days = v.get('lookback_days', 21)
        n_positions = v.get('n_positions', 3)
        
        if not isinstance(lookback_days, int) or lookback_days < 1:
            raise ValueError("lookback_days must be a positive integer")
        
        if not isinstance(n_positions, int) or n_positions < 1:
            raise ValueError("n_positions must be a positive integer")
        
        return v
