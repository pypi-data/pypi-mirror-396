"""
Strategy tools for NSMBL MCP server.

Provides access to systematic investment strategy creation and management.
"""

from typing import Optional, Any
from mcp.types import Tool
from ..client import NSMBLClient, NSMBLAPIError
from ..utils.errors import format_api_error
from ..utils.schemas import (
    STRATEGY_CREATE_SCHEMA,
    BASKET_CONFIG_SCHEMA,
    TACTICAL_CONFIG_SCHEMA,
    ENSEMBLE_CONFIG_SCHEMA,
    PORTFOLIO_CONFIG_SCHEMA
)
from ..utils.validation import validate_strategy_data, format_validation_error
import json


async def create_strategy(
    strategy_type: str,
    strategy_name: str,
    strategy_config: dict[str, Any],
    strategy_symbol: Optional[str] = None
) -> str:
    """
    Create a systematic investment strategy.
    
    Args:
        strategy_type: Strategy type (basket, tactical, ensemble, portfolio)
        strategy_name: Human-readable strategy name
        strategy_config: Complete strategy configuration with universe and models
        strategy_symbol: Optional URL-friendly identifier (auto-generated if not provided)
        
    Returns:
        str: Formatted strategy details
        
    Note:
        This endpoint is charged 1¢ per call.
    """
    try:
        # Build request payload
        strategy_data = {
            "strategy_type": strategy_type,
            "strategy_name": strategy_name,
            "strategy_config": strategy_config
        }
        if strategy_symbol:
            strategy_data["strategy_symbol"] = strategy_symbol
        
        # Client-side validation to catch common mistakes
        is_valid, error_message = validate_strategy_data(strategy_data)
        if not is_valid:
            return format_validation_error("parameters", error_message)
        
        client = NSMBLClient()
        
        # Make API request
        strategy = await client.post("/strategies", strategy_data)
        
        # Format response
        result = [
            f"✅ Strategy Created Successfully",
            f"",
            f"ID: {strategy['strategy_id']}",
            f"Name: {strategy['strategy_name']}",
            f"Symbol: {strategy['strategy_symbol']}",
            f"Type: {strategy['strategy_type']}",
            f"",
            f"Configuration:",
            json.dumps(strategy['strategy_config'], indent=2),
        ]
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def list_strategies(strategy_type: Optional[str] = None) -> str:
    """
    List all strategies with optional type filtering.
    
    Args:
        strategy_type: Optional filter by type ('basket', 'tactical', 'ensemble', 'portfolio')
        
    Returns:
        str: Formatted list of strategies
        
    Note:
        This endpoint is free (no charge).
    """
    try:
        client = NSMBLClient()
        
        # Build query params
        params = {}
        if strategy_type:
            if strategy_type not in ["basket", "tactical", "ensemble", "portfolio"]:
                return format_api_error(
                    f"Invalid strategy_type: {strategy_type}. "
                    f"Must be 'basket', 'tactical', 'ensemble', or 'portfolio'.",
                    status_code=422
                )
            params["strategy_type"] = strategy_type
        
        # Make API request
        strategies = await client.get("/strategies", params=params if params else None)
        
        if not strategies or len(strategies) == 0:
            return "No strategies found."
        
        # Format response
        result = [f"Found {len(strategies)} strategies:\n"]
        for strategy in strategies:
            universe_count = len(strategy['strategy_config'].get('universe', []))
            result.append(
                f"• {strategy['strategy_symbol']} - {strategy['strategy_name']}\n"
                f"  Type: {strategy['strategy_type']}, Universe: {universe_count} assets/strategies\n"
                f"  ID: {strategy['strategy_id']}"
            )
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def get_strategy(strategy_identifier: str) -> str:
    """
    Get details for a specific strategy by ID or symbol.
    
    Args:
        strategy_identifier: Strategy UUID or symbol
        
    Returns:
        str: Formatted strategy details
        
    Note:
        This endpoint is free (no charge).
    """
    try:
        client = NSMBLClient()
        
        # Make API request
        strategy = await client.get(f"/strategies/{strategy_identifier}")
        
        # Format response
        result = [
            f"Strategy Details:",
            f"",
            f"ID: {strategy['strategy_id']}",
            f"Name: {strategy['strategy_name']}",
            f"Symbol: {strategy['strategy_symbol']}",
            f"Type: {strategy['strategy_type']}",
            f"",
            f"Configuration:",
            json.dumps(strategy['strategy_config'], indent=2),
            f"",
            f"Created: {strategy['created_at']}",
            f"Updated: {strategy['updated_at']}",
        ]
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def update_strategy(
    strategy_id: str,
    strategy_name: Optional[str] = None,
    strategy_config: Optional[dict[str, Any]] = None
) -> str:
    """
    Update an existing strategy.
    
    Args:
        strategy_id: Strategy UUID
        strategy_name: Optional new name
        strategy_config: Optional new configuration
        
    Returns:
        str: Formatted updated strategy details
        
    Note:
        This endpoint is charged 1¢ per call.
    """
    try:
        client = NSMBLClient()
        
        # Build update payload
        update_data: dict[str, Any] = {}
        if strategy_name:
            update_data["strategy_name"] = strategy_name
        if strategy_config:
            update_data["strategy_config"] = strategy_config
        
        if not update_data:
            return "No updates provided. Please specify strategy_name or strategy_config."
        
        # Make API request
        strategy = await client.put(f"/strategies/{strategy_id}", update_data)
        
        # Format response
        result = [
            f"✅ Strategy Updated Successfully",
            f"",
            f"ID: {strategy['strategy_id']}",
            f"Name: {strategy['strategy_name']}",
            f"Symbol: {strategy['strategy_symbol']}",
            f"Type: {strategy['strategy_type']}",
            f"",
            f"Configuration:",
            json.dumps(strategy['strategy_config'], indent=2),
            f"",
            f"Updated: {strategy['updated_at']}",
        ]
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def delete_strategy(strategy_id: str) -> str:
    """
    Delete a strategy permanently.
    
    Args:
        strategy_id: Strategy UUID
        
    Returns:
        str: Confirmation message
        
    Note:
        This endpoint is free (no charge).
    """
    try:
        client = NSMBLClient()
        
        # Make API request
        result = await client.delete(f"/strategies/{strategy_id}")
        
        return f"✅ {result.get('message', 'Strategy deleted successfully')}"
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


