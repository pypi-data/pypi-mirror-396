# JSON Schema Validation Fix

## The Problem

The complex `oneOf` discriminated union in the schema was causing validation errors. When Claude sent the request, JSON Schema tried to validate it and got confused because multiple branches matched (basket, tactical, ensemble, portfolio all looked valid for the same config).

Error message:
```
Input validation error: {...} is valid under each of {tactical}, {ensemble}, {portfolio}, {basket}
```

This happens when `oneOf` has multiple matching branches - it must match exactly ONE.

## The Fix

Simplified the JSON Schema in `get_strategy_data_schema()`:
- Removed complex `oneOf` with `allOf` nesting
- Made `strategy_config` accept all possible fields
- Let **client-side validation** (in `validation.py`) handle business logic

This is actually better because:
1. ✅ JSON Schema provides type information to LLMs
2. ✅ Python validation provides business rule enforcement
3. ✅ No confusing JSON Schema error messages
4. ✅ More maintainable

## What Changed

**Before (too complex):**
```python
"oneOf": [
    {"allOf": [
        {"properties": {"strategy_type": {"const": "basket"}}},
        {"properties": {"strategy_config": BASKET_CONFIG_SCHEMA}}
    ]},
    # ... more complex nesting
]
```

**After (simpler):**
```python
"strategy_config": {
    "type": "object",
    "properties": {
        "universe": {...},
        "allocation_model": {...},
        "rebalancing_model": {...},
        "tactical_model": {...}  # Optional, validated in Python
    },
    "required": ["universe", "allocation_model", "rebalancing_model"]
}
```

## Testing

After restarting Claude Desktop, try the same request:

```json
{
  "strategy_data": {
    "strategy_type": "basket",
    "strategy_name": "MAG7 + SPXU Risk Parity (Daily)",
    "strategy_symbol": "mag7-spxu-rp-daily",
    "strategy_config": {
      "universe": [
        {"asset_symbol": "META"},
        {"asset_symbol": "AAPL"},
        // ... etc
      ],
      "allocation_model": {
        "model_name": "risk_parity",
        "model_params": {"lookback_days": 252}
      },
      "rebalancing_model": {
        "model_name": "calendar_based",
        "model_params": {"frequency": "daily"}
      }
    }
  }
}
```

Should now work! ✅

## Next Steps

1. Restart Claude Desktop (`Cmd+Q`, reopen)
2. Try creating the strategy again
3. Should succeed (or give a more helpful error if there's an API issue)

