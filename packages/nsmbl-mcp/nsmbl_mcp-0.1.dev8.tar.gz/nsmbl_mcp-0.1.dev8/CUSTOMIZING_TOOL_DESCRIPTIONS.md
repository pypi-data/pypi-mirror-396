# Customizing MCP Tool Descriptions

## How LLMs Learn About Your Tools

When Claude (or any LLM) connects to your MCP server, it reads the **tool descriptions** you define in the code. These descriptions are the LLM's only way to understand what each tool does.

## Where Tool Descriptions Live

Tool descriptions are defined in three files:

### 1. Asset Tools
**File**: `src/nsmbl_mcp/tools/assets.py`

Look for:
- `LIST_ASSETS_TOOL = Tool(...)`
- `GET_ASSET_TOOL = Tool(...)`

The `description` field in each `Tool()` object is what the LLM reads.

### 2. Strategy Tools
**File**: `src/nsmbl_mcp/tools/strategies.py`

Look for:
- `CREATE_STRATEGY_TOOL = Tool(...)`
- `LIST_STRATEGIES_TOOL = Tool(...)`
- `GET_STRATEGY_TOOL = Tool(...)`
- `UPDATE_STRATEGY_TOOL = Tool(...)`
- `DELETE_STRATEGY_TOOL = Tool(...)`

### 3. Backtest Tools
**File**: `src/nsmbl_mcp/tools/backtests.py`

Look for:
- `CREATE_BACKTEST_TOOL = Tool(...)`
- `GET_BACKTEST_TOOL = Tool(...)`
- `LIST_BACKTESTS_TOOL = Tool(...)`
- `CREATE_BACKTEST_AND_WAIT_TOOL = Tool(...)`
- `WAIT_FOR_BACKTEST_TOOL = Tool(...)`
- `CHECK_BACKTEST_STATUS_TOOL = Tool(...)`

## Example: Good vs Better Description

### Before (Generic)
```python
CREATE_STRATEGY_TOOL = Tool(
    name="create_strategy",
    description=(
        "Create a systematic investment strategy (basket, tactical, ensemble, or portfolio). "
        "Requires strategy_type, strategy_name, and complete strategy_config."
    ),
)
```

### After (Specific & Educational)
```python
CREATE_STRATEGY_TOOL = Tool(
    name="create_strategy",
    description=(
        "Create a systematic investment strategy. Four types available:\n"
        "• Basket: Static allocation across multiple assets with periodic rebalancing\n"
        "• Tactical: Dynamic strategies that select subsets of assets based on signals\n"
        "• Ensemble: Combines multiple existing strategies with sophisticated allocation\n"
        "• Portfolio: Highest-level strategy type that can contain assets AND all other "
        "strategy types, managing position sizing across everything\n\n"
        "Requires strategy_type, strategy_name, and complete strategy_config."
    ),
)
```

## Best Practices for Tool Descriptions

### 1. Be Specific
❌ "Create a strategy"
✅ "Create a systematic investment strategy with custom allocation and rebalancing rules"

### 2. Explain Context
❌ "List strategies"
✅ "List all your existing strategies with configurations - useful for reviewing what you've already built"

### 3. Clarify Hierarchies
❌ "Portfolio strategy"
✅ "Portfolio: Highest-level strategy type that can contain everything (assets + other strategies)"

### 4. Note Costs
Always include billing information:
✅ "Charged 1¢ per call"
✅ "Free (no charge) - designed for polling"

### 5. Explain Use Cases
❌ "Get backtest"
✅ "Get backtest status and results. Use this to poll for completion after creating a backtest. Free (no charge)."

## How to Update Descriptions

### Step 1: Edit the Tool File

Find the appropriate file and locate the `Tool()` definition.

### Step 2: Update the Description

Modify the `description` parameter with better text.

### Step 3: Test Locally (Optional)

```bash
conda activate nsmbl-mcp
python -m nsmbl_mcp.server
```

Press Ctrl+C to verify it starts without errors.

### Step 4: Restart Claude Desktop

For changes to take effect in Claude:
1. Completely quit Claude Desktop (`Cmd+Q`)
2. Reopen Claude Desktop
3. Ask Claude: "What NSMBL tools do you have?"
4. Claude will now use your updated descriptions

## Field-Level Descriptions

You can also improve descriptions in `inputSchema`:

```python
"strategy_type": {
    "type": "string",
    "enum": ["basket", "tactical", "ensemble", "portfolio"],
    "description": (
        "Strategy type: 'basket' (static allocation), "
        "'tactical' (signal-driven selection), "
        "'ensemble' (combines strategies), "
        "'portfolio' (top-level container for everything)"
    )
}
```

## Tips

1. **Think like a teacher**: Explain concepts the LLM might not know
2. **Use examples**: "e.g., 'VTI', 'AAPL'" helps clarify formats
3. **Explain relationships**: "Portfolio strategies can contain basket strategies"
4. **Note limitations**: "Max 10 concurrent backtests", "Rate limit: 10/minute"
5. **Guide workflows**: "Use list_assets first to see available options"

## Testing Your Changes

After updating descriptions, test with Claude:

```
User: Explain the different strategy types available

Claude: [Should now use your improved descriptions]
```

Compare Claude's explanation to your description text - they should align closely!