# Tool definitions for MCP
CREATE_STRATEGY_TOOL = Tool(
    name="create_strategy",
    description=(
        "Create a systematic investment strategy. Four types available:\n\n"
        "• Basket: Static allocation across multiple assets with periodic rebalancing\n"
        "• Tactical: Dynamic strategies that select subsets of assets based on signals (momentum/contrarian)\n"
        "• Ensemble: Combines multiple existing strategies with sophisticated allocation\n"
        "• Portfolio: Highest-level strategy type that can contain assets AND all other strategy types\n\n"
        "IMPORTANT - All models use a two-field structure:\n"
        "1. 'model_name': Specifies which model to use (e.g., 'risk_parity', 'calendar_based', 'momentum')\n"
        "2. 'model_params': Object containing model-specific parameters (can be empty {})\n\n"
        "⚠️ CRITICAL STRUCTURE RULES:\n"
        "• Universe must be an ARRAY of objects: [{'asset_symbol': 'AAPL'}, {'asset_symbol': 'MSFT'}]\n"
        "• Each model needs 'model_name' + 'model_params' (NOT 'type'!)\n"
        "• Use exact enum values - see schema for all valid values\n\n"
        "✅ EXAMPLE - Basket Strategy:\n"
        "{\n"
        '  "strategy_type": "basket",\n'
        '  "strategy_name": "My Strategy Name",\n'
        '  "strategy_config": {\n'
        '    "universe": [\n'
        '      {"asset_symbol": "AAPL"},\n'
        '      {"asset_symbol": "MSFT"}\n'
        '    ],\n'
        '    "allocation_model": {\n'
        '      "model_name": "equal_weight",\n'
        '      "model_params": {}\n'
        '    },\n'
        '    "rebalancing_model": {\n'
        '      "model_name": "calendar_based",\n'
        '      "model_params": {"frequency": "monthly"}\n'
        '    }\n'
        '  }\n'
        '}\n\n'
        "📋 VALID VALUES (see schema for complete details):\n"
        "allocation model_name: 'risk_parity', 'equal_weight', 'fixed_weight', 'inverse_volatility'\n"
        "rebalancing model_name: 'calendar_based', 'drift_based'\n"
        "tactical model_name: 'momentum', 'contrarian' (tactical strategies only)\n"
        "frequency (calendar_based): 'daily', 'weekly', 'monthly', 'quarterly'\n\n"
        "Charged 1¢ per call."
    ),
    inputSchema=STRATEGY_CREATE_SCHEMA
)

