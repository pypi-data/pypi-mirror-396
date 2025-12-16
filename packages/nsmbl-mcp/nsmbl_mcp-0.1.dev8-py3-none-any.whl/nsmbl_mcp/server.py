"""
Main MCP server for NSMBL API.

Registers all tools and handles MCP protocol communication.
"""

import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.types import TextContent, Tool
from mcp.server.stdio import stdio_server

# Import all tools
from .tools.assets import (
    list_assets,
    get_asset,
    LIST_ASSETS_TOOL,
    GET_ASSET_TOOL
)
from .tools.strategies import (
    create_strategy,
    list_strategies,
    get_strategy,
    update_strategy,
    delete_strategy,
    CREATE_STRATEGY_TOOL,
    LIST_STRATEGIES_TOOL,
    GET_STRATEGY_TOOL,
    UPDATE_STRATEGY_TOOL,
    DELETE_STRATEGY_TOOL
)
from .tools.backtests import (
    create_backtest,
    get_backtest,
    list_backtests,
    create_backtest_and_wait,
    wait_for_backtest,
    check_backtest_status,
    CREATE_BACKTEST_TOOL,
    GET_BACKTEST_TOOL,
    LIST_BACKTESTS_TOOL,
    CREATE_BACKTEST_AND_WAIT_TOOL,
    WAIT_FOR_BACKTEST_TOOL,
    CHECK_BACKTEST_STATUS_TOOL
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nsmbl-mcp")

# Create server instance
app = Server("nsmbl-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        # Asset tools (2)
        LIST_ASSETS_TOOL,
        GET_ASSET_TOOL,
        # Strategy tools (5)
        CREATE_STRATEGY_TOOL,
        LIST_STRATEGIES_TOOL,
        GET_STRATEGY_TOOL,
        UPDATE_STRATEGY_TOOL,
        DELETE_STRATEGY_TOOL,
        # Backtest tools (6)
        CREATE_BACKTEST_TOOL,
        GET_BACKTEST_TOOL,
        LIST_BACKTESTS_TOOL,
        CREATE_BACKTEST_AND_WAIT_TOOL,
        WAIT_FOR_BACKTEST_TOOL,
        CHECK_BACKTEST_STATUS_TOOL,
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool execution requests.
    
    Args:
        name: Tool name to execute
        arguments: Tool arguments
        
    Returns:
        list[TextContent]: Tool execution results
    """
    try:
        logger.info(f"Executing tool: {name}")
        
        # Asset tools
        if name == "list_assets":
            result = await list_assets(
                asset_type=arguments.get("asset_type"),
                limit=arguments.get("limit", 50),
                offset=arguments.get("offset", 0)
            )
        elif name == "get_asset":
            result = await get_asset(
                asset_id_or_symbol=arguments["asset_id_or_symbol"]
            )
        
        # Strategy tools
        elif name == "create_strategy":
            result = await create_strategy(
                strategy_type=arguments["strategy_type"],
                strategy_name=arguments["strategy_name"],
                strategy_config=arguments["strategy_config"],
                strategy_symbol=arguments.get("strategy_symbol")
            )
        elif name == "list_strategies":
            result = await list_strategies(
                strategy_type=arguments.get("strategy_type")
            )
        elif name == "get_strategy":
            result = await get_strategy(
                strategy_identifier=arguments["strategy_identifier"]
            )
        elif name == "update_strategy":
            result = await update_strategy(
                strategy_id=arguments["strategy_id"],
                strategy_name=arguments.get("strategy_name"),
                strategy_config=arguments.get("strategy_config")
            )
        elif name == "delete_strategy":
            result = await delete_strategy(
                strategy_id=arguments["strategy_id"]
            )
        
        # Backtest tools
        elif name == "create_backtest":
            result = await create_backtest(
                target_id=arguments["target_id"],
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date"),
                initial_capital=arguments.get("initial_capital", 100000.0)
            )
        elif name == "get_backtest":
            result = await get_backtest(
                backtest_id=arguments["backtest_id"]
            )
        elif name == "list_backtests":
            result = await list_backtests(
                target_id=arguments.get("target_id"),
                status=arguments.get("status"),
                limit=arguments.get("limit", 100)
            )
        elif name == "create_backtest_and_wait":
            result = await create_backtest_and_wait(
                target_id=arguments["target_id"],
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date"),
                initial_capital=arguments.get("initial_capital", 100000.0),
                timeout_seconds=arguments.get("timeout_seconds")
            )
        elif name == "wait_for_backtest":
            result = await wait_for_backtest(
                backtest_id=arguments["backtest_id"],
                timeout_seconds=arguments.get("timeout_seconds")
            )
        elif name == "check_backtest_status":
            result = await check_backtest_status(
                backtest_id=arguments["backtest_id"]
            )
        
        else:
            result = f"Unknown tool: {name}"
            logger.error(result)
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=f"❌ {error_msg}")]


async def main() -> None:
    """Main entry point for MCP server."""
    try:
        # Validate configuration on startup
        from .config import get_config
        config = get_config()
        logger.info(f"NSMBL MCP Server starting with config: {config}")
        logger.info("14 tools available: 2 assets, 5 strategies, 6 backtests (3 raw + 3 convenience)")
        
        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
            
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure NSMBL_API_KEY is set.")
        raise
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


def run() -> None:
    """Synchronous entry point for running the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()

