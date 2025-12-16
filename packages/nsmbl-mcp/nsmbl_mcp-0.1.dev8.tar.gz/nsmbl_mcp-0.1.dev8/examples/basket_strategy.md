# Creating Basket Strategies

Basket strategies allocate capital across multiple assets using various weighting schemes without tactical rebalancing signals.

## ⚠️ Common Pitfalls to Avoid

### Incorrect Universe Structure
❌ **WRONG** - Using a nested object structure:
```json
"universe": {
  "type": "static",
  "assets": ["AAPL", "MSFT", "GOOGL"]
}
```

✅ **CORRECT** - Use an array of objects:
```json
"universe": [
  {"asset_symbol": "AAPL"},
  {"asset_symbol": "MSFT"},
  {"asset_symbol": "GOOGL"}
]
```

### Incorrect Model Structure
❌ **WRONG** - Using "type" instead of "model_name":
```json
"allocation_model": {
  "type": "risk_parity"
}
```

✅ **CORRECT** - Use "model_name" + "model_params":
```json
"allocation_model": {
  "model_name": "risk_parity",
  "model_params": {"lookback_days": 252}
}
```

### Incorrect Rebalancing Model Name
❌ **WRONG** - Using "periodic":
```json
"rebalancing_model": {
  "type": "periodic",
  "frequency": "daily"
}
```

✅ **CORRECT** - Use "calendar_based" with proper structure:
```json
"rebalancing_model": {
  "model_name": "calendar_based",
  "model_params": {"frequency": "daily"}
}
```

## Risk Parity Basket

Allocates based on inverse volatility (equal risk contribution):

```
User: Create a risk parity basket strategy with VTI, VEA, and AGG. 
      Use a 252-day lookback for risk calculation and rebalance monthly. 
      Call it "Global Risk Parity"

Claude: Will use create_strategy with:
{
  "strategy_type": "basket",
  "strategy_name": "Global Risk Parity",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "VTI"},
      {"asset_symbol": "VEA"},
      {"asset_symbol": "AGG"}
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
        "frequency": "monthly"
      }
    }
  }
}
```

## Equal Weight Basket

Simple equal allocation across all assets:

```
User: Create an equal weight basket with VTI, VEA, VWO, and EEM, 
      rebalanced quarterly. Name it "Equal Global Equity"

Claude: Will use create_strategy with equal_weight allocation model
```

## Fixed Weight Basket

Custom allocation percentages:

```
User: Create a basket with 60% VTI, 30% VEA, and 10% AGG, 
      rebalanced monthly using drift-based 5% threshold. 
      Call it "60/30/10 Portfolio"

Claude: Will use create_strategy with:
{
  "allocation_model": {
    "model_name": "fixed_weight",
    "model_params": {
      "weights": [0.6, 0.3, 0.1]
    }
  },
  "rebalancing_model": {
    "model_name": "drift_based",
    "model_params": {
      "threshold": 0.05
    }
  }
}
```

## Inverse Volatility Basket

Allocates inversely to volatility (less volatile gets more weight):

```
User: Create an inverse volatility basket with tech ETFs: 
      QQQ, VGT, and SOXX. Use 126-day lookback and weekly rebalancing. 
      Call it "Tech Defensive"

Claude: Will use inverse_volatility allocation model with 126 lookback_days
```

## Tips

- **Risk Parity**: Best for diversification across different asset classes
- **Equal Weight**: Simplest approach, good for similar assets
- **Fixed Weight**: Use when you have specific allocation targets
- **Inverse Volatility**: Reduces portfolio volatility by tilting to stable assets
- **Lookback Period**: 252 days = 1 year, 126 days = 6 months, 21 days = 1 month
- **Rebalancing**: Monthly is common; quarterly for lower turnover; daily for active management

