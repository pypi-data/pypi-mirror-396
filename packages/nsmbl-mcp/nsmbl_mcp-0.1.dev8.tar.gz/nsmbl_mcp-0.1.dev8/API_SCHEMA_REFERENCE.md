# NSMBL MCP API Schema Reference

Complete JSON schema reference for all NSMBL MCP tools. Use this as a reference when constructing API calls through the MCP server.

## Our Schema Philosophy

### Detailed But Not Complex

Our MCP tool schemas are:
- ✅ **Detailed**: All enums, nested properties, descriptions, constraints (LLMs need this!)
- ✅ **Flat**: No `oneOf` discriminated unions (prevents massive error dumps)
- ✅ **Direct**: Tool parameters map 1:1 to API parameters (no wrappers)

### Why No `oneOf`?

Complex `oneOf` validation in JSON Schema can trigger error messages containing thousands of tokens of schema definitions. Instead:
- **JSON Schema**: Provides type information and enums
- **Tool Descriptions**: Provide examples and guidance
- **Python Validation**: Enforces business rules with concise errors

This approach:
- ✅ Prevents 5000+ token error dumps
- ✅ Gives LLMs all the information they need
- ✅ Provides helpful, actionable error messages
- ✅ Keeps context windows clean

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Universe References](#universe-references)
3. [Allocation Models](#allocation-models)
4. [Rebalancing Models](#rebalancing-models)
5. [Tactical Models](#tactical-models)
6. [Strategy Configurations](#strategy-configurations)
7. [Complete Examples](#complete-examples)
8. [Common Mistakes](#common-mistakes)

---

## Core Concepts

### Model Structure Pattern

All models in NSMBL API follow a consistent two-field pattern:

```json
{
  "model_name": "specific_model_type",
  "model_params": {
    // Model-specific parameters
  }
}
```

**CRITICAL**: Always use `model_name` (not `type`!) and always include `model_params` (even if empty `{}`).

---

## Universe References

A universe is an **array** of references to assets or strategies. Each reference is an object with exactly ONE of the following identifiers:

### Schema

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "oneOf": [
      {"required": ["asset_symbol"]},
      {"required": ["asset_id"]},
      {"required": ["strategy_symbol"]},
      {"required": ["strategy_id"]}
    ]
  },
  "minItems": 1
}
```

### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `asset_symbol` | string | Asset ticker symbol | `"AAPL"`, `"VTI"`, `"SPY"` |
| `asset_id` | string | Asset UUID with `as-` prefix | `"as-12345678-1234-5678-9abc-123456789012"` |
| `strategy_symbol` | string | Strategy identifier (lowercase, hyphens) | `"my-risk-parity-basket"` |
| `strategy_id` | string | Strategy UUID with prefix (`sb-`, `st-`, `se-`, `sp-`) | `"sb-12345678-1234-5678-9abc-123456789012"` |

### Examples

```json
// Using asset symbols (most common)
"universe": [
  {"asset_symbol": "AAPL"},
  {"asset_symbol": "MSFT"},
  {"asset_symbol": "GOOGL"}
]

// Using strategy symbols
"universe": [
  {"strategy_symbol": "tech-basket"},
  {"strategy_symbol": "defensive-basket"}
]

// Mixed (assets and strategies)
"universe": [
  {"asset_symbol": "VTI"},
  {"strategy_symbol": "my-tactical-strategy"}
]
```

---

## Allocation Models

Allocation models determine how capital is distributed across universe components.

### Valid Model Names

- `risk_parity`
- `equal_weight`
- `fixed_weight`
- `inverse_volatility`

### Risk Parity

Allocates based on inverse volatility for equal risk contribution across assets.

```json
{
  "model_name": "risk_parity",
  "model_params": {
    "lookback_days": 252  // Optional, default: 252, range: 5-1000
  }
}
```

**Parameters:**
- `lookback_days` (integer, optional): Days for risk calculation (5-1000, default: 252)

### Equal Weight

Distributes capital equally across all universe components.

```json
{
  "model_name": "equal_weight",
  "model_params": {}
}
```

**Parameters:** None

### Fixed Weight

Uses custom specified weights that must sum to 1.0.

```json
{
  "model_name": "fixed_weight",
  "model_params": {
    "weights": [0.5, 0.3, 0.2]  // Required, must sum to 1.0
  }
}
```

**Parameters:**
- `weights` (array of floats, **required**): Weights for each universe component, must sum to 1.0

### Inverse Volatility

Weights inversely to volatility (lower volatility = higher weight).

```json
{
  "model_name": "inverse_volatility",
  "model_params": {
    "lookback_days": 252  // Optional, default: 252, range: 5-1000
  }
}
```

**Parameters:**
- `lookback_days` (integer, optional): Days for volatility calculation (5-1000, default: 252)

---

## Rebalancing Models

Rebalancing models determine when to rebalance the portfolio.

### Valid Model Names

- `calendar_based`
- `drift_based`

### Calendar Based

Rebalances on a fixed schedule.

```json
{
  "model_name": "calendar_based",
  "model_params": {
    "frequency": "monthly"  // Optional, default: "monthly"
  }
}
```

**Parameters:**
- `frequency` (string, optional): One of `"daily"`, `"weekly"`, `"monthly"`, `"quarterly"` (default: `"monthly"`)

### Drift Based

Rebalances when allocation drifts beyond threshold.

```json
{
  "model_name": "drift_based",
  "model_params": {
    "threshold": 0.05  // Optional, default: 0.05 (5% drift)
  }
}
```

**Parameters:**
- `threshold` (float, optional): Drift threshold as decimal (0.01-0.5, default: 0.05)
  - `0.05` = 5% drift
  - `0.10` = 10% drift

---

## Tactical Models

Tactical models generate signals for asset selection (tactical strategies only).

### Valid Model Names

- `momentum`
- `contrarian`

### Momentum

Selects top-performing assets based on recent returns.

```json
{
  "model_name": "momentum",
  "model_params": {
    "lookback_days": 21,  // Optional, default: 21, range: 5-1000
    "n_positions": 3      // Optional, default: 3, range: 1-100
  }
}
```

**Parameters:**
- `lookback_days` (integer, optional): Days for performance calculation (5-1000, default: 21)
- `n_positions` (integer, optional): Number of top performers to select (1-100, default: 3)

### Contrarian

Selects worst-performing assets (mean reversion strategy).

```json
{
  "model_name": "contrarian",
  "model_params": {
    "lookback_days": 21,  // Optional, default: 21, range: 5-1000
    "n_positions": 3      // Optional, default: 3, range: 1-100
  }
}
```

**Parameters:**
- `lookback_days` (integer, optional): Days for performance calculation (5-1000, default: 21)
- `n_positions` (integer, optional): Number of worst performers to select (1-100, default: 3)

---

## Strategy Configurations

### Valid Strategy Types

- `basket` - Static allocation strategies
- `tactical` - Signal-driven selection strategies
- `ensemble` - Multi-strategy combinations (min 2 items)
- `portfolio` - Top-level investment portfolios

### Basket Configuration

Static allocation across multiple assets.

**Required Fields:**
- `universe` (array, min 1 item)
- `allocation_model` (object)
- `rebalancing_model` (object)

```json
{
  "strategy_type": "basket",
  "strategy_name": "My Basket Strategy",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "AAPL"},
      {"asset_symbol": "MSFT"}
    ],
    "allocation_model": {
      "model_name": "equal_weight",
      "model_params": {}
    },
    "rebalancing_model": {
      "model_name": "calendar_based",
      "model_params": {"frequency": "monthly"}
    }
  }
}
```

### Tactical Configuration

Signal-driven asset selection strategies.

**Required Fields:**
- `universe` (array, min 1 item)
- `tactical_model` (object) - **REQUIRED for tactical strategies!**
- `allocation_model` (object)
- `rebalancing_model` (object)

```json
{
  "strategy_type": "tactical",
  "strategy_name": "My Momentum Strategy",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "SPY"},
      {"asset_symbol": "QQQ"},
      {"asset_symbol": "IWM"}
    ],
    "tactical_model": {
      "model_name": "momentum",
      "model_params": {
        "lookback_days": 60,
        "n_positions": 2
      }
    },
    "allocation_model": {
      "model_name": "equal_weight",
      "model_params": {}
    },
    "rebalancing_model": {
      "model_name": "calendar_based",
      "model_params": {"frequency": "weekly"}
    }
  }
}
```

### Ensemble Configuration

Combines multiple strategies and/or assets.

**Required Fields:**
- `universe` (array, **min 2 items**)
- `allocation_model` (object)
- `rebalancing_model` (object)

```json
{
  "strategy_type": "ensemble",
  "strategy_name": "My Ensemble Strategy",
  "strategy_config": {
    "universe": [
      {"strategy_symbol": "tech-basket"},
      {"strategy_symbol": "defensive-basket"}
    ],
    "allocation_model": {
      "model_name": "risk_parity",
      "model_params": {"lookback_days": 252}
    },
    "rebalancing_model": {
      "model_name": "calendar_based",
      "model_params": {"frequency": "monthly"}
    }
  }
}
```

### Portfolio Configuration

Top-level container for assets and all strategy types.

**Required Fields:**
- `universe` (array, min 1 item)
- `allocation_model` (object)
- `rebalancing_model` (object)

```json
{
  "strategy_type": "portfolio",
  "strategy_name": "My Complete Portfolio",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "VTI"},
      {"strategy_symbol": "my-tactical-strategy"},
      {"strategy_symbol": "my-defensive-basket"}
    ],
    "allocation_model": {
      "model_name": "fixed_weight",
      "model_params": {
        "weights": [0.4, 0.3, 0.3]
      }
    },
    "rebalancing_model": {
      "model_name": "drift_based",
      "model_params": {"threshold": 0.05}
    }
  }
}
```

---

## Complete Examples

### Example 1: Simple Equal Weight Basket

```json
{
  "strategy_type": "basket",
  "strategy_name": "MAG7 Equal Weight",
  "strategy_symbol": "mag7-equal",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "AAPL"},
      {"asset_symbol": "MSFT"},
      {"asset_symbol": "GOOGL"},
      {"asset_symbol": "AMZN"},
      {"asset_symbol": "NVDA"},
      {"asset_symbol": "META"},
      {"asset_symbol": "TSLA"}
    ],
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

