"""
Rebalancing model schemas for strategy rebalancing configuration.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class RebalancingModelType(str, Enum):
    """Available rebalancing model types"""
    CALENDAR_BASED = "calendar_based"
    DRIFT_BASED = "drift_based"


class CalendarBasedConfig(BaseModel):
    """Calendar-based rebalancing model configuration"""
    model_name: str = Field("calendar_based", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"frequency": "monthly"},
        description="Parameters: frequency (str), day_of_month (int), months (list) for quarterly",
        example={"frequency": "monthly", "day_of_month": 1}
    )
    
    @validator('model_params')
    def validate_calendar_params(cls, v):
        """Validate calendar-based parameters"""
        frequency = v.get('frequency')
        valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        
        if frequency not in valid_frequencies:
            raise ValueError(f"frequency must be one of: {', '.join(valid_frequencies)}")
        
        # Validate day_of_month if provided
        day_of_month = v.get('day_of_month')
        if day_of_month is not None:
            if not isinstance(day_of_month, int) or not (1 <= day_of_month <= 31):
                raise ValueError("day_of_month must be an integer between 1 and 31")
        
        # Validate months if provided (for quarterly)
        months = v.get('months')
        if months is not None:
            if not isinstance(months, list) or not all(isinstance(m, int) and 1 <= m <= 12 for m in months):
                raise ValueError("months must be a list of integers between 1 and 12")
        
        return v


class DriftBasedConfig(BaseModel):
    """Drift-based rebalancing model configuration"""
    model_name: str = Field("drift_based", const=True)
    model_params: Dict[str, Any] = Field(
        default_factory=lambda: {"threshold": 0.05},
        description="Parameters: threshold (float) - drift threshold to trigger rebalancing",
        example={"threshold": 0.05}
    )
    
    @validator('model_params')
    def validate_drift_params(cls, v):
        """Validate drift-based parameters"""
        threshold = v.get('threshold', 0.05)
        
        if not isinstance(threshold, (int, float)) or threshold <= 0:
            raise ValueError("threshold must be a positive number")
        
        return v
