# NSMBL MCP Server

> Model Context Protocol server for NSMBL API - enables LLMs to create systematic investment strategies and run backtests

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io)

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [MCP Client Setup](#mcp-client-setup)
- [Quick Start](#quick-start)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Billing Notes](#billing-notes)
- [Links](#links)

## Overview

The NSMBL MCP Server provides LLM access to the NSMBL API for creating systematic investment strategies and running sophisticated backtests. It implements the Model Context Protocol (MCP), enabling AI assistants like Claude to interact with NSMBL's investment platform.

### Key Features

- **14 Tools** covering assets, strategies, and backtests
- **Asset Management**: Browse and search stocks and ETFs
- **Strategy Creation**: Build basket, tactical, ensemble, and portfolio strategies
- **Backtesting**: Run historical simulations with automatic polling
- **Async Support**: Built for MCP's async-first architecture
- **Convenience Tools**: Auto-polling tools for better UX with long-running backtests

## Prerequisites

**For Users:**
- **Homebrew** (macOS only) - Install from [brew.sh](https://brew.sh) if not already installed
- **uv Package Manager** - Fast Python package installer (see installation below)
- **NSMBL API Account** - Sign up at [app.nsmbl.io](https://app.nsmbl.io)
- **NSMBL API Key** - Get your key from the NSMBL dashboard
- **MCP-Compatible Client** - Claude Desktop, Cursor, Cline, or other MCP clients

**For Developers:**
- **Python 3.10+** (Python 3.11 or 3.12 recommended)
- **Git** - For cloning the repository
- All of the above

## Installation

> 📖 **Detailed guide**: See [INSTALLATION.md](INSTALLATION.md) for comprehensive platform-specific instructions and troubleshooting.

### For Users (Recommended - Zero Setup!)

The easiest way to use NSMBL MCP is through `uvx`, which automatically handles installation and updates:

**Step 1: Install `uv` (one-time setup)**

**macOS (Recommended):**
```bash
brew install uv
```
> Using Homebrew ensures `uvx` is in the system PATH and works with GUI applications like Claude Desktop.

**Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
> After installation, add `~/.local/bin` to your PATH if needed.

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 2: Configure your MCP client**

That's it! Just add the configuration below to your MCP client, and the server will auto-install when first used.

### For Developers

If you want to contribute or modify the code:

```bash
git clone https://github.com/nsmbl/nsmbl-mcp.git
cd nsmbl-mcp
pip install -e .
```

> **Note**: The `-e` flag installs in **editable mode**, which means changes to the source code are immediately active without reinstalling.

### API Key Setup

Get your NSMBL API key from [app.nsmbl.io](https://app.nsmbl.io) - you'll add it to your MCP client configuration below.

## MCP Client Setup

### Claude Desktop

1. Open your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the NSMBL MCP server configuration:

```json
{
  "mcpServers": {
    "nsmbl": {
      "command": "uvx",
      "args": ["nsmbl-mcp"],
      "env": {
        "NSMBL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Replace**: `your_api_key_here` with your actual NSMBL API key from [app.nsmbl.io](https://app.nsmbl.io)

3. Restart Claude Desktop - the server will auto-install on first use!

> **For Developers**: If you're developing locally with `pip install -e .`, use this config instead:
> ```json
> {
>   "mcpServers": {
>     "nsmbl": {
>       "command": "/path/to/nsmbl-mcp/venv/bin/python",
>       "args": ["-m", "nsmbl_mcp.server"],
>       "env": {"NSMBL_API_KEY": "your_api_key_here"}
>     }
>   }
> }
> ```

### Verification

After setup, ask Claude: "What NSMBL tools do you have available?"

You should see 14 tools listed (2 asset tools, 5 strategy tools, 6 backtest tools).

## Quick Start

### Example 1: List Available Assets

```
User: Show me some available ETFs to invest in

Claude will use: list_assets(asset_type="etf")
```

### Example 2: Create a Simple Basket Strategy

```
User: Create a risk parity basket strategy with VTI and VEA, 
      rebalanced monthly, called "Global Diversified"

Claude will use: create_strategy with appropriate configuration
```

### Example 3: Run a Backtest

```
User: Backtest the VTI asset from 2020 to 2023 with $100,000 initial capital

Claude will use: create_backtest_and_wait for automatic completion
```

## Available Tools

### Asset Tools (2)

| Tool | Description | Cost |
|------|-------------|------|
| `list_assets` | List all tradeable stocks/ETFs with pagination and optional filtering | 1¢ |
| `get_asset` | Get details for a specific asset by symbol or ID | 1¢ |

### Strategy Tools (5)

| Tool | Description | Cost |
|------|-------------|------|
| `create_strategy` | Create systematic investment strategies (basket/tactical/ensemble/portfolio) | 1¢ |
| `list_strategies` | List all your strategies with optional type filtering | Free |
| `get_strategy` | Get complete strategy details by ID or symbol | Free |
| `update_strategy` | Update strategy name or configuration | 1¢ |
| `delete_strategy` | Delete a strategy permanently | Free |

### Backtest Tools (6)

**Raw API Tools:**

| Tool | Description | Cost |
|------|-------------|------|
| `create_backtest` | Queue a backtest (returns immediately) | 1¢ + usage |
| `get_backtest` | Get backtest status and results | Free |
| `list_backtests` | List all backtests with filtering | Free |

**Convenience Tools:**

| Tool | Description | Notes |
|------|-------------|-------|
| `create_backtest_and_wait` | Create and auto-poll until complete | Better UX |
| `wait_for_backtest` | Poll existing backtest until done | Use after create |
| `check_backtest_status` | Quick status check | Lightweight |

## Usage Examples

### Creating Different Strategy Types

#### Basket Strategy (Risk Parity)
```
Create a risk parity basket with VTI, VEA, and AGG, 
monthly rebalancing, 252-day lookback
```

#### Tactical Strategy (Momentum)
```
Create a momentum tactical strategy that selects top 3 
performers from VTI, VEA, VWO, EEM with 60-day momentum, 
equal weight allocation, monthly rebalancing
```

#### Ensemble Strategy
```
Create an ensemble combining my "Global Diversified" and 
"Tech Momentum" strategies with equal weight allocation
```

### Working with Backtests

#### Immediate Return (Manual Polling)
```
User: Create a backtest for VTI from 2020-01-01 to 2023-12-31
Claude: Uses create_backtest, returns backtest_id immediately

User: Check status of that backtest
Claude: Uses get_backtest to poll status
```

#### Auto-Wait (Better UX)
```
User: Run a complete backtest for my "Global Diversified" strategy
Claude: Uses create_backtest_and_wait, waits up to 5 minutes for completion
```

### Handling Errors

The MCP server provides clear, actionable error messages:

- **401 Errors**: Check your API key in .env
- **402 Errors**: Add credits at app.nsmbl.io
- **422 Errors**: Validation failed - check parameters
- **429 Errors**: Rate limit - wait before retrying
- **Timeouts**: Use wait_for_backtest with longer timeout

## Updating

### For Users (uvx)

Updates are **automatic**! Every time you restart your MCP client (like Claude Desktop), `uvx` checks for the latest version and updates if needed.

To force an immediate update:
```bash
uvx --force nsmbl-mcp --version
```

### For Developers (editable install)

When you pull updates from GitHub, the changes are **immediately active** thanks to editable mode:

```bash
# Pull latest changes
git pull origin main

# That's it! Just restart your MCP client to reload
```

**For Claude Desktop:**
1. Quit Claude Desktop completely (`Cmd+Q` on Mac)
2. Reopen Claude Desktop
3. Your updated MCP server is now active

> **Why this works**: The `-e` flag in `pip install -e .` creates a symbolic link to your source code rather than copying files. Any changes to the source are automatically picked up - no reinstallation needed!

### How Auto-Publishing Works

- Every commit to `main` is automatically published to PyPI via GitHub Actions
- Users with `uvx` get updates automatically on next MCP client restart
- Version numbers are derived from git history (e.g., `0.1.0.dev123+abc1234`)
- Tagged releases get clean version numbers (e.g., `0.1.0`)

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NSMBL_API_KEY` | Yes | - | Your NSMBL API key |
| `NSMBL_API_BASE_URL` | No | `https://api.nsmbl.io/api/v1` | API endpoint |
| `NSMBL_REQUEST_TIMEOUT` | No | `30` | Request timeout (seconds) |
| `NSMBL_BACKTEST_POLL_INTERVAL` | No | `5` | Polling interval (seconds) |
| `NSMBL_BACKTEST_DEFAULT_TIMEOUT` | No | `300` | Max wait time for backtests (seconds) |

### Optional JSON Config

Create `~/.nsmbl/mcp-config.json` for additional preferences:

```json
{
  "request_timeout": 60,
  "backtest_poll_interval": 3,
  "backtest_default_timeout": 600
}
```

## Troubleshooting

### "Missing required environment variable: NSMBL_API_KEY"

**Solution**: Ensure your `.env` file exists and contains your API key:
```bash
NSMBL_API_KEY=your_actual_key_here
```

### "Authentication failed"

**Solution**: Verify your API key is correct at [app.nsmbl.io](https://app.nsmbl.io)

### "Insufficient funds"

**Solution**: Add credits to your NSMBL account at [app.nsmbl.io](https://app.nsmbl.io)

### "Rate limit exceeded"

**Solution**: Wait 60 seconds before retrying. Backtest endpoint has a 10/minute rate limit.

### "Backtest timeout"

**Solution**: Complex strategies take longer. Use `wait_for_backtest` with a longer timeout:
- Asset backtests: usually < 30 seconds
- Basket strategies: usually < 60 seconds  
- Tactical/Ensemble/Portfolio: may take 2-5 minutes

### Network or connection errors

**Solution**: Check your internet connection and verify `NSMBL_API_BASE_URL` is correct.

### Changes not reflected after git pull

**Solution**: 
1. Verify you installed with `-e` flag: `pip show nsmbl-mcp` should show your source directory location
2. If not installed in editable mode, reinstall: `pip install -e .`
3. Always restart your MCP client (e.g., Claude Desktop) after pulling changes

### "spawn uvx ENOENT" or "uvx not found" in Claude Desktop

**Problem**: Claude Desktop can't find the `uvx` command even though it works in your terminal.

**Solution**: 
- **macOS**: Reinstall `uv` via Homebrew (recommended):
  ```bash
  brew install uv
  ```
  Homebrew installs to `/opt/homebrew/bin` which is in Claude Desktop's PATH.

- **If you installed via curl script**: Create a symlink to a system PATH location:
  ```bash
  sudo ln -s ~/.local/bin/uvx /usr/local/bin/uvx
  ```

- **Alternative**: Use the full path in your config:
  ```json
  {
    "command": "/Users/YOUR_USERNAME/.local/bin/uvx",
    "args": ["nsmbl-mcp"]
  }
  ```

## Billing Notes

### Charged Operations (1¢ each)

- `list_assets` - Market data lookup
- `get_asset` - Market data lookup
- `create_strategy` - Strategy creation
- `update_strategy` - Strategy modification
- `create_backtest` - Backtest creation (+ projected usage based on complexity)

### Free Operations

- `list_strategies` - Read your own data
- `get_strategy` - Read your own data
- `delete_strategy` - Resource cleanup
- `get_backtest` - Read results (designed for polling)
- `list_backtests` - Read your own data
- All convenience tools use free polling internally

### Projected Usage for Backtests

When you create a backtest, NSMBL pre-charges projected usage based on complexity:

- **Asset backtests**: 60¢
- **Basket strategies**: $1.20
- **Tactical strategies**: $1.80
- **Ensemble strategies**: $2.40
- **Portfolio strategies**: $3.00

Actual usage is charged when the backtest completes. If it costs less, you're refunded the difference.

## Links

- **NSMBL Dashboard**: [app.nsmbl.io](https://app.nsmbl.io)
- **NSMBL API Documentation**: [docs.nsmbl.io](https://docs.nsmbl.io)
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Get Support**: support@nsmbl.io

## License

MIT License - see LICENSE file for details

---

Built with ❤️ for the AI-powered investment community