LIST_STRATEGIES_TOOL = Tool(
    name="list_strategies",
    description=(
        "List all your strategies with optional type filtering. "
        "Returns strategy IDs, names, symbols, types, and universe sizes.\n\n"
        "Strategy types:\n"
        "• basket: Static allocation strategies\n"
        "• tactical: Signal-driven selection strategies\n"
        "• ensemble: Multi-strategy combinations\n"
        "• portfolio: Top-level investment portfolios\n\n"
        "Use this before creating new strategies to:\n"
        "- See what you've already built\n"
        "- Get strategy IDs/symbols for ensemble or portfolio strategies\n"
        "- Review your existing strategy universe\n\n"
        "Free (no charge)."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "strategy_type": {
                "type": "string",
                "enum": ["basket", "tactical", "ensemble", "portfolio"],
                "description": "Optional: Filter by strategy type (returns all if not specified)"
            }
        }
    }
)

GET_STRATEGY_TOOL = Tool(
    name="get_strategy",
    description=(
        "Get complete details for a specific strategy by UUID or symbol.\n\n"
        "Returns:\n"
        "• Full strategy configuration with all model details\n"
        "• Universe composition (assets/strategies)\n"
        "• Allocation, rebalancing, and tactical model settings\n"
        "• Creation and update timestamps\n\n"
        "Use this to:\n"
        "- Review a strategy's exact configuration before backtesting\n"
        "- See the proper structure when updating a strategy\n"
        "- Verify your strategy was created correctly\n"
        "- Get strategy details for building ensemble/portfolio strategies\n\n"
        "Free (no charge)."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "strategy_identifier": {
                "type": "string",
                "description": (
                    "Strategy UUID (e.g., 'sb-12345678-...') or "
                    "symbol (e.g., 'mag7-rp-daily')"
                )
            }
        },
        "required": ["strategy_identifier"]
    }
)

UPDATE_STRATEGY_TOOL = Tool(
    name="update_strategy",
    description=(
        "Update an existing strategy's name or configuration.\n\n"
        "IMPORTANT - When updating strategy_config:\n"
        "• All models use 'model_name' + 'model_params' structure (NOT 'type'!)\n"
        "• Universe must be an array of objects: [{'asset_symbol': 'AAPL'}]\n"
        "• Configuration must match the strategy's type (basket/tactical/ensemble/portfolio)\n"
        "• Use get_strategy first to see the current configuration structure\n\n"
        "📋 VALID VALUES:\n"
        "allocation model_name: 'risk_parity', 'equal_weight', 'fixed_weight', 'inverse_volatility'\n"
        "rebalancing model_name: 'calendar_based', 'drift_based'\n"
        "tactical model_name: 'momentum', 'contrarian' (tactical strategies only)\n"
        "frequency (calendar_based): 'daily', 'weekly', 'monthly', 'quarterly'\n\n"
        "Charged 1¢ per call."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "strategy_id": {
                "type": "string",
                "description": "Strategy UUID to update (e.g., 'sb-12345678-...')"
            },
            "strategy_name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "Optional: New name for the strategy"
            },
            "strategy_config": {
                "type": "object",
                "description": (
                    "Optional: New configuration for the strategy. "
                    "Must match the strategy's type. Use proper 'model_name' and 'model_params' structure! "
                    "See create_strategy tool for complete structure details."
                )
            }
        },
        "required": ["strategy_id"]
    }
)

DELETE_STRATEGY_TOOL = Tool(
    name="delete_strategy",
    description=(
        "Delete a strategy permanently. This cannot be undone.\n\n"
        "⚠️ WARNING: This is permanent and cannot be reversed!\n\n"
        "Use cases:\n"
        "- Remove test strategies\n"
        "- Clean up strategies you no longer need\n"
        "- Remove strategies before recreating with different config\n\n"
        "💡 TIP: Use list_strategies first to get the correct strategy_id\n\n"
        "Note: Cannot delete strategies that are currently referenced in other strategies "
        "(ensemble/portfolio universes). Remove those references first.\n\n"
        "Free (no charge)."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "strategy_id": {
                "type": "string",
                "description": "Strategy UUID to delete (e.g., 'sb-12345678-...')"
            }
        },
        "required": ["strategy_id"]
    }
)

