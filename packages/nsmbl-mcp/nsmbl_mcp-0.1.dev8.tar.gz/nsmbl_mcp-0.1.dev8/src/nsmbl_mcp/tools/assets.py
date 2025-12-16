"""
Asset tools for NSMBL MCP server.

Provides access to tradeable assets (stocks, ETFs).
"""

from typing import Optional
from mcp.types import Tool, TextContent
from ..client import NSMBLClient, NSMBLAPIError
from ..utils.errors import format_api_error


async def list_assets(
    asset_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> str:
    """
    List all tradeable assets with optional type filtering and pagination.
    
    Args:
        asset_type: Optional filter by asset type ('stock' or 'etf')
        limit: Maximum number of assets to return per page (default: 50, max: 500)
        offset: Starting position in result set for pagination (default: 0)
        
    Returns:
        str: Formatted list of assets with pagination metadata
        
    Note:
        This endpoint is charged 1¢ per call.
    """
    try:
        client = NSMBLClient()
        
        # Build query params
        params = {}
        if asset_type:
            if asset_type not in ["stock", "etf"]:
                return format_api_error(
                    f"Invalid asset_type: {asset_type}. Must be 'stock' or 'etf'.",
                    status_code=422
                )
            params["asset_type"] = asset_type
        
        # Validate pagination parameters
        if limit < 1 or limit > 500:
            return format_api_error(
                f"Invalid limit: {limit}. Must be between 1 and 500.",
                status_code=422
            )
        if offset < 0:
            return format_api_error(
                f"Invalid offset: {offset}. Must be 0 or greater.",
                status_code=422
            )
        
        params["limit"] = limit
        params["offset"] = offset
        
        # Make API request
        response = await client.get("/assets", params=params)
        
        # Extract assets array from paginated response
        assets = response.get("assets", [])
        total = response.get("total", 0)
        returned = response.get("returned", 0)
        current_offset = response.get("offset", 0)
        current_limit = response.get("limit", limit)
        
        if not assets or len(assets) == 0:
            return "No assets found."
        
        # Calculate pagination info
        current_page = (current_offset // current_limit) + 1
        total_pages = (total + current_limit - 1) // current_limit  # Ceiling division
        has_more = (current_offset + returned) < total
        
        # Format response
        result = [
            f"Assets (Page {current_page} of {total_pages}):",
            f"Showing {returned} of {total} total assets",
            ""
        ]
        
        for asset in assets:
            result.append(
                f"• {asset['asset_symbol']} - {asset['asset_name']} ({asset['asset_type']})"
            )
        
        # Add pagination hint
        if has_more:
            next_offset = current_offset + returned
            result.append("")
            result.append(f"→ More assets available. Use offset={next_offset} to see the next page.")
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def get_asset(asset_id_or_symbol: str) -> str:
    """
    Get details for a specific asset by symbol or ID.
    
    Args:
        asset_id_or_symbol: Asset symbol (e.g., 'VTI') or asset UUID
        
    Returns:
        str: Formatted asset details
        
    Note:
        This endpoint is charged 1¢ per call.
    """
    try:
        client = NSMBLClient()
        
        # Make API request
        asset = await client.get(f"/assets/{asset_id_or_symbol}")
        
        # Format response
        result = [
            f"Asset Details:",
            f"",
            f"Symbol: {asset['asset_symbol']}",
            f"Name: {asset['asset_name']}",
            f"Type: {asset['asset_type']}",
            f"ID: {asset['asset_id']}",
        ]
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


# Tool definitions for MCP
LIST_ASSETS_TOOL = Tool(
    name="list_assets",
    description=(
        "Browse all available tradeable assets (stocks and ETFs) with pagination and optional type filtering. "
        "Returns asset symbols, names, types, and IDs for use in strategy construction. "
        "Results are paginated to handle large datasets efficiently - use limit and offset for pagination. "
        "Use this to explore what assets are available before building strategies. "
        "Charged 1¢ per call."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "asset_type": {
                "type": "string",
                "enum": ["stock", "etf"],
                "description": "Optional: Filter by asset type (returns all if not specified)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of assets to return per page (default: 50, max: 500)",
                "default": 50,
                "minimum": 1,
                "maximum": 500
            },
            "offset": {
                "type": "integer",
                "description": "Starting position in result set for pagination (default: 0)",
                "default": 0,
                "minimum": 0
            }
        },
    }
)

GET_ASSET_TOOL = Tool(
    name="get_asset",
    description=(
        "Get details for a specific asset by symbol or UUID. "
        "Charged 1¢ per call."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "asset_id_or_symbol": {
                "type": "string",
                "description": "Asset symbol (e.g., 'VTI', 'AAPL') or asset UUID"
            }
        },
        "required": ["asset_id_or_symbol"]
    }
)

