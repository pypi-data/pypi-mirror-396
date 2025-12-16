# Creating Tactical Strategies

Tactical strategies use signals to select a subset of assets from a universe based on momentum or mean reversion.

## ⚠️ Common Pitfalls to Avoid

### Missing Tactical Model
❌ **WRONG** - Tactical strategies without tactical_model:
```json
{
  "strategy_type": "tactical",
  "strategy_config": {
    "universe": [...],
    "allocation_model": {...},
    "rebalancing_model": {...}
  }
}
```

✅ **CORRECT** - Tactical strategies MUST include tactical_model:
```json
{
  "strategy_type": "tactical",
  "strategy_config": {
    "universe": [...],
    "tactical_model": {
      "model_name": "momentum",
      "model_params": {"lookback_days": 60, "n_positions": 3}
    },
    "allocation_model": {...},
    "rebalancing_model": {...}
  }
}
```

### Incorrect Tactical Model Names
❌ **WRONG** - Using "mean_reversion":
```json
"tactical_model": {
  "model_name": "mean_reversion"
}
```

✅ **CORRECT** - Use "contrarian" for mean reversion:
```json
"tactical_model": {
  "model_name": "contrarian",
  "model_params": {"lookback_days": 21, "n_positions": 3}
}
```

## Momentum Strategy

Selects top-performing assets based on recent returns:

```
User: Create a momentum strategy that picks the top 3 performers 
      from VTI, VEA, VWO, EEM, and EFA. Use 60-day momentum signal, 
      equal weight the selected assets, and rebalance monthly. 
      Call it "Global Momentum Top 3"

Claude: Will use create_strategy with:
{
  "strategy_type": "tactical",
  "strategy_name": "Global Momentum Top 3",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "VTI"},
      {"asset_symbol": "VEA"},
      {"asset_symbol": "VWO"},
      {"asset_symbol": "EEM"},
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

## Contrarian Strategy

Selects worst-performing assets (mean reversion):

```
User: Create a contrarian strategy that buys the 2 worst performers 
      from sector ETFs: XLK, XLV, XLF, XLE, XLI. Use 21-day lookback, 
      risk parity allocation, and weekly rebalancing. 
      Call it "Sector Rotation Contrarian"

Claude: Will use create_strategy with:
{
  "tactical_model": {
    "model_name": "contrarian",
    "model_params": {
      "lookback_days": 21,
      "n_positions": 2
    }
  },
  "allocation_model": {
    "model_name": "risk_parity",
    "model_params": {
      "lookback_days": 252
    }
  }
}
```

## Advanced: Momentum with Risk Parity

Combines tactical selection with sophisticated allocation:

```
User: Create a momentum strategy selecting top 5 from a universe 
      of 10 global ETFs. Use 90-day momentum. Allocate selected assets 
      using risk parity with 126-day lookback. Rebalance monthly. 
      Call it "Global Momentum Risk Parity"

Claude: Combines momentum tactical_model with risk_parity allocation_model
```

## Tips

### Signal Lookback Periods

- **21 days**: Short-term signals, higher turnover
- **60 days**: Medium-term, balanced approach
- **90-126 days**: Longer-term trends, lower turnover

### Number of Positions

- **Fewer positions (2-3)**: More concentrated, higher conviction
- **More positions (5-8)**: Better diversification, lower concentration risk

### Momentum vs Contrarian

- **Momentum**: "Buy the winners" - trend following
- **Contrarian**: "Buy the losers" - mean reversion
- Momentum typically works better in trending markets
- Contrarian can work in range-bound or reverting markets

### Allocation After Selection

- **Equal Weight**: Simple, treats all selected assets the same
- **Risk Parity**: Balances risk across selected assets
- **Inverse Volatility**: Tilts to more stable of the selected assets

### Rebalancing Frequency

- **Weekly**: Most responsive to signals, higher turnover
- **Monthly**: Balanced approach, most common
- **Quarterly**: Lower turnover, longer-term approach

