# MCP Schema Improvements Summary

## Overview

This document summarizes the comprehensive improvements made to the NSMBL MCP server to prevent schema-related errors when LLMs (like Claude Desktop) attempt to create strategies.

## Problem Statement

During testing with Claude Desktop, the LLM attempted to create a strategy with invalid parameters:

```json
{
  "universe": {"type": "static", "assets": [...]},      // ❌ Wrong structure
  "allocation_model": {"type": "risk_parity"},          // ❌ Wrong field name
  "rebalancing_model": {"type": "periodic", ...}        // ❌ Invalid model_name
}
```

**Root causes:**
1. Tool schemas were too vague (`"type": "object"` with no nested structure)
2. No documentation of valid enum values
3. Missing field specifications (required vs optional)
4. Insufficient examples in tool descriptions
5. No client-side validation to catch mistakes before API calls

## Solution Implemented

### 1. Created Comprehensive Schema Module

**File:** `src/nsmbl_mcp/utils/schemas.py`

- Complete JSON Schema definitions for all backend models
- Discriminated unions using `oneOf` for model types
- Detailed field descriptions with examples
- Validation constraints (min/max, patterns, enums)
- Reusable schema components

**Key schemas:**
- `UNIVERSE_REFERENCE_SCHEMA` - Proper array of objects structure
- `ALLOCATION_MODEL_SCHEMA` - All 4 allocation models with parameters
- `REBALANCING_MODEL_SCHEMA` - Both rebalancing models
- `TACTICAL_MODEL_SCHEMA` - Both tactical models
- Complete strategy config schemas for each type

### 2. Updated Tool Definitions

**File:** `src/nsmbl_mcp/tools/strategies.py`

**CREATE_STRATEGY_TOOL improvements:**
- Uses `get_strategy_data_schema()` for complete nested structure
- Includes concrete example showing correct format
- Lists all valid enum values inline
- Explains the two-field model pattern (model_name + model_params)
- Highlights critical structure rules

**UPDATE_STRATEGY_TOOL improvements:**
- Full schema for strategy_config using oneOf
- Same guidance on valid values and structure
- References get_strategy to see current configuration

**Other tools enhanced:**
- LIST_STRATEGIES_TOOL - Better context on when to use
- GET_STRATEGY_TOOL - Explains what's returned and why it's useful
- DELETE_STRATEGY_TOOL - Warnings and use cases

### 3. Client-Side Validation

**File:** `src/nsmbl_mcp/utils/validation.py`

Validates strategy_data before API calls and provides helpful error messages:

- `validate_strategy_data()` - Main validation function
- `validate_universe()` - Catches nested object mistake
- `validate_allocation_model()` - Catches "type" vs "model_name" mistake
- `validate_rebalancing_model()` - Catches "periodic" mistake
- `validate_tactical_model()` - Validates tactical strategies

**Features:**
- Detects common mistakes and suggests corrections
- Maps common wrong values to correct ones
- User-friendly error messages with emoji indicators
- Validates weights sum to 1.0 for fixed_weight
- Ensures tactical strategies have tactical_model

**Integrated into:**
- `create_strategy()` function validates before API call
- Returns formatted error if validation fails
- Prevents unnecessary 1¢ API charges for invalid requests

### 4. Enhanced Documentation

#### Updated Examples
**Files:** `examples/basket_strategy.md`, `examples/tactical_strategy.md`

Added "Common Pitfalls" sections showing:
- ❌ Incorrect structure (what not to do)
- ✅ Correct structure (what to do instead)
- Side-by-side comparisons
- Specific to each strategy type

#### Created API Schema Reference
**File:** `API_SCHEMA_REFERENCE.md`

Comprehensive reference document with:
- All valid model names and parameters
- Complete JSON schemas for every model type
- Full working examples for each strategy type
- Common mistakes section with corrections
- Quick reference tables
- Default values and validation constraints

#### Created Testing Guide
**File:** `TESTING_GUIDE.md`

Testing guide for verifying improvements with:
- Original failing example
- Expected correct output
- Multiple test cases covering different scenarios
- Validation testing examples
- Verification checklist
- Troubleshooting guide

## Key Improvements Summary

### Before
```json
// Vague tool schema
{
  "strategy_config": {
    "type": "object",
    "description": "Strategy configuration with universe, models, etc."
  }
}
```

Result: LLMs guessed at structure, often incorrectly

### After
```json
// Detailed nested schema with discriminated unions
{
  "strategy_config": {
    "oneOf": [
      {
        "properties": {
          "universe": {
            "type": "array",
            "items": {
              "type": "object",
              "oneOf": [
                {"required": ["asset_symbol"]},
                {"required": ["asset_id"]},
                // ...
              ]
            }
          },
          "allocation_model": {
            "oneOf": [
              {
                "properties": {
                  "model_name": {"const": "risk_parity"},
                  "model_params": {
                    "properties": {
                      "lookback_days": {"type": "integer", "default": 252, ...}
                    }
                  }
                }
              },
              // ... other models
            ]
          },
          // ...
        }
      }
    ]
  }
}
```

Result: LLMs have complete type information and examples

## Benefits

1. **Prevents Invalid Requests**: LLMs know exactly what structure to use
2. **Self-Documenting**: Schemas embedded in tool definitions
3. **Better Error Messages**: Client-side validation catches issues before API
4. **Reduced API Costs**: Fewer failed requests = fewer 1¢ charges
5. **Improved UX**: Correct results on first try
6. **Type Safety**: JSON Schema provides strong guarantees
7. **Future-Proof**: Easy to update when API evolves

