"""
NSMBL MCP Server

Provides LLM access to NSMBL API for systematic investment strategies and backtesting.
"""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback version when package is not installed (e.g., during development)
    __version__ = "0.0.0.dev0+unknown"