### Example 2: Risk Parity with Daily Rebalancing

```json
{
  "strategy_type": "basket",
  "strategy_name": "Global Risk Parity Daily",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "VTI"},
      {"asset_symbol": "VEA"},
      {"asset_symbol": "VWO"},
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
        "frequency": "daily"
      }
    }
  }
}
```

### Example 3: Momentum Tactical Strategy

```json
{
  "strategy_type": "tactical",
  "strategy_name": "Sector Momentum Top 3",
  "strategy_config": {
    "universe": [
      {"asset_symbol": "XLK"},
      {"asset_symbol": "XLV"},
      {"asset_symbol": "XLF"},
      {"asset_symbol": "XLE"},
      {"asset_symbol": "XLI"},
      {"asset_symbol": "XLY"},
      {"asset_symbol": "XLP"},
      {"asset_symbol": "XLU"}
    ],
    "tactical_model": {
      "model_name": "momentum",
      "model_params": {
        "lookback_days": 90,
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

### Example 4: Fixed Weight Portfolio

```json
{
  "strategy_type": "portfolio",
  "strategy_name": "60/40 Portfolio",
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

---

## Common Mistakes

### ❌ Mistake 1: Using "type" instead of "model_name"

**WRONG:**
```json
"allocation_model": {
  "type": "risk_parity"
}
```

**CORRECT:**
```json
"allocation_model": {
  "model_name": "risk_parity",
  "model_params": {"lookback_days": 252}
}
```

### ❌ Mistake 2: Using nested object for universe

**WRONG:**
```json
"universe": {
  "type": "static",
  "assets": ["AAPL", "MSFT", "GOOGL"]
}
```

**CORRECT:**
```json
"universe": [
  {"asset_symbol": "AAPL"},
  {"asset_symbol": "MSFT"},
  {"asset_symbol": "GOOGL"}
]
```

### ❌ Mistake 3: Using "periodic" instead of "calendar_based"

**WRONG:**
```json
"rebalancing_model": {
  "model_name": "periodic",
  "model_params": {"frequency": "daily"}
}
```

**CORRECT:**
```json
"rebalancing_model": {
  "model_name": "calendar_based",
  "model_params": {"frequency": "daily"}
}
```

### ❌ Mistake 4: Using "mean_reversion" instead of "contrarian"

**WRONG:**
```json
"tactical_model": {
  "model_name": "mean_reversion"
}
```

**CORRECT:**
```json
"tactical_model": {
  "model_name": "contrarian",
  "model_params": {"lookback_days": 21, "n_positions": 3}
}
```

### ❌ Mistake 5: Forgetting tactical_model in tactical strategies

**WRONG:**
```json
{
  "strategy_type": "tactical",
  "strategy_config": {
    "universe": [...],
    "allocation_model": {...},
    "rebalancing_model": {...}
    // Missing tactical_model!
  }
}
```

**CORRECT:**
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

### ❌ Mistake 6: Missing model_params

**WRONG:**
```json
"allocation_model": {
  "model_name": "equal_weight"
  // Missing model_params!
}
```

**CORRECT:**
```json
"allocation_model": {
  "model_name": "equal_weight",
  "model_params": {}
}
```

---

## Quick Reference Tables

### Allocation Models

| model_name | Required Params | Optional Params | Description |
|------------|----------------|-----------------|-------------|
| `risk_parity` | None | `lookback_days` (252) | Equal risk contribution |
| `equal_weight` | None | None | Equal capital allocation |
| `fixed_weight` | `weights` (array) | None | Custom weights |
| `inverse_volatility` | None | `lookback_days` (252) | Inverse to volatility |

### Rebalancing Models

| model_name | Required Params | Optional Params | Description |
|------------|----------------|-----------------|-------------|
| `calendar_based` | None | `frequency` ("monthly") | Fixed schedule |
| `drift_based` | None | `threshold` (0.05) | Threshold trigger |

### Tactical Models

| model_name | Required Params | Optional Params | Description |
|------------|----------------|-----------------|-------------|
| `momentum` | None | `lookback_days` (21), `n_positions` (3) | Top performers |
| `contrarian` | None | `lookback_days` (21), `n_positions` (3) | Worst performers |

### Valid Frequency Values

- `"daily"`
- `"weekly"`
- `"monthly"`
- `"quarterly"`

---

## Additional Notes

### Strategy Symbols

- Auto-generated from `strategy_name` if not provided
- Must be lowercase with hyphens only
- Pattern: `^[a-z0-9-]+$`
- Example: `"mag7-risk-parity-daily"`

### Universe Minimums

- **Basket**: 1+ items
- **Tactical**: 1+ items
- **Ensemble**: 2+ items (minimum)
- **Portfolio**: 1+ items

### Default Values

- `lookback_days`: 252 (1 year)
- `frequency`: "monthly"
- `threshold`: 0.05 (5%)
- `n_positions`: 3

### ID Prefixes

- Assets: `as-` (e.g., `as-12345678-...`)
- Basket strategies: `sb-` (e.g., `sb-12345678-...`)
- Tactical strategies: `st-` (e.g., `st-12345678-...`)
- Ensemble strategies: `se-` (e.g., `se-12345678-...`)
- Portfolio strategies: `sp-` (e.g., `sp-12345678-...`)

