"""
Validation helpers for NSMBL MCP tools.

Provides client-side validation to catch common mistakes before API calls,
with user-friendly error messages and suggestions for corrections.
"""

from typing import Any, Dict, List, Optional, Tuple


# Valid enum values
VALID_STRATEGY_TYPES = ["basket", "tactical", "ensemble", "portfolio"]
VALID_ALLOCATION_MODELS = ["risk_parity", "equal_weight", "fixed_weight", "inverse_volatility"]
VALID_REBALANCING_MODELS = ["calendar_based", "drift_based"]
VALID_TACTICAL_MODELS = ["momentum", "contrarian"]
VALID_FREQUENCIES = ["daily", "weekly", "monthly", "quarterly"]

# Common mistakes mapping
COMMON_MISTAKES = {
    # allocation_model mistakes
    "type": "model_name",
    "equal_risk_contributions": "risk_parity",
    "erc": "risk_parity",
    "equal": "equal_weight",
    "fixed": "fixed_weight",
    "inverse_vol": "inverse_volatility",
    "inv_vol": "inverse_volatility",
    
    # rebalancing_model mistakes
    "periodic": "calendar_based",
    "scheduled": "calendar_based",
    "calendar": "calendar_based",
    "threshold": "drift_based",
    "drift": "drift_based",
    
    # tactical_model mistakes
    "mean_reversion": "contrarian",
    "mean_rev": "contrarian",
    "mom": "momentum",
    
    # frequency mistakes
    "day": "daily",
    "week": "weekly",
    "month": "monthly",
    "quarter": "quarterly",
}