## Files Changed

### New Files Created
1. `src/nsmbl_mcp/utils/schemas.py` - JSON Schema definitions
2. `src/nsmbl_mcp/utils/validation.py` - Client-side validation
3. `API_SCHEMA_REFERENCE.md` - Complete schema reference
4. `TESTING_GUIDE.md` - Testing procedures
5. `SCHEMA_IMPROVEMENTS_SUMMARY.md` - This document

### Files Modified
1. `src/nsmbl_mcp/tools/strategies.py` - Enhanced tool definitions
2. `examples/basket_strategy.md` - Added pitfalls section
3. `examples/tactical_strategy.md` - Added pitfalls section

## Testing Instructions

See `TESTING_GUIDE.md` for complete testing procedures.

**Quick test:**
1. Restart Claude Desktop
2. Ask Claude to create the original failing strategy
3. Verify it generates correct structure on first attempt

## Validation Examples

### Example 1: Catches "type" mistake

Input:
```json
"allocation_model": {"type": "risk_parity"}
```

Output:
```
❌ Validation Error in strategy_data:

❌ Common mistake detected! Use 'model_name' not 'type' in allocation_model. 
Try: {'model_name': 'risk_parity', 'model_params': {}}
```

### Example 2: Catches universe structure mistake

Input:
```json
"universe": {"type": "static", "assets": ["AAPL", "MSFT"]}
```

Output:
```
❌ Validation Error in strategy_data:

❌ Common mistake detected! Don't use {'type': 'static', 'assets': [...]} structure. 
Instead use: [{'asset_symbol': 'AAPL'}, {'asset_symbol': 'MSFT'}]
```

### Example 3: Catches "periodic" mistake

Input:
```json
"rebalancing_model": {"model_name": "periodic", ...}
```

Output:
```
❌ Invalid model_name 'periodic'. Did you mean 'calendar_based'? 
Valid values: calendar_based, drift_based
```

## Architecture

```
┌─────────────────────────────────────┐
│      Claude Desktop (LLM)           │
│  - Reads tool schemas               │
│  - Generates strategy_data          │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│    MCP Server (create_strategy)     │
│  ┌─────────────────────────────┐   │
│  │ 1. Client-Side Validation   │   │
│  │    (validation.py)          │   │
│  │    - Checks structure       │   │
│  │    - Suggests corrections   │   │
│  └────────┬────────────────────┘   │
│           │ Valid?                  │
│           ├─ No ──→ Return error   │
│           │                         │
│           ▼ Yes                     │
│  ┌─────────────────────────────┐   │
│  │ 2. API Call to Backend      │   │
│  │    (NSMBLClient)            │   │
│  └────────┬────────────────────┘   │
└──────────┼─────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│    NSMBL Backend API                │
│  - Final server-side validation     │
│  - Creates strategy in database     │
│  - Returns strategy details         │
└─────────────────────────────────────┘
```

## Valid Values Reference

### Strategy Types
- `basket`, `tactical`, `ensemble`, `portfolio`

### Allocation Models
- `risk_parity`, `equal_weight`, `fixed_weight`, `inverse_volatility`

### Rebalancing Models
- `calendar_based`, `drift_based`

### Tactical Models
- `momentum`, `contrarian`

### Frequencies
- `daily`, `weekly`, `monthly`, `quarterly`

## Model Structure Pattern

All models follow this pattern:

```json
{
  "model_name": "specific_type",
  "model_params": {
    // Model-specific parameters (can be empty {})
  }
}
```

**Never use `"type"` - always use `"model_name"`!**

## Common Mistake Mappings

The validation system recognizes these common mistakes:

| Mistake | Correct Value | Context |
|---------|---------------|---------|
| `type` | `model_name` | All models |
| `periodic` | `calendar_based` | Rebalancing |
| `static` | Array of objects | Universe |
| `mean_reversion` | `contrarian` | Tactical |
| `equal` | `equal_weight` | Allocation |

## Success Metrics

After implementation, expect:
- ✅ 100% correct structure on first attempt from LLMs
- ✅ No "type" vs "model_name" confusion
- ✅ No "periodic" vs "calendar_based" errors
- ✅ No nested universe object mistakes
- ✅ Clear validation errors if mistakes occur
- ✅ Reduced API error rate from schema issues

## Maintenance

When the backend API changes:

1. Update `src/nsmbl_mcp/utils/schemas.py` with new schema definitions
2. Update `src/nsmbl_mcp/utils/validation.py` if new validations needed
3. Update tool descriptions in `tools/strategies.py`
4. Update `API_SCHEMA_REFERENCE.md` with new models/parameters
5. Update examples in `examples/` directory
6. Update `COMMON_MISTAKES` dict in validation.py if new patterns emerge
7. Test with Claude Desktop to verify changes

## Future Enhancements

Potential improvements:
1. Add validation for ensemble and portfolio specific rules
2. Create interactive schema explorer tool
3. Add more sophisticated validation (e.g., check if assets exist)
4. Generate OpenAPI spec from schemas for broader tooling support
5. Add schema versioning if API evolves significantly

## Conclusion

These improvements transform the MCP server from having vague, guesswork-based schemas to having complete, self-documenting, validated schemas. LLMs now have all the information they need to construct valid API requests on the first attempt, dramatically improving the user experience and reducing errors.

