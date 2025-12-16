# Testing Guide for MCP Schema Improvements

This guide helps you verify that the schema improvements successfully prevent the issues encountered during testing.

## Setup

1. **Restart the MCP Server** (if running in development mode):
   ```bash
   conda activate nsmbl-mcp
   python -m nsmbl_mcp.server
   ```

2. **Restart Claude Desktop completely**:
   - Quit Claude Desktop (`Cmd+Q` on Mac)
   - Reopen Claude Desktop
   - The updated tool schemas will be loaded

## Original Failing Example

This was the request that Claude Desktop tried to make, which failed:

```json
{
  "strategy_data": {
    "strategy_type": "basket",
    "strategy_name": "MAG7 + SPXU Risk Parity (Daily)",
    "strategy_symbol": "mag7-rp-daily",
    "strategy_config": {
      "universe": {
        "type": "static",
        "assets": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "SPXU"]
      },
      "allocation_model": {
        "type": "risk_parity"
      },
      "rebalancing_model": {
        "type": "periodic",
        "frequency": "daily"
      }
    }
  }
}
```

### Issues with the Original Request

1. ❌ `universe` was an object with `type` and `assets` instead of an array
2. ❌ `allocation_model` used `type` instead of `model_name`
3. ❌ `allocation_model` missing `model_params` object
4. ❌ `rebalancing_model` used `type` instead of `model_name`
5. ❌ `rebalancing_model` used `"periodic"` instead of `"calendar_based"`
6. ❌ `rebalancing_model` missing `model_params` object structure

## Expected Correct Output

After the improvements, Claude Desktop should generate this structure:

```json
{
  "strategy_data": {
    "strategy_type": "basket",
    "strategy_name": "MAG7 + SPXU Risk Parity (Daily)",
    "strategy_symbol": "mag7-rp-daily",
    "strategy_config": {
      "universe": [
        {"asset_symbol": "AAPL"},
        {"asset_symbol": "MSFT"},
        {"asset_symbol": "GOOGL"},
        {"asset_symbol": "AMZN"},
        {"asset_symbol": "NVDA"},
        {"asset_symbol": "META"},
        {"asset_symbol": "TSLA"},
        {"asset_symbol": "SPXU"}
      ],
      "allocation_model": {
        "model_name": "risk_parity",
        "model_params": {
          "lookback_days": 252
        }
      },
      "rebalancing_model": {
        "model_name": "calendar_based",
        "model_params": {
          "frequency": "daily"
        }
      }
    }
  }
}
```

## Test Cases

### Test Case 1: Basic Basket Strategy

**Prompt to Claude:**
> Create a basket strategy called "MAG7 + SPXU Risk Parity (Daily)" with ticker mag7-rp-daily containing AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, and SPXU. Use risk parity allocation and rebalance daily.

**Expected Behavior:**
- ✅ Claude should use `create_strategy` tool
- ✅ Structure should match the "Expected Correct Output" above
- ✅ API call should succeed (or fail with API-specific error, not schema error)

### Test Case 2: Tactical Strategy with Momentum

**Prompt to Claude:**
> Create a momentum tactical strategy that selects the top 3 performers from SPY, QQQ, IWM, and EFA. Use 60-day momentum, equal weight the selected assets, and rebalance monthly.

**Expected Structure:**
```json
{
  "strategy_type": "tactical",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "SPY"},
      {"asset_symbol": "QQQ"},
      {"asset_symbol": "IWM"},
      {"asset_symbol": "EFA"}
    ],
    "tactical_model": {
      "model_name": "momentum",
      "model_params": {
        "lookback_days": 60,
        "n_positions": 3
      }
    },
    "allocation_model": {
      "model_name": "equal_weight",
      "model_params": {}
    },
    "rebalancing_model": {
      "model_name": "calendar_based",
      "model_params": {
        "frequency": "monthly"
      }
    }
  }
}
```

**Expected Behavior:**
- ✅ Claude should include `tactical_model` (not forget it)
- ✅ Should use `"momentum"` as `model_name`
- ✅ Should use `"calendar_based"` not `"periodic"`

### Test Case 3: Equal Weight with Weekly Rebalancing

**Prompt to Claude:**
> Create an equal weight basket with VTI, VEA, VWO, and AGG, rebalanced weekly.

**Expected Structure:**
```json
{
  "strategy_type": "basket",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "VTI"},
      {"asset_symbol": "VEA"},
      {"asset_symbol": "VWO"},
      {"asset_symbol": "AGG"}
    ],
    "allocation_model": {
      "model_name": "equal_weight",
      "model_params": {}
    },
    "rebalancing_model": {
      "model_name": "calendar_based",
      "model_params": {
        "frequency": "weekly"
      }
    }
  }
}
```

