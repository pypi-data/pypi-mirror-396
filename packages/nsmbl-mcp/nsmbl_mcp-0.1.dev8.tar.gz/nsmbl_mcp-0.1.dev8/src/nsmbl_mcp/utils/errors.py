"""
Error handling utilities for NSMBL MCP server.
"""

from typing import Optional


def format_api_error(error_message: str, status_code: Optional[int] = None) -> str:
    """
    Format API error for display to user via LLM.
    
    Args:
        error_message: Error message from API or client
        status_code: HTTP status code if available
        
    Returns:
        str: Formatted error message with actionable guidance
    """
    if status_code == 401:
        return (
            f"❌ Authentication Error\n\n"
            f"{error_message}\n\n"
            f"Action needed: Verify your NSMBL_API_KEY is correct in .env file."
        )
    
    elif status_code == 402:
        return (
            f"💳 Insufficient Funds\n\n"
            f"{error_message}\n\n"
            f"Action needed: Add credits at https://app.nsmbl.ai"
        )
    
    elif status_code == 404:
        return (
            f"🔍 Not Found\n\n"
            f"{error_message}\n\n"
            f"The requested resource does not exist. Please check the ID or symbol."
        )
    
    elif status_code == 422:
        return (
            f"⚠️ Validation Error\n\n"
            f"{error_message}\n\n"
            f"Please check your input parameters and try again."
        )
    
    elif status_code == 429:
        return (
            f"⏱️ Rate Limit Exceeded\n\n"
            f"{error_message}\n\n"
            f"Action needed: Wait a moment before retrying."
        )
    
    elif status_code and status_code >= 500:
        return (
            f"🔧 Server Error\n\n"
            f"{error_message}\n\n"
            f"The NSMBL API is experiencing issues. Please try again in a few moments."
        )
    
    else:
        return f"❌ Error\n\n{error_message}"


def format_timeout_error(timeout_seconds: int, backtest_id: str) -> str:
    """
    Format timeout error for backtest operations.
    
    Args:
        timeout_seconds: Timeout duration that was exceeded
        backtest_id: ID of the backtest that timed out
        
    Returns:
        str: Formatted timeout message with guidance
    """
    return (
        f"⏱️ Backtest Timeout\n\n"
        f"The backtest did not complete within {timeout_seconds} seconds.\n\n"
        f"The backtest is still running on the server. You can:\n"
        f"1. Use `get_backtest` with ID '{backtest_id}' to check current status\n"
        f"2. Use `wait_for_backtest` with a longer timeout to continue waiting\n"
        f"3. Use `list_backtests` to see all your backtests and their statuses\n\n"
        f"Complex backtests (tactical, ensemble, portfolio) may take several minutes."
    )


def format_validation_error(field: str, message: str) -> str:
    """
    Format Pydantic validation error for display.
    
    Args:
        field: Field name that failed validation
        message: Validation error message
        
    Returns:
        str: Formatted validation error
    """
    return (
        f"⚠️ Invalid Input: {field}\n\n"
        f"{message}\n\n"
        f"Please check the parameter and try again."
    )