def validate_strategy_data(strategy_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate strategy_data structure before sending to API.
    
    Args:
        strategy_data: Strategy configuration dict
        
    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid with helpful correction suggestion
    """
    # Check required top-level fields
    if "strategy_type" not in strategy_data:
        return False, "Missing required field 'strategy_type'. Must be one of: basket, tactical, ensemble, portfolio"
    
    if "strategy_name" not in strategy_data:
        return False, "Missing required field 'strategy_name'"
    
    if "strategy_config" not in strategy_data:
        return False, "Missing required field 'strategy_config'"
    
    # Validate strategy_type
    strategy_type = strategy_data["strategy_type"]
    if strategy_type not in VALID_STRATEGY_TYPES:
        return False, (
            f"Invalid strategy_type '{strategy_type}'. "
            f"Must be one of: {', '.join(VALID_STRATEGY_TYPES)}"
        )
    
    # Validate strategy_config structure
    config = strategy_data["strategy_config"]
    if not isinstance(config, dict):
        return False, "strategy_config must be an object (dict), not a string or other type"
    
    # Check for universe
    if "universe" not in config:
        return False, (
            "Missing 'universe' in strategy_config. "
            "Universe must be an array of objects like [{'asset_symbol': 'AAPL'}]"
        )
    
    # Validate universe structure
    universe_valid, universe_error = validate_universe(config["universe"])
    if not universe_valid:
        return False, universe_error
    
    # Check for allocation_model
    if "allocation_model" not in config:
        return False, "Missing 'allocation_model' in strategy_config"
    
    # Validate allocation_model
    alloc_valid, alloc_error = validate_allocation_model(config["allocation_model"])
    if not alloc_valid:
        return False, alloc_error
    
    # Check for rebalancing_model
    if "rebalancing_model" not in config:
        return False, "Missing 'rebalancing_model' in strategy_config"
    
    # Validate rebalancing_model
    rebal_valid, rebal_error = validate_rebalancing_model(config["rebalancing_model"])
    if not rebal_valid:
        return False, rebal_error
    
    # Tactical strategies must have tactical_model
    if strategy_type == "tactical":
        if "tactical_model" not in config:
            return False, (
                "Tactical strategies require 'tactical_model' in strategy_config. "
                "Use either 'momentum' or 'contrarian'"
            )
        
        tactical_valid, tactical_error = validate_tactical_model(config["tactical_model"])
        if not tactical_valid:
            return False, tactical_error
    
    # Ensemble strategies require minimum 2 items in universe
    if strategy_type == "ensemble":
        if len(config["universe"]) < 2:
            return False, (
                "Ensemble strategies require at least 2 items in universe. "
                "Use basket type for single strategy or asset allocation."
            )
    
    return True, None


def validate_universe(universe: Any) -> Tuple[bool, Optional[str]]:
    """Validate universe structure."""
    if not isinstance(universe, list):
        # Check for common mistake: {"type": "static", "assets": [...]}
        if isinstance(universe, dict):
            if "type" in universe or "assets" in universe:
                return False, (
                    "❌ Common mistake detected! "
                    "Don't use {'type': 'static', 'assets': [...]} structure. "
                    "Instead use: [{'asset_symbol': 'AAPL'}, {'asset_symbol': 'MSFT'}]"
                )
            return False, "universe must be an array, not an object"
        return False, f"universe must be an array, not {type(universe).__name__}"
    
    if len(universe) == 0:
        return False, "universe cannot be empty - must have at least 1 item"
    
    # Validate each universe reference
    for i, ref in enumerate(universe):
        if not isinstance(ref, dict):
            return False, (
                f"universe item {i} must be an object. "
                f"Use {{'asset_symbol': 'AAPL'}} not just 'AAPL'"
            )
        
        # Check if at least one identifier is present
        identifiers = ["asset_symbol", "asset_id", "strategy_symbol", "strategy_id"]
        has_identifier = any(key in ref for key in identifiers)
        
        if not has_identifier:
            return False, (
                f"universe item {i} must have at least one of: "
                f"{', '.join(identifiers)}. "
                f"Example: {{'asset_symbol': 'AAPL'}}"
            )
    
    return True, None


def validate_allocation_model(model: Any) -> Tuple[bool, Optional[str]]:
    """Validate allocation_model structure."""
    if not isinstance(model, dict):
        return False, "allocation_model must be an object"
    
    # Check for common mistake: using "type" instead of "model_name"
    if "type" in model and "model_name" not in model:
        model_type = model["type"]
        suggestion = COMMON_MISTAKES.get(model_type, model_type)
        return False, (
            f"❌ Common mistake detected! "
            f"Use 'model_name' not 'type' in allocation_model. "
            f"Try: {{'model_name': '{suggestion}', 'model_params': {{}}}}"
        )
    
    if "model_name" not in model:
        return False, (
            "allocation_model must have 'model_name' field. "
            f"Valid values: {', '.join(VALID_ALLOCATION_MODELS)}"
        )
    
    model_name = model["model_name"]
    
    # Check for common mistakes in model_name value
    if model_name not in VALID_ALLOCATION_MODELS:
        if model_name in COMMON_MISTAKES:
            suggestion = COMMON_MISTAKES[model_name]
            return False, (
                f"❌ Invalid model_name '{model_name}'. "
                f"Did you mean '{suggestion}'? "
                f"Valid values: {', '.join(VALID_ALLOCATION_MODELS)}"
            )
        return False, (
            f"Invalid allocation model_name '{model_name}'. "
            f"Valid values: {', '.join(VALID_ALLOCATION_MODELS)}"
        )
    
    # Validate model_params for specific models
    if model_name == "fixed_weight":
        if "model_params" not in model:
            return False, "fixed_weight allocation requires 'model_params' with 'weights' array"
        
        params = model["model_params"]
        if "weights" not in params:
            return False, (
                "fixed_weight allocation requires 'weights' array in model_params. "
                "Example: {'model_name': 'fixed_weight', 'model_params': {'weights': [0.5, 0.3, 0.2]}}"
            )
        
        weights = params["weights"]
        if not isinstance(weights, list) or not weights:
            return False, "weights must be a non-empty array of numbers"
        
        # Check if weights sum to approximately 1.0
        total = sum(weights)
        if abs(total - 1.0) > 0.01:
            return False, f"weights must sum to 1.0 (currently sum to {total:.4f})"
    
    return True, None


def validate_rebalancing_model(model: Any) -> Tuple[bool, Optional[str]]:
    """Validate rebalancing_model structure."""
    if not isinstance(model, dict):
        return False, "rebalancing_model must be an object"
    
    # Check for common mistake: using "type" instead of "model_name"
    if "type" in model and "model_name" not in model:
        model_type = model["type"]
        suggestion = COMMON_MISTAKES.get(model_type, model_type)
        return False, (
            f"❌ Common mistake detected! "
            f"Use 'model_name' not 'type' in rebalancing_model. "
            f"Try: {{'model_name': '{suggestion}', 'model_params': {{}}}}"
        )
    
    if "model_name" not in model:
        return False, (
            "rebalancing_model must have 'model_name' field. "
            f"Valid values: {', '.join(VALID_REBALANCING_MODELS)}"
        )
    
    model_name = model["model_name"]
    
    # Check for common mistakes in model_name value
    if model_name not in VALID_REBALANCING_MODELS:
        if model_name in COMMON_MISTAKES:
            suggestion = COMMON_MISTAKES[model_name]
            return False, (
                f"❌ Invalid model_name '{model_name}'. "
                f"Did you mean '{suggestion}'? "
                f"Valid values: {', '.join(VALID_REBALANCING_MODELS)}"
            )
        return False, (
            f"Invalid rebalancing model_name '{model_name}'. "
            f"Valid values: {', '.join(VALID_REBALANCING_MODELS)}"
        )
    
    # Validate frequency for calendar_based
    if model_name == "calendar_based":
        if "model_params" in model:
            params = model["model_params"]
            if "frequency" in params:
                frequency = params["frequency"]
                if frequency not in VALID_FREQUENCIES:
                    if frequency in COMMON_MISTAKES:
                        suggestion = COMMON_MISTAKES[frequency]
                        return False, (
                            f"❌ Invalid frequency '{frequency}'. "
                            f"Did you mean '{suggestion}'? "
                            f"Valid values: {', '.join(VALID_FREQUENCIES)}"
                        )
                    return False, (
                        f"Invalid frequency '{frequency}'. "
                        f"Valid values: {', '.join(VALID_FREQUENCIES)}"
                    )
    
    return True, None


def validate_tactical_model(model: Any) -> Tuple[bool, Optional[str]]:
    """Validate tactical_model structure."""
    if not isinstance(model, dict):
        return False, "tactical_model must be an object"
    
    # Check for common mistake: using "type" instead of "model_name"
    if "type" in model and "model_name" not in model:
        model_type = model["type"]
        suggestion = COMMON_MISTAKES.get(model_type, model_type)
        return False, (
            f"❌ Common mistake detected! "
            f"Use 'model_name' not 'type' in tactical_model. "
            f"Try: {{'model_name': '{suggestion}', 'model_params': {{}}}}"
        )
    
    if "model_name" not in model:
        return False, (
            "tactical_model must have 'model_name' field. "
            f"Valid values: {', '.join(VALID_TACTICAL_MODELS)}"
        )
    
    model_name = model["model_name"]
    
    # Check for common mistakes in model_name value
    if model_name not in VALID_TACTICAL_MODELS:
        if model_name in COMMON_MISTAKES:
            suggestion = COMMON_MISTAKES[model_name]
            return False, (
                f"❌ Invalid model_name '{model_name}'. "
                f"Did you mean '{suggestion}'? "
                f"Valid values: {', '.join(VALID_TACTICAL_MODELS)}"
            )
        return False, (
            f"Invalid tactical model_name '{model_name}'. "
            f"Valid values: {', '.join(VALID_TACTICAL_MODELS)}"
        )
    
    return True, None


def format_validation_error(field_path: str, error: str) -> str:
    """
    Format a validation error with helpful context.
    
    Args:
        field_path: Dot-notation path to field (e.g., "strategy_config.allocation_model")
        error: Error description
        
    Returns:
        Formatted error message
    """
    return f"❌ Validation Error in {field_path}:\n\n{error}\n\n💡 See tool description for correct structure and examples."