**Expected Behavior:**
- ✅ Should use proper array structure for universe
- ✅ Should include empty `model_params: {}` for equal_weight
- ✅ Should use `"weekly"` frequency

### Test Case 4: Fixed Weight Portfolio

**Prompt to Claude:**
> Create a 60/40 portfolio with 60% VTI and 40% AGG, rebalanced when drift exceeds 5%.

**Expected Structure:**
```json
{
  "strategy_type": "basket",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "VTI"},
      {"asset_symbol": "AGG"}
    ],
    "allocation_model": {
      "model_name": "fixed_weight",
      "model_params": {
        "weights": [0.6, 0.4]
      }
    },
    "rebalancing_model": {
      "model_name": "drift_based",
      "model_params": {
        "threshold": 0.05
      }
    }
  }
}
```

**Expected Behavior:**
- ✅ Should use `"fixed_weight"` allocation
- ✅ Should include weights array summing to 1.0
- ✅ Should use `"drift_based"` rebalancing
- ✅ Should use threshold as decimal (0.05 not 5)

## Validation Testing

The client-side validation should catch and report these errors clearly:

### Invalid Test 1: Using "type" instead of "model_name"

If you manually test with invalid structure (via API testing tool), validation should catch it:

```json
{
  "allocation_model": {
    "type": "risk_parity"  // ❌ Should be "model_name"
  }
}
```

**Expected Error:**
```
❌ Validation Error in strategy_data:

❌ Common mistake detected! Use 'model_name' not 'type' in allocation_model. 
Try: {'model_name': 'risk_parity', 'model_params': {}}

💡 See tool description for correct structure and examples.
```

### Invalid Test 2: Wrong universe structure

```json
{
  "universe": {
    "type": "static",
    "assets": ["AAPL", "MSFT"]
  }
}
```

**Expected Error:**
```
❌ Validation Error in strategy_data:

❌ Common mistake detected! Don't use {'type': 'static', 'assets': [...]} structure. 
Instead use: [{'asset_symbol': 'AAPL'}, {'asset_symbol': 'MSFT'}]

💡 See tool description for correct structure and examples.
```

## Verification Checklist

After testing, verify:

- [ ] Claude Desktop successfully creates strategies on first attempt
- [ ] No more "type" instead of "model_name" errors
- [ ] No more "periodic" instead of "calendar_based" errors  
- [ ] No more incorrect universe structure errors
- [ ] Validation catches common mistakes with helpful messages
- [ ] Tool descriptions in Claude Desktop show the examples and valid values
- [ ] API calls succeed (or fail with legitimate API errors, not schema errors)

## Checking Tool Descriptions in Claude

To verify Claude has the updated descriptions:

**Prompt to Claude:**
> What are the valid allocation model names I can use?

**Expected Response:**
Claude should list: `risk_parity`, `equal_weight`, `fixed_weight`, `inverse_volatility`

**Prompt to Claude:**
> Show me an example of a correct basket strategy structure.

**Expected Response:**
Claude should show an example with proper structure including `model_name`, `model_params`, array universe, etc.

## Troubleshooting

### Issue: Claude still uses old structure

**Solution:** 
1. Completely quit Claude Desktop (`Cmd+Q`)
2. Wait 5 seconds
3. Reopen Claude Desktop
4. Try again

### Issue: Validation not catching errors

**Solution:**
1. Check that validation.py is being imported correctly
2. Verify create_strategy function calls validate_strategy_data
3. Check Python environment has latest code

### Issue: Schema changes not reflected

**Solution:**
1. Verify strategies.py imports from utils/schemas.py
2. Check that get_strategy_data_schema() is being called in CREATE_STRATEGY_TOOL
3. Restart MCP server if running in development

## Success Criteria

The improvements are successful if:

1. ✅ Claude Desktop generates correct structure on first attempt
2. ✅ No trial-and-error needed to create strategies
3. ✅ Clear error messages if mistakes are made
4. ✅ Tool descriptions provide sufficient guidance
5. ✅ All test cases pass with correct structure
6. ✅ Validation catches the original failing patterns

## Next Steps After Testing

If testing is successful:
1. Document any remaining edge cases
2. Consider adding more examples for ensemble/portfolio strategies
3. Monitor real-world usage for new patterns
4. Update validation rules if new mistakes are discovered

If issues are found:
1. Document the specific issue
2. Check which validation rule or schema needs adjustment
3. Update schemas.py, validation.py, or tool descriptions as needed
4. Re-test after fixes

